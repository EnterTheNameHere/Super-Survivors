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


User returned control to orchestration after runtime checks. Latest restart log
(15 November 14:31:11) contains no prior mod recipe-property or option-format
errors; crafting itself untested. Native probe passed, full SSR persistence
review/lifecycle acceptance pending. Next actor: orchestrator; implementer awaits
next bounded assignment. See mail/orchestrator/inbox/2026-11-15-return-to-orchestration.md.


## SSR-TEST-01 in-game outcome (2026-11-15)
- Tests UI usable; native position probe exercised twice in-session and once
  after actual restart, with captured logs.
- Native load restores X/Y and identity, not square registration after a
  deliberately different constructor position. Z not independently varied.
- Review: `mail/implementer/archive/2026-11-15-test-01-orchestrator-review.md`.
- Status: scoped diagnostic delivered and validated in-game; full SSR-PERSIST-01
  remains under review, next gate real SSR survivor/group lifecycle.
- Source: `codex/persistence-b42`, observed head `090f424`. No production merge.

## Delivered for review: SSR-TEST-02 — cell-only IsoPlayer construction (2026-11-15)
User requested experiment before more persistence work. Verify installed B42.22.2 IsoPlayer.new(cell) availability/side effects and, only if safe, add opt-in Tests UI experiment for raw :load() and explicit world registration. Assignment: `assignments/test-cell-only-isoplayer-02.md`; inbox: `mail/implementer/archive/2026-11-15-test-02-cell-only.md`. DELIVERED FOR REVIEW; focused probe implemented, user live test pending. SSR-PERSIST-01 code preserved; no automatic merge.


## Completed source analysis: SSR-ANALYSIS-01
- Compare IsoSurvivor and IsoPlayer in installed B42 Java/Lua, source-only, before any in-game experiment. Assignment: `assignments/isosurvivor-vs-isoplayer-analysis.md`; inbox: `mail/implementer/archive/2026-11-15-isosurvivor-analysis.md`.
- Status: ANALYSIS COMPLETE; proposed IsoSurvivor migration REJECTED by user. No change to SSR actor implementation. SSR-TEST-02 remains pending separately.


SSR-ANALYSIS-01 acknowledged by existing exclusive local Codex, source-only
research. Latest user instruction restricts this turn to analysis; SSR-TEST-02
and supplement remain pending. Ack: mail/orchestrator/inbox/2026-11-15-analysis-01-ack.md.


## SSR-ANALYSIS-01 final disposition (15 November 2026)
Analysis complete; user requested the proposed IsoSurvivor migration be REJECTED.
Keep IsoPlayer. Installed-source blockers: inherited getVisual throws, primary
BodyDamage/Moodles/XP absent, shared attack state requires IsoPlayer, filename
save/control/update contracts differ. Documentation a4c523b35cc5e1cfac5958a75d41bd0548c3802a
(parent 6234ff63df16dcd67dbed56f7836aad4ab254420) on codex/persistence-b42;
report docs/ISOSURVIVOR_VS_ISOPLAYER_B42.md. No runtime code/test/experiment or
Java changes. SSR-TEST-02 and factory supplement remain pending, explicitly not
executed under user's analysis-only instruction. Next actor: orchestrator.
Delivery: mail/orchestrator/inbox/2026-11-15-analysis-01-delivery.md.


SSR-TEST-02 now ACKNOWLEDGED: user explicitly resumed Test 2 after analysis.
Existing exclusive local Codex checkout, constructor/factory research and focused
probe only. Prior analysis-only restriction no longer applies. Ack:
mail/orchestrator/inbox/2026-11-15-test-02-ack.md. Native test NOT RUN yet.


## SSR-TEST-02 delivered (15 November 2026)
Focused cell-only/native-load/explicit-registration probe at source
85be6306a77bc32af6fd6586bfdd5dc5f4a875c8 (parent ACK
8e50dbf95a59d64864353d8795c89d87e937fa6d), codex/persistence-b42.
Factory supplement answered; no arbitrary-NPC-returning managed factory found
in inspected scope. No human loading/control helper used. New fourth selector:
Native IsoPlayer - cell-only construction and placement. 185 tests, 112 syntax;
LuaLS 88 legacy diagnostics, none test modules. USER IN-GAME NOT RUN.
No production loader/scan/unload/group rewrite, Java change or automatic merge.
Next actor: user runs the new entry after restart; orchestrator reviews observations.
Delivery: mail/orchestrator/inbox/2026-11-15-test-02-delivery.md.

## Saved future design direction (2026-11-16)
- `docs/SURVIVOR_WORLD_KNOWLEDGE_DIRECTION.md` — B42 building/floor/Z correctness, unified observation, individually acquired survivor knowledge, stale resource memory, communication, possible offscreen simulation and multiplayer considerations. Direction only; no implementation assignment. Independent SSR document.


## SSR-TEST-02 actual result (17 November 2026)
Cell-only/native-load/explicit-registration probe PASSED in actual B42.22.2.
Constructor unplaced at 0.5/0.5/0; raw load restores saved X/Y/marker but remains
unregistered; explicit current/moving-square/cell sequence establishes membership.
Human and all four local slots unchanged; both actors cleaned up in same frame.
No normal AI/update or full lifecycle validation. No production adoption/merge.
Next actor: orchestrator reviews results; no implementation continues automatically.
Report: mail/orchestrator/inbox/2026-11-17-test-02-runtime-results.md.

## SSR-TEST-02 in-game review (2026-11-17)
User completed the focused B42.22.2 cell-only IsoPlayer probe. Runtime log on codex/persistence-b42: `docs/evidence/CELL_ONLY_ISOPLAYER_2026-11-17.log`; implementer report: `ai-workflow/mail/orchestrator/inbox/2026-11-17-test-02-runtime-results.md`. Cell-only constructor yielded (0.5,0.5,0), no square/cell membership; native load restored saved XYZ (9884.5,12827.5,0) and marker, still unregistered; explicit setCurrentSquare(saved tile), setMovingSquareNow(), addMovingObject() established correct square and objectList. Human slots/singleton/position and cleanup checks passed. **Scoped diagnostic accepted** by orchestrator; review mail: `ai-workflow/mail/implementer/inbox/2026-11-17-test-02-orchestrator-review.md`. No differential Z, restart or prolonged active NPC test for Test 2. No evidence that existing saved-position constructor SSR loader is faulty or that cell-only route is superior. Production SSR-PERSIST-01 remains under review, awaiting live end-to-end SSR survivor/group persistence/streaming/death checks. No code merge/adoption authorized.

## SSR-TEST-03 — real SSR persistence lifecycle tests (2026-11-17)
User authorized repurposing/rewriting existing native diagnostic tests in the development-gated SS Tests UI; their historical findings/logs remain retained. New Codex assignment: `ai-workflow/assignments/persistence-live-tests-03.md`, request `ai-workflow/mail/implementer/inbox/2026-11-17-persistence-live-tests-03.md`. First goal: one real SSR-managed survivor/group, baseline captured at actual game OnSave, normal save/exit and user-confirmed restart, explicit consent to resume, compare saved native state, SSR registry and reconstructed actor, including square/list membership. Gradually extend/manual-check multiple survivors/groups, unload/return, death, repeated snapshots; do not overbuild framework. No auto execution, no production persistence rewrite, no source merge. Status REQUESTED/NOT ACKNOWLEDGED.


SSR-TEST-03 ACKNOWLEDGED by existing exclusive local Codex; implementing minimal
real SSR restart test, preserving production persistence and historical probes.
Ack: mail/orchestrator/inbox/2026-11-17-test-03-ack.md. No engine result yet.
