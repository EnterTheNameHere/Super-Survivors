FROM: Local Codex implementer
TO: SSR Orchestrator
DATE: 2026-11-17
STATUS: SOURCE DIAGNOSIS DELIVERED / NO COMBAT FIX OR DIAGNOSTIC IMPLEMENTED
SUBJECT: SSR-COMBAT-01 active Lua chain and B42 native gates

BRANCH: exclusive existing codex/persistence-b42, W:/Projects/Super-Survivors
REPORT COMMIT: 79c6d10519542b174c5e3c88954615e1de19820a
PARENT ACK: 913d2cef97d954e24ed345fa5d86eec57db72ea4
RUNTIME SOURCE: unchanged from3e99b8f2637616238ac0d02e73d579dd3ccfc1f6.
Test04 R1 delivered first, native save/restart check pending. No concurrent owner.
User source/settings/common save edits excluded and preserved, no source merge.

REPORT: docs/COMBAT_B42_INVESTIGATION_01.md plus docs/LOCAL_HANDOFF.md update.
Trace covers OnRenderTick/manager/updateTime/WaitTicks -> DoVision -> active
role decisions/later priority preemption -> TaskManager validation/completion/
queue cancellation -> AttackTask movement/range/cooldown -> requestCombatAttack
rejections -> native pressedAttack flags/control post-update -> swing/collision.

PROVEN SOURCE FACTS:
- IsoCell.getLuaObjectList returns dense1-based Kahlua table, moving collection
  itself Set; VirtualZombieManager registers new/reused zombies in that set.
  Existing ipairs/key lookup correct. Particular live membership not observed.
- Active AIManager equip branches275/653 impossible: hasWeapon requires held
  HandWeapon, simultaneously checks primary==nil. Inventory weapon not equipped
  can lead non-companion to later unarmed flee. Other loot/equip path still exists.
- PursueTask requires SSM wrapper for target ModData.ID, so ordinary zombie
  pursuit construction returns nil. Same-room Attack has its own movement.
- Active Attack additions at AI-Manager242/399 exist. AIManager_Companion,
  AiNPC_CanAttack and NPCTask_DoAttack are unused paths/helpers (names reversed
  in unused type helper). Do not fix an unused path and claim active repair.
- Both outdoor nil rooms compare equal, so not universally invalid outdoors.
  Injury/fear/role/follow/range/priority/update suppression can still stop combat.
- needToFollow tests method truthiness; AttackTask.Target absent leads -1 distance
  and StopWalk on completion; secondary distinct issues, not universal no-fight proof.

NATIVE CURRENT JAR:
42.22.2 rev3d39148846 SHA256
3c4a7c5f149d784758c6fb5f8fa85f3a21d572e38bc081400e89035f8120d287.
Fresh CFR for IsoCell/CombatManager/AIComponent/control vars/VirtualZombieManager/
IsoZombie; cached relevant class bytes verified identical to actual JAR.
- NPC isAiming reads AIComponent humanControlVars.aiming; setIsAiming writes
  ordinary field. postUpdatePlayer writes initiateAttack/running/justMoved from
  control vars. No SSR writes to these vars. Exact flag-vs-action consumption
  ordering still needs runtime observation, not proof every swing suppressed.
- Native pressedAttack can reject hand-model readiness/hand-to-hand/hit states,
  independent of SSR WeaponReady (which MUTATES gun/ammo/actions). Immediate
  initiate/attackStarted success doesn't guarantee animation or damage.
- Normal SwipeStatePlayer AttackCollisionCheck callback requires actual local
  player membership. Standalone NPC outside local slots fails that route even
  if swing starts. Not proof observed NPC reached it or no other native route exists.
  No NPC local-slot swap, Java change or victim:Hit workaround authorized/proposed.

LIVE EVIDENCE: current console lacks owned-NPC perception/decision/request/event
history. Cannot yet assign observed incident to(a)-(e). No combat engine run,
no diagnostic installed, no damage or animation success claim. Original Test04
human observations delivered separately; they don't diagnose combat.

CHECKS: source-only Lupa witnesses passed against isolated intended runtime
source: equip contradiction3hand states, outdoor/indoor room equality, ordinary
zombie pursuit rejection, follow method-truthiness skip. Existing230 tests and
113syntax passed preceding R1 tree; no code changes in this docs-only audit, no
new tests pinning defects as desired behavior. Native source facts distinguished
from Lua mocks/user observation. No live save written or manipulated.

PROPOSAL: next bounded user-invoked readOnly existing-owned-NPC snapshot in gated
SS Tests, ID>0 validated, cached perception/task queue/policy inputs plus safe
native readiness/state flags. Don't call mutating predicate/task/update/readiness
functions merely to inspect; getLuaObjectList also replaces global Objects.
Bounded passive request-return/event observation only if snapshot insufficient,
separately reviewed, scoped ownership/timeout/cancel/restoration, no extra attacks.
No automatic spawn/provocation/hit or arbitrary cleanup; future fixture requires
fresh explicit consent/disposable world. Review equip/pursue narrow fixes and
regressions separately; public Lua control/collision adapter remains to verify.

NEXT ACTOR: orchestrator reviews report and authorizes bounded diagnostic/fix
assignment. Test04 R1 user restart/capture/save/restart/AFTER pending separately.
Test03 earliest observer remains DEFERRED, not implemented. No automatic merge.
