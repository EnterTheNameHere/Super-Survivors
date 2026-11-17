# Super Survivors Reloaded — orchestrator thread handoff

Updated: 2026-11-15
Repo: EnterTheNameHere/Super-Survivors
Canonical coordination/ref: B42
Role: ChatGPT orchestrator/design coordinator; local Codex implementer after explicit start; user design authority and game tester.

## Context and boundaries
Project ports original Super Survivors B40 / Superb Survivors B41 to Super Survivors Reloaded for B42.15+. Development B42 branch is incomplete/buggy, unreleased; no old save compatibility requirement. No Java engine modifications. Local Codex accesses installed game's Lua/Java and local runtime; ChatGPT reviews GitHub/coordinates.

Existing relevant source and docs: 42/media/lua/client/2_Group/SuperSurvivorGroup.lua and SuperSurvivorGroupManager.lua; 42/media/lua/client/3_Other/SuperSurvivorManager.lua, SuperSurvivor.lua and SuperSurvivorsMod.lua; 0_Utilities/SuperSurvivorTablesUtilities.lua; docs/B42_PORT.md, LOCAL_HANDOFF.md, BEHAVIOUR_DESIGN.md, DEVELOPMENT_SCENARIOS.md, CODEBASE_PORT_REVIEW_2026-11-10.md, CORE_BEHAVIOUR_REVIEW_2026-11-12.md, SAVE_IO_ERROR_2026-11-10.md.

## Accepted AI design direction (NOT implemented)
AI Manager = registry/coordinator of participants (vision, hearing, hunger, state, injury, memory, equipment, group). Participants report observations, motivations, constraints and proposals, potentially receiving allocated LIMITED ATTENTION. More attention can improve report detail, specificity, uncertainty and planning; panic narrows/redistributes attention, causing possible poor recognition, not automatically lower danger. Multiple competing long- and short-term goals; active goals gain commitment; alerts suspend and later reconsider; plans organize reusable behaviors with sequences, branches, loops and actions. Decision reasons should be actual captured metadata, not invented retrospectively.
Phase 01 survivor should autonomously survive: seek weapon, food, water, handle threats/injuries, within same vanilla Sandbox world rules as human. No guaranteed survival, complex settlement jobs later.

## Accepted debug UI direction (not current task)
SS Debug optional setting without game's -debug, quiet main hub lists all known loaded/unloaded survivors, groups placeholder, system diagnostics, subtle Tests entry. Independent per-survivor inspector windows (no arbitrary maximum; expected 1-2), showing stable identity/name/group/role, health and needs, skills/levels/progress XP to next, inventory/equipment/health interfaces, goals/current plan/behavior/task/decision reasons, attention/perception/memory and history. Mark unloaded records as last-known. Later consider general actor-to-actor trade, player UI when participating, silent AI trades, and instant privileged debug transfers/equip bypassing gameplay time but preserving engine integrity. Current legacy debug/tests use -debug and are not release-packaged. Existing SurvivorInfoWindow/Inventory/DDebugUI provide precedent.

Scenario Runner future: destructive tests in disposable world, user may knowingly run in persistent world. No restoration guarantee. Warning text in coordination-protocol.md. Tests set world fixtures but must exercise real AI; outcomes Passed / Failed under valid conditions / Inconclusive environmental interruption / Setup error. Example search for weapon hidden in nearby house. Game-engine results authoritative.

## Current task: SSR-PERSIST-01
Static review found six unconditional groups, twelve area types, four per-group mod-dir files, group loader contiguous ID assumption, location-index map errors, character IsoPlayer:save in actual world path, periodic render-tick and Escape saving. User expressly chose clean B42 fresh-world baseline: no migration of B40/B41 or experimental B42 files, no legacy fallback, dynamic group/survivor registries, native per-world data and correct lifecycle. Candidate: Global ModData (ModData.getOrCreate, OnInitGlobalModData, OnSave), but Codex must verify installed engine and NPC character serialization/reload before choosing exact mechanics. Single-player first, no new AI Manager/UI in this task.

## Coordination
Local Codex acknowledged SSR-PERSIST-01 in commit 792a129d6561d5e35fb8ace4c03eb4fd2558f8cd,
published on B42, then implemented on codex/persistence-b42 in the existing local
checkout. Source delivery is dc4dde25d612d33650c1ed5ef4ad0401c02394b5, parent
792a129d6561d5e35fb8ace4c03eb4fd2558f8cd. Read addressed delivery mail
mail/orchestrator/inbox/2026-11-15-persist-01-delivery.md and docs/PERSISTENCE_B42.md
on the implementation ref. Request mail has been processed and archived.

161 automated tests and 109 runtime Lua syntax checks pass. Native 42.22.2 JAR
API/order evidence is separate from mocked Lua tests. NO in-game validation was
performed. LuaLS still reports 88 legacy diagnostics. Key tradeoff: unique native
snapshot generations retain older checkpoints and accumulate files; no atomic
transaction across native characters and world Global ModData is claimed.

Canonical B42 contains coordination updates, not an accepted implementation merge.
Writing delivery mail does not automatically notify/launch another live session.
Read current index/protocol/state and exact refs before further work.

## Next
Orchestrator reviews the exact source diff and delivery, then coordinates real
disposable-world save/reload/unload/death/copy checks with the user. Request any
corrections as new addressed mail. Acceptance/merge remain explicit decisions.
SS Debug hub/inspector and AI work remain unassigned; do not start them merely
because a persistence delivery exists.


## Engine-first investigation and runtime-test option (user decision, 2026-11-15)
The old Super Survivors B40/B41 code is approximately three years old. Its
save/load sequence must NOT be treated as evidence of what B42 requires.
Likewise, current port code shows what it attempts, not the engine contract.
Verify with the installed B42 Java/Lua implementation and, wherever practical,
with an actual runtime experiment. Separate established facts, concerns, design
preferences, and experimental hypotheses.

Open question: IsoPlayer has world X/Y/Z and save(String)/load(String).
Independently determine whether native save serializes world position; whether
native load assigns X/Y/Z; and whether character creation or world registration
requires additional placement even if X/Y/Z is restored. The current
SuperSurvivor:loadPlayer explicitly sets X/Y/Z after load, but that DOES NOT
establish the step is necessary. Registry location still may be useful for
deciding which unloaded survivor to instantiate and when.

User offered a live empirical route: they will create a NEW disposable B42
world, create a player character, and enter gameplay; then a focused runtime
test can be executed. Codex can inspect engine source AND/OR prepare a small
diagnostic test harness for the user to run in that world. Design the probe
before invoking unsafe engine operations: never overwrite the real player's
save, don't disrupt their live character, and use a uniquely named test
character/snapshot if native actor construction is required. Candidate test:
record actual actor X/Y/Z and current square, save a test NPC, instantiate a
different NPC at distinguishable coordinates, invoke native load without
manual coordinate restoration, then inspect X/Y/Z, current square and world
registration. Test actual save/restart/reload separately from an in-session
round trip. Report concrete before/after values and observed errors, not
merely an asserted pass. These are proposed test ideas, NOT yet assigned
or verified safe in the installed B42 runtime.

Related R1 concern: SSPersistence.tick scans every indexed saved location and
calls getGridSquare every tick. This is a demonstrated scaling property of
the code, not a measured bottleneck. It may compensate for loaded-square events
that occurred before registry/player initialization. Investigate engine event
timing, potential one-time catch-up, chunk-based indices or safe caching before
deciding whether an optimization is required. Don't assume a cached grid-square
reference remains valid across chunk unload/recycling.

The already published R1 mail,
ai-workflow/mail/implementer/archive/2026-11-15-persist-01-r1-review.md,
calls this a mandatory correction. The orchestrator acknowledged that wording
is stronger than the evidence supports. User explicitly requested thinking
through the question BEFORE changing that assignment. This handoff records
the revised reasoning but does NOT revise, supersede or dispatch a new Codex
assignment. Any follow-up needs explicit coordination.

## Continuation after this discussion
First resolve native B42 position/serializer behavior via installed source or
a carefully scoped user-run world probe. Then revisit the per-tick scan's
necessity and actual performance using evidence. Clarify the outstanding R1
mail before the implementer acts on its optimization instruction. Source branch
codex/persistence-b42 and canonical B42 have diverged; don't force-update
either. Persistence acceptance still requires live disposable-world verification.
SS Debug hub/inspector and AI work remain unassigned.


## SSR-TEST-01 decision (2026-11-15)
User approved introducing a reusable in-game Tests UI immediately, accessible via a development/testing-gated right-click context-menu entry (without requiring vanilla -debug). UI should explicitly warn that tests can irreversibly change the world and require affirmative acknowledgement before each destructive run. A small test registry decouples test definitions from UI; tests can be added/replaced/removed. Result reporting includes concrete observations, errors, inconclusive/setup error, and optional multi-tick execution. One world-mutating test at a time initially. No full SS Debug hub or generalized DSL/runner.

First test: the native IsoPlayer save/load and position/world-registration diagnostic already discussed in the SSR-PERSIST-01 R1 investigation. Codex to independently inspect installed B42, implement a safe isolated test NPC/snapshot and log original vs restored X/Y/Z without forcing coordinates, then provide instructions for user to execute in a fresh disposable world. Distinguish same-session probe from restart roundtrip; do not modify human player data. No actual runtime evidence exists yet.

Canonical assignment: ai-workflow/assignments/tests-ui-01.md; addressed mail: ai-workflow/mail/implementer/archive/2026-11-15-test-01.md on B42. Status DELIVERED FOR REVIEW (see delivery below). Coordinate with existing exclusive local Codex branch codex/persistence-b42; no second implementer, no automatic merge to B42. Previous R1 mandatory tick optimization remains superseded by engine investigation; no speculative rewrite requested.


## SSR-TEST-01 / R1 delivery (2026-11-15)

Source 594e65bc6af92927d8ec2c4b20c5c36806bf31a3, parent c1dea17a8f052a8e861635a86eec1619e791035e, on exclusive
codex/persistence-b42 checkout. Addressed report: mail/orchestrator/inbox/2026-11-15-test-01-r1-delivery.md.
All three R1/test requests processed and archived; clarification supersedes
the original mandatory-optimization request. No persistence scan/unload/loader
rewrite for this follow-up. No source merge into B42 or acceptance.

Minimal opt-in Tests UI uses existing Debug Options, no -debug requirement,
per-run warning consent, independent registry and one active test. Native
position probe is restricted to inspected 42.22.2 and disposable single-player
worlds; raw distinct actors, unique retained snapshots, native-safe cleanup and
explicit stage/restart/resume. Human player slots/save are never replaced.

Installed source establishes XYZ serialization/restoration but separate square
registration. Actual runtime observations remain NOT RUN. Same-floor Z is not
independently distinguished; session-token change is not proof of process restart.
Read docs/NATIVE_POSITION_R1.md and docs/TESTS_UI.md on implementation ref.
174 automated tests, 112 Lua syntax checks; LuaLS 88 legacy diagnostics, none
in new modules. Mocks do not establish native rendering or engine correctness.

Next actor: orchestrator reviews exact delivery and user runs a NEW disposable
world probe after game restart. Full debug hub/inspector and AI remain unassigned.


Runtime follow-up: user opened Tests UI; version gate prevented running.
Fix delivered at 4164ad7bead8d6dd2d7db3c6e514e7c9acb52a42 (parent
5f215b056cf00908a6c84a95dfa4dde89348fef2): compare full build API; preserve
checkbox on selection at user request; show disabled-run reason. 177 tests and
112 syntax checks pass. Actual native roundtrip still NOT RUN. Report: mail/orchestrator/inbox/2026-11-15-test-01-runtime-fix.md.


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


## SSR-TEST-01 real runtime review (2026-11-15)
Tests UI was implemented and exercised in real B42.22.2. User ran two native
same-session probes and staged/resumed across a genuine game restart. Log:
docs/evidence/NATIVE_POSITION_2026-11-15.log on codex/persistence-b42.
Native load independently restored X/Y and identity marker; currentSquare
and square membership remained at intentionally different constructor location.
The human was unaffected, isolated actors were detached, and missing-file
load was silent. Z was unchanged and not independently proven by runtime probe.
Do not infer a bug in current SSR loader solely from deliberate mismatched
constructor diagnostic: SSR creates actor at saved square. Do not add speculative
square repairs or remove manual coordinate setters without separate evidence.
Test UI/probe scope is satisfied; SSR-PERSIST-01 still requires true survivor
and group lifecycle testing. Orchestrator review is recorded at
ai-workflow/mail/implementer/archive/2026-11-15-test-01-orchestrator-review.md
on B42. Codex reports 178 tests, 112 syntax checks; not independently rerun.
Recent startup translation/recipe error fixes verified by absence of prior
startup errors after restart, but actual crafting untested. Production source
branch remains codex/persistence-b42; no merge. Next user-led gate:
docs/PERSISTENCE_B42.md's real save/reload/unload/death tests.

## SSR-TEST-02 requested (2026-11-15)
User wants to verify whether a cell-only IsoPlayer construction followed by native load can simplify SSR survivor reconstruction. Do not assume such a Lua-exposed constructor is viable based on the previous assistant's claim. Codex is requested to inspect the exact installed 42.22.2 constructor and lifecycle first; if safe, implement a focused opt-in test via existing SS Tests UI. Log state before/after native load plus any explicitly safe world registration, with human guards and cleanup. No production loader changes until runtime findings reviewed; no automatic merge. Assignment: ai-workflow/assignments/test-cell-only-isoplayer-02.md; inbox: ai-workflow/mail/implementer/archive/2026-11-15-test-02-cell-only.md. Status unacknowledged.


## New source-only IsoSurvivor comparison (2026-11-15)
User requested read-only analysis of IsoSurvivor vs IsoPlayer from installed B42.22.2 Java/Lua before in-game testing. Compare concrete class/engine use, native save/load, character lifecycle, gameplay hooks and SSR migration costs, without altering production implementation or Tests UI. Codex request: ai-workflow/assignments/isosurvivor-vs-isoplayer-analysis.md; inbox ai-workflow/mail/implementer/archive/2026-11-15-isosurvivor-analysis.md. Pending acknowledgment; separate from active SSR-TEST-02.


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

## SSR world/knowledge/simulation direction recorded (2026-11-16)
User requested durable preservation of recent direction WITHOUT associating it with any other project. Read `docs/SURVIVOR_WORLD_KNOWLEDGE_DIRECTION.md` on B42. Main ideas: source-backed B42 vertical/Z and building-area correctness (concrete issue), shared technical observation but individual survivor knowledge/provenance, containers requiring inspection, remembered loot possibly becoming stale, radio/social transmission, persistent survivor identity and possible lower-frequency offscreen simulation, and hypothetical eventual multiplayer server authority/reconciliation. These are principles/possibilities, NOT a new implementation assignment or authorization to refactor; profile caching rather than assume benefit.


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
