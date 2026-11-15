# Orchestrator review — SSR-TEST-01 native position evidence

FROM: SSR Orchestrator (ChatGPT)
TO: Local Codex implementer / user
DATE: 2026-11-15
STATUS: SCOPED TEST/PROBE REVIEW COMPLETE; SSR-PERSIST-01 NOT ACCEPTED
COORDINATION REF: B42
IMPLEMENTATION REF: codex/persistence-b42
LATEST OBSERVED SOURCE HEAD: 090f424fe7fce1e2230f968eb7eeda452c51a3b6

REVIEW BASIS
Read Codex delivery and follow-ups, docs/TESTS_UI.md, docs/NATIVE_POSITION_R1.md,
and filtered actual game evidence docs/evidence/NATIVE_POSITION_2026-11-15.log.
Two in-session tests and one explicit game-restart phase are documented with
user-confirmed restart. Engine build 42.22.2. Test interface was used in game
and gates corrected after actual runtime feedback. Codex reports 178 automated
tests and 112 Lua syntax checks, not independently rerun by orchestrator.
No full SSR survivor lifecycle engine test has yet been documented.

ESTABLISHED
- Native IsoPlayer load(String) restored independently differing X and Y values
  without post-load setX/setY: 9870.5/12799.5 from a snapshot into an actor
  constructed at 9868.5/12801.5 after full restart.
- The actor remained associated with the constructor IsoGridSquare and its
  moving-object collection immediately after load. Native deserialization of
  world coordinates and world/square registration are separate processes.
- Identity marker restored; missing-file load produced no exception/change;
  human invariants and isolated-actor cleanup succeeded.
- Z was not independently differentiated; no proof from this runtime probe that
  a changed Z is restored. Installed engine source is a separate line of evidence.
- Current SSR loader constructs actors in the registry's saved tile. The probe's
  deliberate mismatched-constructor scenario does NOT alone demonstrate an SSR
  loader defect. No automatic manual coordinate/square correction authorized.
- The per-tick scan remains a scaling concern, not a measured bottleneck;
  unload/reload streaming behavior is still unvalidated in real gameplay.

DECISION / NEXT
Treat the minimal Tests UI and native position diagnostic as delivered and
successfully exercised for this bounded investigation, subject to any later
integration/packaging issues; do not extrapolate to general persistence
acceptance. Keep SSR-PERSIST-01 in review. The next useful user-led test is
genuine SSR survivor/group save, exit, restart, reload and streaming/death
roundtrip in a fresh disposable world (docs/PERSISTENCE_B42.md), not a new
speculative optimization. Investigate specific failures if the real test
identifies them. Keep canonical B42 coordination and source branch separate;
branches have diverged, so no blind fast-forward or force push.

Additional user-requested startup fixes were delivered in 29bebd0; a restart
log no longer showed previous option-description / recipe-property errors.
Actual crafting behavior remains untested and outside SSR-TEST-01.

This review message is a coordination decision, not a production-source merge.
