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
This repo now has ai-workflow inspired by Tertalis but wholly local to Super-Survivors. README explains operation; index routes. Task spec assignments/persistence-b42.md and mail/implementer/inbox/2026-11-15-persist-01.md. Current status: requested, NO Codex acknowledgment and NO implementation evidence. Writing inbox mail cannot launch Codex. Future orchestrator should read index, protocol, state, handoff, pending orchestrator inbox and exact source/ref before resuming.

## Next
Verify workflow files committed on B42. User explicitly starts local Codex to read ai-workflow/index.md; Codex claims owned branch, acknowledges, implements and reports to orchestrator inbox. Review actual diff, commits and test evidence; user does real disposable-world validation. Then assign SS Debug hub/inspector and later AI design implementation.
