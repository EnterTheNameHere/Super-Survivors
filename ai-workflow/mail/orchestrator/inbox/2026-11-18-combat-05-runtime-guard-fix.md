FROM: Local Codex implementer
TO: SSR Orchestrator
DATE: 2026-11-18
STATUS: TWO NATIVE STARTS VERIFIED / GUARD FIX DELIVERED / POST-FIX RUN PENDING
SUBJECT: Native per-actor singleton caused immediate Combat05 false rejection

User asked to check log. console.txt has two earliest-attack starts for ID5 at
frames14268/15209, stopping14269/15210 (about2ms) with guard Human/control actor
cannot be inspected as NPC. Both initially started/initiate/animation/swing false,
ready true, Base.SpearScrewdriver, target present/range false, tasks Follow/Attack.
All request/StopWalk/accepted/swing/hitpoint/rise counts0; both hooks restoredtrue.
No Lua exception during either run; no natural attack handoff evidence collected.
Preserved12records + consoleSHA256 in docs/evidence/COMBAT_FIRST_ATTACK_2026-11-18.log.

SOURCE CAUSE: installed IsoPlayer.updateInternal2 assigns static instance=this
immediately before OnPlayerUpdate, including SP nonlocal actors. Shared snapshot
validator actor==IsoPlayer.getInstance therefore mistakes selected NPC for human
at early callback. New observer's frozen instance comparison would also falsely
stop on normal update changes. Singleton is an update cursor, not stable human
ownership. Corrected both assumptions, not combat behavior.

Source commit c69ff48099395a82f9ea6de6b8b5d0e705d9253e; parent
f6d360b0d69d1859298c5b2d0ba6870fd3b87025, exclusive codex/persistence-b42.
Paths: SSRCombatSnapshot.lua and SSRCombatFirstAttack.lua under client/Testing;
tests/test_combat_snapshot.py, tests/test_combat_first_attack.py; diagnostic docs,
LOCAL_HANDOFF and evidence file. Shared snapshot/general trace now also use stable
ownership: exclude SSR MainPlayer ID, actual local slots and native isLocalPlayer;
preserve registry/world/cell/life/loaded guards. First observer still freezes
MainPlayer and all4actual slots. No singleton getter dependency or setter/restore.
User human and owned slots remain excluded; no production combat/AI/flags/damage/
Java/fixture/save changes, no trace rearm. User source/settings/common preserved.

CHECKS: isolated staged export, PZ_GAME_DIR installed game, unittest discover -v:
291passed/no skips; Lua syntax117/117. New regression simulates instance=selected
NPC before OnPlayerUpdate, survives and preserves snapshot/request observation;
also traps singleton reads. Existing real local slot/MainPlayer rejection stays.
diff --check pass. LuaLS not rerun for narrow guard condition change; initial
delivery baseline88legacy/no changed diagnostics remains historical check only.

Restart to load fix, then same explicit Information -> Diagnostics -> Start earliest
natural attack observation, existing eligible actor only. Keep Information visible.
Post-fix native execution still PENDING. Existing two starts prove entry and safe
false-positive teardown, not first setter/swing/collision/damage or both UI layouts.
Do not promote to combat success. Canonical ai-workflow only, no source merge.
Test04 R1 pending/Test03 observer deferred/inventory deferred unchanged. Next actor
user reruns observer; orchestrator reviews evidence/source and separate damage path.
