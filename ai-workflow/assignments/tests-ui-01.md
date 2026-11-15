# SSR-TEST-01 — minimal in-game Tests UI and test registry

Date: 2026-11-15
Owner: Local Codex implementer after acknowledgment
Coordinator: SSR ChatGPT orchestrator
Canonical coordination: B42
Implementation starting point: current codex/persistence-b42 (dc4dde2 at assignment creation); check actual branch heads and prior ownership before edits.

## Approved direction
Introduce a reusable but intentionally minimal real B42 in-game testing surface now. The first test is the native IsoPlayer save/load investigation from SSR-PERSIST-01 R1. Tests are disposable definitions: add, modify, disable or remove them over time. UI discovery/execution is separate from test logic. This is NOT the full SS Debug hub, and is NOT a general testing DSL, script platform or AI manager.

## Required experience
- A discreet right-click context-menu item opens a modest Super Survivors Tests window in-game, without requiring the game's -debug mode. Gate the entry by a mod-owned development/testing option if feasible using existing settings; do not make ordinary players accidentally run destructive tests. Document the exact visibility condition; avoid broad options-system refactoring.
- Show a prominently readable warning BEFORE any world-modifying execution. Approved warning text:
  **Warning — World Modifications**
  Tests may irreversibly alter this game world, including characters, items, objects and zombies. Use a disposable world. Restoration is not guaranteed.
- Require affirmative, deliberate acknowledgment prior to running a test. Reopening the UI, switching tests or launching a new destructive run should not silently inherit consent. The UI should clearly state what the selected test does and what may be modified.
- Show registered tests with name/description, requirements and availability. Initially include the IsoPlayer native save/load diagnostic as the first test; more tests may come and go.
- Have a small independent Lua registry of test definitions (stable ID, title, description/risk, optional prerequisites, execution function / step or callbacks), not hard-coded button logic for each test.
- Report actual observed values, meaningful success/failure/inconclusive/setup-error status, and exceptions, ideally to in-game UI and console. Do not manufacture PASS merely because test invocation returned.
- Only one world-mutating test runs at once initially. Prevent duplicate clicks/runs; permit tests that take multiple ticks, and preserve enough explicitly designed evidence to inspect/restart if a test requires it. Do not invent a universal persistent scheduler or require every test to support restarts.
- Cleanup, where safe, is best effort, not a promise that a test leaves the world unchanged.

## First diagnostic: native IsoPlayer save/load
Follow the engine-first investigation requirement in ai-workflow/mail/implementer/inbox/2026-11-15-persist-01-r1-clarification.md and orchestrator handoff. Confirm installed B42.22.2 engine requirements independently; old mod code is not API authority.
- Use an isolated test NPC and unique test snapshot/name inside a disposable world; do NOT overwrite or modify the user's human player or their native save.
- Log original actor X/Y/Z and currentSquare; construct a distinct safe actor at intentionally different coordinates and load the snapshot without manual setX/setY/setZ after load. Record post-load X/Y/Z, currentSquare and relevant world membership/lifecycle markers.
- Distinguish in-session diagnostic evidence from an actual restart persistence roundtrip. If a restart-phase probe is warranted, stage and resume explicitly, show instructions and observed data, and do not automatically reset/alter the world.
- If raw construction/snapshotting cannot be established safe in installed B42, do not pretend to perform the experiment: show INCONCLUSIVE or SETUP ERROR with specific reason and offer a safer read-only observation/proposal.
- The diagnostic is an investigation of B42 engine behavior, NOT proof that our SSR persistence implementation works end-to-end.

## Source/compatibility boundaries
- Keep SSR-PERSIST-01 implementation on its review branch; no automatic merge to B42. Coordinate potentially overlapping edits: one implementer/working tree only; no second concurrent ownership.
- No generalized SS Debug hub, inspector, trade UI, new AI manager, gameplay automation, or Workshop publishing in this task.
- Do not rewrite native persistence or its OnTick scan as a precondition of implementing the test UI; report evidence and propose changes separately.
- Inspect B42 actual UI/Events/context-menu conventions, not copied B40/B41 code, and verify whether intended hooks are available in the installed version.

## Deliverable / acceptance
Codex reports exact branch, parent and commit, changed paths, the UI entry condition and how to turn it on, warning/acknowledgment behavior, test registry shape, first diagnostic safety measures, actual test output expected, and results of runnable automated checks. Include step-by-step user instructions for starting a NEW disposable world, creating the character, entering gameplay, enabling the Tests entry, launching test, and sharing console/log evidence. Mark actual engine gameplay validation NOT RUN unless the user actually ran it.
Submit delivery and blockers to ai-workflow/mail/orchestrator/inbox/ on canonical B42 if possible, otherwise report precise ref; update current state. Orchestrator reviews source; user validates actual in-game functionality. Do not merge without explicit review/authorization.
