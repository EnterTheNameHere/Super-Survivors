# SSR current state

Reconciled: 2026-11-15
Repo/ref: EnterTheNameHere/Super-Survivors / B42
Initial inspected tree: 857543978dbc2571a164666f1f6c864acb88b4da
Coordinator: ChatGPT design/orchestrator thread
Implementer: NONE ACKNOWLEDGED
Execution: REQUESTED, NOT CONFIRMED RUNNING
Task: SSR-PERSIST-01 (assignments/persistence-b42.md)
Outgoing mail: mail/implementer/inbox/2026-11-15-persist-01.md

Legacy B42 static findings:
- Six groups are instantiated in group manager by default. No hard-coded max of twelve groups; twelve fixed area types in group model.
- Group state writes four files/group through mod-dir writer; group loader assumes contiguous IDs and interacts with predefined groups.
- Survivor count and X/Y/Z index use mod-dir files, while individual NPC IsoPlayer:save appears directed at actual world directory.
- Location map concatenates coordinates without separators; a table.remove call treats survivor ID as array position.
- Parts of persistence run from render-tick counters and Escape.
- Installed B42 behavior still requires actual code/API verification and real in-game validation.

Current objective: new-world native B42 persistence; dynamic stable survivor/group registry; no legacy loaders or compatibility; world-owned state; loaded/unloaded/dead handling; report engine-backed verification.

Next actor: local Codex starts explicitly, confirms branch ownership, acknowledges task via orchestrator inbox, then implements. Orchestrator reviews exact delivery. User validates using disposable PZ world.

Not assigned: debug hub / individual inspector; future AI manager; in-game scenario runner.
