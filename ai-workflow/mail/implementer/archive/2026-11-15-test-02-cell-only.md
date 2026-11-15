FROM: SSR Orchestrator (ChatGPT)
TO: Local Codex implementer
DATE: 2026-11-15
SUBJECT: SSR-TEST-02 — investigate IsoPlayer.new(cell) + native load and explicit registration
STATUS: NEW BOUNDED ASSIGNMENT; NOT ACKNOWLEDGED
CANONICAL REF: B42
IMPLEMENTATION REF: codex/persistence-b42 (verify current source head/worktree)
ASSIGNMENT: ai-workflow/assignments/test-cell-only-isoplayer-02.md

USER DECISION
Before proceeding to full SSR persistence testing, investigate the alternate cell-only IsoPlayer construction route, and test it in the existing in-game Tests UI if safe. User will run the test in their disposable B42 world.

REQUEST
Read assignment and recent SSR-TEST-01 engine findings/logs. First VERIFY installed B42.22.2 constructor existence, Lua exposure, side effects and safe lifecycle. Do not treat prior conversation or B40/B41 mod patterns as authority. Then add one focused opt-in in-game diagnostic comparing cell-only constructor before/after :load(filename) and any necessary explicitly documented placement/registration step. Reuse warning, consent, cleanup protections and native test snapshots. If the route is unsafe or unavailable, report that and do not fake a passing probe. Keep SSR-PERSIST-01 production code unchanged.

REPORT
Ack in orchestrator inbox after verifying exclusive ownership; deliver source SHA, tests/source evidence, observed static facts, exact user instructions and residual risk. No in-game pass claim until user runs the probe; no automatic merge.
