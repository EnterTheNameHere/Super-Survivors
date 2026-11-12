# Live station result and clothing timing

## Observed result

The current console log records stationary NPC 10 at frame 2550, a manual
visibility PASS at frame 27934, and patrol A/B/A PASS at frame 28804. The user
also exercised inspection, medical information, conversation, gifting a keyring,
group membership and loadout controls during the stationary interval.

The exception at frame 28805 came from the following **inventory setup**, not
from walking: `SuperbSurvivorsTests.lua` raised “NPC cannot accept the fixture
item (check capacity).” That message conflated source ownership, capacity, range,
floor/wall and equipped-owner checks, so the log does not prove which condition
rejected this transfer.

The station now prepares its three fixture items, asks the user to stand adjacent,
and waits when the source/player is out of reach. Other ordinary rejections print
the actual reason as a failed station instead of a generic capacity exception.
Item definitions/constructor failures still surface as genuine errors.

## Clothing changes

The loadout previously called `setWornItem`/`setClothingItem_Back` directly to wear
items and passed duration 1 when removing them. It now uses the installed
`ISWearClothing` and `ISUnequipAction` for clothing/bags, with normal timing,
animation events and completion. Unequipping uses the same 50-unit duration
passed by the vanilla inventory context menu. The game adjusts action timing;
the UI displays actual percentage, not an invented seconds estimate.

While an action is queued/running, its loadout button displays Queued or progress
percentage plus Cancel. Clicking that button cancels the actor's native action
queue. Moving/running interruption follows vanilla clothing rules. Cancellation
does not manually change equipment; a completed action is not rolled back.
Panels refresh after actual equipped state changes, including after native
completion rather than merely when a command is clicked. NPC unequipping avoids
using the real player's hotbar animation. Nonwearable containers are rejected.

The bulk Remove Clothing command also uses native unequip/drop action queues,
replacing the old pseudo-action that directly performed from update inside the
AI task manager. Interrupting the queue cancels the remaining removals/drops.
Previously completed removals remain completed.

Immediate `WearThis` remains for spawn/load appearance initialization. Other
legacy paths, including gift auto-equipping, are not converted by this change.
Weapon equip commands retain their existing behavior. This is not a global
replacement of vanilla clothing actions.

## Validation and next run

106 tests pass with `PZ_GAME_DIR` set, including actual installed clothing-action
definitions under mocked game objects: no equipment change before completion,
wear progress, cancellation, normal unequip duration, duplicate/missing-item
rejection, nonwearable containers, the loadout progress/cancel control, and the
inventory station waiting for range. All 108 runtime Lua files compile. Actual
animation/progress display and the revised inventory station still need a live
check.

Restart PZ to load the changed UI/actions. To retry only the failed station in a
disposable world, without repeating the successful minute/patrol checks:

```lua
SuperbSurvivorsTests.start("inventory")
-- Stand beside the fixture and follow the printed prompts.
-- Restore normal spawning/AI after testing:
SuperbSurvivorsTests.endSession()
```

Three separate option-tooltip formatter warnings and missing vegetation tile
warnings also appear earlier in the log. They are not the station exception and
are not repaired by these changes.
