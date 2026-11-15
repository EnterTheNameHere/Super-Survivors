# SSR-TEST-01 actual native position results

FROM: Local Codex
TO: SSR orchestrator
STATUS: ENGINE PROBE EXECUTED; persistence acceptance still pending review

User reports all phases successful, with actual game restart/world reload.
Runtime code includes a7222ebbf247313ea1738e008b2cec4e0d46184b on
codex/persistence-b42, current source head before evidence abcb15860c5dee6e98af6204acd700a804fec29d.
Engine 42.22.2, zero save offsets. No gameplay changes in this report.

Read docs/NATIVE_POSITION_R1.md and filtered
 docs/evidence/NATIVE_POSITION_2026-11-15.log on implementation branch.
Two same-session passes, stage and next-session resumed pass are captured.
Resume source XYZ 9870.5/12799.5/0, destination constructor 9868.5/12801.5/0,
raw load 9870.5/12799.5/0; currentSquare remains 9868/12801/0. Same split in
both same-session loads. Position/marker restoration, missing-file behavior,
human guards and actor cleanup pass. Staged manifest survived restart.

Observed: native coordinate deserialization does NOT reconcile current square
or moving-square collection. No manual coordinate correction occurred in probe.
Z unchanged, so independently differentiated only X/Y. User confirms full
restart; session tokens alone would not prove process restart.

Focused probe passes, NOT full SSR save/unload/death/streaming acceptance.
REQUEST: review results and loader registration implications before assigning
correction; no speculative tick-scan optimization, automatic merge or Java change.
This evidence completes the requested first runtime experiment; broader lifecycle
verification and source review remain. No new automated checks needed for
record-only update; preceding code validation remains 178 tests/112 syntax.
