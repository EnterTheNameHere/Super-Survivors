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
