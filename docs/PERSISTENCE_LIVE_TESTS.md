# SSR-PERSIST-01 live acceptance: first restart checkpoint

17 November 2026; SSR-TEST-03. Source branch codex/persistence-b42. Scope is test
implementation, not a production persistence fix. Start with [TESTS_UI.md](TESTS_UI.md).
Historical native-probe findings and logs remain in [NATIVE_POSITION_R1.md](NATIVE_POSITION_R1.md).

## Save boundary and independence

SSRPersistenceTest requires production persistence before appending its OnSave
observer. Installed zombie.Lua.Event.trigger iterates callbacks in registration
order using protected synchronous calls. The observer does not remove, wrap,
replace, reorder or call P.save. Installed GameWindow.save emits OnSave before
GlobalModData's write, as previously verified in installed-JAR checks.

The first reliable sampling point without changing production callbacks is an
observer *inside* actual OnSave, after P.save publishes native snapshot metadata.
It reads actor and registry/group state synchronously; ordinary AI does not tick
between those callbacks. It does not assert it sampled before native serialization.
Other mods' OnSave hooks could still alter state between callbacks, which is a
stated limit when interpreting snapshot/observation mismatches. The native
snapshot is independently re-read after restart to expose such a discrepancy.
A pre-stage actor copy would be stale if AI changed it before saving, and is
therefore explicitly not used as the baseline.

The observer requires a newer published generation than its last captured save,
a matching actor SSRSnapshot and an existing file. Failure invalidates the old
checkpoint. It refreshes at every actual normal save in the staging session;
the last save/exit checkpoint is serialized in the same world's separate test
ModData. New sessions never rearm it or execute comparison automatically.

On resume the production registry initializes and the existing P.tick/loadSquare/
SSM.LoadSurvivor path reconstructs the real actor normally. The test only waits
for/reads it; it never invokes reconstruction to manufacture the outcome.
A temporary native reader independently loads the exact validated filename
SSR_Survivor_<ID>_<generation>.bin, captures native properties and is detached
before the callback returns. It has no intentional world/square membership;
if construction acquires any, the raw-read branch is skipped as inconclusive.
Native reading uses no position/registration repair. The real SSR actor/group
are never removed by test cleanup. Failure before a reader handle returns makes
cleanup unverifiable and blocks further test runs until restart.

Ownership is a new SSR allocation plus unique native ModData/item tokens and
new group ID. Files are accepted only by exact schema/ID/generation naming.
The test does not adopt arbitrary existing survivors, reset allocation counters,
mutate human saves or use native human-loading/player-control helpers.

## What this first delivery does not automate

These follow-ups remain manual until the single fixture restart is observed.
Do not treat unit tests or a single restart result as these results.

| Follow-up | User action in disposable world | Evidence required |
| --- | --- | --- |
| Multiple survivors/groups | Complete first restart; explicitly stage additional fixtures or use normal SSR group UI, then save/restart | Stable distinct IDs and group roster/leader before/after, including at least one empty group; no arbitrary actor cap inferred. |
| Streaming unload/return | Record a fixture's ID/group, travel far enough for its area to unload, then return | Production loaded/unloaded states, latest snapshot pointer, one actor/wrapper per ID on return; exact errors if any. Do not fake streaming by calling unload in a test. |
| Death tombstone | Deliberately kill only an owned fixture using normal gameplay, save and restart/return | Registry dead state, roster removal, no respawn/reused ID; distinguish actual death from missing wrapper. |
| Repeated snapshots | Save the same living fixture several times | Advancing published generations, files exist, prior files remain, no live duplicates. OnSave observer logs generation during staging. |
| World isolation/copy | Use a separate disposable save or copy through normal save management | Registry belongs to that world; no unrelated mod-folder save import. No automatic destructive copy/delete script. |
| Vertical restoration | Run future controlled fixture at an available nonzero floor and document it | Actual Z before/after and meaningful differential; no broad spatial/Z refactor in this assignment. |

If a manual check finds a failure, capture console/registry evidence and send a
separately scoped correction proposal. Do not silently change loader, unload,
index, group persistence or per-tick algorithm under this test assignment.

## Automated checks / unverified runtime

Mock integration tests use production SSPersistence, group manager/group,
survivor manager and loader adapter with mock native actor IO and ordered events.
They exercise real save-boundary sampling, latest-generation refresh, checkpoint
invalidation, restart comparison, duplicate detection, group mismatch, native-file
mismatch, live drift, unloaded tile, missing/invalid files, later-save pointers,
human aliases, reader handle gaps and non-allocating unrelated-object inspection.
Historical native tests run from a tests-only fixture and are not shipped or
registered as current UI entries. No new general test framework was added.

At delivery: actual SSR fixture creation/save/restart/resume, native reader
capture and native UI outcomes are **NOT RUN**. Automated results are reported
separately in the delivery mail; native callbacks/API source were inspected
read-only. Successful prior Tests 1/2 establish only their scoped native facts.


Delivery checks: 199 tests and 112 Lua syntax checks pass in an isolated export
of the staged Git tree, excluding concurrent user source/settings edits. The
working-copy checks also pass. LuaLS reports 88 legacy diagnostics across 13
files, none in SSRPersistenceTest/SSRTestsWindow. Documentation links and prior
evidence preservation checked. Installed JAR SHA256 remains
3c4a7c5f149d784758c6fb5f8fa85f3a21d572e38bc081400e89035f8120d287.
Ignored logs: .venv/test03-index-suite.txt, .venv/test03-final-suite.txt,
.venv/luals-test03-final-result.txt. No native Test 03 PASS is claimed.


## Runtime prerequisite correction (17 November 2026)

User error log revealed production tick calling missing global next(entries)
before a useful restart comparison. Installed Kahlua BaseLib omits global next;
Lua 5.1 mock runtime supplied it, masking the incompatibility. Both global-next
uses in persistence now use a local pairs-based firstKey helper, preserving the
same index/empty-bucket behavior. Iterator/SpiralSearch next methods are unrelated.
[Captured error](evidence/PERSISTENCE_NEXT_ERROR_2026-11-17.log). This is a separate
minimal compatibility fix prompted by actual runtime evidence, not a speculative
persistence rewrite. Added next=nil regressions; 201 tests/112 syntax pass.
Restart the game and retry stage/save/restart/resume; no native success claimed.


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
