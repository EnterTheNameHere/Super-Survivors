# SSR-TEST-02 actual runtime result

FROM: Local Codex
TO: SSR orchestrator
STATUS: FOCUSED PROBE PASSED IN-GAME; no production adoption/merge implied
DATE: 2026-11-17

User reports Test run. Inspected console.txt (17 November, updated 07:54:05).
Runtime probe source 85be6306a77bc32af6fd6586bfdd5dc5f4a875c8 on
codex/persistence-b42; implementation head before this evidence
5afd8ce0d1d82d563244d956742084486600160e. No uncommitted probe-file changes.
Engine 42.22.2, zero offsets. No runtime code changes in this evidence delivery.

Observed at frame 1774:
- Conventional source XYZ 9884.5/12827.5/0, matching square, in cell objectList.
- Cell-only constructor XYZ 0.5/0.5/0, currentSquare nil, no object/add/remove.
- Raw load restores 9884.5/12827.5/0 and marker, but currentSquare remains nil
  with no world/square membership.
- Explicit setCurrentSquare(saved tile), setMovingSquareNow, addMovingObject
  establishes square 9884/12827/0, square contains actor=true, objectList=true,
  add/remove=false. Position unchanged by placement; NPC=true.
- Human identity/position/singleton/save filename and all four slots unchanged.
- Both actors cleaned: object/add/remove=false, currentSquare=nil, same frame.
- Final PASSED; no associated probe exception. Snapshot files retained.

Filtered evidence docs/evidence/CELL_ONLY_ISOPLAYER_2026-11-17.log (console hash
at capture included); findings added to docs/NATIVE_POSITION_R1.md,
docs/TESTS_UI.md and docs/LOCAL_HANDOFF.md on implementation branch.

Established: the one-argument Lua constructor/native load/explicit registration
route works for immediate controlled reconstruction. Sequence is tested together,
not minimized through omission experiments. Z unchanged. No normal actor update,
prolonged AI/animation, streaming/death or restart cycle exercised for Test 2.
Full SSR persistence remains under review. Do not infer saved-tile loader defect
or automatically adopt this route. IsoSurvivor migration remains rejected.

NEXT: orchestrator reviews actual results and chooses bounded follow-up.
Validation of record-only update: captured log and report cross-checked, links
and staged whitespace checked; no tests rerun or new native experiment requested.
Canonical B42 receives coordination only; no implementation merge or acceptance.
