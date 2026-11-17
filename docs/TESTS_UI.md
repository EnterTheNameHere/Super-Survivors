# Minimal SS Tests UI — SSR-TEST-01

15 November 2026; implementation on codex/persistence-b42. This is the small
approved Tests surface, not the future SS Debug hub or AI scenario runner.
The persistence scan/unload implementation remains unchanged in this task.

## Start and visibility

1. Restart the game to load all new modules.
2. Use installed **B42.22.2** and create a **fresh disposable single-player world**
   with one local player. Create the character and enter gameplay. Prefer only
   Super Survivors Reloaded while collecting this native-engine evidence.
3. In game options, open the existing **Superb Survivors** page. Set **Debug
   Options = On**, then apply/accept. Internally this is saved DebugOptions = 2;
   the default/missing value is off. It also exposes the existing legacy debug
   options; this task does not audit or add those cheats.
4. Right-click in the world and choose the root entry **SS Tests...**. The entry
   is hidden when that setting is off, in multiplayer or for other local-player
   indices. Controller preview passes only advertise menu availability using
   vanilla setTest(); they never open the UI or execute a test. The game's
   **-debug flag is not required**.
5. The window lists registered tests, their description, risk, requirements,
   availability and observed results. Move to an open area if the native probe
   cannot find two nearby loaded, free floor tiles. Unsupported game versions,
   no-save worlds and nonzero/unknown native save offsets are unavailable.

## Warning and consent

The window displays the approved warning before any execution:

> Warning — World Modifications
>
> Tests may irreversibly alter this game world, including characters, items,
> objects and zombies. Use a disposable world. Restoration is not guaranteed.

Tick the acknowledgment checkbox, then choose **Run selected test**. Every run
consumes consent immediately. Switching tests or refreshing the registry preserves
the checkbox. Reopening the window clears it. There is no automatic test execution
on startup, window open or restart. A disabled Run button shows its blocking reason
in the output panel and its tooltip, even after acknowledgment.

Only one test runs at a time. Run is disabled while active. Cancel or closing
the window stops a pending/multi-tick run and attempts its cleanup. Disabling
Debug Options, losing the living player, changing world/mode or timing out also
stops it. Cleanup failure changes the outcome to INCONCLUSIVE and blocks further
runs until a new gameplay session; follow the displayed restart instruction.

## First diagnostic: same-session native position

Select **Native IsoPlayer position — same session**, read the description,
acknowledge and run. The execution is deferred to OnTick, then waits for the
cell's native safeToAdd state. It:

- Constructs an isolated raw NPC on a free loaded tile and records actor and
  square coordinates, containment and object/add/remove membership.
- Saves it to a checked unique SSR_Test_NativePosition_* file in this world.
- Constructs a distinct raw NPC on a different free tile and records that state.
- Calls native load(String) without manual setX/Y/Z, square repair or a world
  update, and immediately records the result.
- Records actual current-square reference equality, which constructor axes were
  differentiated, restored identity marker and a missing-file load case.
- Verifies the human player identity, XYZ, singleton and saveFileName are
  unchanged; removes only owned non-local test actors in a verified safe phase.

The inspected source predicts restored coordinates with constructor-associated
currentSquare state potentially remaining. That distinction is the experiment,
not a reason to manually correct the actor during the test. Actors are removed
in the same callback, before a deliberate world update can move/reassociate them.

PASS requires matching native position and identity marker at a distinguishable
constructor location, unchanged human guards and expected missing-file behavior,
with verified cleanup. **It does not mean square association is correct, all axes
were independently differentiated, or SSR persistence is accepted.** Each is
reported separately. Same-floor Z equality alone is not proof of Z restoration.

## Explicit restart-phase diagnostic

1. Select **Native IsoPlayer position — stage restart probe** and give fresh
   consent. It creates one isolated snapshot and a small serializable manifest
   under ModData key SSR.Tests.NativePosition, then cleans up the actor.
2. Expect **INCONCLUSIVE / snapshot staged**, with clear instructions. Staging
   is not a completed roundtrip. Record the file and session token from the UI/log.
3. Save and exit normally, **close the game completely**, restart, and load the
   same disposable world. The manifest only persists through a normal world save.
4. Enter gameplay, reopen SS Tests, select **Native IsoPlayer position — resume
   after restart**, read its requirements and give new consent. Nothing resumes
   automatically. It refuses the staging Lua session or a changed engine build.
5. It loads the referenced test snapshot into an isolated NPC constructed at a
   distinguishable location, repeats raw observations and cleanup, and logs the
   earlier/current session tokens. The manifest's source values are reprinted,
   so the current console can show both sides.

A different Lua boot token is evidence of a different Lua session, **not proof
that the OS process was restarted**. Follow and report the actual steps. Repeated
explicit resume runs are allowed, each with fresh consent. Staging a new probe
replaces the manifest but does not delete earlier test files. Missing/invalid
evidence is unavailable/setup error, never silently reconstructed.

## Results and evidence to send

The window shows RUNNING, PASSED, FAILED, INCONCLUSIVE or SETUP ERROR and concrete
observations/exceptions. Scroll the details/results panels as needed. The full
trace is also printed to `C:\Users\Enter\Zomboid\console.txt` with
`[SS Tests][native-position...]` prefixes.

Report which entry was run and whether the game was actually closed/restarted.
Include the outcome and source/before-load/after-load XYZ, square positions,
world/add/remove flags, differentiated axes, human guards and cleanup lines.
Existing unrelated errors should be distinguished by their stack/timestamp.
The tests do not automatically treat invocation returning as success.

## Safety boundaries and implementation contract

- No human snapshot path, human character setters, player-slot swapping or Java
  modifications. Native save(String) uses its own temporary singleton handling;
  the probe checks that the previous singleton was restored.
- Raw test actors have no SSR IDs and are not inserted into the survivor registry.
  Construction still emits native/other-mod character events. Other mods and
  engine-side bugs can have effects the probe cannot reverse. It is not a sandbox.
- If construction throws after internal registration but before returning a
  handle, selective cleanup cannot be proven. Report INCONCLUSIVE, block more
  runs and restart. Do not find/delete arbitrary actors to conceal that failure.
- Native snapshots and staging metadata are retained. Cleanup verifies owned
  actor detachment, not full restoration of world state or native internal caches.
  The probe deliberately does not call removeSaveFile, which can involve native
  player-database saving; test files are distinct and can remain in this disposable
  save. No guarantee of crash-safe or atomic world persistence is made.
- Whole SSR persistence, actor streaming and unload handling are separate user
  tests. See [NATIVE_POSITION_R1.md](NATIVE_POSITION_R1.md) for installed-engine
  facts versus concerns and proposals. No per-tick scan rewrite is included.

Registry/executor: client/Testing/SSRTests.lua. Definitions:
client/Testing/SSRNativePositionTest.lua. UI: client/5_UI/SSRTestsWindow.lua.
Definitions provide id/title/description/risk/requirements, optional available(),
and run(context). A run may finish with an explicit outcome or set context.step
for subsequent ticks; bounded timeout is supported. This is not a general DSL,
persistent scheduler or broad scenario runner. Current native staging is a
specific diagnostic's data, not generic resumable execution.

The new Testing modules/UI are included by normal packaging but gated off by
default. Existing client/Debug disposable scenarios remain excluded. Automated
checks use mocked UI/native IO and installed-JAR inspection; actual engine UI
and gameplay results remain **NOT RUN** until the user executes these steps.

## Automated delivery checks

With PZ_GAME_DIR set to the installed ProjectZomboid directory:

```powershell
$env:PZ_GAME_DIR = 'G:\Steam\steamapps\common\ProjectZomboid'
.\.venv\Scripts\python.exe -m unittest discover -s tests -q
.\.venv\Scripts\python.exe tools/check_lua.py
.\.venv\Scripts\python.exe tools/generate_editor_api.py "$env:PZ_GAME_DIR\projectzomboid.jar"
git diff --check
```

174 tests pass, including 12 new mocked registry/UI/probe guardrail checks and
the installed-JAR position encoding check. All 112 runtime Lua files compile.
The packaging regression retains the new normal Testing/UI modules while
excluding legacy Debug scenarios. Existing persistence tests remain green;
the reviewed persistence scan/loader files are unchanged from dc4dde2.

LuaLS warning-level inspection completed with 88 legacy diagnostics across 13
files, with none in the new Testing/SSRTestsWindow modules. It is not a clean
whole-project diagnostic result. Native editor declarations now include the
verified public nullable IsoPlayer.saveFileName field and used native methods.
No blanket field suppression or user VS Code settings change was made.

Local ignored logs: .venv/test01-delivery-suite.txt and
.venv/luals-test01-delivery-result.txt. Mock widgets do not establish actual
engine rendering/layout, and mock native IO does not establish an engine roundtrip.

Checkbox/version follow-up: 177 automated tests and 112 Lua syntax checks pass.
Selection changes preserve acknowledgment at the user’s request; each run still
consumes it. The reported blocker was a version API mismatch: GameVersion yields 42.22,
while getGameAndBuildVersion yields the inspected 42.22.2. The probe now uses
the latter and reports the detected build when it differs.


Runtime update (15 November 2026): user completed all three phases. Logs confirm
two same-session passes, staging and resumed pass after user-confirmed restart.
Coordinates/marker restored; currentSquare stayed at constructor tile. Human
guards/cleanup passed. See [findings](NATIVE_POSITION_R1.md) and its captured
evidence. Earlier NOT RUN statements describe the initial delivery state.


## Test 2: cell-only constructor, raw load and explicit placement

SSR-TEST-02 is a NEW fourth entry, independent of the earlier three restart
phases. Exact selector title: **Native IsoPlayer - cell-only construction and
placement** (`native-cell-only`). It does not use or replace the restart manifest.

1. Restart the game to load the updated diagnostic. Use the disposable B42.22.2
   single-player world, one living local player, normal saves and zero offsets.
2. Enable Superb Survivors -> Debug Options -> On, right-click -> SS Tests... .
3. Select **Native IsoPlayer - cell-only construction and placement**. Read its
   warning/requirements, check acknowledgment, then Run selected test.
4. It runs once in a native safe-to-add callback and logs four rows: conventional
   saved source; cell-only before load; immediately after RAW load; after explicit
   registration. No coordinate setters or normal test-actor updates are used.
5. Report the final status. The implementation can read console.txt and archived
   DebugLog files for the actual values; `[SS Tests][native-cell-only]` is the prefix.
   No additional restart phase is requested by this test.

PASS requires saved position and marker restored, final correct current square,
moving-object containment, object-list membership without add/remove remnants,
NPC state, unchanged position through registration, and unchanged human identity,
position, singleton, save filename and all four local-player slots. Cleanup must
also succeed; otherwise final outcome becomes INCONCLUSIVE and further tests
are blocked for the session. This does not certify long-term AI, animation,
streaming, death, or production SSR persistence.

The cell-only constructor is full initialization at origin, not an empty shell.
Expected source behavior is centered X/Y=0.5, Z=0, no cell object-list registration
from its zero-coordinate constructor, and currentSquare nil when origin is not
loaded. The probe MEASURES these fields and does not assume origin is unloaded
or that third-party creation hooks leave registration untouched. Constructor
observations are after explicitly setting NPC/block-movement flags, which do not
perform world placement in inspected native code. All actor phases and cleanup
occur before this callback returns; no test actor intentionally survives to a
normal world update.

Registration after verified load uses `setCurrentSquare(savedTile)`, then
`setMovingSquareNow()`, then `cell:addMovingObject(actor)` only when absent.
Each has a separate installed native contract. It never calls IsoCell.LoadPlayer,
player databases, coop/controller setup, generic file factories or singleton/slot
setters. Snapshot files remain in the world with unique test names, as before.
Constructor events can affect other mods; use a disposable world. A constructor
throwing before a handle is returned makes cleanup unverifiable: INCONCLUSIVE,
block new runs, restart. The probe does not search for or delete unfamiliar actors.

Automated evidence: 185 tests passed (including six new mocked cell-only cases
and an installed-JAR constructor/registration check); 112 Lua syntax checks pass.
LuaLS: 88 legacy diagnostics across 13 files, none in the test modules. These
checks do not execute native actor construction or establish in-game PASS.
**USER IN-GAME NOT RUN for SSR-TEST-02 at delivery.**


## SSR-TEST-02 actual result (17 November 2026)

User ran the new cell-only probe. Console records PASSED on B42.22.2 with zero
save offsets. Filtered evidence:
[CELL_ONLY_ISOPLAYER_2026-11-17.log](evidence/CELL_ONLY_ISOPLAYER_2026-11-17.log).
Runtime source 85be6306a77bc32af6fd6586bfdd5dc5f4a875c8, no probe-file changes
in working copy at inspection. Earlier NOT RUN statements describe delivery time.

| Phase | XYZ | current square | Square contains actor | Cell object/add/remove |
| --- | --- | --- | --- | --- |
| Conventional source | 9884.5,12827.5,0 | 9884,12827,0 | true | true/false/false |
| Cell-only constructor | 0.5,0.5,0 | nil | false | false/false/false |
| Immediately after raw load | 9884.5,12827.5,0 | nil | false | false/false/false |
| After explicit registration | 9884.5,12827.5,0 | 9884,12827,0 | true | true/false/false |

The snapshot marker restored. NPC was true in all logged phases. In this run,
cell-only construction did not register in the world, and raw native load did
not place/register the actor. Setting currentSquare to the loaded saved tile,
calling setMovingSquareNow and adding the actor through cell.addMovingObject
established immediate square/cell invariants without changing loaded coordinates.
This verifies the combined explicit sequence in this run; it does not test
omitting each operation or determine a minimal alternative sequence.

Human identity/XYZ/singleton/save filename and all four local-player slots
remained unchanged. Both owned actors were removed from object/add/remove lists
and their currentSquare was nil on cleanup. Files intentionally remain. All
mutation and cleanup occurred at frame 1774, before a normal test-actor update.
There was no associated probe exception/stack trace in the captured log.

This establishes an available reconstruction/explicit-placement route in the
controlled safe callback. It does not establish a simpler/better production
loader, a defect in the saved-tile constructor path, long-term AI/animation,
streaming/death behavior or full SSR persistence acceptance. Z stayed zero;
only X/Y were independently changed by load. No restart roundtrip was requested
or run for this experiment. No production changes are made from this result.
Next actor: orchestrator reviews the measured sequence and decides further work.
