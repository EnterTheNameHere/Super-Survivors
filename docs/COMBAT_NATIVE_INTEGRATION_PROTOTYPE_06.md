# Combat06: native integration gate

2026-11-18. **BLOCKED for full native combat under the current constraints. Stage B not entered; no prototype implemented.**

The installed build supplies a real actor attack request but no verified ordinary Lua route that satisfies both native NPC control ownership and nonlocal native melee collision/damage. An initiation-only or animated prototype would not meet the assignment. No runtime source, Combat05 observer, AI, existing UI, persistence, settings or save changed.

## Decision table

| Route | Verified source/API | What it establishes / missing support | Gate |
| --- | --- | --- | --- |
| IsoPlayer:pressedAttack() | Public method on exposed IsoPlayer; forwards to CombatManager.pressedAttack(IsoPlayer). Actual ID3 natural request accepted in Combat05. | Immediate initiation/started flags; AI post-update can replace initiation before animation. No collision authority conferred. | Lifecycle incomplete; damage absent. |
| AttemptAttack()/AttemptAttack(float)/DoAttack(float[,String]) | Public inherited/player methods. Player DoAttack funnels to pressedAttack and returns false in this implementation; inherited AttemptAttack(float) eventually dispatches virtual DoAttack. | Changing entry-method spelling does not change the player control/collision pipeline. | No alternative. |
| AIComponent.getHumanControlVars() | Public Java getter, private final owned AIBrainPlayerControlVars. Component/control types not registered in Lua Exposer; controls have public instance fields, no command setters. | Relevant authoritative NPC controls exist, but no verified ordinary exposed Lua control bridge. Component map/Class traversal does not expose missing methods/fields. | Lifecycle blocked. |
| Actor input/force-aim methods | CharacterInputComponentEntity default methods act on CharacterInputComponent. NPC update instead uses AIComponent; NPC isAiming reads AI controls. | Accessible inherited input methods are not the missing NPC command channel. Normal human input branch is skipped for NPC. | No complete lifecycle route. |
| Normal SwipeStatePlayer animation | Exposed state; private doAttack and collision listener. Normal XML transitions consume initiateAttack; entry emits OnWeaponSwing, exit clears started. | Authoritative control must survive until consumption. Forcing flags/state/events is excluded. | No allowed handoff repair established. |
| Normal AttackCollisionCheck | Private listener calls public Java CombatManager.attackCollisionCheck only for !ATTACKED && IsoPlayer.isLocalPlayer(owner). | Standalone nonlocal SSR actor fails identity gate. SP isLocal and playerNum are not isLocalPlayer. | Damage blocked. |
| Direct native manager collision | Java signature exists; manager absent from default exposed-class registrations; no ordinary Lua GlobalObject getter found. Whole-JAR caller locator finds the normal Swipe listener. | Public Java is not a supported Lua command. Reflection/exposer registration/direct replay would violate the gate or bypass lifecycle. | No supported route. |
| Exposed event/state broadcaster | State.animEvent forwards to its broadcaster; Swipe's registered listener still contains the gate. | Event forwarding cannot change the listener's identity requirement. Synthetic Lua swing/hitpoint events run listeners without calculating a hit. | No damage route; do not replay. |
| IsoSurvivor actor replacement | Class exposed; no replacement attack override. Inherited old DoAttack forces SwipeStatePlayer; Swipe entry operates on IsoPlayer. | Different actor class, incompatible state assumptions and persistence/AI footprint. Its ranged branch counts candidate objects, not a separate successful damage path. | Not a compatible minimal adapter. |
| getCombatConfig / ballistics access | CombatConfig is exposed get/set configuration. Actor ballistics getter returns its cached controller; BallisticsController not registered as a normal exposed type. | Config does not issue NPC attacks or change hard-coded listener predicate. Ranged aiming helpers do not supply nonlocal melee collision. | No route; do not alter global config. |
| Flag reset/reassert, NPC toggle, direct Hit, slots, Java | Excluded by assignment and prior user constraints. | May hide latch/ownership defects or invent damage; not a native integration. | Rejected, not prototyped. |

## Evidence and scope

Exclusive existing codex/persistence-b42 checkout, start 077a608d18b2926e0be9cc9ce15ce37e9ec77834; ACK 4c554a0. Canonical request 39b18b94639cad81a3a7a3c8217b0305567da212. Source evidence file: **docs/evidence/COMBAT_NATIVE_API_06.txt**. User's uncommitted source/settings/common saves and concurrent documentation remain untouched.

Installed G:/Steam/steamapps/common/ProjectZomboid/projectzomboid.jar SHA256 recomputed: **3c4a7c5f149d784758c6fb5f8fa85f3a21d572e38bc081400e89035f8120d287**, same reviewed B42.22.2 revision 3d39148846. IsoPlayer, IsoGameCharacter, IsoLivingCharacter, AIComponent, AIBrainPlayerControlVars, SwipeStatePlayer, CombatManager, LuaManager.Exposer and LuaJavaClassExposer extraction bytes compare equal to the current JAR. Additional input, actor, state, configuration and ballistics classes were freshly extracted/decompiled read-only. No game class was loaded or modified by this audit.

Public method/field descriptors were inspected with tools/inspect_game_api.py, following the entire IsoPlayer superclass/interface graph, not just declared player methods. This catches inherited CharacterInputComponentEntity/ECSEntity APIs and confirms the absent B41 NPCSetAttack/NPCSetAiming/NPCGetAiming aliases. Exposer registration and implementation were inspected separately; a method list is not by itself proof of Lua usability.

Whole-JAR constant-reference candidate scans covered getHumanControlVars, control-field reads/writes, direct attack flag writes and attackCollisionCheck callers; matched source methods were inspected. Raw operand matching is a locator, not a bytecode instruction decoder or proof against every dynamic/native mechanism. Findings are scoped to ordinary inspected APIs and the current installed build; undocumented reflection, class-exposure modification, third-party Java and future engine changes are excluded, not explored as loopholes.

### NPC control and consumption

Exact native sources: zombie.characters.IsoPlayer.setNpc/updateInternal2/pressedAttack/DoAttack; zombie.characters.IsoGameCharacter.isAiming/postUpdateAnimating; zombie.characters.component.AIComponent; zombie.ai.AIBrainPlayerControlVars.

- setNpc(true) installs AIComponent on a non-NPC actor; repeated true preserves it. The owned control object defaults false/zero; AIComponent.update is empty.
- doUpdatePlayerControls supplies melee/bannedAttacking, postUpdatePlayer supplies initiateAttack/running/justMoved and movement rates; player also reads strafe axes. isAiming reads AI control aiming for NPCs rather than the ordinary aim field, outside the special throwing override.
- The control-field reference scan found reads in those consumers and no direct PUTFIELD producer for that control class elsewhere in the JAR. That supports the absence of a located ordinary command producer; it does not prove dynamic Java/reflection can never write fields.
- Scheduled actor update precedes scheduler postupdate. postUpdateAnimating calls ActionContext.update and AdvancedAnimator.update; native player melee XML requires initiateAttack. A callback/state update must not be manually run to force consumption.
- IsoPlayer.DoAttack overloads call pressedAttack, while the generic superclass implementation changes state and consumes items. Calling a base implementation through a guessed token/superclass bridge is not an ordinary player API and is outside the gate.
- CharacterInputComponentEntity.getCharacterInputComponent/setForceAim and other human input methods are distinct from AIComponent.humanControlVars. The normal update input branch is guarded by !isNpc. Their existence is positive API evidence but does not prove NPC attack ownership.

LuaManager.Exposer registers IsoPlayer/IsoGameCharacter/SwipeStatePlayer/IsoSurvivor/CombatConfig and standard HashMap. It does not register AIComponent, ECSComponent, AIBrainPlayerControlVars, CombatManager or BallisticsController in the inspected list. Its shouldExpose checks the whitelist even during recursive traversal. LuaJavaClassExposer exposes eligible public methods and public static fields/class tables, not arbitrary public instance fields as editable Lua properties. The public ECSEntity map/getter therefore does not establish a supported mutable control object. No guessed class token, reflective access or runtime exposure registration was attempted.

### Collision, state and event ownership

Exact sources: zombie.ai.states.SwipeStatePlayer constructor/enter/doAttack/exit/OnAnimEvent_AttackCollisionCheck; zombie.ai.State.animEvent; zombie.CombatManager.attackCollisionCheck; zombie.characters.IsoPlayer.isLocalPlayer; zombie.characters.component.NetworkComponent.isLocal.

Swipe registers its private listener for AttackCollisionCheck. State.animEvent merely forwards events; reaching that listener through the public inherited broadcaster still checks exact actual local-player membership before native collision. CombatManager has some NPC-aware internal branches, but they do not provide an ordinary alternative caller or remove the prior gate. Native isLocal in SP and the mutable IsoPlayer.instance update cursor cannot be substituted for local-player ownership. Combat05's singleton guard correction remains intact.

The native hit routine emits OnWeaponSwingHitPoint before final target/damage processing. Emitting that Lua event is not collision calculation. Installed media/lua/shared/TimedActions/ISReloadWeaponAction.lua:470/:542 subscribes onShoot, which changes chamber/spent-round/reload state. Synthetic event replay could therefore alter ammunition without any native hit. It is explicitly not an experiment candidate.

IsoSurvivor is not an overlooked current standalone-human melee backend: it has no overriding attack implementation; inherited DoAttack changes to SwipeStatePlayer, whose enter casts the owner to IsoPlayer. Its old ranged branch calculates candidate count and then follows that same state path. Switching SSR's actor class would also affect native saves, clothing, UI, controls and AI—not a reversible per-actor combat adapter. No actor was created to try it.

### SSR callers and weapon invariants

- SuperSurvivor.lua:4231 requestCombatAttack is the normal enemy-combat path, reached by Attack/NPC_Attack and active AttackTask. It validates cached target/cooldown/range/readiness, calls StopWalk, faces/targets, then native pressedAttack and sets cooldown/auto-repeat from immediate flags. Combat05 observes that path without changing it.
- SuperSurvivor:PlayerUpdate can naturally repeat requests through Attack/NPC_Attack. StopWalk and movement/task completion can cancel initiation; no new repeating hook or cancellation policy is authorized.
- AttemptEntryIntoBuildingTask.lua:250 still calls actor:AttemptAttack() for a building-entry action; it reaches the same native player initiation path. A requestCombatAttack observer is not a universal observer of all native attack calls. The captured Combat05 accepted interval nonetheless records a normal wrapper request.
- WeaponReady (:3739) is a mutator: it repairs/unjams firearms and performs ammunition lookup/bookkeeping; ReadyGun (:3435) and reload helpers can unjam, create/fill/insert/eject ammunition containers or queue actions. They were read, not invoked. Normal native isWeaponReady is a separate cached model/action readiness getter.
- A future adapter must preserve weapon identity, hands, ammo/chamber/magazine, condition, endurance, actual native hit/miss and action interruption. Existing SSR automatic repair/ammunition policy must be stated separately from engine-native resource accounting. This task does not change either policy or use their effects as evidence of a functioning native shot.

## Runtime evidence versus feasibility

Combat05 evidence/COMBAT_FIRST_ACCEPTED_ATTACK_2026-11-18.log is actual native execution: ID3 frame1189 starts false/false, natural request returns true with both flags true; next tick1190 loses initiation while started remains true, without a recorded later StopWalk or swing. Three-tick follow-up ends1192, hooks restored. It corroborates the control-write loss interval; it does not identify the exact setter, first-ever attack, eventual animation, native collision or damage.

Combat03's 98 completed busy rejections demonstrate a later latched condition on other sampled intervals. Neither dataset validates a complete correction. No further repetitive already-busy diagnostic is proposed; no new game test, attack, fixture, option or adapter was introduced in Combat06.

## Smallest alternative architecture — design only, approval required separately

Keep combat intent and the engine backend separate in the future design: one actor/world-bound request with a unique lifetime, one backend owner for initiation/resource accounting/collision completion, and explicit interruption/teardown. Backend capabilities must distinguish **can initiate and release a native attack** from **can resolve native nonlocal damage**; an animated actor or accepted flag is not a completed attack. This is a design boundary, not an empty adapter or new no-op wired into production.

Under the current requirements, the only acceptable native backend would use an engine-supplied ordinary Lua NPC command/control interface and native nonlocal collision authority. That support was not found here. Keep this integration unimplemented until such an API/build is available and verified; do not substitute a human slot or class-exposure patch. Other porting work can be ordered separately by orchestration; inventory remains deferred until explicitly assigned.

If the user instead wants functional NPC fighting without waiting for native support, a **separately approved custom Lua combat backend design** would relax the native-damage-only requirement and define its own collision/resource/animation authority. That is a different product/compatibility decision and is not approved or implemented by this task. No victim:Hit loop, synthetic event or approximate damage formula is proposed as an incremental fix here. Java modification remains excluded.

## Reopening criteria, tests and rollback

Before any Stage B code: verify actual exposed signatures and ownership semantics for both missing interfaces on the installed build. Then authorize a disabled-by-default adapter launched only with explicit disposable-save/debug consent, scoped to an exact NPC/world; one natural request, no global vanilla replacements, and native cleanup on all outcomes.

Required evidence would include first request -> swing/state entry -> actual native collision -> attributable hit or valid miss -> normal release -> a second natural request; obstruction/Z/range, weapon condition/stamina and ammo/chamber/reload conservation; no double hit or shared human UI/slot/singleton effects; interruption/death/unload/replacement/world/menu/error/reload teardown; and compatibility with the current invincibility/mod setup recorded. Mock/unit results and swing/HitPoint alone cannot pass damage acceptance.

Rollback must detach only owned per-actor adapter work without resetting native combat flags, replacing outside hooks, replaying damage or touching saves. Since no admissible adapter exists in this delivery, rollback is simply removing these documentation changes; there is no runtime component or restart requirement.

Checks performed: installed JAR hash/byte provenance, declared and inherited member descriptors, exposure implementation, whole-JAR reference locators plus matched source, installed Lua and current SSR caller audit, and git diff --check. No test suite or Lua syntax run is necessary for this documentation-only gate decision. Prior 291 tests/117 syntax checks belong to Combat05 and are not Combat06 runtime validation. **Deliver Stage A findings and stop; full native combat remains BLOCKED.**
