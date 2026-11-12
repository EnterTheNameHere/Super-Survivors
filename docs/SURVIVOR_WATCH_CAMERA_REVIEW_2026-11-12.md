# Survivor watch camera review — 12 November 2026

Camera following remains unfinished. The user confirmed that both attempted
implementations left the camera on the human character. State monitoring works
independently; the debug helper now reports its monitor-only behavior explicitly
and no longer writes camera state.

## Installed native render order

Read-only inspection of the installed B42.22.2 projectzomboid.jar found:

1. GameWindow.logic calls GameStateMachine.update, including world OnTick,
   then IsoCamera.updateAll. That update restores the real player camera.
2. GameWindow.frameStep calls logic, then renderInternal, then onRender.
   onRender emits OnRenderTick, so that event is too late for the world draw.
3. IngameState.renderInternal selects IsoPlayer.players[n] as camera character,
   calls Core.StartFrame, then snapshots IsoCamera.frameState and draws the world.
4. Core.StartFrame constructs the view/projection from the selected character's
   coordinates. Changing a camera target in an earlier Lua callback is therefore
   overwritten before view construction.

The earlier test established only that OnRenderTick followed the update reset.
It omitted renderInternal and incorrectly treated the event as a pre-draw hook.
The corrected native-order regression checks that rendering precedes onRender.
The monitor tests check that polling does not write camera state or register a
render camera callback. These tests do not establish camera-follow capability.

## Scope and remaining question

No usable camera-only Lua hook was found around native frame setup in the APIs
checked. This is not proof that every possible Lua approach is impossible.
OnPreRender/OnRenderUpdate names in an event registry alone do not establish that
the renderer emits them. The inspected UI and post-render hooks run too late.

PlayerCamera and IsoCamera.FrameState were not present in the inspected Lua
exposure whitelist. A native dummy-camera candidate was rejected by the camera
setter. None of those candidates supplies a verified solution.

The game JAR was not modified. Java-side changes are excluded by the user.
Swapping local-player slots or possessing the NPC was not implemented. Future
Lua-only camera feasibility work must establish a real rendering hook before
claiming success. This is separate from the deferred NPC/player visibility work.

## Current usable behavior

SuperbSurvivorsWatch.list/start/status/stop provide a loaded-survivor state
monitor: tasks, AI mode, role, health, danger, position and wait ticks. Starting
returns true with the reason monitor_only; snapshots contain cameraFollow=false.
The overlay and console explicitly say camera following is unavailable. Death,
unload and world changes stop the monitor. Debug code is excluded from releases.
