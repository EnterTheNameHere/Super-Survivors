"""Callbacks and quest checks handle unavailable actors without inventing state."""
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime

CLIENT = Path(__file__).resolve().parents[1] / '42/media/lua/client'


class NilSafetyChecks(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.globals().clientRoot = str(CLIENT)
        self.lua.execute("""
            package.path = clientRoot .. '/?.lua;' .. package.path
            package.preload['0_Utilities/SuperSurvivorWeaponsList'] = function() end
            print = function() end
            getSpecificPlayer = function() return nil end
            Events = setmetatable({}, {__index = function(self, name)
                local event = {Add = function() end, Remove = function() end}
                rawset(self, name, event)
                return event
            end})
        """)

    def test_startup_and_create_player_callbacks_skip_unavailable_player(self):
        self.lua.execute((CLIENT / '3_Other/SuperSurvivorsMod.lua').read_text())
        self.lua.execute("""
            -- No UI or initialization helpers are supplied: neither may run.
            SuperSurvivorsInit()
            SSCreatePlayerHandle(0)
        """)

    def test_player_dependent_quest_conditions_wait_for_player(self):
        self.lua.execute((CLIENT / '8_QuestManager/QuestManager.lua').read_text())
        self.lua.execute("""
            local manager = QuestManager:new()
            for _, kind in ipairs({'DistanceToSquare','DistanceToNPC','FindItem'}) do
                assert(manager:CheckTrigger({ConditionType=kind,Enabled=true},kind)==false)
            end
            -- Non-player conditions retain their behavior without a local actor.
            assert(manager:CheckTrigger({ConditionType='KillNPC',NPCName='Emma'},'KillNPC','Emma'))
            getSpecificPlayer = function() return {
                getX=function() return 10 end, getY=function() return 20 end,
                getInventory=function() return {getItemFromTypeRecurse=function(_,name)
                    return name=='Base.Nails' and {} or nil
                end} end}
            end
            getDistanceBetweenPoints=function(x,y,tx,ty)
                assert(x==10 and y==20 and tx==10 and ty==20);return 0
            end
            assert(manager:CheckTrigger({ConditionType='DistanceToSquare',Enabled=true,
                SquareX=10,SquareY=20,Distance=1},'DistanceToSquare'))
            assert(manager:CheckTrigger({ConditionType='FindItem',Enabled=true,ItemType='Nails'},'FindItem'))
        """)
