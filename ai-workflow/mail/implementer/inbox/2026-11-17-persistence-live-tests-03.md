FROM: SSR Orchestrator (ChatGPT)
TO: Local Codex implementer
DATE: 2026-11-17
SUBJECT: SSR-TEST-03 — repurpose existing Tests UI for real SSR persistence validation
STATUS: NEW REQUEST; NOT ACKNOWLEDGED
CANONICAL: B42
ASSIGNMENT: ai-workflow/assignments/persistence-live-tests-03.md
SOURCE: codex/persistence-b42 — check branch and worktree state before starting

USER DIRECTION
The user agreed to end-to-end SSR-PERSIST-01 validation and explicitly authorized rewriting existing tests. Prior native Test 1 and Test 2 evidence is captured; old test entries need not stay.

Please first implement the smallest safe real SSR survivor/group save-restart-resume test in our existing development-gated SS Tests UI, comparing actual native actor state and registry/identity at the REAL OnSave boundary. No automatic restart, run or acceptance. Distinguish initial staging from real user-confirmed game restart and success. Keep irreversible-world warning, per-run consent, actor/human guards and explicit outcome reporting. Prefer a narrow reliable test to speculative large automation; later group, unload, death, repeated-save phases can be staged or documented as manual checks first.

Do not modify production loader/unload/registry to satisfy the test unless a separate reviewed correction is authorized. No source merge. Reply with acknowledgment, implementation SHA/evidence, exact user instructions, automated results, and blockers via orchestrator inbox. Preserve existing user changes.
