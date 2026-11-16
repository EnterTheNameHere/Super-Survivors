# Survivor world observation, knowledge and simulation — design direction

Recorded: 2026-11-16
Status: Direction and considerations, NOT a frozen specification or implementation assignment.
Project: Super Survivors Reloaded (SSR), Project Zomboid B42.
Scope: SSR itself. No external-platform linkage, dependency, or migration is implied.

## Motivation and boundaries

We want useful, clever survivors with ongoing identity, needs, goals, memory, relationships and decisions in a world that can change independently of them. Reusable/general approaches are worthwhile where they actually simplify multiple SSR problems; avoid generalized machinery for its own sake.

This document retains possibilities from discussion rather than declaring them approved features. **Immediate B42 correctness issue:** replace hard-coded assumptions that floors are only Z=0..2 or Z=0 in building, loot and zombie queries. B42 supports much larger vertical extents including basements. Investigate actual installed engine's building/room/floor APIs and world loading constraints before changing algorithms.

A building is identified by actual game spatial/building information, not by its furniture. Furniture and containers can be moved by players or survivors and do not logically establish whether something is a house, room or building. Building footprint, usable square meters (potentially sum across floors), floors/basements, entrances, exits, internal connectivity, obstacles, escape opportunities, and known threats may influence survivor risk decisions: e.g., whether an unarmed survivor should enter and could get out safely. Separate total geometry from what the survivor can actually perceive or know.

## Distinguish reality, observation, and knowledge

1. **World truth:** the actual PZ world, loaded objects and persistent map/state.
2. **World observation/access:** SSR's way of requesting engine information, searching squares, rooms, containers, items and characters, optionally caching access/results. A shared technical cache does not give survivors automatic knowledge.
3. **Survivor knowledge:** beliefs and memories acquired through sight, exploration, inspecting containers, conversation, radio or inference. Each survivor knows only what their experience and communication justify.

Observations have subject/location, content, observer, source/provenance, time and possibly uncertainty/confidence. Historical knowledge is not guaranteed current: a survivor can remember steel plates in a container seen 30 days ago without knowing that the plates remain. A survivor may discover a building from outside without knowing its internal structure, enter and discover rooms or visible items, then separately inspect a container to discover its contents. Do not conflate building discovered, entered, explored, container noticed, container inspected, or contents currently available.

Even if SSR has cached container contents or geometry from another actor, that does not entitle an unobserving survivor to use them. No omniscience by sharing implementation data.

## Unified observation/search direction (not yet architecture)

Today multiple Lua tasks independently enumerate getCell():getGridSquare, rooms, building bounds, square:getObjects, square:getWorldObjects, square:getMovingObjects and ItemContainer:getItems. A unified observation/search facility may reduce duplication, make loaded vs unknown distinctions explicit, centralize Z-correctness, and allow profiling and selective caching later.

Treat cache maintenance and performance as empirical questions, not automatic justifications for a redesign. Prefer direct access where cheap. Differentiate slow-changing building geometry from volatile container contents, moveable furniture, doors, loose items, zombies and visibility. World object references may become stale after unloading; do not equate cached coordinates/history with live objects. A missing unloaded square does not mean the structure or resources do not exist.

## Survivor-centered memory and action

Survivors can remember resources, tell others about them, and later choose to return. Example: a survivor saw steel plates in a warehouse a month ago; they can inform a player, ask for a vehicle trip, accompany the player, or go themselves when an actual loaded/usable path permits it. On arrival, the plates may be gone. This is a legitimate difference between knowledge and truth, not automatically a synchronization defect.

Information may move through conversations, walkie-talkies and radios. Track that an observation was firsthand versus received secondhand, including who supplied it and when. In any future realistic radio treatment, investigate PZ's actual equipment/channel/range/power/listening constraints before adding rules. Communication transfers information, not world truth.

## Loaded and offscreen existence / simulation

A survivor's persistent identity, knowledge, needs, goals and ongoing activity should conceptually survive beyond the existence of an active loaded IsoPlayer actor. The actor is one physical representation while the game needs one.

Consider activity-dependent simulation frequencies, rather than updating every survivor every tick:
- Full simulation when an actor is close to any relevant player or interacting in an immediate physical situation.
- Reduced simulation when loaded but little needs attention.
- Abstract periodic progression when unloaded or far from players (an illustrative cadence was once per 1,000 ticks, not a fixed design decision).
- Dormant/event- or deadline-driven progression when no work is needed.

Offscreen progression could approximate travel, resources, needs and goals at plausible time intervals, and eventually allow survivors who have been unloaded to move toward a player's last known whereabouts and reconnect. Do not confuse simulated movement with guaranteed valid pathfinding. On entering loaded space, reconcile position, obstacles, conflicts, shared-world inventory, identity, and physical actor registration. Never duplicate items by committing an offscreen resource claim that conflicts with the current world state. Offscreen progress need not resolve every event with full physical fidelity, but consequences and invariants need deliberate rules.

## Multiplayer as a *future constraint*, not present scope

If SSR ever supports multiplayer, do not assume one main player defines the active area: actors may be close to any of several players, and remote players may change the world and exchange information while others are absent. Server-authoritative world/survivor state, separate per-survivor knowledge, communication provenance, scheduling/attention budgets and reconciliation would matter. Details remain hypothetical; single-player B42 delivery takes priority. Do not assert multiplayer support or plan implementation now.

## Development sequence and open questions

1. **Near-term concrete correctness:** investigate B42 spatial APIs; eliminate unjustified hard-coded Z limits in relevant house/room/loot/zombie logic and distinguish building dimensions from observed/accessible interior. Do this with source evidence and focused tests; no silent broad rewrite.
2. **Next possible foundation:** examine unified world observation and how to expose results without handing every survivor universal knowledge; profile before investing in complex caching.
3. **Later:** individual survivor memory/uncertainty, communication, survivor-managed goals, loaded/unloaded abstraction and offscreen simulation. Only develop as gameplay and test evidence demand.
4. **Optional future:** multiplayer authority and simulation coordination.

Open questions include whether native B42 provides complete vertical building/room definitions, how dynamic room/building edits are represented, what can be observed when world chunks are not loaded, how cache invalidation works, how perception and sensor access are modeled, how histories are persisted without exploding save size, and what offscreen state transitions can be safely committed.

The discussion does NOT authorize source modifications, tests, broad architecture rewrites or assignments. Continue current SSR-PERSIST-01 and SSR-TEST-02 coordination separately.
