"""Earliest natural attack observer; native getters/events are mocks, never engine proof."""
import unittest
import test_combat_snapshot as snapshot_fixture


class CombatFirstAttackChecks(unittest.TestCase):
    def setUp(self):
        f = snapshot_fixture.CombatSnapshotChecks()
        f.setUp()
        self.lua = f.lua
        self.lua.execute('''
            requests=0;walks=0;nativeStarted=false;nativeInitiate=false
            npcActor.isAttackStarted=function() return nativeStarted end
            npcActor.isInitiateAttack=function() return nativeInitiate end
            requestOriginal=function(self,...)
                requests=requests+1;received={n=select('#',...),...};requestSelf=self
                return false,'busy',nil,42,nil
            end
            walkOriginal=function(self,...)
                walks=walks+1;walkArgs={n=select('#',...),...};walkSelf=self
                return 'walk',nil,7,nil
            end
            setmetatable(npc,{__index={requestCombatAttack=requestOriginal,StopWalk=walkOriginal}})
            require 'Testing/SSRCombatFirstAttack';F=SSRCombatFirstAttack;R=SSRCombatTrace
            baselineCallbacks={}
            for _,list in pairs(events) do for _,fn in ipairs(list) do baselineCallbacks[fn]=true end end
            function window()
                local w={visible=true,ssCombatSelection=choice()}
                w.getIsVisible=function(self) return self.visible end
                return w
            end
            w=window()
            function start() local r,why=F.start(w.ssCombatSelection,w);assert(r,why);return r end
            function callbackCount() local n=0;for _,list in pairs(events) do n=n+#list end;return n end
            function event(name,...)
                local copy={};for _,fn in ipairs(events[name] or {}) do copy[#copy+1]=fn end
                -- Existing persistence callbacks need full runtime actors; exercise
                -- only callbacks registered by the observer under test here.
                for _,fn in ipairs(copy) do if not baselineCallbacks[fn] then fn(...) end end
            end
            function output(r) return table.concat(r.output,'|') end
            function clean(r,before)
                assert(r.finished and not F.active)
                assert(not rawget(npc,'requestCombatAttack') and not rawget(npc,'StopWalk'))
                assert(npc.requestCombatAttack==requestOriginal and npc.StopWalk==walkOriginal)
                assert(callbackCount()==before and mutations==0)
            end
        ''')

    def test_no_callbacks_or_capture_without_explicit_start(self):
        self.lua.execute('''
            local before=callbackCount();event('OnTick');event('OnPlayerUpdate',npcActor)
            assert(not F.active and not F.last and before==callbackCount())
            assert(requests==0 and walks==0 and mutations==0)
            assert(not F.start(choice(),nil))
        ''')

    def test_both_originals_exact_once_receiver_arguments_trailing_nils(self):
        self.lua.execute('''
            local before=callbackCount();local r=start();local token={}
            local a,b,c,d,e=npc:requestCombatAttack(token,nil,8)
            assert(a==false and b=='busy' and c==nil and d==42 and e==nil)
            assert(requests==1 and requestSelf==npc and received.n==3)
            assert(received[1]==token and received[2]==nil and received[3]==8)
            assert(select('#',npc:StopWalk(token,nil))==4)
            assert(walks==1 and walkSelf==npc and walkArgs.n==2 and walkArgs[1]==token)
            assert(r.requests==1 and r.walks==1 and output(r):find('reason=busy',1,true))
            local foreign={};local hook=npc.requestCombatAttack;hook(foreign,token,nil)
            assert(requests==2 and requestSelf==foreign and r.requests==1)
            npc.StopWalk(foreign,token);assert(walks==2 and r.walks==1 and walkSelf==foreign)
            F.stop(w,'done');clean(r,before)
        ''')

    def test_error_objects_and_strings_escape_each_original_unchanged(self):
        for name in ('requestCombatAttack', 'StopWalk'):
            for error_kind in ('object', 'string'):
                with self.subTest(name=name, kind=error_kind):
                    self.setUp()
                    self.lua.globals().method = name
                    self.lua.globals().errorKind = error_kind
                    self.lua.execute('''
                        local err=errorKind=='object' and {} or 'original string'
                        local count=0;local fn=function() count=count+1;error(err,0) end
                        rawset(npc,method,fn);local r=start()
                        local ok,actual=pcall(npc[method],npc)
                        assert(not ok and actual==err and count==1 and r.inFlight==1)
                        event('OnRenderTick');assert(r.finished and rawget(npc,method)==fn)
                        assert(output(r):find('original error was not intercepted',1,true))
                    ''')

    def test_nested_stopwalk_and_sampled_first_transition_with_three_tick_followup(self):
        self.lua.execute('''
            local before=callbackCount()
            requestOriginal=function(self,...)
                requests=requests+1;self:StopWalk(...);nativeStarted=true;nativeInitiate=true
                return true,nil,nil
            end
            getmetatable(npc).__index.requestCombatAttack=requestOriginal
            local r=start();local task={Name='Attack'};npc.MyTaskManager.Tasks[0]=task
            assert(select('#',npc:requestCombatAttack({}))==3)
            assert(requests==1 and walks==1 and r.requests==1 and r.walks==1 and r.rises==1)
            assert(r.accepted==1 and r.followAt==3 and r.inFlight==0)
            assert(output(r):find('STOPWALK #1 ENTRY depth=1',1,true))
            assert(output(r):find('earliest OBSERVED only',1,true) and not output(r):find('first-ever=true',1,true))
            nativeInitiate=false;event('OnPlayerUpdate',npcActor);event('OnTick');event('OnTick')
            assert(F.active==r and output(r):find('EARLY OnPlayerUpdate started=true initiate=false',1,true))
            event('OnTick');clean(r,before)
            assert(nativeStarted and not nativeInitiate and npc.MyTaskManager.Tasks[0]==task)
        ''')

    def test_only_selected_update_and_event_identity_is_observed(self):
        self.lua.execute('''
            local before=callbackCount();local r=start();local n=#r.output
            event('OnPlayerUpdate',player);event('OnWeaponSwing',player);event('OnWeaponSwingHitPoint',player)
            assert(#r.output==n and r.swings==0 and r.hitPoints==0)
            event('OnWeaponSwing',npcActor);event('OnWeaponSwingHitPoint',npcActor)
            assert(r.swings==1 and r.hitPoints==1 and r.followAt==3)
            for i=1,3 do event('OnTick') end
            clean(r,before);assert(output(r):find('not proof of damage',1,true))
        ''')

    def test_preexisting_started_and_unavailable_flags_reject_without_hooks(self):
        self.lua.execute('''
            local n=callbackCount();nativeStarted=true
            local r,why=F.start(w.ssCombatSelection,w);assert(not r and why:find('Already',1,true))
            nativeStarted=false;npcActor.isAttackStarted=nil;assert(not F.start(w.ssCombatSelection,w))
            assert(not rawget(npc,'requestCombatAttack') and callbackCount()==n)
        ''')

    def test_initiation_animation_non_npc_and_local_actor_rejected(self):
        self.lua.execute('''
            nativeInitiate=true;assert(not F.start(w.ssCombatSelection,w));nativeInitiate=false
            npcActor.isPerformingAttackAnimation=function() return true end
            assert(not F.start(w.ssCombatSelection,w));npcActor.isPerformingAttackAnimation=function() return false end
            npcActor.npc=false;assert(not F.start(w.ssCombatSelection,w));npcActor.npc=true
            local old=getSpecificPlayer;getSpecificPlayer=function(i) return i==0 and npcActor or old(i) end
            assert(not F.start(w.ssCombatSelection,w) and not rawget(npc,'StopWalk'))
        ''')

    def test_deadline_while_paused_no_request_is_inconclusive(self):
        self.lua.execute('''
            local before=callbackCount();local r=start();clock=clock+10000;event('OnRenderTick')
            clean(r,before);assert(r.requests==0 and output(r):find('INCONCLUSIVE',1,true))
            assert(r.reason:find('deadline',1,true) and requests==0 and walks==0)
        ''')

    def test_tick_cap_and_no_heartbeat_fill(self):
        self.lua.execute('''
            local before=callbackCount();local r=start();local initial=#r.output
            for i=1,599 do event('OnTick') end
            assert(F.active==r and #r.output==initial and requests==0)
            event('OnTick');clean(r,before);assert(r.reason=='600 tick cap')
        ''')

    def test_moving_target_and_timers_alone_do_not_exhaust_pre_request_log(self):
        self.lua.execute('''
            enemy();local r=start();local n=#r.output
            for i=1,200 do
                npc.WaitTicks=i;npc.AtkTicks=i
                npc.LastEnemeySeen.getX=function() return i end
                event('OnTick');event('OnPlayerUpdate',npcActor)
            end
            assert(F.active==r and #r.output==n)
            F.stop(w,'done');assert(mutations==0)
        ''')

    def test_missing_event_setup_failure_restores_both_raw_slots_and_callbacks(self):
        self.lua.execute('''
            local before=callbackCount();Events.OnWeaponSwingHitPoint={}
            local r,why=F.start(w.ssCombatSelection,w)
            assert(not r and why:find('API unavailable',1,true));clean(F.last,before)
        ''')

    def test_observer_does_not_duplicate_registration_and_trace_reload_tears_down(self):
        self.lua.execute('''
            local before=callbackCount();local r=start();local n=callbackCount()
            assert(not F.start(w.ssCombatSelection,w) and callbackCount()==n)
            package.loaded['Testing/SSRCombatTrace']=nil;require 'Testing/SSRCombatTrace'
            clean(r,before)
        ''')

    def test_nested_request_cap_and_actor_invalidated_inside_original_preserve_results(self):
        self.lua.execute('''
            local before=callbackCount()
            local count=0
            requestOriginal=function(self)
                count=count+1;if count<10 then return self:requestCombatAttack() end
                return false,'nested',nil
            end
            getmetatable(npc).__index.requestCombatAttack=requestOriginal
            local r=start();local a,b,c=npc:requestCombatAttack()
            assert(a==false and b=='nested' and c==nil and count==10 and r.requests==8)
            clean(r,before)
            requestOriginal=function() npcActor.loaded=false;return 'untouched',nil,7 end
            getmetatable(npc).__index.requestCombatAttack=requestOriginal
            r=start();a,b,c=npc:requestCombatAttack()
            assert(a=='untouched' and b==nil and c==7);clean(r,before)
        ''')

    def test_eight_request_cap_and_120_line_cap_preserve_natural_calls(self):
        self.lua.execute('''
            local before=callbackCount();local r=start()
            for i=1,8 do npc:requestCombatAttack({}) end
            clean(r,before);assert(r.requests==8 and requests==8 and #r.output<=120)
            assert(r.reason:find('8 natural',1,true))
            r=start();for i=1,80 do npc:StopWalk() end
            clean(r,before);assert(walks==80 and r.reason:find('line cap',1,true) and #r.output==120)
        ''')

    def test_owner_window_and_selection_cancellation(self):
        self.lua.execute('''
            local before=callbackCount();local r=start();assert(not F.stop({},'foreign close'))
            w.visible=false;event('OnRenderTick');clean(r,before);w.visible=true
            r=start();w.ssCombatSelection=choice();event('OnTick');clean(r,before)
            r=start();F.stop(w,'user stopped');clean(r,before)
        ''')

    def test_stale_actor_life_world_debug_and_slot_guards(self):
        for change in (
            'npcActor.payload.dead=true', 'npcActor.loaded=false',
            'SSM.SuperSurvivors[7]={player=npcActor}', 'npc.player=player',
            "world='B'", 'enabled=false', 'npcActor.npc=false',
            'getSpecificPlayer=function() return player end',
            'SSM.MainPlayer=99',
        ):
            with self.subTest(change=change):
                self.setUp()
                self.lua.execute('local before=callbackCount();local r=start();'+change+'''
                    event('OnRenderTick');clean(r,before)
                ''')

    def test_outside_method_replacement_is_retained_other_owned_hook_restored(self):
        self.lua.execute('''
            local before=callbackCount();local r=start();local replacement=function() end
            npc.StopWalk=replacement;event('OnTick')
            assert(r.finished and npc.StopWalk==replacement and not rawget(npc,'requestCombatAttack'))
            assert(callbackCount()==before and output(r):find('StopWalk:false',1,true))
        ''')

    def test_native_update_singleton_changes_do_not_imply_human_ownership(self):
        self.lua.execute('''
            local before=callbackCount();local r=start()
            -- Installed updateInternal2 assigns instance=this before this event.
            IsoPlayer.getInstance=function() return npcActor end
            event('OnPlayerUpdate',npcActor);event('OnTick')
            assert(F.active==r and not r.finished)
            local result=SSRCombatSnapshot.inspect(w.ssCombatSelection)
            assert(result and result.observations.id==7)
            -- The observation must never depend on this process-wide update cursor.
            IsoPlayer.getInstance=forbidden
            event('OnPlayerUpdate',npcActor);npc:requestCombatAttack({});event('OnTick')
            assert(F.active==r and r.requests==1)
            F.stop(w,'done');clean(r,before)
            r=start();event('OnPlayerUpdate',npcActor);F.stop(w,'done');clean(r,before)
        ''')

    def test_reload_menu_session_and_observer_failure_cleanup(self):
        for action in (
            "event('OnMainMenuEnter')", "event('OnGameStart')",
            "package.loaded['Testing/SSRCombatFirstAttack']=nil;require 'Testing/SSRCombatFirstAttack'",
            "print=function() error('logger failed') end;npc:requestCombatAttack({})",
        ):
            with self.subTest(action=action):
                self.setUp()
                self.lua.execute('local before=callbackCount();local r=start();'+action+'''
                    clean(r,before);assert(SSRCombatFirstAttack==F)
                ''')

    def test_conflicting_legacy_trace_is_rejected_in_both_directions(self):
        self.lua.execute('''
            local before=callbackCount();local r=start()
            assert(not R.start(choice(),{}));F.stop(w,'done');clean(r,before)
            local legacy=assert(R.start(choice(),{}));assert(not F.start(w.ssCombatSelection,w))
            R.stop(nil,'done');assert(callbackCount()==before)
        ''')

    def test_readonly_getters_never_call_mutators_lazy_models_or_ai(self):
        self.lua.execute('''
            traps();local before=callbackCount();local oldTask=npc.MyTaskManager.Tasks
            local slots={};for i=0,3 do slots[i]=getSpecificPlayer(i) end
            local instance=IsoPlayer.getInstance();local r=start()
            event('OnPlayerUpdate',npcActor);event('OnTick');event('OnRenderTick')
            F.stop(w,'done');clean(r,before)
            assert(requests==0 and walks==0 and npc.MyTaskManager.Tasks==oldTask)
            assert(IsoPlayer.getInstance()==instance)
            for i=0,3 do assert(getSpecificPlayer(i)==slots[i]) end
        ''')


if __name__ == '__main__':
    unittest.main()
