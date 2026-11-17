FROM: Local Codex implementer
TO: SSR Orchestrator
DATE: 2026-11-17
STATUS: IMPLEMENTED / AUTOMATED CHECKS PASS / NATIVE EXECUTION PENDING
SUBJECT: Combat05 explicit earliest-natural-attack observer delivered

Exclusive existing codex/persistence-b42 checkout, one owner, no inventory work.
Source commit bfcbf6fd9f7b667b6e9c13ade1123553d87554ff; parent
9facaae08f13733cc922b405fbfd05895e31ec3d. ACK publication
d18c66c0cd64fcb0cc74d27a3b247de258f3d6e5.

MODIFIED PATHS:
42/media/lua/client/Testing/SSRCombatFirstAttack.lua (new)
42/media/lua/client/Testing/SSRCombatTrace.lua (mutual exclusion/reload only)
42/media/lua/client/5_UI/SSRCombatInfoDiagnostics.lua
tests/test_combat_first_attack.py (new)
tests/test_combat_info_diagnostics.py
docs/COMBAT_FIRST_NATURAL_ATTACK_B42.md (new)
docs/LOCAL_HANDOFF.md

BEHAVIOR:
Both existing Information paths have explicit Diagnostics Start earliest natural
attack observation / Stop. Requires existing loaded/live/nonlocal NPC, started
false, initiation false, no known active swing/attack animation. Rejects already
started, unavailable flags or missing Lua methods; no reset/fixture/spawn. Always
earliest OBSERVED: current registry has no verified never-attacked provenance.

Two selected wrapper raw slots only: requestCombatAttack and StopWalk, exact-once
resolved original, original receiver/args/trailing nil results. Direct production
call, no pcall/catch/rethrow, Kahlua original error escapes through observer frame.
In-flight depth handles nested natural StopWalk and deferred aborted-call cleanup.
Other receivers pass straight through. Observer errors detach without replacing
natural call results. External raw replacements are retained; other owned hook
restored. No Java method/global class interception or cached native setter hook.

Frozen ID/wrapper/actor/world/cell/Information binding and human singleton,
MainPlayer/all four slots; revalidate at callbacks/call boundaries. Identity-filtered
early OnPlayerUpdate, OnTick, swing/hitpoint. Native flags/state/shove/aim/running/
block/readiness/weapon, cached task/target/range/timers recorded with timestamp/frame.
Only reviewed pure getters, no lazy model/animation/attack-var/AI reads. Moving
target positions/timers alone don't spend pre-request budget, no heartbeat flood.
Sampled flag rises explicitly not native setter observation. Hitpoint not damage.

Hard first-wins 10s/600ticks/120lines/8natural entries; requests still run exactly
once when observation stops at cap, including nested calls. First accepted request
or owned swing/hitpoint starts 3-tick follow-up; hard caps still win. Deadlines via
render watchdog while ticks paused. No eligible request -> INCONCLUSIVE.
Stop/close/hide/rebind, actor invalidation, world/menu/new session, debug off,
slots/control change, reload/error/limits restore owned hooks/remove callbacks.
No passive capture/auto rearm; retains latest bounded in-memory result only.
Legacy snapshot/trace remain; observers mutually exclusive. No SS Tests scenario,
consent/state bypass or generic test dispatch.

CHECKS (isolated export of intended staged source, not user working-copy edits):
PZ_GAME_DIR=G:/Steam/steamapps/common/ProjectZomboid
python -m unittest discover -s <isolated-root>/tests -v: 290 passed, no skips.
python <isolated-root>/tools/check_lua.py: 117/117 Lua5.1 compiled.
Installed Lua action/constructor checks run under mocks, not native game proof.
LuaLS check Warning with installed vanilla/stub libraries: 88 pre-existing
warnings in13files, same baseline, none in changed diagnostics. diff --check pass.
New regressions cover both methods/returns/errors/foreign receiver, nested calls,
first-observed labels, follow-up/caps, missing events/errors, stale actors/slots/
world/debug, hook restoration/replacement, no start without click, no mutation,
simultaneous Information windows, stale menu/user callbacks/hide/close/reload.

NATIVE USE PENDING: restart to load update. Enable mod Debug Options, existing
survivor Information -> Diagnostics -> Start earliest natural attack observation
(up to10s). Keep Information visible and let normal AI run. Reject started actor
and choose another existing eligible one; do not reset/spawn/provoke. Console
prefix [SS Combat][first-natural-attack]. Report ran/visible outcome. No-request
or rejection is valid evidence. No special destructive-test acknowledgment.

LIMITS: no actual fresh first request/swing/collision/damage observed in this task.
Current runtime evidence remains prior98busy returns. Early event/tick samples
are not exact setters and animation can be skipped/threaded. Three ticks may not
span a slow clip. Original native Kahlua errors/UI rendering need game validation.
Separate native isLocalPlayer collision barrier unchanged; no damage solution
claimed. ZWare setup noted, no unsupported interaction attribution.
No production combat/AI/inventory/flags/actions/player-slot/Java/save changes.
User source/settings/common saves preserved; Test04 R1 baseline/restart proof
pending, Test03 early observer deferred. Source pushed separately; canonical
publication ai-workflow only. No merge/acceptance. Next orchestrator reviews
exact source; user runs explicit diagnostic, then independent native-damage review.
