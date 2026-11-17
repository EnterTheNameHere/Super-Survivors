"""Passive trace exact-once dispatch, bounded lifetime and observer ownership."""
import unittest
import test_combat_snapshot as snapshot_fixture


class CombatTraceChecks(unittest.TestCase):
    def setUp(self):
        f = snapshot_fixture.CombatSnapshotChecks()
        f.setUp()
        self.lua = f.lua
        self.lua.execute('''
            calls=0;nativeStarted=false
            npcActor.isAttackStarted=function() return nativeStarted end
            original=function(self,...)
                calls=calls+1;received={n=select('#',...),...};receivedSelf=self
                return false,'busy',nil,42,nil
            end
            local proto={requestCombatAttack=original};setmetatable(npc,{__index=proto})
            require 'Testing/SSRCombatTrace';R=SSRCombatTrace
            function start() local r,why=R.start(choice(),npc);assert(r,why);return r end
            function callbackCount()
                local n=0;for _,list in pairs(events) do n=n+#list end;return n
            end
        ''')

    def test_no_startup_callbacks_or_requests_and_context_snapshot_does_not_start_test(self):
        self.lua.execute('''
            local n=callbackCount();fire('OnTick');assert(not R.active and calls==0)
            local old=SSRTests.active;local r=SSRCombatSnapshot.inspect(choice())
            assert(r.observations and SSRTests.active==old and not SSRTests.results[D.id])
            assert(callbackCount()==n and mutations==0)
        ''')

    def test_original_exactly_once_untouched_arguments_and_trailing_nil_returns(self):
        self.lua.execute('''
            local before=callbackCount();local r=start();assert(calls==0)
            local token={};local result={n=select('#',npc:requestCombatAttack(token,nil,8))}
            assert(result.n==5 and calls==1 and receivedSelf==npc)
            assert(received.n==3 and received[1]==token and received[2]==nil and received[3]==8)
            local a,b,c,d,e=npc:requestCombatAttack(token)
            assert(calls==2 and a==false and b=='busy' and c==nil and d==42 and e==nil)
            assert(r.requests==2 and table.concat(r.output,'|'):find('reason=busy',1,true))
            R.stop(npc,'done');assert(not rawget(npc,'requestCombatAttack') and npc.requestCombatAttack==original)
            assert(callbackCount()==before and mutations==0)
        ''')

    def test_error_object_propagates_unchanged_and_original_raw_method_restored(self):
        self.lua.execute('''
            local err={reason='original'}
            local fn=function() calls=calls+1;error(err) end
            rawset(npc,'requestCombatAttack',fn);local r=start()
            local ok,actual=pcall(npc.requestCombatAttack,npc,{})
            assert(not ok and actual==err and calls==1)
            fire('OnRenderTick') -- production errors are not caught/rethrown by observer
            assert(not R.active and r.finished and rawget(npc,'requestCombatAttack')==fn)
        ''')

    def test_initial_started_is_preexisting_and_new_transition_only_when_observed(self):
        self.lua.execute('''
            nativeStarted=true;local r=start()
            assert(table.concat(r.output,'|'):find('PREEXISTING',1,true) and r.rises==0)
            fire('OnTick');assert(r.rises==0 and calls==0)
            nativeStarted=false;fire('OnTick');nativeStarted=true;fire('OnTick')
            assert(r.rises==1);R.stop(npc,'done');assert(mutations==0)
        ''')

    def test_error_string_is_not_prefixed_or_rethrown_by_observer(self):
        self.lua.execute('''
            local fn=function() error('original string',0) end
            rawset(npc,'requestCombatAttack',fn)
            local _,baseline=pcall(fn,npc)
            local r=start();local ok,actual=pcall(npc.requestCombatAttack,npc)
            assert(not ok and actual==baseline)
            fire('OnTick');assert(r.finished and rawget(npc,'requestCombatAttack')==fn)
        ''')

    def test_bounds_time_even_paused_ticks_and_tick_cap(self):
        self.lua.execute('''
            local before=callbackCount();local r=start()
            clock=clock+10001;fire('OnRenderTick')
            assert(r.finished and r.reason:find('deadline',1,true) and callbackCount()==before)
            r=start();for i=1,600 do fire('OnTick') end
            assert(r.finished and r.reason:find('tick cap',1,true) and #r.output<=80 and calls==0)
        ''')

    def test_natural_request_log_cap_stops_observer_without_dropping_original_call(self):
        self.lua.execute('''
            local r=start()
            for i=1,60 do npc:requestCombatAttack({}) end
            assert(calls==60 and r.finished and #r.output<=80)
            assert(npc.requestCombatAttack==original and not R.active)
        ''')

    def test_other_receivers_and_actors_are_not_instrumented_or_counted(self):
        self.lua.execute('''
            local r=start();local other={};npc.requestCombatAttack(other,17)
            assert(calls==1 and receivedSelf==other and r.requests==0)
            for _,fn in ipairs(events.OnWeaponSwing or {}) do fn(player,{}) end
            assert(r.swings==0)
            for _,fn in ipairs(events.OnWeaponSwing or {}) do fn(npcActor,{}) end
            assert(r.swings==1);R.stop(npc,'done')
        ''')

    def test_external_replacement_is_not_overwritten_by_cleanup(self):
        self.lua.execute('''
            local r=start();local replacement=function() end
            npc.requestCombatAttack=replacement;R.stop(npc,'done')
            assert(r.restored==false and npc.requestCombatAttack==replacement)
        ''')

    def test_death_unload_replacement_and_debug_off_teardown(self):
        self.lua.execute('''
            local before=callbackCount();local r=start();npcActor.payload.dead=true;fire('OnTick')
            assert(r.finished and callbackCount()==before);npcActor.payload.dead=false
            r=start();npcActor.loaded=false;fire('OnRenderTick');assert(r.finished);npcActor.loaded=true
            r=start();SSM.SuperSurvivors[7]={player=npcActor};fire('OnTick');assert(r.finished)
            SSM.SuperSurvivors[7]=npc;r=start();enabled=false;fire('OnRenderTick');assert(r.finished)
        ''')

    def test_world_menu_game_start_and_module_reload_teardown(self):
        self.lua.execute('''
            local r=start();world='B';fire('OnTick');assert(r.finished);world='A'
            r=start();fire('OnMainMenuEnter');assert(r.finished)
            r=start();fire('OnGameStart');assert(r.finished)
            r=start();package.loaded['Testing/SSRCombatTrace']=nil;require 'Testing/SSRCombatTrace'
            assert(r.finished and SSRCombatTrace==R and not R.active and npc.requestCombatAttack==original)
        ''')

    def test_stale_selection_and_owner_stop_cannot_cancel_another_trace(self):
        self.lua.execute('''
            local p=choice();p.id=99;assert(not R.start(p,npc))
            local r=start();assert(not R.start(choice(),{}))
            assert(not R.stop({},'foreign close') and R.active==r)
            R.stop(npc,'own close');assert(r.finished)
        ''')

    def test_observer_logging_failure_does_not_change_natural_request_result(self):
        self.lua.execute('''
            local r=start();print=function() error('observer log failure') end
            local a,b,c,d,e=npc:requestCombatAttack({})
            assert(calls==1 and a==false and b=='busy' and c==nil and d==42 and e==nil)
            assert(r.finished and npc.requestCombatAttack==original)
        ''')

    def test_ss_tests_cancel_stops_only_owned_trace_and_no_mutation_calls(self):
        self.lua.execute('''
            traps()
            -- Natural-call spy kept; the observation itself must not invoke it.
            assert(SSRTests.start('combat-existing-trace',true,choice()))
            fire('OnTick');assert(R.active and calls==0)
            SSRTests.cancel('cancel');assert(not R.active and mutations==0 and calls==0)
        ''')


if __name__ == '__main__':
    unittest.main()
