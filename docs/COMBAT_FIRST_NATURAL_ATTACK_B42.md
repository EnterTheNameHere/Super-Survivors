# Combat05: earliest natural attack observation

2026-11-17 implementation; runtime guard correction 2026-11-18. Native start/guarded teardown observed twice; execution after the correction **PENDING**. This does not fix combat, initiate an attack or establish a native NPC damage route. Prior source analysis: COMBAT_B42_CORRECTION_OPTIONS_04.md.

## Runtime follow-up, 18 November

Two observations of survivor ID 5 started at frames 14268/15209 and stopped on the next frame with “Human/control actor cannot be inspected as an NPC.” Both began started=false/initiate=false, weapon Base.SpearScrewdriver, ready=true, target present but native range=false; tasks Follow then Attack. Both report zero requests/StopWalks/events/transitions and both hooks restored. Evidence: docs/evidence/COMBAT_FIRST_ATTACK_2026-11-18.log with source console SHA256. No Lua exception occurred in these attempts; they did not reach a natural request.

The old ownership guard treated IsoPlayer.getInstance as a stable human identity. Installed IsoPlayer.updateInternal2 assigns instance=this for the actor being updated immediately before OnPlayerUpdate, including standalone SP NPCs. The early observation therefore rejects its own selected actor. The guard now uses SSR MainPlayer ID, all actual local-player slots, isLocalPlayer and registry/actor ownership. The first observer still freezes MainPlayer and all four local slots, but no longer requires an engine-owned update singleton to remain constant. Nothing reads/writes or restores that singleton in the corrected guard. Shared snapshot/general-trace availability benefits from the same correction. Human actors remain excluded. Restart to load this fix and repeat the same explicit observation; original first combat cause is still unobserved.

## Use

1. **Restart the game to load the update.** Enable the mod's Debug Options. Native `-debug` is not required by this diagnostic. Existing single-player, one living human and installed B42.22.2 guards apply.
2. Open an existing survivor's **Information → Diagnostics → Start earliest natural attack observation (up to 10s)**. Both survivor Information interfaces use the same action. Keep that Information window visible while observing the survivor's normal behavior.
3. The selection must be a loaded, living, NPC-controlled actor outside every human player slot, with attackStarted=false, initiateAttack=false and no known active swing/attack animation. Already-started actors are rejected with a reason in the Diagnostics button tooltip. Choose another eligible existing actor; this action never resets flags or spawns a replacement.
4. Let normal AI run. There is no setup step to issue an attack, move actors, give weapons or change targets. The observer finishes after the first accepted natural request plus three simulation ticks, or after an owned swing/hitpoint event plus the same short follow-up, subject to all hard caps below.
5. **Stop earliest attack observation**, close/hide Information, or wait for completion. The button changes to “observation logged”; its tooltip gives the termination reason. Logs are in console.txt under **`[SS Combat][first-natural-attack]`**. Report that the observation ran and what you saw; do not infer successful damage from the logging alone.

If there is no eligible actor or no request during the window, report that result. No disposable-world fixture is included. “Log combat state” and the existing general “Start combat trace” remain available; only one of the two observers can run at once. The new observer is not an SS Tests scenario and does not require destructive-test consent or alter that consent/state.

## What it records

- START: exact SSR ID, limits and instructions. Always **earliest OBSERVED only**: current registry metadata does not prove a never-attacked history. False initial flags are not first-ever provenance; no new persistent marker is written.
- INITIAL, natural REQUEST and STOPWALK entry/post, EARLY OnPlayerUpdate, OnTick and owned swing/hitpoint events. Each line includes timestamp and native frame when available. Request lines include return count, first result and reason, preserving trailing nils in the actual call result. StopWalk records include nesting depth, distinguishing the StopWalk inside a request from a later cancellation.
- Started/initiation/attack/shove animation, current state and Swipe identity, aiming/running/block movement, native weapon readiness, equipped weapon type, cached task/target reference, native range, current target position and cached wait/cooldown.
- Ordinary samples log only meaningful state or target-identity changes. Position and timer changes alone do not spend the pre-request log budget; their latest values appear in the next state/call record. There is no periodic repeating heartbeat.
- Sampled false→true transitions are explicitly labeled **not an exact native setter observation**. No getter is used to consume attack vars, initialize an animation/model, refresh perception or run a task. Installed native isWeaponReady reads cached hand models/current action; IsAttackRange reads held weapon/range/positions. Both were reviewed in the installed class. Missing getters log UNAVAILABLE rather than guessed data.
- END: reason, request/StopWalk/accepted/swing/hitpoint/sample-rise counts and individual owned-hook restoration results. Final result is INCONCLUSIVE as to first-ever setter, root cause and attributable damage.

## Ownership and behavior preservation

SSRCombatFirstAttack installs only two temporary raw method slots on the selected Lua wrapper: requestCombatAttack and StopWalk. It retains each resolved original and raw prior value (including nil for inherited functions), invokes the original exactly once with unchanged receiver/arguments, and returns all original results with their count. Other receivers pass through without observation.

The production invocation is direct, **not protected with pcall or caught/rethrown**. Kahlua's native error/stack/Throwable behavior differs from desktop Lua. An original error escapes through the observer frame unchanged; a nonzero in-flight depth triggers owned cleanup at the next tick/render callback. Observer-only errors are caught and stop observation; they do not replace a natural call's result. The reviewed production calls are synchronous; coroutine/yield interception is not supported.

ID, wrapper, actor, world, cell and Information binding are frozen. The actor and loaded registry/square ownership are revalidated at callbacks and natural call boundaries. MainPlayer and all four local-player slots must remain identical to their start values. The observer never sets them or the native singleton. B42's changing per-actor singleton is not a human-identity guard. Closing another Information window cannot stop this window's observation; stale menu callbacks cannot start on a different binding.

Caps: **10 real seconds / 600 simulation ticks / 120 log lines / eight natural request entries, first reached wins**. The line cap reserves two terminal lines. A capped interval is labeled censored. StopWalks share the line/time cap. Nested request calls also obey the eight-entry observation cap; natural calls still run after interception detaches. Three-tick follow-up never overrides a hard cap and does not wait indefinitely while paused: the render watchdog enforces the deadline.

Stop/hide/close/rebind, death/unload/replacement, local/control changes, debug disabled, menu/new session, reload, limits, method replacement, setup failure and observer failure detach callbacks and hooks. Cleanup restores only a still-owned raw slot; an outside replacement is retained. If engine callbacks stop entirely, teardown occurs on the first resumed callback. There is no startup capture, auto-rearm, world/save write, AI queue change, native setter hook or Java modification. Only one active record and one latest bounded in-memory result are retained.

## Interpretation limits

OnPlayerUpdate is an early native boundary before AIComponent.postUpdatePlayer in this build. Event listener order does not make it an exact setter interceptor. Native animation post-update can be skipped/threaded; OnTick samples do not claim a universal ordering after animation completion. A request returning true means SSR's immediate native flags indicated acceptance, not that animation or hit processing succeeded.

An immediate true initiation followed by false initiation/true started and no swing narrows the loss interval. A recorded later StopWalk may identify a Lua cancellation; absence does not prove AIComponent was the sole writer. OnWeaponSwing means swing-state entry. OnWeaponSwingHitPoint means native collision routine entry, **not a hit or damage**. Three follow-up ticks may not span a slow animation; absence within that short interval is not proof no later swing/hit occurs. Limits, missing APIs and stopped captures must stay explicit.

The independently identified ordinary SwipeStatePlayer nonlocal collision gate remains. This diagnostic does not bypass it, invoke Hit, force state/animation, reset flags, toggle NPC controls, change player slots or implement inventory/AI corrections. ZWare Invincibility remains part of the user's setup; no interaction or causal claim is established by these mocks or this implementation.

## Validation

The intended staged source was exported to an isolated ignored checkout (without unrelated user changes/saves). With PZ_GAME_DIR pointing to the installed game, **291 unit/regression tests passed after the runtime guard correction**, including installed-Lua constructor/action checks; **117/117 Lua 5.1 syntax checks passed**. Initial delivery LuaLS reported the same 88 pre-existing warnings in 13 files, with none in the changed diagnostics; it was not rerun for the narrow guard correction. No engine execution is implied by running installed Lua under mocks.

New regression coverage includes both exact-once originals/foreign receivers/trailing nils, unchanged string/object errors, nested StopWalk and requests, sampled transition labels, three-tick completion, time/tick/line/request caps, unchanged moving-target samples, setup/observer errors, stale actor/world/slot/NPC guards, external replacements, legacy observer exclusion, reload and UI close/hide/rebind/two-window/menu actions. Read-only traps forbid gameplay/model/AI/persistence calls. Native UI rendering, Kahlua error behavior and real first-request chronology require user verification.
