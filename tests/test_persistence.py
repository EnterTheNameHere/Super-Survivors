"""World registry integration with mocked native file/character IO, not engine tests."""
from pathlib import Path
import os
import unittest
from lupa.lua51 import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]
CLIENT = ROOT / '42/media/lua/client'


class PersistenceChecks(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.globals().clientRoot = str(CLIENT).replace('\\', '/')
        self.lua.execute('''
            package.path=clientRoot..'/?.lua;'..package.path
            print=function() end
            isClient=function() return multiplayer or false end
            isServer=function() return false end
            getText=function(key) return key end
            getActionText=function(key) return key end
            function has_value(t, value) for _,v in pairs(t) do if v==value then return true end end return false end
            function copy(value)
                if type(value)~='table' then return value end
                local t={};for k,v in pairs(value) do t[k]=copy(v) end;return t
            end
            worlds={A={files={},tables={}},B={files={},tables={}}}; world='A'
            getSaveDir=function() return world..'/' end
            getGameTime=function() return {getWorldAgeHours=function() return 25 end} end
            ModData={get=function(key) return worlds[world].tables[key] end,
                getOrCreate=function(key)
                    local tables=worlds[world].tables;tables[key]=tables[key] or {};return tables[key]
                end}
            checkSaveFileExists=function(file) return worlds[world].files[file]~=nil end
            getModFileReader=function() error('legacy reader called') end
            getModFileWriter=function() error('legacy writer called') end
            events={}
            Events=setmetatable({}, {__index=function(t,key)
                local event={Add=function(fn) events[key]=fn end};rawset(t,key,event);return event
            end})
            cell={getObjectList=function() return {contains=function(_,a) return a.loaded end} end,
                getAddList=function() return {contains=function(_,a) return a.pendingAdd or false end} end,
                getRemoveList=function() return {contains=function(_,a) return a.pendingRemove or false end} end,
                getGridSquare=function(_,x,y,z) return squares[x..':'..y..':'..z] end}
            squares={}
            function square(x,y,z)
                local s={getX=function() return x end,getY=function() return y end,getZ=function() return z end}
                squares[x..':'..y..':'..z]=s;return s
            end
            getCell=function() return cell end
            getWorld=function() return {getCell=function() return cell end} end
            SurvivorFactory={CreateSurvivor=function() return {} end}
            actorCount=0
            function actor(x,y,z,localPlayer)
                actorCount=actorCount+1
                local a={loaded=true,payload={x=x,y=y,z=z,md={},hp=77,
                    inventory={'Hammer','Bandage'},skills={Axe=4},worn={'Jacket'},appearance='test'}}
                a.getX=function() return a.payload.x end
                a.getY=function() return a.payload.y end
                a.getZ=function() return a.payload.z end
                a.setX=function(_,v) a.payload.x=v end
                a.setY=function(_,v) a.payload.y=v end
                a.setZ=function(_,v) a.payload.z=v end
                a.getCurrentSquare=function() return a.loaded and square(a:getX(),a:getY(),a:getZ()) or nil end
                a.getModData=function() return a.payload.md end
                a.isLocalPlayer=function() return localPlayer or false end
                a.isDead=function() return a.payload.dead or false end
                a.setNpc=function(_,v) a.npc=v end
                a.setBlockMovement=function(_,v) a.block=v end
                a.setSceneCulled=function() end
                a.save=function(_,path)
                    if failSave then error('disk failure') end
                    assert(path:sub(1,2)==world..'/')
                    worlds[world].files[path:sub(3)]=copy(a.payload)
                end
                a.load=function(_,path)
                    if worlds[world].files[path:sub(3)] then a.payload=copy(worlds[world].files[path:sub(3)]) end
                end
                a.removeFromWorld=function() a.loaded=false end
                a.removeFromSquare=function() a.loaded=false end
                a.getPrimaryHandItem=function() return a.payload.hand end
                a.setPrimaryHandItem=function(_,v) a.payload.hand=v end
                return a
            end
            IsoPlayer={new=function(_,_,x,y,z) return actor(x,y,z) end}
            player=actor(0,0,0,true)
            getSpecificPlayer=function() return player end
            SuperSurvivor={}
            SuperSurvivor.__index=SuperSurvivor
            function wrap(a)
                return setmetatable({player=a},SuperSurvivor)
            end
            function SuperSurvivor:Get() return self.player end
            function SuperSurvivor:getID() return self.player:getModData().ID end
            function SuperSurvivor:setID(id) self.player:getModData().ID=id end
            function SuperSurvivor:getName() return self.player:getModData().name or 'Test' end
            function SuperSurvivor:getGroupID() return self.player:getModData().Group end
            function SuperSurvivor:setGroupID(id) self.player:getModData().Group=id end
            function SuperSurvivor:getGroupRole() return self.player:getModData().GroupRole end
            function SuperSurvivor:setGroupRole(role) self.player:getModData().GroupRole=role end
            function SuperSurvivor:getGroup() return SSGM:Get(self:getGroupID()) end
            function SuperSurvivor:getAIMode() return nil end
            function SuperSurvivor:refreshName() end
            function SuperSurvivor:newSet(a) return wrap(a) end
            function SuperSurvivor:new(_,s)
                if failConstruct then return nil end
                return wrap(actor(s:getX(),s:getY(),s:getZ()))
            end
            function SuperSurvivor:newLoad(id,s)
                local a=self:loadPlayer(s,id)
                if failWrapper then error('wrapper failed after native load') end
                return wrap(a)
            end
        ''')
        # Execute the production native-loader adapter, not a replica of it.
        source = (CLIENT / '3_Other/SuperSurvivor.lua').read_text()
        adapter = source[source.index('function SuperSurvivor:loadPlayer('):source.index('function SuperSurvivor:WearThis(')]
        self.lua.execute(adapter)
        self.lua.execute('''
            require '0_Utilities/SuperSurvivorPersistence'
            require '2_Group/SuperSurvivorGroupManager'
            require '3_Other/SuperSurvivorManager'
            events.OnInitGlobalModData(true)
            SSM:init()
        ''')

    def test_saved_index_load_unload_and_dead_unindex_without_global_next(self):
        self.lua.execute('''
            local s=SSM:spawnSurvivor(nil,square(4,5,0));events.OnSave()
            SSPersistence.init(false);SSM:init()
            local luaNext=next;next=nil -- Match the installed Kahlua environment.
            SSPersistence.tick();assert(SSM:Get(1))
            assert(SSPersistence.unload(1))
            SSPersistence.tick();assert(SSM:Get(1))
            SSPersistence.markDead(1)
            assert(SSPersistence.keys[1]==nil)
            local nonempty=false;for _ in pairs(SSPersistence.index) do nonempty=true end
            assert(not nonempty)
            next=luaNext
        ''')

    def test_fresh_dynamic_groups_named_areas_and_stable_sparse_ids(self):
        self.lua.execute('''
            assert(SSGM:getCount()==0)
            local a=SSGM:newGroup(); local b=SSGM:newGroup()
            assert(a:getID()==0 and b:getID()==1 and b:getMemberCount()==0)
            a:setGroupArea('CustomZone',12,18,-9,-3,1)
            a:setGroupArea('GuardArea',2,4,6,8,0)
            local s=SSM:spawnSurvivor(nil,square(1,23,0))
            a:addMember(s,'Guard'); events.OnSave()
            local root=copy(SSPersistence.get())
            assert(root.groups[0].areas.CustomZone.x1==12 and root.groups[0].areas.GuardArea.y2==8)
            assert(root.survivors[1].groupID==0)
            SSPersistence.init(false)
            assert(SSGM:getCount()==2 and SSGM:Get(1):getMemberCount()==0)
            assert(SSGM:Get(0):getGroupArea('CustomZone')[3]==-9)
            failConstruct=true;assert(not SSM:spawnSurvivor(nil,square(12,3,0)));failConstruct=false
            local next=SSM:spawnSurvivor(nil,square(12,3,0))
            assert(next:getID()==3)
            assert(SSPersistence.squareKey(1,23,0)~=SSPersistence.squareKey(12,3,0))
        ''')

    def test_save_reload_native_state_and_prevent_duplicate_loads(self):
        self.lua.execute('''
            local s=SSM:spawnSurvivor(nil,square(10.25,20.75,-1))
            s:Get().payload.hand='Hammer';events.OnSave()
            local file=SSPersistence.getRecord(1).saved.file
            -- Last observation can be newer than the native snapshot.
            s:Get().payload.x=99;SSPersistence.observe(s)
            SSPersistence.init(false);SSM:init()
            local loaded=SSM:LoadSurvivor(1,square(10,20,-1))
            assert(loaded and loaded:getID()==1 and loaded:Get():getX()==10.25)
            local state=loaded:Get().payload
            assert(state.hp==77 and state.inventory[2]=='Bandage' and state.skills.Axe==4)
            assert(state.worn[1]=='Jacket' and state.appearance=='test' and state.hand=='Hammer')
            assert(not SSM:LoadSurvivor(1,square(10,20,-1)))
            events.OnSave();assert(SSPersistence.getRecord(1).saved.file~=file)
            assert(checkSaveFileExists(file)) -- earlier checkpoint is not overwritten
        ''')

    def test_unload_keeps_record_and_membership_then_loads_only_available_square(self):
        self.lua.execute('''
            local group=SSGM:newGroup()
            local s=SSM:spawnSurvivor(nil,square(4,5,0));group:addMember(s,'Guard')
            assert(SSPersistence.unload(1))
            assert(not SSM:Get(1) and SSPersistence.getState(1)=='unloaded')
            assert(group:getMemberIDs()[1]==1 and #group:getMembers()==0)
            SSPersistence.loadSquare(square(44,55,0));assert(not SSM:Get(1))
            SSPersistence.loadSquare(square(4,5,0));assert(SSM:Get(1))
            SSPersistence.loadSquare(square(4,5,0));assert(SSM:Get(1):getID()==1)
        ''')

    def test_dead_tombstone_does_not_respawn_or_reuse_id(self):
        self.lua.execute('''
            local group=SSGM:newGroup()
            local s=SSM:spawnSurvivor(nil,square(4,5,0));group:addMember(s,'Leader')
            events.OnSave();s:Get().payload.dead=true;SSM:OnDeath(1);events.OnSave()
            assert(SSPersistence.getState(1)=='dead' and group:getMemberCount()==0 and group.Leader==-1)
            SSPersistence.init(false);SSM:init();SSPersistence.loadSquare(square(4,5,0))
            assert(not SSM:Get(1) and SSPersistence.getState(1)=='dead')
            assert(SSM:spawnSurvivor(nil,square(4,5,0)):getID()==2)
        ''')

    def test_snapshot_write_failure_retains_previous_checkpoint_and_live_actor(self):
        self.lua.execute('''
            local s=SSM:spawnSurvivor(nil,square(1,2,0));events.OnSave()
            local file=SSPersistence.getRecord(1).saved.file
            failSave=true
            assert(not pcall(SSPersistence.unload,1))
            assert(SSM:Get(1)==s and s:Get().loaded and SSPersistence.getRecord(1).saved.file==file)
            failSave=false;events.OnSave()
            assert(SSPersistence.getRecord(1).saved.file~=file)
        ''')

    def test_missing_and_mismatched_snapshots_report_without_replacement(self):
        self.lua.execute('''
            SSM:spawnSurvivor(nil,square(1,2,0));events.OnSave()
            local r=SSPersistence.getRecord(1);local filename=r.saved.file
            local payload=worlds.A.files[filename];worlds.A.files[filename]=nil
            SSPersistence.init(false);SSM:init();local before=actorCount
            SSPersistence.loadSquare(square(1,2,0))
            assert(actorCount==before and SSPersistence.getState(1)=='inconsistent')
            worlds.A.files[filename]=payload;payload.md.SSRIdentity=999
            SSPersistence.init(false);SSM:init()
            assert(not SSM:LoadSurvivor(1,square(1,2,0)))
            assert(SSPersistence.getRecord(1).issue:find('identity/generation',1,true))
            assert(not SSM:Get(1))
        ''')

    def test_world_copy_is_independent_and_unknown_schema_is_rejected(self):
        self.lua.execute('''
            SSM:spawnSurvivor(nil,square(1,2,0));events.OnSave()
            worlds.B=copy(worlds.A);world='B';SSPersistence.init(false);SSM:init()
            assert(SSM:LoadSurvivor(1,square(1,2,0)))
            SSM:Get(1):Get().payload.hp=33;events.OnSave()
            assert(worlds.A.tables[SSPersistence.KEY].survivors[1].saved.file ~= SSPersistence.getRecord(1).saved.file)
            world='A';SSPersistence.init(false);SSM:init()
            assert(SSM:LoadSurvivor(1,square(1,2,0)):Get().payload.hp==77)
            worlds.A.tables[SSPersistence.KEY].schema=999
            assert(not pcall(SSPersistence.init,false) and not SSPersistence.data)
        ''')

    def test_scenarios_create_groups_lazily_and_keep_ids_after_reload(self):
        self.lua.execute('''
            assert(SSGM:getCount()==0)
            local g=SSGM:scenarioGroup('HillTop');local id=g:getID()
            assert(g:getGroupArea('FarmingArea')[1]==11741)
            assert(SSGM:scenarioGroup('HillTop')==g and SSGM:getCount()==1)
            SSPersistence.init(false)
            assert(SSGM:scenarioGroup('HillTop'):getID()==id and SSGM:getCount()==1)
        ''')

    def test_partial_wrapper_failure_does_not_leave_a_live_unregistered_actor(self):
        self.lua.execute('''
            SSM:spawnSurvivor(nil,square(1,2,0));events.OnSave()
            SSPersistence.init(false);SSM:init();failWrapper=true
            assert(not SSM:LoadSurvivor(1,square(1,2,0)))
            assert(not SSM:Get(1) and not SSPersistence.loading[1])
            assert(SSPersistence.getState(1)=='inconsistent')
        ''')

    def test_multiplayer_does_not_initialize_or_write_registry(self):
        self.lua.execute('''
            multiplayer=true;SSPersistence.init(false)
            assert(not SSPersistence.data);events.OnSave()
        ''')

    def test_tick_handles_pending_add_then_unload_and_initial_available_squares(self):
        self.lua.execute('''
            local s=SSM:spawnSurvivor(nil,square(6,7,0))
            s:Get().loaded=false;s:Get().pendingAdd=true
            -- A pending native addition can already have a square.
            s:Get().getCurrentSquare=function() return {} end
            events.OnTick();assert(SSM:Get(1)==s)
            s:Get().pendingAdd=false;squares={}
            events.OnTick();assert(not SSM:Get(1) and SSPersistence.getState(1)=='unloaded')
            square(6,7,0);events.OnTick();assert(SSM:Get(1))
            assert(not SSM:LoadSurvivor(1,square(100,100,0)))
        ''')

    def test_membership_contradiction_is_reported_without_creating_group_or_actor(self):
        self.lua.execute('''
            local group=SSGM:newGroup()
            local s=SSM:spawnSurvivor(nil,square(1,2,0));group:addMember(s,'Guard');events.OnSave()
            SSPersistence.getRecord(1).groupID=999
            SSPersistence.init(false);SSM:init()
            assert(SSPersistence.getState(1)=='inconsistent' and not SSGM:Get(999))
            assert(SSPersistence.get().groups[0].issue)
            SSPersistence.loadSquare(square(1,2,0));assert(not SSM:Get(1))
        ''')

    def test_manifest_cannot_redirect_load_outside_world_owned_snapshot_names(self):
        self.lua.execute('''
            SSM:spawnSurvivor(nil,square(1,2,0));events.OnSave()
            SSPersistence.getRecord(1).saved.file='../other-world/player.bin'
            SSPersistence.init(false);SSM:init()
            assert(SSPersistence.getState(1)=='inconsistent')
            assert(not SSM:LoadSurvivor(1,square(1,2,0)))
        ''')

    def test_save_path_uses_engine_save_root(self):
        source = (ROOT / '42/media/lua/shared/Utilities.lua').read_text()
        adapter = source[source.index('function getSaveDir()'):source.index('function getSourceSquareOfItem')]
        self.lua.execute('''
            getFileSeparator=function() return '/' end
            getWorld=function() return {getGameMode=function() return {toString=function() return 'Sandbox' end} end,
                getWorld=function() return 'Test World' end} end
            getAbsoluteSaveFolderName=function(relative)
                assert(relative=='Sandbox/Test World');return 'CustomCache/Saves/'..relative
            end
        ''')
        self.lua.execute(adapter)
        self.assertEqual(self.lua.eval('getSaveDir()'), 'CustomCache/Saves/Sandbox/Test World/')

    def test_sparse_groups_have_no_slot_limit_and_unloaded_leader_is_preserved(self):
        self.lua.execute('''
            for i=1,20 do SSGM:newGroup() end
            local group=SSGM:Get(19)
            local s=SSM:spawnSurvivor(nil,square(1,2,0));group:addMember(s,'Guard');group:setLeader(1)
            events.OnSave();SSPersistence.unload(1)
            assert(group:hasLeader() and group:getLeader()==1)
            SSPersistence.get().groups[3]=nil
            SSPersistence.get().nextGroupID=0 -- Reconcile a stale high-water mark.
            SSPersistence.init(false)
            assert(SSGM:getCount()==19 and not SSGM:Get(3) and SSGM:Get(19):hasLeader())
            assert(SSGM:newGroup():getID()==20)
        ''')


if __name__ == '__main__':
    unittest.main()
