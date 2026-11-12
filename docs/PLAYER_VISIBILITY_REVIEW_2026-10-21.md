# Player visibility: static review

User requested a pause in live debugging after the local-opacity guard failed.
No new runtime change was made or deployed during this review.

## Definite timing defect in the current guard

The guard in SuperSurvivorRender.render runs in RenderOpaqueObjectsInWorld.
The installed FBORenderCell.performRenderTiles invokes these methods in order
(bytecode offsets shown to make the finding reproducible):

| Offset | Method |
| --- | --- |
| 241 | renderPlayers(playerIndex) |
| 374 | renderOpaqueObjectsEvent(playerIndex) |
| 387 | renderMovingObjects() |

Thus the local player is drawn, or skipped at alpha zero, before our guard runs.
On the next simulation update, native LOS can set alpha zero again before the
next player draw. The guard can appear to work when tested in isolation and
still never make the actual player draw visible. An offline Lua reproduction
using the current callback and this order confirms that sequence over three
frames: draw sees zero, late callback writes one, next world update resets zero.
This is an explanatory reproduction, not a live Java writer trace.

The opaque event is also conditional: renderOpaqueObjectsEvent can return when
the picked tile is absent or invalid. It is suitable for the existing NPC render
submission but unsuitable for a general player-state repair.

## Native standalone-player assumptions

- spawnPlayer constructs an ordinary IsoPlayer, then setNpc(true).
- The installed setNpc adds AIComponent. It does not change playerIndex or remote.
- playerIndex defaults to zero; getIndex/getPlayerNum return that field. The SP
  constructor defaults remote=false. A standalone player shares viewport zero.
- updateInternal1 calls updateLOS after updateInternal2 returns true when remote
  is false. isNpc branches in updateInternal2 do not generally exclude that LOS
  call. updateRemotePlayer immediately returns false when remote is false.
- updateLOS iterates cell objects and writes target alpha using its playerIndex.
  It skips itself, but the real player is another object to this NPC.
- IsoGameCharacter.TestIfSeen returns false for observer==subject.
  updateSeenVisibility stores that result in isVisibleToPlayer[view] even for
  IsoPlayer, then skips its own alpha write for player subjects. updateLOS reads
  the shared visibility array and can fade other player subjects in that view.

This gives a concrete native interference path consistent with the captured
alpha/targetAlpha zero. Which precise native invocation last wrote the snapshot
was not instrumented. No active mod Lua directly writes alpha zero: the other
legacy visibility setters write one.

## Additional singleton coupling

IsoPlayer.updateInternal2 assigns `IsoPlayer.instance = this` on its non-remote
update path. IsoPlayer.update itself only wraps updateInternal1 with profiling;
it does not save/restore that singleton. The scheduler invokes player updates
through the ordinary moving-object path. The mod's speech code still calls
getPlayer(), whose global implementation returns IsoPlayer.getInstance(). Thus
an ordinary NPC player can influence which character those Lua calls address.
This is an architectural coupling to review, not an established second cause of
the captured disappearance. Other higher-level engine code may reset instance.
Prefer explicit observer/character references in mod logic where appropriate.

## Correction supported by the reviewed order

Move player-opacity ownership out of the opaque drawing callback. In this build,
IngameState.updateInternal invokes IsoWorld.update at offset1067 and onTick at
1331; onTick triggers OnTick. A dedicated OnTick compatibility callback therefore
runs after native NPC/world updates and before the subsequent player draw. It
must retain the narrow own-viewport scope, explicit visibility/death flags and
MP exclusion. On hot load, a one-time invocation can repair an already-paused
session without waiting for a simulation tick.

This corrects the guard's timing; it does not isolate all native NPC LOS effects
on other actors. A fuller native ownership solution should be reviewed before
claiming general NPC visibility/following/combat compatibility. Do not give NPCs
arbitrary viewport indices or mark them network-remote without auditing those
paths and their fixed-size per-player arrays.

## Validation gap

The current 59 tests verify callback behavior and filters but do not establish
engine event order. Future regression coverage must model world update, OnTick,
native player submission and opaque callback in that order, and check alpha at
the actual player-submission point. Purely checking alpha after our draw callback
would repeat the same testing mistake.

Live facts remain: stationary NPC now visible; local player later invisible with
intact mesh/texture, correct membership and explicit visibility flags false,
but alpha and targetAlpha zero. The startup/spawn milestone remains incomplete.

## Follow-up — 2026-11-12

The user reported the local character disappearing again. The latest console
contains no new render exception or current alpha snapshot. Rechecked the
installed JAR: the world-update/OnTick offsets remain 1067/1331, and native player
submission still precedes the opaque event at offsets 241/374.

Implemented the timing correction described above. NPC rendering remains in the
opaque event; local observer opacity is now restored by a separate OnTick
callback after world updates. It runs only in SP with a loaded living standalone
NPC and preserves explicit invisibility/render flags and death. Each local player
is written only in that player's own view. Hot reload removes both old callbacks
and invokes the correction once immediately, including while paused.

Regression tests now model native LOS fading the observer, OnTick, actual player
submission, and the later opaque event across successive frames. They also check
paused-session recovery, hot reload, flags, and scope. These tests establish the
Lua correction's ordering behavior, not the identity of the latest native alpha
writer. Live recovery remains to be confirmed; if invisibility persists, capture
the current player's state instead of assuming opacity is the only cause.

Subsequent configuration inspection found `Invisible=true` and `GodMod=true` in
`C:/Users/Enter/Zomboid/Lua/CheatPanel.ini`. This is the vanilla debug/admin
panel's saved configuration: `ISAdminPowerUI.onGameStart` reads it and calls
`setInvisible` for that option; the current log confirms the loader ran. This is
an additional concrete reason the old and new opacity guards may skip the
player. Saved Invisible was changed to false, preserving GodMod true; a backup
is under `.venv/CheatPanel-before-visibility-fix.ini`. The running character still
needs `getSpecificPlayer(0):setInvisible(false)` (or the corresponding debug UI
toggle), followed by hot reload of the render correction. Which cause dominates
the current disappearance remains unconfirmed until that live check.

The user confirmed that `setInvisible(false)` made the character visible and
reiterated that their protection mod is **Z'Ware Invincibility: Three Ways Out**.
Do not conflate that mod with vanilla God Mode or attribute the Invisible setting
to Z'Ware without evidence. The saved vanilla GodMod flag is an observed setting,
not a statement about which protection mechanism the user intended to use.

Important interpretation: clearing Invisible also enables our alpha-restoration
guard, which deliberately skips explicit invisibility. Recovery therefore does
not by itself prove that native single-player Invisible is intended to hide the
local model. The direct invisible-subject alpha-zero branch found in
IsoPlayer.updateLOS at offsets 409–432 is gated by GameClient.client; it must not
be presented as the explanation for this SP session. Standalone NPC viewport/LOS
ownership remains a separate, supported interference path. The precise native
writer responsible for the latest incident has not been captured.

## User decision — 2026-11-12

Defer further visibility-ownership investigation and continue other porting work.
The user accepts the remaining symptom for now and restarting as a recovery
option if needed. Keep this as a future exploration item, not a blocking
startup/spawn requirement. The current Lua correction remains in place; do not
describe the root ownership issue as resolved.

Java-side modifications are explicitly excluded. Future work is limited to
existing Lua-accessible engine controls or a documented Lua compatibility
workaround. Resume deeper investigation when the user requests it.
