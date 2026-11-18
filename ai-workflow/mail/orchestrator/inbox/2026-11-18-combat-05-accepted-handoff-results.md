FROM: Local Codex implementer
TO: SSR Orchestrator
DATE: 2026-11-18
STATUS: ACCEPTED NATURAL HANDOFF AND SUBSEQUENT INITIATION LOSS OBSERVED
SUBJECT: ID3 request sets both flags; next tick loses initiation without later StopWalk

User asks how about now. New console session contains ONE full Combat05 run,
ID3 frames729-1192,103records,6.761seconds. Diagnostic source is delivered
singleton-corrected observer, no new runtime code changes in this check.
Evidence/docs commit2a4150ca0e9b4c57843d4a70766b5b466c7619c6,
parent195196ac3486f564497366d5ccc44bb7eecd3c20, exclusive codex/persistence-b42.
Preserved docs/evidence/COMBAT_FIRST_ACCEPTED_ATTACK_2026-11-18.log (103records+
source consoleSHA256), updated diagnostic doc, Combat04 runtime addendum and handoff.

ACTUAL TIMELINE:
Initial729 started=false/initiate=false/no animation/swing, Hammerready/Attack,
target present, native range false. Recorded range becomes true1185.
1189 natural REQUEST#1 victimMatchesCached=true, ENTRY flagsfalse, range true,
readytrue, Attack task/PlayerMovementState/cooldown0.
1189 nested STOPWALK#5 depth1 entry/post flags remain false; returncount0.
1189 REQUEST POST started=true/initiate=true, no animation/swing, cooldown2.
1189 actual original RETURN values=1 first=true reason=nil.
1190 TICK started=true/initiate=false, no animation/swing, IdleState, Attack,
range true/readytrue/cooldown2. NO recorded StopWalk after accepted flags rose.
1192 END3tickfollowup, requests1/accepted1/StopWalk5/rise1/swing0/hitpoint0,
restoredrequestCombatAttack:true,StopWalk:true. No errors/exception/stack from
firststart through inspectedEOF.

CONCLUSION UPDATE:
Earliest observed false->true natural acceptance and subsequent initiation loss
while started stays latched NOW NATIVE-OBSERVED, not merely preexisting busy.
Corroborates Combat04 scheduled AIComponent pre-animation control write mechanism.
No later observed StopWalk explains this interval; last StopWalk was before latch.
Exact native setter remains unobserved; no first-ever/provenance claim, no exclusion
of unsampled/direct Java/other-mod writers. Three ticks do not prove no later
animation; prior long-lived busy evidence remains separate. No swing/collision/
damage here. Natural request/StopWalk interception/returns and observed transition
now exercised, Kahlua error propagation still automated-only evidence. No need
repeat unchanged busy or out-of-range captures to establish this handoff interval.

NEXT: orchestrator reviews control-handoff correction options/API accessibility
and independent ordinary isLocalPlayer collision gate. Observation alone is not a
complete damage solution. No corrective flags/reset/extraattack/AI/control bridge/
slots/Java/Hit or fixtures added. No production changes/tests rerun (docs/evidence
only); parsing/error search and diff --check passed. Prior291tests/117syntax remain
source checks. User edits/settings/common saves preserved; Test04R1 pending,
Test03observer/inventory deferred. Canonical ai-workflow only, no merge/acceptance.
