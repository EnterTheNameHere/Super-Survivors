# Vanilla replacement review — 10 November 2026

## Applied first cleanup

Follow-up during development-station implementation: the obsolete global
`ISDisinfect.lua` copy was also removed. DoctorTask now resolves the installed
disinfection action; native fluid treatment is checked by the new doctor station.
The removal is implemented; its in-game result is still pending.

After this review, the redundant `ISApplyBandage.lua`, `ISRemoveBrokenGlass.lua`
and copied `ISPlayerStatsUI.lua` were removed from the mod. The debug context
menu now explicitly requires the installed stats panel. Bandage/window tests
read installed vanilla through `PZ_GAME_DIR`; all 69 tests pass against the local
42.22.2 installation, and all 107 remaining runtime Lua files parse. The linked
development installation sees these removals immediately, but a full game
restart is required to discard previously loaded classes/event handlers.
In-game treatment, window interaction and panel opening remain to be checked.

The sections below describe the pre-cleanup comparison and the remaining
recommendations. Barricading, disinfection, eating, vehicle entry and method
hooks were not changed by this first cleanup.

## Conclusion

None of the examined whole-file Lua replacements currently demonstrates a need to replace the global vanilla class. Two supply no behavioral change at all. Four action families preserve old behavior that has drifted from B42. The copied admin panel also replaces a much newer vanilla implementation for mostly layout/localization changes and older APIs.

Use installed vanilla first, adapting NPC call sites to its current contracts. If an NPC-specific incompatibility is reproduced, implement the smallest namespaced NPC adaptation required. Do not assume vanilla works for standalone NPC players merely because it works for the local player; that actor-ownership problem is separate. A temporary whole-file replacement should have a documented necessary delta and exact baseline version, neither of which the older copies currently provide.

This comparison used the installed **42.22.2** Lua files and assets under `G:/Steam/steamapps/common/ProjectZomboid`. It is a static comparison with an isolated barricade-constructor probe, not a new in-game validation. **No runtime files were changed.**

## What actually replaces what

There are eight mod Lua files with matching installed filenames, defining seven overlapping vanilla classes. Some vanilla actions now live under `shared/TimedActions`, while these copies live under `client/TimedActions`. Moving a copy into client scope does not make the global class NPC-only. Files assign `IS… = ISBaseTimedAction:derive(...)`, creating replacement class tables rather than extending the existing vanilla table. Previously added methods/patches on the displaced table can also be lost. Exact effective loading order is not proven by this file comparison.

| Mod file under `42/media/lua/client/` | What it does | Comparison and recommendation |
|---|---|---|
| `TimedActions/ISApplyBandage.lua` | Bandaging/unbandaging another character or self | **Identical to installed vanilla** after line-ending normalization. Remove the redundant copy; preserve current caller signatures and test vanilla resolution. |
| `TimedActions/ISRemoveBrokenGlass.lua` | Removes broken glass from a window | **Behaviorally identical**; only whitespace and optional semicolons differ. Remove the redundant copy. This is not medical glass removal. |
| `TimedActions/ISBarricadeAction.lua` | Wooden/metal/bar barricading, tools, costs, XP and sounds | Old implementation conflicts with current constructor, validation and completion. Restore vanilla and update NPC caller. |
| `TimedActions/ISDisinfect.lua` | Disinfects a body part using an inventory item | Old fluid, treatment, animation and synchronization behavior. Restore vanilla first; adapt medical task only if necessary. |
| `TimedActions/ISEatFoodAction.lua` | Eating/drinking food-item actions, smoking-related requirements and cancellation | Large obsolete copy drops current behavior. Restore vanilla first; isolate actual NPC animation differences if reproduced. |
| `Vehicles/TimedActions/ISEnterVehicle.lua` | Enters a vehicle seat | Exact duplicate of the following mod file. Old instant animation workaround bypasses current safety/setup behavior. One NPC-specific adaptation at most, if needed. |
| `TimedActions/ISEnterVehicle.lua` | Same class and implementation, under a second require path | Remove duplicate class ownership. Two files under different require paths can each redefine the global class. |
| `ISUI/PlayerStats/ISPlayerStatsUI.lua` | Global player/admin statistics editor | Older vanilla panel with layout/translations and stale APIs. Use the installed panel; keep the mod's menu entry if useful. |

### Bandaging: redundant replacement

[Mod file](../42/media/lua/client/TimedActions/ISApplyBandage.lua), installed reference `media/lua/shared/TimedActions/ISApplyBandage.lua`.

Both are 192 lines and text-identical after normalizing line endings. The recent port already brought this action back to vanilla, including `ISBaseTimedAction.new`, current traits, duration, completion and treatment synchronization. There is no remaining NPC-specific delta to preserve.

**Approach:** remove the mod copy and let `require "TimedActions/ISApplyBandage"` resolve to the game implementation. Keep doctor/self-treatment calls with the current five-argument constructor. Some existing Python tests read the local copied file directly; update those tests to validate the installed action or the actual mod adaptation rather than keeping a duplicate solely for the test fixture. Actual patient/doctor execution still needs validation after the broader actor changes.

### Broken window glass: redundant replacement, previously misclassified

[Mod file](../42/media/lua/client/TimedActions/ISRemoveBrokenGlass.lua), installed reference `media/lua/shared/TimedActions/ISRemoveBrokenGlass.lua`.

It defines `ISRemoveBrokenGlass` and acts on `self.window`: animation, validity, `complete()` and window synchronization match installed vanilla. Normalizing whitespace and optional semicolons makes the two sources identical. The NPC entry task already calls `ISRemoveBrokenGlass:new(character, window)` with the current signature.

**Approach:** remove the copy and retain the vanilla call. Medical removal of glass from a patient is the separate `ISRemoveGlass` action used by `DoctorTask`; the mod does not replace that action. The earlier file guide conflated the two and has been corrected.

### Barricading: constructor and resource contract have drifted

[Mod file](../42/media/lua/client/TimedActions/ISBarricadeAction.lua), installed reference `media/lua/shared/TimedActions/ISBarricadeAction.lua`.

The mod still performs the actual barricade mutation, material removal and XP directly in `perform()`, or sends the older `'object','barricade'` client command. Installed vanilla separates presentation/queue completion from `complete()`, checks/removes the required materials, sends container/object updates, awards XP through current helpers and marks construction state.

Specific differences:

- Mod `isValid` accepts the presence of nails; vanilla checks at least **two**. The mod then removes two regardless.
- Mod only accepts named `Hammer`/`HammerStone`; vanilla uses `hasEquippedTag(ItemType.HAMMER)`. The older check rejects other qualifying tools.
- Mod plays a hammering sound itself; vanilla relies on animation events for that sound.
- Mod `new(character,item,isMetal,isMetalBar,time)` requires a fifth argument. Vanilla `new(character,item,isMetal,isMetalBar)` calculates duration from the skill/material/Handy rules.
- Mod consumes the primary item's use three times for metal work in its old path; current vanilla has a different cost/completion split. Do not preserve the old cost by mechanically moving those calls into a new method.

**Reproduced:** calling the actual mod constructor with four arguments and a minimal normal character produces `maxTime=nil`; with Handy it raises `attempt to perform arithmetic on local 'time' (a nil value)` at mod line 158. Current installed action tests use the four-argument contract. This proves signature incompatibility, without asserting that every current UI barricade path uses this action.

The NPC caller is `BarricadeBuildingTask.lua:117`, which explicitly supplies `100` as a fifth argument. Restoring vanilla requires removing that duration assumption and accepting the current duration calculation. The result will change NPC barricading speed to the current game rules.

**Approach:** restore vanilla; update the task caller, current qualifying tools/material preparation and completion tracking. Validate wood, sheet metal and bars with insufficient materials, cancellation, Handy and normal players. Do not globally retain old action behavior to keep one task's hard-coded 100-tick duration.

### Disinfection: obsolete fluids and treatment lifecycle

[Mod file](../42/media/lua/client/TimedActions/ISDisinfect.lua), installed reference `media/lua/shared/TimedActions/ISDisinfect.lua`.

The visible customizations are a mod-specific translated job label and a manually chosen body-part animation variable. Those changes do not justify replacing all treatment behavior globally.

The copy loses current client item-ID resolution, animation `reportEvent` calls, treatment sounds and sound cleanup, `getDuration`, and the separate authoritative `complete` method. It uses old `Food` thirst/hunger changes or `DrainableComboItem:Use()` to consume alcohol. Current vanilla explicitly reads the fluid container's alcohol properties, adjusts its amount, uses `UseAndSync()` for drainables, and synchronizes body-part fields.

There is also a material logic difference in pain: the mod adds pain only when `getAccessLevel() ~= "None"`; vanilla uses the current multiplayer health-cheat condition. An access-level string is not a reliable substitute for health-cheat policy.

The mod calls `ISBaseTimedAction.perform(self)` **before** its treatment mutation, so queue advancement can precede the effect. This is another reason to retain current lifecycle ownership rather than copying the old method.

**Approach:** use vanilla with the existing four-argument doctor-task call. If an NPC animation fails, address only that startup/animation path in a namespaced action and preserve current completion/consumption semantics. Validate wipes, fluid alcohol, self/other patient, cancellation, ordinary pain and item consumption. DoctorTask's unlimited supply generation and patient selection are separate defects.

### Eating: old copy replaces current food behavior for everyone

[Mod file](../42/media/lua/client/TimedActions/ISEatFoodAction.lua), installed reference `media/lua/shared/TimedActions/ISEatFoodAction.lua`.

The copy is 184 lines versus 327 installed lines. Visible mod changes include translated Eat/Drink labels, different animation setup, a direct `Eat` in `perform`, and a nil-container guard. Historical intent cannot be proven from the present diff alone; much of the difference is simply an older vanilla baseline.

Current behavior missing from the copy includes:

- `isValidStart`'s food-eaten check and current client item lookup.
- Current smoking support for car lighters/open flames and appropriate required-item checks/consumption.
- `reportEvent("EventEating")`, current bowl/plate/can handling and utensil selection/benefits.
- Per-item eating time, separate `complete()` consumption, and current server cancellation handling.
- Current sound stop/trigger and scrape behavior.

The old copy sets job delta to zero in `stop()` and then uses that delta when applying partial eating. Current vanilla obtains cancellation progress via its server-stop path and network-action progress when available. Do not assume old cancellation gives equivalent partial consumption.

**Approach:** restore the current action and keep `EatFoodTask`'s three-argument call, then check the task's separate canned-food substitution behavior. Verify NPC eating and cancellation plus ordinary-player meals, utensils and smoking. A translation change should live in the relevant translation keys or a narrowly scoped display adaptation, not a global copy of the food action.

### Vehicle entry: deliberate workaround, excessive global scope

[Copy 1](../42/media/lua/client/Vehicles/TimedActions/ISEnterVehicle.lua), [copy 2](../42/media/lua/client/TimedActions/ISEnterVehicle.lua), installed reference `media/lua/client/Vehicles/TimedActions/ISEnterVehicle.lua`.

Both mod files contain the same 75-line implementation. The clear deliberate workaround is in `update`: the `EnterAnimationFinished` conditional is commented out, so every update clears the entry variables and calls `forceComplete()`. It makes entry finish without waiting for the expected animation state, globally for every actor using that class.

Relative to current vanilla it also omits:

- Clearing aim before starting.
- Drag/context-menu cleanup (which is observer/player-specific and may itself need care for standalone NPCs).
- Checking distance to the actual passenger outside position before entering.
- Vehicle-entry music event and current heavy-item dropping behavior.
- `ignoreHandsWounds` constructor setting.

`start()` immediately calls `vehicle:enter`; `stop()` exits the character, and `perform()` positions the character inside and triggers `OnEnterVehicle`. Bypassing the current startup checks has consequences beyond animation length.

**Approach:** first establish whether current vanilla still hangs for these NPC actors. If it does, use one `SS…EnterVehicle` subclass/action on the NPC follow path, with explicit distance/seat/door/heavy-item handling and a bounded animation fallback. Preserve vanilla for the real player. Do not keep two global copies or simply restore an infinite animation wait without checking the NPC case. Validate seat competition, locked doors, distance, cancellation, heavy items and player entry.

### Player stats UI: old admin panel is not an NPC adaptation

[Mod file](../42/media/lua/client/ISUI/PlayerStats/ISPlayerStatsUI.lua), installed reference `media/lua/client/ISUI/PlayerStats/ISPlayerStatsUI.lua`.

The old panel changes layout, dimensions and some labels, but also replaces current profession/trait/role handling, XP controls, modal signatures and event registration. For example, it uses `getProfession`/`setProfession`, `getTraits`/`TraitFactory`, and `setAccessLevel` where installed code uses current profession/character-trait/role APIs. It omits current trait XP-boost adjustments and newer controls, and passes older arguments to several vanilla modal constructors.

The mod's context menu at `SuperSurvivorsContextMenu.lua:1105` simply invokes `ISPlayerStatsUI.OnOpenPanel`. Installed vanilla already exposes that function and opens the current player panel. The copy's `OnOpenPanel` likewise uses `getPlayer()`, not the selected NPC; there is no NPC-targeting feature here that requires preserving the old global panel.

**Approach:** remove the copied panel and retain a menu entry that explicitly loads/calls the installed panel. If editing a selected NPC is wanted later, build a dedicated NPC inspector/editor with an explicit actor target. Do not bring back obsolete admin role/user-log controls for that purpose. Validate in-game opening and hot reload, since duplicate callback registrations from an already-loaded old panel are not automatically undone by deleting its source while the game runs.

## Method hooks, not whole-file replacements

### `TimedActions/ZOverrides.lua`: theft detection

This wraps `ISInventoryTransferAction.perform` and `ISGrabItemAction.perform`, saving the old functions in local tables and calling them afterward. Theft detection is an intended cross-cutting feature: the real player as well as NPCs can steal. Restricting the entire feature to NPCs would remove player theft detection.

The **method and timing are wrong for the current implementation**:

- Installed transfer/grab `perform()` processes `queueList` batches and can fail validation or skip an item. The wrapper evaluates only the current `self.item` **before** the original method processes the batch. It can report a failed attempt and does not reliably inspect every successfully transferred item.
- In `ISGrabItemAction`, `self.item` is a **world inventory object**, while transfer actions use an **inventory item**. The wrapper treats their mod data/source lookup uniformly. The `FreeToTake` exemption on an inventory item is not the same storage as the world object's mod data.
- The helper can fall back to the character's square rather than the actual item source. This can attribute ownership to the wrong group's territory.
- Every reload adds another wrapper; there is no registration/idempotence guard. Missing manager/target/container checks can prevent the original action from running.
- Per-action unconditional prints add noise on a high-frequency path.

**Approach:** preserve theft as a narrow global observation, but observe successful per-item ownership changes with a captured source/group and normalized inventory-item identity. Installed `ISInventoryTransferAction` exposes `setOnComplete` for actions the mod creates, but that is not a global per-item success event and does not cover all player grabs. For general player theft, inspect the current transfer/transaction boundary or a documented event before selecting a hook. Do not indiscriminately move these wrappers to `complete()`: **these two installed actions still perform their batch/transaction processing in `perform()` and do not define the same `complete` pattern as medical actions.** Network authority needs a separate design.

### `5_UI/SurvivorLocator.lua`: map markers

It saves and calls `ISWorldMap.render`, then draws survivor rectangles and names. Calling the original first is a legitimate narrow extension pattern; it is substantially less invasive than replacing the whole map class.

The problems are lifecycle and data: no reload guard, global player-0 state, assuming member 1 is the player, and dereferencing unloaded numeric members as `member.player`. Rendering also calls `get_group()`, which can create/change groups while drawing.

**Approach:** use supported marker/overlay APIs where suitable, or retain one guarded narrow wrapper. Resolve a read-only marker list outside rendering, handle loaded/unloaded members explicitly, and never mutate group membership from a draw callback. A global map extension is reasonable for this feature; a whole-file map replacement is unnecessary.

## Files that look like replacements but are not, in this installation

| File/resource | Verified classification | Port implication |
|---|---|---|
| `TimedActions/ISDropItemAction.lua` | No installed Lua file or class definition with this name. A custom helper, not a replacement of current vanilla. | Rename to a mod-prefixed action and migrate it to the current drop/transfer path. It directly adds/removes items and bypasses current transactions; absence of a collision does not make its behavior correct. |
| `TimedActions/ISNPCScavengeAction.lua` | Custom-named legacy scavenging action. | Old copied subsystem logic, but not a replacement of a current class with the same name. Requires a feature port. |
| `3_Other/SuperSurvivorUndressing.lua` | Defines custom `ISUnequipClothingAction`; no installed class definition with that name found. | Namespace and repair lifecycle; it calls `perform()` from `update` and queues a drop, rather than replacing the installed `ISUnequipAction`. |
| Custom hit/surrender actions | No matching installed filenames in the Lua inventory. | Custom actions; still review state cleanup and native hit ownership. |
| `media/AnimSets/player/actions/StaggerForward.xml`, `StaggerBackward.xml` | Neither exact relative path exists in the installed media tree. These add player action nodes keyed by custom `PerformingAction` values used by the custom hit actions. | Shared player action-set extensions, **not verified replacements of existing XML nodes**. Animation names/schema/loading still require validation. |
| `42/zombie/scripting/commands/Character/Attack.class` | Current JAR has neither this class nor entries under that legacy scripting-commands package. | Not a verified current engine-class replacement. A loose `.class` inside a mod is not evidence of JVM loading; do not rely on it as active combat behavior. |
| Six `shared/Translate/EN/*.json` files | Standard translation resource names also exist in vanilla. | Translation catalogs are not whole Lua-class replacements; inspect key collisions/merge semantics separately. Their common filename alone is not a reason to rename the resource files. |

This corrects the earlier broad guide's classification of `ISDropItemAction` and the two animation XML files. A familiar vanilla-style name/path is evidence to investigate, not proof that the current engine contains a matching file.

## Concrete implementation order

1. Remove redundant bandage/window-glass copies and replace direct-copy test dependencies; verify normal and NPC actions resolve to installed vanilla.
2. Restore current admin UI; keep/load the existing menu callback.
3. Restore barricading/disinfection/eating one at a time, adapting the NPC task's current signatures, costs and completion assumptions.
4. Replace duplicate vehicle-entry ownership with vanilla or one narrowly scoped NPC adaptation after reproducing whether the animation workaround is still needed.
5. Repair theft observation and map overlay independently, preserving their intended player-facing features.
6. Namespace/custom-port drop, unequip, scavenging and hit actions; investigate or retire the unused legacy Java asset based on actual loader evidence.

These are recommendations, not changes already deployed. Removing all copies at once would conceal which remaining failure is due to NPC actor identity, action lifecycle or an ordinary task bug. Each migration needs real-player and NPC validation because the old global replacements have affected both.

## Reproducible evidence

### Options helper follow-up — 2026-11-12

`SuperSurvivorOptions.lua` now requires vanilla `OptionScreens/GameOption`
instead of defining its own old GameOption/GameOptions copies. The current
helper supplies `storeCurrentValue`/`restoreOriginalValue`, which the options
lifecycle invokes. Each combo's `gameOption` is local, avoiding writes to the
global also used by vanilla and the resulting cross-file LuaLS duplicate-field
warnings for `toUI`, `apply`, and `onChange`. The `MainOptions:create` wrapper
remains intentional: it calls the previous implementation before adding the mod
page. Only that declaration has a documented, next-line `duplicate-set-field`
annotation. No workspace-wide diagnostic suppression was added.

Two tests use installed GameOption definitions to check page registration,
vanilla helper identity, current lifecycle calls, independent option callbacks,
Apply behavior, and preservation of the existing global `gameOption`.

The comparison enumerated every `.lua` file in `42/media/lua` against matching installed filenames, compared full normalized source, checked mod-to-game relative asset paths, searched installed class definitions, and examined the current JAR entries. Local detailed diffs are under `.venv/override-review/` and are disposable diagnostics. Durable conclusions and relevant source entry points are recorded above.

The barricade probe executes the actual mod constructor in Lua 5.1 with only `require`, the base `derive` operation, typed Handy constant and two character methods stubbed. It demonstrates the constructor's missing-duration behavior without a running game. The two redundant-action conclusions come from exact normalized text comparisons. No live action queue, multiplayer transaction or visual animation was exercised in this pass.
