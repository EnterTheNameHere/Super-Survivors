# LuaLS need-check-nil review — 2026-11-12

Reviewed the current runtime Lua with the installed Lua Language Server, vanilla
Lua libraries and native editor definitions. There were **69 distinct reported
locations**; repeated copies of the same diagnostic were counted once. The
refreshed scan reports **zero need-check-nil diagnostics**. The rule remains
enabled, and nullable API declarations were not weakened to silence warnings.

## Changes

- `SuperSurvivorPanels.contextMenu` checks for player UI data before calling the
  vanilla context-menu factory, which dereferences that data internally. Debug
  and survivor-window menu callers check its result before adding entries.
  Missing context menus accounted for most of the repeated reports.
- Survivor startup and player-creation callbacks return before using an
  unavailable local player. The latter also checks the main survivor's group
  before registering an additional local player.
- The prison-start key branch checks the building definition, destination tile,
  and created key. It removes the key from inventory only after world placement
  succeeds; unavailable world data cannot cause a nil access or lost key.
- Inventory transfer clicks return before reading a missing player's position or
  inventory. Quest conditions requiring a player wait when that player is
  unavailable; independent NPC/event conditions retain their behavior.
- Both active AI threat branches check that the seen character has a registered
  survivor wrapper before reading its player. A native IsoPlayer alone does not
  guarantee a matching mod wrapper.
- The old key-0 debug branch checks its cached attacker before dereferencing it.
  The old information-window compatibility probe checks the player exists.
- Weapon setup checks the result of the second ammo-type lookup before indexing
  it. The existing `FindAndReturnCount(nil)` contract returns zero, so a missing
  second lookup now produces zero ammo rather than an indexing error.
- Three entity scans now explicitly check the scanned list at the final lookup.
  These were flow-analysis limitations: the selected index was only assigned
  inside the nonnil-list branch. Selection behavior is unchanged.

## Validation and limits

All **135 tests pass**, and all **108 runtime Lua files compile**. Added checks
exercise absent startup/player objects, missing player UI context, both inventory
transfer directions without a player, unavailable ammo mappings, and quest
conditions with and without a player. Existing valid menu/quest paths are also
checked. Visibility ownership remains deferred as requested; this review does not
change that compatibility code.

These diagnostics only cover values LuaLS can infer as nullable. Zero reports
does not establish that every engine lookup, unloaded object, or asynchronous
action is safe. No live game test was performed for this pass.
