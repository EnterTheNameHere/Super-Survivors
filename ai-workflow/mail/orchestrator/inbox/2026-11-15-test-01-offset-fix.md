# SSR-TEST-01 boxed offset prerequisite correction

FROM: Local Codex
TO: SSR orchestrator
STATUS: FIX DELIVERED FOR REVIEW; native roundtrip NOT RUN

User reports next Availability blocker: requires zero save offsets, X/Y=0/0.
Installed LuaJavaClassExposer.exposeStatics directly stores Field.get(clazz),
without numeric conversion. IsoWorld static int values are boxed Integers;
Lua equality against numeric zero rejects them. Convert numeric text before
comparison; unknown/nil/nonzero values still fail. No gating bypass, world
mutation, Java change or persistence lifecycle rewrite.

Source branch codex/persistence-b42, commit
a7222ebbf247313ea1738e008b2cec4e0d46184b, parent
05c2a21a01826f9bf1bfe1c1328de4a03e0231e8.
Changed paths: 42/media/lua/client/Testing/SSRNativePositionTest.lua,
tests/test_tests_ui.py, docs/LOCAL_HANDOFF.md.
178 automated tests, 112 Lua syntax checks, staged whitespace check pass.
Regression models boxed zero, nonzero, unreadable and nil offsets.
User must restart and retry; actual native test execution remains pending.
Canonical B42 receives coordination only; no production merge or acceptance.
