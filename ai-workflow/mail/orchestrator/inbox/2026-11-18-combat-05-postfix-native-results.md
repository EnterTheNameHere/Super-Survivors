FROM: Local Codex implementer
TO: SSR Orchestrator
DATE: 2026-11-18
STATUS: POST-FIX SAMPLING/STOPWALK/CAP VERIFIED; FIRST NATURAL REQUEST UNOBSERVED
SUBJECT: Two full Combat05 runs, no errors, all sampled targets out of native range

User requested log check. Runtime source c69ff48099395a82f9ea6de6b8b5d0e705d9253e
on exclusive codex/persistence-b42, singleton guard correction installed.
Evidence/docs commit31826ae27c608ae78e5b24ae41f6a405153dc5ac,
parentc1f0f229a67a22451f1fbfd51ab3c1788d88297f. No runtime code changes this turn.
Preserved190records + consoleSHA256:
docs/evidence/COMBAT_FIRST_ATTACK_POSTFIX_2026-11-18.log.
Updated docs/COMBAT_FIRST_NATURAL_ATTACK_B42.md and docs/LOCAL_HANDOFF.md.

ID1 frames20028-20628,108records,8.820seconds,600tick cap,StopWalk2.
ID3 frames22549-23149,82records,8.451seconds,600tick cap,StopWalk6.
Both requests0/accepted0/swingEvents0/hitPointEvents0/sampledFalseToTrue0;
restored=requestCombatAttack:true,StopWalk:true. No error/exception/stack from
first observation through inspected EOF. Initial false flags remain false in
all samples, weapons Golfclub/Hammer, readytrue, target present. EVERY recorded
range check false. ID1 tasks Follow/Attack/Flee; ID3 Follow/Attack and fence state.

VERIFIED: guard correction allows early OnPlayerUpdate sampling, bounded natural
StopWalk interception,600tick cap and reported owned-hook restoration. NOT VERIFIED:
natural request interception/acceptance/initial setter/error propagation/swing/
collision/damage or both Information layouts. Sampled range/state cannot rule out
an unsampled transient. Do not diagnose a movement bug solely from these records.
Both are valid INCONCLUSIVE first-attack results, not failed tests or combat fix.
Next useful evidence is eligible existing actor's normal close-range engagement;
do not repeat identical out-of-range captures or force attacks/spawn/reset flags.

Checks: evidence parsing/record counts, source console error search, diff --check.
No suite rerun for documentation-only update; prior291tests/117syntax remain
historical source checks. No production/AI/diagnostic behavior edits, user source/
settings/common saves untouched. Test04R1 pending/Test03 deferred/inventory deferred.
Canonical ai-workflow only, no merge. Next orchestrator reviews native evidence;
first transition and independent native-damage path still outstanding.
