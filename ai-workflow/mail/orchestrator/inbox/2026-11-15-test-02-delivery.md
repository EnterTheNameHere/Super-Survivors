# SSR-TEST-02 and factory supplement delivery

FROM: Local Codex
TO: SSR orchestrator
STATUS: IMPLEMENTATION DELIVERED FOR REVIEW / USER IN-GAME NOT RUN
DATE: 2026-11-15

Latest user explicitly resumed Test 2 after analysis-only work. Exclusive existing
checkout W:/Projects/Super-Survivors, branch codex/persistence-b42.
Source commit 85be6306a77bc32af6fd6586bfdd5dc5f4a875c8.
Parent / task ACK 8e50dbf95a59d64864353d8795c89d87e937fa6d.
Starting source head fbcf2307beda4efbad58962ca239d0b8b522f792.
Canonical B42 carries coordination only; no source merge or acceptance.

## Installed-source findings

42.22.2 revision 3d39148846, same projectzomboid.jar SHA256:
3c4a7c5f149d784758c6fb5f8fa85f3a21d572e38bc081400e89035f8120d287.
Public IsoPlayer(IsoCell) delegates to five-argument constructor with null desc,
zero coordinates. Full initialization/creation events still run. Base character
centers X/Y=0.5, skips addMovingObject at input zero coordinates, queries origin
square if cell supplied and sets moving-square membership if present. Therefore
object existence, current square and cell membership are distinct observations.
Lua exposure verified via native Exposer/public constructor machinery. No new
native constructor execution claimed from this inspection.

Placement primitives inspected: setCurrentSquare only assigns current;
setMovingSquareNow reconciles old/new moving-square membership; addMovingObject
uses objectList in safe phase, otherwise addList. Probe waits for/rechecks safe
phase and completes all mutation/cleanup before callback returns. No coordinate
setters or actor:update, and no test actor intentionally survives to normal AI.

Factory supplement: CreateSurvivor returns descriptor; InstansiateInCell returns
IsoSurvivor. Generic IsoObject ID-1/header factory constructs IsoPlayer(cell),
not full native load/registration. IsoCell.LoadPlayer imports human map_p state,
mutates singleton/slots/chunk map and DB/files. IsoWorld.init and LuaManager
setPlayerMouse/setPlayerJoypad wire humans/controls/world; private addPlayerToWorld
is integration, not isolated-NPC-returning factory. PlayerDB/network consumers
serve player records. No dedicated fully prepared arbitrary NPC-returning factory
identified in the 23,692-class constructor-reference inventory and followed paths;
not a universal absence claim. Probe calls none of those human-loading helpers.
Detailed signatures/source references and limits: docs/NATIVE_POSITION_R1.md.
IsoSurvivor migration stays rejected, independent of this test.

## Delivered probe and safeguards

New fourth registry entry native-cell-only, exact title:
Native IsoPlayer - cell-only construction and placement.
Existing Debug Options / single-player gate, warning, consent and one-active-run
control reused. It is not the earlier second restart-stage entry.

Creates conventional isolated source, writes uniquely named native snapshot,
then invokes exactly IsoPlayer.new(cell) for destination. Logs conventional
source, cell-only pre-load, raw-load and explicit-registration phases, including
XYZ/square coords, square containment, NPC flag and world/add/remove membership.
Does not presume initial cell-only actor is unregistered or origin unloaded.

Only after matching loaded position/marker and human guards, exact saved tile
must remain loaded with floor and no unexpected pending cell lists. Applies
setCurrentSquare(saved tile), setMovingSquareNow, then addMovingObject only if
absent. PASS requires correct final cell/square membership, unchanged coordinates,
marker/NPC/human guards and verified cleanup. Human guard now includes all four
local-player slots in addition to identity/XYZ/singleton/save filename. No slot,
singleton or human restoration setters are used. No SSR IDs/registry writes.
All returned nonlocal actors owned before further calls; cleanup is best effort
and verified. Constructor throw before handle -> inconclusive/unverifiable cleanup,
block further runs and require restart; never hunt/delete unfamiliar actors.
Native character events/other mods remain a documented risk. Snapshot files stay;
no native removeSaveFile or arbitrary file loading. No restart phase added.

## Validation

PZ_GAME_DIR=G:/Steam/steamapps/common/ProjectZomboid.
.venv/Scripts/python.exe -m unittest discover -s tests -q: 185 passed.
.venv/Scripts/python.exe tools/check_lua.py: 112/112 Lua 5.1 compile.
Six new mocked cell-only guardrail scenarios plus native JAR signature/delegation
check. Implicit constructor membership/no duplicate add, load/placement failure,
missing moving membership, unreturned handle and nonzero local-slot changes covered.
Existing first-probe behavior remains tested; mocks do not execute the engine.
LuaLS: 88 existing diagnostics in 13 legacy files, none test modules.
Editor API regenerated for used placement primitives. Changed-path whitespace
and documentation checked. Native test NOT RUN; no UI/engine PASS claimed.
No production SSR loader/scan/unload/group persistence changes. Concurrent user
source/settings/save edits preserved and excluded.

## User steps / report back

Restart game. Enter disposable B42.22.2 normal-save single-player world with
one living local player; enable Superb Survivors -> Debug Options -> On.
Right-click SS Tests..., choose Native IsoPlayer - cell-only construction and
placement, read requirements/warning, acknowledge, Run. Share final status; local
Codex reads console.txt / archived DebugLog for [SS Tests][native-cell-only].
Do not run a new restart cycle for this experiment. Detailed docs/TESTS_UI.md.
Result distinguishes immediate reconstruction/registration, not prolonged AI,
streaming, death or full SSR persistence acceptance. Await actual user logs.

Changed source paths:
- 42/media/lua/client/Testing/SSRNativePositionTest.lua
- docs/LOCAL_HANDOFF.md
- docs/NATIVE_POSITION_R1.md
- docs/TESTS_UI.md
- editor/pz-api/library.lua
- tests/test_persistence_engine_api.py
- tests/test_tests_ui.py
