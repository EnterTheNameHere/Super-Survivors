# SS Tests: real SSR persistence roundtrip

17 November 2026. SSR-TEST-03 on codex/persistence-b42. Existing native diagnostic
entries are retired; [their instructions](archive/NATIVE_TESTS_UI_2026-11-15.md),
[findings](NATIVE_POSITION_R1.md) and captured evidence remain. No production
persistence algorithm or actor backend is changed by this assignment.

## Run the test

1. **Restart the game** to load the new definitions. Use installed B42.22.2, a
   disposable save-enabled single-player world and one living local human.
2. Enable **Options -> Superb Survivors -> Debug Options -> On**. No -debug
   parameter required. Enter gameplay and stand in an open, quiet loaded area.
3. Right-click **SS Tests...**, select **SSR persistence - stage one survivor and
   group**, read the warning, acknowledge and Run.
4. Staging creates one real SSR survivor/group, token-marked pencil/hammer,
   equipped hammer and Axe XP. It deliberately leaves the fixture in the world.
   The result is **INCONCLUSIVE: staged**, not a persistence pass. Its ID/group
   and instructions appear in the window and console. Do not edit the fixture,
   change its group, leave the area or put it in danger.
5. Close the window, **save and exit normally**, then fully close the game.
   The armed observer captures the baseline during the actual OnSave event,
   after production persistence publishes its snapshot. There is no forced save.
   Closing the window does not cancel this armed save observation.
6. Restart, Continue the same world, then promptly open SS Tests. Select
   **SSR persistence - resume (I fully restarted the game)**, acknowledge and Run.
   Selecting/running this entry explicitly confirms a full game restart. A new
   Lua token alone cannot prove a process restart. Nothing auto-runs on startup.
7. Report the outcome; Codex reads console.txt and archived DebugLogs. Log prefix:
   **[SS Tests][ssr-restart-stage]** / **[SS Tests][ssr-restart-resume]**.

Run attempts consume acknowledgment; switching choices preserves it as requested.
Reopening clears it. One active run at a time. The irreversible-world warning
is unchanged. Debug Options off, multiplayer, no-save worlds, unsupported builds
and unknown/nonzero world save offsets are unavailable. Wait for SSR managers
and the real player wrapper if initialization is incomplete.

## What is compared

The test manifest is separate world ModData containing only serialized observations,
fixture ownership IDs/token and a pointer copied from production at OnSave. It is
not a replacement registry, does not force reconstruction and cannot manufacture
a snapshot generation. Each actual normal save in the staging session refreshes
the checkpoint, so save/exit's final generation is the expected one.

The resume reads the exact checkpoint file into an isolated, unplaced native
reader using the already investigated cell-only route; it removes that reader
before a normal update. Separately it inspects the ordinary SSR registry/group
and normally reconstructed wrapper/actor. It never calls the production loader,
P.save, human-loading helpers, player-slot setters or singleton setters.

Property logs show expected/actual/match for ID, native identity/generation,
ownership token, name/descriptor name, group/role, XYZ, bounded recursive inventory
(full type/count/condition/token), primary/secondary equipment, worn item types,
Axe XP/level, aggregate body health and dead state. Hunger/thirst are observed,
but live need equality is not a pass gate because ordinary simulation continues.
Individual wounds, every skill, visual appearance and every item-specific field
are not certified by this first narrow test. Inventory capture is limited to
256 items and four levels; exceeding it is a setup/capture error.

Registry snapshot position/name/group/role, complete saved group record plus
runtime roster/leader, square/world membership and actor/wrapper/record counts
are compared independently. Duplicate counting uses hasModData before reading
unrelated moving objects, avoiding empty ModData allocation on them. Human
identity/position/singleton/save filename and all four local slots are guarded.
Actual Z is logged; no forced vertical differential is claimed.

- **PASSED:** measured native snapshot, registry/group and live reconstructed
  state match this checkpoint, counts/membership and human/reader cleanup pass.
- **FAILED:** a concrete checkpoint/property/count/metadata comparison failed,
  or production reported a loading issue. Inspect logs before attributing a
  production bug; other OnSave hooks or later interactions may explain differences.
- **INCONCLUSIVE:** staging only; unloaded saved tile; newer snapshot pointer;
  fixture death; or live drift after restart while the native checkpoint matches.
  AI may move/equip the survivor before you click resume. No automatic freeze or
  comparison is installed on startup to hide that uncertainty.
- **SETUP ERROR:** missing prerequisites, invalid/unavailable API or unexpected
  exception. Unverifiable native cleanup changes the result to INCONCLUSIVE and
  blocks more runs until restart.

If a new save happened after restart before resume, the record may point to a
newer generation. This is inconclusive, not permission to force an old snapshot
into the real actor. If the saved tile is unloaded, travel back and explicitly
retry. If stage reports a save-capture error, the old checkpoint is invalidated;
inspect the log and save again in the same session or stage a new fixture.

Real fixture survivors/groups/items and all production snapshot generations
remain. No automatic cleanup removes them, no ID is recycled, no other actor is
searched for deletion. A completed comparison permits another explicit stage,
creating a new fixture; older fixtures remain. Delete the disposable world when
finished. Use the normal game UI for any manual cleanup you deliberately choose.

**Actual SSR-TEST-03 in-game execution: NOT RUN at delivery.** Automated mocks
and installed-source inspection are not native end-to-end acceptance.
See [detailed lifecycle coverage](PERSISTENCE_LIVE_TESTS.md).


## Actual first restart result (17 November 2026)

**INCONCLUSIVE overall due to live position drift; positive native/metadata
roundtrip evidence.** Filtered [stage/OnSave/resume log](evidence/SSR_RESTART_2026-11-17.log).
The prior global-next exception did not recur in this captured session. No probe
exception occurred; unrelated startup font/vehicle/map errors remain.

Stage created real SSR survivor ID 2 / group 3. Actual OnSave at 09:03:21
published SSR_Survivor_2_4.bin, generation 4. After the restart-confirmation
resume action, the native reader restored every compared baseline property.

| Observation | Expected / native snapshot | Reconstructed actor at comparison |
| --- | --- | --- |
| Identity / generation | ID 2 / generation 4 | Match |
| Group / role / name / ownership marker | Group 3; recorded role/name/token | Match |
| Inventory, primary/secondary, worn item types | Token-marked pencil/hammer plus original clothing; equipped hammer | Match |
| Position XYZ | 9885.5,12824.5,0 | 9888.5,12828.3349609375,0 |
| Axe XP / level | 0 / 0 | Match, but no nonzero skill differential |
| Aggregate health / dead | 100 / false | Match, but no injury/health differential |

Registry snapshot metadata and saved group record/runtime roster/leader matched.
Actor/wrapper/registry counts were exactly 1/1/1, square/world membership passed,
human identity/XYZ/singleton/save filename/all four slots remained unchanged,
and the temporary native reader was detached. Only live X/Y comparisons failed.

The result is consistent with AI movement before explicit resume, but this run
has no first-reconstruction position observation to prove when the change
occurred. Do not upgrade it to PASS, infer data loss, or change loader coordinates
from this evidence. There is no full lifecycle acceptance: streaming, death,
multiple/empty groups and differential Z remain untested.

Axe XP was already zero in the actual save baseline despite the setup's AddXP
attempt. This run therefore does not independently validate nonzero XP retention;
review test setup/native XP rules before claiming that coverage. No skill or
movement behavior is changed in this record-only update. Orchestrator should
review whether an earliest read-only observation or a new bounded fixture control
is warranted; do not silently suppress movement comparisons to manufacture PASS.
