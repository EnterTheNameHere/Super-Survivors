"""Behavioral regressions for task and UI names previously read as globals."""
from pathlib import Path
import unittest

from lupa.lua51 import LuaRuntime

CLIENT = Path(__file__).resolve().parents[1] / '42/media/lua/client'


class NameFixChecks(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.globals().clientRoot = str(CLIENT)
        self.lua.execute("""
            package.path = clientRoot .. '/?.lua;' .. package.path
            print = function() end
        """)

    def test_dialogue_resolves_existing_table_and_waits_for_parent_speech(self):
        self.lua.execute("""
            getDialogue = function(key) return key end
            require '7_Tasks/SpeakDialogueTask'
            local spoken = {}
            busy = true
            local target = {}
            local parent = {
                player = {faceThisObject = function(_, other) assert(other == target) end},
                isInAction = function() return false end,
                isSpeaking = function() return busy end,
                DebugSay = function() end, StopWalk = function() end,
                Speak = function(_, line) table.insert(spoken, line) end,
            }
            getDistanceBetween = function() return 1 end
            local task = SpeakDialogueTask:new(parent, target, 'WifeSpeech')
            assert(task.Dialogue == SuperDialogue.WifeSpeech)
            task:update()
            assert(#spoken == 0)
            busy = false
            for i = 1, #task.Dialogue do
                task:update()
                assert(spoken[i] == task.Dialogue[i])
            end
            assert(task:isComplete())
            assert(SpeakDialogueTask:new(parent, target, 'MissingDialogue') == nil)
        """)

    def test_surrender_uses_parent_and_enemy_character(self):
        self.lua.execute("""
            require '7_Tasks/SurenderTask'
            ASuperSurvivor = {RealCanSee = function() error('unrelated global') end}
            local character = {
                getDotWithForwardDirection = function() return 1 end,
                isAiming = function() return true end,
                CanSee = function() return true end,
            }
            local parentCharacter = {getX = function() return 1 end, getY = function() return 1 end}
            local parent = {player = parentCharacter,
                RealCanSee = function(_, other) assert(other == character); return false end,
                isEnemy = function(_, other) assert(other == character); return true end,
            }
            distance = 1
            getDistanceBetween = function(a, b)
                assert((a == character and b == parentCharacter) or
                       (a == parentCharacter and b == character))
                return distance
            end
            local task = setmetatable({TaskTicks = 4, NowSafeTicks = 0, parent = parent,
                enemy = {player = character, usingGun = function() return false end}}, SurenderTask)
            assert(task:isComplete() == false)
            distance = 8
            assert(task:isComplete() == true)
        """)

    def test_unloaded_member_without_coordinates_attempts_reload(self):
        self.lua.execute("""
            require '5_UI/UIUtils'
            coord = 999 -- An unrelated global must not suppress the reload.
            local member = {
                getName = function() return 'Emma' end,
                getID = function() return 12 end,
                isInCell = function() return false end,
                isDead = function() return false end,
                saveFileExists = function() return true end,
            }
            local group = {
                isMember = function() return true end,
                hasLeader = function() return true end,
                getMembers = function() return {member} end,
            }
            local square = {}
            reloads = 0
            SSM = {
                Get = function() return {getGroupID = function() return 3 end} end,
                LoadSurvivor = function(_, id, sq)
                    assert(id == 12 and sq == square)
                    reloads = reloads + 1
                end,
            }
            SSGM = {Get = function(_, id) assert(id == 3); return group end}
            getSpecificPlayer = function() return {getCurrentSquare = function() return square end} end
            getCoordsFromID = function(id) assert(id == 12); return 0 end
            local name, role = get_member_info(1)
            assert(name == 'Emma' and role == '0' and reloads == 1)
            getCoordsFromID = function() return '10,20' end
            name, role = get_member_info(1)
            assert(role == '10,20' and reloads == 1)
        """)


if __name__ == '__main__':
    unittest.main()
