# Local Codex handoff

Repository: `EnterTheNameHere/Super-Survivors`, branch `B42`.

## Latest direction: design only (12 November 2026)

**The user explicitly stopped implementation: we are designing.** The current
request is to consolidate the discussion into documentation, not to build the
new AI or debug UI. Do not treat the proposed roadmap as implementation approval.

Start with [BEHAVIOUR_DESIGN.md](BEHAVIOUR_DESIGN.md), the consolidated design:

- Gradually replace decision rules with prioritized persistent goals, coordinated
  responses and cancellable actions; preserve useful working task code.
- Interrupt work for threats and resume valid unfinished work afterward.
- Independent facing/travel, aimed melee backstepping, sidesteps into clear space,
  surrounding-threat checks and safe escape routes; prove Lua NPC feasibility.
- Weapon reach/recovery/noise, skill, injuries and endurance inform risk; include
  native shoves/stomps and retain an escape reserve.
- Sound/alarm awareness with uncertainty, cautious room-by-room exploration and
  willingness to skip a building; avoid a complex police-clearing simulation.
- Proposed 2–4-slot attention budget affected by traits/panic/skill, without
  disabling basic survival reactions or making concurrent movement/attack impossible.
- Sit/rest safely for endurance, distinguish sleep/fatigue, and restore suppressed
  needs only alongside actual food/medicine/smoking/recovery responses.
- Enable SS Debug in normal options without -debug for supported Lua tools;
  main-window/context controls for AI/task-queue monitoring and survivor location,
  separate from state-changing cheats. Reuse DebugOptions; no code changed for it.
- Normal releases should include supported mod-debug tools, while disposable
  scenarios remain development-only. The current packaging excludes all Debug
  code, so this is an intended change, not current release behavior.

[CORE_BEHAVIOUR_REVIEW_2026-11-12.md](CORE_BEHAVIOUR_REVIEW_2026-11-12.md) records
the current task/AI behavior and identified defects. They have not been repaired
as part of the design discussion. Current danger handling is spread between AI
rules and tasks; interruption does not invoke cancellation cleanup. There are
separate mod-task and native timed-action queues to coordinate.

Existing watch monitoring/navigation works in the development helper; camera
following remains unfinished. See
[SURVIVOR_WATCH_CAMERA_REVIEW_2026-11-12.md](SURVIVOR_WATCH_CAMERA_REVIEW_2026-11-12.md).
Java modifications are excluded, and player-slot swapping is not an accepted
camera solution. General visibility root-cause work remains deferred. Historical
status paragraphs below are dated snapshots, not the latest design direction.

Session preferences: never apologize; when changes require a restart, say directly
to restart the game to load them. User uses Z'Ware Invincibility: Three Ways Out;
do not equate it with vanilla god mode.

## Local installation: linked checkout (10 November 2026)

The local game installation now uses directory junctions:

- `C:\Users\Enter\Zomboid\mods\SuperbSurvivors\42` points to `W:\Projects\Super-Survivors\42`.
- `C:\Users\Enter\Zomboid\mods\SuperbSurvivors\common` points to `W:\Projects\Super-Survivors\common`.

Do not run the historical copy/deployment commands below: the game paths now
refer to the source files themselves. Edit the repository and restart the game
to reload cached content (or deliberately reload individual Lua modules when
appropriate). Keep the W: checkout available while playing.

The previous standalone mod copy is preserved outside the scanned mods folder:
`C:\Users\Enter\Zomboid\mod-backups\SuperbSurvivors-before-link-20261110-000428`.
Both junction targets and hashes of linked mod.info/common asset were verified.
Current repository metadata is `Super Survivors Reloaded`, ID `Super-Survivors`;
the directory name remains SuperbSurvivors. Enable the repository's current mod
entry when selecting mods for a world; old copy metadata used ID SuperbSurvivors.

## Current state

12 November survivor watch: state/task monitoring is available through
SuperbSurvivorsWatch, but camera following remains UNIMPLEMENTED after two live
failures. Removed ineffective camera writes and corrected the UI/docs. Native
frame setup restores the real player before building the view; OnRenderTick
runs AFTER world rendering. The previous timing claim/test was incomplete.
See SURVIVOR_WATCH_CAMERA_REVIEW_2026-11-12.md. Future Lua-only camera feasibility
work is separate from the deferred general visibility issue. User excludes Java
modifications and prefers a direct restart instruction when required.


Next10 November save error: getGameMode now returns GameMode, so string
concatenation in getSaveDir failed. Both client/shared helper definitions now
use :toString(), matching vanilla.69 tests,110 syntax checks pass; linked source
needs no copying. Restart/live validation pending. Also logged: undefined
Subpar.StrangeMeat in old death-loot hook, separately unresolved.

10 November autosave fix: game is now42.22.2. Linked mod.info ID Super-Survivors
did not match legacy table IO's SuperbSurvivors ID, so getModFileWriter returned
nil and group autosave failed at write(). Updated IO ID, added descriptive writer
failure handling and closed existence-probe readers.67 tests,110 syntax checks
pass. No copying: installation uses junctions. See SAVE_IO_ERROR_2026-11-10.md.
Legacy storage layout/migration is unchanged; live restart/autosave check pending.

8 November review of latest 6 November long run: user confirms NPC rendering.
No gameplay Lua failure stacks through frame263147. Four frame0 UIManager
exceptions match four child buttons also registered as roots; removed those
root registrations. Fixed18 obsolete item/module IDs and Foraging/First Aid
perk lookups after a broader installed-script/JAR audit. Four semantic item cases
and three legacy grave recipes remain.64 tests,110 syntax checks pass. See
LONG_RUN_REVIEW_2026-11-08.md for precise mappings, warnings and limits. No new
debug probes or render/LOS changes. Next launch uses nine updated Lua files.

Latest: user paused live debugging to request static analysis. The own-opacity
guard did not restore visibility. Review found that native renderPlayers runs
before RenderOpaqueObjectsInWorld, so the guard is too late; an offline ordering
reproduction confirms the defect. Native standalone IsoPlayers also retain
viewport0/remote=false and run LOS; their update path writes IsoPlayer.instance.
See PLAYER_VISIBILITY_REVIEW_2026-10-21.md. No additional source change deployed
during this review. A dedicated post-world-update OnTick guard is the reviewed
correction, still unimplemented; no new user test requested.

This branch began as a copy of the B41 mod. The cloud work has:

- Moved version-specific content into `42/`, textures and sounds into
  `common/media/`, and old save/options artifacts into `reference/`.
- Changed `42/mod.info` to `versionMin=42.0`; this is metadata, not proof of
  compatibility. The mod ID remains `SuperbSurvivors`.
- Fixed stale require paths and explicit dialogue/translation/name dependencies.
- Removed an unused require for the absent `CharacterSave_SaveLoad` module.
- Added `SuperbSurvivorsDebug.spawn()` for a manual, debug-only single-player
  spawn check. It spawns nothing automatically and preserves constructor errors.
- Added seven isolated regression checks in `tests/test_startup.py`.

All 109 Lua files passed Lua 5.1 syntax checks and all seven tests passed in the
cloud. The tests mock game services. No game client was available; no in-game
loading, NPC creation, combat, persistence or multiplayer claim has been verified.

## Set up on Windows

Clone the branch and open its folder in VS Code:

```bat
git clone --branch B42 https://github.com/EnterTheNameHere/Super-Survivors.git
cd Super-Survivors
code .
```

For an existing checkout, preserve local work, fetch, switch to `B42`, and pull
with `--ff-only` instead of cloning another copy.

Install the official OpenAI Codex extension, sign in, and select local execution.
The local session has its own permissions; it does not inherit this chat's tool
access or conversation. The native x64 command prompt is suitable. A Python 3
installation is needed only for the isolated checks:

```bat
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install lupa==2.6
.venv\Scripts\python.exe -m unittest discover -s tests -v
.venv\Scripts\python.exe tools\check_lua.py
```

## First local task

1. Locate the installed game and record the exact version. The agreed initial
   target is 42.21; verify that against the actual installation. Inspect its Lua
   files and Java API instead of relying on the older 42.20.2 community mirror.
2. Copy only `42/` and `common/` into
   `%USERPROFILE%\Zomboid\mods\SuperbSurvivors\`. These are copies: recopy changed
   files after edits, removing obsolete files from this development copy as needed.
   Do not copy `reference/`, `.git/`, tests or tools. Disable other copies of this
   mod, including Workshop copies with the same ID.
3. Follow `B42_PORT.md`: use a fresh disposable single-player world, launch with
   `-debug`, fix the first startup exception, then run
   `SuperbSurvivorsDebug.spawn()` in the debug Lua console.
4. Inspect `%USERPROFILE%\Zomboid\console.txt` (or the configured game cache
   directory), preserving the full first relevant stack and the game version.
   Continue until one survivor can spawn and remain present without recurring
   errors, then work on following/navigation and combat.

The game can use a custom cache path; confirm paths before copying or reading
logs. Do not overwrite an existing mod installation or valuable save blindly.

## Local inspection — 2026-10-21

- Game installation found at `G:\Steam\steamapps\common\ProjectZomboid`.
  Steam manifest reports build ID `25485521`. The existing default-cache
  `console.txt` reports `42.21.0`, revision `4a0e9546ec`; this is an earlier run,
  not a newly verified launch of the installed game.
- Default cache found at `C:\Users\Enter\Zomboid`. Its console log was last
  modified on October 6 and contains many enabled mods, including KnoxSurvivors,
  but no SuperbSurvivors load. It cannot establish a failure for this checkout.
- Created a new development copy at
  `C:\Users\Enter\Zomboid\mods\SuperbSurvivors`, containing only `42/` and
  `common/`, after checking the destination did not exist. No existing saves,
  mod selections, or launcher configuration were changed. No matching
  `id=SuperbSurvivors` was found in the installed Steam Workshop mod metadata.
- `ProjectZomboid64.json` contains Knox bridge native/Java agent arguments.
  Disabling Workshop mods alone therefore does not remove all instrumentation.
  Account for this in test results; do not silently edit the user's launcher.
- Installed vanilla Lua uses uppercase moodle constants such as
  `MoodleType.PAIN`, `PANIC`, and `HEAVY_LOAD`; legacy references in this mod still
  need porting. No gameplay changes were made based on the old log.
- Python 3.12.10 was found under `W:\DevEnv\Python\vLLM\python`, but it lacks
  `lupa`. The isolated tests were not rerun locally during this inspection.
- Next: launch with `-debug`, enable only the development mod in a fresh
  disposable single-player world, then run `SuperbSurvivorsDebug.spawn()` if
  initialization succeeds. Inspect the newly written log's first relevant full
  stack before changing gameplay code. Confirm a custom cache path if the
  default log does not update. Startup and spawn remain unverified in game.

## Decisions to preserve

Local follow-up: the first fresh in-game test reached the world but recorded
moodle initialization errors and a spawn failure at `setNPC(true)`. The installed
JAR confirms the replacement is `setNpc(true)`. NPC flag calls and speech moodle
lookups have now been updated; nine isolated tests and 109 syntax checks pass
using the new workspace `.venv` with `lupa==2.6`. See
[port status](B42_PORT.md) and [original stacks](LOCAL_STARTUP_ERRORS_2026-10-21.md).
Next step is a full game restart and a fresh disposable world to validate these
fixes. The startup/spawn milestone is not yet complete.

The following run reached `getTraits()` at line 609. Ported `spawnPlayer` trait
assignment and its hunger/thirst setters to the installed B42 APIs, omitting the
removed Lucky bonus. Ten isolated tests and 109 syntax checks now pass. The next
fresh in-game run must validate the complete constructor and continued presence;
the new full-`spawnPlayer` test still uses mocked game services.

The latest run reached the removed player `setForname` call. Fixed naming via
the survivor descriptor and completed a conservative whole-file Java API review,
including additional verified stat, movement, aiming and clothing fixes.
Thirteen tests and 109 syntax checks pass. Before treating another spawn run as
the next milestone, see [the API audit](SUPER_SURVIVOR_API_AUDIT.md): seven combat
flag calls and two legacy water calls are known unsupported APIs still requiring
ports. Combat flags affect stopping/movement as well as attacking. No broad error
suppression or guessed attack-flag replacements were added.

Combat/fluid follow-up is now implemented: both attack paths request B42 engine
combat, stop methods cancel pending intent, and NPC swing callbacks no longer
apply legacy ammo/chamber compensation. Drinking/washing use installed vanilla
B42 actions and fluid volumes; wash batches reserve water/soap and use corrected
constructor signatures. All 25 tests (including two installed-vanilla checks with
`PZ_GAME_DIR` set) and 109 syntax checks pass. The targeted unsupported methods
are gone from active code. Next is a restarted game/fresh disposable world to
validate presence, movement, melee/ranged hits and water actions. The engine now
owns attack accuracy/damage; none of that live behavior has been established by
the isolated checks. See the updated API audit for the exact scope.

The latest in-game failure reached `SuitUp`: a raw `"Jacket"` string no longer
matches `setWornItem(ItemBodyLocation, item)`. Fixed typed jacket and bag/clothing
attachment, removed dressing's local-player inventory UI call, and added explicit
suit dependencies. A full mocked constructor now completes outfit setup. All 28
tests and 109 syntax checks pass; fresh in-game spawn/presence is still next.

Latest result: the debug probe logged **Spawned survivor 4 at 10778,9764,0**.
Construction now completes in game. Its next update failed on indexed access to
the new Set returned by `IsoCell:getObjectList()`. Fixed all four scan paths with
the verified one-based `getLuaObjectList()` API. All 33 tests and 109 syntax checks
pass. Restart and recheck continued presence/update behavior; stable AI, following
and combat remain unverified.

Latest follow-up spawned survivor 4 at 10697,9383,0, passed vision and stopped in
movement calculation because `WornItems:getItem("Shoes")` requires a typed slot.
Fixed both shoe accesses and the nearby bag-speed item/container mismatch and
zero no-bag running baseline. All 37 tests and 109 syntax checks pass. Restart
and recheck stable updates/presence, then following/navigation and combat.

Latest user observation: NPCs appear to act/move but are invisible. The log
records survivors 5 and 6 followed by an entry-task exception: the old smash-window
duration argument `20` is now interpreted as `vehiclePart`. Corrected the smash
and glass-removal constructors. All 42 tests and 109 syntax checks pass, including
three optional installed-vanilla checks with `PZ_GAME_DIR` set. Invisibility is
not diagnosed/fixed yet. After restart, spawn one probe, let a few frames run,
pause and run `SuperbSurvivorsDebug.inspect()` to log its rendering state; inspect
that output next. It is read-only and defaults to the last debug-spawned ID.

First rendering inspection: model registered/active, visual and cell/square
membership present, invisibility flags false; alpha/targetAlpha zero, but the NPC
had moved about eight tiles away and both observer/square visibility were false.
This is inconclusive. The console compound hold command then failed after
spawning survivor 5. Added `SuperbSurvivorsDebug.spawnStationary()` to choose a
visible adjacent tile and stop/wait inside the module without changing rendering.
All 45 tests and 109 syntax checks pass. Reload the debug Lua module, run that
single-call probe, wait a few frames, pause and inspect again. Invisibility is
still unresolved. See `docs/RENDER_DIAGNOSTICS_2026-10-21.md`.

Stationary probe 6 is still invisible to the user despite adjacent position,
alpha/targetAlpha 1, true observer/square visibility and active registered model.
Spawn and inspection share frame 5678. Extended debug inspection to check render
permission, animation presence/state, render square and offsets;
`inspectAfterTicks()` captures after 120 simulation ticks. Reload debug module,
run it on the existing probe, close console and unpause. 47 tests and 109 syntax
checks pass. Invisibility is unresolved; see rendering diagnostics for details.
The first deferred capture failed because AnimationPlayer Java methods are not
Lua-exposed. Removed calls through that handle and added a regression check.
Reload the corrected module and repeat inspectAfterTicks on the existing NPC.
Completed deferred inspection at frame 9637: doRender true, animation player
present/idle, render square matches, offsets zero; alpha1 and visibility true
persist. Added debug-only resetModelProbe() to rebuild that model and inspect
after 120 ticks; this is an experiment, not a proven fix. A later glass-removal
error exposed the bundled B41 action override, now ported to installed B42
duration/completion/event/sync behavior. 49 tests and 109 syntax checks pass.
Reload TimedActions/ISRemoveBrokenGlass.lua and the debug module, then run
SuperbSurvivorsDebug.resetModelProbe(), close console and unpause. Check whether
the existing NPC appears. Production visibility fix remains pending.

Whole-Lua follow-up: frame13095 fails in the bundled B41 bandage perform at
HasTrait. Rebased that action to installed B42. Confirmed stale stat/name/aiming/
trait calls across AI, tasks and status panels are fixed. Removed a leftover
nil-call test event hook and fixed gift handling. 53 tests and 109 syntax checks
pass. See REMAINING_API_NAMES_2026-10-21.md for the reproducible 109-file inventory
and eight remaining unmatched sites (legacy admin UI, scavenge UI, debug UnStuck).
These require coherent subsystem ports; the name audit is not a compatibility
proof. Restart to load the broad changes. God mode console command verified:
getSpecificPlayer(0):setGodMod(true). Model-reset result still pending.

Restarted run: probe9 stays invisible after two engine model resets. Deferred
captures29998/30982 still have alpha1, visible square/observer, active model,
animation idle, correct render square and zero offsets. Added read-only
compareModels() using verified vanilla debug reflection globals to compare the
opaque model/mesh/texture/animation/slot fields with player0. Reload only debug
module, run SuperbSurvivorsDebug.compareModels() on existing probe9 and inspect
log next. 54 tests and 109 syntax checks pass. No production render fix yet.

Comparison34679: NPC mesh/skinning/scale/animation valid, body texture nil;
observer texture present. Installed FBORenderCell skips exact IsoPlayer objects
in moving pass, and SP player pass draws only IsoPlayer.players, omitting NPCs.
Added SuperSurvivorRender.lua SP opaque-world render bridge, using vanilla event
and native render signature/light, with load/screen/visibility/floor filters.
57 tests and 110 syntax checks pass. Hot-load
media/lua/client/3_Other/SuperSurvivorRender.lua, unpause and check existing probe.
Live visibility/occlusion still pending; see latest rendering diagnostics.

Live bridge result: stationary probe4 now visible after restart, but user reports
local player disappears after a few dozen seconds. No new Lua error in log through
10826. Requested inspect(0) and compareModels() while local player is invisible;
their output is pending. Do not mark spawn milestone complete or add speculative
alpha fixes. See latest rendering diagnostics; no source change for regression yet.

Player snapshot15090: alpha/targetAlpha0, all model/world/visibility checks valid;
comparison15809 has textures on both NPC and player. Native NPC updateLOS shares
default playerIndex0 and writes alpha in that view. Added narrow own-viewport
opacity guard for the living local observer while managed NPCs are loaded,
respecting explicit invisibility/render flags and death fade. No NPC/zombie alpha
changes. This is a compatibility guard; dynamic Java writer not traced. 59 tests
and110 syntax checks pass. Reload SuperSurvivorRender.lua while player invisible,
unpause and check both characters stay visible beyond one minute. Live result pending.

- Port incrementally, initially single-player, while designing server-owned state.
- Do not mask API failures with broad error suppression or disable meaningful
  behavior merely to make loading appear successful.
- Replace old group/location text files with versioned global mod data under a
  `SuperbSurvivors` namespace: named areas, stable survivor IDs, rebuilt location
  indexes, and explicit multiplayer synchronization. This is not implemented yet.
- Full NPC serialization (inventory, appearance, health, skills) is separate from
  registry metadata; `ModData` does not automatically serialize live NPC objects.
- Keep historical save artifacts for reference and exclude them from releases.

Known work includes old moodle/trait/API references, `loadstring` moodle lookups,
copied vanilla timed actions and UI, fluids, farming, and Java/animation overrides.
The bundled `42/zombie/.../Attack.class` is preserved, not validated. Existing
random/preset spawning and legacy saving still run; the debug command does not
isolate the entire mod or guarantee save compatibility.

## Prompt for the local Codex session

### Current user decision — 2026-11-12

For updates that need a fresh game session, tell the user directly to restart to
load all changes. The user explicitly prefers that over elaborate hot-reload
instructions or engineering around a restart solely for convenience.

Local-player visibility interference is an accepted, non-blocking issue for now.
Keep the current Lua opacity timing correction, but defer further investigation
of native NPC/viewport ownership and continue the rest of the B42 port. The user
accepts restarting as a recovery option if the symptom recurs; this is an
accepted workaround, not proof the underlying issue is fixed.

Future exploration must use existing Lua-accessible controls. **Java-side
modifications are excluded by the user.** Investigate whether NPCs can avoid the
conflicting native visibility update while retaining required actor behavior.
If existing Lua controls cannot isolate it, document the compatibility limits.
Do not resume this investigation as a prerequisite for other porting work.

The user's protection mod is Z'Ware Invincibility: Three Ways Out; do not conflate
it with vanilla God Mode or attribute visibility changes to it without evidence.
See [the visibility review](PLAYER_VISIBILITY_REVIEW_2026-10-21.md) for findings,
the implemented timing correction, and the distinction between cheat flags and
render opacity.

> Read README.md, docs/LOCAL_HANDOFF.md and docs/B42_PORT.md. Continue the B42 port
> from the startup/spawn milestone. Inspect the local Project Zomboid installation
> and console.txt, confirm the actual game version, and fix the first reproducible
> loading or spawn failure. Preserve the agreed persistence design and distinguish
> isolated tests from real in-game validation. Ask me to launch/test the game when
> needed, then inspect the resulting logs.
