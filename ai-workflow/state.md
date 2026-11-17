# SSR current state

Reconciled: 2026-11-15
Repo/ref: EnterTheNameHere/Super-Survivors / B42
Initial inspected tree: 857543978dbc2571a164666f1f6c864acb88b4da
Coordinator: ChatGPT design/orchestrator thread
Implementer: Local Codex; acknowledged 2026-11-15
Execution: SSR-TEST-03 delivered for user stage/save/restart/resume; full SSR persistence acceptance pending
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


## Orchestrator scoped review, 2026-11-15
SSR-TEST-01 Tests UI and native position probe were exercised in real B42.22.2,
including two same-session runs and a user-confirmed full restart/resume.
Evidence: docs/evidence/NATIVE_POSITION_2026-11-15.log and
docs/NATIVE_POSITION_R1.md on codex/persistence-b42. Native load restored
X/Y without manual setters, but currentSquare stayed associated with
constructor tile; Z was not independently varied. Human state guards and
owned-actor cleanup passed. These observations do not show a defect in the
normal SSR loader, which constructs at saved location. Scoped test objective
met; full SSR-PERSIST-01 acceptance remains pending live survivor/group
save/reload/streaming/death checks. Review to implementer inbox:
ai-workflow/mail/implementer/archive/2026-11-15-test-01-orchestrator-review.md.
No source merge. Latest observed implementation branch head 090f424.
Codex reports 178 automated tests/112 Lua syntax checks; orchestrator has
not independently rerun those checks.

## SSR-TEST-02 new request (2026-11-15)
User explicitly chose to test possible IsoPlayer.new(cell) / native load construction before broader SSR lifecycle. Assignment on B42: ai-workflow/assignments/test-cell-only-isoplayer-02.md; Codex inbox: ai-workflow/mail/implementer/archive/2026-11-15-test-02-cell-only.md. First verify installed B42 constructor overload and safe registration/cleanup, then (if safe) implement a user-run Tests UI probe, observing position/currentSquare/moving-square/world lists before load, after load and after explicit placement. The alternative constructor is an UNVERIFIED hypothesis; not a design decision. Status: REQUESTED, NOT ACKNOWLEDGED. No production persistence rewrite or acceptance. Existing exclusive codex/persistence-b42 worktree owner only.


## SSR-ANALYSIS-01 source-only investigation requested (2026-11-15)
User explicitly narrowed IsoSurvivor vs IsoPlayer comparison to installed B42 Java/Lua FIRST, before in-game testing. Compare inheritance/constructors/factories, real engine use, native persistence, world lifecycle and gameplay APIs, plus potential SSR migration implications; report actual evidence and remaining uncertainties. Do not implement code, tests, or class migration. Assignment: ai-workflow/assignments/isosurvivor-vs-isoplayer-analysis.md; inbox: ai-workflow/mail/implementer/archive/2026-11-15-isosurvivor-analysis.md. REQUESTED, NOT ACKNOWLEDGED; existing Codex worktree only, coordinate with SSR-TEST-02.


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


## SSR-TEST-02 actual result (17 November 2026)
Cell-only/native-load/explicit-registration probe PASSED in actual B42.22.2.
Constructor unplaced at 0.5/0.5/0; raw load restores saved X/Y/marker but remains
unregistered; explicit current/moving-square/cell sequence establishes membership.
Human and all four local slots unchanged; both actors cleaned up in same frame.
No normal AI/update or full lifecycle validation. No production adoption/merge.
Next actor: orchestrator reviews results; no implementation continues automatically.
Report: mail/orchestrator/inbox/2026-11-17-test-02-runtime-results.md.

## SSR-TEST-02 in-game review (2026-11-17)
User completed the focused B42.22.2 cell-only IsoPlayer probe. Runtime log on codex/persistence-b42: `docs/evidence/CELL_ONLY_ISOPLAYER_2026-11-17.log`; implementer report: `ai-workflow/mail/orchestrator/inbox/2026-11-17-test-02-runtime-results.md`. Cell-only constructor yielded (0.5,0.5,0), no square/cell membership; native load restored saved XYZ (9884.5,12827.5,0) and marker, still unregistered; explicit setCurrentSquare(saved tile), setMovingSquareNow(), addMovingObject() established correct square and objectList. Human slots/singleton/position and cleanup checks passed. **Scoped diagnostic accepted** by orchestrator; review mail: `ai-workflow/mail/implementer/archive/2026-11-17-test-02-orchestrator-review.md`. No differential Z, restart or prolonged active NPC test for Test 2. No evidence that existing saved-position constructor SSR loader is faulty or that cell-only route is superior. Production SSR-PERSIST-01 remains under review, awaiting live end-to-end SSR survivor/group persistence/streaming/death checks. No code merge/adoption authorized.

## SSR-TEST-03 — real SSR persistence lifecycle tests (2026-11-17)
User authorized repurposing/rewriting existing native diagnostic tests in the development-gated SS Tests UI; their historical findings/logs remain retained. New Codex assignment: `ai-workflow/assignments/persistence-live-tests-03.md`, request `ai-workflow/mail/implementer/archive/2026-11-17-persistence-live-tests-03.md`. First goal: one real SSR-managed survivor/group, baseline captured at actual game OnSave, normal save/exit and user-confirmed restart, explicit consent to resume, compare saved native state, SSR registry and reconstructed actor, including square/list membership. Gradually extend/manual-check multiple survivors/groups, unload/return, death, repeated snapshots; do not overbuild framework. No auto execution, no production persistence rewrite, no source merge. Status REQUESTED/NOT ACKNOWLEDGED.


SSR-TEST-03 ACKNOWLEDGED by existing exclusive local Codex; implementing minimal
real SSR restart test, preserving production persistence and historical probes.
Ack: mail/orchestrator/inbox/2026-11-17-test-03-ack.md. No engine result yet.


## SSR-TEST-03 implementation delivered (17 November 2026)
Source e6f08e05b3ec3805a1c8394d8de2f7dab8e261d9 (parent ACK
4d5002e816e7a5cc3aca9a5d1a708913299153ec), codex/persistence-b42.
Two visible choices: real survivor/group stage and explicit full-restart resume.
OnSave observer samples after production snapshot publication, not stage click;
no production save/load call or callback reordering. Independent native reader,
registry/group/live actor/property/count comparisons. Old diagnostics archived,
evidence unchanged. Persistent fixtures remain; no deletion of other actors.
199 tests/112 syntax pass in isolated intended tree; LuaLS 88 legacy diagnostics,
none new modules. USER IN-GAME NOT RUN. No production persistence rewrite/merge.
Instructions: docs/TESTS_UI.md; manual broader checks: docs/PERSISTENCE_LIVE_TESTS.md.
Next actor: user stage/save/exit/full restart/resume, orchestrator reviews evidence.
Delivery: mail/orchestrator/inbox/2026-11-17-test-03-delivery.md.
