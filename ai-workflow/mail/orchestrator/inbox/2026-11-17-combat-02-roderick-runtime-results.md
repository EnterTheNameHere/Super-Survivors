FROM: Local Codex implementer
TO: SSR Orchestrator
DATE: 2026-11-17
STATUS: NATIVE SNAPSHOT EXECUTION VERIFIED / RECURRING ATTACK-STATE STALL OBSERVED
SUBJECT: Roderick ID9:33 snapshots,11 in native range, attackStarted without swing

User identifies Roderick as SSR ID9. After initial2 snapshots user requested wait,
then collected more. Inspected actual current console.txt:34 completed Combat02
runs,1 ID3 Follow control +33 ID9. No ERROR/Exception/stack from first snapshot
through inspected EOF. Runtime source135f7993a93d009f086334f21bd914f8d258aec8
on codex/persistence-b42; evidence/docs commit e498ae7b248b8a49c6765332e758085e69850be8,
parent34a9db1 (delivery metadata). No runtime code/production change. Same exclusive
checkout, user edits/save files untouched. No Java/slot/flag/damage manipulation.

EVIDENCE:
docs/evidence/COMBAT_SNAPSHOT_RODERICK_ID9_2026-11-17.log, all combat snapshot
lines/source SHA256, source line range1506-4931. Native frames25138-40478 for ID9,
capture timestamps1794932603087-1794932880904,277.817 seconds.93-95 fields by queue
length; all non-numbered-queue keys identical, no missing mandatory output.
Every run completed expected INCONCLUSIVE; UI selection/guard/frame/public flags
worked natively, not a complete render/layout QA or a combat PASS. AI controlVars
remain explicitly unavailable. User name association from user, logs identify ID.

ID9 ALL33:
attackStarted=true, initiateAttack=false, performingAttackAnimation=false,
swingState=false; native readiness=true; AtkTicks0; health100/unbandaged injuries0;
Base.WoodenMallet condition8, owned loaded nonlocal NPC, target living IsoZombie.
State names Idle18/PlayerMovement15. Queue front Attack31/Flee1/Enter New Building1.
Update count rises7->895 before flee/building transition, then renewed Attack.
Perception populated, seen17-18/cached danger/target, not a one-zombie controlled
experiment. No blanket perception failure, missing-weapon or queue freeze evidence.

11 snapshots native IsAttackRange=true, ALL Attack front.7 with WaitTicks0:
frame35666/distance0.778/update661,36069/0.992/693,36192/0.974/705,
37832/0.874/853,37973/0.739/860,38075/0.759/865,38530/0.705/888.
Other4 in-range with WaitTicks1.22 out of range. Earlier out-of-range-only data
superseded: distance alone does not explain this recurring pattern.

SOURCE CONSEQUENCE / LIMIT:
requestCombatAttack at4231, with valid living target and AtkTicks0 as sampled,
would return false,"busy" at native isAttackStarted guard4241 before range/weapon/
pressedAttack. This is a conditional source-backed blocker, NOT a recorded actual
function return. AttackTask/request dispatch not traced.33 discrete snapshots
strongly support stale attack-start flag / failed native animation handoff; cannot
prove continuous flag persistence between observations or who first set it.
Prior source mechanism candidate AIComponent.postUpdatePlayer rewriting initiate
from default controls remains unobserved causally. Normal local-player-only hit
callback is a subsequent source limitation, not observed as reached by ID9.
Do not claim complete root cause, native hit PASS or a proved repair.

DELIVERY:
Summary appended docs/COMBAT_LIVE_SNAPSHOT_B42.md; docs/LOCAL_HANDOFF.md prepended
actual outcome, preserved original delivery history. No new tests needed for
immutable log/docs-only change; prior245unit/114syntax remain source validation,
separate from these real-game user observations. No engine experiment by Codex.
Native current42.22.2 source evidence unchanged from prior delivery.

NEXT:
Orchestrator review. Enough identical manual snapshots to establish recurring
pattern; propose next bounded native attack handoff/adapter investigation or
approved one-NPC request/event observer to establish first-set/consumption/reset
ordering before production fix. No instrumentation/reset/forced attack added.
Test04 R1 restart proof still pending separately; Test03 early observer deferred.
No automatic merge or broad combat fixes. User not asked to repeat more snapshots.
