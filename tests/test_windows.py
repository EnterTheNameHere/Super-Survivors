"""Building-entry calls matched to the installed B42 window-action signatures."""
import os
from pathlib import Path
import unittest

from lupa.lua51 import LuaRuntime

CLIENT = Path(__file__).resolve().parents[1] / '42/media/lua/client'
GAME = os.environ.get('PZ_GAME_DIR')


class WindowChecks(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute("""
            local noop = function() end
            smashed = false
            window = {isSmashed = function() return smashed end,
                      IsOpen = function() return false end,
                      isGlassRemoved = function() return false end}
            player = {faceThisObject = function(_, target) assert(target == window); faced = target end,
                isPlayerMoving = function() return false end, isTurning = function() return false end,
                shouldBeTurning = function() return false end, isTimedActionInstant = function() return false end}
            parent = {player = player, TargetBuilding = {},
                getSeenCount = function() return 1 end, getDangerSeenCount = function() return 0 end,
                isInAction = function() return false end, inFrontOfDoor = function() return nil end,
                inFrontOfWindow = function() return window end, isInBase = function() return false end,
                hasWeapon = function() return true end, DebugSay = noop,
                StopWalk = function() stopped = true end, Wait = function(_, ticks) waited = ticks end}
            function getDistanceBetween() return 0.5 end
            queue = {}
            ISTimedActionQueue = {add = function(action) table.insert(queue, action) end}
            local function strictAction(_, ...)
                assert(select('#', ...) == 2)
                local character, target = ...
                assert(character == player and target == window)
                return {character = character, window = target}
            end
            ISSmashWindow = {new = strictAction}
            ISRemoveBrokenGlass = {new = strictAction}
        """)
        self.lua.execute((CLIENT / '7_Tasks/AttemptEntryIntoBuildingTask.lua').read_bytes())
        self.lua.execute("""
            task = setmetatable({parent = parent, TargetSquare = {}, Window = window,
                TryWindow = true, TryBreakDoor = false, ClimbThroughWindowAttempts = 0},
                AttemptEntryIntoBuildingTask)
        """)

    def test_building_entry_queues_window_without_legacy_duration_as_vehicle_part(self):
        self.lua.execute("""
            task:update()
            assert(stopped and #queue == 1 and queue[1].window == window and waited == 3)
        """)

    def test_building_entry_queues_glass_removal_with_current_signature(self):
        self.lua.execute("""
            smashed = true
            task:update()
            assert(stopped and #queue == 1 and queue[1].window == window and waited == 1)
        """)

    @unittest.skipUnless(GAME, 'Set PZ_GAME_DIR to test the installed vanilla window action')
    def test_installed_glass_action_with_installed_base_has_numeric_duration_and_completion(self):
        self.lua.execute("""
            ISBaseObject = {derive = function(self)
                local cls = {}; cls.__index = cls
                return setmetatable(cls, {__index = self})
            end}
            package.preload['ISBaseObject'] = function() end
            package.preload['TimedActions/ISBaseTimedAction'] = function() end
            MoodleType = {UNHAPPY = {}, DRUNK = {}}
            BodyPartType = {Hand_L = 0, ForeArm_R = 1,
                ToIndex = function(x) return x end, FromIndex = function(x) return x end}
            player.getMoodles = function() return {getMoodleLevel = function() return 0 end} end
            player.getBodyDamage = function() return {getBodyPart = function()
                return {getPain = function() return 0 end} end} end
            player.getTimedActionTimeModifier = function() return 1 end
            window.removeBrokenGlass = function() removed = (removed or 0) + 1 end
            window.sync = function() synced = (synced or 0) + 1 end
            server = false
            function isServer() return server end
        """)
        self.lua.execute((Path(GAME) / 'media/lua/shared/TimedActions/ISBaseTimedAction.lua').read_bytes())
        self.lua.execute((Path(GAME) / 'media/lua/shared/TimedActions/ISRemoveBrokenGlass.lua').read_bytes())
        self.lua.execute("""
            smashed = true
            task:update()
            local action = queue[1]
            assert(action.maxTime == 100 and action:adjustMaxTime(action.maxTime) == 100)
            assert(action.stopOnAim and action.stopOnWalk and action.stopOnRun)
            assert(removed == nil)
            assert(action:complete() and removed == 1 and synced == nil)
            server = true
            assert(action:complete() and removed == 2 and synced == 1)
            player.isTimedActionInstant = function() return true end
            assert(ISRemoveBrokenGlass:new(player, window).maxTime == 1)
        """)

    @unittest.skipUnless(GAME, 'Set PZ_GAME_DIR to test the installed vanilla window action')
    def test_installed_smash_window_wait_to_start_uses_window_not_a_vehicle_part(self):
        self.lua.execute("""
            ISBaseTimedAction = {derive = function(self)
                local cls = {}; cls.__index = cls
                return setmetatable(cls, {__index = self})
            end, new = function(self, character)
                return setmetatable({character = character}, {__index = self})
            end}
            package.preload['TimedActions/ISBaseTimedAction'] = function() end
        """)
        vanilla = Path(GAME) / 'media/lua/shared/TimedActions/ISSmashWindow.lua'
        self.lua.execute(vanilla.read_bytes())
        self.lua.execute("""
            task:update()
            assert(#queue == 1 and queue[1].vehiclePart == nil and queue[1].maxTime == 35)
            assert(not queue[1]:waitToStart() and faced == window)
        """)


if __name__ == '__main__':
    unittest.main()
