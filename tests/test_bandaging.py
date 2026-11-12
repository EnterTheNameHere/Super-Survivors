"""Check the installed bandage action used by NPC treatment call sites.

Set PZ_GAME_DIR to the target game installation. The mod no longer bundles this
vanilla action; these mocked checks do not establish native NPC compatibility.
"""
import os
from pathlib import Path
import unittest

from lupa.lua51 import LuaRuntime


GAME = os.environ.get('PZ_GAME_DIR')


@unittest.skipUnless(GAME, 'Set PZ_GAME_DIR to test the installed vanilla bandage action')
class BandageChecks(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute("""
            ISBaseTimedAction = {derive = function(self)
                local cls = {}; cls.__index = cls
                return setmetatable(cls, {__index = self})
            end, new = function(self, character)
                return setmetatable({character = character}, {__index = self})
            end, perform = function() performed = true end}
            package.preload['TimedActions/ISBaseTimedAction'] = function() end
            CharacterTrait = {HEMOPHOBIC = {}}
            CharacterStat = {PANIC = {}}
            Perks = {Doctor = {}}
            BodyPartType = {Groin = 0, ToIndex = function(x) return x end}
            function isClient() return false end
            function isServer() return false end
            function ZombRandFloat(a,b) return a end
            function syncPlayerStats() statsSynced = true end
            function syncBodyPart() bodySynced = true end
            function addXp(_, perk, amount) assert(perk == Perks.Doctor); xp = amount end
            item = {getBandagePower = function() return 2 end,
                getType = function() return 'Bandage' end, getModule = function() return 'Base' end,
                isAlcoholic = function() return false end, isInfected = function() return false end,
                setJobDelta = function() end}
            body = {getIndex = function() return 1 end, bandaged = function() return false end,
                manipulatingUsername = function() return nil end,
                getBleedingTime = function() return 5 end, isGetBandageXp = function() return true end,
                setManipulatingUsername = function() end}
            local inventory = {Remove = function(_, target) assert(target == item); removed = true end}
            local stats = {add = function(_, key, amount)
                assert(key == CharacterStat.PANIC and amount == 50); panic = amount end}
            local damage = {SetBandaged = function(_, index, applied, life, alcohol, name)
                assert(index == 1 and applied and life > 0 and name == 'Base.Bandage')
                bandaged = true end}
            doctor = {getPerkLevel = function() return 3 end,
                getX = function() return 0 end, getY = function() return 0 end,
                isTimedActionInstant = function() return false end,
                hasTrait = function(_, key) assert(key == CharacterTrait.HEMOPHOBIC); return true end,
                getStats = function() return stats end, getInventory = function() return inventory end,
                getBodyDamage = function() return damage end}
            ISHealthPanel = {setBodyPartActionForPlayer = function() end}
        """)
        path = Path(GAME) / 'media/lua/shared/TimedActions/ISApplyBandage.lua'
        self.lua.execute(path.read_bytes())

    def test_perform_only_finishes_ui_and_completion_applies_bandage_with_typed_apis(self):
        self.lua.execute("""
            local action = ISApplyBandage:new(doctor, doctor, item, body, true)
            assert(action.maxTime == 108)
            action:perform()
            assert(performed and not bandaged and not removed and panic == nil)
            assert(action:complete())
            assert(bandaged and removed and panic == 50 and xp == 5 and statsSynced and bodySynced)
        """)

    def test_instant_action_duration_and_doctor_level(self):
        self.lua.execute("""
            doctor.isTimedActionInstant = function() return true end
            local action = ISApplyBandage:new(doctor, doctor, item, body, true)
            assert(action.maxTime == 1 and action.doctorLevel == 10)
        """)

    def test_first_aid_waits_for_vanilla_completion_without_forced_bandage(self):
        path = Path(__file__).resolve().parents[1] / '42/media/lua/client/7_Tasks/FirstAideTask.lua'
        self.lua.execute(path.read_bytes())
        self.lua.execute("""
            body.HasInjury=function() return true end
            body.bandaged=function() return bandaged==true end
            local parts={size=function() return 1 end,get=function(_,i) assert(i==0);return body end}
            local damage=doctor:getBodyDamage();damage.getBodyParts=function() return parts end
            local inventory=doctor:getInventory()
            inventory.getItemFromType=function() return item end
            inventory.AddItem=function() error('supplies already provided') end
            local queued=false
            ISTimedActionQueue={add=function(action) pending=action;queued=true end,clear=function() queued=false end}
            package.preload['TimedActions/ISApplyBandage']=function() end
            local parent={Get=function() return doctor end,HasInjury=function() return not bandaged end,
                StopWalk=function() end,isInAction=function() return queued end}
            local task=FirstAideTask:new(parent)
            task:update()
            for i=1,40 do task:update() end
            assert(pending and not bandaged and not removed)
            pending:perform();pending:complete();queued=false
            assert(task:isComplete() and bandaged and removed)
        """)


if __name__ == '__main__':
    unittest.main()
