# SSR-PERSIST-01: fresh-world B42 persistence

Implementation branch: `codex/persistence-b42`, based on B42
`3a087ee8c4aceb151443848e19bbc3a999a129f5`. Date: 15 November 2026.
Target: installed **42.22.2, revision 3d39148846**, single-player.
Inspected projectzomboid.jar SHA-256:
`3c4a7c5f149d784758c6fb5f8fa85f3a21d572e38bc081400e89035f8120d287`.

This implements the persistence assignment. It does not implement the proposed
AI manager, SS Debug hub, inspector or test UI. No Java game files were modified.
No old saves or experimental B42 metadata are imported. Test a fresh disposable
world; restarting the game is required to load the new definitions/callbacks.

## World-owned state

`SSPersistence` owns `ModData.getOrCreate("SuperSurvivorsReloaded.Registry")`.
The engine stores it in the world's `global_mod_data.bin`. Its schema contains:

- `schema = 1`, monotonic `nextSurvivorID`, `nextGroupID`, `nextSnapshot` counters.
- `survivors[id]`: identity, name, kind, alive/pending/dead state, group/role,
  last-observed position/time, matching native snapshot manifest, and issues.
- `groups[id]`: stable identity, member IDs, leader, ROE, warnings, named areas and
  bounds. Persisted rectangles use x1/x2/y1/y2/z fields. Existing gameplay code
  retains its runtime rectangle-array interface; areas are never flattened by
  unordered iteration.
- `scenarioGroups[name]`: identities created lazily when a preset needs them.
- `checkpointWorldHours`: the last completed registry preparation callback,
  **not** confirmation that the engine successfully wrote the world afterward.

Survivor ID zero is reserved for the human player's wrapper, whose character
save is owned by vanilla. NPC IDs start at one; group IDs start at zero. Failed
construction consumes an identity rather than recycling it. Tombstones retain
dead NPC identities. Initializing the managers creates no default groups. The
ordinary player initialization may create the player's group; preset scenario
groups are allocated only when needed.

`SSM.SuperSurvivors` contains live wrappers only. `SSM:getRecord(id)` and
`SSM:getState(id)` expose known records and loaded/unloaded/dead/inconsistent
status without constructing an IsoPlayer. Loaded status is runtime-only; all
non-dead persisted records start unloaded on a new session. Group `getMembers()`
returns live wrappers; `getMemberIDs()` retains the full roster including
unloaded members. An unloaded leader remains a leader.

## Native characters and save ordering

`OnInitGlobalModData` binds and validates the registry after native loading.
`OnSave` writes live NPCs with the installed `IsoPlayer:save(String)` serializer,
then prepares group/registry metadata. The normal native save continues and
writes Global ModData. There is no registry autosave tied to render counts or
the Escape key. Options remain separately stored user preferences.

Snapshot names are relative to the current world:
`SSR_Survivor_<id>_<generation>.bin`. The absolute write/load path uses the
engine save root, current game mode and world. No absolute paths are persisted,
so copying the complete save folder carries the registry and snapshots together.

Every new snapshot gets a unique generation filename. The registry pointer is
updated only after the synchronous native save returns and its file exists.
Loading verifies saved ID and generation markers from native character ModData,
and uses the snapshot's matching saved position, not a newer observation. Missing,
invalid or mismatched snapshots are reported and withheld from automatic loading;
no replacement NPC is silently generated. Group contradictions are also reported.

`lastObserved` can be newer than `saved`; it is not proof that newer character
state reached disk. The registry is serializable data only, with no live Java
objects. Runtime loading maps/indexes live outside Global ModData. Coordinate
index keys have separators, avoiding ambiguous coordinate concatenation.

`OnTick` tracks live objects, including pending native additions/removals. An
unloaded actor is stopped, its task/native-action ownership released, saved, then
detached from the runtime manager. Its record and group membership remain. When
the matching square is available, it can load once. Initial squares loaded
before the human wrapper exists are also checked. Death is recorded before the
old optional death-loot hook, removes membership and prevents reloading that NPC.

## Installed-engine evidence

Read-only inspection/decompilation of the installed JAR, held under ignored
`.venv/persistence-decompiled`, established:

- `GlobalModData.init()` resets, loads, then emits `OnInitGlobalModData(newGame)`.
  `ModData` is the exposed Lua wrapper; both get/getOrCreate exist.
- `GameWindow.save` emits OnSave before cell/world and Global ModData saving.
  Global ModData writes a temporary file and copies it to the final file; this
  is not an atomic transaction spanning the registry and character files.
- `IsoPlayer.save(String)` validates the path, writes native version 251 and
  delegates character encoding. `load(String)` silently returns if missing,
  which is why existence and identity checks are required.
- `IsoGameCharacter` encodes descriptor/appearance, inventory, stats, body damage
  and XP. IsoPlayer additionally restores worn locations and hand-item references.
  Base IsoObject serialization includes character ModData. These are source
  findings; preservation during an actual engine round trip still needs testing.
- `checkSaveFileExists` resolves against the current world. The exposed
  getAbsoluteSaveFolderName resolves against the engine save root.
- `IsoPlayer.removeFromWorld` handles world/sound removal; native corpse code can
  call removeSaveFile, which can delete an NPC's current snapshot. Dead records
  do not depend on that file for respawning.

References consulted as requested, secondary to installed evidence:
[official GlobalModData API](https://projectzomboid.com/modding/zombie/world/moddata/GlobalModData.html)
and [event reference](https://demiurgequantified.github.io/ProjectZomboidLuaDocs/md_Events.html).

## Limits and risks

- **No in-game engine validation has been performed for this implementation.**
  Automated tests exercise production Lua with mocked native IO and actors.
  They do not prove engine animation, chunk lifecycle or serializer round trips.
- Character files and the world registry are not atomic together. An interruption
  can leave unused newer files or roll back to the last world checkpoint. The
  native world-file write can itself fail. No crash-proof or power-loss guarantee.
- Old generations are deliberately retained. Save-folder disk use grows with
  saves/unloads. No automatic garbage collection or orphan-file recovery is
  implemented; deleting files speculatively could destroy a referenced checkpoint.
- An interrupted native save can leave a partial orphan. Native checks plus
  generation identity prevent silently treating a failed load as a fresh NPC.
  A manually corrupted matching snapshot may still fail native loading.
- Last-known records do not simulate offscreen AI. There is no new goal/task
  serialization; existing AIMode reconstruction remains. Normal legacy gameplay
  still changes/heals stats in ways outside this persistence assignment.
- Native unload timing, collision/streaming and character creation event ordering
  need live validation. A save failure intentionally leaves the wrapper available
  for retry/diagnosis rather than discarding its state.
- Unsupported schemas stop initialization. There is no compatibility fallback.
  No multiplayer persistence/authority contract is provided.
- Existing common/ legacy save output was left untouched as user data and is not
  read or committed. Releases package common/media only, not these files.

## Automated validation at delivery

PowerShell, from the implementation checkout:

```powershell
$env:PZ_GAME_DIR = 'G:\Steam\steamapps\common\ProjectZomboid'
.\.venv\Scripts\python.exe -m unittest discover -s tests -q
.\.venv\Scripts\python.exe tools/check_lua.py
.\.venv\Scripts\python.exe tools/generate_editor_api.py "$env:PZ_GAME_DIR\projectzomboid.jar"
git diff --check
```

Results: **161 tests passed**, including 15 registry integration checks with
mocked IO/actors and two installed-JAR API/order checks. **109/109 runtime Lua
files compile as Lua 5.1**. Whitespace checks pass. Editor definitions were
regenerated from the installed JAR, including ModData and the engine save-root
resolver. The generator writes predictable LF output on Windows.

LuaLS warning-level inspection completed with 88 diagnostics across 13 legacy
files; this is not a clean whole-codebase diagnostic result. No diagnostics were
reported in the new persistence module or group manager/model. Existing optional
mod globals, copied vanilla overrides and subtype-related diagnostics remain
outside this assignment. Logs are local ignored `.venv/persistence-delivery-suite.txt`
and `.venv/luals-persistence-final-result.txt`.

## Disposable-world verification for the user

Use the linked development checkout and restart the game. Create a **fresh**
single-player disposable world. `-debug` is useful for the existing Lua console;
the new registry itself does not depend on it. Keep item/character mods constant
between saves. Do not use the old experimental world as a migration test.

1. After entering, run `print(SSPersistence.get().schema)`; expect 1. Record
   `SSGM:getCount()` and existing IDs; there must not be six automatic groups.
   The human's ordinary group may already exist.
2. Create two additional groups, including one left empty:
   `SSRGroup = SSGM:newGroup(); SSREmptyGroup = SSGM:newGroup()`.
   Print their IDs. Set distinct areas:
   `SSRGroup:setGroupArea("GuardArea", 10, 12, 20, 22, 0)` and
   `SSRGroup:setGroupArea("CustomZone", 30, 32, 40, 42, 1)`.
   These sample areas are for metadata checking, not work orders.
3. Spawn several NPCs in free nearby tiles with the existing
   `SuperbSurvivorsDebug.spawn()` helper. Record their IDs; add at least one via
   `SSRGroup:addMember(SSM:Get(id), "Guard")` using its actual numeric ID.
   Put distinguishable items/clothing on them, equip a weapon and record skill
   levels/XP, appearance, health, name, group/role and position. Keep them nearby
   and stationary if needed to avoid legacy healing/AI obscuring the comparison.
4. Save/exit normally, restart, reload. Inspect records with
   `SSM:getRecord(id)` and status with `SSM:getState(id)`; visit their saved
   positions for loading. Compare the character fields above and both named
   areas; confirm the empty group survives. Search console.txt for persistence
   issues. A last-observed position is not a substitute for the saved position.
5. Travel far enough to unload the NPCs' area. Confirm live wrappers disappear
   while records/member IDs remain and status is unloaded. Return; verify one
   actor per ID and matching state. Do not equate camera distance with chunk
   unloading; confirm the reported state.
6. Kill one NPC in this disposable world. Record its dead status, save/exit and
   reload. Return to its location: it must not respawn, and its group must not
   retain it as a living member. Native corpse inventory is separate.
7. Repeat normal saves and spawn another NPC. IDs must not duplicate a living,
   unloaded or dead record. Files named SSR_Survivor_* should be in the actual
   world folder; no new SurvivorLoc*/SurvivorGroup* world metadata should appear
   under the mod directory. Options preference writes are unrelated.
8. With the game closed, copy the **complete world-save folder** to another save
   slot. Load the copy, change an NPC's inventory and save. Load the original
   and verify it is independent. No common/ metadata copy is needed.

Report real results separately for each step, including any errors and whether
the NPC was loaded at the time. This is implementation delivery for review,
not acceptance or proof of those live outcomes.
