# Combat: inspect an existing survivor — B42

17 November 2026, SSR-COMBAT-02. **Implemented; native UI/snapshot NOT RUN.**
One explicit read-only snapshot of an existing loaded SSR survivor. No combat
fix, test spawn, zombie creation, forced attack, task update or event interception.
Findings motivating this diagnostic: [COMBAT_B42_INVESTIGATION_01.md](COMBAT_B42_INVESTIGATION_01.md).

## Run

1. Restart to load the new module and UI. In single-player with one living human,
   enable Options -> Superb Survivors -> Debug Options -> On. Native -debug is
   not required and is not consulted by this diagnostic.
2. Find an existing survivor behaving incorrectly near a zombie. Prefer one
   healthy, equipped NPC near one zombie in an open area, same floor, with the
   human nearby. Use a disposable world for any manual combat setup. This control
   creates neither actor nor equipment and does not provoke a target.
3. Right-click the world -> SS Tests... -> **Combat - inspect existing survivor**.
4. In the new survivor dropdown choose **ID <number> - <name>**. Its initial
   placeholder deliberately selects nobody. Click **Refresh survivors** if none
   were loaded when the list was populated. No automatic substitute is selected.
5. Acknowledge the existing warning and Run. Wait for the next game tick; if
   paused, unpause to execute it. Availability explains rejected selections.
6. Report the NPC ID and what you actually saw (zombie visible/near, NPC movement,
   attack animation or lack of it). Output is in the window and console.txt under
   `[SS Tests][combat-existing-snapshot]`. Re-run explicitly for another instant.

The survivor dropdown is used only by this test, disabled for other definitions.
Refresh preserves selection only for the identical wrapper+actor/world/cell;
replacements require choosing again. List population scans at most256 SSR wrapper
entries and lists at most128 valid NPCs, with cap notice. It never scans the world.
Normal UI Availability rechecks ownership/liveness without capturing combat fields;
no sampling or automatic test execution is installed. During an active run the
survivor selector/refresh button are disabled. Other test choices and per-run
consent semantics remain. Six visible definitions in the current registry.

## Guards and lifetime

Selected ID must be an integer >0, an existing SSM wrapper holding the identical
IsoPlayer actor, matching its already-existing ModData.ID, living and in the
current cell, registered in both native world moving-object set and square list.
It excludes every local slot0-3, the singleton and manager's MainPlayer. An owned
nonlocal actor with isNpc=false is reported as such, not silently changed.
Selections cannot cross worlds/cells or adopt a replacement actor at the same ID.
Start freezes the flat selection table; execution revalidates before/after reads.
A lost actor fails setup or discards the snapshot, never repairs/adopts it.
Generic one-local-human/SP/debug-option/living-loaded-human guards remain.

Existing cleanup failure still blocks writes and allows this readOnly observation
without clearing the failure. No gameplay RNG/native-fixture boot token is drawn.
No ModData is created: actor:getModData is called only after hasModData confirms
existing data, and diagnostic code does not access world GlobalModData at all.
Test04 R1 world-saved human baseline is independent and unchanged. The latest
single result replaces that test's previous result in memory; no disk baseline
or snapshot history is saved. Java refs in the input stay session-only.

## Output and limits

Sorted scalar fields distinguish `<null>` from `UNAVAILABLE (reason)`; strings
are bounded to320 characters, queue names to12 entries, body parts to64. Output
fits the registry's200-line limit (about100 fields, depending on target/weapon/
queue). No inventory traversal, world/zombie scan or expensive repeated vision.

- `capture`: millisecond timestamp, native world frame number, mod render-update
  counter (a different clock), world/build/game speed/world age. The snapshot is
  execution-time data, not the exact frame when Run was clicked.
- `ownership`, `human`, `actor`: selected ID/type/ref/membership verification,
  human loaded/dead/asleep, NPC XYZ/room presence, health, unbandaged injury count.
- `policy`, `scheduler`: group ID/role vs AIMode, bravery/ROE, felldown,
  follow target ID/follow distance/attack range, AIEnabled/manager MainPlayer/filter
  presence, reducer/delay/wait/cooldown,
  walking-permitted/trigger/swipe counters. Unset caches are labeled unavailable.
  Filter acceptance/needToFollow/tooScared/group-bravery predicates are deliberately
  not called. Follow-target distances and complete policy decisions are not inferred.
- `perception`, `target`: cached seen/danger/close counts and LastEnemeySeen,
  target type/dead/XYZ/room presence, room equality, weighted distance/Z difference,
  public native range result. Outside/outside null rooms can compare equal.
  Counters can be stale or danger>0 with no selected target; no refresh is forced.
- `queue`: current cached front, count/update count/limit, at most12 task names.
  No isValid/isComplete/update/AI decision is invoked to predict removal.
- `weapon`: actual primary presence/type/condition and, for HandWeapon, firearm/
  ammo/chamber/clip/jam state. Having a weapon in inventory is not equivalent to
  equipping it. No ammo unpacking, repair, unjam, reload or equip.
- `native`: NPC/local/dead/asleep/running/blockMovement, actual aiming,
  initiateAttack/attackStarted, attack/shove animation, aim-at-floor/doShove,
  authorization/hand-to-hand/native weapon-readiness, state name and exact native
  SwipeStatePlayer equality. They describe state at this instant, not a hit result.

AIComponent controlVars are explicitly UNAVAILABLE: its public getter needs an
AIComponent Class token through getECSComponent; a safe Lua-accessible token was
not established. No reflection, getAnimationPlayer, model creation or fallback
setter is attempted. Actual isAiming for an NPC reads its native control variable
through the verified character getter; other native flags are separate observations.
Missing native getters are unavailable, never silently false. Native isWeaponReady
is distinct from the mod's mutating WeaponReady. Current state getters read the
existing component/state, not getStateMachineParams (which can create a map).

Result is **INCONCLUSIVE** with an explanation. No target means only no target at
snapshot, not proven perception failure. An Attack queue/true attack flag does
not prove request entry, a new swing, native collision or damage. A single frame
cannot reveal an earlier rejection or flag overwrite. No root-cause/PASS claim.

## Installed API evidence

Installed42.22.2 rev3d39148846, JAR SHA256
3c4a7c5f149d784758c6fb5f8fa85f3a21d572e38bc081400e89035f8120d287.
Read-only native extracts .venv/combat02-native and CFR .venv/combat02-decompiled;
prior current-JAR combat sources retained. Public selected classes are registered
in LuaManager.Exposer (IsoPlayer/IsoGameCharacter/BodyPart/BodyDamage/HandWeapon/
InventoryItem/IsoCell/IsoGridSquare/SwipeStatePlayer/HashSet/ArrayList/IsoWorld).
Missing exposure at runtime is reported/rejected through protected reads.

Verified direct field getters: IsoWorld.getFrameNo, attackStarted/initiateAttack/
blockMovement, performing attack/shove, aimAtFloor, current ammo, jam/chamber/clip,
bandaged. State.getName is class.simpleName; state-machine/component getters
retrieve existing fields/maps (getECSComponent throws if missing, no creation).
Native isWeaponReady checks action hand override, existing primary model ready
and ranged muzzle attachment; canPerformHandToHandCombat checks existing hand
items/replacement script fields/masks. Neither performs the corresponding action.
Native IsAttackRange calls weapon max/min/range modifier and perk reads; Z and
strict distance checks, no attacks. BodyPart.HasInjury/bandaged read injury flags/
timers; health/body parts return existing objects. getBodyDamageRemote is not used.

The diagnostic deliberately avoids DoVision/getLuaObjectList (writes global Objects),
RealCanSee (god branch writes alpha), WeaponReady, needToFollow, pursue score,
updateTime, task predicates, AIManager, pressedAttack and every gameplay setter.
No timed actions, event hooks, temporary wrappers or save APIs are added.

## Verification and next scope

Automated mocks cover explicit/invalid IDs, guards/dead/unloaded/membership,
wrong-world and replaced wrappers/actors, local slots/singleton/MainPlayer,
missing native fields and missing existing ModData, no target/weapon, cached
queue/target preservation, mutation traps/no RNG/no auto execution, bounded queue,
repeat snapshots and UI selection freezing/refresh. Native bytecode tests check
reviewed direct field getters and actual native moving collection type Set.
Mock UI contracts do not validate native rendering/layout; native run NOT RUN.

If this snapshot cannot distinguish the stage, propose a separately authorized,
opt-in bounded observer for one owned ID/actor/world: exact entry/return tracing
of existing requestCombatAttack once per natural call, unchanged errors/returns,
filtered native swing/hit events, timestamp/frame, small cap/timeout, explicit
cancel and guarded cleanup on world/menu/actor change. Restore an installed
wrapper only if it is still ours. Verify event arguments/exposure first. No extra
attack, forced tick, state/slot manipulation, arbitrary cleanup or direct Hit.
This observer is a proposal only; no temporal instrumentation is implemented.

Delivery verification: **245 automated tests pass**, no skips with installed
PZ_GAME_DIR, and **114/114 Lua5.1 syntax checks pass** in an isolated staged export
excluding user edits. LuaLS retains88 legacy diagnostics in13 files, none in the
new snapshot or registry/Tests window. Human baseline persistence tests remain
passing. Actual native UI/layout and snapshot execution still NOT RUN.
