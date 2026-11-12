# Startup/spawn failure evidence — 2026-10-21

Source: `C:\Users\Enter\Zomboid\console.txt`; Project Zomboid 42.21.0, revision 4a0e9546ec.
User reports a fresh single-player world with only Superb Survivors enabled.
Command: `SuperbSurvivorsDebug.spawn()`. These are pre-fix errors.

## First startup error

```text
ERROR: General      f:0 at KahluaThread.flushErrorMessage      > dumping Lua stack trace
-----------------------------------------
STACK TRACE
-----------------------------------------
	Lua(Vanilla).stdin(spawnpoints.lua:1)
	Lua((MOD:Superb Survivors)).retrieveMoodles(SuperSurvivorSpeakConditions.lua:93)
	Lua((MOD:Superb Survivors)).checkIfLoaded(SuperSurvivorSpeakConditions.lua:86)
ERROR: General      f:0> Lua(Vanilla).stdin> Exception thrown
	java.lang.NullPointerException: Cannot invoke "zombie.characters.Moodles.Moodle.getLevel()" because the return value of "java.util.Map.get(Object)" is null at Moodles.getMoodleLevel(Moodles.java:40).
	Stack trace:
		zombie.characters.Moodles.Moodles.getMoodleLevel(Moodles.java:40)
		java.base/jdk.internal.reflect.DirectMethodHandleAccessor.invoke(Unknown Source)
		java.base/java.lang.reflect.Method.invoke(Unknown Source)
		se.krka.kahlua.integration.expose.caller.MethodCaller.call(MethodCaller.java:58)
		se.krka.kahlua.integration.expose.LuaJavaInvoker.call(LuaJavaInvoker.java:194)
		se.krka.kahlua.integration.expose.LuaJavaInvoker.call(LuaJavaInvoker.java:184)
		se.krka.kahlua.vm.KahluaThread.callJava(KahluaThread.java:178)
		Lua(Vanilla).stdin(spawnpoints.lua:1)
		Lua((MOD:Superb Survivors)).retrieveMoodles(SuperSurvivorSpeakConditions.lua:93)
		Lua((MOD:Superb Survivors)).checkIfLoaded(SuperSurvivorSpeakConditions.lua:86)
		se.krka.kahlua.vm.KahluaThread.luaMainloop(KahluaThread.java:795)
		se.krka.kahlua.vm.KahluaThread.call(KahluaThread.java:162)
		se.krka.kahlua.vm.KahluaThread.pcall(KahluaThread.java:1740)
		se.krka.kahlua.vm.KahluaThread.pcallvoid(KahluaThread.java:1572)
		se.krka.kahlua.integration.LuaCaller.pcallvoid(LuaCaller.java:60)
		se.krka.kahlua.integration.LuaCaller.protectedCallVoid(LuaCaller.java:131)
		zombie.Lua.Event.trigger(Event.java:55)
		zombie.Lua.LuaEventManager.triggerEvent(LuaEventManager.java:248)
		zombie.gameStates.IngameState.enter(IngameState.java:782)
		zombie.gameStates.GameStateMachine.update(GameStateMachine.java:95)
		zombie.GameWindow.logic(GameWindow.java:391)
		zombie.GameWindow.frameStep(GameWindow.java:791)
		zombie.GameWindow.mainThreadStep(GameWindow.java:568)
		zombie.MainThread.mainLoop(MainThread.java:69)
		java.base/java.lang.Thread.run(Unknown Source)
```

## Spawn error

```text
ERROR: General      f:767 at KahluaThread.flushErrorMessage      > dumping Lua stack trace
-----------------------------------------
STACK TRACE
-----------------------------------------
	Lua((MOD:Superb Survivors)).spawnPlayer(SuperSurvivor.lua:579)
	Lua((MOD:Superb Survivors)).new(SuperSurvivor.lua:25)
	Lua((MOD:Superb Survivors)).spawnSurvivor(SuperSurvivorManager.lua:148)
	Lua((MOD:Superb Survivors)).spawn(SuperbSurvivorsDebug.lua:37)
	Lua(Vanilla).console(worldmap-annotations.lua:1)
Lua fail. Message: Object tried to call nil in spawnPlayer
	se.krka.kahlua.vm.KahluaUtil.fail(KahluaUtil.java:96)
	Lua((MOD:Superb Survivors)).spawnPlayer(SuperSurvivor.lua:579)
	Lua((MOD:Superb Survivors)).new(SuperSurvivor.lua:25)
	Lua((MOD:Superb Survivors)).spawnSurvivor(SuperSurvivorManager.lua:148)
	Lua((MOD:Superb Survivors)).spawn(SuperbSurvivorsDebug.lua:37)
	Lua(Vanilla).console(worldmap-annotations.lua:1)
	se.krka.kahlua.vm.KahluaThread.luaMainloop(KahluaThread.java:763)
	se.krka.kahlua.vm.KahluaThread.call(KahluaThread.java:162)
	se.krka.kahlua.vm.KahluaThread.pcall(KahluaThread.java:1740)
	se.krka.kahlua.vm.KahluaThread.pcall(KahluaThread.java:1544)
	se.krka.kahlua.integration.LuaCaller.pcall(LuaCaller.java:69)
	se.krka.kahlua.integration.LuaCaller.protectedCall(LuaCaller.java:109)
	zombie.ui.UIDebugConsole.ProcessCommand(UIDebugConsole.java:391)
	zombie.ui.UITextBox2.onKeyEnter(UITextBox2.java:1051)
	zombie.core.Core.updateKeyboardAux(Core.java:2069)
	zombie.core.Core.updateKeyboard(Core.java:2199)
	zombie.core.Core.DoFrameReady(Core.java:3131)
	zombie.GameWindow.frameStep(GameWindow.java:820)
	zombie.GameWindow.mainThreadStep(GameWindow.java:568)
	zombie.MainThread.mainLoop(MainThread.java:69)
	java.base/java.lang.Thread.run(Unknown Source)
```

## Follow-up run: trait initialization failure

After the NPC flag/moodle fixes, both automatic world spawning and the manual
debug probe reached the obsolete `getTraits()` call at line 609.
The following is the manual probe stack from the new run.

```text
ERROR: General      f:598 at KahluaThread.flushErrorMessage      > dumping Lua stack trace
-----------------------------------------
STACK TRACE
-----------------------------------------
	Lua((MOD:Superb Survivors)).spawnPlayer(SuperSurvivor.lua:609)
	Lua((MOD:Superb Survivors)).new(SuperSurvivor.lua:25)
	Lua((MOD:Superb Survivors)).spawnSurvivor(SuperSurvivorManager.lua:148)
	Lua((MOD:Superb Survivors)).spawn(SuperbSurvivorsDebug.lua:37)
	Lua(Vanilla).console(worldmap-annotations.lua:1)
DEBUG-MODE STACK TRACE:
	Lua((MOD:Superb Survivors)).spawnPlayer(SuperSurvivor.lua:609)
	Lua((MOD:Superb Survivors)).new(SuperSurvivor.lua:25)
	Lua((MOD:Superb Survivors)).spawnSurvivor(SuperSurvivorManager.lua:148)
	Lua((MOD:Superb Survivors)).spawn(SuperbSurvivorsDebug.lua:37)
	Lua(Vanilla).console(worldmap-annotations.lua:1)
	se.krka.kahlua.vm.KahluaThread.luaMainloop(KahluaThread.java:1108)
	se.krka.kahlua.vm.KahluaThread.call(KahluaThread.java:162)
	se.krka.kahlua.vm.KahluaThread.pcall(KahluaThread.java:1740)
	se.krka.kahlua.vm.KahluaThread.pcall(KahluaThread.java:1544)
	se.krka.kahlua.integration.LuaCaller.pcall(LuaCaller.java:69)
	se.krka.kahlua.integration.LuaCaller.protectedCall(LuaCaller.java:109)
	zombie.ui.UIDebugConsole.ProcessCommand(UIDebugConsole.java:391)
	zombie.ui.UITextBox2.onKeyEnter(UITextBox2.java:1051)
	zombie.core.Core.updateKeyboardAux(Core.java:2069)
	zombie.core.Core.updateKeyboard(Core.java:2199)
	zombie.core.Core.DoFrameReady(Core.java:3131)
	zombie.GameWindow.frameStep(GameWindow.java:820)
	zombie.GameWindow.mainThreadStep(GameWindow.java:568)
	zombie.MainThread.mainLoop(MainThread.java:69)
	java.base/java.lang.Thread.run(Unknown Source)
```

## Follow-up run: player naming failure

The next manual spawn reached the obsolete `setForname()` call at line 677.

```text
ERROR: General      f:328 at KahluaThread.flushErrorMessage      > dumping Lua stack trace
-----------------------------------------
STACK TRACE
-----------------------------------------
	Lua((MOD:Superb Survivors)).spawnPlayer(SuperSurvivor.lua:677)
	Lua((MOD:Superb Survivors)).new(SuperSurvivor.lua:25)
	Lua((MOD:Superb Survivors)).spawnSurvivor(SuperSurvivorManager.lua:148)
	Lua((MOD:Superb Survivors)).spawn(SuperbSurvivorsDebug.lua:37)
	Lua(Vanilla).console(worldmap-annotations.lua:1)
DEBUG-MODE STACK TRACE:
	Lua((MOD:Superb Survivors)).spawnPlayer(SuperSurvivor.lua:677)
	Lua((MOD:Superb Survivors)).new(SuperSurvivor.lua:25)
	Lua((MOD:Superb Survivors)).spawnSurvivor(SuperSurvivorManager.lua:148)
	Lua((MOD:Superb Survivors)).spawn(SuperbSurvivorsDebug.lua:37)
	Lua(Vanilla).console(worldmap-annotations.lua:1)
	se.krka.kahlua.vm.KahluaThread.luaMainloop(KahluaThread.java:1108)
	se.krka.kahlua.vm.KahluaThread.call(KahluaThread.java:162)
	se.krka.kahlua.vm.KahluaThread.pcall(KahluaThread.java:1740)
	se.krka.kahlua.vm.KahluaThread.pcall(KahluaThread.java:1544)
	se.krka.kahlua.integration.LuaCaller.pcall(LuaCaller.java:69)
	se.krka.kahlua.integration.LuaCaller.protectedCall(LuaCaller.java:109)
	zombie.ui.UIDebugConsole.ProcessCommand(UIDebugConsole.java:391)
	zombie.ui.UITextBox2.onKeyEnter(UITextBox2.java:1051)
	zombie.core.Core.updateKeyboardAux(Core.java:2069)
	zombie.core.Core.updateKeyboard(Core.java:2199)
	zombie.core.Core.DoFrameReady(Core.java:3131)
	zombie.GameWindow.frameStep(GameWindow.java:820)
	zombie.GameWindow.mainThreadStep(GameWindow.java:568)
	zombie.MainThread.mainLoop(MainThread.java:69)
	java.base/java.lang.Thread.run(Unknown Source)
```

## Follow-up run: typed worn-item location failure

The constructor reached `SuitUp` and passed a legacy string body location to
`setWornItem`, which now requires `ItemBodyLocation`. This is an argument-type
failure that the earlier name/arity audit did not establish compatibility for.

```text
ERROR: General      f:279> Lua((MOD:Superb Survivors)).SuitUp> Exception thrown
	java.lang.RuntimeException: No implementation found for function: setWornItem(class zombie.characters.IsoPlayer IsoPlayer{  Name:null,  ID:84 }, class java.lang.String Jacket, null null)) at MultiLuaJavaInvoker.call(MultiLuaJavaInvoker.java:113).
	Stack trace:
		se.krka.kahlua.integration.expose.MultiLuaJavaInvoker.call(MultiLuaJavaInvoker.java:113)
		se.krka.kahlua.vm.KahluaThread.callJava(KahluaThread.java:178)
		Lua((MOD:Superb Survivors)).SuitUp(SuperSurvivor.lua:4672)
		Lua((MOD:Superb Survivors)).new(SuperSurvivor.lua:142)
		Lua((MOD:Superb Survivors)).spawnSurvivor(SuperSurvivorManager.lua:148)
		Lua((MOD:Superb Survivors)).spawn(SuperbSurvivorsDebug.lua:37)
		Lua(Vanilla).console(worldmap-annotations.lua:1)
		se.krka.kahlua.vm.KahluaThread.luaMainloop(KahluaThread.java:795)
		se.krka.kahlua.vm.KahluaThread.call(KahluaThread.java:162)
		se.krka.kahlua.vm.KahluaThread.pcall(KahluaThread.java:1740)
		se.krka.kahlua.vm.KahluaThread.pcall(KahluaThread.java:1544)
		se.krka.kahlua.integration.LuaCaller.pcall(LuaCaller.java:69)
		se.krka.kahlua.integration.LuaCaller.protectedCall(LuaCaller.java:109)
		zombie.ui.UIDebugConsole.ProcessCommand(UIDebugConsole.java:391)
		zombie.ui.UITextBox2.onKeyEnter(UITextBox2.java:1051)
		zombie.core.Core.updateKeyboardAux(Core.java:2069)
		zombie.core.Core.updateKeyboard(Core.java:2199)
		zombie.core.Core.DoFrameReady(Core.java:3131)
		zombie.GameWindow.frameStep(GameWindow.java:820)
		zombie.GameWindow.mainThreadStep(GameWindow.java:568)
		zombie.MainThread.mainLoop(MainThread.java:69)
		java.base/java.lang.Thread.run(Unknown Source)
```

## Follow-up run: spawn succeeded, vision update failed

The probe logged survivor 4 at 10778,9764,0. The next survivor update failed
because the cell object collection is a Set in B42 and has no indexed `get(i)`.
Character construction is now observed in game; continued presence and AI are
still unverified.

```text
LOG  : Lua          f:275> [SuperbSurvivors] Spawned survivor 4 at 10778,9764,0
ERROR: General      f:286 at KahluaThread.flushErrorMessage      > dumping Lua stack trace
-----------------------------------------
STACK TRACE
-----------------------------------------
	Lua((MOD:Superb Survivors)).DoVision(SuperSurvivor.lua:1684)
	Lua((MOD:Superb Survivors)).update(SuperSurvivor.lua:2979)
	Lua((MOD:Superb Survivors)).update(SuperSurvivorManager.lua:193)
	Lua((MOD:Superb Survivors)).SuperSurvivorsOnTick(SuperSurvivorsMod.lua:73)
Lua fail. Message: Object tried to call nil in DoVision
	se.krka.kahlua.vm.KahluaUtil.fail(KahluaUtil.java:96)
	Lua((MOD:Superb Survivors)).DoVision(SuperSurvivor.lua:1684)
	Lua((MOD:Superb Survivors)).update(SuperSurvivor.lua:2979)
	Lua((MOD:Superb Survivors)).update(SuperSurvivorManager.lua:193)
	Lua((MOD:Superb Survivors)).SuperSurvivorsOnTick(SuperSurvivorsMod.lua:73)
	se.krka.kahlua.vm.KahluaThread.luaMainloop(KahluaThread.java:763)
	se.krka.kahlua.vm.KahluaThread.call(KahluaThread.java:162)
	se.krka.kahlua.vm.KahluaThread.pcall(KahluaThread.java:1740)
	se.krka.kahlua.vm.KahluaThread.pcallvoid(KahluaThread.java:1572)
	se.krka.kahlua.integration.LuaCaller.pcallvoid(LuaCaller.java:60)
	se.krka.kahlua.integration.LuaCaller.protectedCallVoid(LuaCaller.java:131)
	zombie.Lua.Event.trigger(Event.java:55)
	zombie.Lua.LuaEventManager.triggerEvent(LuaEventManager.java:248)
	zombie.GameWindow.onRender(GameWindow.java:877)
	zombie.GameWindow.frameStep(GameWindow.java:816)
	zombie.GameWindow.mainThreadStep(GameWindow.java:568)
	zombie.MainThread.mainLoop(MainThread.java:69)
	java.base/java.lang.Thread.run(Unknown Source)
```

## Follow-up run: typed shoe location in movement update

The probe again spawned survivor 4, this time at 10697,9383,0. The update passed
vision and reached walking-speed calculation; the worn-items shoe lookup still
passed a string where B42 requires `ItemBodyLocation.SHOES`. Full emitted stack:

```text
	java.lang.RuntimeException: expected argument of type ItemBodyLocation, got String at MethodArguments.assertValid(MethodArguments.java:128).
	Stack trace:
		se.krka.kahlua.integration.expose.MethodArguments.assertValid(MethodArguments.java:128)
		se.krka.kahlua.integration.expose.LuaJavaInvoker.call(LuaJavaInvoker.java:182)
		se.krka.kahlua.vm.KahluaThread.callJava(KahluaThread.java:178)
		Lua((MOD:Superb Survivors)).NPCgetwalkSpeedModifier(SuperSurvivor.lua:2840)
		Lua((MOD:Superb Survivors)).NPCcalculateWalkSpeed(SuperSurvivor.lua:2875)
		Lua((MOD:Superb Survivors)).update(SuperSurvivor.lua:3062)
		Lua((MOD:Superb Survivors)).update(SuperSurvivorManager.lua:193)
		Lua((MOD:Superb Survivors)).SuperSurvivorsOnTick(SuperSurvivorsMod.lua:73)
		se.krka.kahlua.vm.KahluaThread.luaMainloop(KahluaThread.java:795)
		se.krka.kahlua.vm.KahluaThread.call(KahluaThread.java:162)
		se.krka.kahlua.vm.KahluaThread.pcall(KahluaThread.java:1740)
		se.krka.kahlua.vm.KahluaThread.pcallvoid(KahluaThread.java:1572)
		se.krka.kahlua.integration.LuaCaller.pcallvoid(LuaCaller.java:60)
		se.krka.kahlua.integration.LuaCaller.protectedCallVoid(LuaCaller.java:131)
		zombie.Lua.Event.trigger(Event.java:55)
		zombie.Lua.LuaEventManager.triggerEvent(LuaEventManager.java:248)
		zombie.GameWindow.onRender(GameWindow.java:877)
		zombie.GameWindow.frameStep(GameWindow.java:816)
		zombie.GameWindow.mainThreadStep(GameWindow.java:568)
		zombie.MainThread.mainLoop(MainThread.java:69)
		java.base/java.lang.Thread.run(Unknown Source)
ERROR: General      f:1071 at KahluaThread.flushErrorMessage      > dumping Lua stack trace
-----------------------------------------
STACK TRACE
-----------------------------------------
	Lua((MOD:Superb Survivors)).NPCgetwalkSpeedModifier(SuperSurvivor.lua:2840)
	Lua((MOD:Superb Survivors)).NPCcalculateWalkSpeed(SuperSurvivor.lua:2875)
	Lua((MOD:Superb Survivors)).update(SuperSurvivor.lua:3062)
	Lua((MOD:Superb Survivors)).update(SuperSurvivorManager.lua:193)
	Lua((MOD:Superb Survivors)).SuperSurvivorsOnTick(SuperSurvivorsMod.lua:73)
DEBUG-MODE STACK TRACE:
	Lua((MOD:Superb Survivors)).NPCgetwalkSpeedModifier(SuperSurvivor.lua:2840)
	Lua((MOD:Superb Survivors)).NPCcalculateWalkSpeed(SuperSurvivor.lua:2875)
	Lua((MOD:Superb Survivors)).update(SuperSurvivor.lua:3062)
	Lua((MOD:Superb Survivors)).update(SuperSurvivorManager.lua:193)
	Lua((MOD:Superb Survivors)).SuperSurvivorsOnTick(SuperSurvivorsMod.lua:73)
	se.krka.kahlua.vm.KahluaThread.luaMainloop(KahluaThread.java:1108)
	se.krka.kahlua.vm.KahluaThread.call(KahluaThread.java:162)
	se.krka.kahlua.vm.KahluaThread.pcall(KahluaThread.java:1740)
	se.krka.kahlua.vm.KahluaThread.pcallvoid(KahluaThread.java:1572)
	se.krka.kahlua.integration.LuaCaller.pcallvoid(LuaCaller.java:60)
	se.krka.kahlua.integration.LuaCaller.protectedCallVoid(LuaCaller.java:131)
	zombie.Lua.Event.trigger(Event.java:55)
	zombie.Lua.LuaEventManager.triggerEvent(LuaEventManager.java:248)
	zombie.GameWindow.onRender(GameWindow.java:877)
	zombie.GameWindow.frameStep(GameWindow.java:816)
	zombie.GameWindow.mainThreadStep(GameWindow.java:568)
	zombie.MainThread.mainLoop(MainThread.java:69)
	java.base/java.lang.Thread.run(Unknown Source)
LOG  : General      f:1076> Saving worldgen params
LOG  : General      f:1076> Saving GlobalModData
LOG  : Lua          f:1076> removing all player data
LOG  : Lua          f:1076> - player: 0
LOG  : Lua          f:1076> removing all player data
LOG  : Lua          f:1076> - player: 0
LOG  : General      f:1076> GameThread exited.
```

## Follow-up: invisible survivors and window action failure

User reports spawned characters were not visible, though they appeared to act
and move. The earlier log recorded survivor 5 at 10778,9764,0 and survivor 6 at
10777,9757,0. No cause of invisibility is established yet. The subsequent
window-entry action passed the old duration `20` as B42 `vehiclePart`; this is
a separate confirmed exception. Representative full stack from the repeated error:

```text
ERROR: General      f:7525> Lua(Vanilla).waitToStart> Exception thrown
	java.lang.RuntimeException: Object tried to call nil in waitToStart at KahluaUtil.fail(KahluaUtil.java:100).
	Stack trace:
		se.krka.kahlua.vm.KahluaUtil.fail(KahluaUtil.java:100)
		Lua(Vanilla).waitToStart(ISSmashWindow.lua:11)
		se.krka.kahlua.vm.KahluaThread.luaMainloop(KahluaThread.java:763)
		se.krka.kahlua.vm.KahluaThread.call(KahluaThread.java:162)
		se.krka.kahlua.vm.KahluaThread.pcall(KahluaThread.java:1740)
		se.krka.kahlua.vm.KahluaThread.pcallBoolean(KahluaThread.java:1625)
		se.krka.kahlua.integration.LuaCaller.protectedCallBoolean(LuaCaller.java:83)
		zombie.characters.CharacterTimedActions.LuaTimedActionNew.waitToStart(LuaTimedActionNew.java:80)
		zombie.characters.IsoGameCharacter.updateInternal(IsoGameCharacter.java:9217)
		zombie.characters.IsoGameCharacter.update(IsoGameCharacter.java:8854)
		zombie.characters.IsoPlayer.updateInternal1(IsoPlayer.java:2214)
		zombie.characters.IsoPlayer.update(IsoPlayer.java:2192)
		zombie.MovingObjectUpdateSchedulerUpdateBucket.update(MovingObjectUpdateSchedulerUpdateBucket.java:58)
		zombie.MovingObjectUpdateScheduler.update(MovingObjectUpdateScheduler.java:150)
		zombie.iso.IsoCell.ProcessObjects(IsoCell.java:2662)
		zombie.iso.IsoCell.updateInternal(IsoCell.java:4918)
		zombie.iso.IsoCell.update(IsoCell.java:4875)
		zombie.iso.IsoWorld.updateWorld(IsoWorld.java:3350)
		zombie.iso.IsoWorld.updateInternal(IsoWorld.java:3442)
		zombie.iso.IsoWorld.update(IsoWorld.java:3375)
		zombie.gameStates.IngameState.updateInternal(IngameState.java:1550)
		zombie.gameStates.IngameState.update(IngameState.java:1370)
		zombie.gameStates.GameStateMachine.update(GameStateMachine.java:65)
		zombie.GameWindow.logic(GameWindow.java:391)
		zombie.GameWindow.frameStep(GameWindow.java:791)
		zombie.GameWindow.mainThreadStep(GameWindow.java:568)
		zombie.MainThread.mainLoop(MainThread.java:69)
		java.base/java.lang.Thread.run(Unknown Source)
```
