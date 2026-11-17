"""One-shot combat observations against real registry; native calls are mocks."""
import unittest

import test_persistence_lifecycle as fixture_module


class CombatSnapshotChecks(unittest.TestCase):
    def setUp(self):
        fixture = fixture_module.LifecycleChecks()
        fixture.setUp()
        self.lua = fixture.lua
        self.lua.execute('''
            mutations=0
            function forbidden() mutations=mutations+1;error('forbidden mutation/update') end
            npcActor=actor(3,2,0);npcActor.npc=true;npcActor.kind='IsoPlayer';npcActor.payload.md.ID=7
            npcActor.payload.md.Name='Ada';npcActor.payload.md.GroupRole='Companion'
            npcActor.payload.md.AIMode='Follow';npcActor.payload.md.BravePoints=4
            npcActor.getCell=function() return cell end
            npcActor.current.getRoom=function() return nil end
            npc={player=npcActor,MyTaskManager={Tasks={},TaskCount=0,TaskUpdateCount=0,TaskUpdateLimit=0},
                seenCount=0,dangerSeenCount=0,EnemiesOnMe=0,Reducer=20,UpdateDelayTicks=20,
                WaitTicks=0,AtkTicks=0,WalkingPermitted=true,TriggerHeldDown=false,SwipeStateTicks=0}
            SSM.SuperSurvivors[7]=npc
            local flags={isRunning=false,isBlockMovement=true,isAiming=false,isAttackStarted=false,
                isInitiateAttack=false,isPerformingAttackAnimation=false,isPerformingShoveAnimation=false,
                isAimAtFloor=false,isDoShove=false,isAuthorizedHandToHand=true,isAuthorizedHandToHandAction=true,
                canPerformHandToHandCombat=true,isWeaponReady=true}
            for name,value in pairs(flags) do local v=value;npcActor[name]=function() return v end end
            local swipe={};SwipeStatePlayer={instance=function() return swipe end}
            npcActor.getCurrentState=function() return {} end
            npcActor.getCurrentStateName=function() return 'Idle' end
            npcActor.IsAttackRange=function() return false end
            local oldBody=npcActor.getBodyDamage
            npcActor.getBodyDamage=function()
                local body=oldBody();body.getBodyParts=function() return {
                    size=function() return 2 end,get=function(_,i) return {
                        HasInjury=function() return i==0 end,bandaged=function() return false end} end} end
                return body
            end
            held=nil;npcActor.getPrimaryHandItem=function() return held end
            function armed()
                held={kind='HandWeapon',getFullType=function() return 'Base.Hammer' end,
                    getCondition=function() return 9 end,isAimedFirearm=function() return false end,
                    getCurrentAmmoCount=function() return 0 end,isContainsClip=function() return false end,
                    isRoundChambered=function() return false end,isJammed=function() return false end}
            end
            instanceof=function(o,kind) return o and o.kind==kind end
            function enemy()
                local e=actor(4,2,0);e.kind='IsoZombie';e.current.getRoom=function() return nil end
                npc.LastEnemeySeen=e;npc.seenCount=1;npc.dangerSeenCount=1
                return e
            end
            function traps()
                for _,name in ipairs({'DoVision','getLuaObjectList','WeaponReady','ReadyGun','RealCanSee',
                    'needToFollow','isTooScaredToFight','NPC_CheckPursueScore','update','updateTime'}) do npc[name]=forbidden end
                npc.MyTaskManager.update=forbidden
                npcActor.pressedAttack=forbidden;npcActor.update=forbidden;npcActor.resetModel=forbidden
                npcActor.setNpc=forbidden;npcActor.setBlockMovement=forbidden
                npcActor.save=forbidden;npcActor.load=forbidden;npcActor.setIsAiming=forbidden
                npcActor.getAnimationPlayer=forbidden;npcActor.getECSComponent=forbidden
                SSM.UpdateFilter=forbidden;cell.getLuaObjectList=forbidden
                ZombRand=forbidden;getDebug=forbidden
                ModData.getOrCreate=forbidden;SSM.spawnSurvivor=forbidden;IsoPlayer.new=forbidden
            end
            getGameSpeed=function() return 1 end;OnTickTicks=99
            require 'Testing/SSRCombatSnapshot'
            C=SSRCombatSnapshot;D=SSRTests.definitions['combat-existing-snapshot']
            function choice()
                local list=C.choices();for _,p in ipairs(list) do if p.id==7 then return p end end
                error('choice missing')
            end
            function inspect(p)
                assert(SSRTests.start(D.id,true,p or choice()))
                fire('OnTick');return SSRTests.results[D.id]
            end
            function clean()
                assert(mutations==0 and slots[0]==player and singleton==player and npcActor.payload.md.ID==7)
            end
        ''')

    def test_no_auto_execution_callbacks_or_world_data_creation(self):
        self.lua.execute('''
            local before=copy(worlds.A.tables);traps()
            C.choices();fire('OnTick');fire('OnGameStart');fire('OnTick')
            assert(not SSRTests.results[D.id] and not SSRTests.active)
            assert(not ModData.get('SSR.Tests.Combat') and not SSRTests.bootToken);clean()
        ''')

    def test_no_target_snapshot_is_inconclusive_not_broken_perception(self):
        self.lua.execute('''
            local p=choice();traps();local result=inspect(p)
            assert(result.status=='INCONCLUSIVE' and not result.observations.targetPresent)
            assert(result.summary:find('No target at snapshot',1,true))
            assert(result.observations.fields['native.AIComponent.controlVars']:find('UNAVAILABLE',1,true))
            assert(result.observations.fields['native.swingState']=='false')
            assert(result.observations.fields['actor.unbandagedInjuries']=='1')
            assert(result.observations.fields['weapon.equippedHandWeapon']=='false')
            assert(not SSRTests.bootToken and #result.lines<200);clean()
        ''')

    def test_cached_enemy_equipment_queue_and_flags_are_preserved_without_predicates(self):
        self.lua.execute('''
            armed();local e=enemy()
            npc.MyTaskManager.Tasks[0]={Name='Attack',isValid=forbidden,isComplete=forbidden,update=forbidden}
            npc.MyTaskManager.TaskCount=1;npcActor.isAttackStarted=function() return true end
            npcActor.isInitiateAttack=function() return true end
            local p=choice();traps();local result=inspect(p);local f=result.observations.fields
            assert(result.status=='INCONCLUSIVE' and f['queue.front']=='Attack')
            assert(f['target.class']=='IsoZombie' and f['target.sameRoom']=='true')
            assert(f['native.isAttackStarted']=='true' and f['native.isInitiateAttack']=='true')
            assert(f['native.isAiming']=='false' and f['weapon.fullType']=='Base.Hammer')
            assert(npc.LastEnemeySeen==e and held:getCondition()==9 and npc.AtkTicks==0)
            assert(npc.MyTaskManager.Tasks[0].Name=='Attack' and npc.seenCount==1);clean()
        ''')

    def test_wrong_id_and_missing_explicit_selection(self):
        self.lua.execute('''
            local p=choice()
            assert(not SSRTests.start(D.id,true))
            for _,id in ipairs({0,-1,1.5,2147483648,'7',99}) do
                p.id=id;assert(not SSRTests.start(D.id,true,p))
            end
            p.id=0/0;assert(not SSRTests.start(D.id,true,p));clean()
        ''')

    def test_dead_unloaded_and_unregistered_are_rejected(self):
        self.lua.execute('''
            local p=choice();npcActor.payload.dead=true
            assert(not SSRTests.start(D.id,true,p));assert(#C.choices()==0)
            npcActor.payload.dead=false;npcActor.loaded=false
            assert(not SSRTests.start(D.id,true,p))
            npcActor.loaded=true;local square=npcActor.current;npcActor.current=nil
            assert(not SSRTests.start(D.id,true,p));npcActor.current=square
            npcActor.getCell=function() return {} end
            assert(not SSRTests.start(D.id,true,p));clean()
        ''')

    def test_human_singleton_main_player_and_all_local_slots_excluded(self):
        self.lua.execute('''
            local p=choice()
            for i=1,3 do slots[i]=npcActor;assert(not SSRTests.start(D.id,true,p));slots[i]=nil end
            singleton=npcActor;assert(not SSRTests.start(D.id,true,p));singleton=player
            SSM.MainPlayer=7;assert(not SSRTests.start(D.id,true,p));SSM.MainPlayer=0
            npcActor.isLocalPlayer=function() return true end
            assert(not SSRTests.start(D.id,true,p));clean()
        ''')

    def test_ownership_world_and_cell_selection_cannot_be_reused(self):
        self.lua.execute('''
            local p=choice();p.world='different';assert(not SSRTests.start(D.id,true,p))
            p.world=world;p.cell={};assert(not SSRTests.start(D.id,true,p))
            p.cell=cell;npcActor.payload.md.ID=8;assert(not SSRTests.start(D.id,true,p))
            npcActor.payload.md.ID=7
            SSM.SuperSurvivors[7]={player=npcActor};assert(not SSRTests.start(D.id,true,p));clean()
        ''')

    def test_start_freezes_selection_and_tick_revalidates_owned_actor(self):
        self.lua.execute('''
            local p=choice();assert(SSRTests.start(D.id,true,p));p.id=99
            fire('OnTick');assert(SSRTests.results[D.id].observations.id==7)
            p=choice();assert(SSRTests.start(D.id,true,p))
            local other=actor(3,3,0);SSM.SuperSurvivors[7].player=other
            fire('OnTick');local result=SSRTests.results[D.id]
            assert(result.status=='SETUP ERROR' and not result.observations)
            assert(mutations==0)
        ''')

    def test_missing_native_fields_are_unavailable_not_false(self):
        self.lua.execute('''
            local p=choice();npcActor.isWeaponReady=nil;npcActor.getCurrentState=nil
            npcActor.isInitiateAttack=nil;traps()
            local f=inspect(p).observations.fields
            assert(f['native.isWeaponReady']:find('UNAVAILABLE',1,true))
            assert(f['native.isInitiateAttack']:find('UNAVAILABLE',1,true))
            assert(f['native.swingState']:find('UNAVAILABLE',1,true));clean()
        ''')

    def test_queue_and_selection_enumeration_are_bounded(self):
        self.lua.execute('''
            local p=choice();npc.MyTaskManager.TaskCount=1000
            for i=0,999 do npc.MyTaskManager.Tasks[i]={Name='Wait'} end
            traps();local result=inspect(p)
            assert(result.observations.fields['queue.truncated']=='true')
            assert(result.observations.fields['queue.11']=='Wait' and not result.observations.fields['queue.12'])
            assert(#result.lines<200);clean()
        ''')

    def test_read_only_consent_cleanup_gate_and_no_rng(self):
        self.lua.execute('''
            local p=choice();local fault={};SSRTests.cleanupFailure=fault;traps()
            assert(not SSRTests.start(D.id,false,p));inspect(p)
            assert(SSRTests.cleanupFailure==fault and not SSRTests.bootToken);clean()
        ''')

    def test_repeat_observations_do_not_accumulate_polling_or_write_history(self):
        self.lua.execute('''
            local p=choice();traps()
            inspect(p);npc.seenCount=4;inspect(p)
            assert(SSRTests.results[D.id].observations.fields['perception.seenCount']=='4')
            local old=SSRTests.results[D.id];fire('OnTick');assert(SSRTests.results[D.id]==old)
            assert(not C.history and not C.baseline);clean()
        ''')

    def test_missing_moddata_is_not_created_and_build_guard_is_exact(self):
        self.lua.execute('''
            local p=choice();npcActor.hasModData=function() return false end
            npcActor.getModData=forbidden;assert(not SSRTests.start(D.id,true,p))
            assert(#C.choices()==0)
            local core=getCore();core.getGameAndBuildVersion=function() return '42.23' end
            getCore=function() return core end
            assert(not SSRTests.start(D.id,true,p));clean()
        ''')


if __name__ == '__main__':
    unittest.main()
