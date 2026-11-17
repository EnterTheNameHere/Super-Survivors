"""Lifecycle test harness against real persistence/manager/group Lua; native IO mocked."""
from pathlib import Path
import unittest

import test_persistence as persistence_fixture


class LifecycleChecks(unittest.TestCase):
    def setUp(self):
        fixture = persistence_fixture.PersistenceChecks()
        fixture.setUp()
        self.lua = fixture.lua
        self.lua.execute('''
            -- Retain production event registrations, now with ordered multi-callback events.
            local initial=events;events={}
            Events=setmetatable({}, {__index=function(t,name)
                local list={};events[name]=list
                local e={Add=function(fn) list[#list+1]=fn end,
                    Remove=function(fn) for i=#list,1,-1 do if list[i]==fn then table.remove(list,i) end end end}
                rawset(t,name,e);return e
            end})
            for name,fn in pairs(initial) do Events[name].Add(fn) end
            eventErrors={}
            function fire(name)
                for _,fn in ipairs(events[name] or {}) do
                    local ok,err=pcall(fn);if not ok then eventErrors[#eventErrors+1]=err end
                end
            end
            enabled=true;clock=1000
            getTimestampMs=function() return clock end;ZombRand=function() return 17 end
            getNumActivePlayers=function() return 1 end
            SuperSurvivorGetOption=function() return enabled and 2 or 1 end
            getCore=function() return {isNoSave=function() return false end,
                getGameAndBuildVersion=function() return '42.22.2' end} end
            IsoWorld={saveoffsetx=0,saveoffsety=0};Perks={Axe='Axe'}
            CharacterStat={HUNGER='hunger',THIRST='thirst'}
            instanceof=function(_,kind) return false end
            local function array(list,transform)
                return {size=function() return #list end,get=function(_,i) return transform and transform(list[i+1]) or list[i+1] end}
            end
            function item(r)
                return {_record=r,getFullType=function() return r.kind end,
                    getCondition=function() return r.condition or 10 end,getCount=function() return 1 end,
                    getModData=function() r.md=r.md or {};return r.md end}
            end
            function container(a)
                return {getItems=function() return array(a.payload.inventory,item) end,
                    AddItem=function(_,kind)
                        local r={kind=kind,md={}};a.payload.inventory[#a.payload.inventory+1]=r;return item(r)
                    end}
            end
            allActors={}
            local baseSquare=square
            function square(x,y,z)
                local s=baseSquare(x,y,z)
                s.getFloor=function() return {} end;s.isFree=function() return true end
                s.getMovingObjects=function() return {contains=function(_,a) return a.current==s and a.loaded end} end
                return s
            end
            local baseActor=actor
            function upgrade(a)
                a.current=square(math.floor(a:getX()),math.floor(a:getY()),math.floor(a:getZ()))
                a.hasModData=function() for _ in pairs(a.payload.md) do return true end return false end
                for i,v in ipairs(a.payload.inventory) do if type(v)=='string' then a.payload.inventory[i]={kind='Base.'..v,md={}} end end
                a.payload.forename=a.payload.forename or 'Test';a.payload.axeXP=a.payload.axeXP or 0
                a.getDescriptor=function() return {getForename=function() return a.payload.forename end} end
                a.getInventory=function() return container(a) end
                a.getWornItems=function() return array(a.payload.worn,function(kind)
                    return {getItem=function() return item({kind='Base.'..kind}) end} end) end
                a.getXp=function() return {getXP=function() return a.payload.axeXP end,
                    AddXP=function(_,_,xp) a.payload.axeXP=a.payload.axeXP+xp end} end
                a.getPerkLevel=function() return a.payload.skills.Axe end
                a.getBodyDamage=function() return {getOverallBodyHealth=function() return a.payload.hp end} end
                a.getStats=function() return {get=function() return 0.2 end} end
                a.getPrimaryHandItem=function() return a.payload.hand and item({kind=a.payload.hand}) or nil end
                a.getSecondaryHandItem=function() return nil end
                a.setPrimaryHandItem=function(_,value) a.payload.hand=value and value:getFullType() end
                a.getCurrentSquare=function() return a.current end
                a.isNpc=function() return a.npc or false end
                a.removeFromSquare=function() a.current=nil end
                allActors[#allActors+1]=a;return a
            end
            function actor(x,y,z,localPlayer) return upgrade(baseActor(x,y,z,localPlayer)) end
            upgrade(player);slots={[0]=player};singleton=player
            getSpecificPlayer=function(index) return slots[index] end
            getWorld=function() return {getWorld=function() return world end,getCell=function() return cell end} end
            IsoPlayer.getInstance=function() return singleton end
            IsoPlayer.new=function(...)
                local n=select('#',...);local _,_,x,y,z=...
                if n==1 then
                    if readerHuman then return player end
                    local a=actor(0.5,0.5,0);a.current=nil;a.loaded=false
                    if readerConstructorFails then error('constructor handle gap') end
                    return a
                end
                return actor(x,y,z)
            end
            function collection(field)
                return {contains=function(_,a) return a[field] or false end,
                    iterator=function()
                        local found={};for _,a in ipairs(allActors) do if a[field] then found[#found+1]=a end end
                        local i=0;return {hasNext=function() return i<#found end,next=function() i=i+1;return found[i] end}
                    end}
            end
            cell.getObjectList=function() return collection('loaded') end
            cell.getAddList=function() return collection('pendingAdd') end
            cell.getRemoveList=function() return collection('pendingRemove') end
            cell.isSafeToAdd=function() return true end
            function SuperSurvivor:setName(name)
                self.player.payload.forename=name;self.player:getModData().Name=name
            end
            function SuperSurvivor:getName() return self.player:getModData().Name or 'Test' end
            function SuperSurvivor:StopWalk() end
            function SuperSurvivor:Wait(ticks) self.WaitTicks=ticks end
            local oldSquare=squares['0:0:0'];player.current=oldSquare or square(0,0,0)
            for _,o in ipairs({{2,0},{0,2},{-2,0},{0,-2},{3,1},{-3,-1}}) do square(o[1],o[2],0) end
            require 'Testing/SSRPersistenceTest'
            function run(id)
                assert(SSRTests.start(id,true));fire('OnTick');fire('OnTick')
                return SSRTests.results[id]
            end
            function stage() return run('ssr-restart-stage') end
            function current() return ModData.get(SSRTestsLifecycle.KEY).manifest end
            function saveGame()
                fire('OnSave') -- production P.save then observer, followed by native GlobalModData write
                disk=copy(worlds.A.tables)
            end
            function restart()
                for _,a in ipairs(allActors) do if a~=player then a.loaded=false;a.current=nil end end
                worlds.A.tables=copy(disk)
                clock=clock+1000;SSRTests.bootToken=nil
                SSPersistence.init(false);SSM:init();fire('OnGameStart')
                SSPersistence.tick() -- real production ordinary reconstruction, never forced by test
            end
            function resume() return run('ssr-restart-resume') end
            function readerClean()
                local a=allActors[#allActors];assert(not a.loaded and not a.current)
                assert(slots[0]==player and singleton==player and player.loaded)
            end
        ''')

    def test_two_current_entries_and_no_automatic_fixture_or_save(self):
        self.lua.execute('''
            assert(#SSRTests.list()==2 and not SSRTests.definitions['native-cell-only'])
            assert(not ModData.get(SSRTestsLifecycle.KEY) and SSPersistence.get().nextSurvivorID==1)
            fire('OnSave');assert(not ModData.get(SSRTestsLifecycle.KEY))
            local old=copy(player.payload)
            local result=stage();assert(result.status=='INCONCLUSIVE' and current().phase=='armed')
            assert(not current().checkpoint and SSGM:getCount()==1 and SSM:Get(current().id))
            assert(player.payload.md.ID==old.md.ID and player.payload.hp==old.hp)
        ''')

    def test_baseline_is_actual_save_not_staging_and_latest_normal_save_wins(self):
        self.lua.execute('''
            stage();local m=current();local a=SSM:Get(m.id):Get()
            a.payload.hp=68;a:getInventory():AddItem('Base.Bandage')
            assert(not m.checkpoint);saveGame()
            assert(m.phase=='saved' and m.checkpoint.actor.health==68)
            assert(m.checkpoint.actor.inventory:find('Base.Bandage',1,true))
            local first=m.lastGeneration
            a.payload.hp=65;saveGame()
            assert(m.lastGeneration>first and m.checkpoint.actor.health==65)
            assert(#eventErrors==0)
        ''')

    def test_real_registry_managers_group_and_loader_roundtrip_with_native_mock(self):
        self.lua.execute('''
            stage();saveGame();local id=current().id;local gid=current().groupID
            assert(not SSRTests.start('ssr-restart-resume',true))
            restart();assert(not SSRTests.active and SSM:Get(id))
            local result=resume();assert(result.status=='PASSED',result.summary)
            assert(result.observations.nativeMatch and result.observations.liveMatch)
            assert(result.observations.counts.actors==1 and SSGM:Get(gid))
            assert(SSM:Get(id):Get().loaded);readerClean()
        ''')

    def test_failed_production_save_invalidates_checkpoint_instead_of_reusing_stale_one(self):
        self.lua.execute('''
            stage();saveGame();assert(current().checkpoint)
            failSave=true;saveGame()
            assert(current().phase=='capture-error' and not current().checkpoint)
            assert(#eventErrors==1)
        ''')

    def test_native_snapshot_content_mismatch_is_logged_and_fails(self):
        self.lua.execute('''
            stage();saveGame();local file=current().checkpoint.registry.saved.file
            worlds.A.files[file].inventory[#worlds.A.files[file].inventory+1]={kind='Base.Corrupt',md={}}
            restart();local result=resume()
            assert(result.status=='FAILED' and not result.observations.nativeMatch)
            readerClean()
        ''')

    def test_live_ai_drift_is_inconclusive_when_exact_snapshot_matches(self):
        self.lua.execute('''
            stage();saveGame();restart()
            SSM:Get(current().id):Get().payload.hp=33
            local result=resume()
            assert(result.status=='INCONCLUSIVE' and result.observations.nativeMatch)
            assert(not result.observations.liveMatch);readerClean()
        ''')

    def test_duplicate_actor_or_group_record_mismatch_cannot_pass(self):
        self.lua.execute('''
            stage();saveGame();restart()
            local a=SSM:Get(current().id):Get();local duplicate=actor(a:getX(),a:getY(),a:getZ())
            duplicate.payload.md=copy(a.payload.md)
            local result=resume();assert(result.status=='FAILED' and result.observations.counts.actors==2)
            assert(duplicate.loaded) -- unrelated actor is never removed by probe
            duplicate.loaded=false;duplicate.current=nil
            SSPersistence.get().groups[current().groupID].leader=-1
            local second=resume();assert(second.status=='FAILED' and not second.observations.groupMatch)
        ''')

    def test_unloaded_tile_is_inconclusive_and_retry_does_not_force_reconstruction(self):
        self.lua.execute('''
            stage();saveGame();local saved=current().checkpoint.actor
            squares[saved.x..':'..saved.y..':'..saved.z]=nil
            restart();local id=current().id;assert(not SSM:Get(id))
            local result=resume();assert(result.status=='INCONCLUSIVE' and not SSM:Get(id))
        ''')

    def test_missing_snapshot_and_invalid_manifest_never_load_arbitrary_files(self):
        self.lua.execute('''
            stage();saveGame();local file=current().checkpoint.registry.saved.file
            worlds.A.files[file]=nil;restart()
            local result=resume();assert(result.status=='FAILED')
            current().checkpoint.registry.saved.file='map_p.bin'
            local before=actorCount;assert(not SSRTests.start('ssr-restart-resume',true));assert(actorCount==before)
        ''')

    def test_new_checkpoint_after_restart_is_inconclusive_not_false_comparison(self):
        self.lua.execute('''
            stage();saveGame();restart();fire('OnSave')
            local result=resume();assert(result.status=='INCONCLUSIVE')
            assert(result.summary:find('pointer changed',1,true))
        ''')

    def test_reader_handle_gap_blocks_further_runs_without_fixture_deletion(self):
        self.lua.execute('''
            stage();saveGame();restart();readerConstructorFails=true
            local result=resume();assert(result.status=='INCONCLUSIVE' and SSRTests.cleanupFailure)
            assert(SSM:Get(current().id):Get().loaded and player.loaded)
        ''')

    def test_reader_human_alias_is_never_removed(self):
        self.lua.execute('''
            stage();saveGame();restart();readerHuman=true
            local before=copy(player.payload)
            local result=resume();assert(result.status=='INCONCLUSIVE' and SSRTests.cleanupFailure)
            assert(player.loaded and player.current and player.payload.hp==before.hp)
            assert(slots[0]==player and singleton==player)
        ''')

    def test_identity_count_does_not_allocate_moddata_on_unrelated_objects(self):
        self.lua.execute('''
            stage();local other=actor(2,2,0);other.payload.md={}
            other.getModData=function() error('unexpected read allocating ModData') end
            saveGame();assert(current().checkpoint and #eventErrors==0)
            assert(other.loaded and next(other.payload.md)==nil)
        ''')

    def test_full_lifecycle_runs_without_lua_global_next(self):
        self.lua.execute('''
            next=nil
            stage();saveGame();restart()
            local result=resume();assert(result.status=='PASSED',result.summary)
            readerClean()
        ''')

    def test_no_save_baseline_or_same_session_resume_cannot_run(self):
        self.lua.execute('''
            stage();assert(not SSRTests.start('ssr-restart-resume',true))
            assert(not SSRTests.start('ssr-restart-stage',true))
            saveGame();assert(not SSRTests.start('ssr-restart-resume',true))
            enabled=false;saveGame();assert(not current().checkpoint)
        ''')


if __name__ == '__main__':
    unittest.main()
