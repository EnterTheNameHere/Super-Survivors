# Build 42 port status

Target: Project Zomboid 42.21, initially single-player. This is still B41 gameplay
code being ported to B42. Local testing has begun against 42.21.0.

## First increment: dependencies and a spawn probe

Fixed the survivor -> preset -> group-manager -> group require paths, made the
translation/dialogue/name prerequisites explicit, and removed the unused
`CharacterSave_SaveLoad` require from the context menu. Character saving still
uses the existing `SuperSurvivor:SaveSurvivor` path; persistence has not migrated.

The isolated Lua tests cover the real survivor dependency chain, context-menu
registration, the debug probe's preconditions/delegation/error propagation,
NPC flag setup before perk initialization, moodle speech initialization, and
`spawnPlayer` trait/stat setup. Game-provided services are mocked. These tests
do not exercise the survivor constructor in game or establish that all mod files
load inside Kahlua. A later test covers the full wrapper constructor with strict
game-object stubs through outfit completion.

## Local startup/spawn increment — 2026-10-21

The user entered a fresh single-player world on 42.21.0 (`4a0e9546ec`) and ran
`SuperbSurvivorsDebug.spawn()`. The log records an earlier startup failure in
`retrieveMoodles` and then a nil method call at `SuperSurvivor.lua:579` when
setting the new character's NPC flag. See the preserved
[pre-fix stacks](LOCAL_STARTUP_ERRORS_2026-10-21.md).

Inspected the installed `projectzomboid.jar`: `IsoPlayer` declares
`setNpc(boolean)`, its parent exposes `isNpc()`, and moodle constants use uppercase
names. Updated NPC flag calls throughout the mod, switched speech moodles to
those constants, and replaced the generated `loadstring` moodle lookup with
direct access. No constructor errors are suppressed.

Local validation: all nine isolated tests and all 109 Lua 5.1 syntax checks pass.
These fixes still need a restarted in-game run; successful NPC spawning and
continued presence have not yet been observed. A failed constructor may already
have created a partial character, so retest in a fresh disposable world.

`tools/inspect_game_api.py` lists declared fields/methods from a local JAR without
executing game code or requiring a separate JDK, for example:

```powershell
.venv\Scripts\python.exe tools\inspect_game_api.py G:\Steam\steamapps\common\ProjectZomboid\projectzomboid.jar zombie.characters.IsoPlayer --filter '(?i)npc'
```

The next in-game run passed NPC flag setup and failed at `getTraits()` on line
609, during both automatic grid-square spawning and the manual probe. No
`retrieveMoodles` errors appeared in that log. Updated `spawnPlayer` to use
`getCharacterTraits():add(CharacterTrait.…)`, verified against the installed JAR
and vanilla Lua. The eight supported bonuses remain; the removed legacy `Lucky`
trait is omitted because the installed `CharacterTrait` API has no such constant.
Also replaced this function's obsolete hunger/thirst setters with
`Stats:set(CharacterStat.HUNGER/THIRST, value)`, preserving the original values.

Validation now passes ten isolated tests, including the entire `spawnPlayer`
function with strict B42 trait/stat stubs, and all 109 Lua syntax checks. This
still requires an in-game retest of the complete survivor constructor and AI.

The next run failed at player `setForname` (line 677). Fixed naming through the
descriptor and reviewed the full survivor file against the installed game APIs.
Ported additional stat, movement, aiming, alpha and clothing-dirt calls. Thirteen
isolated tests and all 109 syntax checks pass. The
[whole-file API audit](SUPER_SURVIVOR_API_AUDIT.md) records coverage, verified
replacements, and known remaining combat/fluid calls. In particular, removed
`NPCSetAttack`/`NPCSetMelee` calls still block an error-free movement/AI run and
must receive a behavior-level port; another spawn check alone will not resolve
those known incompatibilities.

The targeted combat/fluid follow-up is now implemented. Attack requests go through
B42 `pressedAttack()` and engine hit resolution; stopping clears pending intent,
and the NPC swing callback no longer duplicates engine ammo/chamber handling.
Drinking and washing use vanilla B42 actions, fluid volumes and corrected queue
arguments. Water/soap budgets are reserved across wash actions, and rejected
drinking requests are not reported as successful. See the current
[API audit](SUPER_SURVIVOR_API_AUDIT.md) for details and limits.

Validation now passes 25 tests with `PZ_GAME_DIR` set, including two tests running
the installed vanilla water/wash Lua against mocked game services. All 109 Lua
syntax checks pass. The targeted removed APIs no longer appear in active code;
remaining audit misses are the documented subtype/vanilla Lua cases. Restart the
game and use a fresh disposable world to verify spawning, continued presence,
movement, melee/ranged attacks and water use. B42 now determines attack accuracy,
damage and ammo consumption; live combat behavior is not yet verified.

The next run reached outfit setup and failed at `setWornItem("Jacket", nil)`:
B42 requires `ItemBodyLocation.JACKET`. Fixed the survivor file's jacket
accessors and typed clothing/bag attachment. Removed NPC dressing's local-player
inventory UI access and made suit utilities explicit dependencies. All 28 tests
pass, including a full mocked survivor constructor through outfit completion;
109 syntax checks pass. The audit now catches literal string body-location
arguments, but still does not provide complete argument-type inference.
Restart and retest the debug spawn in a fresh disposable world.

The following run logged successful creation of survivor 4 at 10778,9764,0,
then failed on its next `DoVision` update: `IsoCell:getObjectList()` now returns
a Set, not an indexed list. Switched the three survivor scans and the debug-player
scan to B42's one-based `getLuaObjectList()` snapshot. All 33 tests and 109 Lua
syntax checks pass. Construction is now observed in game; continued presence,
navigation and combat still require restarted in-game validation.

The next run spawned survivor 4 at 10697,9383,0 and got past vision, then failed
in walking-speed calculation on `WornItems:getItem("Shoes")`. Both shoe lookups
now use `ItemBodyLocation.SHOES`. Fixed the adjacent running path to pass bag
items rather than contents containers to the bag-speed helper and retain the
1.0 baseline when no bag is carried. All 37 tests and 109 syntax checks pass.
Restart and verify continued presence/update behavior; movement/combat remain
unverified in game.

The user subsequently reports invisible NPCs despite apparent movement/activity.
The log records survivors 5 and 6, then a later building-entry failure:
`ISSmashWindow:new(player, window, 20)` puts `20` into B42's `vehiclePart` slot,
causing `waitToStart` to fail at `vehiclePart:getVehicle()`. Corrected that call
and the adjacent glass-removal call to their installed two-argument signatures.
The climbing action still accepts a duration; its valid call was retained.

All 42 tests and 109 syntax checks pass with `PZ_GAME_DIR` set. Three optional
tests now execute installed vanilla Lua, including the actual smash-window
`waitToStart` path. This fixes the confirmed exception, not the invisible model.

For the next visibility investigation, restart and run:

```lua
SuperbSurvivorsDebug.spawnStationary()
-- Let a few game frames run, then pause and inspect the latest probe:
SuperbSurvivorsDebug.inspect()
```

An explicit survivor ID is also accepted, e.g. `SuperbSurvivorsDebug.inspect(6)`.
Inspection logs coordinates, observer visibility, cell/square membership, model
registration/activation, culling, alpha and visual properties. It changes no
visibility flags and does not spawn another NPC. The invisibility cause is still
unresolved; use this evidence before choosing a rendering initialization fix.

The first inspection found a registered active model and valid cell/square
membership, but zero alpha on a square outside the observer's visible area;
the NPC had moved about eight tiles away. That snapshot is inconclusive. The
compound console hold command failed after spawning another character, so the
single-call stationary probe now chooses a visible free adjacent tile and uses
the existing stop/wait methods inside the module. It pauses Lua AI only for that
explicit diagnostic spawn and does not alter visibility flags. To release it,
set the wrapper's wait to zero with
`SSM:Get(SuperbSurvivorsDebug.lastSpawnedID):Wait(0)`.

All 45 tests and 109 syntax checks pass. The new tests verify visible/free tile
selection, one spawn/stop/wait sequence, and constructor error propagation.
Reload only the changed debug module in the running game before using the probe:

```lua
reloadLuaFile("media/lua/client/Debug/SuperbSurvivorsDebug.lua")
```

Run from the checkout with Python and `lupa==2.6`:

```sh
python -m unittest discover -s tests -v
```

## In-game check

1. Use a fresh disposable 42.21 single-player world with only this mod enabled.
   Start the game with `-debug`. Avoid a second Workshop copy of the same mod.
2. Record any loading/initialization errors from `Zomboid/console.txt` first.
   Stop and investigate the first relevant stack trace if initialization fails.
3. Once the player is in the world, run in the debug Lua console:

   ```lua
   SuperbSurvivorsDebug.spawn()
   ```

   This requests one survivor two tiles east, on the player's floor, only if the
   tile is loaded, free and has a floor. To choose a tile explicitly:

   ```lua
   SuperbSurvivorsDebug.spawn(x, y, z)
   ```

4. A successful call returns the survivor wrapper and logs its ID and position.
   Confirm that the character is visible and remains present without recurring
   errors. The command uses the existing constructor, so it is not an isolated
   AI mode and can trigger legacy initialization behavior.
5. Record the exact game version, command, observed behavior, and first full
   relevant error stack. Constructor exceptions deliberately propagate.

Nothing spawns automatically from the new debug module. Existing random/preset
spawning remains unchanged. Repeated calls deliberately create additional NPCs;
the probe does not provide cleanup or save-migration guarantees.

## Remaining work

- Deferred, non-blocking: explore NPC/local-player visibility ownership through
  existing Lua APIs only. Java-side modifications are excluded. On 2026-11-12
  the user accepted the current visibility issue and restart recovery so other
  porting work can proceed. See the latest decision in [LOCAL_HANDOFF.md](LOCAL_HANDOFF.md).

- Validate startup events and remaining trait/API references; verify the updated
  moodle speech code in game.
- Verify the survivor constructor, NPC flags and registration against 42.21.
- Verify movement, combat, animations and the bundled Java bytecode.
- Rebase copied vanilla actions and UI onto the target game's implementations;
  inventory and action authority need particular attention.
- Implement versioned, server-owned global mod data for groups and the survivor
  registry. Full character serialization is a separate requirement.
- Port fluids, farming, jobs and multiplayer synchronization after the core.

The historical files under `reference/` are not runtime defaults and must stay
out of release packages. See [the local handoff](LOCAL_HANDOFF.md) for continuing
in VS Code with a local Codex session.
