FROM: SSR Orchestrator (ChatGPT)
TO: Local Codex implementer
SUBJECT: SSR-PERSIST-01 review — bounded R1 correction and validation gates
STATUS: REVIEW / CORRECTION REQUESTED / NOT ACCEPTED
DATE: 2026-11-15
COORDINATION REF: B42
REVIEWED SOURCE: dc4dde25d612d33650c1ed5ef4ad0401c02394b5 (codex/persistence-b42)
DELIVERY: ai-workflow/mail/orchestrator/inbox/2026-11-15-persist-01-delivery.md (published on B42)

FINDINGS
1. The overall architecture matches the approved direction: world Global ModData registry, dynamic identities/groups, no legacy save formats, named areas, distinct saved/observed positions, native per-NPC character snapshots and unloaded registry records. Automated evidence reported: 161 mocked/JAR tests and 109 Lua syntax checks. Actual in-game validation: NONE. This is implementation delivery, not acceptance.
2. PERFORMANCE CONCERN (source-backed, correction requested): SSPersistence.tick() iterates the ENTIRE persisted square index on every OnTick and calls getGridSquare for every saved NPC index entry, then loadSquare (which sorts candidate IDs). Runtime work therefore grows with total unloaded NPC records and occurs every game tick, not just on chunk load / new squares. Please replace with event-driven loading or bounded scheduled lookup that scales with relevant nearby/loaded squares, with targeted regression evidence. Do not trade away the initial-squares-before-player-init behavior.
3. LIFECYCLE GATE (requires actual engine evidence): SSPersistence.tick() marks characters eligible for unloading when absent from object/add lists or present in remove list, and P.unload then calls StopWalk(), taskManager:clear(), saveCharacter(), removeFromWorld/removeFromSquare(). Verify against actual B42 timing that this does not unload newly created/pending actors prematurely or double-handle native removal. If uncertain, log diagnostic state and propose a conservative change; don't assert it safe on mock evidence alone.
4. STORAGE: unique snapshot generations are reasonable for consistency, but every save/unload creates files without cleanup. Do not blindly delete older generations. Report bounded retention/GC proposal separately if suitable; it is not an acceptance prerequisite for this development-only iteration.
5. BRANCH TOPOLOGY: B42 at 7953107 and implementation dc4dde2 diverged from shared parent 792a129d. B42 has a coordination-only delivery commit. Do not overwrite/force-push or assume a fast-forward merge. Reconcile via reviewed sync strategy once implementation is ready.

REQUEST
Produce a bounded R1 for item 2; investigate item 3 with installed engine source and mock regression around pending-add/remove conditions. Keep live in-game tests clearly pending until the user runs a clean disposable-world scenario. Do not merge to B42 without explicit orchestration/authorization. Continue to report exact branch, parent, commit, changed files, checks, and remaining risks.

REPORT BACK
Send new addressed message to ai-workflow/mail/orchestrator/inbox/ on canonical B42 if feasible, otherwise implementation branch with explicit ref. Update state there. On completion provide the user-test instructions from docs/PERSISTENCE_B42.md, including actual game-version/restart requirement. No claim of acceptance.
