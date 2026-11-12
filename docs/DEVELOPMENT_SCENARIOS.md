# Development scenarios and release packaging

The stations run only in debug single-player mode, and never spawn on startup
without an explicit console command. Use a fresh **disposable** world, normal
game speed, and an open area with a five-tile clear lane. Restart the game after
updating production task/action code; hot-reloading only the runner does not
replace classes already referenced by active tasks.

## Monitor a survivor

Debug single-player, one local viewport only:

```lua
SuperbSurvivorsWatch.list()     -- Living, loaded NPC IDs and names.
SuperbSurvivorsWatch.start()    -- Monitor the nearest loaded NPC.
SuperbSurvivorsWatch.start(12)  -- Monitor a specific ID; can switch targets.
SuperbSurvivorsWatch.status()   -- Snapshot plus console/log output.
SuperbSurvivorsWatch.stop()     -- Stop monitoring.
```

The post-UI overlay shows name/ID, current and previous task, AI mode, group role,
health, seen/danger counts, position and wait ticks. Task/mode/role changes are
logged. Monitoring also supports a dead local player, provided the target is
still loaded. It stops when the NPC dies/unloads or the world changes.

The overlay also shows horizontal distance in tiles, compass direction, screen
direction (for example down-right), and signed floor difference from your player.
These refresh as either character moves. Positive floors mean the survivor is
above you; negative means below. The coordinates remain visible as well. This is
a direct bearing, not a route around walls or stairs.

**Camera following is not implemented.** Both attempted camera fixes failed in
live use. The helper now states this explicitly and performs no camera writes.
It does not change player slots, actor positions, tasks or AI enablement.

The installed B42.22.2 renderer restores the real player as camera character
before constructing the world view. OnRenderTick runs after world rendering,
not before it as the previous documentation incorrectly claimed. No working
camera-only Lua route was found in the APIs checked. See
[SURVIVOR_WATCH_CAMERA_REVIEW_2026-11-12.md](SURVIVOR_WATCH_CAMERA_REVIEW_2026-11-12.md).
Camera following remains unfinished; Java changes and player-slot swapping are
not part of this implementation.

Restart the game to load these changes. Definitions remain in the existing
`Debug/SuperbSurvivorsDebug.lua`. All of `client/Debug` is excluded from release
output.

### Transfer error while the player is dead

The first reported error in the watch session was vanilla
`ISInventoryTransferAction:update` attempting
`getPlayerLoot(npc:getPlayerNum()):selectButtonForContainer(...)` at frame 55825.
It was not a watch-helper stack. Such an action may be ordinary NPC looting and
does not establish that the NPC was trading with the dead player. The log does
not identify the actor or item.

`SuperSurvivorTransferUtilities` now installs narrow, reload-safe hooks around
native update/perform. For non-local NPC actors only, the action keeps its facing
container separately and leaves vanilla's UI-only `selectedContainer` unset.
Vanilla progress, validation, transfer and completion still run. Human transfer
UI behavior is preserved. Class-level hooks cover legacy callers and existing
queued actions, not only transfers created by the mod's queue adapter.

Apply in an already-running game before retrying watch:

```lua
reloadLuaFile("media/lua/client/0_Utilities/SuperSurvivorTransferUtilities.lua")
```

Tests execute the installed vanilla update/perform methods with no human loot
panel, verify facing/progress and one completion, preserve upstream hooks across
reload, and check the normal human loot-panel path. Live verification is pending.

## Run the sequence

```lua
SuperbSurvivorsTests.runAll()
```

The game prints the station name, expected behavior, fixture NPC IDs and numbered
steps to the console/log. Short instructions/results also appear as speech above
the real player. No custom UI or screenshots are required.

The first station asks you to watch the stationary NPC **and your player** for at
least a minute, then enter:

```lua
SuperbSurvivorsTests.record(true, "Both visible; no errors")
-- If either disappears or errors occur:
SuperbSurvivorsTests.record(false, "What went wrong")
```

Following a pass, the runner advances automatically through patrol, inventory,
self-bandaging and doctor treatment. These use state checks, not automatic
judgments about whether animations look correct. Stay beside the probes, do not
block their lane or manipulate fixture items, and watch the printed steps.
Any failure, setup error or 120-second station timeout stops the sequence.

Afterward, restore the previous spawning/AI settings:

```lua
SuperbSurvivorsTests.endSession()
```

## Individual stations and controls

```lua
SuperbSurvivorsTests.list()
SuperbSurvivorsTests.start("patrol") -- also stationary, inventory, medical, doctor
SuperbSurvivorsTests.status()
SuperbSurvivorsTests.stop()         -- abort current station/sequence; retain isolation
SuperbSurvivorsTests.endSession()   -- abort and restore the previous settings
```

Completed or stopped probes are parked and reused on the next run. Repeating
`start` resets the station's tasks/actions and creates any needed supplies; it
does not delete all world changes or restore the entire save. New doctor-test
patients spawn near the doctor; the doctor approaches an existing patient if
they are farther apart. If setup
fails, the error is retained and the session remains isolated until you retry or
call `endSession()`. Starting a new world discards old test IDs/session state.

| Station | Prepared fixture and checks |
|---|---|
| `stationary` | Adjacent visible NPC, AI wait. User observes both characters; no automatic visual PASS. |
| `patrol` | Five-tile lane, actual PatrolTask. Requires A/B/A arrivals, preserving the destination between intermediate squares. |
| `inventory` | Three new nails in the player's inventory; queues the same transfer helper used by the inventory UI. Checks all three object identities left the source, entered the NPC inventory once, and the action queue finished. |
| `medical` | Heals only the fixture NPC, creates a nonbleeding forearm scratch and a ripped sheet, runs FirstAideTask. Checks bandaging and exactly one fewer sheet. |
| `doctor` | Second patient near the doctor where possible, nonbleeding scratch, alcohol wipes and bandage supplied. DoctorTask approaches if needed, then treats; checks bandaging, positive alcohol level and one bandage consumed. |

The inventory fixture does not exercise the equipped-item UI path; a separate
regression checks queued unequip-before-transfer. The doctor station does not
verify every injury, all supply types or resource scarcity. Existing NPC medical
supply generation is preserved; balancing/removing it is a separate behavior
decision. Native actions, rendering and synchronization still require in-game
validation despite passing mocked checks.

Live follow-up: stationary visibility and A/B/A patrol have passed in game.
Inventory setup now waits for the player to approach, and reports other transfer
rejections precisely. See [the live result and clothing timing changes](LIVE_STATION_AND_CLOTHING_2026-11-10.md).

## Isolation boundaries

During a session, new grid/random/preset mod spawns and raids are suppressed.
Other managed NPC Lua AI updates are filtered out; fixture task decisions run
without the autonomous AI manager inserting unrelated tasks. Ending the session
restores the previous manager filter/spawn flag and fixture AI/wait settings.
Skipped grid squares are not marked as already populated by the suppression.

Existing zombies, native actor updates, collision, health and saving remain
active. The runner does not grant god mode, remove zombies, patch rendering or
repair the real player's health. It is therefore repeatable **mod AI/spawn
isolation**, not a sandbox of the native game. Fixture actors/items can be saved;
keep this work in disposable worlds. Cleanup stops fixture tasks and native
action queues but leaves actors and supplies in the world for inspection.

## Production fixes exercised by these stations

- TaskManager clears/cancels the active and queued tasks, compacts removals,
  cleans timed-out/invalid tasks and releases old entries. It retains the public
  zero-based queue. Cancellation prefers OnCancel, then ForceComplete,
  ForceFinish, then OnComplete; success calls OnComplete. Cleanup failures are
  surfaced after the remaining detached tasks have been cleaned.
- PatrolTask retains its endpoint and records arrivals. Barricade task completion
  no longer repeats cleanup each time its completion predicate is queried.
- FirstAideTask uses vanilla completion/consumption instead of forced treatment
  after a frame counter. Its historical emergency sheet-generation policy stays.
- Inventory UI transfers queue unequipping before vanilla transfer, validate a
  nearby living member/capacity, and refresh panels after completion.
  Queued transfers also recheck moving actors' distance, floor and blocking wall.
- DoctorTask updates the nearest-patient distance and guards vanished wrapper
  lookups. The old global ISDisinfect replacement was removed so current vanilla
  owns fluid treatment and synchronization.

## Release generation

New stations belong under `42/media/lua/client/Debug/`. Future development map
folders must use `SSDebug_` under `42/media/maps/`. The builder excludes these,
including all existing debug helpers, while keeping source/development junctions
intact. Original Hilltop/Blockade/Prison/Woodbury content remains normal content.

```powershell
python tools/build_mod.py --output dist/my-build.zip
```

The ZIP uses `Contents/mods/SuperbSurvivors/{42,common}` layout and includes only
versioned content and `common/media` assets. It excludes debug helpers/maps,
generated `common/<world>/` save data, docs, tests, tools and historical reference
files. Existing output files are never silently overwritten. This generates a
local artifact; it does not publish to Workshop or certify release readiness.

Validation at implementation: 94 Python/Lua regression checks pass with
`PZ_GAME_DIR` set to the installed game; all 108 runtime Lua files compile.
These include cancellation/timeout/cleanup failure, endpoint traversal, transfer
ordering/range, medical completion, spawn suppression, session restoration and
sequence failure handling. No new station has yet been observed in the native game.
