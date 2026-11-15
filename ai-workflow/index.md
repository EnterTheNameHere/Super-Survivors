# Super Survivors Reloaded — coordination index

Repository: `EnterTheNameHere/Super-Survivors`  
Canonical coordination branch: `B42`  
Source tree inspected at setup: `857543978dbc2571a164666f1f6c864acb88b4da`  
Date: 2026-11-15

**Read in order:** `README.md`, `coordination-protocol.md`, `state.md`, `handoff/orchestrator-thread.md`, your role's inbox, and any referenced assignment. Then verify actual Git head/ownership.

**Roles:** orchestrator = ChatGPT design thread; implementer = local Codex after explicit startup; user = design authority and in-game tester.

**Active request:** SSR-PERSIST-01 — B42 native world-save persistence and stable survivor/group registry.
- Task: `assignments/persistence-b42.md`
- Processed mail: `mail/implementer/archive/2026-11-15-persist-01.md`
- Current status: REVIEW IN PROGRESS / R1 ENGINE INVESTIGATION + OPT-IN RUNTIME PROBE ASSIGNED; no gameplay validation.
- Implementation ref: `codex/persistence-b42`, base `3a087ee8c4aceb151443848e19bbc3a999a129f5`.
- Acknowledgment: `mail/orchestrator/inbox/2026-11-15-persist-01-ack.md`.
- Delivery: `mail/orchestrator/inbox/2026-11-15-persist-01-delivery.md`.
- Source commit: `dc4dde25d612d33650c1ed5ef4ad0401c02394b5`; parent `792a129d6561d5e35fb8ace4c03eb4fd2558f8cd`.
- Canonical B42 carries coordination only; production implementation remains on its review branch. No acceptance or implementation merge is implied.
- Authoritative R1 clarification: `mail/implementer/inbox/2026-11-15-persist-01-r1-clarification.md` on B42. It supersedes the earlier mandatory-optimization request.\n- Next actor: local Codex investigates installed engine, produces safe opt-in runtime probe and reports findings; user executes probe in fresh disposable world. No code rewrite required before evidence.

**Next (not yet assigned):** SS Debug hub and inspector, then new survivor AI Manager and scenarios.

Do not work on `master` or merge/publish without review and authorization.


## Newly assigned: SSR-TEST-01 (2026-11-15)
- User approved a reusable minimal in-game Tests UI via context menu, destructive-world warning with affirmative acknowledgment, independent Lua registry, and IsoPlayer native save/load position probe as first test.
- Task: `assignments/tests-ui-01.md`
- Outstanding inbox: `mail/implementer/inbox/2026-11-15-test-01.md`
- Status: REQUESTED, NOT YET ACKNOWLEDGED. No Codex execution claimed.
- Related: SSR-PERSIST-01 R1 engine investigation; no mandatory OnTick rewrite.
- Next: same local Codex implementer claims/acknowledges within existing exclusive branch/worktree; report exact evidence. Do not merge automatically.
