# Local Codex handoff

Repository: `EnterTheNameHere/Super-Survivors`, branch `B42`.

## Combat05 earliest natural attack diagnostic (17 November 2026)

Implemented explicit Information -> Diagnostics -> Start earliest natural attack
observation (up to 10s), both Information paths. Restart to load update. Existing
live nonlocal NPC, flags false/no known active swing only; already-started rejected,
no reset/spawn/attack. Always earliest OBSERVED: registry has no never-attacked
provenance. Module SSRCombatFirstAttack observes two instance-local Lua methods,
requestCombatAttack and StopWalk, exact-once/direct original invocation/results/
errors; filtered early OnPlayerUpdate, tick, swing/hitpoint. Frozen actor/world/
Information binding and human singleton/MainPlayer/all slots; owned hook cleanup
on close/hide/rebind/unload/death/debug/menu/reload/error/caps. Legacy trace remains,
mutually exclusive. No SS Tests consent/state bypass, gameplay/AI/Java/flag changes.
10s/600ticks/120lines/8request cap, three ticks after acceptance/event; caps first.
Console prefix [SS Combat][first-natural-attack]. No request -> INCONCLUSIVE.
Moving positions/timers alone don't fill log. First-ever setter, exact chronology,
animation/hit/damage unproved; collision gate remains. Docs
COMBAT_FIRST_NATURAL_ATTACK_B42.md. 290 isolated tests/117 syntax pass; native UI/
execution PENDING. Test04 R1 baseline/restart proof and Test03 deferred observer
unchanged; inventory implementation deferred. User edits/saves preserved.

## Combat04 correction-options research (17 November 2026)

Read docs/COMBAT_B42_CORRECTION_OPTIONS_04.md. Investigation/design only, no
production fix/fixture. Current-JAR full flag-writer/caller audit and exposure
inspection: pressedAttack exists and may latch both flags for SP NPC, but NPC
post-update writes initiateAttack from default-false AI controls before scheduled
postUpdateAnimating -> ActionContext.update consumes transition conditions.
StopWalk also clears initiation without started; first live cause still unknown.
New actors default false; native save/load does not explicitly restore these flags;
loaded SSR actors are newly constructed, unlike loading into an existing actor.
Other native setters include spear-charge contact and network replay; ordinary
state exits/getup/sitting clear flags. Do not force these as recovery recipes.
AIComponent/control vars and CombatManager are not normally exposed Lua classes;
Java public methods/HashMap component access do not establish a usable control
bridge. Ordinary Swipe collision requires exact local-player membership; SP
isLocal is a different predicate. No supported alternate standalone-NPC collision
route was verified. B41 NPC setters absent. Do not ship animation as damage fix.
Next proposed assignment: bounded first natural request observation on existing
provenance-known fresh false-flag actor, exact-once request/StopWalk and filtered
early-native/tick/swing/hitpoint samples. No busy re-trace, flags, AI changes,
spawn or damage. Fixture only by later disposable-world consent/assignment.
Prior traces/logs/settings/user edits preserved; Test04 R1 and Test03 unchanged.

## Inventory01 investigation delivered (17 November 2026)

Read docs/INVENTORY_B42_INVESTIGATION_01.md before implementing inventory reuse.
Installed B42.22.2 binds displayed ItemContainer separately from local acting
player. Full stock page/pane/context/bag controls are not arbitrary-NPC UI.
Use separate window ownership, native presentation pieces, explicit NPC actor,
and existing SSR native-action adapters. Never replace human inventory/loot
registrations, hotbar or player slots. First prove read-only presentation, then
individual actor-aware actions, then additive human Give To event subscriber.
Event is (playerNum, context, items); normalize grouped items with getActualItems,
validate actual item container and stable recipient ID/actor/world at execution.
Concrete existing issues: selected human bag displayed but transfer source assumes
main inventory; mutable group-index recipient binding; misleading capacity header;
silent transfer rejection. Equipment uses instant remembered-weapon changes;
live TakeGift paths bypass some native timing. Old Back clothing accessors remain
valid B42 APIs. Native timed actions still contain human UI callbacks even with
explicit NPC actors; retain existing NPC transfer loot-UI isolation.
Investigation only: no production/UI/action code changed or engine proof run.
Combat03 follow-up remains separate; Test04 restart proof pending; Test03 early
observer deferred. No source merge or inventory implementation acceptance.

## Combat03 actual native trace result (17 November 2026)

5 user traces IDs9/1/5/5/5,400lines;98 complete natural request returns ALL false,
"busy".102entries with4returns censored by80line caps (not failed/hung). Roderick
ID9 has15 in-range natural calls rejectedbusy, startedtrue/initiatefalse/no swing,
cooldown0. All traces preexisting startedtrue, no sampledrise/swing/hit event.
All report own wrapper restored, no actual errors. Stage(d) request rejection now
observed, not conditional; sourcebusyguard before nativepressedAttack. First setter/
handoff chronology still unobserved, no root-cause/fix claim. Evidence
COMBAT_TRACE_2026-11-17.log, summary COMBAT_HANDOFF_TRACE_B42.md. No extra trace,
flag reset or production edits. Inventory01 inbox arrived separately, preserved
and not started as part of this runtime log check. Prior delivery notes historical.

## Combat03 contextual diagnostics and bounded trace (17 November 2026)

Implemented shared Diagnostics menu on BOTH reachable information UI paths,
bound exact wrapper/actor/world at Load/show. Snapshot reuse via dedicated
observation endpoint, no generic test/consent bypass. Trace max10s/600ticks/80lines/
30natural calls, only instance-local request interception, original once/args/
counted returns preserved. Original errors escape without pcall/rethrow (Kahlua
error tuple differs), deferred cleanup next callback after aborted synchronous
call. Owned raw-slot restoration, callbacks removed on limits/cancel/close/death/
unload/replacement/debug-off/world/menu/reload. Verified swing/HitPoint events
filtered exact attacker; no damage proof. Preexisting started flags labeled,
not fixed. SS Tests optional7th definition retains consent. Native trace/UI NOT
RUN. Restart, Information -> Diagnostics -> Start combat trace. Detailed docs
COMBAT_HANDOFF_TRACE_B42.md, including B41/legacy B41 NPC framework/current API matrix and native
post-update ordering. Legacy PerkCount builder writes remain independent; no
production combat/Java/flag/slot changes. Test04 R1 preserved. Prior notes below
are earlier deliveries, not current lack-of-implementation claims.

## Combat02 actual ID9 observations (17 November 2026)

User identifies Roderick as ID9.33 native snapshots/277.817s: all native attackStarted
true, initiate false, no attack animation/SwipeState, readiness true, healthy/armed;
11 in-range (7 wait0), Attack front31, Flee1, Enter New Building1; updates progress.
No errors after first snapshot. Strong recurring stale attack flag/animation handoff
candidate: requestCombatAttack would reject busy at these flags, but no request
trace/first-set/reset transition recorded. Not a proven full cause or continuous
trace. Evidence COMBAT_SNAPSHOT_RODERICK_ID9_2026-11-17.log, summary in
COMBAT_LIVE_SNAPSHOT_B42.md. No fixes/flag resets or temporal observer implemented.
Orchestrator review next; additional identical snapshots not needed for this pattern.

## Combat02 read-only existing-NPC snapshot (17 November 2026)

Implemented Combat - inspect existing survivor in SS Tests with explicit loaded
ID/name selector and manual Refresh survivors. One protected next-tick snapshot:
cached perception/queue/weapon/policy/scheduler plus safe native flags and engine
frame. No task predicates, updates, attacks, spawn or temporal tracing; latest
result in memory only. Input identity/world/cell frozen/revalidated, all local
slots/singleton/MainPlayer excluded. ControlVars Class token unverified -> explicit
UNAVAILABLE; native actual aiming/start/swing reported independently. INCONCLUSIVE,
no root cause or hit proof. Restart to load, select existing NPC near a zombie,
acknowledge/Run and report what user saw. Native UI/snapshot NOT RUN. See
COMBAT_LIVE_SNAPSHOT_B42.md. Test04 R1 GMD baseline unchanged; restart proof pending.
No proven combat defects fixed; no Java/slot/damage modifications. User edits kept.

## Combat01 source diagnosis (17 November 2026)

Analysis only after Test04 R1 delivery. See COMBAT_B42_INVESTIGATION_01.md:
perception list is one-based Kahlua table, native moving list is Set and ordinary
zombies are registered there. Definite impossible equipped-and-empty equip rules,
zombie Pursue requiring nonexistent SSR wrapper; active Attack branches remain.
Native NPC controls override aiming/initiation semantics and usual collision
callback gates on local-player membership. No runtime combat-stage evidence yet;
no root cause/reproduction or animation/hit success claimed. Proposed existing-NPC
snapshot first, bounded passive request/event observation if needed, separately
reviewed Lua defects/native adapter. No gameplay code or test diagnostic added.
Java changes/direct Hit/local-slot manipulation excluded. User edits preserved.

## Test 04 R1 persistent human baseline (17 November 2026)

Current implementation keeps an explicitly captured scalar baseline in separate
versioned world GlobalModData SSR.Tests.HumanVisual for NEXT NORMAL SAVE. No forced
save/native character IO/production change. Restart, capture once while correct,
save/exit normally, restart/load, invoke AFTER without recapture and check original
timestamp. R1 native roundtrip NOT RUN. Cross-session identity always UNVERIFIED;
name/sex hints are not proof, changed hints withhold comparison. Pointers never
persist. First explicit AFTER anchors refs only for later checks this session.
AFTER remains readOnly, history four in memory. Capture is diagnosticWrite,
blocked by cleanup failure but draws no RNG. Invalid/missing data explained, no
repair; unavailable debug fields stay explicit. Existing session-only baseline
cannot survive the upgrade without new capture/save. Prior original Test04 logs
verified: 83 fields each, expected 25 unavailable, no errors, baseline captured,
AFTERs inconclusive; no user-confirmed symptom reproduction. Detailed record in
HUMAN_VISUAL_DIAGNOSTICS_B42.md. Earlier notes below are historical deliveries.

## Test 04 human visual diagnostics (17 November 2026)

Priority changed by canonical inbox: user directly saw restored NPC AI movement;
Test-03 machine INCONCLUSIVE history retained, R1 observer not started/deferred.
Human skin/hair/probable beard change occurred during ordinary play, not active
test; separate invisibility-off recovery has no identified origin. Implemented
three explicit Human appearance baseline/changed/invisible controls in SS Tests.
No production fixes, setters/reset/model reconstruction, native load/save or
automatic captures. Read-only definitions retain consent but skip gameplay RNG.
Baseline is session-only (no verified stable public human DB identity getter),
world/cell/actor scoped; after captures never overwrite it, bounded history four.
Full raw colors/styles require native-debug reflection; unsafe lazy public getters
and getAnimationPlayer are never called. Without -debug unavailable fields stay
explicit, safe indices/flags/identity/context still work. See
HUMAN_VISUAL_DIAGNOSTICS_B42.md. 219 tests/113 syntax pass working-copy; native
Test 04 NOT RUN. Concurrent source/settings/save edits preserved.

## Test 03 actual restart: inconclusive position (17 November 2026)

Actual stage/OnSave/restart/resume completed: SSR survivor 2/group 3, snapshot
SSR_Survivor_2_4.bin. Native snapshot matches all baseline fields; registry/group,
loaded inventory/equipment/identity/health match, counts 1/1/1, membership/human
checks/reader cleanup pass. Live X/Y shifted from 9885.5/12824.5 to
9888.5/12828.3349609375 before comparison; overall INCONCLUSIVE. No earliest
reconstruction observation distinguishes ordinary AI movement from loading.
Axe XP baseline remained 0, so nonzero XP retention untested despite AddXP setup.
No repeat next exception or new probe stack trace. Evidence:
evidence/SSR_RESTART_2026-11-17.log; full results in PERSISTENCE_LIVE_TESTS.md.
No code changed; send to orchestrator for scoped next decision, not forced PASS.

## Persistence global-next compatibility fix (17 November 2026)

User reports error after Test 03 deployment. Console repeats tick failure at
SuperSurvivorPersistence.lua:256, global next(entries). Installed Kahlua BaseLib
has no global next, unlike Lua 5.1 used by mocked tests. Small follow-up replaces
both global next calls (index selection and empty-bucket removal) with a local
pairs-based firstKey helper; no scan/load/unload algorithm rewrite. Native iterator
and SpiralSearch :next methods remain unchanged. New regression disables next
for index load/unload/dead unindex and full lifecycle test. 201 tests/112 syntax
pass; native retry requires restart. Captured first error:
evidence/PERSISTENCE_NEXT_ERROR_2026-11-17.log. No full Test 03 pass yet.

## SSR-TEST-03 implemented; runtime pending (17 November 2026)

Read/acknowledged canonical assignment to replace visible native diagnostic
choices with one real SSR survivor/group stage/save/restart/resume test. Current
UI has two entries: SSR persistence - stage one survivor and group; SSR persistence
- resume (I fully restarted the game). Restart required. See TESTS_UI.md and
PERSISTENCE_LIVE_TESTS.md for exact steps, baseline semantics, statuses and manual
follow-ups. Historic native instructions moved to docs/archive; native code kept
as tests-only fixture, evidence unchanged. Production persistence/loader untouched.
Observer appends after P.save and samples inside actual OnSave, not earlier at
staging; it refreshes latest normal save and invalidates absent/new-generation
failures. Resume independently reads exact native snapshot, real registry/group,
ordinary reconstructed actor and counts; no forced load/save. Fixtures remain.
Live AI drift is inconclusive; strict native/metadata mismatches are logged failures.
Human slots/identity protected; temporary reader owned and detached before update.
199 automated tests and 112 syntax checks pass in an isolated staged-tree export
(excluding user edits); LuaLS 88 legacy diagnostics, none in new modules. No
in-game Test 03 result. No streaming/death/multi-group acceptance claimed.

## SSR-TEST-02 passed in-game (17 November 2026)

Actual console shows cell-only actor at 0.5/0.5/0 without square/world membership;
raw load restores 9884.5/12827.5/0 and marker but remains unregistered. Explicit
currentSquare, moving-square and cell registration establishes matching
membership without changing position. Human/all four slots unchanged; both actors
cleaned up at same frame. Evidence: evidence/CELL_ONLY_ISOPLAYER_2026-11-17.log;
full findings in NATIVE_POSITION_R1.md. Scoped probe passes; no long-term AI,
streaming or full SSR lifecycle acceptance. No code changes; return to orchestration.

## SSR-TEST-02 prepared (15 November 2026)

User resumed Test 2. Cell-only constructor and registration primitives verified
in installed 42.22.2. New fourth Tests entry: Native IsoPlayer - cell-only
construction and placement (native-cell-only). Source, cell-only before load,
raw load and explicit square/moving-square/cell registration measured in one
safe callback, cleanup before normal update. Human guard includes all four
local slots; no human factory/load/control calls, coordinate setters or production
persistence edits. See TESTS_UI.md and NATIVE_POSITION_R1.md for findings and
factory supplement. 185 tests, 112 syntax checks; LuaLS 88 legacy diagnostics,
none test modules. USER IN-GAME NOT RUN. Restart required before using new entry.

## IsoSurvivor comparison closed (15 November 2026)

User requested ONLY SSR-ANALYSIS-01 and then asked to finish the proposed switch
as rejected. Read-only installed-engine comparison is in
[ISOSURVIVOR_VS_ISOPLAYER_B42.md](ISOSURVIVOR_VS_ISOPLAYER_B42.md).
Reject IsoSurvivor migration: inherited visual getter throws, primary bodyDamage,
moodles and XP are absent, current attack state casts to IsoPlayer, filename
save/control methods differ. Keep IsoPlayer; no runtime edits or experiments.
SSR-TEST-02 and factory supplement remain pending separately. Source scan covered
23,692 JAR classes plus bundled Lua; source evidence is not an IsoSurvivor runtime
test. Existing uncommitted source/settings/save edits preserved.

## Returned to orchestration (15 November 2026)

User restarted after startup fixes; log at 14:31:11 has no prior option-format
or grave-recipe property errors and no new gameplay Lua stack trace. Actual
crafting remains untested. User requested return to orchestration; no further
implementation started. Canonical addressed report:
ai-workflow/mail/orchestrator/inbox/2026-11-15-return-to-orchestration.md.

## Startup error fixes (15 November 2026)

User requested fixing mod-owned errors from the post-probe log. Three English
option descriptions used unescaped percent symbols, causing Translator format
exceptions. JSON and legacy English text now spell out percent/percentage.
Three grave recipes in SuperSurvivors.txt used legacy recipe syntax; installed
Recipe.Load rejects every colon property except Override. Converted to craftRecipe
with explicit inputs/outputs, preserved ingredient quantities, retained tools,
and times 500/100/500. Grave item definitions unchanged. Added Recipes.json names
and module-qualified timed actions for digging/cross work; installed Shoveling
and Hammering sounds replace old digging/PZ_Hammer names. These remain legacy
inventory-item recipes, not a rewrite of vanilla map graves/burial.
178 automated tests and 112 Lua syntax checks pass, edited JSON and staged
whitespace valid. Installed CraftRecipe/TimedAction examples inspected; actual
recipe load/crafting validation awaits game restart. Unrelated game/map/vehicle
errors and concurrent user edits left alone.

## Native position runtime results (15 November 2026)

User completed same-session test, staging, game restart/world reload and resume.
Logs verify two same-session PASSED runs plus PASSED resume. Native load restores
X/Y and marker but leaves currentSquare/moving-square membership at constructor
location. Human invariants and actor cleanup passed. Z remained zero; complete
SSR lifecycle remains unvalidated. See NATIVE_POSITION_R1.md and filtered
 evidence/NATIVE_POSITION_2026-11-15.log. No gameplay code changed on this report.

## Tests UI boxed-offset follow-up (15 November 2026)

After fixing the version gate, user reports offset prerequisite rejects X/Y=0/0.
Installed LuaJavaClassExposer.exposeStatics directly stores Field.get(clazz)
without numeric conversion, exposing boxed Integer values. Probe now parses
numeric representations before comparison; unreadable/nil and nonzero values
remain blocked. No world mutation or native roundtrip observed yet.

## Tests UI runtime follow-up (15 November 2026)

User opened SS Tests; ticking consent left Run disabled with the version warning.
Installed Core.getGameVersion():toString() yields 42.22; getGameAndBuildVersion()
yields 42.22.2. JAR hash/revision unchanged. Probe now checks the latter and
includes the detected version on mismatch. At the user's explicit request,
switching definitions preserves the checkbox; run attempts/reopening still clear
it. Disabled Run reports its reason in output and tooltip. 177 automated tests
and 112 syntax checks pass; native roundtrip execution is still pending.

## Tests UI and R1 investigation (15 November 2026)

User reported updated inbox; read canonical B42 through 02a23f1 and acknowledged
SSR-TEST-01 plus the authoritative PERSIST-01 R1 clarification. Same exclusive
codex/persistence-b42 checkout, starting d585676. Acknowledgment is published on
B42 at d59792b. Preserve user .vscode/settings.json edits and common/ save output.

R1 is an engine investigation, NOT a mandatory tick-scan optimization. Production
persistence scan/unload code is unchanged in this follow-up. See
[NATIVE_POSITION_R1.md](NATIVE_POSITION_R1.md) for installed 42.22.2 source facts,
remaining lifecycle questions and proposals. Native save/load already encodes
coordinates; current-square/moving-square association is separate.

[TESTS_UI.md](TESTS_UI.md) documents the approved minimal, option-gated Tests UI,
per-run warning/consent, independent registry, raw native diagnostic, and explicit
stage/restart/resume. No native -debug requirement, AI manager or full debug hub.
Restart, enter a fresh disposable world, enable Debug Options on the Superb
Survivors options page and right-click SS Tests. Actual game results remain
unobserved; code/mocks are not engine acceptance.

## Persistence implementation assignment (15 November 2026)

The user explicitly resumed implementation for **SSR-PERSIST-01 only**, following
ai-workflow/index.md on canonical B42. Work is on `codex/persistence-b42`, based
on `3a087ee8c4aceb151443848e19bbc3a999a129f5`, in this existing checkout.
Read [../ai-workflow/index.md](../ai-workflow/index.md) and its protocol/inbox
before further work. Acknowledgment is in the orchestrator inbox on the
implementation ref. No unreviewed implementation merge into B42 is authorized.

See [PERSISTENCE_B42.md](PERSISTENCE_B42.md) for schema/lifecycle, installed B42
evidence, limitations and exact disposable-world checks. Persistence now uses
world Global ModData and versioned native character snapshots. No legacy import;
fresh worlds only. No in-game results are claimed. Old per-world metadata files
are not used; options remain independent user preferences. AI/debug UI plans
remain design-only and are not part of this assignment.

Historical statuses below predate this bounded authorization and implementation.

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
