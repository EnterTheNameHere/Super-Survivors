# Runtime correction: unavailable Lua next global

FROM: Local Codex
TO: SSR orchestrator
STATUS: MINIMAL COMPATIBILITY FIX DELIVERED; native retry pending
DATE: 2026-11-17

User reported Error after Test 03 delivery. Actual console repeats failure from
frame 1 at SuperSurvivorPersistence.tick line 256: next(entries) calls nil.
Engine/JAR unchanged (42.22.2, SHA256 3c4a7c5f149d784758c6fb5f8fa85f3a21d572e38bc081400e89035f8120d287).
Installed se.krka.kahlua.stdlib.BaseLib does not register global next. Lua 5.1
mock tests supplied it, masking a concrete runtime incompatibility.
Captured first error: docs/evidence/PERSISTENCE_NEXT_ERROR_2026-11-17.log.

Separate focused follow-up to user's runtime-error request, announced before
editing: replace only two global next uses in persistence (first saved-index
entry, empty-bucket detection) with local pairs-based firstKey. No scan algorithm,
loader, unload, group policy or constructor change; no Java modification.
Iterator/SpiralSearch :next methods are valid and left alone. This production
compatibility correction is explicit, not a silent persistence redesign under
the test assignment. No broader fixes/acceptance/merge implied.

Source codex/persistence-b42:
786c8ea0c0d8aeb4c2dbf35b99bcb4f91839c415, parent
dd42788ebbc494bac6db578580f2da87b85a744c.
Changed paths: SuperSurvivorPersistence.lua; test_persistence.py;
test_persistence_lifecycle.py; docs/LOCAL_HANDOFF.md; docs/PERSISTENCE_LIVE_TESTS.md;
captured error log; editor/pz-api/library.lua source fingerprint only.
Unrelated user edits preserved/excluded.

201 tests pass (including isolated staged-tree export excluding user edits),
112 Lua syntax checks pass, staged whitespace checked. New regressions disable
next globally through indexed load/unload/dead unindex and complete lifecycle
mock roundtrip. No new LuaLS run claimed; previous delivery result was 88 legacy
diagnostics, none in the new module. Editor fingerprint regenerated from isolated
intended source. No actual engine retry or end-to-end Test 03 success yet.

Restart game to load fix/rebuild index, retry Test 03. Existing disposable world
can be used; if already staged, continue its normal save/restart/resume sequence.
Await user runtime evidence. Canonical B42 receives coordination only; no source
merge/acceptance or speculative optimization.
