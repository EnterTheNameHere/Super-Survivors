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
- Current status: REVIEW IN PROGRESS / R1 PROBE PASSED IN-GAME; full SSR lifecycle review/validation pending.
- Implementation ref: `codex/persistence-b42`, base `3a087ee8c4aceb151443848e19bbc3a999a129f5`.
- Acknowledgment: `mail/orchestrator/inbox/2026-11-15-persist-01-ack.md`.
- Delivery: `mail/orchestrator/inbox/2026-11-15-persist-01-delivery.md`.
- Source commit: `dc4dde25d612d33650c1ed5ef4ad0401c02394b5`; parent `792a129d6561d5e35fb8ace4c03eb4fd2558f8cd`.
- Canonical B42 carries coordination only; production implementation remains on its review branch. No acceptance or implementation merge is implied.
- Authoritative R1 clarification: `mail/implementer/archive/2026-11-15-persist-01-r1-clarification.md` on B42. It supersedes the earlier mandatory-optimization request.
- Next actor: orchestrator reviews the delivery; user executes the opt-in probe in a fresh disposable world. No speculative persistence rewrite.

**Next (not yet assigned):** SS Debug hub and inspector, then new survivor AI Manager and scenarios.

Do not work on `master` or merge/publish without review and authorization.


## Delivered for review: SSR-TEST-01 (2026-11-15)
- User approved a reusable minimal in-game Tests UI via context menu, destructive-world warning with affirmative acknowledgment, independent Lua registry, and IsoPlayer native save/load position probe as first test.
- Task: `assignments/tests-ui-01.md`
- Processed request: `mail/implementer/archive/2026-11-15-test-01.md`
- Status: DELIVERED FOR REVIEW; native roundtrip passed in-game, full SSR lifecycle unvalidated.
- Acknowledgment: `mail/orchestrator/inbox/2026-11-15-test-01-r1-ack.md`.
- Related: SSR-PERSIST-01 R1 engine investigation; no mandatory OnTick rewrite.
- Delivery: `mail/orchestrator/inbox/2026-11-15-test-01-r1-delivery.md`.
- Source: `594e65bc6af92927d8ec2c4b20c5c36806bf31a3`, parent `c1dea17a8f052a8e861635a86eec1619e791035e` on `codex/persistence-b42`.
- Next: orchestrator review and user-led in-game checks; no automatic merge.


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
