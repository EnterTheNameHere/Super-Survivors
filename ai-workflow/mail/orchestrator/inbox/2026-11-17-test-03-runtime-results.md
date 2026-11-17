# SSR-TEST-03 actual restart comparison

FROM: Local Codex
TO: SSR orchestrator
STATUS: INCONCLUSIVE overall; positive native/metadata evidence, live X/Y differs
DATE: 2026-11-17

User reports Test run. Captured archived staging log (09:02 session) and current
restart/resume console (09:03 session). Implementation e6f08e05b3ec3805a1c8394d8de2f7dab8e261d9
plus next compatibility fix 786c8ea0c0d8aeb4c2dbf35b99bcb4f91839c415;
pre-evidence source head 2735d42308f803263dc2fdc3452ca5c13edb0979.
B42.22.2; canonical B42 coordination only, no production merge/acceptance.

Real SSR fixture ID 2/group 3 staged; actual OnSave at 09:03:21 published
SSR_Survivor_2_4.bin, generation 4, XYZ 9885.5/12824.5/0. Explicit restart-confirming
resume read native snapshot: every compared field matches the OnSave baseline.
Reconstructed live actor matches identity/generation, token/name/group/role,
inventory, equipment/worn types, zero Axe XP/level, health=100/dead=false.
Registry/group/runtime roster/leader match, actors/wrappers/records=1/1/1,
square/world membership valid. Human/all four slot guard unchanged; native
reader cleanup succeeded. No new probe exception or repeated global-next error.
Unrelated startup errors remain outside this result.

ONLY failed property comparisons are live X/Y: 9888.5/12828.3349609375 at resume.
Final status INCONCLUSIVE as designed, consistent with AI movement before click.
No earliest reconstruction observation proves when the change occurred, so do
not call full PASS, infer loader defect or adjust coordinates from this run.

Coverage limit: Axe XP was already 0 in saved baseline despite setup AddXP call.
Nonzero XP retention therefore untested; inspect fixture/native XP rules before
claiming it. Health=100 and Z=0 likewise have no injury/vertical differential.
No streaming/death/multi-group acceptance. No code fix or additional experiment
performed under this record-only update. Recommend reviewing read-only earliest
observation or bounded fixture control; do not merely ignore position comparisons.

Filtered evidence docs/evidence/SSR_RESTART_2026-11-17.log includes source hashes.
Results in docs/PERSISTENCE_LIVE_TESTS.md, TESTS_UI.md and LOCAL_HANDOFF.md.
Record validation: log assertions confirm native fields match and live mismatches
are exactly X/Y; links/whitespace checked. No tests rerun for documentation-only
update. Next actor: orchestrator reviews actual evidence and assigns next step.
