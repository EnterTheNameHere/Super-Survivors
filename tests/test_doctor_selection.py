"""Nearest-patient selection must update the running best distance."""
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime


class DoctorSelectionChecks(unittest.TestCase):
    def test_doctor_walks_to_a_patient_who_is_not_adjacent(self):
        lua = LuaRuntime(unpack_returned_tuples=True)
        source = Path(__file__).resolve().parents[1] / '42/media/lua/client/7_Tasks/DoctorTask.lua'
        lua.execute(source.read_bytes())
        lua.execute('''
            local destination={}
            function getDistanceBetween() return 5 end
            function getActionText(key) return key end
            local parent={Get=function() return {} end,isInAction=function() return false end,
                Speak=function() end,walkTo=function(_,square) walked=square end}
            local patient={isDead=function() return false end,getCurrentSquare=function() return destination end}
            local task=setmetatable({parent=parent,Patient=patient},DoctorTask)
            task:update();assert(walked==destination)
        ''')

    def test_nearer_patient_is_not_replaced_by_later_farther_match(self):
        lua = LuaRuntime(unpack_returned_tuples=True)
        source = Path(__file__).resolve().parents[1] / '42/media/lua/client/7_Tasks/DoctorTask.lua'
        lua.execute(source.read_bytes())
        lua.execute('''
            local function patient()
                return {isDead=function() return false end,getModData=function() return {} end}
            end
            local near,far=patient(),patient()
            local function square(distance,person)
                return {distance=distance,getMovingObjects=function() return {
                    size=function() return 1 end,get=function() return person end} end}
            end
            local squares={[-1]=square(1,near),[2]=square(2,far)}
            function getCell() return {getGridSquare=function(_,x,y) if y==0 then return squares[x] end end} end
            function getDistanceBetween(sq) return sq.distance end
            function instanceof() return true end
            function RequiresTreatment() return true end
            local player={getX=function() return 0 end,getY=function() return 0 end,getZ=function() return 0 end,
                CanSee=function() return true end}
            local task=setmetatable({parent={player=player}},DoctorTask)
            assert(task:FindPatient()==near)
        ''')
