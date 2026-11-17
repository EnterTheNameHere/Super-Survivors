# SSR-TEST-04 delivery: explicit human appearance/visibility snapshots

FROM: Local Codex
TO: SSR orchestrator
STATUS: IMPLEMENTED / DELIVERED FOR REVIEW; ACTUAL IN-GAME NOT RUN
DATE: 2026-11-17

## Refs, ownership and priority

Existing exclusive W:/Projects/Super-Survivors, codex/persistence-b42.
Source 4d998eedd5e06a553a0b0cd3e58b41b1b0a23d0c;
parent/ACK d8bb5ad48c19781f34519f245fb8cf1328edb903;
starting source 162c944a6d229e81badba0172e5559f51707be17.
Canonical B42 remains coordination only. No production merge/acceptance.
Unrelated concurrent source/settings/save edits preserved and excluded.

Read all five addressed messages. User eyewitness AI movement is direct user
evidence, reducing priority of the earlier position observer. Test-03 R1 was
NOT STARTED and is DEFERRED pending explicit further direction; its request stays
in implementer inbox as deferred, not silently executed. Preserve archived
machine INCONCLUSIVE and all scoped positive evidence/coverage gaps. No early
reconstruction instrumentation or production persistence/AI fix introduced.

The earlier human-regression triage said no fix authorized; later Test 04
assignment authorizes this bounded observation tooling. No appearance/control/
renderer fix or forced reproduction performed. Ordinary-play appearance change
and earlier invisibility-off recovery remain user observations, not proven causes.

## Three controls delivered in existing gated SS Tests UI

- Human appearance - capture baseline (only when user says intended human looks correct)
- Human appearance - compare changed
- Human appearance - diagnose invisible

All three read current local slot 0 explicitly, record timestamped fields and
supporting dynamic observations, and never reconstruct/load/save actors, modify
appearance, toggle invisibility, call resetModel or change slots/singleton.
No automatic captures/checks/polling on gameplay/startup. OnGameStart only clears
this module's memory. Existing consent and single-active-run UX retained. A vetted
readOnly flag skips the executor's gameplay-RNG persistence boot-token draw and
allows observations after prior mutation cleanup failure WITHOUT clearing that
failure/unlocking mutation tests. New UI/common-runner regressions cover that.

Baseline is session-only, world-name/cell/actor scoped. No reliable public stable
human database identity getter was verified, so no cross-restart descriptor-ID or
filename guessing. Raw actor/descriptor/visual/model refs stay in session memory,
never in ModData. AFTER never overwrites baseline; last four scalar AFTER records
retained separately, each also logged. New actor is identified and its appearance
is not compared as original human; wrong world/session is blocked. Reload/new
character requires deliberate recapture when correct again.

## Critical safe-getter/coverage findings

Installed 42.22.2 revision 3d39148846; JAR SHA256 unchanged:
3c4a7c5f149d784758c6fb5f8fa85f3a21d572e38bc081400e89035f8120d287.
Read-only actual class/member/bytecode inspection. Exact methods and limits in
docs/HUMAN_VISUAL_DIAGNOSTICS_B42.md.

HumanVisual hair/beard/skin color/style getters may initialize/randomize/clear
fields; getSkinTexture may change indices. They are NOT called. copyFrom also
calls lazy getters on source, so no copied visual workaround. getAnimationPlayer
can allocate/release/rebind animation state, also NOT called.

Safe public cached/direct getters include actor/descriptor HumanVisual, descriptor
ID/name/sex, skin texture index/body hair index/non-attached hair, invisibility/
ghost/god/no-clip/sprite/cull/draw/viewport-0 alpha flags, existing model/texture-
creator presence. Optional native-debug raw-field reflection supplies skin texture
name, hair/beard styles, skin/hair/beard/natural RGBA, visual owner, model name,
tints, texture name and creator rendered status. ImmutableColor component getters
and Texture.getName are field reads. No enabling/bypass of native debug.

Important limitation: native reflection is rejected by LuaManager when Core.debug
is false. WITHOUT -debug, the controls run with explicit UNAVAILABLE hair/style/
color fields; unsafe getters are not used to fill gaps. Full raw detail requires
native debug already on at the known-good baseline. Unavailable is not equality;
known null and absent getter are distinguished. No reliable rendered-pixel/skin
texture-cache fingerprint, even with debug. Timing is explicit user-run OnTick,
not an exact retrospective symptom frame. No automatic symptom reproduction.

Same-session actor/descriptor/visual/model reference changes, singleton and all
four local slots logged; supporting XP/levels (Axe/Strength/Fitness), HP, needs,
position, held/worn types and bounded top-level inventory are dynamic context,
not automatic failures. Inventory cap 64 items/text 2400 chars; no recursive
inventory or actor enumeration. Invisible control explicitly prints current
isInvisible true/false/UNAVAILABLE. IsoPlayer ghost aliases invisible in this
build, not independent confirmation. ZWare protection is not inferred from
native isGodMod.

Baseline PASSED means capture completed at user request, not validated appearance.
Data/reference/flag change or unchanged-with-unavailable-coverage yields diagnostic
INCONCLUSIVE, no cause/repair verdict. Ordinary XP/gear/inventory drift never
produces a FAILED assertion. Baseline/history are preserved through comparisons.

## Read-only source triage

SSR normally constructs a fresh descriptor; constructor copyFrom initializes its
source but does not show a human alias. Preset visual setters target survivor
objects; not proof human was passed. DebugCharacterSwap context path calls
SSM.switchPlayer, which really changes slots/singleton/control; no evidence user
invoked it. Native save's temporary singleton swap/finally and prior bounded
human guards do not establish visual safety during arbitrary later ordinary play.
Existing renderer opacity patch writes alpha, not isInvisible/skin/hair. No source
inventory or existing log proves root cause, and no speculative fix made.

## Validation

219 tests / 113 Lua 5.1 syntax checks PASS in isolated staged-tree export excluding
user edits. Earlier working checks pass as well. New human tests exercise lazy/
mutation traps, no-debug/raw-debug data, null/missing APIs, dynamic drift, actual
flag/data/ref changes, identity/slot/singleton/world/new-character isolation,
unchanged-visible-symptom ambiguity, history bound, no automatic capture or RNG,
retained cleanup block and per-run consent. Native-JAR checks verify direct
visual getters and ghost alias. Packaging keeps new diagnostics; prior evidence
unchanged. Editor fingerprint regenerated from intended isolated runtime source.
LuaLS: 88 legacy diagnostics/13 files, none new test/UI modules. Not globally clean.
Staged whitespace/docs links checked. No native Test 04 capture, bug repro or
rendering/visibility recovery executed. No Java/production actor/persistence edits.
Ignored logs .venv/test04-delivery-suite.txt, luals-test04-delivery-result.txt.

## User procedure / next actor

Restart game; enable Superb Survivors -> Debug Options -> On if needed. In ordinary
single-player world, while intended human looks right, SS Tests -> Human appearance
- capture baseline -> acknowledge/Run. Continue gameplay, then explicitly compare
changed or diagnose invisible when symptom occurs. No forced repro/toggle/repair.
Recapture baseline after reload/new character. Full raw hair/colors need existing
native -debug; otherwise limited fields report unavailable. Shared warning remains
because UI also contains destructive persistence tests; human controls observe only.
Send symptom/result; local Codex reads [SS Tests][human-visual-*] log entries.
Instructions/coverage: docs/HUMAN_VISUAL_DIAGNOSTICS_B42.md and docs/TESTS_UI.md.
Next: user establishes baseline, later captures symptom; orchestrator reviews.

Changed paths (source commit):

42/media/lua/client/5_UI/SSRTestsWindow.lua
42/media/lua/client/Testing/SSRHumanVisualTest.lua
42/media/lua/client/Testing/SSRTests.lua
docs/HUMAN_VISUAL_DIAGNOSTICS_B42.md
docs/LOCAL_HANDOFF.md
docs/PERSISTENCE_LIVE_TESTS.md
docs/TESTS_UI.md
editor/pz-api/library.lua
tests/test_human_visual_diagnostics.py
tests/test_persistence_engine_api.py
tests/test_release_package.py
tests/test_tests_ui.py
