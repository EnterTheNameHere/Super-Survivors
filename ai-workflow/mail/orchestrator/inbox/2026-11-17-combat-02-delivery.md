FROM: Local Codex implementer
TO: SSR Orchestrator
DATE: 2026-11-17
STATUS: DELIVERED FOR REVIEW / NATIVE UI AND SNAPSHOT NOT RUN
SUBJECT: SSR-COMBAT-02 explicit existing-NPC combat snapshot

SOURCE BRANCH: exclusive existing codex/persistence-b42
SOURCE COMMIT: 135f7993a93d009f086334f21bd914f8d258aec8
PARENT ACK: da2c6f966a77b75a382bdb1a9e4fe0f41ee3d22e
START: 342e44d575ea9a541ff9fee7953c5e44e3d1b3b5
W:/Projects/Super-Survivors same owner/worktree; unrelated source/settings/common
save edits preserved/excluded. No implementation merge or Java modification.

IMPLEMENTED:
Combat - inspect existing survivor, sixth SS Tests definition, readOnly. New
compact survivor dropdown/manual Refresh survivors, explicit placeholder/no default
NPC. At most256 wrapper inspections/128choices; IDs/names sorted, unchanged refs
preserved on refresh, replacement requires reselection. Guards existing owned
IsoPlayer ID>0, matching existing ModData.ID, same world/cell, alive, native moving
Set + square membership; excludes all local slots0-3/singleton/MainPlayer.
Flat parameters copied at start, target revalidated at execution before/after.
No dead/unloaded/replaced actor adoption. Existing global SP/living human/option
and per-run consent/cleanup gates preserved. During run selection/refresh disabled.

Single next-tick capture: time/native world frame/mod render counter/speed/world;
SSR ownership and actor/human state; cached role vs AIMode/group/bravery/follow ID/
range/ROE/AIEnabled/filter presence/wait/reducer/cooldown/walking/trigger counters;
LastEnemeySeen type/alive/xyz/rooms/weighted distance/deltaZ/native attack range;
cached perception/close counts, task front/count/update-limit +12names max;
primary weapon type/condition/HandWeapon/ammo/chamber/clip/jam; native actual
NPC/local/aiming/start/initiate/performing attack/shove/swing-state/authorization/
hand-to-hand/weapon readiness; health/unbandaged injury count max64parts.
Sorted scalar strings capped320chars, below200-line output cap. Missing/null
separate. No target -> explicit no-target-at-snapshot, not broken perception.
Result always INCONCLUSIVE; no request/hit history or root cause inferred.

AIComponent controlVars explicitly unavailable: no verified Lua Class token for
getECSComponent(AIComponent.class); no reflection/unverified getter fallback.
Actual native isAiming for NPC uses verified native getter of control var. Native
isWeaponReady is distinct from mutating SSR WeaponReady. Filter acceptance and
policy predicates deliberately not executed, partial cached inputs not complete
policy inference. Frame getter was verified on IsoWorld (not Core/GameTime).

No DoVision/getLuaObjectList/RealCanSee/WeaponReady/needToFollow/pursue-score/task
predicates/updateTime/AIManager/pressedAttack calls. No actors/zombies/spawn/
movement/equipment/timed actions/attack requests/Hit/local-slot/model/cheat writes.
Actor ModData read only after hasModData; no world GMD access at all, no RNG or
fixture token. Latest result in memory, no disk baseline/history. Test04 R1 module
unchanged, all its persistence regressions pass. No temporal sampling/interception
or new callback from diagnostic. UI Availability checks are guards, not snapshots.

NATIVE EVIDENCE:
Installed42.22.2 rev3d39148846, JAR SHA256 unchanged
3c4a7c5f149d784758c6fb5f8fa85f3a21d572e38bc081400e89035f8120d287.
Current native extracts/CFR .venv/combat02-native, .venv/combat02-decompiled plus
verified prior combat sources. Exposer registers relevant player/weapon/body/cell/
square/state/HashSet/ArrayList/world classes. Pure direct getter bytecode checked
for frame, attack/animation/aim/block/ammo/chamber/jam/clip/bandage flags. Existing
component/state lookup/getName inspected, no params-map allocation; hand-to-hand
checks existing item replacement script fields/masks, readiness existing model/
action override/muzzle; native range uses perk/weapon read-only calculations.
No getter guessed from B41. Native missing fields remain protected unavailable.

VALIDATION:
Isolated staged export (user working edits excluded), PZ_GAME_DIR actual install:
245 tests PASS, no skips; 114/114 Lua5.1 syntax PASS. 13 dedicated snapshot tests,
new UI selection/regression and current-JAR flag/frame/Set contract check.
Covers wrong/stale ID/world/wrapper/actor, no enemy/weapon, dead/unloaded/local
actor guards, missing fields, cached queues/targets, no mutation/automatic run/
RNG/save write, bounded queue/repeat, frozen inputs/manual refresh. Existing human
baseline tests now check six registered entries and remain passing. Release fixture
keeps new module. Editor API fingerprint regenerated from isolated intended source.
LuaLS88 legacy diagnostics in13files, none snapshot/registry/UI; not globally clean.
No actual in-game UI render/snapshot or combat repro performed. Mock/native bytecode
checks do not validate actor animation or hit outcomes. Documentation links checked.

MODIFIED SOURCE PATHS:
42/media/lua/client/Testing/SSRCombatSnapshot.lua (new), Testing/SSRTests.lua
(optional flat parameters), 5_UI/SSRTestsWindow.lua (selector); tests/test_combat_snapshot.py
(new), test_tests_ui.py, test_human_visual_diagnostics.py, test_persistence_engine_api.py,
test_release_package.py; editor/pz-api/library.lua fingerprint; docs/COMBAT_LIVE_SNAPSHOT_B42.md
(new), TESTS_UI.md, LOCAL_HANDOFF.md. No production combat/task/survivor change.

USER STEPS:
Restart, mod Debug Options On, right-click SS Tests..., Combat - inspect existing
survivor, Refresh survivors if needed, select explicit ID/name, acknowledge/Run
while observing NPC near a zombie. Unpause for next-tick run. Report NPC ID/what
was visibly happening. Log prefix [SS Tests][combat-existing-snapshot]. User needs
no -debug. INCONCLUSIVE/no-target are observation outcomes, not automatic failure.

NEXT:
Orchestrator reviews/user runs snapshot. If insufficient, separately authorize
bounded one-owned-NPC temporal request-return/event observer: exact original call
once, unchanged returns/errors, verified event argument contracts, small time/log
cap, explicit cancel and owned wrapper restoration on menu/world/actor/timeout.
No extra attack/forced update/hit; verify hooks first. Proposal in docs, not built.
Proven equip/pursue/follow defects remain unchanged pending separate assignment.
Test04 R1 save/restart proof pending separately; Test03 early observer deferred.
