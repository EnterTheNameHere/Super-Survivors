# SSR-TEST-03 — Replace native diagnostics with real SSR persistence lifecycle tests

Date: 2026-11-17
Status: REQUESTED; requires local Codex acknowledgement
Coordinator: ChatGPT SSR orchestrator
Implementer: existing exclusive local Codex worktree, verify ownership/actual branch before starting
Canonical coordination: B42
Source branch: codex/persistence-b42 (latest observed 773f482537750fbc3b36d263563443044f0fba1c)
Related: SSR-PERSIST-01; SSR-TEST-01/02 completed and engine findings recorded.

## User authorization and intent
The user agrees the next gate should be actual SSR-PERSIST-01 end-to-end testing and explicitly says **existing tests can be rewritten**. The existing minimal SS Tests UI/registry is reusable, but its native constructor diagnostic definitions are not a permanent compatibility burden. Keep historic documentation and captured logs for Tests 1 and 2; do not delete prior evidence. The purpose now is to inspect the complete real SSR lifecycle, not prove IsoPlayer.save/load in isolation yet again.

## Required implementation — reusable in-game lifecycle tests
1. Review existing production SSR persistence implementation and test registry/UI to determine safe, deterministic coverage. Implement a deliberately SMALL focused set of development-gated in-game tests; replace/rework existing native test definitions rather than accumulating obsolete choices. Keep SS Tests menu, prominent irreversible-world warning, fresh affirmative consent for each destructive run, explicit statuses and log evidence, and one active mutation test at a time. Avoid generic DSL/runner/large debug hub.
2. **First priority**: one real SSR survivor created via ordinary SSR manager/wrapper and group API, distinct identity and controlled character state; record BEFORE actual OnSave event the native character details, inventory/equipment, skills/health as practical, group/role/identity, recorded position and snapshot/registry state. Trigger nothing automatically on launch. Allow explicit stage, normal game save/exit, full user-confirmed restart/reload, then explicit resume with new consent and comparison. Protect native human player and real survivors: use disposable-world owned test actor/group with unique markers; never enumerate/delete other characters as cleanup. Across restart, use persistent serializable test manifest, but not one that substitutes for the actual SSR registry or fakes the production save/load result.
3. **Observe independently** the recorded native snapshot/identity and SSR registry/manifest, plus reconstructed loaded actor, square/world membership and count per ID. The save boundary is the game's actual OnSave; do not stage baseline earlier if autonomous AI could alter it before save. Log what was measured versus what was inferred. If save and staging cannot be coordinated safely, show INCONCLUSIVE and propose a manual step instead of fabricating an automatic pass.
4. Expand in bounded independent phases only after step 2: multiple survivors/groups including empty group and stable IDs/roster, unload/return with no duplicate actor, death tombstone and no respawn, repeated save generations. It is acceptable to first deliver ONE robust restart roundtrip and provide manual acceptance checks for the remaining phases instead of building a fragile end-to-end autonomous game driver.
5. Preserve existing SSR production code for first investigation. If testing finds lifecycle bugs, capture exact evidence and report a separately scoped correction proposal; do not silently rewrite persistence loader/unload/index or onTick algorithm under a test assignment.
6. Use the installed B42.22.2 Java/Lua to validate API assumptions and existing constructor/snapshot findings. No reliance on old B40/B41 as engine specification. Any test which must manipulate the world must check actor/group ownership and lifecycle, and make cleanup intentionally best-effort. Real survivor save data, groups and snapshots may persist after tests; DO NOT promise reversible cleanup or delete another test's surviving record.
7. Preserve or simplify test registry and UI only as needed for user-friendly stage/resume instructions, evidence/status and crash/restart semantics. No need to keep all 4 former native probe entries visible; historical tests are archived in docs/logs. Never execute or resume a world-mutating test automatically on restart.
8. For B42 large Z range: log actual survivor Z and identify whether test differentiates Z; do not claim vertical restoration if all actors stay on Z=0. Do not expand current assignment into general spatial/Z search overhaul, which is documented separately.
9. Do not add multiplayer support; keep single-player one-human guard and avoid modifying user's human player state.

## Verification and delivery
- Real source commit(s), changed paths, parent, branch and ownership, doc steps: which SS Tests entry to select, exact run/stage/save/exit/restart/resume sequence, and what output to share. Tests should be possible in a disposable world without -debug.
- Automated tests and Lua syntax checks; detailed list of unverified in-game steps until user runs them.
- Captured comparison per property with supported PASS/FAIL/INCONCLUSIVE behavior, including mismatches attributable to native snapshot, SSR metadata, or reconstruction where evidence permits.
- Add test documentation to docs/TESTS_UI.md and relevant evidence or new lifecycle test doc; keep prior logs.
- Addressed delivery in ai-workflow/mail/orchestrator/inbox on B42; track state and handoff. Do not merge implementation branch into B42 automatically.
- If current checkout has uncommitted user code, preserve it; do not overwrite or commit unrelated changes. One implementer per branch.
