# Combat03: contextual diagnostics and bounded handoff trace

17 November 2026. Implementation on codex/persistence-b42. **Native UI/trace NOT
RUN at delivery.** Observation tooling only; no combat fix, actor/flag/slot/visual/
ammo/damage changes, no extra native attack, no Java modification. Earlier evidence
[COMBAT_LIVE_SNAPSHOT_B42.md](COMBAT_LIVE_SNAPSHOT_B42.md) remains unchanged.

## User steps

1. Restart. Enable Superb Survivors -> Debug Options -> On. Native -debug is not
   required and is not enabled by this feature.
2. Open Roderick's **Information** window, either through his world context menu
   or the group window's Information action. Both are reachable legacy UI paths.
3. Click **Diagnostics** at the bottom. **Log combat state** immediately runs the
   same guarded Combat02 capture for exactly this displayed survivor. No SS Tests
   window, repeated survivor selection or destructive-world acknowledgment. The
   button says logged/unavailable; hover for details, not a combat PASS.
4. **Start combat trace (up to 10s)** explicitly observes natural behavior for up
   to10seconds or600ticks,80log lines,30natural request interceptions (first limit
   wins). Let the game run. **Stop combat trace** ends early. Close/hide the owning
   info window to stop its trace. Other info windows do not stop somebody else's.
5. When the button says trace logged, report completion and what you saw. Records
   use `[SS Tests][combat-existing-trace]`; immediate state uses the existing
   `[SS Tests][combat-existing-snapshot]` prefix. The prefix is shared logging,
   not evidence that an SS Test/fixture was launched. No screenshots/pixels recorded.

Only existing living loaded owned SSR ID>0 is eligible, outside all local slots,
singleton and MainPlayer, same world/cell and exact wrapper/actor ownership. The
menu captures its binding; loading a different survivor rejects an old menu action,
never retargets it. Debug off/human/dead/unloaded/replaced actors hide the button.
Selection is derived from existing actor ID, never global last-selected/member index
or legacy PerkCount. Existing info builders still have historical PerkCount writes;
the NEW actions do not rerun Load or use/write that field. This is not a claim the
entire old information builder was already observational.

The normal layout is unchanged without debug. When visible, the new button has a
reserved footer: legacy body shrinks/clips with wheel scrolling; the group-panel
body/Call/Close rows move up30px. Debug-off restores original geometry. Both paths
have mocked lifecycle/normal-size geometry tests; native rendering/resizing/layout
still needs user verification. No Call behavior or other information content changed.

SS Tests also retains **Combat - trace existing survivor**, with explicit ID/name
selection and the existing per-run warning/consent. All mutating tests still need
consent. Contextual actions are dedicated observation endpoints, not a generic
permission bypass: they cannot dispatch arbitrary test definitions, alter consent,
clear cleanupFailure, change SSRTests.active/results, or run a fixture. One trace
may run at a time. Starting a second returns unavailable with reason.

## Scope and implementation

Combat02 private capture is shared via SSRCombatSnapshot.inspect, with its original
read-only guard/capture/output logic. The adapter creates only a small in-memory
logging context, not a test context/actor. Result stays INCONCLUSIVE. Test04 R1
GlobalModData baseline and every production combat/AI/persistence path are unchanged.

SSRCombatTrace stores a frozen flat selection, one active record and one latest
finished record (max80lines). It installs callbacks only on explicit start, removes
them on completion/cancel/deadline/invalid ownership/death/unload/debug-off/world/
menu/new game/reload. OnTick samples compact states; unchanged states are suppressed
except a60tick heartbeat. OnRenderTick only checks guards/deadline (also while
simulation ticks are paused), not combat state. If the application ceases dispatching
callbacks entirely, cleanup runs at the first callback after it resumes; no OS timer.
The normal registry's OnTick already exists; there is no startup monitor or capture.

Compact data: native started/initiate/attack-animation/aiming/state/swing equality,
current cached task/target-reference changes, public native range, WaitTicks/AtkTicks,
wall time/native frame. Samples cannot see every transition between callbacks.
Initial started=true is explicitly PREEXISTING; sampledFalseToTrue counts only
observed adjacent false->true states, not the first native setter or its cause.
AIComponent control object remains unavailable without a verified safe Lua token;
no reflection or speculative getter/mutator is added.

Natural request observation is scoped to that wrapper's raw Lua method slot. The
current ordinary `self:requestCombatAttack(...)` dispatch goes through this slot.
The original resolved Lua function is retained, called exactly once with the same
receiver/arguments, returns preserved by count including trailing nil values.
Other receivers pass straight through. Return/reason and before/after flags are
recorded only while the record is owned/active. No request is invoked by the trace.
If no Lua method exists, interception is explicitly unavailable; passive samples
still work. Direct cached/class-function calls could bypass the instance slot;
zero logged requests is not proof that no native attack anywhere happened.

Cleanup restores the original raw value (often nil, restoring inheritance) only
if our wrapper is still installed. An outside replacement is left untouched. Errors
in observation logging are caught and detach the observer; they never suppress an
original call or alter its results. The production call itself is **not pcall'd,
translated or rethrown**: installed Kahlua pcall returns false/error/stack/Throwable,
and converts native Throwables. Lua5.1 error's numeric level argument also differs
from Kahlua's stack-string argument. Direct original invocation avoids that change.
If a synchronous original call aborts, an in-flight marker stops/restores on the
next tick/render callback (or explicit close/menu/cancel). Its original error
escapes normally; observer adds a Lua stack frame, not a replacement payload.
No new coroutine/yield protocol is supported; the reviewed production path is
synchronous and does not yield. A stopped trace never restarts itself.

Native event callbacks are limited to verified **OnWeaponSwing(attacker,weapon)**
and **OnWeaponSwingHitPoint(attacker,weapon)**. Only identical selected attacker
is counted; unrelated actors ignored. First means swing state entered; second
means native collision routine entered, NOT a successful hit/damage guarantee.
Missing event API is unavailable. No additional event contracts are guessed.
No generic OnHitZombie/OnWeaponHitCharacter listener or damage path is added.

## Installed engine order and limits

Installed42.22.2 rev3d39148846 JAR SHA256
3c4a7c5f149d784758c6fb5f8fa85f3a21d572e38bc081400e89035f8120d287.
Current-JAR source inspection (read-only CFR) retained under .venv/combat03-native
and .venv/combat03-decompiled, alongside prior verified extracts. Relevant ordering:

- GameWindow.render emits OnRenderTick (:785); SSR updates its manager there.
  Natural Lua request hooks run synchronously wherever the existing call occurs.
- IsoPlayer.updateInternal1 calls updateInternal2, then super.update when enabled.
  updateInternal2 invokes NPC AIComponent.postUpdatePlayer near its end (:2546).
  That writes initiateAttack/running/justMoved from humanControlVars before the
  subsequent base-character update. Current source is a mechanism candidate for
  losing an initiation; actual causal transition is not established by snapshots.
- Native pressedAttack has readiness/state guards, sets initiation/started and
  calculates attack vars. Immediate returned flags do not prove animation/hit.
- SwipeStatePlayer.enter clears initiate, computes native attack, emits
  OnWeaponSwing. Its ordinary AttackCollisionCheck callback requires actual local
  player membership before entering native collision, which emits HitPoint.
- IngameState.update calls IsoWorld.update, entity/other updates, then onTick,
  which emits OnTick. Thus a sample is after that update block, not an exact setter
  observation. Cached IngameState bytes were checked against the current JAR.

No native setter, debug reflection, force-update, local-slot swap, direct Hit or
state reset is used to produce a transition. Persistent Roderick started=true
will probably be labeled preexisting/busy, not repaired. A different existing NPC
before its first natural engagement may provide a false->true observation, but
this tooling never creates/provokes one. No continuous-history or root-cause claim.

## Documented / older / replaced / current API matrix

Research inspected17November2026. Public Javadoc is a reference; installed JAR
and exposure are the contract for this build. No downloaded NPC code was executed
or copied into runtime.

| Precedent | Verified status / consequence |
| --- | --- |
| [B41 IsoGameCharacter docs](https://projectzomboid.com/modding41/zombie/characters/IsoGameCharacter.html) | Lists NPCSetAttack/NPCSetAiming/NPCGetAiming. Historical API, not safe B42 names. |
| [B42 character docs](https://projectzomboid.com/modding/zombie/characters/IsoGameCharacter.html) | Older setters absent in document search. Actual installed IsoGameCharacter/IsoLivingCharacter/IsoPlayer member inspection also finds none; no call attempted. |
| [B42 AIComponent docs](https://projectzomboid.com/modding/zombie/characters/component/AIComponent.html) | Public getHumanControlVars/postUpdatePlayer match installed signatures. Native control vars replace that part of behavior, but a safe Lua Class-token path is still unverified. Documentation alone does not establish Lua access. |
| [PZNS weapon helper](https://github.com/Project-Zomboid-Community-Modding/PZNS/blob/20a30212f98aa891aec9cb070bb96164be27c12a/PZNS_Framework/media/lua/client/05_npc_actions/PZNS_WeaponAttack.lua) | Inspected main commit20a30212 (2026-08-15); helper last-path commit f05334fd (2023-09-19). It uses old NPC setters and custom Hit-based damage helpers. Historical design evidence, unsuitable for copying into this native-only B42 path. |
| [PZNS aiming helper](https://github.com/Project-Zomboid-Community-Modding/PZNS/blob/20a30212f98aa891aec9cb070bb96164be27c12a/PZNS_Framework/media/lua/client/05_npc_actions/PZNS_WeaponAiming.lua) | Uses NPCSetAiming/NPCGetAiming. It does not validate those calls on installed B42. |
| [PZNS issue44](https://github.com/Project-Zomboid-Community-Modding/PZNS/issues/44) | Earlier animation/damage timing reports provide precedent, not proof of Roderick's current flag stall. |

## Verification and next action

Dedicated tests cover exact-once receiver/argument/trailing-nil returns, unchanged
error payload/string and deferred cleanup, no extra request/mutation, preexisting
flags/observed transitions, time/tick/log caps, foreign receivers/events/replacements,
owner stop, death/unload/debug/world/menu/new-game/reload, scoped SS cancellation,
contextual snapshot without test/consent mutation, both real info Load paths,
stale menus, hidden/debug-off geometry, close/remove and UI reload. Native API
checks cover removed legacy setters and current control component contract.
Native trace/UI execution NOT RUN; mocks do not demonstrate an engine transition
or native rendering. Full test/syntax/LuaLS results accompany delivery.

Next user action: restart, open Roderick Information, Diagnostics -> Start combat
trace, allow it to finish, report. If only preexisting busy is observed, next review
may need a separately bounded native-control adapter/first-natural-request study.
No speculative fix or repeated manual snapshot loop is installed.


Final isolated delivery validation: **267 tests pass** (no skips with installed
PZ_GAME_DIR), **116/116 Lua5.1 syntax checks pass**; LuaLS retains88 legacy
diagnostics in13files, none new diagnostics/trace/UI code. Native run NOT RUN.


## Actual user traces (17 November 2026)

Native trace execution is now verified; initial delivery NOT RUN statements above
are historical. Preserved full extract:
[evidence/COMBAT_TRACE_2026-11-17.log](evidence/COMBAT_TRACE_2026-11-17.log).
Five traces (ID9, ID1, ID5 three times),400lines total. Every trace stopped at the
80line cap and reported ownedWrapperRestored=true, zero swing/HitPoint events and
zero sampled false->true transitions. All started with attackStarted already true;
none observes its original setter. No actual error/exception/stack or observer
failure occurs from first trace through inspected EOF. Native UI start/logging,
instance dispatch interception, bounded logging and reported restoration worked.
Not all teardown/error/UI resizing paths were exercised natively.

| ID | Native frame span | Duration seconds | Request entries | Complete logged returns |
| --- | --- | --- | --- | --- |
|9(Roderick per user)|3122-3433|2.212|15|15 busy|
|1|7318-7678|2.686|17|16 busy|
|5|13621-13851|1.616|22|21 busy|
|5|14848-15091|1.729|24|23 busy|
|5|16105-16351|1.788|24|23 busy|

**98 observed completed natural requests all returned false,"busy".**102 request
entries total; the four absent return records are censored by the log cap, not
proof of hung/failed calls. The observer stops/restores at the cap even if the
current original request continues normally without further logging. Do not count
these four as success/failure. All15 Roderick entries/returns were captured in
native range, Attack task, cooldown0, native started=true/initiate=false/no swing
or attack animation. ID5 entries likewise native in-range; ID1 uses the close-range
task fallback with native range false, so it also has a range caveat beyond busy.

This advances evidence from conditional source analysis to **actual stage(d)
request rejection**: NPCs do invoke requestCombatAttack, and the busy guard returns
before CombatManager.pressedAttack in the observed completed calls. With the
logged native started=true and cooldown0, that guard is sufficient to block
further requests. Perception/Attack selection and attempted dispatch are working
for these calls; this is not simply a failure to decide to fight. No native swing
or hit transition was seen; it cannot be evaluated from these rejected requests.

Source order still supplies a mechanism candidate (NPC AI control post-update
clears initiate before later base update), but initial true-setting/consumption/
reset chronology was not observed because the state predated all traces. The
root cause of the stale state remains unproven. No reset, native-control adapter,
production fix or extra diagnostic implemented. Repeating already-busy traces
is not needed to establish this rejection; next orchestration decision should
address first natural attack/handoff or a separately reviewed correction path.
