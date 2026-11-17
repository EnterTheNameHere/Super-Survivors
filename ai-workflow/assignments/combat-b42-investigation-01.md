# SSR-COMBAT-01 — Why survivors do not attempt to fight (B42)

Date: 2026-11-17
Status: REQUESTED, source/evidence diagnosis first; NO gameplay fix preauthorized
Canonical coordination: B42
Source implementation/investigation worktree: existing exclusive codex/persistence-b42 only after confirming current implementer ownership and finishing/deferring pending Test-04 R1
Owner: Local Codex, report findings to SSR orchestrator

## User observation / scope

User reports survivors in current gameplay **are not trying to fight**. This is an actual user observation, not yet an engine-verified cause. The new near-term game objective is basic survivor survival (food/water/weapons/threat response), with combat inability a high-priority blocker. Diagnose the end-to-end chain first, without speculative broad combat redesign or forced hits.

## Source-backed suspects to verify

Current source on codex/persistence-b42 at investigation time:
- `42/media/lua/client/3_Other/SuperSurvivor.lua` `DoVision` around lines 1654-1720 scans `getCell():getLuaObjectList()` with `ipairs`, picks nearest using bracket indexing, sets `LastEnemeySeen`, `dangerSeenCount`, `seenCount`. Confirm collection type/index convention and actual B42 zombie membership; don't conclude this is broken without native evidence.
- Legacy task selection `NPC_CheckPursueScore`, `Task_Is...`, `NPCTask_DoAttack` around lines 2429-2640; search *all* call sites across repository, not only methods in one file. Trace whether and when AttackTask is queued, role/fear/weapon/condition gating and whether another task overrides it.
- `7_Tasks/AttackTask.lua`: `isValid()` checks current target and `isInSameRoom`, `isComplete()` checks follow/danger/range/injury, `update()` requests attack. **Note:** `isInSameRoom` compares square `getRoom()` values, so two outside squares with both nil can compare equal. Do not declare all outdoor combat invalid on source alone; test indoor/outdoor transitions and cross-room targets.
- `SuperSurvivor:hasWeapon()` around line 1522 requires equipped HandWeapon. Determine barehanded/shove expectation and weapon acquisition. `requestCombatAttack` around 4231-4265 checks target, cooldown, `CanAttackAlt`, running, `IsAttackRange`, `WeaponReady`, then face, target square, aim, and native `pressedAttack`; checks `isInitiateAttack/isAttackStarted`. Distinguish did not request vs request rejected vs engine attack initiated vs actual hit/damage.
- Existing `setBlockMovement(true)`, `setNpc(true)`, actor states, `SwipeStatePlayer`-specific logic, B42 combat manager and AI update cadence may affect attack; inspect current installed 42.22.2 methods and actual logs without guessing.

## Requested work

1. **Read-only complete call-graph/source and installed-JAR review** of detection -> candidate enemy -> decision/priority -> AttackTask -> attack request -> native B42 attack start/hit. Include the actual update scheduler/task invocation and old B40/B41 paths only as historical clues, not engine contracts.
2. Locate the first decision point which could explain 'doesn't try to fight'. Report evidence versus hypotheses; check any disabled/unreachable attack scheduling path, list indexing/collection type mismatch, predicates making task immediately invalid, weapon requirements, and native AI attack path.
3. Design a minimal controlled in-game **combat diagnostic** using existing gated SS Tests UI: only user-initiated on disposable world with explicit warning and fresh consent for any spawned zombie/survivor or world changes; prefer a read-only snapshot of an existing owned NPC's perception/task/weapon/attack flags first. Avoid automatic provocation/kill, human control manipulation or arbitrary actor cleanup. Make preconditions and sample log fields clear; if user setup required, say so.
4. If the source audit alone proves a narrow defect, propose a separately reviewable fix and regression tests; DO NOT edit production combat behavior under this diagnosis request. Do not bypass B42 native damage/combat manager with direct Hit calls just to get animations or kills.
5. Since Test 04 R1 persistent baseline is pending on the same implementation branch, acknowledge ordering/ownership before starting; never run concurrent implementers on one source branch.
6. Deliver report, exact commit if docs/tests-only, actual tested vs not-run, recommended next bounded action via `ai-workflow/mail/orchestrator/inbox` on B42. Record design and handoff, no automatic source merge.

## Success criterion for diagnosis

We can identify whether NPCs (a) fail to perceive zombies, (b) perceive but deliberately choose not to attack, (c) queue AttackTask but cancel/replace it, (d) reach attack request but preconditions reject it, or (e) successfully request attack but B42 does not produce attack animation/hit. That classification leads to the next implementation assignment.
