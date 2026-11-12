# Survivor behavior and SS Debug design

Consolidated 12 November 2026 from the port/design discussion. This document
records what we want to build, not capabilities already implemented or verified
in B42. The user explicitly said **we are in design; no implementation now**.
The present request authorizes documentation only. Java-side changes are excluded.

## Direction and scope

Port useful working actions while gradually replacing the decision layer. Avoid
both preserving every contradictory legacy rule and rewriting all gameplay at
once. Aim for understandable survival behavior, not an elaborate tactical
simulation. Numerical costs, thresholds and scoring below are proposals to test,
not settled balancing rules.

Separate three responsibilities:

| Layer | Example | Responsibility |
|---|---|---|
| Persistent goal | Prepare a farming plot | Remember the assignment and completed work. |
| Behavior/response | Handle a nearby threat | Choose a coordinated plan for the circumstances. |
| Task/action | Equip, move, attack, till | Execute a specific operation and report its outcome. |

Prioritize goals/responses rather than letting independent movement, equipping
and attack tasks compete without a shared plan. Perception supplies observations;
decision logic selects a response; movement/combat controllers carry it out.

## Existing implementation and findings

See [CORE_BEHAVIOUR_REVIEW_2026-11-12.md](CORE_BEHAVIOUR_REVIEW_2026-11-12.md)
for Flee, Flee From Spot, Listen, Attack, Equip Weapon, Hold Still, Wander and
Wander In Area, their callers and confirmed defects. That review is a static
analysis, not a set of repairs already applied.

The current flow is perception, AIManager decisions, then TaskManager validation,
completion/limit checks and current-task update. AIManager is a sequence of
conditional rules, and several can fire in one pass. The main AI-Manager.lua
also handles companions; AIManager_Companion in the separate companion file has
no callers in the reviewed code.

AddToTop interrupts by pushing existing tasks down, without suspension cleanup;
AddToBottom appends. Only the current task updates. Normal completion calls
OnComplete. Invalidity, expiry, clear and explicit removal use the first available
OnCancel/ForceComplete/ForceFinish/OnComplete hook. Returning false from update
does not itself remove a task. The shared update limit is not a per-goal deadline.
There is also a separate native timed-action queue, whose work can outlive task
removal unless cleanup stops it. StopWalk clears those actions as well as movement.

Both AI and tasks currently react to danger, with inconsistent consequences:
replace the queue, interrupt, complete normally, or merely stop making progress.
The redesign should make those policies explicit. Pause/resume must not depend
on constructors changing actor state before the task becomes current.

Known repairs to plan include the impossible automatic equip condition, broken
needToFollow method check, wrong actor in a threat-induced flee task, missing
Hold Still cancellation cleanup and unset Attack completion target. Preserve
those findings separately from later tactical improvements.

## Goals and interruptions

Retain assigned goals and completed progress independently of immediate actions.
For example, interrupt tilling to handle a threat, then reassess the plot, tools
and remaining tiles before resuming. Do not resume stale paths or timed actions.

Use broad priorities for immediate survival, threat response, essential needs,
assigned work and idle activity. Choose responses within those bands using
context. Commit to a reasonable response until conditions materially change;
require a period of safety before resuming work to prevent rapid switching.

Actions need running/succeeded/failed/cancelled outcomes, explicit interruption
rules and reliable cleanup. Native timed actions and the mod task queue need
coordinated ownership. Existing working actions can be migrated incrementally;
retire corresponding legacy AI rules as replacements become usable.

Reference example: six tiles of a twenty-tile plot have been tilled. A zombie
interrupts the assignment. Assess it, ready a weapon or choose retreat/regrouping,
deal with the immediate threat, wait for reasonable safety, then check the tool,
plot and remaining work before continuing. Work completed during the interruption
by another survivor must not be repeated. Abandon or replan if the goal is no
longer possible.

Possible threat responses include engagement, retreat to safety, regrouping with
companions and eventually calling support over a walkie-talkie. Radio support
requires a working recipient/response and communication rules; it is a later
extension, not a promise of existing radio AI.

## Mobility

Control facing independently from travel direction. Support engine-permitted
combinations of walking, running, sneaking, turning, aiming, sidestepping and
backstepping. Prove aimed backward walking and melee attacks while retreating
on NPCs before claiming support. Do not assume backward running is supported.

Keep pathfinding for travel and obstacle navigation. Use a local controller for
close combat: compare staying and short movements in several directions using
threat proximity, useful weapon distance, clear routes, safe ground, allies,
escape space and continuity of movement. Consider surrounding threats, not only
the current target. Zombies on the right can favor a clear sidestep left while
facing the target. Check the traversed segment as well as the destination.

Distinguish maintaining weapon distance, closing to engage, and fully
disengaging. A survivor may stop attacking briefly to reposition, or lower their
weapon, turn and run when backstepping is no longer sufficient. Movement should
respect obstacles, collision, animation restrictions and engine attack timing.
Do not teleport actors or apply duplicate/manual hits to simulate success.

Current code barriers: requestCombatAttack calls StopWalk before every attack,
and enables aiming only when using a gun. Thus the existing interface actively
prevents the intended continuous aimed melee retreat. Public movement/facing
methods in the JAR are candidates, not proof of a working Lua NPC controller;
native NPC controls differ from the human input path.

## Weapon, skill and physical state

Evaluate weapon suitability from actual properties and engine behavior rather
than a universal long/short ranking. Inputs may include effective reach,
attack/recovery time, condition, endurance cost and noise. Validate the usable
data and its semantics against the installed game before implementation.

Long reach can favor spacing but slow recovery can leave an opening. Short reach
requires closer contact; fast attacks can still be useful in confined space or
an emergency. Weapon skill, movement skill, injury, fatigue and current endurance
adjust the survivor's confidence and spacing. Higher skill must not override
unsafe geometry or exhaustion. Preserve an endurance reserve for disengagement.

Use ordinary engine attacks, shoves and stomps. Shove when it creates useful
space and is safe; stomp a downed enemy only when nearby standing threats permit
the commitment. Reassess after actions; do not invent guaranteed hits, special
piercing bonuses or animation capabilities that have not been verified.

## Sound and uncertainty

The current ListenTask handles conversations, not environmental hearing.
Separate hearing/perception from both conversation and response decisions.

Where available through verified Lua APIs, retain recent sound location, age,
category and confidence, rather than granting exact knowledge of unseen actors.
Gunfire, alarms and suspicious sounds can change route/building decisions and
whether to fight, investigate, wait or withdraw. A sound alone is not proof of
a particular enemy count or an exact position.

Treat firing as having an immediate combat benefit and a possible later cost:
attracting threats the survivor has not seen. Loud options remain appropriate
for emergencies. An alarm can make continuing to loot an unacceptable risk even
when no zombie is currently visible. Never derive perception from unrestricted
world knowledge just because an API permits enumeration.

## Attention, recovery and personal needs

Explore a small attention budget (roughly 2–4 slots as a design model), modified
by traits, skill, panic, pain and exhaustion. Allocate attention to target
tracking, spacing and surrounding/retreat-route checks. Occasional glances can
temporarily divert attention and refresh information that otherwise becomes
stale. Do not prevent basic hit/collision reactions when the budget is exhausted;
reduce awareness or simplify the chosen behavior instead. This is unimplemented.

User example: a less capable survivor might have two slots and a more capable
one four; panic could reduce capacity by one. Backstepping and attacking might
consume the remaining attention, leaving no capacity for a deliberate look
behind. Exact costs/grouping remain open: target tracking and attack timing may
be one focus, maintaining spacing another, and surrounding/route checks another.
Do not make movement and attacking mutually exclusive just because both cost
attention. Skills may reduce familiar activities' costs or improve switching.
When overloaded, prefer simpler behavior or temporarily stop attacking to scan;
do not produce arbitrary paralysis. Recently observed ground remains useful
knowledge, but confidence should decay with time.

Resting should be a resumable recovery goal: choose a recently checked position,
sit/rest using supported native actions, recover endurance, then stand and
reassess before returning to work. Danger interrupts recovery. Account for the
time/vulnerability of getting up; do not sit merely because current danger is
zero. Stamina/endurance recovery and sleep/fatigue management are separate needs.

The current survivors are IsoPlayers with native moodles/stat containers, but
SuperSurvivor:update repeatedly clears fatigue, stress, unhappiness, food sickness
and poison, fixes weight, clears colds and conditionally clears boredom and
hunger/thirst. Consequently player-like self-care cannot be enabled just by
reading moodles. Audit the native NPC stat-update paths and these overrides
before restoring a need. Introduce each need together with a viable response.

There is no general sit-to-recover or self-medication task in the current mod.
ChopWoodTask instead adds endurance directly below 0.5. Existing dialogue code
reads moodles, which does not establish full native parity with human players.

Future self-care may use appropriate food/drink, rest, medicine or smoking for
relevant traits, through verified native actions and actual supplies. Choose
responses based on the cause and condition rather than treating all moodles as
a request for pills. Track pending doses/effects to avoid repeat consumption
every decision update. Smoking is separate from ordinary food consumption.
Do not remove legacy stat protections en masse before supported responses exist.

## Buildings: modest scope

Track unobserved, observed and recently checked locations; do not label a house
permanently safe. Use sight through windows/doors when actual visibility allows,
and react to sounds. Favor alternate entrances, another building or withdrawal
when visible danger exceeds the survivor's capacity. Avoid repeatedly selecting
the same rejected building without changed circumstances.

For an initial building behavior: inspect an accessible entrance, enter
cautiously, check the next room before committing and keep a viable exit. Loot
only while the current risk is acceptable. Unknown rooms remain uncertain, and
previously checked rooms can become unsafe. Detailed police-style team clearing,
formation tactics and comprehensive sound inference are out of initial scope.

## SS Debug and cheats without the game debug flag

User requirement: useful mod diagnostics and cheats should be included in the
normal mod and accessible without launching PZ with -debug wherever Lua permits.
Propose **Enable SS Debug**, off by default, in mod options. Reuse the existing
saved DebugOptions setting rather than create competing switches; its present
label is Debug Options. This change has NOT been implemented.

Proposed access points:

- An SS Debug button/menu in the main survivor window.
- Per-survivor context-menu entries to monitor AI/state, inspect its task queue
  and show its position/direction. Support observed survivors, not only party
  members, where the game currently has a valid loaded actor.
- Main-window access to choose a loaded survivor and stop monitoring, so a Lua
  console is not required. Keep monitor status and navigation available together.
- Clear separation of read-only observation from state-changing cheats such as
  spawning, healing and pausing AI. Toggling SS Debug itself should not silently
  apply cheats or change survivor behavior.

Disabling the setting should hide its controls and stop active monitoring.
Explain current task, queued work and selected behavior/reason where available.
Do not invent behavior reasons for the legacy AI: expose actual recorded
decisions, and mark unavailable details honestly. Existing debug speech can
remain a separately configurable, potentially noisy diagnostic.

The current build already has DebugOptions-gated legacy context cheats. These
are not all audited by this proposal. In particular, existing character-swap
and kill entries do not establish that those operations are suitable for the
new menu. Inventory what exists and validate each retained action. No new
god/invisibility behavior should be silently applied; the user uses Z'Ware
Invincibility: Three Ways Out, which is not vanilla PZ god mode.

Tools that require actual native debug mode must say so rather than pretending
the setting enables -debug. Keep the first supported scope single-player;
multiplayer availability/authority is a separate decision, not something a
client-side option grants.

Normal-release packaging should retain the SS Debug UI and supported tools.
Disposable development scenarios/maps remain separate and can still be excluded
from release output. Currently all client/Debug code is excluded, including
the watcher; relocation/dependency cleanup is therefore required before claiming
the watcher ships in releases. Merely changing its getDebug gate is insufficient.

## Current observation tools and boundaries

SuperbSurvivorsWatch currently provides state/task monitoring and navigation:
coordinates, horizontal distance, compass/screen direction and floor difference.
It still lives in Debug/SuperbSurvivorsDebug.lua, requires -debug and supports
single-player with one viewport. Targets must be living and loaded; monitoring
stops on target death/unload or world changes. The user confirmed the explicit-ID
start works after a console entry error. This does not validate the future UI.

Camera following remains unfinished after two live failures. Native frame setup
restores the real player, and OnRenderTick runs after world drawing. No working
camera-only Lua route has been established. See
[SURVIVOR_WATCH_CAMERA_REVIEW_2026-11-12.md](SURVIVOR_WATCH_CAMERA_REVIEW_2026-11-12.md).
Do not promise camera following, swap local-player slots, possess the NPC, or
modify Java to achieve it. The accepted player/NPC visibility issue is a separate
deferred investigation, not a prerequisite for these design discussions.

## Staged implementation

1. Establish action lifecycle and interruption cleanup.
2. Prove independent facing/movement and attack-while-retreating in a controlled
   debug scenario, using collision and native combat resolution.
3. Add short safe movement selection and surrounding-threat assessment.
4. Add weapon/skill/endurance-aware engagement and disengagement, including
   shove/stomp decisions supported by the engine.
5. Prove a work goal can survive a threat interruption and resume correctly.
6. Add basic sound events and cautious building entry after confirming their
   Lua access and visibility semantics. Leave unsupported senses explicitly
   unavailable rather than approximating them with omniscience.

The SS Debug UI is an enabling workstream for these milestones: expose reliable
existing observations first, then add decision explanations as the new decision
layer records them. Attention budgets, richer needs and radio support come after
the basic movement/response/resumption loop works. This order is a proposal;
no implementation milestone has been authorized by this documentation request.

## Observable acceptance examples

- A survivor backsteps and attacks while facing one target, with native collision
  and hit resolution and no compulsory stop before each swing.
- Additional threats on the right favor a clear move left without dropping
  target-facing; a blocked left route is rejected rather than walked through.
- Exhaustion or an unsafe escape route changes willingness to continue fighting;
  weapon skill never guarantees success or grants knowledge of unseen enemies.
- A sound/alarm can cause withdrawal despite no visible enemy; silence does not
  mark an unexplored room safe.
- A work goal survives interruption and resumes only valid unfinished work.
- Recovery uses actual sitting/resting behavior, can be interrupted, and cannot
  leave the survivor permanently unable to move after cancellation.
- An enabled need has a supported response; medication/smoking consumes suitable
  supplies once, accounts for effects already pending and is interruptible.
- Without -debug, enabling SS Debug reveals supported observation/cheat controls;
  disabling it removes them and stops monitoring. Packaged releases include those
  controls while excluding disposable test scenarios.

Keep the first rules few and inspectable. Debug monitoring should explain the
selected response and its dominant reason, without presenting implementation
details as normal gameplay UI.
