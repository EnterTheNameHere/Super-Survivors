# Rendering inspection — 2026-10-21

Latest review: local-opacity guard failed live. It runs after native player
submission, so its timing is wrong. Live debugging paused at user's request;
see [static code review](PLAYER_VISIBILITY_REVIEW_2026-10-21.md) for verified
ordering, native standalone-player assumptions and the proposed correction.
No additional runtime change was deployed during that review.

## Local-player snapshot: alpha is zero, assets remain valid

Frame15090 inspect(0): localPlayer=true, npc=false, inCell/onSquare true,
sceneCulled/invisible/spriteInvisible false, active registered model, idle,
valid matching render square, zero offsets and true square visibility. Both
alpha and targetAlpha are 0. At15809 both NPC and observer have valid meshes,
skinning, scale1, three animation tracks and CharacterSmartTexture. This rules
out a missing player mesh/texture in this snapshot.

Installed IsoPlayer.updateInternal1 calls updateLOS after updateInternal2 when
the old remote field is false. updateLOS uses its playerIndex to write other
objects' target alpha based on visibility. Standalone SP players default to
playerIndex0 and remote=false. Their native LOS therefore shares viewport0 with
the real observer. This is the identified interference path; no dynamic Java
write trace was captured to prove which specific update wrote the observed zero.

The SP render adapter now restores alpha/targetAlpha only on the living local
observer in its own viewport when a non-local managed player is loaded. It
preserves explicit invisible/spriteInvisible/doRender flags and death fading;
it does not alter any NPC/zombie alpha or global square visibility. This is a
compatibility guard, not a port of native NPC LOS ownership. Root isolation of
native NPC observer updates may eventually require a Java-side bridge.
59 tests and110 syntax checks pass; regression coverage includes offscreen NPCs,
no loaded NPC, MP exclusion and explicit player visibility/death flags. Hot-reload
the renderer while the current player is invisible and recheck beyond a minute.
The local-player fix still needs live validation.

## Live bridge result: NPC visible, local-player regression reported

After restarting with the bridge, user confirms stationary NPC visibility for
the first time. Probe4 spawned at frame464 at10696,9383,0. User then reports the
local character disappears after a few dozen seconds. Current log runs through
10826 without a new Lua exception (the frame0 UIManager.update exceptions remain).
This report does not establish the player's alpha, model state or cell membership,
or that the bridge caused the disappearance. No speculative visibility override
was added. Requested `SuperbSurvivorsDebug.inspect(0)` and `compareModels()` while
the player is invisible to distinguish those conditions. NPC spawn/presence
milestone remains incomplete until the local player stays visible too.

## Model comparison identifies renderer omission

At frame34679 probe9 has FemaleBody.x mesh/VBO/skinning, scale1, white tint,
three animation tracks with the correct model and firstFramePending=false.
Its texture is nil; observer has a CharacterSmartTexture. NPC has one submodel
versus observer six, and neither has a pending texture creator. Core's display
player model flag is true. Both are isLocal=true (different from isLocalPlayer).

Further installed-JAR inspection finds a concrete render-list mismatch:
`FBORenderCell.renderMovingObject` returns immediately when getClass() is exactly
IsoPlayer. `renderPlayers` visits only IsoPlayer.players[0..numPlayers-1] in SP,
or GameClient.IDToPlayerMap in MP. Standalone NPC IsoPlayers are in neither pass.
`IsoGameCharacter.checkUpdateModelTextures` runs in render(), so the absent
texture can be a consequence of this omitted render call. ResetModel alone
cannot repair render-list eligibility.

Added client/3_Other/SuperSurvivorRender.lua: submit managed non-local, living SP
survivors during RenderOpaqueObjectsInWorld, the same event used by vanilla
Fishing/Bobber.lua and ISBuildingObject.lua. The call matches the native player
pass's render signature and uses square:getLightInfo(playerIndex); no alpha,
invisibility, texture or reflection writes. Skip unloaded/off-screen/hidden squares
and floors above the observer to avoid drawing collapsed upper storeys. MP is
explicitly excluded. This is a narrow SP bridge; upper-floor cutaway behavior,
shadows and world depth/occlusion still need live validation. Native local players
are excluded to avoid duplicate submission. Reload removes its prior callback.

57 tests and 110 syntax checks pass. Tests cover engine render arguments,
visibility/load/local-player/floor/MP filters and hot-reload idempotence. Actual
in-game visibility after the bridge is pending. Load into the current game:

```lua
reloadLuaFile("media/lua/client/3_Other/SuperSurvivorRender.lua")
```

## Restarted run: reset does not restore visibility

User confirms no NPCs are visible, including stationary probe 9. Spawn at frame
27604: 10808,9439,0. Two resetModel requests at 29878 and 30862 were followed by
successful captures at 29998 and 30982. Model/animation/render-square membership
remained present, alpha/targetAlpha 1, observerCanSee/squareVisible true, doRender
true, idle state, offsets zero. Observer was about 1.8 tiles away. NPC appearance
was FemaleBody05/CentreParting. Reset is therefore not an observed remedy.

Added debug-only `compareModels()` to compare the existing NPC with player 0.
It reads ModelInstance, mesh, animation, texture and slot fields via the vanilla
ObjectViewer reflection globals getNumClassFields/getClassField/getClassFieldVal.
The local JAR confirms these globals are debug gated, enumerate declared fields
and read them without mutation. No methods are invoked on unexposed model or
animation handles. Missing/nil declared fields are reported as nil; they do not
prove an asset failure by themselves. It also logs Core.isDisplayPlayerModel and
character isLocal, plus the character's exposed getAnimationDebug string.
54 tests and 109 syntax checks pass, including an opaque-handle regression test.
Actual reflected model data is pending. No production render changes were made.

```lua
reloadLuaFile("media/lua/client/Debug/SuperbSurvivorsDebug.lua")
SuperbSurvivorsDebug.compareModels()
```

## Deferred inspection and model reset experiment

Frame 9637 captured survivor 6 after the simulation advanced. It remained near
the observer (10731.775,9981.686,0 vs 10734.356,9981.531,0), with waitTicks 35802.
doRender=true, hasAnimationPlayer=true, animationState=idle,
characterState=IdleState, hasRenderSquare/renderSquareMatches=true and all three
render offsets zero. Alpha/targetAlpha stayed 1; both visibility checks stayed
true. Model and membership checks stayed positive. No ordinary render gate is
identified by these getters.

Added explicit `resetModelProbe()` to call the existing NPC's engine resetModel
and schedule another inspection after 120 simulation ticks. This is an experiment
to distinguish stale model initialization from another render problem, not a
claimed invisibility fix. No production spawn change or visibility override.

The later recurring error at AttemptEntryIntoBuildingTask.lua:200 came from the
bundled client TimedActions/ISRemoveBrokenGlass.lua overriding installed B42 Lua.
Its B41 constructor required `time`, leaving maxTime nil with the B42 two-argument
call. Ported that bundled action to the installed B42 implementation: base
constructor, duration 100 (1 for instant actions), EventLootItem, radius 6 sound,
world mutation in complete() and server sync. Added a regression using the actual
installed ISBaseTimedAction.adjustMaxTime. 49 tests and 109 syntax checks pass.

## Stationary probe follow-up

The user confirms survivor 6 remains invisible. At frame 5678 it was at
10731.5,9981.5,0, while the observer was at 10730.594,9981.444,0. Both alpha values
were 1; observerCanSee and squareVisible were true. Model registered/active/instance,
visual, cell membership and square membership were all present. Invisible,
spriteInvisible and sceneCulled were false. Skin was FemaleBody04, hair Braids.
This narrows the issue beyond ordinary line-of-sight alpha, but does not prove
the model mesh/animation is ready. Spawn and inspection share the same frame,
and waitTicks remained 36000, so subsequent simulation is not established by
this snapshot.

Extended the read-only inspection with verified local-JAR APIs: getDoRender,
animation presence/state, render square and offsets.
`inspectAfterTicks()` replaces any pending capture and records after 120 actual
OnTick callbacks. Reload the debug module, run this command on the existing probe,
then close the console and unpause for several seconds. No rendering flags change.
47 tests and 109 syntax checks pass; the invisibility cause remains unresolved.

The first deferred capture reached frame 8647 (120 ticks after scheduling at
8527), then failed at `animation:getModel()`: `attempted index: getModel of
non-table: zombie.core.skinnedmodel.animation.AnimationPlayer`. Public Java
methods do not imply Lua exposure. The installed LuaManager.Exposer explicitly
exposes IsoGameCharacter and IsoObject, but not AnimationPlayer. Removed every
call through that opaque handle, including readiness and track-count queries;
use `npc:hasAnimationPlayer()` instead. The regression test now rejects access
to getAnimationPlayer. 47 tests and 109 syntax checks pass after correction.

```lua
reloadLuaFile("media/lua/client/Debug/SuperbSurvivorsDebug.lua")
SuperbSurvivorsDebug.inspectAfterTicks()
```

The inspected survivor has an active model, registered cell/square membership,
and neither invisibility flag set. Alpha and target alpha were zero, but both
observer line-of-sight and square visibility were false. It had moved roughly
eight tiles from the observer. This does not yet distinguish normal occlusion
from a visibility-update bug. The compound console hold command subsequently
spawned survivor 5, then failed in the console with a table-call error. A new
single-call `SuperbSurvivorsDebug.spawnStationary()` selects a visible free
adjacent tile and calls the existing stop/wait methods before returning. It
changes no rendering flags. Use that probe for the pending comparison, then run
`SuperbSurvivorsDebug.inspect()` after a few frames. The debug module preserves
the latest probe ID across reloads. Invisibility remains unresolved.

```text
LOG  : Lua          f:1793> [SuperbSurvivors] Render inspection for survivor 4
LOG  : Lua          f:1793> [SuperbSurvivors] render.id=4
LOG  : Lua          f:1793> [SuperbSurvivors] render.x=10725.9794921875
LOG  : Lua          f:1793> [SuperbSurvivors] render.y=9992.5
LOG  : Lua          f:1793> [SuperbSurvivors] render.z=0
LOG  : Lua          f:1793> [SuperbSurvivors] render.npc=true
LOG  : Lua          f:1793> [SuperbSurvivors] render.localPlayer=false
LOG  : Lua          f:1793> [SuperbSurvivors] render.invisible=false
LOG  : Lua          f:1793> [SuperbSurvivors] render.spriteInvisible=false
LOG  : Lua          f:1793> [SuperbSurvivors] render.sceneCulled=false
LOG  : Lua          f:1793> [SuperbSurvivors] render.modelRegistered=true
LOG  : Lua          f:1793> [SuperbSurvivors] render.modelActive=true
LOG  : Lua          f:1793> [SuperbSurvivors] render.modelInstance=true
LOG  : Lua          f:1793> [SuperbSurvivors] render.alpha=0
LOG  : Lua          f:1793> [SuperbSurvivors] render.targetAlpha=0
LOG  : Lua          f:1793> [SuperbSurvivors] render.inCell=true
LOG  : Lua          f:1793> [SuperbSurvivors] render.onSquare=true
LOG  : Lua          f:1793> [SuperbSurvivors] render.hasSquare=true
LOG  : Lua          f:1793> [SuperbSurvivors] render.hasVisual=true
LOG  : Lua          f:1793> [SuperbSurvivors] render.skinTexture=MaleBody01
LOG  : Lua          f:1793> [SuperbSurvivors] render.hair=PonyTail
LOG  : Lua          f:1793> [SuperbSurvivors] render.observerX=10718.5
LOG  : Lua          f:1793> [SuperbSurvivors] render.observerY=9989.5
LOG  : Lua          f:1793> [SuperbSurvivors] render.observerZ=0
LOG  : Lua          f:1793> [SuperbSurvivors] render.observerCanSee=false
LOG  : Lua          f:1793> [SuperbSurvivors] render.squareVisible=false
```
