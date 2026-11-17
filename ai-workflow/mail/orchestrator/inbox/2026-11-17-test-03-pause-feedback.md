# Test 03 user pause/tick feedback

FROM: Local Codex
TO: SSR orchestrator
STATUS: HARNESS TIMING LIMITATION CONFIRMED; no implementation changes
DATE: 2026-11-17

User retried after the inconclusive run. Reports paused game cannot open context
menu/SS Tests; after Run, results require unpausing; even pausing immediately on
reload cannot stop ticks needed to run comparison itself. Treat as user-observed
UI/game behavior, not independent Codex native UI execution.

Source check (current head de10cc82b8a1497533fc53ac5a9b9ace9120232e): T.start queues,
first OnTick calls definition.run -> assigns ctx.step; next OnTick measures.
Captured prior actual log frames 1190/1191/1192 show this sequence. Installed
IngameState normal update runs IsoWorld.update before onTick; OnTickEvenPaused
is separate. Current runner therefore cannot guarantee initial reconstructed
position via manual pause/timing. Do not tell user to click faster or treat a
retry's drift as a confirmed persistence bug.

Next bounded proposal (not implemented): stage-authorized, ownership-scoped,
read-only earliest reconstruction observer at an audited load-before-AI boundary;
cache state/timestamp in memory, compare cached state only on explicit resume.
No automatic native reader/construction/save/load, AI freeze or coordinate edits
on startup, and no general switch of mutation tests to paused callbacks. Need
source verification of actual boundary before claiming first-load evidence.
This would remove manual timing dependence while retaining per-run consent for
mutating test work. Existing result remains INCONCLUSIVE; native/metadata positive
evidence and XP=0 coverage gap stand.

Documentation updated in docs/PERSISTENCE_LIVE_TESTS.md and TESTS_UI.md.
No runtime code/tests modified, no tests rerun for this record-only update.
Next actor orchestrator to review/assign focused harness adjustment; no auto merge.
