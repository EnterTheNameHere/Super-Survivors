# SSR current state

Reconciled: 2026-11-15
Repo/ref: EnterTheNameHere/Super-Survivors / B42
Initial inspected tree: 857543978dbc2571a164666f1f6c864acb88b4da
Coordinator: ChatGPT design/orchestrator thread
Implementer: Local Codex; acknowledged 2026-11-15
Execution: IMPLEMENTATION REVIEWED — bounded R1 CORRECTION REQUESTED; automated checks passed at dc4dde2; in-game validation pending
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

Review: ai-workflow/mail/implementer/inbox/2026-11-15-persist-01-r1-review.md (B42). R1 needed: avoid scanning every saved survivor square on every OnTick; validate unload/pending add/remove lifecycle against installed B42. Branches diverged at 792a129d: B42 coordination commit and Codex source branch; reconcile without force updates.\n\nNext actor: local Codex implements bounded R1, reports ref + evidence. Then orchestrator review and user-led clean disposable-world engine tests. No acceptance or next assignment inferred.

Not assigned: debug hub / individual inspector; future AI manager; in-game scenario runner.
