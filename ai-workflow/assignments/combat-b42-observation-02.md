# SSR-COMBAT-02 — Read-only live combat diagnostic on existing SSR survivor

Date: 2026-11-17
Status: REQUESTED / NOT ACKNOWLEDGED
Coordinator: ChatGPT SSR orchestrator
Canonical branch: B42
Source: exclusive existing local Codex worktree codex/persistence-b42, subject to ownership check

## Evidence baseline
SSR-COMBAT-01 installed-B42.22.2 source report docs/COMBAT_B42_INVESTIGATION_01.md (source report commit 79c6d10519542b174c5e3c88954615e1de19820a). User observes survivors don't attempt combat. Confirmed: two AIManager equip branches requiring hasWeapon() and nil primary are contradictory, ordinary zombie PursueTask requires SSR wrapper, NPC AIComponent aiming/control is not set by normal setIsAiming field, and inspected SwipeStatePlayer AttackCollisionCheck isLocalPlayer gate excludes ordinary NPC route. These are source findings, NOT a measured live combat failure; attack stage and alternative native paths still unknown. getLuaObjectList uses valid 1-based table indexing; nil outdoor rooms compare equal. No speculative damage calls or slot manipulation.

## Task
Implement one small, explicitly user-invoked **Combat — inspect existing survivor** diagnostic in existing gated SS Tests UI. Read-only: no actor construction, zombies, combat attempts, movement, equipment, world mutation, native attack request, automatic polling or forced AI task update. No production combat behavior edits. Honor existing consent UX unless well-scoped readOnly existing runner avoids mutating operations. Single-player/one human guard maintained.

- Make explicit survivor selection (existing loaded SSR ID >0; either a compact ID entry or list if existing UI supports it), verify SSM wrapper owns this actor; not dead, no human/local slots; same cell and world.
- Record time/frame/game speed, SSR ID/actor, group role, AIMode, relevant AI manager scheduling/filters, NPC/perception cached fields (LastEnemeySeen class/alive/xyz/room, seenCount/dangerSeenCount, close enemy), current task queue front/names count, waiting/cooldown/attack readiness flags, primary weapon type/ammo/state, actor position/room and optional target distance/Z. Include player/world loaded state and known fields needed to distinguish no target vs task blocked vs request not started.
- Rely only on verified nonmutating B42 getters and existing cached data. Do not call DoVision, getLuaObjectList (rewrites global Objects), AIManager task selection/update, Task:isValid/isComplete, WeaponReady, needToFollow, RealCanSee, pressedAttack, or any other mutating predicates; don't invoke getters with lazy side effects without verifying.
- If there's no target at snapshot time, label no-target-at-snapshot (not automatically a broken perception system). Capture when user sees NPC near a zombie, preferably a healthy survivor with equipped weapon near one zombie in disposable world. No automatic repro or root-cause claims.
- Include native control flags safely obtainable (NPC AIComponent control variable state, attackStarted/initiateAttack, actual aiming, native swing state) if exposed, otherwise mark unavailable with concrete reason. Correctly distinguish SSR-visible state from actual engine animation/hit.
- Provide enough log output to interpret first stage; bounded output and no expensive full-world scans. Observations may be INCONCLUSIVE instead of PASSED/FAILED in absence of ground truth. Preserve previous test registry and Test04 R1 world-saved baseline functionality.
- Don't build request/event interception or running sampling yet. If snapshot can't distinguish stage, PROPOSE a second opt-in bounded temporal observer in delivery, with exact safe hooks, ownership, cleanup, native event API, and risk. No speculative production edits or direct victim:Hit(), Java changes, or local-slot swap.
- Automated regression tests include wrong survivor ID, unloaded/dead actor, guard local human, no enemy, weapon missing, unavailable native fields, no mutation from observation and no automatic execution. Confirm installed engine exposure/safety.
- Deliver source SHA/parent/changed paths, test results, explicit run steps and actual-vs-not-run evidence in ai-workflow/mail/orchestrator/inbox on B42; docs and handoff. No implementation branch merge.

## Separate potential fixes (NOT in this assignment)
Equip condition, zombie pursuit targeting and follow predicate are proven source-level issues deserving isolated changes and tests, but they do not establish native B42 combat compatibility. Do not conflate a policy/queue fix with successful native melee collision.
