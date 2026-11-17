# SSR-COMBAT-04 — First native attack transition and correction options

Date: 2026-11-17. Status: SOURCE RESEARCH / EXPERIMENT DESIGN DELIVERED FOR REVIEW.
Canonical B42. Existing exclusive Codex source branch codex/persistence-b42; confirm ownership before starting.
Source/native API investigation and future experiment DESIGN ONLY. No production fixes or fixtures authorized.

## Grounded evidence
Combat02: 33 Roderick ID9 snapshots, attackStarted=true, initiate=false, animation/swing=false; 11 native in-range, equipped and attack task active.
Combat03: five actual natural traces across IDs 9,1,5 with 102 intercepted request entries, 98 completed logged returns ALL false,busy; four records censored at cap. All traces began with attackStarted preexisting true, no false-to-true transition, swing or hitpoint observed. Reports docs/COMBAT_HANDOFF_TRACE_B42.md and docs/evidence/COMBAT_TRACE_2026-11-17.log on source branch.
SSR is demonstrably invoking requestCombatAttack but the busy guard rejects requests before native pressedAttack in these cases. Origin of stuck flag remains UNKNOWN.

## Investigation requested
1. Inspect installed B42.22.2 exact Java/Lua contract/call ordering for CombatManager.pressedAttack, IsoPlayer.updateInternal2, AIComponent.postUpdatePlayer/humanControlVars, SwipeStatePlayer state entry/exit/collision and SSR StopWalk/task updates. Track all set/clear sites of attackStarted/initiateAttack and any NPC-specific control APIs. Verify Java signatures and Lua exposure.
2. Determine whether pressedAttack is a valid native entry point for standalone nonlocal NPC IsoPlayer, whether NPC-specific control must be supplied, and which supported path can initiate animation and native hit calculation. Separate source evidence from unverified causal timeline.
3. Investigate initial actor state before first attack, including fresh vs native-loaded survivors, without pretending already-stuck traces show initial setter. If source alone insufficient, DESIGN a bounded opt-in pre-first-request diagnostic in an existing fresh never-attacked NPC or a separately consented disposable-world fixture. Do NOT implement fixture or modify world yet.
4. Distinguish combat initiation, animation, collision callback, and actual hit/damage. Installed ordinary SwipeStatePlayer collision gate requires isLocalPlayer; identify if documented alternative for standalone NPC exists. Do not employ player slot swap, synthetic direct Hit, artificial reset or Java patch.
5. Compare historical legacy B41 NPC framework B41 APIs (NPCSetAttack/NPCSetAiming) to installed current JAR, where absent; do not copy old legacy B41 NPC framework combat helpers or assume legacy B41 NPC framework supports B42.
6. Deliver a candidate matrix with source-native evidence, verified Lua accessibility, which stage each candidate addresses, risks and test acceptance requirements. Recommend smallest valid next approved experiment or correction path.
7. Preserve old logs, user source/settings/save changes, Test04 R1 baseline and diagnostics. No code production/AI/UI/inventory changes, no uncontrolled hooks or automatic merge.

Deliver docs/COMBAT_B42_CORRECTION_OPTIONS_04.md on source branch, inbox ACK and report on B42, identify actual vs untested, source commit and checks. Combat priority ahead of inventory Phase 1; single exclusive worktree.
