# SSR current state

Reconciled: 2026-11-15
Repo/ref: EnterTheNameHere/Super-Survivors / B42
Initial inspected tree: 857543978dbc2571a164666f1f6c864acb88b4da
Coordinator: ChatGPT design/orchestrator thread
Implementer: Local Codex; acknowledged 2026-11-15
Execution: SSR-TEST-01 native probe executed successfully in-game; full SSR persistence review/validation pending
Implementation base: 3a087ee8c4aceb151443848e19bbc3a999a129f5 (origin/B42)
Acknowledgment: mail/orchestrator/inbox/2026-11-15-persist-01-ack.md
Production implementation ref: codex/persistence-b42; exclusive existing checkout
Source commit: dc4dde25d612d33650c1ed5ef4ad0401c02394b5
Source parent: 792a129d6561d5e35fb8ace4c03eb4fd2558f8cd
Delivery: mail/orchestrator/inbox/2026-11-15-persist-01-delivery.md
Canonical coordination remains B42; implementation has NOT been merged into B42 or accepted.
Task: SSR-PERSIST-01 (assignments/persistence-b42.md)
Processed request: mail/implementer/archive/2026-11-15-persist-01.md

Delivery evidence:
- Installed 42.22.2 native APIs inspected read-only; no Java modification.
- World Global ModData schema + versioned native snapshots; dynamic stable registries and named areas.
- 161 automated tests pass, 109/109 runtime Lua syntax checks pass; no in-game results claimed.
- LuaLS completed with 88 legacy diagnostics, not a clean whole-project result.
- Snapshot generations are retained (disk growth); no cross-file atomicity/crash-proof guarantee.
- Source details, limits and manual checks: docs/PERSISTENCE_B42.md on implementation ref.

Legacy B42 static findings:
- Six groups are instantiated in group manager by default. No hard-coded max of twelve groups; twelve fixed area types in group model.
- Group state writes four files/group through mod-dir writer; group loader assumes contiguous IDs and interacts with predefined groups.
- Survivor count and X/Y/Z index use mod-dir files, while individual NPC IsoPlayer:save appears directed at actual world directory.
- Location map concatenates coordinates without separators; a table.remove call treats survivor ID as array position.
- Parts of persistence run from render-tick counters and Escape.
- Installed B42 behavior still requires actual code/API verification and real in-game validation.

Current objective: new-world native B42 persistence; dynamic stable survivor/group registry; no legacy loaders or compatibility; world-owned state; loaded/unloaded/dead handling; report engine-backed verification.

Review clarification (authoritative): ai-workflow/mail/implementer/archive/2026-11-15-persist-01-r1-clarification.md (B42), supersedes older mandatory-optimization mail. Study installed B42 IsoPlayer save/load position and world registration; prepare SAFE opt-in diagnostic for user in fresh world; inspect streaming/add/remove and per-tick scan necessity. No automatic persistence rewrite. Report findings first. B42 coordination and codex source branches diverged; do not force-update.

Next actor: orchestrator reviews delivered source/findings, user runs the disposable-world probe. Persistence fixes/acceptance require review of observed results.

Not assigned: debug hub / individual inspector; future AI manager; in-game scenario runner.


## SSR-TEST-01 (delivered for review)
User on 2026-11-15 approved adding a minimal, independently reusable Tests UI now.
Entry: dev/testing-gated right-click menu (without -debug); UI shows destructive-world warning, explicit consent, registered tests, outcomes and observed values. First test = native IsoPlayer position save/load diagnostic tied to existing SSR-PERSIST-01 engine investigation. No full SS Debug hub, broad runner, AI or speculative persistence rewrite.
Assignment: ai-workflow/assignments/tests-ui-01.md
Processed request: ai-workflow/mail/implementer/archive/2026-11-15-test-01.md
Owner: existing local Codex implementer once acknowledged; no parallel worktree ownership.
State: DELIVERED FOR REVIEW by existing local Codex; no in-game results.
Acknowledgment: mail/orchestrator/inbox/2026-11-15-test-01-r1-ack.md
Source: 594e65bc6af92927d8ec2c4b20c5c36806bf31a3; parent: c1dea17a8f052a8e861635a86eec1619e791035e.
Delivery: mail/orchestrator/inbox/2026-11-15-test-01-r1-delivery.md
Evidence: 174 tests, 112 Lua syntax checks; LuaLS 88 legacy diagnostics, none in new modules.
Findings: native XYZ restoration differs from square registration; scan/unload/loader unchanged for R1.
Instructions/findings: docs/TESTS_UI.md and docs/NATIVE_POSITION_R1.md on implementation ref.
Next: review source and user-run same-session plus explicit restart probe. No automatic implementation merge.


Runtime follow-up: user opened Tests UI; version gate prevented running.
Fix delivered at 4164ad7bead8d6dd2d7db3c6e514e7c9acb52a42 (parent
5f215b056cf00908a6c84a95dfa4dde89348fef2): compare full build API; preserve
checkbox on selection at user request; show disabled-run reason. 177 tests and
112 syntax checks pass. Actual native roundtrip still NOT RUN. Report: mail/orchestrator/inbox/2026-11-15-test-01-runtime-fix.md.


Offset gate follow-up: a7222ebbf247313ea1738e008b2cec4e0d46184b normalizes
boxed Java static save offsets (user reported rejection of 0/0). 178 tests and
112 syntax checks pass; native roundtrip still pending. Report:
mail/orchestrator/inbox/2026-11-15-test-01-offset-fix.md.


Latest runtime evidence (15 November 2026): user completed all three probe
phases with game restart; logs confirm two same-session passes and resumed
pass. Native X/Y/marker restored; currentSquare remains constructor square.
Human guards and isolated cleanup passed. Z not independently differentiated.
Full SSR persistence lifecycle/acceptance still pending orchestrator review.
Report: mail/orchestrator/inbox/2026-11-15-test-01-runtime-results.md.
Next actor: orchestrator reviews concrete engine results and loader placement
implications; no automatic source merge or speculative rewrite.


Direct user-requested startup fixes delivered at 29bebd0 (percent descriptions,
B42 grave craft recipes), 178 tests/112 Lua syntax; restart/load validation
pending. Report: mail/orchestrator/inbox/2026-11-15-startup-error-fixes.md. No persistence acceptance or production merge.


User returned control to orchestration after runtime checks. Latest restart log
(15 November 14:31:11) contains no prior mod recipe-property or option-format
errors; crafting itself untested. Native probe passed, full SSR persistence
review/lifecycle acceptance pending. Next actor: orchestrator; implementer awaits
next bounded assignment. See mail/orchestrator/inbox/2026-11-15-return-to-orchestration.md.
