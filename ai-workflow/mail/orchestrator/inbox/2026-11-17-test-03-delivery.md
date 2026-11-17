# SSR-TEST-03 delivery: one real SSR restart checkpoint

FROM: Local Codex
TO: SSR orchestrator
STATUS: IMPLEMENTED / DELIVERED FOR REVIEW; USER IN-GAME NOT RUN
DATE: 2026-11-17

## Refs and ownership

Exclusive existing W:/Projects/Super-Survivors checkout, codex/persistence-b42.
Source commit e6f08e05b3ec3805a1c8394d8de2f7dab8e261d9.
Parent / ACK 4d5002e816e7a5cc3aca9a5d1a708913299153ec.
Starting source 773f482537750fbc3b36d263563443044f0fba1c.
Canonical B42 coordination only; no implementation merge, acceptance or Workshop
publication. Unrelated user source/settings/save edits preserved and excluded.

## Current test surface

Replaced the four visible native-only diagnostics with two entries using the
existing development-gated SS Tests window/registry:
1. SSR persistence - stage one survivor and group
2. SSR persistence - resume (I fully restarted the game)

Native probe implementation moved unchanged to tests/fixtures, not packaged or
registered in the current game UI. Historic UI instructions preserved under
docs/archive, findings and all captured native evidence unchanged. Existing
warning, per-run consent/reset rules, single-active-run control and statuses kept.
No new general runner/framework or debug hub.

Stage uses ordinary SSM:spawnSurvivor, SSGM:newGroup, group member/leader APIs;
new identity/group plus unique actor/item token, pencil, equipped hammer and
Axe XP. Real fixture intentionally remains under production SSR management.
No automatic deletion or ID recycling, and no human loading/control helpers.
It waits for a native safe-to-add callback, guards human state/all four slots,
and does not force SSPersistence.save or reconstruction.

## Actual save boundary, not staging fiction

Staging ends INCONCLUSIVE with instructions. A transient armed session observes
ACTUAL OnSave after requiring production persistence; no callback removal,
reordering, wrapping or direct P.save call. Installed Event.trigger dispatch is
synchronous in callback order; GameWindow.save writes GlobalModData after OnSave.
The observer samples actor/registry/group after production publishes its native
snapshot, not before serialization or at the earlier staging click. No normal
AI tick occurs between these callbacks. Other OnSave hooks could intervene;
this limitation is explicit rather than asserting a nonexistent pre-save sample.

Requires newer published generation, actor snapshot marker and existing native
file; failure invalidates older checkpoint. Every actual normal save in the
staging session refreshes the manifest, covering final save/exit generation.
Own serializable world test manifest records observed state and production pointer;
it does not substitute for registry/native persistence. Closing window preserves
armed observation. New session never auto-rearms or runs/resumes a test.

Resume requires a different Lua token and explicit full-restart confirmation by
selecting/running the clearly named entry, plus fresh warning consent. Token
change alone is not claimed as proof of process restart. The exact validated
production snapshot is independently read into an isolated cell-only native
reader, removed before a normal update. The real actor is reconstructed only by
ordinary production code; test waits/reads and never calls LoadSurvivor/loadSquare.
Real actor/count observations occur after reader removal to avoid counting a
transient duplicate-ID reader. Unsettled/unexpected reader membership skips raw
read as inconclusive. Handle gaps/cleanup failure block future runs until restart.

## Comparisons, statuses and limits

Expected/actual/match lines cover native ID/identity/generation, token,
name/descriptor name, group/role, XYZ, bounded recursive item type/count/condition/
token, primary/secondary and worn item types, Axe XP/level, aggregate health/dead.
Hunger/thirst logged as observations, not live equality gates. Not every wound,
skill, visual or item field is certified. Inventory cap 256 items/four levels.
Registry snapshot position/name/group/role, full saved group record plus runtime
roster/leader, world/square membership, actor/wrapper/record counts compared.
Duplicate counting checks hasModData first to avoid allocating empty ModData on
unrelated objects. Human identity/XYZ/singleton/save filename/all four slots guarded.
Z logged; no forced vertical differential claimed.

PASS only on matching measured native/metadata/live properties, memberships,
counts and guards/reader cleanup. Concrete native/metadata/count mismatches FAIL
with layer-specific property logs; attribution still requires considering other
hooks/world interaction. Matching checkpoint but live drift/movement is
INCONCLUSIVE, as is changed generation after a later save, unloaded tile or fixture
death. Setup failures explicit. Tests never silently repair production state.
Real fixtures/groups/items/files remain; only the owned temporary reader removed.

Broader multiple/empty groups, streaming unload/return, death tombstones, repeated
save generations, world-copy/isolation and vertical checks documented manually
in docs/PERSISTENCE_LIVE_TESTS.md, not reported as executed or automated.

## Validation

PZ_GAME_DIR=G:/Steam/steamapps/common/ProjectZomboid.
Installed 42.22.2 revision 3d39148846; JAR SHA256 unchanged:
3c4a7c5f149d784758c6fb5f8fa85f3a21d572e38bc081400e89035f8120d287.
Native API/Event/save ordering read-only inspection; no Java modifications.

- .venv/Scripts/python.exe -m unittest discover -s tests -q: 199 passed.
- tools/check_lua.py: 112/112 Lua 5.1 compile.
- Both passed in isolated export of staged Git tree, excluding unrelated user
  edits; working-copy checks also pass. Fourteen new integration/guardrail tests
  use real persistence/group/manager/loader Lua with mocked native IO/events.
- LuaLS: 88 legacy diagnostics in 13 files, none new test/UI modules. Not globally
  clean. Regenerated editor API against isolated intended runtime source.
- Changed-path whitespace/docs links checked; historical evidence unchanged.
- Actual Test 03 native fixture/save/restart/resume NOT RUN. Mocks are not engine
  acceptance. Production loader/registry/unload/index/per-tick files unchanged.

Ignored logs: .venv/test03-index-suite.txt, test03-final-suite.txt,
luals-test03-final-result.txt. Source/detailed docs: docs/TESTS_UI.md,
docs/PERSISTENCE_LIVE_TESTS.md, docs/LOCAL_HANDOFF.md.

## User instructions / next actor

Restart game. Enter disposable B42.22.2 normal-save single-player world; enable
Options -> Superb Survivors -> Debug Options -> On. In quiet open area, right-click
SS Tests..., select stage one survivor/group, acknowledge and Run. Staging is
INCONCLUSIVE pending save. Close window; save/exit normally, fully close/restart
and Continue SAME world. Promptly select resume (I fully restarted the game),
acknowledge and Run. Do not interact with fixture or travel away before saving.
Share outcome; Codex reads [SS Tests][ssr-restart-stage/resume] console/DebugLog.
No further implementation starts automatically; orchestrator reviews actual results.

Changed paths (source commit):

M	42/media/lua/client/5_UI/SSRTestsWindow.lua
A	42/media/lua/client/Testing/SSRPersistenceTest.lua
M	docs/LOCAL_HANDOFF.md
M	docs/NATIVE_POSITION_R1.md
A	docs/PERSISTENCE_LIVE_TESTS.md
M	docs/TESTS_UI.md
A	docs/archive/NATIVE_TESTS_UI_2026-11-15.md
M	editor/pz-api/library.lua
R100	42/media/lua/client/Testing/SSRNativePositionTest.lua	tests/fixtures/SSRNativePositionTest.lua
A	tests/test_persistence_lifecycle.py
M	tests/test_release_package.py
M	tests/test_tests_ui.py
