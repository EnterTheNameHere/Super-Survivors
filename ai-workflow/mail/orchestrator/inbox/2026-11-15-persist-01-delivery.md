FROM: Local Codex implementer
TO: SSR Orchestrator
SUBJECT: SSR-PERSIST-01 implementation delivery and engine-test checklist
STATUS: DELIVERED FOR REVIEW / AUTOMATED CHECKS PASS / IN-GAME VALIDATION PENDING
DATE: 2026-11-15
CANONICAL COORDINATION REF: B42
IMPLEMENTATION REF: codex/persistence-b42
SOURCE COMMIT: dc4dde25d612d33650c1ed5ef4ad0401c02394b5
SOURCE PARENT: 792a129d6561d5e35fb8ace4c03eb4fd2558f8cd
INITIAL BASE: 3a087ee8c4aceb151443848e19bbc3a999a129f5
ACKNOWLEDGMENT: 792a129d6561d5e35fb8ace4c03eb4fd2558f8cd (also published on B42)

CONTEXT / RESULT:
Implemented fresh-world, single-player persistence using world Global ModData
plus the installed native IsoPlayer file serializer. No legacy loaders/import,
fixed group slots, initial six groups, positional persisted areas, SurvivorLoc
text metadata, mod-directory world writes, render-count saves or Escape saves.
Existing untracked common/ output is untouched and excluded from commits.
No AI manager/debug UI rewrite, Java modification or Workshop publication.

Registry schema 1 has monotonic survivor/group/snapshot allocation, dynamic group
records and named areas, alive/dead/pending records, last observations separate
from native snapshot manifests, and runtime loaded/unloaded/inconsistent status.
The runtime manager owns live wrappers only; unloaded records/member IDs remain.
Scenario groups allocate lazily by name. Native load verifies ID/generation and
uses the matching saved position. Missing/corrupt references and contradictory
memberships are reported; no replacement actor is silently invented. UI fallback
teleport/reload and old file-existence assumptions were removed where necessary.

INSTALLED ENGINE EVIDENCE:
42.22.2 revision 3d39148846; projectzomboid.jar SHA-256
3c4a7c5f149d784758c6fb5f8fa85f3a21d572e38bc081400e89035f8120d287.
Read-only CFR inspection of installed classes under ignored .venv plus the
stdlib JAR parser; no vanilla source or tooling JAR is included in the delivery.
GlobalModData.init loads before OnInitGlobalModData; normal GameWindow.save emits
OnSave before GlobalModData.save. ModData is Lua-exposed. IsoPlayer save/load(String)
exist and delegate native character serialization, including native state needed
for health/inventory/skills/appearance/equipment. Base object ModData persists
identity/generation markers. Missing load(String) silently returns, so explicit
checks are essential. Native corpse handling may delete the current NPC savefile;
dead registry records are never used for spawning. Exact source findings and
reference links are in docs/PERSISTENCE_B42.md ON THE IMPLEMENTATION REF.

VALIDATION ACTUALLY RUN:
PowerShell, repository checkout:
  $env:PZ_GAME_DIR='G:\Steam\steamapps\common\ProjectZomboid'
  .\.venv\Scripts\python.exe -m unittest discover -s tests -q
    161 passed (15 mocked registry integration checks, 2 installed-JAR API/order
    checks, and the remaining existing regression suite).
  .\.venv\Scripts\python.exe tools/check_lua.py
    109/109 runtime Lua files compiled with Lua 5.1; zero failures.
  .\.venv\Scripts\python.exe tools/generate_editor_api.py "$env:PZ_GAME_DIR\projectzomboid.jar"
    regenerated native editor definitions, including ModData/save-root APIs.
  git diff --check
    passed before source commit.
  LuaLS warning check using absolute .venv/luals-options-config.json:
    completed; 88 diagnostics in 13 legacy files. NOT a clean whole-project check.
    No diagnostics in the new persistence module or group manager/model.

IN-GAME VALIDATION ACTUALLY PERFORMED:
NONE for this implementation. JAR inspection and mocks are not engine gameplay
tests or proof of NPC character/streaming round trips. Restart is required to load
the changes. User-led fresh disposable-world verification is still required.

LIMITATIONS / REVIEW POINTS:
- Native characters and Global ModData are not one atomic transaction. Unique
  snapshot filenames avoid overwriting older referenced checkpoints but cannot
  guarantee crash/power-loss consistency. Unsaved allocations/state can roll back
  with the world checkpoint. Orphans are not automatically imported.
- Older generations are retained: disk usage grows on saves/unloads. No speculative
  garbage collection was added. Review this tradeoff before broader release.
- Actual unload timing, pending add/remove handling, character creation ordering,
  native health/inventory/skills/equipment restoration and copy independence need
  engine tests. Failed serialization retains the runtime wrapper for diagnosis.
- No offscreen AI simulation or new goal/task persistence; legacy AIMode rebuilding
  remains. Existing gameplay stat resets/healing may affect live comparisons.
- getMembers() now returns live wrappers; getMemberIDs() retains complete membership.
  Future debug hub must use records for unloaded survivors. No new roster UI here.
- Generated editor artifact was normalized to LF; much of its large textual diff
  is line-ending normalization, not additional native API surface.

REPORT BACK / NEXT ACTOR:
Orchestrator: review exact SOURCE COMMIT and parent, then coordinate the user checks
in docs/PERSISTENCE_B42.md: multiple groups including empty; several distinctive
NPCs; normal save/restart/reload; unload/return; death; repeated saves/new IDs; full
world-folder copy independence and absence of mod-directory dependencies.
Send corrections as NEW addressed mail. This delivery is not acceptance; no
implementation merge into B42 was performed. Debug hub and AI work remain unassigned.

CHANGED FILES AT SOURCE COMMIT:
See `git diff --name-only 792a129d6561d5e35fb8ace4c03eb4fd2558f8cd dc4dde25d612d33650c1ed5ef4ad0401c02394b5`:
- 42/media/lua/client/0_Utilities/SuperSurvivorContextUtilities.lua
- 42/media/lua/client/0_Utilities/SuperSurvivorPersistence.lua (new)
- 42/media/lua/client/0_Utilities/SuperSurvivorTablesUtilities.lua
- 42/media/lua/client/2_Group/SuperSurvivorGroup.lua
- 42/media/lua/client/2_Group/SuperSurvivorGroupManager.lua
- 42/media/lua/client/3_Other/SuperSurvivor.lua
- 42/media/lua/client/3_Other/SuperSurvivorManager.lua
- 42/media/lua/client/3_Other/SuperSurvivorPresetSpawns.lua
- 42/media/lua/client/3_Other/SuperSurvivorUpdate.lua
- 42/media/lua/client/3_Other/SuperSurvivorsMod.lua
- 42/media/lua/client/5_UI/SuperSurvivorMyGroupWindow.lua
- 42/media/lua/client/5_UI/UIUtils.lua
- 42/media/lua/client/Debug/SuperbSurvivorsDebug.lua
- 42/media/lua/shared/Utilities.lua
- docs/LOCAL_HANDOFF.md
- docs/PERSISTENCE_B42.md (new)
- editor/pz-api/library.lua
- tests/test_legacy_save_io.py (removed; legacy contract intentionally retired)
- tests/test_name_fixes.py
- tests/test_persistence.py (new)
- tests/test_persistence_engine_api.py (new)
- tests/test_spawn_isolation.py
- tests/test_startup.py
- tools/generate_editor_api.py
