# SSR-TEST-01 and SSR-PERSIST-01 R1 delivery

FROM: Local Codex implementer
TO: SSR orchestrator
SUBJECT: Opt-in Tests UI, native position probe and installed-engine findings
STATUS: DELIVERED FOR REVIEW; actual in-game validation NOT RUN
DATE: 2026-11-15

## Relevant refs and ownership

Canonical coordination: B42. Exclusive existing checkout: W:/Projects/Super-Survivors.
Implementation branch: codex/persistence-b42.
Source commit: 594e65bc6af92927d8ec2c4b20c5c36806bf31a3
Source parent / assignment acknowledgment: c1dea17a8f052a8e861635a86eec1619e791035e
Previous delivery/starting ref: d585676e1679fb1505bb6779bf57bff06fb58d6a.
Prior persistence source: dc4dde25d612d33650c1ed5ef4ad0401c02394b5 (still under review).
No implementation merge to B42, acceptance or Workshop publication is implied.
Unrelated working-copy changes were excluded from this delivery.

## Delivered behavior

Existing Options -> Superb Survivors -> Debug Options -> On enables the root
right-click entry SS Tests... in single-player, one viewport, player 0. No -debug
parameter required. Default/missing option is off. Native controller preview uses
ISWorldObjectContextMenu.setTest() without opening or executing tests.

Window shows the approved warning, test description, risk, requirements,
availability, observed values and outcomes. Consent is affirmative per run and
cleared on opening, selection changes and every run attempt. Only one active
multi-tick test; cancel/close, option changes and world changes stop it.
Independent registry definitions own execution; UI has no diagnostic-specific
button logic. Cleanup failure makes the result inconclusive and blocks further
runs for the session. No broad debug hub, AI manager or general scheduler.

The native diagnostic has three explicit entries: same-session roundtrip,
stage restart, and resume staged snapshot. It uses isolated nonlocal NPCs with
fresh descriptors, no SSR IDs, unique checked native filenames and its own
manifest key. It never assigns human/player slots, manually restores loaded
coordinates/square, deletes native saves or calls actor:update(). It records
original/constructor/restored XYZ, square association, membership, marker,
missing-file behavior, human invariants and verified cleanup.

Only inspected engine 42.22.2 is allowed; normal save-enabled world, living
single local player, known zero world offsets, loaded free tiles and native
safe-to-add phase are prerequisites. Files remain intentionally. If constructor
registration throws before returning its handle, cleanup cannot be verified:
report inconclusive, block further runs, require restart rather than deleting
arbitrary actors. Native creation events and other mods remain environmental
risks; use a disposable world.

PASS concerns measured position/marker restoration and guards, not correct
post-load square association or end-to-end SSR persistence. Same-floor Z does
not independently distinguish Z restoration. The session token only establishes
a new Lua session; the user must actually close/restart the game to establish
a process restart. Staging finishes inconclusive with instructions, never auto-
resumes, and resume requires fresh consent.

## R1 engine investigation

Installed engine: 42.22.2 revision 3d39148846.
projectzomboid.jar SHA256:
3c4a7c5f149d784758c6fb5f8fa85f3a21d572e38bc081400e89035f8120d287.
Read-only native inspection; no Java modification.

Established from installed source: IsoMovingObject saves XYZ and actor ModData;
load assigns XYZ (XY include save offsets) but does not reconcile current or
moving square membership. Construction registers the actor at its constructor
square; this is distinct from positional deserialization. The five-argument
IsoPlayer constructor does not itself claim players[] or the singleton. Native
snapshot save temporarily changes the singleton and restores it in finally.
Missing-file load returns silently.

IsoCell uses immediate/deferred object lists according to safeToAdd. Normal
OnTick follows cell update, but the probe checks the actual flag. Native cell
removal paths skip living IsoPlayers in some cases; flags alone are not proof
of terminal removal. Chunk teardown already detaches actors. Grid-square
lookup is bounded and does not load chunks; references may be invalidated or
recycled. Startup/streaming ordering supports investigating an event-driven
index plus one catch-up after readiness, but the scan has no measured bottleneck.

No persistence scan, unload or loader rewrite was made for R1. Manual setters
in current SSR loader are not proof of necessity; their removal or lifecycle
redesign requires observed results and review. Full findings and caveats:
docs/NATIVE_POSITION_R1.md on the source branch.

## Validation actually performed

- PZ_GAME_DIR set to installed G:/Steam/steamapps/common/ProjectZomboid.
- .venv/Scripts/python.exe -m unittest discover -s tests -q: 174 passed.
- .venv/Scripts/python.exe tools/check_lua.py: 112/112 Lua 5.1 compile checks.
- Installed-JAR serializer/API tests included; mocked UI/probe tests separately
  exercise gate, consent, lifecycle, raw restoration, cleanup and restart flow.
- Editor API regenerated from installed JAR; IsoPlayer.saveFileName explicitly
  curated string|nil. English JSON valid; documentation links checked.
- git diff --check passed. Reviewed persistence scan/loader unchanged from dc4dde2.
- LuaLS check: 88 existing diagnostics in 13 legacy files; none in new modules.
  This is not a clean whole-project result.
- Actual in-game UI rendering, native diagnostic execution and gameplay
  persistence acceptance: NOT RUN. Mocks are not engine evidence.

## User verification / report back

Restart the game to load the new modules. Create a NEW disposable single-player
world, create a character and enter gameplay. Enable Options -> Superb Survivors
-> Debug Options -> On. Right-click -> SS Tests... . Read the warning, select
native position same-session diagnostic, acknowledge and Run. Copy outcome and
observations, or provide C:/Users/Enter/Zomboid/console.txt ([SS Tests] prefix).

For actual restart evidence, run Stage restart separately with fresh consent;
save normally, exit and completely close the game. Restart and Continue that
same world. Open SS Tests..., select Resume staged snapshot, acknowledge and
Run. Share both phases and console output. No test auto-runs after startup.
Detailed instructions, expected statuses and limits: docs/TESTS_UI.md.

REQUEST: review exact source diff and findings, then coordinate user-led native
checks before persistence correction/acceptance. No further source assignment
is inferred. SS Debug hub/inspector and AI remain unassigned.
BLOCKERS: no implementation blocker; live engine evidence remains pending.

## Changed source paths

- `42/media/lua/client/5_UI/SSRTestsWindow.lua`
- `42/media/lua/client/Testing/SSRNativePositionTest.lua`
- `42/media/lua/client/Testing/SSRTests.lua`
- `42/media/lua/shared/Translate/EN/ContextMenu.json`
- `42/media/lua/shared/Translate/EN/UI.json`
- `42/media/lua/shared/Translate/EN/UI_EN.txt`
- `docs/LOCAL_HANDOFF.md`
- `docs/NATIVE_POSITION_R1.md`
- `docs/TESTS_UI.md`
- `editor/pz-api/library.lua`
- `tests/test_persistence_engine_api.py`
- `tests/test_release_package.py`
- `tests/test_tests_ui.py`
- `tools/generate_editor_api.py`
