FROM: Local Codex implementer
TO: SSR Orchestrator
DATE: 2026-11-17
STATUS: DELIVERED FOR REVIEW / NATIVE TRACE AND NEW UI NOT RUN
SUBJECT: Combat03 bounded natural-request trace and contextual Information diagnostics

SOURCE: exclusive codex/persistence-b42, W:/Projects/Super-Survivors
COMMIT: a5b166d45e83a7450acc31b135f31cba937332a2
PARENT ACK: a65e33a4606f436623d7023a27b6ae774f9d1e34
START:15d3def4f52c886efb6b9ce2b518d51d15ce8130. All three Combat03 mails incorporated.
Same owner/worktree, user source/settings/common save edits excluded/preserved.
Canonical B42 coordination only, no source merge/acceptance or Java modification.

UI AMENDMENT:
Both paths reachable and updated: context menu -> SurvivorInfoWindow.Load;
group window Information -> show_survivor_info/PanelSurvivorInfo. Shared Diagnostics
menu, exact ID/wrapper/actor/world binding at load/show, revalidated at menu/action/
execution. Stale menu never retargets. Debug-only, excludes human/local/dead/unloaded/
wrong-world/ownership. No repeated NPC selection. Log combat state shares Combat02
capture, dedicated observation context; no T.start/arbitrary dispatch/consent
bypass or alteration of SSRTests.active/results/cleanupFailure. New action does
not rerun legacy Load or use/write PerkCount (old builder writes remain unchanged).
Small logged/unavailable/tracing/trace-logged indicator/tooltip. Reserved footer,
legacy clipped/wheel-scroll text shrinks only when shown; group Call/Close rows
move30px. Debug off restores geometry/no button. Native rendering still untested.

TRACE:
Explicit Start/Stop in Information; optional seventh SS Tests definition retains
normal per-run consent/selection. One active trace globally,10s/600ticks/80lines/
30natural calls bounds (first wins), last record in memory only. OnTick compact
transitions plus60tick heartbeat; OnRenderTick guards/deadline only including pause;
if app dispatch suspends entirely cleanup resumes on first callback, no OS timer.
Owned teardown on stop/cancel/close/hide/rebind/invalid/death/unload/replacement/
debug-off/world/menu/new game/module reload/limits. All owned callback bindings
removed; restore raw instance method only if ours, foreign replacement retained.
Stable module table identity prevents old UI references from creating parallel
observers after trace reload. No automatic startup capture, polling or actor creation.

Per-instance Lua requestCombatAttack override: original current colon-dispatched
function exactly once, identical self/args, all returns counted including trailing
nil, other receivers untouched. Logs ENTRY/POST/actual RETURN incl rejection reason.
No attack called by tooling. Missing Lua method logs interception unavailable and
still passively samples; direct cached/class-function calls may bypass override.
Preexisting started=true explicitly labeled; sampledFalseToTrue is observed samples,
not setter provenance or a continuous trace. No false causal/hit inference.

ERROR-SAFETY DETAIL:
Native KahluaThread.pcall differs from Lua5.1: error tuple false/error/stack/Throwable,
native exceptions converted; BaseLib.error second argument is stack string. Thus
production original is NOT pcall'd/rethrown by the observer. Direct call leaves
its error payload/native exception path intact, with an extra observer Lua frame.
An inFlight marker detects an aborted synchronous original on next tick/render
and detaches/restores; close/menu also cleans. No original error swallowed, no
new coroutine/yield protocol. Own logging/sampling failures are protected, stop
observation and still let original execute once/return unchanged. Lua mock tests
verify table/string error preservation and deferred cleanup. Real Kahlua trace
not executed yet; inspected implementation is evidence, not engine-run proof.

EVENTS / NATIVE ORDER:
Only verified OnWeaponSwing(attacker,weapon) from SwipeStatePlayer and
OnWeaponSwingHitPoint(attacker,weapon) from CombatManager, filtered exact actor.
Swing means entry; HitPoint means collision routine reached, neither proves damage.
No guessed hit contracts, no native event forwarding/replacement. Missing event
API explicitly unavailable. No extra attack, flags/AIvars/setter/task update/
local-slot/Hit/renderer/loader/registry/Java change. Test04 R1 unchanged.

Installed42.22.2 rev3d39148846 JAR SHA256 unchanged
3c4a7c5f149d784758c6fb5f8fa85f3a21d572e38bc081400e89035f8120d287.
Verified IngameState bytes current: world/entity updates precede onTick. Current
IsoPlayer updateInternal2 invokes NPC postUpdatePlayer before subsequent super
update. It writes initiation from AI control vars; still a source mechanism
candidate, not newly observed cause. Natural request pre/post is synchronous,
OnTick snapshots after update block do not identify exact setter.

RESEARCH ADDENDUM:
Matrix with primary links in docs/COMBAT_HANDOFF_TRACE_B42.md. B41 docs list NPCSetAttack/
NPCSetAiming/NPCGetAiming; actual installed GameCharacter/Living/Player members
lack them and B42 doc search agrees. Current AIComponent public getHumanControlVars
signature verified, safe Lua Class token still unestablished/no reflection used.
PZNS main20a30212f98aa891aec9cb070bb96164be27c12a dated2026-08-15 inspected; weapon
helper last path commit f05334fd7223cf8679646f0cd65790d6800db57e dated2023-09-19,
uses old setters/custom Hit helper. Historical precedent not B42 support or code
to copy. Earlier issue44 timing reports not proof of current Roderick flag cause.
No downloaded mod code executed or copied into runtime.

VALIDATION:
267 automated tests PASS (no skips with actual PZ_GAME_DIR),116/116 Lua5.1 syntax
PASS, isolated staged export excluding user working changes.14 trace tests,7
contextual UI tests, API removal/current component regression plus earlier suite.
Covers natural exact-once/args/trailing nil/error, nonselected actors/events,
preexisting vs sampled transitions, bounds, observer failure, teardown/foreign
replacement, both actual Load/show paths, stale menu, consent isolation, layouts,
close/remove/reload and no auto execution. Old parenting fixture isolated its new
dependency; actual diagnostic wiring tested separately. LuaLS88legacy diagnostics
in13files, none new code. Editor API regenerated incl call-name-selected read
signature, source fingerprint; docs links checked. Native UI/trace NOT RUN, no
combat outcome/transition or fix claimed. Prior Roderick evidence preserved.

CHANGED PATHS:
Testing/SSRCombatTrace.lua(new), Testing/SSRCombatSnapshot.lua(shared endpoint),
5_UI/SSRCombatInfoDiagnostics.lua(new),5_UI/SSRTestsWindow.lua(require trace),
5_UI/SurvivorInfoWindow.lua,5_UI/SuperSurvivorInfoPanel.lua(context binding/lifecycle);
tests/test_combat_trace.py(new),test_combat_info_diagnostics.py(new),
test_human_visual_diagnostics.py(7definitions),test_persistence_engine_api.py,
test_release_package.py,test_ui_parenting.py; editor/pz-api/library.lua;
docs/COMBAT_HANDOFF_TRACE_B42.md(new),LOCAL_HANDOFF.md,TESTS_UI.md.
No production AI/combat/survivor source edit.

USER STEPS / NEXT:
Restart, Debug Options On, open Roderick Information -> Diagnostics -> Start combat
trace (up to10s), let run, report when trace logged. Log combat state immediate,
Stop explicit, closing owner cancels. No SS Tests consent needed for these verified
observation-only actions. User may use ordinary SS Tests trace if preferred.
If Roderick starts already flagged true, expect PREEXISTING and natural busy
returns; no repair. Review actual trace before any bounded native adapter/correction.
Fresh existing NPC before first natural fight may be needed to see initial rise,
but no fixture/provocation or repeated manual still sampling added.
Test03 early observer deferred; Test04 R1 restart proof pending separately.
