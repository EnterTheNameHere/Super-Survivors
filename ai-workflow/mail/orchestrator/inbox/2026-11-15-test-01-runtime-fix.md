# SSR-TEST-01 runtime version gate correction

FROM: Local Codex
TO: SSR orchestrator
SUBJECT: User-reported disabled Run; full build API correction and consent preference
STATUS: FIX DELIVERED FOR REVIEW; actual native roundtrip NOT RUN

Source: codex/persistence-b42, commit 4164ad7bead8d6dd2d7db3c6e514e7c9acb52a42.
Parent: 5f215b056cf00908a6c84a95dfa4dde89348fef2.
Canonical B42 remains coordination only; no production merge or acceptance.

User observed SS Tests opens, but acknowledging still leaves Run disabled.
Reported Availability: probe reviewed for B42.22.2 only. Installed JAR/hash and
revision match original inspection. Read-only Core source confirms GameVersion
is 42.22; getGameAndBuildVersion appends .2. The probe incorrectly compared
GameVersion.toString() with the full build string. It now uses the actual full
build API, retains exact 42.22.2 restriction, and reports detected mismatches.

User explicitly requested checkbox persistence when selecting a different test,
superseding that part of original assignment. Selection/registry refresh now
preserve it; reopening, run attempt and cancel still clear it. Disabled Run
shows its reason in output and tooltip. No persistence lifecycle rewrite.

Validation: 177 automated tests with installed-JAR checks, 112 Lua syntax checks,
staged diff whitespace check passed. Regression models GameVersion as 42.22 and
full build as 42.22.2; other builds remain blocked. No new LuaLS run claimed.
Unrelated local source/settings/save edits excluded; whole-worktree whitespace
check reports existing unrelated SuperSurvivor.lua edits, staged delivery clean.

Restart game to load changes, then retry in disposable world. Actual native
roundtrip still pending; UI opening is the only user runtime evidence so far.

Changed paths:
- 42/media/lua/client/5_UI/SSRTestsWindow.lua
- 42/media/lua/client/Testing/SSRNativePositionTest.lua
- docs/LOCAL_HANDOFF.md
- docs/NATIVE_POSITION_R1.md
- docs/TESTS_UI.md
- editor/pz-api/library.lua
- tests/test_persistence_engine_api.py
- tests/test_tests_ui.py
- tools/generate_editor_api.py
