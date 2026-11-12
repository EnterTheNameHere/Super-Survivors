# Lua duplication review — 10 November 2026

Follow-up: removed `client/TimedActions/ISEnterVehicle.lua`, retaining the identical
implementation at the canonical `client/Vehicles/TimedActions/ISEnterVehicle.lua`
path. FollowTask now explicitly requires that path before entering a vehicle.
This removes duplicate ownership without changing the action's behavior; its
vanilla/NPC compatibility migration is still pending. The scan below records the
pre-removal snapshot.

## Results

Scanned **112 mod Lua files** (108 runtime files and four map spawnpoint scripts)
against one another and **1,395 installed vanilla Lua files**. Historical save
files, translations, binary map/Java assets and generated world metadata are
outside this code-clone scan. Runtime source was not changed by this review.

The scan found:

- **One byte-identical file pair:** the two `ISEnterVehicle.lua` files.
- **48 exact normalized block matches** inside the mod.
- **68 additional structural block candidates**, allowing identifier differences.
- **37 groups of identical function parameter/body tokens**, including shorter helpers.
- **Seven qualifying matching ranges against current vanilla.**

These are overlapping pairwise ranges, not 116 independent defects, a duplicated
line percentage, or a count of functions to delete. Several UI components match
many other copies. A structural match is a review candidate, not semantic equality.
All raw locations, modes and source hashes are in
[LUA_CLONES_2026-11-10.json](LUA_CLONES_2026-11-10.json).

## Highest-value findings

### 1. Inventory cleaning and loot sorting share a large implementation

Locations under `42/media/lua/client/7_Tasks/`:

- `CleanInvTask.lua:84–160` ↔ `SortLootTask.lua:94–170`: **444 exact tokens**.
- `CleanInvTask.lua:59–76` ↔ `SortLootTask.lua:55–72`: **135 exact tokens**.
- `CleanInvTask.lua:180–195` ↔ `SortLootTask.lua:204–219`: **120 exact tokens**.

The shared implementation selects what to retain/drop, searches for containers,
queues transfers/drops and deals with equipment. SortLoot additionally chooses a
destination from the group's storage areas; CleanInv receives a destination.

**Why it matters:** both still iterate Java item lists from index 1 to size-1,
skipping the first item. Repeated transfer logic also makes it easy for the new
inventory/action fixes to reach one path while another retains direct mutations.

**Recommended extraction:** share item-retention rules and a deposit operation;
keep destination-selection policy in each task. Do not merge the entire tasks or
force square drops through a helper that only supports inventory containers.

### 2. The UI has repeated building blocks across several files

The main family is `DDebugUI.lua`, `SuperSurvivorBasePanel.lua`,
`SuperSurvivorInfoPanel.lua`, `SuperSurvivorInventory.lua` and
`SuperSurvivorLoadout.lua` under `5_UI/`.

Examples:

| Component | Example locations | Evidence |
|---|---|---|
| Window/frame setup and lifecycle | Inventory `312–378` ↔ Loadout `336–402` | 322 structural tokens |
| Frame setup | BasePanel `273–328` ↔ Inventory `316–371` and Loadout `340–395` | 288 structural tokens per pair |
| Title-bar drag/visibility handling | DDebugUI `17–70` ↔ Loadout `4–57`; shorter copies in the other panels | 249 structural tokens, plus exact smaller methods |
| Item tooltip handling | Inventory `87–106` ↔ Loadout `95–114` | 120-token identical function bodies |
| Repeated button/label construction | DDebugUI `101–109`, Inventory `201–209`/`249–257`, Loadout `226–234`/`277–285`, Window `79–87`/`208–216`/`290–298` | Eight identical parameter/body occurrences |

**Recommended extraction:** small mod-owned title-bar, tooltip, row/button and
window-frame helpers. Preserve each panel's data/action callbacks. Several
definitions use *local* class names, so sharing a name does not itself prove a
global collision. Avoid a large generic UI framework to eliminate a few methods.

### 3. The same 25-order menu is constructed twice

`5_UI/SuperSurvivorWindow.lua:503–528` and `:540–565` contain the same order labels
and numeric dispatch mapping, targeting different menu variables: **476
structural tokens**, the largest structural block found.

One builds a direct order menu; the other builds an Order submenu. Both hard-code
English labels and index-based `give_order` calls.

**Recommended extraction:** one menu-population function using a canonical order
catalog and translated display labels. Preserve the direct/submenu presentation.
This is a particularly useful companion to the planned translation cleanup.

### 4. Duplicate global helpers already show behavioral drift

| Helper | Definitions | Assessment |
|---|---|---|
| `getSaveDir` | `shared/Utilities.lua:14–16`; `0_Utilities/SuperSurvivorTablesUtilities.lua:204–206` | 47 identical parameter/body tokens. Keep one shared definition. |
| `isModEnabled` | `shared/Utilities.lua:2–11`; `3_Other/SuperSurvivorPresetSpawns.lua:5–14` | Identical helper bodies. Server `SSurvivors.isModEnabled` at `server/SuperSurvivorsLoading.lua:6–15` is a third namespaced copy. |
| `makeToolTip` | `0_Utilities/SuperSurvivorUtilities.lua:132–145`; `5_UI/SuperSurvivorPVPButton.lua:5–18` | 47 identical parameter/body tokens. Two declarations of the same global helper. |
| `SurvivorTogglePVP` | `0_Utilities/SuperSuvivorsCombatUtilities.lua:92`; `5_UI/SuperSurvivorPVPButton.lua:20` | Same feature duplicated, but one uses English string literals and the other translated keys. The literal-preserving clone scan does not group the whole bodies; declaration review found the drift. |

**Why it matters:** later execution of a global declaration replaces the earlier
one. Even when initial behavior is identical, a later fix can silently be
overwritten. Determine ownership and load dependencies before deleting a copy;
namespacing the shared helpers would also reduce collision risk with other mods.

### 5. Actor constructors repeat runtime-state initialization

`3_Other/SuperSurvivor.lua`:

- `:26–85` ↔ `:165–225`: **345 structural tokens**, across new/load initialization.
- `:55–80` ↔ `:268–293`, and `:195–220` ↔ `:268–293`: **137 exact tokens** each,
  shared with the wrapper for an existing player.

These set transient tables, counters, cached equipment/state and presentation
objects. Constructor differences remain meaningful: creating a new NPC, loading
one and wrapping the real player must not have identical actor/trait/ownership
side effects.

**Recommended extraction:** a narrow runtime-state initializer receiving an
already selected actor. Leave creation/loading, durable IDs, native ownership,
trait initialization and player-specific behavior in their own paths.

### 6. Spawn and raid placement repeat an identical search

`3_Other/SuperSurvivorsMod.lua:812–861` ↔ `:1099–1148`: **315 exact tokens**.
The shared section selects off-screen outside spawn locations around a center.
One occurs in `SuperSurvivorsNewSurvivorManager`; the other in the raider manager.
The former is called by the alternate spawn-generation functions, so this is not
merely an unused historical copy.

**Recommended extraction:** a function that returns a candidate square and an
explicit failure. Keep raid timing, population/group creation and hostility
policy outside it. Preserve the test-session spawn suppression guards.

### 7. Spatial helpers repeat traversal/projection calculations

- `0_Utilities/SuperSurvivorContextUtilities.lua:526–542` ↔ `:562–578`: **170 exact
  tokens** shared by closest-unlocked-door and closest-door searches. They differ
  later in whether locked doors qualify; that difference must remain.
- `3_Other/SuperSurvivor.lua:1033–1047` ↔ `:1048–1062`: **112 exact tokens** for
  marking building squares explored, with different entry guards.
- `0_Utilities/SuperSurvivorUtilities.lua:149–158`, `:167–176`, `:183–192`: repeated
  mouse-to-world projection calculations. The functions return a square, X, or Y,
  so they are not interchangeable despite their common arithmetic.
- `5_UI/UIUtils.lua:47–60` ↔ `:64–77`: **101 exact tokens** of group lookup/creation
  in `get_group` and `get_member_info`. Consolidating this is also an opportunity
  to separate read-only UI queries from group mutation.

**Recommended extraction:** small shared traversal/projection primitives with
explicit filters/results, rather than deleting one function in favor of another
whose contract differs.

### 8. The two vehicle-entry files are an exact duplicate

`TimedActions/ISEnterVehicle.lua` ↔ `Vehicles/TimedActions/ISEnterVehicle.lua`:
byte-identical files and **350 normalized code tokens** at lines `5–74`.
Both define the same global `ISEnterVehicle` class under different require paths.

This confirms the earlier replacement review. Removing duplicate ownership is
worth doing, but the actual implementation also needs a current-vanilla/NPC
decision. Keep that action migration separate from a mechanical code cleanup.

## Matches against installed vanilla

Vanilla paths below are relative to
`G:/Steam/steamapps/common/ProjectZomboid/media/lua`.

| Mod file / range (under `42/media/lua`) | Vanilla file / range | Exact tokens |
|---|---|---:|
| `client/TimedActions/ISBarricadeAction.lua:41–73` | `shared/TimedActions/ISBarricadeAction.lua:37–69` | 213 |
| `client/TimedActions/ISBarricadeAction.lua:74–101` | `shared/TimedActions/ISBarricadeAction.lua:69–100` | 195 |
| `client/TimedActions/ISBarricadeAction.lua:5–35` | `shared/TimedActions/ISBarricadeAction.lua:1–31` | 165 |
| `client/TimedActions/ISEnterVehicle.lua:32–72` | `client/Vehicles/TimedActions/ISEnterVehicle.lua:63–103` | 192 |
| `client/Vehicles/TimedActions/ISEnterVehicle.lua:32–72` | Same vanilla range | 192 |
| `client/5_UI/SuperSurvivorOptions.lua:231–255` | `client/OptionScreens/GameOption.lua:51–75` | 112 |
| `client/5_UI/SuperSurvivorOptions.lua:208–229` | `client/OptionScreens/GameOption.lua:5–26` | 111 |

The options match is useful because the mod file has a different name: filename
comparison alone misses this copied implementation. It declares **local**
`GameOption`/`GameOptions` classes; this finding is not evidence that it replaces
the global vanilla class. Assess whether current vanilla options facilities can
be used before maintaining another private copy.

These seven matches are a conservative lower bound. Old scavenging/eating code
can be copied from a former game version yet share no sufficiently long literal
token sequence with today's vanilla. A missing match does not mean original
authorship or B42 compatibility. Recently removed redundant actions/admin UI are
correctly absent from this scan.

## Recommended cleanup order

1. Establish one owner for small duplicate helpers and the order-menu builder.
2. Consolidate loot selection/deposit operations while repairing the repeated
   zero-based-list and action-completion problems.
3. Extract the small shared UI components, preserving each panel's behavior.
4. Share runtime-state initialization and spawn-square search only after their
   differing contracts are explicitly represented.
5. Continue vanilla-action migrations as behavior changes, not merely deduplication.

Do not automatically merge task constructors, generic `isComplete`/`isValid`
methods, hit/surrender actions, or different door filters. Some small copies are
reasonable independent scaffolding. Behavior changes and dependency cycles are
more expensive than a few repeated lines.

## Reproduce and interpret

```powershell
python tools/find_lua_clones.py --game "G:\Steam\steamapps\common\ProjectZomboid" --output .venv/lua-clones.json
python -m unittest discover -s tests -p test_lua_clones.py -v
```

The standard-library detector tokenizes Lua, retaining literal strings/numbers,
ignoring comments/formatting/optional semicolons, fingerprints 40-token windows,
verifies matching seeds and extends them to common ranges. Large ranges require
at least 100 tokens and eight lines on both sides. It compares within files too.
Separate function-body grouping catches shorter helpers, omitting declaration
names but retaining parameter/body tokens. Byte hashing identifies full copies.

Structural scanning additionally masks bare identifiers while preserving field,
method and direct function-call names. It does not resolve variable binding or
establish one-to-one renaming; two structurally similar expressions can mean
different things. Seed occurrence lists are capped at 30, so very repetitive
code may have additional unreported pairs. The block-stack recognizer used for
short helper grouping is not a full Lua AST/type parser. The six detector tests
cover comments/strings, literal preservation, structural matching, repeated
blocks, nested function blocks and exact evidence retention.

Source hashes in the JSON identify the runtime snapshot. No runtime refactoring
was performed, and no gameplay claims follow from these static matches.
