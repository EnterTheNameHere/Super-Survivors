# SSR-COMBAT-06 — B42 native combat integration feasibility and reversible prototype

Date: 2026-11-18
Status: STAGE A DELIVERED / BLOCKED FOR FULL NATIVE COMBAT / STAGE B NOT ENTERED
Priority: Combat. Implementation authorization is **bounded and conditional** below.
Ownership: one existing Codex implementer, exclusive source checkout codex/persistence-b42. Do not edit/integrate protected B42 gameplay code.

## Evidence and target
Combat05 ID3 natural request at frame1189: original requestCombatAttack returned true; attackStarted=false->true, initiateAttack=false->true; by frame1190 attackStarted remained true but initiateAttack=false, no observed swing, no subsequent observed StopWalk. The 3-tick observer ended at1192. Earlier Combat03 had98 natural completed rejections false,busy from preexisting latched actors.
Installed B42.22.2 source audit (docs/COMBAT_B42_CORRECTION_OPTIONS_04.md) shows NPC AIComponent.postUpdatePlayer writes initiateAttack from its private control object before animation transitions, while ordinary SwipeStatePlayer melee collision callback isLocalPlayer-gated. AIComponent, AIBrainPlayerControlVars, CombatManager not registered in default Lua Exposer; old B41 NPC attack APIs absent. Therefore a Lua attack-flag toggle alone is not a complete solution.

## Authorized task
Find and implement the **smallest reversible, opt-in experimental native-combat handoff**, ONLY IF installed game source proves an ordinary accessible supported route that does not require undocumented reflection/Class tokens/native patches, local player slot reassignment, synthetic victim damage, or forcing action-state/flag transitions. The prototype must be explicitly disabled by default and run only with user-controlled consent in a disposable save / debug mode; never silently affect normal SSR AI or existing saves.

Stage A — determine executable route before editing production:
1. Trace exact Lua-exposed paths and NPC control ownership for first attack, animation, swing, reset, weapon and reload invariants; enumerate all available actor and native API exposure and current SSR callsites. Do not invent interfaces from Javadoc signatures.
2. Separately resolve a supported nonlocal native melee collision/damage path. Exact local-player gate in normal SwipeStatePlayer callback must not be ignored. If absent, report **BLOCKED for full native combat**, not a cosmetic success.
3. Present short decision table in docs/COMBAT_NATIVE_INTEGRATION_PROTOTYPE_06.md: route, verified source/API, what behavior can be proven, constraints, regression/rollback, missing engine support.
4. Gate: If no safe Lua native route meets both A(attack lifecycle) and B(native collision/damage) requirements, **do not implement a fake combat prototype**. Deliver evidence, smallest proposed alternative as a distinct design for user approval, and stop. In particular, don't add periodic flag reset, direct victim:Hit calls, local-player-slot spoof, a Java patch/modloader, broad invasive hooks, or global context changes.

Stage B — conditional implementation, only if both routes verified:
1. Make a self-contained experimental adapter, opt-in explicit diagnostic launch, scoped to exact owned SSR NPC and current world, reversible/teardown on stop, death/unload/replacement, session change and exceptions. Avoid global vanilla method replacements or interception of human actor; no hidden continuous rearm.
2. Preserve one natural request, native animation/collision/damage and cleanup, native weapon condition/stamina/ammo and hit vs miss, avoid double hits and third-party mods interaction. Distinguish NPC internal control from local human UI/slots; no invented damage.
3. Include focused tests, Lua syntax/source validation, user-run disposable-world test instructions. Mark native results **PENDING** until actually run. No claim full success from unit mocks, OnWeaponSwing or HitPoint alone.
4. Do NOT modify production AI, default behavior, existing Combat05 observer, persistence, existing UI, or user settings/saves; isolate experiment. No merge to protected branch without review.

## In all cases
- Preserve the exact user code/settings/common saves and concurrent documentation revisions; do not revert user changes.
- Include positive and negative evidence and explicit source vs runtime distinctions; mention constraints if only animation could be repaired.
- No more repetitive already-stuck diagnostics. Combat-first; inventory plan docs/INVENTORY_UI_IMPLEMENTATION_PLAN_B42.md deferred.
- Delivery via ai-workflow/mail/orchestrator/inbox on B42, source report/optional experiment on codex/persistence-b42, exact commit, tests and limitations.
- Earlier source: docs/COMBAT_B42_CORRECTION_OPTIONS_04.md; runtime docs/evidence/COMBAT_FIRST_ACCEPTED_ATTACK_2026-11-18.log.
