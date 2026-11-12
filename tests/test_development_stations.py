"""Station orchestration, state checks, prompts and session restoration."""
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime

CLIENT = Path(__file__).resolve().parents[1] / '42/media/lua/client'


class StationChecks(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute((CLIENT / '7_Tasks/TaskManager.lua').read_bytes())
        self.lua.execute('''
            debugMode=true;clock=0;messages={}
            function getDebug() return debugMode end
            function isClient() return false end
            function isServer() return false end
            function getTimestampMs() return clock end
            function inventory()
                local inv={items={}}
                function inv:AddItem(name) local item={name=name};self.items[item]=true;return item end
                function inv:contains(item) return self.items[item]==true end
                function inv:getItemCount(name) local count=0;for item in pairs(self.items) do if item.name==name then count=count+1 end end;return count end
                return inv
            end
            source=inventory();destination=inventory()
            player={Say=function(_,s) table.insert(messages,s) end,getInventory=function() return source end}
            function getSpecificPlayer() return player end
            body={bandaged=function() return treated==true end,setScratched=function() treated=false end,setBleedingTime=function() end}
            damage={RestoreToFullHealth=function() end,getBodyPart=function() return body end}
            character={isDead=function() return false end,getInventory=function() return destination end,
                getBodyDamage=function() return damage end}
            tm=TaskManager:new({})
            probe={WaitTicks=7,getID=function() return 12 end,Get=function() return character end,
                getTaskManager=function() return tm end,StopWalk=function() end,
                Wait=function(self,n) self.WaitTicks=n;waited=n end,isInAction=function() return busy==true end}
            SSM={Get=function(_,id) if id==0 then return {} end;assert(id==12);return probe end}
            oldFilter=function() return true end;SSM.UpdateFilter=oldFilter
            ISTimedActionQueue={clear=function() end}
            SuperbSurvivorsDebug={spawnStationary=function() spawns=(spawns or 0)+1;return probe end}
            package.preload['Debug/SuperbSurvivorsDebug']=function() end
            package.preload['0_Utilities/SuperSurvivorTransferUtilities']=function() end
            SuperSurvivorTransfers={queue=function() return true end}
            package.preload['7_Tasks/FirstAideTask']=function() end
            FirstAideTask={new=function() return {Name='First Aide',isComplete=function() return false end} end}
            BodyPartType={ForeArm_L={}}
            Events={OnTick={Add=function(callback) tickCallback=callback end,Remove=function() end},
                OnGameStart={Add=function(callback) worldCallback=callback end,Remove=function() end}}
        ''')
        self.lua.execute((CLIENT / 'Debug/SuperbSurvivorsTests.lua').read_bytes())

    def test_manual_result_reuse_prompts_and_session_restoration(self):
        self.lua.execute('''
            assert(spawns==nil)
            local t=SuperbSurvivorsTests
            t.start('stationary')
            assert(spawns==1 and t.active.result=='awaiting observation' and #messages>=2)
            assert(SSM.AutoSpawnsSuspended and tm.AIEnabled==false)
            assert(SSM.UpdateFilter(probe) and not SSM.UpdateFilter({}))
            assert(not pcall(t.start,'stationary'))
            assert(not pcall(t.record,'yes'))
            t.record(true,'both visible')
            assert(t.active==nil and t.lastResult.note=='both visible')
            t.start('stationary');assert(spawns==1 and waited==36000)
            t.endSession()
            assert(t.session==nil and SSM.AutoSpawnsSuspended==nil and SSM.UpdateFilter==oldFilter)
            assert(tm.AIEnabled==nil and probe.WaitTicks==7)
        ''')

    def test_normal_play_cannot_start_station(self):
        self.lua.execute('''
            debugMode=false
            assert(not pcall(SuperbSurvivorsTests.start,'stationary'))
            assert(spawns==nil and SSM.AutoSpawnsSuspended==nil)
        ''')

    def test_inventory_requires_all_item_identities_and_reports_missing_items(self):
        self.lua.execute('''
            local t=SuperbSurvivorsTests;t.start('inventory')
            local active=t.active
            t.tick();assert(t.active==active)
            for _,item in ipairs(active.items) do source.items[item]=nil;destination.items[item]=true end
            clock=1000;t.tick();assert(t.active==nil and string.find(t.lastResult.result,'PASS'))
            t.start('inventory');source.items[t.active.items[1]]=nil
            t.tick();assert(t.active==nil and string.find(t.lastResult.result,'FAIL'))
        ''')

    def test_inventory_waits_for_player_to_approach_instead_of_raising_capacity_error(self):
        self.lua.execute('''
            local t=SuperbSurvivorsTests
            SuperSurvivorTransfers.queue=function() return false,'Stand nearby','out_of_reach' end
            t.start('inventory');local active=t.active
            t.tick();assert(t.active==active and active.queued==0 and active.step==1)
            SuperSurvivorTransfers.queue=function() return true end
            clock=1000;t.tick();assert(active.queued==3 and active.step==2)
        ''')

    def test_medical_requires_consumption_as_well_as_bandaging(self):
        self.lua.execute('''
            local t=SuperbSurvivorsTests;t.start('medical')
            t.tick();assert(t.active)
            treated=true
            clock=1000;t.tick()
            assert(t.active==nil and string.find(t.lastResult.result,'FAIL'))
            t.start('medical');treated=true
            for item in pairs(destination.items) do destination.items[item]=nil;break end
            t.tick();assert(t.active==nil and string.find(t.lastResult.result,'PASS'))
        ''')

    def test_failed_setup_can_be_ended_and_restores_previous_settings(self):
        self.lua.execute('''
            local t=SuperbSurvivorsTests
            t.stations.broken={expected='failure fixture',setup=function() error('setup failed') end}
            local ok,reason=pcall(t.start,'broken')
            assert(not ok and string.find(reason,'setup failed') and t.active==nil)
            t.endSession();assert(SSM.AutoSpawnsSuspended==nil and SSM.UpdateFilter==oldFilter)
        ''')

    def test_world_transition_discards_old_probe_ids_and_isolation(self):
        self.lua.execute('''
            local t=SuperbSurvivorsTests;t.start('stationary')
            worldCallback()
            assert(t.active==nil and t.session==nil and next(t.slots)==nil)
            assert(SSM.AutoSpawnsSuspended==nil and SSM.UpdateFilter==oldFilter)
        ''')

    def test_sequence_waits_for_observation_then_stops_on_failure(self):
        self.lua.execute('''
            local t=SuperbSurvivorsTests
            t.stations.patrol={expected='controlled setup failure',setup=function() error('blocked lane') end}
            t.runAll()
            t.tick();assert(t.active.name=='stationary' and t.pendingStation==nil)
            t.record(true,'visible');assert(t.pendingStation=='patrol')
            local ok,reason=pcall(t.tick)
            assert(not ok and string.find(reason,'blocked lane'))
            assert(t.sequence==nil and t.active==nil and t.pendingStation==nil)
            t.endSession();assert(SSM.UpdateFilter==oldFilter)
        ''')

    def test_doctor_result_requires_disinfection_and_bandage_consumption(self):
        self.lua.execute('''
            local t=SuperbSurvivorsTests
            local bandage=destination:AddItem('Base.Bandage')
            local active={name='doctor',part={bandaged=function() return true end,
                getAlcoholLevel=function() return alcohol or 0 end},inventory=destination,
                supplyCount=1,survivor=probe}
            destination.items[bandage]=nil
            assert(t.stations.doctor.check(active)==false)
            alcohol=1
            assert(t.stations.doctor.check(active)==true)
        ''')

    def test_session_restores_flags_even_if_fixture_cleanup_raises(self):
        self.lua.execute('''
            local t=SuperbSurvivorsTests;t.start('stationary')
            tm:AddToTop({Name='bad cleanup',OnCancel=function() error('cleanup failed') end})
            local ok,reason=pcall(t.endSession)
            assert(not ok and string.find(reason,'cleanup failed'))
            assert(t.session==nil and SSM.AutoSpawnsSuspended==nil and SSM.UpdateFilter==oldFilter)
            assert(tm.AIEnabled==nil)
        ''')

    def test_doctor_spawns_patient_near_doctor_instead_of_player(self):
        self.lua.execute('''
            package.preload['7_Tasks/DoctorTask']=function() end
            package.preload['TimedActions/ISDisinfect']=function() end
            package.preload['TimedActions/ISApplyBandage']=function() end
            DoctorTask={new=function() return {Name='Doctor'} end}
            character.getX=function() return 10 end;character.getY=function() return 20 end;character.getZ=function() return 0 end
            destination.FindAndReturn=function() return {} end
            local otherCharacter={isDead=function() return false end,getBodyDamage=function() return damage end}
            local otherTM=TaskManager:new({})
            local patient={Get=function() return otherCharacter end,getID=function() return 13 end,
                getTaskManager=function() return otherTM end,Wait=function() end,StopWalk=function() end}
            SuperbSurvivorsDebug.spawn=function(x,y,z)
                assert(x==11 and y==20 and z==0);spawnedNearDoctor=true;return patient
            end
            function getCell() return {getGridSquare=function() return {
                getFloor=function() return true end,isFree=function() return true end,isCanSee=function() return true end} end} end
            function getDistanceBetween() return 100 end
            local t=SuperbSurvivorsTests;t.start('doctor')
            assert(spawnedNearDoctor and t.active.patient==patient)
            assert(tm.Tasks[0].Patient==otherCharacter)
            t.tick();assert(t.active and t.active.step==1)
        ''')
