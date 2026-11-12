# Interaction observations — 12 November 2026

User is continuing live tests. This pass traced the behavior without changing
runtime menus or interrupting the current game session.

Subsequent UI request implemented: allied group members' named right-click
submenu now includes Inventory and Equipment. Each panel has a footer button
to switch to the other panel, resolving the same survivor ID rather than relying
on a stale group-list index. Opening either panel no longer requires the main
Superb Survivors window; panel placement falls back to the screen and is clamped.
Switching closes the previous panel only after opening its replacement. Call
Over and Medical Check behaviors described below are unchanged. 109 tests and
109 Lua syntax checks pass; the new navigation has not yet been validated live.

## Call Over

`CallSurvivor` in `5_UI/SuperSurvivorsContextMenu.lua` queues `ListenTask` aimed
at player 0. The task should walk the NPC within 1.8 tiles, face the caller,
greet/respond and listen. Its idle counter, danger and following requirements
can end the interaction. This is a normal mod command, not a test-only command.

The menu deliberately omits Call Over while the current task is Listen (or the
survivor is hostile/sees danger). Therefore disappearance immediately after
calling is expected from the current implementation, rather than evidence that
the command was removed permanently.

The stationary development fixture has a long WaitTicks pause. Calling it still
constructs/queues Listen and plays its initial response, but its task update is
paused. That can leave Call Over hidden while the NPC never approaches. Do not
infer normal NPC call behavior from a paused stationary fixture. The test runner
clears fixture tasks before subsequent stations.

## Medical check entry points

The mod adds a named-survivor submenu and its Medical Check entry. Its
`MedicalCheckSurvivor` explicitly queues walking the real player adjacent to the
NPC followed by the installed `ISMedicalCheckAction`.

The red “too far away” blocking message is implemented in vanilla ISHealthPanel.
Its distance guard blocks medical data/actions outside the allowed examiner /
patient range. Other entry points can expose that window without the mod's
walk-first behavior. The origin of the separate top-level entry was not proven
from the observed UI; it must not automatically be attributed to this mod.

Installed `ISWorldObjectContextMenu.onMedicalCheck` uses the vanilla request
flow; `ISHealthPanel.canPerformMedicalCheck(target, requester)` currently attempts
`luautils.walkAdj(target, requester:getCurrentSquare())`, which differs from the
mod's explicit examiner-walks-to-patient flow. These should not be merged merely
because their displayed labels match.

## Follow-up candidates

- Keep a visible listening/status indication instead of silently hiding Call Over.
- Warn that stationary fixture AI is paused when testing a movement-based command.
- Label the walk-first NPC medical option clearly, such as “Walk over and examine”.
- Identify the other menu entry's owner before removing or overriding it.

The latest console tail at inspection contains the current stationary fixture
startup and the already-known option-tooltip formatter warnings, with no new
interaction exception in that tail. This is not a claim that all ongoing tests
have completed or that all logs were error-free.

## Subsequent station run

Later results: the retried doctor station passed at frame 41605, with positive
alcohol level and bandages 1 -> 0. The old separate bulk Remove Clothing menu
then reached `ISDropItemAction.perform` and failed at its obsolete
`ISInventoryTransferAction.GetDropItemOffset` call (frame 44383, repeated 45564).

Removed the unreferenced `SuperSurvivorUndressing.lua` menu hook/bulk action and
its two menu translations; individual timed equipment control remains in the
Equipment panel. Repaired the shared drop action to use the installed
`ISTransferAction.GetDropItemOffset`, with invalid-item/square guards so other
drop callers do not retain the same failure. 114 tests pass; all 108 remaining
runtime Lua files compile. A restart clears the deleted menu handler and any
old queued undressing actions already loaded in the game.

The next log inspection confirms inventory PASS at frame 38935 (all three item
identities transferred once), and self-bandaging PASS at frame 39338 (one sheet
consumed). Doctor setup failed at frame 39339 because the new patient was placed
beside the human observer rather than the doctor, then rejected for distance.
This was a fixture-placement defect, before native doctor treatment ran.

The runner now places new patients near the doctor and permits DoctorTask to
approach existing/distant patients. Progress steps are monotonic, avoiding
repeated approach/treatment messages after completion. 111 tests pass and all
109 Lua files compile. Only the debug runner changed at runtime in this fix,
so it can be reloaded and the doctor station retried without a full restart.
