"""Opt-in test execution and native-probe guardrails with mocked UI/engine IO."""
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]
CLIENT = ROOT / '42/media/lua/client'


class TestsUiChecks(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.globals().clientRoot = str(CLIENT).replace('\\', '/')
        self.lua.globals().archivedProbe = str(ROOT / 'tests/fixtures/SSRNativePositionTest.lua').replace('\\', '/')
        self.lua.execute('''
            package.path=clientRoot..'/?.lua;'..package.path
            enabled=true;multiplayer=false;players=1;clock=1000;safe=true
            print=function() end
            SuperSurvivorGetOption=function(key) assert(key=='DebugOptions');return enabled and 2 or 1 end
            getDebug=function() error('Tests must not require native debug mode') end
            isClient=function() return multiplayer end;isServer=function() return false end
            getNumActivePlayers=function() return players end
            getTimestampMs=function() return clock end;ZombRand=function() return 11 end
            getText=function(key) return key end;UIFont={Small={}}
            ISWorldObjectContextMenu={setTest=function() previewAvailable=true;return true end}
            getTextManager=function() return {getFontHeight=function() return 14 end} end
            events={}
            Events=setmetatable({}, {__index=function(t,key)
                events[key]={}
                local e={Add=function(fn) events[key][fn]=true end,Remove=function(fn) events[key][fn]=nil end}
                rawset(t,key,e);return e
            end})
            function fire(name) for fn in pairs(events[name] or {}) do fn() end end
            function copy(value)
                if type(value)~='table' then return value end
                local result={};for k,v in pairs(value) do result[k]=copy(v) end;return result
            end
            files,worldData,actors={},{},{}
            function collection(field)
                return {contains=function(_,actor) return actor[field] or false end}
            end
            local squares={}
            function square(x,y,z)
                local key=x..':'..y..':'..z
                if not squares[key] then
                    local s={getX=function() return x end,getY=function() return y end,getZ=function() return z end,
                        getFloor=function() return not noFloor and {} or nil end,isFree=function() return not blocked end}
                    s.getMovingObjects=function() return {contains=function(_,a) return a.moving==s end} end
                    squares[key]=s
                end
                return squares[key]
            end
            cell={getGridSquare=function(_,x,y,z) return square(x,y,z) end,
                getObjectList=function() return collection('inWorld') end,
                getAddList=function() return collection('inAdd') end,
                getRemoveList=function() return collection('inRemove') end,
                isSafeToAdd=function() return safe end,
                addMovingObject=function(_,a) assert(safe and not a.human);a.inWorld=true;a.registerCalls=(a.registerCalls or 0)+1 end}
            getCell=function() return cell end
            getWorld=function() return {getWorld=function() return 'Disposable' end} end
            IsoWorld={saveoffsetx=0,saveoffsety=0}
            getSaveDir=function() return 'world/' end
            checkSaveFileExists=function(file) return files[file]~=nil end
            getCore=function() return {isNoSave=function() return noSave or false end,
                getGameVersion=function() return {toString=function() return '42.22' end} end,
                getGameAndBuildVersion=function() return buildVersion or '42.22.2' end,
                getScreenWidth=function() return 1920 end,getScreenHeight=function() return 1080 end} end
            ModData={get=function(key) return worldData[key] end,
                getOrCreate=function(key) worldData[key]=worldData[key] or {};return worldData[key] end}
            function actor(x,y,z,localPlayer)
                local a={x=x+0.5,y=y+0.5,z=z,current=square(x,y,z),md={},inWorld=true,
                    human=localPlayer,saveFileName=localPlayer and 'human.db' or nil}
                a.moving=a.current
                a.getX=function() return a.x end;a.getY=function() return a.y end;a.getZ=function() return a.z end
                a.getCurrentSquare=function() return a.current end
                a.getModData=function() return a.md end
                a.isLocalPlayer=function() return a.human or false end
                a.isNpc=function() return a.npc or false end
                a.isDead=function() return a.dead or false end
                a.setNpc=function(_,value) assert(not a.human);a.npc=value end
                a.setBlockMovement=function() assert(not a.human) end
                -- Any manual correction by the probe is a test failure.
                a.setX=function() error('manual setX forbidden') end
                a.setY=function() error('manual setY forbidden') end
                a.setZ=function() error('manual setZ forbidden') end
                a.setCurrentSquare=function(_,s)
                    assert(a.cellOnly and not a.human,'square correction permitted only in explicit cell-only phase')
                    if failPlacement then error('placement failed') end
                    a.current=s
                end
                a.setMovingSquareNow=function()
                    assert(a.cellOnly and not a.human)
                    if not failMovingRegistration then a.moving=a.current end
                end
                a.save=function(_,path)
                    assert(not a.human and path:sub(1,6)=='world/')
                    local file=path:sub(7)
                    assert(file:find('SSR_Test_NativePosition_',1,true)==1 and files[file]==nil)
                    if failSave then error('native save exception') end
                    files[file]={x=a.x,y=a.y,z=a.z,md=copy(a.md)}
                    a.saveFileName=path
                end
                a.load=function(_,path)
                    assert(not a.human)
                    if failLoad then error('native load exception') end
                    local data=files[path:sub(7)]
                    if not data then
                        if failMissing then error('missing-file exception') end
                        return
                    end
                    a.saveFileName=path
                    if not failPosition then a.x,a.y,a.z=data.x,data.y,data.z end
                    a.md=copy(data.md)
                    if slotChangedByLoad then slots[1]=a end
                    -- Installed source restores XYZ without assigning currentSquare.
                end
                a.removeFromWorld=function()
                    assert(not a.human);a.inWorld=false;a.inAdd=false;a.inRemove=false
                end
                a.removeFromSquare=function() assert(not a.human);a.current=nil;a.moving=nil end
                if not localPlayer then actors[#actors+1]=a end
                return a
            end
            human=actor(100,100,0,true);singleton=human
            slots={[0]=human};getSpecificPlayer=function(index) return slots[index] end
            IsoPlayer={getInstance=function() return singleton end,
                new=function(...)
                    local argc=select('#',...)
                    local _,_,x,y,z=...
                    local cellOnly=argc==1
                    if cellOnly then x,y,z=0,0,0 else assert(argc==5) end
                    if failConstructor then actor(x,y,z,false);error('constructor failed after registration') end
                    if returnHuman then return human end
                    local a=actor(x,y,z,false)
                    if cellOnly then
                        a.cellOnly=true;a.inWorld=implicitCellRegistration or false
                        a.current=originLoaded and square(0,0,0) or nil;a.moving=a.current
                        if failCellOnlyConstructor then error('cell-only constructor failed before return') end
                    end
                    return a
                end}
            SurvivorFactory={CreateSurvivor=function() return {setForename=function() end} end}
            -- Minimal widget contracts; this is not an engine render/layout test.
            Node={};Node.__index=Node
            function Node:derive() local c={};c.__index=c;return setmetatable(c,{__index=self}) end
            function Node:new(x,y,w,h)
                return setmetatable({x=x,y=y,width=w,height=h,children={},options={},selected=0,visible=true},{__index=self})
            end
            function Node:initialise() end
            function Node:createChildren() end
            function Node:addChild(child) assert(not child.root);self.children[#self.children+1]=child;child.parent=self end
            function Node:addToUIManager() self.root=true;self:createChildren() end
            function Node:removeFromUIManager() self.root=false end
            function Node:setVisible(value) self.visible=value end
            function Node:bringToTop() end
            function Node:getBottom() return self.y+self.height end
            function Node:setEnable(value) self.enabled=value end
            function Node:setEnabled(value) self.enabled=value end
            function Node:setText(value) self.text=value end
            function Node:paginate() if self.autosetheight then self.height=80 end end
            function Node:addScrollBars() end
            function Node:update() end
            function Node:close() self.visible=false end
            function Node:addOption(text) self.options[#self.options+1]=text;if self.selected==0 then self.selected=1 end end
            function Node:clear() self.options={};self.selected=0 end
            ISCollapsableWindow=Node;ISRichTextPanel=Node;ISComboBox=Node;ISButton=Node
            ISTickBox=Node:derive()
            function ISTickBox:new(x,y,w,h)
                local n=Node.new(self,x,y,w,h);n.selected={};return n
            end
            function ISTickBox:addOption(text) self.options[#self.options+1]=text end
            function ISTickBox:setSelected(index,value) self.selected[index]=value end
            function ISTickBox:isSelected(index) return self.selected[index]==true end
            for _,name in ipairs({'ISCollapsableWindow','ISRichTextPanel','ISComboBox','ISTickBox'}) do
                package.preload['ISUI/'..name]=function() return true end
            end
            -- Historical probe fixtures exercise registry/UI guardrails without shipping old choices.
            package.preload['Testing/SSRPersistenceTest']=function() end
            dofile(archivedProbe)
            require '5_UI/SSRTestsWindow'
            function run(id)
                assert(SSRTests.start(id,true));fire('OnTick');fire('OnTick')
                return SSRTests.results[id]
            end
            function assertClean()
                for _,a in ipairs(actors) do assert(not a.inWorld and a.current==nil and a.moving==nil) end
                assert(human.inWorld and human.current~=nil and human.saveFileName=='human.db' and singleton==human)
            end
        ''')

    def test_no_world_changes_at_load_and_entry_gated_without_native_debug(self):
        self.lua.execute('''
            assert(#actors==0 and next(files)==nil and not SSRTests.active)
            local count=0;local context={addOption=function(_,label,target,callback) count=count+1 end}
            enabled=false;SSRTests.menuEntryCallback(0,context,{},false);assert(count==0)
            enabled=true;SSRTests.menuEntryCallback(0,context,{},true);assert(count==0 and previewAvailable)
            SSRTests.menuEntryCallback(1,context,{},false);assert(count==0)
            SSRTests.menuEntryCallback(0,context,{},false);assert(count==1)
            multiplayer=true;SSRTests.menuEntryCallback(0,context,{},false);assert(count==1)
        ''')

    def test_consent_survives_selection_but_resets_on_run_and_reopen(self):
        self.lua.execute('''
            local window=SSRTests.openWindow();window:update()
            assert(window.warning.text:find('Warning — World Modifications',1,true))
            assert(not window.runButton.enabled and not window.consent:isSelected(1))
            window.consent:setSelected(1,true);window:onConsent();window:update();assert(window.runButton.enabled)
            window:onRun();assert(SSRTests.active and not window.consent:isSelected(1) and #actors==0)
            assert(not SSRTests.start('native-position',true))
            SSRTests.cancel('test cancelled before execution')
            window.consent:setSelected(1,true);window.selector.selected=2;window:onSelection()
            assert(window.consent:isSelected(1))
            window:refreshRegistry();assert(window.consent:isSelected(1))
            window.consent:setSelected(1,true);SSRTests.openWindow()
            assert(not window.consent:isSelected(1))
            window:close();assert(not window.visible);assertClean()
        ''')

    def test_disabled_run_shows_the_prerequisite_even_after_consent(self):
        self.lua.execute('''
            local window=SSRTests.openWindow();window.consent:setSelected(1,true)
            noSave=true;window:update()
            assert(not window.runButton.enabled)
            assert(window.runButton.tooltip:find('save-enabled',1,true))
            assert(window.output.text:find('Run disabled:',1,true))
            noSave=false;window:update();assert(window.runButton.enabled)
            assert(window.runButton.tooltip==nil)
        ''')

    def test_combat_ui_requires_explicit_survivor_selection_and_refresh_does_not_adopt_replacements(self):
        self.lua.execute('''
            local npcActor=actor(105,100,0,false);npcActor.kind='IsoPlayer';npcActor.md.ID=4;npcActor.md.Name='Ada'
            npcActor.getCell=function() return cell end;npcActor.hasModData=function() return true end
            getGameTime=function() return {getWorldAgeHours=function() return 1 end} end
            SSM={MainPlayer=0,SuperSurvivors={[4]={player=npcActor}}}
            instanceof=function(obj,kind) return obj and obj.kind==kind end
            local window=SSRTests.openWindow()
            for i,definition in ipairs(window.tests) do
                if definition.id=='combat-existing-snapshot' then window.selector.selected=i end
            end
            window:onSelection();window.consent:setSelected(1,true);window:update()
            assert(#window.survivors==1 and not window.runButton.enabled)
            assert(window.survivorSelector.selected==1)
            window.survivorSelector.selected=2;window:onSurvivorSelection();window:update()
            assert(window.runButton.enabled)
            window:onRun();assert(SSRTests.active.parameters.id==4 and not window.consent:isSelected(1))
            window:update();assert(not window.refreshSurvivorsButton.enabled and not window.survivorSelector.enabled)
            fire('OnTick');assert(SSRTests.results['combat-existing-snapshot'].status=='INCONCLUSIVE')
            window:refreshSurvivors();assert(window.survivorSelector.selected==2)
            SSM.SuperSurvivors[4]={player=npcActor}
            window:refreshSurvivors();assert(window.survivorSelector.selected==1)
            window.selector.selected=1;window:onSelection();window:update()
            assert(not window.survivorSelector.enabled and not window.refreshSurvivorsButton.enabled)
        ''')

    def test_read_only_selection_remains_available_without_clearing_cleanup_failure(self):
        self.lua.execute('''
            SSRTests.register({id='read-only',title='Read only',description='Observe only',order=0,readOnly=true,
                run=function(ctx) ctx:finish('PASSED','Observed') end})
            local failure={};SSRTests.cleanupFailure=failure
            local window=SSRTests.openWindow();window.consent:setSelected(1,true);window:update()
            assert(window.runButton.enabled)
            window:onRun();fire('OnTick')
            assert(SSRTests.results['read-only'].status=='PASSED' and SSRTests.cleanupFailure==failure)
            assert(not SSRTests.start('native-position',true))
        ''')

    def test_same_session_probe_reports_raw_square_mismatch_without_correcting_it(self):
        self.lua.execute('''
            local result=run('native-position')
            assert(result.status=='PASSED' and result.observations.positionRestored)
            assert(not result.observations.after.squareMatchesPosition)
            assert(result.observations.before.square==result.observations.after.square)
            assert(result.observations.humanUnchanged and result.observations.session=='same-session only')
            assertClean()
            local first=next(files);run('native-position');assert(files[first]~=nil)
            local count=0;for _ in pairs(files) do count=count+1 end;assert(count==2)
        ''')

    def test_preexisting_actor_and_singleton_owner_are_not_removed_or_replaced(self):
        self.lua.execute('''
            local bystander=actor(200,200,0,false);singleton=bystander
            local result=run('native-position')
            assert(result.status=='PASSED' and singleton==bystander and bystander.inWorld)
            assert(actors[1]==bystander and not actors[2].inWorld and not actors[3].inWorld)
            assert(human.inWorld and human.saveFileName=='human.db')
        ''')

    def test_failed_position_or_native_exception_is_not_a_pass_and_cleans_actors(self):
        self.lua.execute('''
            failPosition=true;local result=run('native-position')
            assert(result.status=='FAILED' and not result.observations.positionRestored);assertClean()
            failPosition=false;failLoad=true;result=run('native-position')
            assert(result.status=='FAILED' and result.summary:find('native load exception',1,true));assertClean()
        ''')

    def test_missing_file_case_failure_is_reported_and_constructor_cannot_target_human(self):
        self.lua.execute('''
            failMissing=true;assert(run('native-position').status=='FAILED');assertClean()
            failMissing=false;returnHuman=true
            local result=run('native-position')
            assert(result.status=='INCONCLUSIVE' and SSRTests.cleanupFailure)
            assert(not SSRTests.start('native-position',true))
            assert(human.inWorld and singleton==human and human.saveFileName=='human.db')
        ''')

    def test_pending_safe_phase_and_environment_changes_do_not_spawn(self):
        self.lua.execute('''
            safe=false;assert(SSRTests.start('native-position',true));fire('OnTick');fire('OnTick')
            assert(SSRTests.active and #actors==0)
            enabled=false;fire('OnTick');assert(not SSRTests.active and #actors==0)
            enabled=true;safe=true;blocked=true
            assert(run('native-position').status=='SETUP ERROR' and #actors==0)
        ''')

    def test_version_gate_uses_build_suffix_and_reports_other_builds(self):
        self.lua.execute('''
            assert(getCore():getGameVersion():toString()=='42.22')
            local definition=SSRTests.definitions['native-position']
            assert(SSRTests.availability(definition))
            buildVersion='42.22.3'
            local ok,reason=SSRTests.availability(definition)
            assert(not ok and reason:find('42.22.3',1,true))
        ''')

    def test_no_save_and_nonzero_world_offsets_are_unavailable(self):
        self.lua.execute('''
            noSave=true;assert(not SSRTests.start('native-position',true))
            noSave=false;IsoWorld.saveoffsetx=1
            local ok,reason=SSRTests.availability(SSRTests.definitions['native-position'])
            assert(not ok and reason:find('save offsets',1,true))
            assert(#actors==0 and next(files)==nil)
        ''')

    def test_boxed_java_offsets_accept_zero_but_reject_unknown_and_nonzero(self):
        self.lua.execute('''
            local definition=SSRTests.definitions['native-position']
            local function boxed(value) return setmetatable({}, {__tostring=function() return value end}) end
            IsoWorld.saveoffsetx=boxed('0');IsoWorld.saveoffsety=boxed('0')
            assert(IsoWorld.saveoffsetx~=0 and SSRTests.availability(definition))
            for _,value in ipairs({'1','-1','nil','<private>','not a number'}) do
                IsoWorld.saveoffsety=boxed(value)
                assert(not SSRTests.availability(definition))
            end
            IsoWorld.saveoffsety=nil;assert(not SSRTests.availability(definition))
            assert(#actors==0 and next(files)==nil)
        ''')

    def test_cell_only_load_and_three_part_registration_without_coordinate_setters(self):
        self.lua.execute('''
            local result=run('native-cell-only');local o=result.observations
            assert(result.status=='PASSED' and o.positionRestored and o.markerRestored)
            assert(o.before.position.x==0.5 and o.before.position.y==0.5 and not o.before.inWorld)
            assert(o.before.squarePosition==nil and o.after.squarePosition==nil and not o.after.inWorld)
            assert(o.registered.squareMatchesPosition and o.registered.squareContains and o.registered.npc)
            assert(o.registrationValid and o.positionUnchangedByPlacement and o.humanUnchanged)
            assert(actors[2].registerCalls==1 and actors[2].cellOnly)
            assert(not SSRTests.active);assertClean()
        ''')

    def test_cell_only_observes_implicit_constructor_membership_without_duplicate_add(self):
        self.lua.execute('''
            implicitCellRegistration=true;originLoaded=true
            local result=run('native-cell-only');local o=result.observations
            assert(result.status=='PASSED' and o.before.inWorld and o.before.squareContains)
            assert(o.after.squarePosition.x==0 and not o.after.squareMatchesPosition)
            assert(o.registered.squareMatchesPosition and not actors[2].registerCalls)
            assertClean()
        ''')

    def test_cell_only_load_failure_skips_registration_and_cleans_both_actors(self):
        self.lua.execute('''
            failPosition=true
            local result=run('native-cell-only')
            assert(result.status=='FAILED' and not actors[2].registerCalls)
            assertClean()
        ''')

    def test_cell_only_registration_exception_and_missing_moving_membership_cannot_pass(self):
        self.lua.execute('''
            failPlacement=true
            local first=run('native-cell-only');assert(first.status=='FAILED');assertClean()
            failPlacement=false;failMovingRegistration=true
            local second=run('native-cell-only')
            assert(second.status=='FAILED' and not second.observations.registrationValid)
            assertClean()
        ''')

    def test_cell_only_constructor_handle_gap_blocks_more_runs(self):
        self.lua.execute('''
            failCellOnlyConstructor=true
            local result=run('native-cell-only')
            assert(result.status=='INCONCLUSIVE' and SSRTests.cleanupFailure)
            assert(not SSRTests.start('native-cell-only',true))
            assert(not actors[1].inWorld and human.inWorld and singleton==human)
        ''')

    def test_cell_only_guard_detects_nonzero_local_slot_changes(self):
        self.lua.execute('''
            slotChangedByLoad=true
            local result=run('native-cell-only')
            assert(result.status=='INCONCLUSIVE' and SSRTests.cleanupFailure)
            assert(not actors[2].registerCalls and slots[1]==actors[2])
            assert(human.inWorld and singleton==human)
        ''')

    def test_constructor_exception_before_return_blocks_further_mutating_runs(self):
        self.lua.execute('''
            failConstructor=true
            local result=run('native-position')
            assert(result.status=='INCONCLUSIVE' and SSRTests.cleanupFailure)
            assert(result.summary:find('cleanup cannot be verified',1,true))
            assert(not SSRTests.start('native-position',true))
            assert(human.inWorld and human.saveFileName=='human.db' and singleton==human)
            -- Mock deliberately models an unrecoverable returned-handle gap.
            assert(#actors==1 and actors[1].inWorld)
        ''')

    def test_restart_staging_requires_explicit_new_session_and_explicit_resume(self):
        self.lua.execute('''
            assert(run('native-position-stage').status=='INCONCLUSIVE');assertClean()
            local manifest=worldData['SSR.Tests.NativePosition'].manifest
            assert(manifest.file and files[manifest.file])
            assert(not SSRTests.start('native-position-resume',true))
            -- Simulate a different Lua boot in the mock only; not an engine test.
            SSRTests.bootToken=nil;clock=2000;fire('OnGameStart')
            assert(not SSRTests.active and #actors==1)
            local result=run('native-position-resume')
            assert(result.status=='PASSED' and result.observations.session:find('different Lua session',1,true))
            assert(manifest.lastResult.positionRestored);assertClean()
        ''')

    def test_registry_steps_errors_timeout_and_hot_reload_are_explicit(self):
        self.lua.execute('''
            SSRTests.register({id='steps',title='Steps',run=function(ctx)
                ctx.step=function(self) self:finish('PASSED','observed completion') end end})
            assert(run('steps').status=='PASSED')
            SSRTests.register({id='throws',title='Throws',run=function() error('unexpected') end})
            assert(run('throws').status=='SETUP ERROR')
            SSRTests.register({id='noresult',title='No result',run=function() end})
            assert(run('noresult').status=='SETUP ERROR')
            SSRTests.register({id='timeout',title='Timeout',maxTicks=2,run=function(ctx) ctx.step=function() end end})
            run('timeout');fire('OnTick');assert(SSRTests.results.timeout.status=='INCONCLUSIVE')
            SSRTests.unregister('steps');assert(not SSRTests.definitions.steps)
        ''')
        self.lua.execute((CLIENT / 'Testing/SSRTests.lua').read_text())
        self.lua.execute('''
            local count=0;for _ in pairs(events.OnTick) do count=count+1 end;assert(count==1)
            assert(not SSRTests.active)
        ''')

    def test_closing_window_cancels_and_world_start_destroys_old_ui_without_auto_run(self):
        self.lua.execute('''
            local window=SSRTests.openWindow();window.consent:setSelected(1,true);window:onRun()
            window:close();assert(not SSRTests.active and #actors==0)
            SSRTests.openWindow();fire('OnGameStart')
            assert(SSRTests.window==nil and #actors==0 and next(files)==nil)
        ''')


if __name__ == '__main__':
    unittest.main()
