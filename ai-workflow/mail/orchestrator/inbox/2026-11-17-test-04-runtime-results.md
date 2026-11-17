FROM: Local Codex implementer
TO: SSR Orchestrator
DATE: 2026-11-17
STATUS: ORIGINAL TEST04 EXECUTION VERIFIED / NO SYMPTOM REPRODUCTION CLAIMED
SUBJECT: Actual original human diagnostic runs checked before R1

User ran all three controls. Inspected console.txt source lines 1497-1779:
baseline timestamp 1794918818017, changed 1794918909857, invisible 1794918931559.
Each logged all 83 fields; no missing/extra comparison entries. Baseline PASSED
means capture only; both AFTERs INCONCLUSIVE. All readable stable fields and actor,
descriptor, visual, model, four slots/singleton refs unchanged; only X/Y/world time
changed. isInvisible/ghost/sprite/culling false, alpha/target1, getDoRender true,
model present, texture creator absent. Actor/descriptor skin indices3/-1 and
separate visual handles already differ at baseline; no corruption conclusion.
25 unavailable:23 debug raw reads,1 unsafe animation getter skipped,1 absent texture
creator. Native debug false. No ERROR/Exception/stack after first run to inspected
log end. Earlier engine asset/map errors not attributed to controls. User has not
confirmed symptom present at comparison; no root cause/rendered-pixel PASS claimed.
Preserved full test-only extract docs/evidence/HUMAN_VISUAL_2026-11-17.log and source
hash, committed on implementation ref in 3e99b8f2637616238ac0d02e73d579dd3ccfc1f6.
This evidence is original session-only tooling, NOT R1 native save/restart proof.
