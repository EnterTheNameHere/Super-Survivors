# Super Survivors Reloaded — coordination index

Repository: `EnterTheNameHere/Super-Survivors`  
Canonical coordination branch: `B42`  
Source tree inspected at setup: `857543978dbc2571a164666f1f6c864acb88b4da`  
Date: 2026-11-15

**Read in order:** `README.md`, `coordination-protocol.md`, `state.md`, `handoff/orchestrator-thread.md`, your role's inbox, and any referenced assignment. Then verify actual Git head/ownership.

**Roles:** orchestrator = ChatGPT design thread; implementer = local Codex after explicit startup; user = design authority and in-game tester.

**Active request:** SSR-PERSIST-01 — B42 native world-save persistence and stable survivor/group registry.
- Task: `assignments/persistence-b42.md`
- Processed mail: `mail/implementer/archive/2026-11-15-persist-01.md`
- Current status: REVIEW IN PROGRESS / R1 PROBE PASSED IN-GAME; full SSR lifecycle review/validation pending.
- Implementation ref: `codex/persistence-b42`, base `3a087ee8c4aceb151443848e19bbc3a999a129f5`.
- Acknowledgment: `mail/orchestrator/inbox/2026-11-15-persist-01-ack.md`.
- Delivery: `mail/orchestrator/inbox/2026-11-15-persist-01-delivery.md`.
- Source commit: `dc4dde25d612d33650c1ed5ef4ad0401c02394b5`; parent `792a129d6561d5e35fb8ace4c03eb4fd2558f8cd`.
- Canonical B42 carries coordination only; production implementation remains on its review branch. No acceptance or implementation merge is implied.
- Authoritative R1 clarification: `mail/implementer/archive/2026-11-15-persist-01-r1-clarification.md` on B42. It supersedes the earlier mandatory-optimization request.
- Next actor: orchestrator reviews the delivery; user executes the opt-in probe in a fresh disposable world. No speculative persistence rewrite.

**Next (not yet assigned):** SS Debug hub and inspector, then new survivor AI Manager and scenarios.

Do not work on `master` or merge/publish without review and authorization.


## Delivered for review: SSR-TEST-01 (2026-11-15)
- User approved a reusable minimal in-game Tests UI via context menu, destructive-world warning with affirmative acknowledgment, independent Lua registry, and IsoPlayer native save/load position probe as first test.
- Task: `assignments/tests-ui-01.md`
- Processed request: `mail/implementer/archive/2026-11-15-test-01.md`
- Status: DELIVERED FOR REVIEW; native roundtrip passed in-game, full SSR lifecycle unvalidated.
- Acknowledgment: `mail/orchestrator/inbox/2026-11-15-test-01-r1-ack.md`.
- Related: SSR-PERSIST-01 R1 engine investigation; no mandatory OnTick rewrite.
- Delivery: `mail/orchestrator/inbox/2026-11-15-test-01-r1-delivery.md`.
- Source: `594e65bc6af92927d8ec2c4b20c5c36806bf31a3`, parent `c1dea17a8f052a8e861635a86eec1619e791035e` on `codex/persistence-b42`.
- Next: orchestrator review and user-led in-game checks; no automatic merge.


Runtime follow-up: user opened Tests UI; version gate prevented running.
Fix delivered at 4164ad7bead8d6dd2d7db3c6e514e7c9acb52a42 (parent
5f215b056cf00908a6c84a95dfa4dde89348fef2): compare full build API; preserve
checkbox on selection at user request; show disabled-run reason. 177 tests and
112 syntax checks pass. Actual native roundtrip still NOT RUN. Report: mail/orchestrator/inbox/2026-11-15-test-01-runtime-fix.md.


Offset gate follow-up: a7222ebbf247313ea1738e008b2cec4e0d46184b normalizes
boxed Java static save offsets (user reported rejection of 0/0). 178 tests and
112 syntax checks pass; native roundtrip still pending. Report:
mail/orchestrator/inbox/2026-11-15-test-01-offset-fix.md.


Latest runtime evidence (15 November 2026): user completed all three probe
phases with game restart; logs confirm two same-session passes and resumed
pass. Native X/Y/marker restored; currentSquare remains constructor square.
Human guards and isolated cleanup passed. Z not independently differentiated.
Full SSR persistence lifecycle/acceptance still pending orchestrator review.
Report: mail/orchestrator/inbox/2026-11-15-test-01-runtime-results.md.
Next actor: orchestrator reviews concrete engine results and loader placement
implications; no automatic source merge or speculative rewrite.


User returned control to orchestration after runtime checks. Latest restart log
(15 November 14:31:11) contains no prior mod recipe-property or option-format
errors; crafting itself untested. Native probe passed, full SSR persistence
review/lifecycle acceptance pending. Next actor: orchestrator; implementer awaits
next bounded assignment. See mail/orchestrator/inbox/2026-11-15-return-to-orchestration.md.


## SSR-TEST-01 in-game outcome (2026-11-15)
- Tests UI usable; native position probe exercised twice in-session and once
  after actual restart, with captured logs.
- Native load restores X/Y and identity, not square registration after a
  deliberately different constructor position. Z not independently varied.
- Review: `mail/implementer/archive/2026-11-15-test-01-orchestrator-review.md`.
- Status: scoped diagnostic delivered and validated in-game; full SSR-PERSIST-01
  remains under review, next gate real SSR survivor/group lifecycle.
- Source: `codex/persistence-b42`, observed head `090f424`. No production merge.

## Delivered for review: SSR-TEST-02 — cell-only IsoPlayer construction (2026-11-15)
User requested experiment before more persistence work. Verify installed B42.22.2 IsoPlayer.new(cell) availability/side effects and, only if safe, add opt-in Tests UI experiment for raw :load() and explicit world registration. Assignment: `assignments/test-cell-only-isoplayer-02.md`; inbox: `mail/implementer/archive/2026-11-15-test-02-cell-only.md`. DELIVERED FOR REVIEW; focused probe implemented, user live test pending. SSR-PERSIST-01 code preserved; no automatic merge.


## Completed source analysis: SSR-ANALYSIS-01
- Compare IsoSurvivor and IsoPlayer in installed B42 Java/Lua, source-only, before any in-game experiment. Assignment: `assignments/isosurvivor-vs-isoplayer-analysis.md`; inbox: `mail/implementer/archive/2026-11-15-isosurvivor-analysis.md`.
- Status: ANALYSIS COMPLETE; proposed IsoSurvivor migration REJECTED by user. No change to SSR actor implementation. SSR-TEST-02 remains pending separately.


SSR-ANALYSIS-01 acknowledged by existing exclusive local Codex, source-only
research. Latest user instruction restricts this turn to analysis; SSR-TEST-02
and supplement remain pending. Ack: mail/orchestrator/inbox/2026-11-15-analysis-01-ack.md.


## SSR-ANALYSIS-01 final disposition (15 November 2026)
Analysis complete; user requested the proposed IsoSurvivor migration be REJECTED.
Keep IsoPlayer. Installed-source blockers: inherited getVisual throws, primary
BodyDamage/Moodles/XP absent, shared attack state requires IsoPlayer, filename
save/control/update contracts differ. Documentation a4c523b35cc5e1cfac5958a75d41bd0548c3802a
(parent 6234ff63df16dcd67dbed56f7836aad4ab254420) on codex/persistence-b42;
report docs/ISOSURVIVOR_VS_ISOPLAYER_B42.md. No runtime code/test/experiment or
Java changes. SSR-TEST-02 and factory supplement remain pending, explicitly not
executed under user's analysis-only instruction. Next actor: orchestrator.
Delivery: mail/orchestrator/inbox/2026-11-15-analysis-01-delivery.md.


SSR-TEST-02 now ACKNOWLEDGED: user explicitly resumed Test 2 after analysis.
Existing exclusive local Codex checkout, constructor/factory research and focused
probe only. Prior analysis-only restriction no longer applies. Ack:
mail/orchestrator/inbox/2026-11-15-test-02-ack.md. Native test NOT RUN yet.


## SSR-TEST-02 delivered (15 November 2026)
Focused cell-only/native-load/explicit-registration probe at source
85be6306a77bc32af6fd6586bfdd5dc5f4a875c8 (parent ACK
8e50dbf95a59d64864353d8795c89d87e937fa6d), codex/persistence-b42.
Factory supplement answered; no arbitrary-NPC-returning managed factory found
in inspected scope. No human loading/control helper used. New fourth selector:
Native IsoPlayer - cell-only construction and placement. 185 tests, 112 syntax;
LuaLS 88 legacy diagnostics, none test modules. USER IN-GAME NOT RUN.
No production loader/scan/unload/group rewrite, Java change or automatic merge.
Next actor: user runs the new entry after restart; orchestrator reviews observations.
Delivery: mail/orchestrator/inbox/2026-11-15-test-02-delivery.md.

## Saved future design direction (2026-11-16)
- `docs/SURVIVOR_WORLD_KNOWLEDGE_DIRECTION.md` — B42 building/floor/Z correctness, unified observation, individually acquired survivor knowledge, stale resource memory, communication, possible offscreen simulation and multiplayer considerations. Direction only; no implementation assignment. Independent SSR document.


## SSR-TEST-02 actual result (17 November 2026)
Cell-only/native-load/explicit-registration probe PASSED in actual B42.22.2.
Constructor unplaced at 0.5/0.5/0; raw load restores saved X/Y/marker but remains
unregistered; explicit current/moving-square/cell sequence establishes membership.
Human and all four local slots unchanged; both actors cleaned up in same frame.
No normal AI/update or full lifecycle validation. No production adoption/merge.
Next actor: orchestrator reviews results; no implementation continues automatically.
Report: mail/orchestrator/inbox/2026-11-17-test-02-runtime-results.md.

## SSR-TEST-02 in-game review (2026-11-17)
User completed the focused B42.22.2 cell-only IsoPlayer probe. Runtime log on codex/persistence-b42: `docs/evidence/CELL_ONLY_ISOPLAYER_2026-11-17.log`; implementer report: `ai-workflow/mail/orchestrator/inbox/2026-11-17-test-02-runtime-results.md`. Cell-only constructor yielded (0.5,0.5,0), no square/cell membership; native load restored saved XYZ (9884.5,12827.5,0) and marker, still unregistered; explicit setCurrentSquare(saved tile), setMovingSquareNow(), addMovingObject() established correct square and objectList. Human slots/singleton/position and cleanup checks passed. **Scoped diagnostic accepted** by orchestrator; review mail: `ai-workflow/mail/implementer/archive/2026-11-17-test-02-orchestrator-review.md`. No differential Z, restart or prolonged active NPC test for Test 2. No evidence that existing saved-position constructor SSR loader is faulty or that cell-only route is superior. Production SSR-PERSIST-01 remains under review, awaiting live end-to-end SSR survivor/group persistence/streaming/death checks. No code merge/adoption authorized.

## SSR-TEST-03 — real SSR persistence lifecycle tests (2026-11-17)
User authorized repurposing/rewriting existing native diagnostic tests in the development-gated SS Tests UI; their historical findings/logs remain retained. New Codex assignment: `ai-workflow/assignments/persistence-live-tests-03.md`, request `ai-workflow/mail/implementer/archive/2026-11-17-persistence-live-tests-03.md`. First goal: one real SSR-managed survivor/group, baseline captured at actual game OnSave, normal save/exit and user-confirmed restart, explicit consent to resume, compare saved native state, SSR registry and reconstructed actor, including square/list membership. Gradually extend/manual-check multiple survivors/groups, unload/return, death, repeated snapshots; do not overbuild framework. No auto execution, no production persistence rewrite, no source merge. Status IMPLEMENTED/DELIVERED FOR REVIEW; user in-game run pending.


SSR-TEST-03 ACKNOWLEDGED by existing exclusive local Codex; implementing minimal
real SSR restart test, preserving production persistence and historical probes.
Ack: mail/orchestrator/inbox/2026-11-17-test-03-ack.md. No engine result yet.


## SSR-TEST-03 implementation delivered (17 November 2026)
Source e6f08e05b3ec3805a1c8394d8de2f7dab8e261d9 (parent ACK
4d5002e816e7a5cc3aca9a5d1a708913299153ec), codex/persistence-b42.
Two visible choices: real survivor/group stage and explicit full-restart resume.
OnSave observer samples after production snapshot publication, not stage click;
no production save/load call or callback reordering. Independent native reader,
registry/group/live actor/property/count comparisons. Old diagnostics archived,
evidence unchanged. Persistent fixtures remain; no deletion of other actors.
199 tests/112 syntax pass in isolated intended tree; LuaLS 88 legacy diagnostics,
none new modules. USER IN-GAME NOT RUN. No production persistence rewrite/merge.
Instructions: docs/TESTS_UI.md; manual broader checks: docs/PERSISTENCE_LIVE_TESTS.md.
Next actor: user stage/save/exit/full restart/resume, orchestrator reviews evidence.
Delivery: mail/orchestrator/inbox/2026-11-17-test-03-delivery.md.


Test 03 runtime prerequisite fix (17 November 2026): user error exposed missing
Kahlua global next in persistence index at pre-fix line 256. Minimal pairs-based
firstKey substitution at 786c8ea0c0d8aeb4c2dbf35b99bcb4f91839c415; parent
 dd42788ebbc494bac6db578580f2da87b85a744c. No algorithm/loader/unload redesign.
201 tests/112 syntax pass, including next=nil regressions and isolated export.
Restart/native Test 03 retry pending. Report:
mail/orchestrator/inbox/2026-11-17-test-03-next-compatibility-fix.md.


## Test 03 actual restart outcome (17 November 2026)
INCONCLUSIVE overall: native snapshot/registry/group and loaded actor properties
match except live X/Y differs at explicit comparison. ID 2/group 3/generation 4;
counts 1/1/1, membership/human guards/reader cleanup passed. Consistent with AI
movement, not proven without first-reconstruction observation. Axe XP baseline
was 0 despite setup grant: nonzero skill retention untested. No new code change,
no full persistence acceptance or automatic next test. Next actor: orchestrator.
Report: mail/orchestrator/inbox/2026-11-17-test-03-runtime-results.md.


Test 03 pause feedback: user cannot open world context menu while paused, and
Run itself needs simulation ticks. Source confirms setup then measurement on
successive OnTick callbacks, after native world update. Manual pause is not a
reliable control. Proposed audited, owned read-only earliest-reconstruction
observation (not implemented) before explicit comparison; no automatic mutation
or blanket paused-callback execution. Next actor orchestrator. Report:
mail/orchestrator/inbox/2026-11-17-test-03-pause-feedback.md.

## SSR-TEST-03 actual runtime review and R1 request (2026-11-17)
Reviewed implementer inbox delivery, missing Kahlua global-next correction, actual save/restart console result and user pause/tick feedback. Actual OnSave for survivor ID2/group3 generation4; native file checkpoint, SSR group/registry and live non-position actor data matched, actor/wrapper/record 1/1/1, square/world membership valid, human guards and temporary reader cleanup good. **Overall INCONCLUSIVE**: live X/Y at delayed UI test 9888.5/12828.3349609375 versus saved 9885.5/12824.5; no earliest reconstruct observation proves whether AI moved. XP=0 baseline and health/Z defaults do not validate nondefault values. User confirms pause blocks world context menu; OnTick runner and world-update ordering make click-speed workaround invalid. Original Kahlua global `next` error fixed narrowly by Codex at 786c8ea; did not recur in successful native comparison. No full SSR-PERSIST-01 acceptance or merge.
Next bounded assignment SSR-TEST-03 R1: `ai-workflow/assignments/test-03-early-reconstruction-observer.md`, inbox `ai-workflow/mail/implementer/inbox/2026-11-17-test-03-r1-early-observer.md`, paired review `ai-workflow/mail/implementer/archive/2026-11-17-test-03-orchestrator-review.md`. Inspect exact engine/SSR callback ordering; add *read-only*, ownership-scoped earliest actor reconstruction capture only if nonintrusive; compare with OnSave and later UI resume. No automatic test actions on reload, no loader behavior change, no broad fixes. STATUS REQUESTED / NOT ACKNOWLEDGED.

## SSR-TEST-04 — Human appearance/invisibility baseline (2026-11-17)
User observed human skin/hair/probable facial hair change during ordinary play (not active test), other character state apparently remained theirs. Separately had human invisibility; previous disabling of invisibility setting made avatar visible again without proving cause. User proposed explicit good baseline and later symptom-triggered comparisons for changed appearance or invisibility. Skills/XP, equipment and inventory are dynamic diagnostic context, not invariants. Codex assignment: `ai-workflow/assignments/human-visual-baseline-diagnostics.md`, request `ai-workflow/mail/implementer/archive/2026-11-17-test-04-human-visual-diagnostics.md`. Read-only B42 API-backed HumanVisual/descriptor/appearance, actor/slot/singleton and visibility flags; bounded baseline/symptom snapshots; no auto checks or repairs, no runtime fix or merge. STATUS REQUESTED/NOT ACKNOWLEDGED. Test-03 R1 earliest observer remains lower priority following user's direct observation of AI movement.


SSR-TEST-04 ACKNOWLEDGED by existing exclusive local Codex; implementing explicit
read-only human diagnostics after getter safety inspection. Test-03 R1 not
started and DEFERRED per user-observed AI movement priority. Ack:
mail/orchestrator/inbox/2026-11-17-test-04-ack.md. No native Test 04 run.


## SSR-TEST-04 delivered (17 November 2026)
Source 4d998eedd5e06a553a0b0cd3e58b41b1b0a23d0c, parent ACK
d8bb5ad48c19781f34519f245fb8cf1328edb903, codex/persistence-b42.
Three explicit observation-only Human appearance controls in SS Tests: baseline,
compare changed, diagnose invisible. Session-only baseline/world+actor scoping,
bounded four AFTER records; no ModData/raw reference persistence or automatic
capture/repair. No unsafe lazy getters/animation allocation. Without -debug,
full hair/color data explicitly unavailable; optional debug raw reads only.
Dynamic XP/gear/inventory are context. Native Test 04 NOT RUN. 219 tests/113 syntax
pass isolated; LuaLS 88 legacy diagnostics, none new modules. No production fix.
Test-03 R1 NOT STARTED / DEFERRED; inbox request retained pending new direction.
Direct user AI movement observation recorded; archived Test-03 result unchanged.
Next actor user known-good baseline/later symptom capture, orchestrator review.
Delivery: mail/orchestrator/inbox/2026-11-17-test-04-delivery.md.


SSR-TEST-04 R1 ACKNOWLEDGED / IMPLEMENTING by exclusive existing local Codex
checkout codex/persistence-b42. Separate scalar diagnostic GlobalModData baseline
with normal-save durability and cautious cross-session identity; AFTER stays
read-only. Prior Test04 logs verified, no symptom reproduction claimed.
Ack: mail/orchestrator/inbox/2026-11-17-test-04-r1-ack.md. Test-03 R1 deferred.

## SSR-COMBAT-01 — survivors not attempting to fight (2026-11-17)
User reports in ordinary B42 gameplay that survivors **do not try to fight**. Requested a focused source/native audit distinguishing lack of perception, blocked decisions/AttackTask, missing weapon/range/readiness, native request rejected, or no combat engine outcome. Initial code areas: `SuperSurvivor.lua` DoVision (getLuaObjectList), priority/task selection and `requestCombatAttack` (pressedAttack), `7_Tasks/AttackTask.lua`; no proven root cause yet. Assignment: `ai-workflow/assignments/combat-b42-investigation-01.md`, implementer inbox: `ai-workflow/mail/implementer/archive/2026-11-17-combat-01-diagnose-no-fighting.md`. First read-only evidence and a bounded diagnostic proposal; no speculative production combat rewrite. Do not overlap same source branch with pending Test-04 R1 baseline persistence; ack ordering/ownership. STATUS REQUESTED/NOT ACKNOWLEDGED.


SSR-TEST-04 R1 DELIVERED for review at 3e99b8f2637616238ac0d02e73d579dd3ccfc1f6,
parent165e289410b3415b4fcc2ad04d7c5ef7587d90f0 on exclusive codex/persistence-b42.
Explicit scalar diagnostic GMD baseline for next normal save, no forced save,
AFTER readOnly; cross-session identity UNVERIFIED (hints only), no persisted refs.
230 tests/113syntax pass isolated, LuaLS88 legacy/no new module issues. R1 native
save/restart NOT RUN. Original three Test04 log runs verified 83fields/25expected
unavailable, baseline capture and AFTER inconclusive, no errors/no symptom repro.
Reports: mail/orchestrator/inbox/2026-11-17-test-04-r1-delivery.md and
mail/orchestrator/inbox/2026-11-17-test-04-runtime-results.md. Test03 R1 deferred.
Combat01 new mail preserved at finish barrier; source diagnosis next separately.


SSR-COMBAT-01 ACKNOWLEDGED after Test04 R1 delivery; exclusive existing local
Codex codex/persistence-b42, read-only source/native diagnosis and diagnostic
proposal, no gameplay fix. Ack: mail/orchestrator/inbox/2026-11-17-combat-01-ack.md.


SSR-COMBAT-01 SOURCE DIAGNOSIS DELIVERED at79c6d10519542b174c5e3c88954615e1de19820a,
parent913d2cef97d954e24ed345fa5d86eec57db72ea4, codex/persistence-b42. Runtime
unchanged since Test04 R1 3e99b8f. Complete active chain/native review: correct
one-based perception table; impossible equip predicates, zombie Pursue wrapper
requirement, NPC control-var initiation/aiming mismatch and local-player-only
normal attack collision gate. No observed incident stage/root cause claimed.
Read-only existing-NPC snapshot proposed; no diagnostic/gameplay fix/Java change.
Report docs/COMBAT_B42_INVESTIGATION_01.md on implementation ref; delivery
mail/orchestrator/inbox/2026-11-17-combat-01-delivery.md. Next actor orchestrator
review/new bounded authorization. Test04 R1 native save/restart pending separately.
Test03 early observer remains deferred. No production source merge/acceptance.

## SSR-COMBAT-01 reviewed, SSR-COMBAT-02 requested (2026-11-17)
Source-only investigation report `docs/COMBAT_B42_INVESTIGATION_01.md` on codex/persistence-b42, delivery `ai-workflow/mail/orchestrator/inbox/2026-11-17-combat-01-delivery.md`. Native/B42 evidence: AI-manager equip branches contradict held weapon vs empty hand; PursueTask requires SSR wrapper and ordinary zombies have none. NPC AIComponent aiming/control differs from normal IsoPlayer setters; normal SwipeStatePlayer collision callback requires actual local-player membership and excludes SSR standalone NPCs on that specific route. Perception Lua table indexing is valid, outside/outside nil-room equality passes, active AttackTask scheduling exists. No live NPC combat diagnostic or root-cause attribution yet; no combat code changes. New bounded read-only in-game diagnostic task `ai-workflow/assignments/combat-b42-observation-02.md`, inbox `ai-workflow/mail/implementer/archive/2026-11-17-combat-02-live-snapshot.md`, STATUS REQUESTED/NOT ACKNOWLEDGED. Use only existing owned loaded SSR NPC, observe cached target/task/weapon/native flags without forcing attacks or mutating world; temporal tracing or actual fixes await separate review. Test04 R1 delivered but save/restart proof pending; Test03 early observer deferred.


SSR-COMBAT-02 ACKNOWLEDGED / IMPLEMENTING by exclusive existing local Codex
codex/persistence-b42: explicit existing-NPC read-only one-shot snapshot, no
combat fix or temporal tracing. Ack: mail/orchestrator/inbox/2026-11-17-combat-02-ack.md.


SSR-COMBAT-02 DELIVERED for review at135f7993a93d009f086334f21bd914f8d258aec8,
parentda2c6f966a77b75a382bdb1a9e4fe0f41ee3d22e, exclusive codex/persistence-b42.
Explicit existing loaded NPC selector/manual refresh + one readOnly snapshot in
SS Tests; cached AI/task/perception/weapon/native flags/world frame, bounded output,
identity/local/world guards, no predicates/updates/attacks/spawn/temporal tracing.
Native AI control Class token unverified -> unavailable; no root cause/hit claim.
245 tests/114 syntax pass isolated; LuaLS88 legacy, none new modules/UI. Native
UI/snapshot NOT RUN. User restart/select/acknowledge/Run near zombie and report
observed NPC behavior. Docs/COMBAT_LIVE_SNAPSHOT_B42.md on implementation ref;
delivery mail/orchestrator/inbox/2026-11-17-combat-02-delivery.md. Next orchestrator
review/user native check. Test04 R1 unchanged/restart proof pending; Test03 R1
deferred. No production combat fixes, Java changes or source merge/acceptance.


Combat02 ACTUAL USER RUNS verified17November: Roderick(user identifies ID9),33
snapshots277.817s, attackStarted true/initiate false/no animation/Swipe throughout
samples;11 native in-range (7 wait0), healthy/armed/native readiness true. Attack
front31, Flee1/building1, updates progress. No errors after first snapshot. Native
snapshot functionality verified; not combat success/full root cause. Conditional
request guard would reject busy; no request trace/continuous flag ordering recorded.
Source mechanism candidate NPC control handoff; no fixes/flag resets/observer added.
Evidence/docs commit e498ae7b248b8a49c6765332e758085e69850be8 on codex/persistence-b42;
report mail/orchestrator/inbox/2026-11-17-combat-02-roderick-runtime-results.md.
Next orchestrator review/bounded handoff investigation; more identical snapshots
not needed. Original delivery NOT RUN history superseded by native user evidence.
Test04 R1 restart proof pending separately; Test03 R1 deferred. No source merge.

## SSR-COMBAT-02 actual run and SSR-COMBAT-03 request (2026-11-17)
User ran Combat02; local Codex inspected 34 real-game snapshots (33 Roderick SSR ID9). Evidence docs/evidence/COMBAT_SNAPSHOT_RODERICK_ID9_2026-11-17.log on source branch, inbox ai-workflow/mail/orchestrator/inbox/2026-11-17-combat-02-roderick-runtime-results.md. Of ID9 33 samples, 31 Attack-front, 11 native in-range, 7 in-range+WaitTicks0. ALL33 isAttackStarted=true, isInitiateAttack=false, swing/animation false, native weapon-ready=true, AtkTicks0; healthy, equipped mallet, living zombie target, AI updates advance. Source requestCombatAttack would return busy if called with these flags, but request-return/first flag setter not observed. Evidence supports recurrent native attack-state stall, not proven root cause or collision stage. No more repeated still-frame sampling recommended. New bounded user-invoked existing-owned-NPC temporal trace assignment ai-workflow/assignments/combat-b42-handoff-trace-03.md and mail ai-workflow/mail/implementer/archive/2026-11-17-combat-03-attack-handoff-trace.md; verify native order, strict scope/log/time/cancellation, no forced attacks/flag changes/hits/slot edits, no production fix/merge. Status REQUESTED / NOT ACKNOWLEDGED.


Combat03 ACKNOWLEDGED / IMPLEMENTING by exclusive existing local Codex on
codex/persistence-b42. Includes source/API research and contextual read-only
Diagnostics on both reachable info paths; bounded natural-call trace, no combat
fix. Ack: mail/orchestrator/inbox/2026-11-17-combat-03-ack.md.


Combat03 DELIVERED for review ata5b166d45e83a7450acc31b135f31cba937332a2,
parenta65e33a4606f436623d7023a27b6ae774f9d1e34, exclusive codex/persistence-b42.
Shared Diagnostics on both reachable information paths: immediate reused snapshot,
explicit bounded passive trace, no destructive consent or global test bypass.
10s/600ticks/80lines/30natural calls, instance-only exact-once request observer,
returns/errors unchanged (no protected call around original; deferred aborted-call
cleanup), owned callback/method teardown. No extra attack/flags/slots/Hit/Java/fix.
B41/PZNS/current API matrix delivered; old NPC setters absent installed B42, native
AI control handoff candidate still unproven.267tests/116syntax pass isolated,
LuaLS88legacy/no new. Native UI/trace NOT RUN. Restart, Information -> Diagnostics
-> Start combat trace, report trace logged. Docs COMBAT_HANDOFF_TRACE_B42.md on
source ref; report mail/orchestrator/inbox/2026-11-17-combat-03-delivery.md.
Prior evidence/Test04 R1 preserved; Test03 observer deferred. No source merge.

## SSR-INVENTORY-01 — native inventory UI compatibility audit (2026-11-17)
User confirmed investigate first: separate survivor-owned inventory UI reusing native B42 presentation/actions where safe (icons, bags, worn/held, wear/unequip/drop, right click) without replacing/reparenting the human inventory UI; eventually additive player inventory Give To -> Survivor Name using SSR transfer semantics. Compare installed B42.22.2 UI Java/Lua and SSR's SuperSurvivorInventory/Loadout and transfer/clothing utilities, document obsolete/unsafe local-player assumptions and phased proof. Investigation only, NO UI/action code authorized. Assignment ai-workflow/assignments/inventory-b42-investigation-01.md; implementer inbox ai-workflow/mail/implementer/inbox/2026-11-17-inventory-01-native-ui-audit.md; STATUS REQUESTED / NOT ACKNOWLEDGED. Coordinate existing exclusive implementation checkout with Combat03, no parallel owners.


Combat03 ACTUAL NATIVE TRACE verified17November:5traces IDs9/1/5/5/5,98complete
natural request returns ALLfalse,busy (102entries,4returns log-cap-censored).
Roderick15 in-range Attack requests rejectedbusy; all startedtrue/initiatefalse/
no swing, preexisting at every start. All5 hit80line cap and report own method
restored, no actual errors. Stage(d) request rejection now observed, original
flag setter/handoff cause remains unobserved. No more alreadybusy traces needed
for gate; no fixes/resets/extra observer added. Evidence/docs6a51060e0c8f451c70fef2927e8bdcf7b642d0a8
on codex/persistence-b42; report mail/orchestrator/inbox/2026-11-17-combat-03-runtime-results.md.
Inventory01 mail preserved/read but not acknowledged/started during this user log
check; separate startup/priority next. Test04 R1 restart proof pending; Test03
early observer deferred. No production source merge or combat success claimed.


Inventory01 ACKNOWLEDGED / READ-ONLY INVESTIGATION by exclusive existing local
Codex codex/persistence-b42, after Combat03 runtime report; no overlapping code
work. Native inventory reuse audit/matrix/proposal only, no UI/action edits.
Ack: mail/orchestrator/inbox/2026-11-17-inventory-01-ack.md.
