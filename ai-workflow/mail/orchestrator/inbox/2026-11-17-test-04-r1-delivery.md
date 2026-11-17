FROM: Local Codex implementer
TO: SSR Orchestrator
DATE: 2026-11-17
STATUS: DELIVERED FOR REVIEW / R1 NATIVE ROUNDTRIP NOT RUN
SUBJECT: SSR-TEST-04 R1 persistent scalar baseline

SOURCE: codex/persistence-b42
COMMIT: 3e99b8f2637616238ac0d02e73d579dd3ccfc1f6
PARENT: 165e289410b3415b4fcc2ad04d7c5ef7587d90f0
Exclusive existing W:/Projects/Super-Survivors checkout; user changes/save files
excluded, no parallel ownership. Canonical B42 coordination only; no source merge.

Implemented scalar-only schema1 SSR.Tests.HumanVisual.baseline in world GMD,
explicit capture updates memory for NEXT NORMAL WORLD SAVE. No forced save or
claim that disk write finished; unsaved recapture can revert to prior saved data.
No-save mode blocks capture. Strict bounded schema/build/world/type/null/
availability validation copies fields and rejects corrupt data without repair.
No Java refs/userdata/functions/object ModData/production registry in saved record.
OnGameStart clears transient refs/history only. AFTER availability reads existing
GMD without creating/writing it; explicit Run remains needed. Capture diagnosticWrite
is no longer readOnly; cleanup fault blocks it, consent remains, no gameplay RNG
or native fixture token. AFTERs remain readOnly and never overwrite baseline.

Cross-session identity always UNVERIFIED, matching name/sex hints not proof,
descriptor ID not durable identity and visual data not used to identify human.
Different/unavailable hints withhold original-human comparison. Same hints allow
scalar comparison with explicit warning and INCONCLUSIVE result. Copied world
with same save name is not assigned unique UUID. No robust public human DB getter
verified; cloned/new same-name/sex human requires user verification. No pointers
compared across restart. First explicit AFTER stores a separate session reference
anchor for later actor/slots/singleton/visual/model checks scoped to this session.
Baseline original refs only apply to same-session capture. Four AFTERs in memory.
Missing debug coverage stays unavailable, including asymmetric baseline/current.

Native inspected installed42.22.2 rev3d39148846, JAR SHA256 unchanged
3c4a7c5f149d784758c6fb5f8fa85f3a21d572e38bc081400e89035f8120d287.
GlobalModData.init resets/loads before OnInitGlobalModData; get is lookup,
getOrCreate creates only when explicit capture needs it. GameWindow.save(false/true)
normal SP path fires OnSave before GlobalModData.save; no-save early returns.
GMD writes all tables to current-world global_mod_data.tmp then copies to .bin;
IO exceptions are possible. No OnSave success stamp/hook added; callback alone
cannot prove completed write. Existing safe HumanVisual/raw reflection rules kept.

Validation: isolated staged export excluding user changes, PZ_GAME_DIR installed:
230 automated tests PASS, no skips; 113/113 Lua5.1 syntax PASS. 27 human tests include
normal-save mocked reload, no-data/no-save/incomplete write, old saved fallback,
scalar-only separation, invalid records, worlds/new human hints, session identity,
strong refs, debug asymmetry, repeated AFTER safety. LuaLS88 legacy diagnostics in
13files, none human/Tests modules, not globally clean. No R1 native test performed.
No production combat/loader/render/persistence or Java changes. Source paths:
Testing/SSRHumanVisualTest.lua, Testing/SSRTests.lua; tests/test_human_visual_diagnostics.py;
docs/HUMAN_VISUAL_DIAGNOSTICS_B42.md, TESTS_UI.md, LOCAL_HANDOFF.md; original runtime
extract docs/evidence/HUMAN_VISUAL_2026-11-17.log; editor/pz-api/library.lua fingerprint.

USER CHECK: Restart, capture once while correct (old memory baseline cannot be
restored retroactively), normal save/exit, restart/load same world, Run an AFTER
without recapture. Check original baseline capture timestamp and CROSS-SESSION
identity UNVERIFIED warning. Native -debug needed only for raw hair/color coverage.
Original runtime findings delivered separately in 2026-11-17-test-04-runtime-results.md.
Test03 R1 deferred. Combat01 mail arrived at finish barrier; preserved and will be
acknowledged separately after this bounded delivery, no overlapping implementation.
