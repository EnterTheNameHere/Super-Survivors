"""Both real information-window entry points share guarded observation actions."""
import unittest
import test_tests_ui as ui_fixture


class CombatInfoChecks(unittest.TestCase):
    def setUp(self):
        f = ui_fixture.TestsUiChecks()
        f.setUp()
        self.lua = f.lua
        self.lua.execute('''
            function Node:setX(v) self.x=v end
            function Node:setY(v) self.y=v end
            function Node:setHeight(v) self.height=v end
            function Node:setWidth(v) self.width=v end
            function Node:setTitle(v) self.title=v end
            function Node:getIsVisible() return self.visible end
            function Node:ignoreHeightChange() end
            function Node:noBackground() end
            ISPanel=Node
            ISContextMenu={get=function()
                menu={options={},addOption=function(self,title,_,fn) self.options[#self.options+1]={title=title,fn=fn} end}
                return menu
            end}
            package.preload['ISUI/ISContextMenu']=function() end
            package.preload['ISUI/ISLayoutManager']=function() end
            getMouseX=function() return 1 end;getMouseY=getMouseX
            getContextMenuText=function(k) return k end;getActionText=getContextMenuText
            getGameTime=function() return {getWorldAgeHours=function() return 2 end} end
            size=function(t) return #t end;SurvivorPerks={};isModEnabled=function() return false end
            CharacterStat={};Perks={};mutations=0
            function forbidden() mutations=mutations+1;error('forbidden actor mutation') end
            function member(id)
                local a=actor(105+id,100,0,false);a.kind='IsoPlayer';a.md.ID=id;a.md.Name='NPC'..id
                a.md.PerkCount=777;a.getCell=function() return cell end;a.hasModData=function() return true end
                a.getStats=function() return {get=function() return 0 end} end
                a.getPrimaryHandItem=function() return nil end
                a.getCurrentState=function() return nil end
                a.pressedAttack=forbidden;a.setIsAiming=forbidden
                local s={player=a,Get=function() return a end,getName=function() return a.md.Name end,
                    getCurrentTask=function() return 'None' end,getGroupRole=function() return 'Guard' end,
                    getGroupID=function() return nil end,getAIMode=function() return 'Guard' end,
                    getFilth=function() return 0 end,getID=function() return id end,
                    requestCombatAttack=function() return false,'busy' end}
                return s
            end
            npc=member(4);other=member(5);SSM={MainPlayer=0,SuperSurvivors={[4]=npc,[5]=other}}
            instanceof=function(o,kind) return o and o.kind==kind end
            require '5_UI/SurvivorInfoWindow';require '5_UI/SuperSurvivorInfoPanel'
            D=SSRCombatInfoDiagnostics;R=SSRCombatTrace
            function legacy()
                local w=SurvivorInfoWindow:new(0,0,300,650);w:addToUIManager();w:Load(npc);w:update();return w
            end
            function groupInfo()
                create_panel_survivor_info()
                get_group=function() return {getMembers=function() return {npc,other} end} end
                show_survivor_info(1);panel_survivor_info:update();return panel_survivor_info
            end
        ''')

    def test_both_entry_points_bind_exact_survivor_and_log_without_test_consent(self):
        self.lua.execute('''
            for _,create in ipairs({legacy,groupInfo}) do
                local w=create();assert(w.ssCombatButton.visible and w.ssCombatSelection.actor==npc.player)
                local fault={};SSRTests.cleanupFailure=fault
                local result=D.log(w,w.ssCombatSelection)
                assert(result.observations.id==4 and w.ssCombatStatus=='logged')
                assert(not SSRTests.active and SSRTests.cleanupFailure==fault)
                assert(npc.player.md.PerkCount==777 and mutations==0)
                assert(not SSRTests.start('native-position-roundtrip',false))
            end
        ''')

    def test_debug_off_changes_no_button_or_original_layout(self):
        self.lua.execute('''
            enabled=false;local w=legacy();assert(not w.ssCombatButton)
            local h=w.HomeWindow.height;w:update();assert(w.HomeWindow.height==h)
            local g=groupInfo();assert(not g.ssCombatButton and g.text_panel.height==g.height-54)
            enabled=true;w:update();assert(w.ssCombatButton.visible)
            assert(w.HomeWindow.y+w.HomeWindow.height<w.ssCombatButton.y)
            g:update();assert(g.text_panel.height<g.button_call.y)
            assert(g.button_close.y+g.button_close.height<g.ssCombatButton.y)
            enabled=false;w:update();g:update()
            assert(not w.ssCombatButton.visible and w.HomeWindow.height==h)
            assert(not g.ssCombatButton.visible and g.text_panel.height==g.height-54)
        ''')

    def test_old_menu_cannot_retarget_after_information_load_changes(self):
        self.lua.execute('''
            local w=legacy();D.menu(w);local old=menu
            w:Load(other);w:update();old.options[1].fn();old.options[2].fn()
            assert(w.ssCombatStatus=='unavailable' and not R.active)
            assert(w.ssCombatSelection.id==5 and mutations==0)
        ''')

    def test_close_hide_and_group_remove_stop_only_their_trace(self):
        self.lua.execute('''
            local w=legacy();local r=D.start(w,w.ssCombatSelection);assert(r and R.active==r)
            local g=groupInfo();g:setVisible(false);assert(R.active==r)
            w:close();assert(r.finished and not R.active)
            w:setVisible(true);w:update();r=D.start(w,w.ssCombatSelection)
            w:setVisible(false);assert(r.finished)
            g=groupInfo();r=D.start(g,g.ssCombatSelection);remove_panel_survivor_info()
            assert(r.finished and not R.active and mutations==0)
        ''')

    def test_unload_replacement_and_disabled_debug_reject_callback_and_stop(self):
        self.lua.execute('''
            local w=legacy();local p=w.ssCombatSelection;local r=D.start(w,p)
            npc.player.inWorld=false;w:update();assert(r.finished and not w.ssCombatButton.visible)
            assert(not D.log(w,p));npc.player.inWorld=true
            w:Load(npc);w:update();r=D.start(w,w.ssCombatSelection)
            SSM.SuperSurvivors[4]={player=npc.player};w:update();assert(r.finished)
            SSM.SuperSurvivors[4]=npc;w:Load(npc);w:update();r=D.start(w,w.ssCombatSelection)
            enabled=false;w:update();assert(r.finished and not w.ssCombatButton.visible)
        ''')

    def test_contextual_menu_has_explicit_log_start_stop_and_never_autostarts(self):
        self.lua.execute('''
            local w=legacy();w:update();D.menu(w)
            assert(#menu.options==5 and not R.active and not SSRCombatFirstAttack.active)
            menu.options[2].fn();assert(R.active)
            menu.options[3].fn();assert(not R.active and w.ssCombatStatus=='trace stopped')
            assert(mutations==0)
        ''')

    def test_ui_module_reload_stops_existing_trace(self):
        self.lua.execute('''
            local w=legacy();mySurvivorInfoWindow=w
            local r=D.start(w,w.ssCombatSelection)
            package.loaded['5_UI/SurvivorInfoWindow']=nil;require '5_UI/SurvivorInfoWindow'
            assert(r.finished and not R.active)
            local g=groupInfo();r=D.start(g,g.ssCombatSelection)
            package.loaded['5_UI/SuperSurvivorInfoPanel']=nil;require '5_UI/SuperSurvivorInfoPanel'
            assert(r.finished and not R.active)
        ''')

    def test_first_observation_both_ui_paths_and_stop_callbacks(self):
        self.lua.execute('''
            local F=SSRCombatFirstAttack
            npc.player.isNpc=function() return true end
            npc.player.isAttackStarted=function() return false end
            npc.player.isInitiateAttack=function() return false end
            npc.StopWalk=function() end
            for _,create in ipairs({legacy,groupInfo}) do
                local w=create();D.menu(w);assert(not F.active)
                menu.options[4].fn();local r=F.active
                assert(r and r.owner==w and r.p.actor==npc.player)
                assert(w.ssCombatStatus=='observing earliest attack (10s cap)')
                menu.options[5].fn();assert(r.finished and not F.active)
                assert(w.ssCombatStatus=='observation stopped' and mutations==0)
            end
        ''')

    def test_first_observation_stale_menu_two_windows_close_hide_rebind_and_reload(self):
        self.lua.execute('''
            local F=SSRCombatFirstAttack
            npc.player.isNpc=function() return true end
            npc.player.isAttackStarted=function() return false end
            npc.player.isInitiateAttack=function() return false end
            npc.StopWalk=function() end
            local w=legacy();D.menu(w);local old=menu
            w:Load(other);w:update();old.options[4].fn();assert(not F.active)
            w:Load(npc);w:update();local r=assert(D.startFirst(w,w.ssCombatSelection))
            local g=groupInfo();assert(not D.startFirst(g,g.ssCombatSelection))
            D.close(g);assert(F.active==r);g:setVisible(false);assert(F.active==r)
            w:setVisible(false);assert(r.finished and not F.active)
            w:setVisible(true);w:update();r=assert(D.startFirst(w,w.ssCombatSelection))
            w:Load(other);assert(r.finished and not F.active)
            w:Load(npc);w:update();r=assert(D.startFirst(w,w.ssCombatSelection))
            package.loaded['5_UI/SSRCombatInfoDiagnostics']=nil;require '5_UI/SSRCombatInfoDiagnostics'
            assert(r.finished and not F.active)
            r=assert(D.startFirst(w,w.ssCombatSelection));w:close();assert(r.finished)
            assert(mutations==0)
        ''')

    def test_first_observation_preexisting_rejection_reason_and_finished_status(self):
        self.lua.execute('''
            local F=SSRCombatFirstAttack;local w=legacy()
            npc.player.isNpc=function() return true end
            npc.player.isAttackStarted=function() return true end
            assert(not D.startFirst(w,w.ssCombatSelection))
            assert(w.ssCombatStatus=='unavailable' and w.ssCombatButton.tooltip:find('Already',1,true))
            npc.player.isAttackStarted=function() return false end
            npc.player.isInitiateAttack=function() return false end;npc.StopWalk=function() end
            local r=assert(D.startFirst(w,w.ssCombatSelection));F.stop(w,'deadline')
            w:update();assert(w.ssCombatStatus=='observation logged')
            assert(w.ssCombatButton.tooltip:find('deadline',1,true))
            assert(not SSRTests.active and mutations==0)
        ''')


if __name__ == '__main__':
    unittest.main()
