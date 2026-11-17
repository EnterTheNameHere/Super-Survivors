# B42 survivor combat: source investigation 01

17 November 2026. SSR-COMBAT-01. **Analysis/proposal only; no gameplay or diagnostic
implementation.** User sees survivors not trying to fight. No observed combat
stage or root cause is established by existing logs.

Source: codex/persistence-b42, production tree at
3e99b8f2637616238ac0d02e73d579dd3ccfc1f6 (investigation ACK 913d2cef97d954e24ed345fa5d86eec57db72ea4).
Working-copy changes to SuperSurvivor.lua rename commented/local identifiers in
spawn/sixth-sense code; combat utility changes rename locals/comments. Audited
chain matches committed code. User edits remain untouched/uncommitted. Group
working edits are also excluded; committed group policy is the source reference.

Installed engine: 42.22.2 revision3d39148846, JAR SHA256
3c4a7c5f149d784758c6fb5f8fa85f3a21d572e38bc081400e89035f8120d287.
Read-only CFR sources under ignored .venv/combat01-decompiled plus previously
extracted classes. Existing IsoPlayer/IsoGameCharacter/SwipeStatePlayer/AIComponent
class bytes were checked against this installed JAR, not assumed current.
No Java modification, native game experiment or source merge.

## Findings that determine the next step

1. **The perception-list indexing is correct.** Native IsoCell.getLuaObjectList
   creates a Kahlua table, enumerates objectList from numeric key1, returns it.
   VirtualZombieManager adds both newly created and reused zombies to that moving
   object set. Thus ordinary loaded zombies can be present; ipairs plus stored
   numeric key is correct. This does not prove a particular live zombie was in
   that snapshot. The native moving collection itself is a **Set**, not an
   ArrayList. Do not replace this with zero-based Lua table traversal.
2. **Two equip branches are unreachable.** AI-Manager.lua:275 and:653 require
   hasWeapon() AND getPrimaryHandItem()==nil. hasWeapon(:1522) only returns a held
   HandWeapon or false. Those predicates cannot be true in ordinary synchronous
   execution. Carrying a weapon in inventory does not meet hasWeapon. An unarmed
   non-companion then hits the later fleeing rule even with one nearby zombie.
   This is a concrete stage(b) candidate, not proof that the reported NPC was unarmed.
   A separate looting branch around1065 can still queue EquipWeaponTask; not all
   weapon acquisition is disabled. EquipWeaponTask searches getBag():getBestWeapon,
   so blindly inverting the predicate would also risk repeatedly trying an empty
   bag or missing a weapon elsewhere in inventory. No change made.
3. **PursueTask rejects ordinary zombie targets.** Constructor:23 reads target
   ModData.ID, asks SSM:Get(ID), returns nil without a wrapper. Zombies normally
   lack an SSR survivor wrapper. Both active role paths can request zombie pursuit,
   but AddToTop(nil) silently ignores it. This can explain failure to close distance,
   especially across rooms; same-room AttackTask has its own movement and can still
   work. Candidate stage(b), not a universal perception failure.
4. **B42 NPC controls differ from ordinary player setters.** setNpc(true) installs
   AIComponent. IsoGameCharacter.isAiming() reads humanControlVars.aiming for NPCs;
   setIsAiming only writes the ordinary isAiming field. AIComponent.postUpdatePlayer
   writes initiateAttack/running/justMoved from its control vars. The control object
   initializes to false/zero, and SSR has no code writing these control vars.
   A pressedAttack request can set initiateAttack/attackStarted immediately, yet
   later NPC post-update rewrites initiateAttack. Exact ordering relative to
   action/animation consumption requires observation; do not assert every attack
   is erased before animation. These are concrete stage(d/e) integration risks.
5. **The normal melee collision callback excludes standalone NPCs.** Installed
   SwipeStatePlayer.OnAnimEvent_AttackCollisionCheck calls CombatManager's native
   collision routine only when !ATTACKED and IsoPlayer.isLocalPlayer(owner).
   That static helper delegates to instance.isLocalPlayer: membership in actual
   local player slots, not isNpc/playerNum/viewport index. A standalone SSR actor
   outside those slots fails this gate even if a swing animation starts. This is
   a demonstrated limitation of that specific stage(e) route, not evidence that
   the observed NPC reached it, nor proof every possible native route is absent.
   Do not make NPCs local players, change human slots, fake Hit damage or modify Java.
6. Other proven secondary issues: needToFollow checks `not Task.isComplete` rather
   than invoking it; normal FollowTask has a method there, so the inner branch is
   skipped. This weakens following interruption, rather than explaining all missing
   combat. Two unused AiNpc_IsTarget_* helper names are reversed, but their caller
   AiNPC_CanAttack is itself unused. AIManager_Companion is an unused duplicate;
   edits there would not fix the active manager. NPCTask_DoAttack has no active call
   sites beyond its definition/comments. The active AttackTask additions are in
   AI-Manager.lua:242 and:399; AttackTask creation is not globally disabled.

## Actual execution chain and cancellation

| Stage | Current behavior / useful source anchors |
| --- | --- |
| Scheduler | SuperSurvivorsMod.lua:73-81 OnRenderTick when speed!=0 -> SSM:update; manager:180 skips MainPlayer, optional UpdateFilter, asleep/not-in-cell/dead cases, updateTime gate. updateTime:2725 increments Reducer, runs modulo UpdateDelayTicks and consumes WaitTicks only there. Cadence follows render callbacks, not a fixed simulation frequency. |
| Refresh | SuperSurvivor:update:2963 runs DoVision first, then stuck/movement/stats logic; :3051 calls task manager unless human asleep or GroupRole exactly Random Solo. AIMode=Random Solo at spawn is a different key; do not infer all fresh NPCs skip manager. DoVision changes delay to10 only with danger and current Attack, otherwise20. |
| Perception | DoVision:1654 resets counters/target every scan; considers living IsoZombie/IsoPlayer, excludes self, <=19 distance and isEnemy. Group and ungrouped enemy policies both accept zombies first. Danger count uses same-Z distance <max(6,AttackRange), even without LOS. seenCount requires RealCanSee. Nearest target needs CanSee OR distance<0.5. Thus danger>0 does not guarantee LastEnemeySeen exists. Native CanSee does LOS lineClear; native god mode bypasses it through SSR RealCanSee and also writes alpha. |
| Decisions | TaskManager:update:115 invokes active AIManager before executing Tasks[0], unless AIEnabled==false. Manager early returns if needToFollow or NPC in vehicle. Companion and non-companion paths separately require no Attack/Threaten/First Aide/Flee, same room, danger>0, not too scared; companion also checks enemy distance from follow target <GFollowDistance+AttackRange. No blanket equipped-weapon condition on these active attack additions. Robbers may Threaten human enemies instead. |
| Priority | Later rules in the SAME AI pass can push Flee/First Aide or clear the queue after Attack was just added. Injuries, no equipped weapon (non-companion), too many close enemies, bravery, gun preparation and other role/needs rules matter. AddToTop shifts existing tasks down, no automatic cleanup on preemption; clear cancels all. The last matching rule wins the front of the queue. |
| Task validation | TaskManager first checks isValid, removes/cancels invalid tasks; then isComplete/moveDown or update-limit cancellation; otherwise update. AttackTask:isValid requires target alive and same room. Two outdoor nil rooms compare equal; outside vs inside or different indoor rooms do not. It is false that all outdoor attacks are invalid. |
| Completion | AttackTask:isComplete requires !needToFollow, danger>0 OR enemyInRange+hasWeapon, living target and no unbandaged injury. Any unbandaged injury can terminate even if fear check allowed selection. Constructor never sets Target; its initial getDistanceBetween(self.Target,...) returns -1 through the mod helper, not an exception. On completion that -1 satisfies <1 and calls StopWalk. This is a separate cleanup error, not proof initial attacks never run. |
| Movement/readiness | AttackTask:update repeats validation/completion, moves toward target when permitted; guns ready/reload first; NPC_ShouldRunOrWalk then currently sets running false while Attack is active. Merely seeing setRunning(true) in movement does not prove busy rejection. Attack range or distance<0.65 gates the task call, but requestCombatAttack checks strict native range again. The <0.65 fallback does not bypass min range. Cooldown counts only through relevant update paths; it is not a wall-clock duration. |
| Request | SuperSurvivor:4231 requestCombatAttack rejects target/cooldown/busy/range/weapon. busy includes SwipeState, felldown, native attackStarted and running. WeaponReady is a mutator for firearms: repairs/unjams, ammo bookkeeping/creation/box opening/readiness actions. StopWalk clears actions/path/aim/initiate before face/target/aim/pressedAttack. NPC_Attack and Attack route here; Attack may ammo-search/melee-fallback on weapon reason. AttackTask ignores its return/rejection reason. |
| Native start | IsoPlayer.pressedAttack -> CombatManager.pressedAttack. It can reject attack-started/hit reaction/fishing, inability to perform hand-to-hand after a drop attempt, or !doShove&&!native isWeaponReady. Native readiness checks hand-model presence/readiness/action override/ranged muzzle attachment, not SSR WeaponReady or merely holding a weapon. It sets initiateAttack/attackStarted, calculates native attack vars; unauthorized shove/grapple can reset both flags. Immediate true is not an animation/hit guarantee. |
| Native consumption | IsoPlayer NPC post-update writes AI controls. SwipeStatePlayer.enter clears initiateAttack, calculates native vars, enters swing and emits OnWeaponSwing. Normal AttackCollisionCheck animation callback has local-player gate above. Native CombatManager.attackCollisionCheck emits OnWeaponSwingHitPoint and owns ammo/damage/targets; no manual damage may be added alongside it. |
| Per-player path | SuperSurvivorGlobalUpdate -> PlayerUpdate via existing SSR ID wrapper; nonlocal actors may request automatic repeats via TriggerHeldDown, then WalkToUpdate. Successful/failed path completion can call StopWalk, which also clears initiate/target/aim/trigger. Another cancellation risk, timing-dependent. |

## What we can and cannot conclude now

Earliest demonstrated decision defects are equip scheduling and zombie Pursue
construction. With an equipped healthy NPC and nearby same-room visible zombie,
those defects alone do not explain failure: valid active attack branches remain.
Native target lists are calculated by CombatManager from weapon/range/Z/LOS/
standing/prone context; facing a supplied victim and setting its target square
does not promise that exact victim will receive a hit. Native IsAttackRange uses
strict min<distance<max and rejects Z difference>0.3; task distance<0.65 fallback
does not override it. Native model/readiness, AI-control overwrites and collision authority must be
separated from policy/queue decisions. A snapshot of isAttackStarted=true can
also mean stale/stuck state, not a new successful swing.

Current console has Test04 human records but no per-NPC perception/selection/
request-return timeline identifying the observed failure. No controlled combat
run occurred. Existing mocked pressedAttack tests only prove delegation/cooldown,
not engine acceptance, NPC action-state transitions or damage. Do not claim (a),
(b), (c), (d) or (e) as the actual user incident yet.

## Proposed next bounded diagnostic (not implemented)

Start with one user-invoked **Combat - inspect existing survivor** in gated SS Tests.
User selects explicit loaded SSR ID>0; validate wrapper identity, actor alive in
current world, not human/local slot, ordinary AI enabled, and a loaded square.
User should choose a healthy equipped survivor near one ordinary zombie in an
open area, stay nearby, report expected attack and whether threat/swing is visible.
A disposable world is advisable for any combat setup. The snapshot itself creates
nothing, does not select/provoke enemies, move/control actors or alter AI/gear.
No native-debug prerequisite for public fields; unavailable values explicitly named.

Log time/frame/speed and version; SSR ID/actor/ownership, role vs AIMode, group,
AIEnabled/UpdateFilter/MainPlayer, delay/reducer/wait/asleep/square; bounded queue
front+names/count/update-limit; LastEnemeySeen type/alive/coordinates/square/room,
seen/danger/EnemiesOnMe/bravery/injury context; primary weapon type/condition/
firearm/ammo state; distance and public native IsAttackRange; running/NPC/local/
blockMovement, actual isAiming, initiateAttack/attackStarted, performing attack/
shove/ground/authorization/hand-to-hand/native weapon-readiness/state flags.
Separate cached policy inputs from derived predicted predicates and unavailable
native fields. Log room identity comparisons within this observation only.

Do not call DoVision, AIManager, TaskManager:update, task:isComplete/update,
NPC_CheckPursueScore, RealCanSee (god-mode branch writes alpha), WeaponReady,
ReadyGun, updateTime or pressedAttack to obtain a diagnostic answer. Some change
counters/queues/movement/ammo/visuals. Do not call getLuaObjectList just to observe:
its implementation also replaces global Objects. If candidate context is needed,
use reviewed pure getZombieList ArrayList size/get bounded sampling plus native
CanSee LOS and Z/distance, never treating an incomplete sample as no enemies.
Moving getObjectList is a Java Set; do not assume get(i) exists. Verify every
chosen public getter's Lua exposure/safety before implementing.

One snapshot cannot prove whether a request happened earlier or was transiently
cancelled. If needed, a separately reviewed opt-in **observe for a bounded window**
may log up to a small cap of snapshots/events, explicit start/cancel/timeout and
same actor/world ownership. To classify request rejection vs post-request reset,
a scoped wrapper around ONLY that NPC's existing requestCombatAttack could log
entry, existing function's exact return values and before/after flags, preserving
behavior/errors and calling original exactly once; never invoke an extra attack.
Restore only if wrapper is still ours, on cancel/timeout/world/menu/change. This
instrumentation design needs review; not installed by this audit. Correlate normal
OnWeaponSwing/OnWeaponSwingHitPoint/OnWeaponHitCharacter/OnHitZombie (verify actual
argument contracts/exposure at implementation), filtering owned attacker identity.
Absence of HitPoint for a nonlocal NPC is consistent with native callback gate;
no forced hit. Record timing of captures relative to native update, not just UI click.

Interpretation: no candidate/target -> (a) with LOS/membership caveats; target and
policy rejection -> (b); actual queue preempt/cancel -> (c); observed request with
false/reason and native readiness/state -> (d); accepted request then no initiation/
state/event/hit -> (e), distinguish animation from native collision/hit separately.
Missing data -> INCONCLUSIVE, no automatic root-cause or PASS.

Only after evidence/review consider a second, explicitly destructive fixture:
fresh user consent for each run; one tracked NPC+zombie, healthy/dry/open same-Z,
known equipped melee weapon, baseline actors and clear ownership, safety distance,
no human teleport/control/god-mode toggles. Never clean arbitrary actors or save
files. Prefer manual existing pair first. No fixture code is authorized now.

## Separately reviewable changes and regression proposals

- Equip: distinguish equipped weapon from accessible inventory candidate, queue
  Equip only when empty/unusable hand AND candidate exists AND no equip/task/action
  conflict. Cover empty hand+weapon in bag, empty inventory, held nonweapon,
  held valid weapon, active action and danger priority. Review barehanded flee
  policy separately; do not silently change bravery/shove behavior.
- Pursue: allow zombie target with valid square without requiring SSR wrapper;
  retain optional wrapper logic for human buildings/roles. Cover living/dead/
  absent-square zombies, human wrappers, disappearing targets and room transitions.
- Follow predicate and AttackTask missing Target cleanup each warrant separate
  narrow reviews/tests. They do not solve native attack acceptance/collision gates.
- Native attack adapter: first prove public Lua-accessible B42 control/animation/
  collision routes and ownership; Java modifications are excluded. Do not guess
  that setIsAiming controls NPC AI, or equate immediate pressedAttack flags with
  native hit. No local-slot swap and no direct victim:Hit workaround. Public
  CombatManager collision method exists, but its complete Lua exposure/ordering/
  safe invocation is NOT established here; not a proposed automatic call.

## Validation / delivery limits

Source-only Lupa witnesses against the isolated intended source tree passed:
impossible equip condition for empty/HandWeapon/nonweapon hand, outdoor nil-room
true and outside-to-room false, ordinary-zombie Pursue constructor returns nil,
FollowTask method-truthiness guard skips its needed follow evaluation. These
reproduce source behavior, not engine combat. No tests were added to pin defects
as desired behavior. Existing 230 tests/113 Lua syntax passed at preceding R1
source commit; this investigation changes documentation/coordination only.
No native combat experiment, diagnostic implementation or gameplay fix performed.

Next bounded action: review findings and authorize the single existing-NPC
read-only snapshot, then bounded request/event observation only if needed. Review
proven Lua defects separately. Test04 R1 is delivered and awaits its own native
capture/save/restart check; Test03 early observer remains deferred.
