# SuperSurvivor.lua API audit — 2026-10-21

Target: locally installed Project Zomboid **42.21.0**, revision `4a0e9546ec`,
Steam build `25485521`. Inspected `projectzomboid.jar` and vanilla Lua under
`G:\Steam\steamapps\common\ProjectZomboid`.

The latest user report describes invisible survivors despite apparent activity.
The log recorded survivors **5** and **6**, then a window-action failure caused
by the old duration argument being interpreted as a vehicle part. That exception
is fixed, but invisibility remains unresolved. Construction completes in game;
visible presence and functioning AI are not yet established.
The success message and following full stack are preserved in
[the local error record](LOCAL_STARTUP_ERRORS_2026-10-21.md).

## Changes from the whole-file review

| Legacy call | Verified replacement |
| --- | --- |
| Player `getForname` / `setForname` | Descriptor `getForename` / `setForename`, plus player `setDisplayName` |
| `Stats:getHunger`, `getThirst`, and legacy stat setters | `Stats:get/set(CharacterStat.…, value)` |
| BodyDamage food sickness, poison, unhappiness and wetness access | Corresponding `Stats:get/set(CharacterStat.…, value)` |
| `NPCGetRunning`, `NPCSetRunning` | `isRunning`, `setRunning` |
| `NPCSetJustMoved` | `setJustMoved` |
| `NPCSetAiming` | `setIsAiming` |
| `setTarAlphaAlpha` | `setTargetAlpha` |
| Clothing `getDirtyness`, `setDirtyness` | `getDirtiness`, `setDirtiness` |
| String `"Jacket"` passed to worn-item accessors | `ItemBodyLocation.JACKET` |
| `WornItems:getItem("Shoes")` in walking/running modifiers | `ItemBodyLocation.SHOES` |
| Indexed access to `IsoCell:getObjectList()` | `getLuaObjectList()` snapshot traversed with `ipairs` |

The worn-item failure is a signature-type change, not a missing method. Fixed
all literal jacket accesses in the survivor file and made `WearThis` use the
typed location returned by clothing/bags. Bags now retain their declared
attachment slot instead of being forced onto the back. The NPC dressing path no
longer accesses the local player's inventory UI; model updates and the clothing
event remain. Suit/table utility dependencies are explicit. A full mocked
`SuperSurvivor:new()` now completes outfit setup with strict typed-slot stubs.

Stat changes retain the existing values and thresholds. Removed the old
`NPCGetRunning` existence guard that silently prevented running after the API
was removed. Movement and aiming behavior still require in-game observation.

The cell's `getObjectList()` now declares `java.util.Set`, which has no `get(i)`.
Inspected bytecode confirms `getLuaObjectList()` builds a one-based Lua table.
All three survivor vision/sensing scans and the debug-player scan now use that
snapshot, with direct Lua indexing when retrieving the selected target. Existing
range, visibility, hostility and threat-counter behavior remains. A targeted
audit rule now detects indexed `get` access on simple local aliases of the
cell's Set-returning getters; a negative probe catches the original pattern.

The subsequent movement failure revealed another typed-location accessor on
`WornItems`, separate from the player worn-item methods. Fixed both shoe lookups.
The adjacent bag-speed path was also passing an `ItemContainer` into a helper
that calls the item-only `getScriptItem()`. It now receives the bag item, whose
contents weight/effective capacity and public script run-speed modifier were
verified against the installed JAR. Corrected the aggregate calculation so no bag
preserves the 1.0 baseline instead of producing a zero running multiplier, and
avoided division by zero for zero-capacity bags. Shoe and load penalties remain.

## Combat and fluid follow-up: targeted calls ported

The previously identified unsupported calls have been removed from active code.

| Legacy methods | Replacement behavior |
| --- | --- |
| `NPCSetAttack` / `NPCSetMelee` | Stop methods clear pending attack intent/target; both attack entry points use a shared B42 `pressedAttack()` request. |
| `getWaterAmount` | `getFluidAmount()` and the installed vanilla B42 drinking/washing actions. |

Combat now checks target validity, range, readiness, cooldown and current attack
state, faces the target, sets its square and aiming state, then invokes
`IsoPlayer:pressedAttack()`. Installed bytecode shows that method delegating to
`CombatManager:pressedAttack(player)`, which manages initiation/start flags.
An accepted request starts the mod cooldown; rejection is returned to the caller.
No exceptions are suppressed. The old manual `victim:Hit()` calculations were
removed from both attack paths so the engine owns accuracy and damage instead of
receiving a second forced hit. Existing ammo-search/melee fallback remains.
Stop methods cancel queued intent without resetting an active attack animation.
The old swing-event ammo/chamber/sound compensation was also removed for NPCs;
the local player's gunshot reaction hook remains. Actual hits, animation, ammo
consumption and cancellation timing still need in-game validation.

Drinking uses `ISTakeWaterAction:new(player, nil, source, tainted)` and lets the
vanilla action compute liters, consume source fluid and apply `DrinkFluid` effects
on completion. Empty, nonwater, unreachable and unneeded sources are rejected.
`FindThisTask` no longer marks a rejected queue request successful.

The affected `WashSelfTask` also used old water and clothing-dirt calls and shifted
constructor arguments. It now uses B42 action signatures, the inventory soap list,
and fluid amounts, reserving water and soap across self/clothing actions without
consuming at queue time. The wash-source selection policy remains large-volume
or tainted water, preserving the prior preference for not spending small clean
supplies on washing. There is no mod copy of `ISTakeWaterAction` in this checkout;
the installed vanilla action is required directly.

## Audit coverage and interpretation

`tools/audit_survivor_api.py` scans the entire file with strings and comments
excluded, checks known Java receiver chains through public inherited methods
and interfaces, and follows unambiguous declared return types. It found public
methods at **611 call sites**, with no argument-count mismatch among those sites.
It also inventories every colon-call name against public methods in all `zombie/`
classes and named function definitions in the mod, and checks static-looking
calls whose class names can be resolved uniquely. A targeted check now reports
literal strings passed to `getWornItem` / `setWornItem` and simple local aliases
of `getWornItems():getItem/setItem`; negative probes catch the old jacket and shoe
calls. It does not infer all argument types.

Some reported Java misses are valid uses of runtime subtypes or vanilla Lua:

- `getItemContainer` exists on `InventoryContainer`; `isAimedFirearm` and
  `getMinRange` exist on `HandWeapon`.
- Blood access exists on `HumanVisual`, though `getVisual()` declares `BaseVisual`.
- `ArrayList:size()` belongs to the Java runtime, outside the game JAR.
- `refreshBackpacks` is defined in vanilla `ISInventoryPage.lua`; `match` is a
  Lua string method.
- `AdjacentFreeTileFinder.FindWindowOrDoor` is defined by vanilla
  `shared/Util/AdjacentFreeTileFinder.lua`, which replaces the Java global with
  a Lua table. It must not be removed because the Java class lacks that method.

This is a conservative static review, not complete type inference. Presence and
argument counts do not prove Lua exposure, argument types, overload selection,
valid item IDs, state preconditions, or equivalent gameplay. Arbitrarily named
local variables and mod-defined wrappers are not fully type-checked. No claim
is made that all calls in this file, or the rest of the mod, are B42-compatible.

Reproduce the report locally (JSON includes each checked and unresolved site):

```powershell
.venv\Scripts\python.exe tools\audit_survivor_api.py G:\Steam\steamapps\common\ProjectZomboid\projectzomboid.jar 42\media\lua\client\3_Other\SuperSurvivor.lua --inventory
```

Validation: **45 tests** and **109/109 Lua syntax checks** pass with `PZ_GAME_DIR`
set to the installation above. Combat tests cover one engine request without
manual damage, cooldown/busy/invalid-target rejection, cancellation, propagated
errors, and the swing callback avoiding duplicate ammo changes. Fluid tests cover
queue arguments, source rejection, water search and shared resource budgets.
Three optional checks execute installed vanilla water/wash/window Lua with mocked
game services; they verify consumption/completion, constructor compatibility and
the smash-window waiting path. Without `PZ_GAME_DIR`, those checks are skipped.
No test runs live combat,
animation, navigation or a complete in-game survivor. Outfit tests cover the
full mocked constructor, preset dressing, correct bag attachment, and
missing/unlocated items; the location stub rejects legacy strings.

Vision tests use plain one-based Lua arrays without Java `size/get` methods and
cover nearest-target selection, threat counts, stale-state clearing, human-only
sensing, companion sensing, and the debug-player scan.

Movement checks execute the walking-speed calculation with typed shoe-slot
stubs, verify barefoot/broken-shoe penalties and a nonzero bag-free running
baseline, and check back/hand bag penalties without passing contents containers
as items. They still do not run live pathfinding or animation.

```powershell
$env:PZ_GAME_DIR = 'G:\Steam\steamapps\common\ProjectZomboid'
.venv\Scripts\python.exe -m unittest discover -s tests -v
```
