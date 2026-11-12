# Core survivor behaviour review — 12 November 2026

Static review of the eight requested task files, their AI/context-menu callers,
TaskManager, and the movement/container helpers they use. No gameplay code was
changed. These findings describe source behavior; they do not establish which
branch a particular survivor took during live testing.

## Execution model

TaskManager runs AI decisions before updating the current task. AddToTop pushes
the old task down rather than cancelling it, so a temporary task can interrupt
and later resume another one. clear/removal invokes a cleanup hook when the task
provides one. The OnGoing fields in these task files are not used by TaskManager
to determine lifetime. Completion methods, validity, interruptions and the shared
task-update limit determine lifetime instead.

Counters here count task updates, not seconds. Survivor update frequency and
WaitTicks affect their elapsed duration. StopWalk is broader than its name: it
clears timed actions, path, running, sneaking and aiming/attack state.

## Expected behavior and implementation

| Task | Behavior implemented | Completion |
|---|---|---|
| Flee | Run away from LastEnemeySeen, disable sneaking, repeatedly request a retreat square. Mark the previous target building explored to discourage immediately returning. | Danger count reaches zero or needToFollow returns true; missing enemy also invalidates it. |
| FleeAwayFromHereTask.lua | Defines FleeFromHereTask, displayed as Flee From Spot. Run away from the supplied location, even if no current enemy is visible. Used for panic, threats, dismissal and witnessed violence. Slow to walking within one tile of the human player. | Distance from the supplied location exceeds Option_Panic_Distance (default 21). |
| Listen | Stop existing actions, acknowledge the speaker, approach within 1.8 distance, face them, give an initial/custom greeting, then potentially chatter. Context-menu conversation calls Talked to reset its timer. | More than 15 exchange ticks, danger, or needToFollow. Non-group partners get a goodbye. |
| Attack | Engage the current LastEnemeySeen rather than a fixed constructor target. Delegate melee/gun positioning, gun readiness and attacks to survivor helpers; apply attack cooldowns. | Enemy absent/dead/in another room, injury, needToFollow, or no remaining qualifying danger/in-range armed target. |
| EquipWeapon | Wait for no movement/action, choose getBag():getBestWeapon(), accept damage above 0.1, announce it, directly set the primary-hand item. | One attempt, including when no usable weapon is found. |
| Hold Still | Cancel existing actions and disable walking. Used by the player and by a doctor treating another survivor. | Explicit setComplete, danger, or a player-initiated order after the human leaves the original square. No timeout. |
| Wander | When idle, request a random same-floor destination offset by -10 through 9 on each axis from the current position. | Never completes itself; can be interrupted, removed or limited by the manager. |
| Wander In Area | When idle, a 1-in-4 chance per update to request a random destination in a supplied rectangular area and floor. Guard work and preset spawns use it. | Continues until interrupted/removed/limited, or invalid parent/area. |

Neither wandering task checks safety, clear floor or reachability before choosing
a square; the shared movement/pathfinding code handles the actual attempt. An
area constrains destination selection, not necessarily every step of the route.
Wander has no permanent center, so repeated choices can drift a long way.

The flee helper uses the sign of each coordinate difference, applies seven tiles
on both axes and adds random offsets of -5 through 4. This is coarse diagonal
retreat, not a normalized vector, scored escape route or search for safety. A
missing destination is ignored by walkTo; there is no task-level retry limit or
alternative-route strategy. Flee requests a new destination every update, even
while moving, which can contribute to repeated replanning.

## Confirmed defects

1. **Broken follow-priority helper.** SuperSurvivor:needToFollow tests
   `not Task.isComplete`. Normal FollowTask instances inherit that method, so it
   is a truthy function and the condition is false. The wrapper never reaches
   FollowTask:needToFollow for a normal task. Flee, Listen and Attack therefore
   do not yield through their intended follow-priority condition. This does not
   mean the FollowTask itself cannot move a follower.
2. **Unreachable automatic Equip Weapon condition.** hasWeapon means a
   HandWeapon is already in the primary hand. Both AI managers also require the
   primary hand to be nil before adding EquipWeaponTask. Those conditions cannot
   both hold, so those automatic branches cannot schedule the task.
3. **Wrong actor in a threat-triggered retreat.** ThreatenTask clears the
   threatened survivor's queue, then inserts FleeFromHereTask whose parent is
   the threatening survivor and whose retreat origin is the victim's square.
   The victim's queue therefore executes movement for the threatener.
4. **Attack completion uses an unset target.** AttackTask:isComplete measures
   self.Target, which this task never assigns. getDistanceBetween returns -1
   for nil, so the later `distance < 1` condition always succeeds on completion.
   StopWalk consequently clears actions/path even when the enemy was far away.
5. **Hold Still has no cancellation cleanup.** Walking is restored only when
   isComplete observes completion/danger. Clearing/removing/expiring the task
   can bypass that path and leave walking disabled. A buried Hold Still can
   also keep walking disabled while another task is at the top.

## Other limitations and review targets

- Equip Weapon searches only the container selected by getBag: back bag, then
  secondary-hand bag, then primary-hand bag, then main inventory. An empty worn
  bag can therefore hide a weapon in main inventory from this task. Equipping
  directly sets a hand reference: no timed equip, transfer out of a bag,
  two-handed coordination or interruption handling is implemented here.
  The zero-argument getBestWeapon overload still exists in the installed JAR;
  this particular call is not an obsolete API name.
- Flee sets running during construction and restores it on normal completion,
  but has no cancellation/invalid-target cleanup. Creating queued tasks already
  mutates the actor before the task becomes active. Both flee constructors also
  mark target buildings explored as a side effect.
- Listen validates only object references, not the partner's life/load state or
  current square. Its timeout advances while approaching, so it may expire
  before reaching a difficult-to-access partner. NPC idle chatter does not reset
  TicksSinceLastExchange in this task.
- Attack's same-room comparison treats two outdoor squares as the same room
  because both have nil room references. It is not an outdoor visibility or
  reachability check. Other perception/range/movement helpers must supply those
  decisions. Injury ends this task irrespective of injury severity.
- Doctor completion releases Hold Still only when it is the patient's current
  top task. Interruption or loss of the doctor can leave a patient waiting;
  there is no hold timeout/ownership contract to recover independently.
- Flee From Spot assumes a valid origin, Wander In Area assumes well-formed
  bounds, and player-initiated Hold Still assumes a local player. These are
  weaker lifetime/argument checks than a robust task interface should have.
- Multiple AI conditions can push tasks in one decision pass. The last push
  becomes current; construction side effects occur even for tasks pushed below
  another task immediately. Rapid task changes are not necessarily errors, but
  repeated attack/flee/equip transitions deserve inspection at the decision level.

Recommended fix order: actor ownership in ThreatenTask; automatic equip
conditions and complete weapon selection; cancellation-safe Hold Still;
needToFollow; Attack target cleanup; then flee route selection/replanning and
conversation/idle behavior. The first five are concrete logic/lifecycle repairs,
separate from B42 API migration and later behavior redesign.
