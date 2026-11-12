# Whole-Lua name audit — 2026-10-21

Scanned all 109 active mod Lua files against public method names in the installed
42.21.0 JAR and method definitions in both mod and installed vanilla Lua. Run:

```powershell
.\.venv\Scripts\python.exe tools/audit_lua_names.py G:\Steam\steamapps\common\ProjectZomboid
```

This inventories colon-call names. A name existing somewhere does not establish
the receiver type, argument types/arity, Lua exposure, action lifecycle or behavior.
Global functions, Java field access and data identifiers are outside its scope.
Comment/string contents and standard Lua string methods are excluded. Dynamic
method assignment of the form `Table.method = function` is recognized.

## Confirmed fixes in this pass

- The new frame-13095 error is `ISApplyBandage:perform`, line 71: removed
  `HasTrait`. Rebased the bundled override onto the installed B42 action, including
  typed HEMOPHOBIC/PANIC, mutation in complete(), events, sounds, sync and duration.
  Tests cover constructor timing, instant action, UI-only perform and bandage
  application/panic/XP in complete. This is mocked service validation, not a live
  medical gameplay result.
- AI, eating/chopping/foraging tasks and both survivor status panels now use
  Stats:get/set(CharacterStat) for hunger, thirst, fatigue, endurance, boredom,
  morale, sanity, idleness, pain, unhappiness and wetness. Debug infection values
  likewise use ZOMBIE_INFECTION. Numeric formulas and thresholds are preserved.
- Remaining Marksman/Handy trait calls use hasTrait(CharacterTrait).
- Dialogue name lookup uses the descriptor's getForename. Threatening uses
  setIsAiming; debug running output uses isRunning.
- Conditional legacy silencer attachment uses HandWeapon:attachWeaponPart;
  this does not validate that the third-party Silencer mod itself supports B42.
- Gift clothing detection uses instanceof(Clothing). Fixed an adjacent accidental
  second call on DebugSay's return value.
- Removed the leftover SuperSurvivorTest event hook whose only behavior was
  calling `now()` on an uninitialized local variable. No gameplay logic existed
  in that handler.

## Remaining unmatched call sites

| File | Method | Assessment |
| --- | --- | --- |
| client/5_UI/SuperSurvivorsContextMenu.lua | SetState (1) | Old debug UnStuck control. Java now spells it setState, but AdvancedAnimator is not explicitly Lua-exposed by this build; do not blindly substitute. |
| client/ISUI/PlayerStats/ISPlayerStatsUI.lua | getProfession (3), setProfession (1), setAccessLevel (1) | Bundled B41 admin UI. Needs a coherent rebase for typed professions, traits, roles and sync. It also still uses old getTraits collection mutations; those are not caught by a global name-only inventory. |
| client/TimedActions/ISNPCScavengeAction.lua | setItemScavenged (1), updateZoneProgress (1) | Optional legacy scavengeUI callback path. No matching current UI definitions. The old zone/recipe/foraging design needs a separate port; stat calls alone do not establish compatibility. |

Other copied actions/UI can have stale lifecycle or typed-argument assumptions
even when every method name exists. Bandaging and glass removal were ported;
barricading, eating, disinfection, inventory actions and other overrides still
need behavior review. Farming and multiplayer remain separate work.

Validation: 53 tests pass with PZ_GAME_DIR set; all 109 Lua files pass Lua 5.1
syntax checks; git diff --check passes. A new test verifies all active explicit
CharacterStat, CharacterTrait and MoodleType constants against the installed JAR.

God mode for the current disposable test world is available through the exposed
IsoGameCharacter API: `getSpecificPlayer(0):setGodMod(true)`; pass false to disable.
The command was verified against the installed JAR and vanilla debug menu usage.
No game control tool was used to enable it on the user's behalf.

The rendering issue remains unresolved. No model-reset result was logged before
the medical error; the previously installed resetModelProbe is still available.
