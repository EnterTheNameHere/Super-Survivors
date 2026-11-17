FROM: Local Codex implementer
TO: SSR Orchestrator
DATE: 2026-11-17
STATUS: SOURCE RESEARCH / EXPERIMENT DESIGN DELIVERED FOR REVIEW
SUBJECT: Combat04 source ordering, writer inventory, Lua boundaries and first-request proposal

Exclusive existing codex/persistence-b42 checkout. Report commit
f2b1686c03dcf04f03e4275fb4344ac83a285ec4; parent
df330ac990d27925f91d4e080c5b296a90acb3a0. Modified report paths:
docs/COMBAT_B42_CORRECTION_OPTIONS_04.md and docs/LOCAL_HANDOFF.md.
ACK publication a3a0bbc9df8935861a626c6c5305769117bb7809.
No production code, AI, UI, inventory, fixture, flag, Java or world changes.

CURRENT SOURCE EVIDENCE, not new runtime proof:
Recomputed installed projectzomboid.jar SHA256 matches prior evidence:
3c4a7c5f149d784758c6fb5f8fa85f3a21d572e38bc081400e89035f8120d287,
B42.22.2 revision 3d39148846. Fresh read-only CFR, independent signature scan,
whole-JAR setter/caller candidate locator followed by matched-source inspection.

1 pressedAttack is public/exposed on IsoPlayer and forwards to native manager;
  no categorical SP nonlocal-NPC rejection in its body. Guards/flags/attack vars
  are initiation only. AttemptAttack/DoAttack funnel back to it; DoAttack even
  returns false after call in this build, not a success API.
2 NEW ordering detail: normal world update -> scheduled actor update, including
  AIComponent.postUpdatePlayer -> later scheduler.postupdate -> actor
  postUpdateAnimating -> ActionContext.update -> AdvancedAnimator.update.
  AI writes initiation from default-false controls before those XML transitions
  consume it; started is not cleared. Early OnPlayerUpdate precedes the AI write.
  Animation can skip or run async. Source mechanism concrete, Roderick's first
  setter/chronology remains unobserved. StopWalk is another initiation clearer.
3 Fresh constructor flags false, AI controls false/zero. Native save/load doesn't
  explicitly restore these flags/controls. SSR load constructs a new actor first;
  loading into existing stuck actor differs and is not a reset guarantee.
4 Full native direct writer inventory includes pressedAttack, clearHandToHand,
  Swipe enter/exit/remote setParams, getup/bumped/bed/sit clears, spear-charge
  contact started=true, network replay. Animation-variable callback can also write
  initiation. None was invoked artificially and no first cause asserted.
5 Lua exposure boundary stronger: IsoPlayer/GameCharacter/Swipe exposed; AIComponent,
  ECSComponent, AIBrainPlayerControlVars and CombatManager not registered in stock
  Exposer. Public component getter/map does not establish exposed AI methods or
  instance-field controls. No reflection/guessed Class token/registration bypass.
6 Native melee listener remains private and requires exact isLocalPlayer before
  collision. SP isLocal is true through NetworkComponent and is DIFFERENT from
  human slots. Native collision has some NPC-aware internals but no supported
  alternative Lua entry/caller established. No claim full native damage can be
  fixed solely by repairing initiation. No slot swap/direct Hit/Java proposed.
7 B41 NPCSetAttack/NPCSetAiming/NPCGetAiming absent installed hierarchy. Historical
  setters/custom damage are not a B42 correction. Candidate/access/stage/
  risk/acceptance matrix and public reference links in report.

RECOMMEND NEXT BOUNDED ASSIGNMENT (DESIGN ONLY):
Existing provenance-known fresh never-attacked NPC, flags false and no swing.
Reject busy/unknown-history-as-first actors. Observe natural request and StopWalk
instance slots exact-once, filtered early OnPlayerUpdate/OnTick/swing/hitpoint;
10sec/600ticks/120lines/8entries, end after first acceptance + short follow-up,
owned cleanup and unchanged native request/AI/player-slot invariants. No request,
provocation, rearm, flags or actor spawn. If no suitable actor, inconclusive;
separately assigned/consented disposable-world fixture only as later fallback.
Independently require proof of supported nonlocal collision and attributable
damage before calling any animation correction a full combat fix.

VALIDATION: source/API/byte provenance audit and git diff --check only. No new
engine tests, gameplay attempts or production test suite run for docs-only task.
Combat02/03 logs untouched; 98 actual false,busy returns still latest runtime
evidence, first accepted request/swing/hit/damage untested. User source/settings/
common saves preserved. Test04 R1 baseline/restart proof pending; Test03 observer
deferred; inventory plan remains on B42 with no implementation. Canonical publish
ai-workflow only, no source merge. Next actor: orchestrator reviews exact report
and orders observation/API research or makes a scope decision on collision limit.
