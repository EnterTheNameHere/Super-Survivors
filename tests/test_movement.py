"""Movement calculations with typed worn slots and item/container separation."""
from pathlib import Path
import unittest

from lupa.lua51 import LuaRuntime

CLIENT = Path(__file__).resolve().parents[1] / '42/media/lua/client'


class MovementChecks(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.globals().clientRoot = str(CLIENT)
        self.lua.execute("""
            package.path = clientRoot .. '/?.lua;' .. package.path
            print = function() end
            function getActivatedMods() return {size = function() return 0 end} end
            function getText(key) return key end
            function ZombRand(first, last) return last and first or 0 end
            ImmutableColor = {new = function() return {} end}
            function instanceof(obj, kind) return obj and obj.kind == kind end
            require '3_Other/SuperSurvivor'
            ItemBodyLocation = {SHOES = {}}
            condition, shoesPresent, running = 10, true, false
            local shoe = {getCondition = function() return condition end,
                getCategory = function() return 'Clothing' end,
                getRunSpeedModifier = function() return 1 end}
            local worn = {size = function() return shoesPresent and 1 or 0 end,
                getItemByIndex = function() return shoe end,
                getItem = function(_, slot)
                    assert(slot == ItemBodyLocation.SHOES, 'Expected typed shoe location')
                    return shoesPresent and shoe or nil
                end}
            capacity, contentsWeight = 20, 10
            bag = {kind = 'InventoryContainer',
                getScriptItem = function() return {runSpeedModifier = 0.9} end,
                getContentsWeight = function() return contentsWeight end,
                getEffectiveCapacity = function() return capacity end}
            local variables = {}
            player = {getWornItems = function() return worn end,
                getClothingItem_Back = function() return backpack end,
                getPrimaryHandItem = function() return primary end,
                getSecondaryHandItem = function() return secondary end,
                calculateBaseSpeed = function() return 0.8 end,
                getPerkLevel = function() return 0 end,
                getSlowFactor = function() return 0 end,
                getBodyDamage = function() return nil end,
                isAiming = function() return false end,
                isInTreesNoBush = function() return false end,
                setVariable = function(_, name, value) variables[name] = value end}
            Perks = {FromString = function(name) return name end}
            AbsoluteValue = math.abs
            ss = setmetatable({player = player,
                getRunning = function() return running end,
                NPCgetFootInjurySpeedModifier = function() return 0 end}, SuperSurvivor)
            function walkSpeed() ss:NPCcalculateWalkSpeed(); return variables.WalkSpeed end
        """)

    def test_walking_uses_typed_shoe_slot_and_preserves_barefoot_penalty(self):
        self.lua.execute("""
            assert(math.abs(walkSpeed() - 0.64) < 0.00001)
            shoesPresent = false
            assert(math.abs(walkSpeed() - 0.544) < 0.00001)
            shoesPresent, condition = true, 0
            assert(math.abs(walkSpeed() - 0.544) < 0.00001)
        """)

    def test_running_without_bags_keeps_a_nonzero_baseline(self):
        self.lua.execute("""
            running = true
            assert(ss:NPCgetfullSpeedMod() == 1)
            assert(math.abs(walkSpeed() - 0.52) < 0.00001)
        """)

    def test_temperature_and_tree_slowdowns_use_local_objects(self):
        self.lua.execute("""
            -- Unrelated globals must never supply the movement modifiers.
            thermo = {getMovementModifier = function() error('global thermo') end}
            tree = {getSlowFactor = function() error('global tree') end}
            player.getBodyDamage = function() return {
                getThermoregulator = function() return {
                    getMovementModifier = function() return 0.5 end}
                end}
            end
            player.isInTreesNoBush = function() return true end
            player.getCurrentSquare = function() return {
                HasTree = function() return true end,
                getTree = function() return {
                    getSlowFactor = function(_, character)
                        assert(character == player)
                        return 0.25
                    end}
                end}
            end
            assert(math.abs(walkSpeed() - 0.08) < 0.00001)
        """)

    def test_pursuit_uses_target_kind_and_exempts_companions_from_fear(self):
        self.lua.execute("""
            role = 'Guard'
            ss.getGroupRole = function() return role end
            ss.getSeenCount = function() return 5 end
            ss.isEnemyInRange = function(_, enemy)
                assert(enemy == ss.LastEnemeySeen)
                return true
            end
            ss.isTooScaredToFight = function() return false end
            ss.zDebugSayPTSC = function() end
            ss.getTaskManager = function() return {getCurrentTask = function() return '' end} end
            ss.getDangerSeenCount = function() return 5 end
            ss.RealCanSee = function() return true end
            ss.NPC_TargetIsOutside = function() return true end
            ss.NPC_IsOutside = function() return true end
            getDistanceBetween = function() return 1 end
            getSpecificPlayer = function() return player end
            assert(ss:NPC_CheckPursueScore() == 0) -- No target.
            Enemy_Is_a_Zombie = true -- Must not influence human-target handling.
            ss.LastEnemeySeen = {kind = 'IsoPlayer'}
            assert(ss:NPC_CheckPursueScore() == 6)
            ss.LastEnemeySeen = {kind = 'IsoZombie'}
            assert(ss:NPC_CheckPursueScore() == 0)
            role = 'Companion'
            assert(ss:NPC_CheckPursueScore() == 5)
            ss.player = nil
            assert(ss:NPC_CheckPursueScore() == 0)
        """)

    def test_back_and_hand_bags_use_items_and_preserve_load_penalty(self):
        self.lua.execute("""
            -- The bag exposes no getItemContainer; its contents container is not
            -- the item that provides the script definition/run-speed modifier.
            for _, slot in ipairs({'back', 'primary', 'secondary'}) do
                backpack, primary, secondary = nil, nil, nil
                if slot == 'back' then backpack = bag
                elseif slot == 'primary' then primary = bag else secondary = bag end
                assert(math.abs(ss:NPCgetfullSpeedMod() - 0.875) < 0.00001)
            end
            running = true
            assert(walkSpeed() > 0)
        """)

    def test_empty_zero_capacity_bag_does_not_divide_by_zero(self):
        self.lua.execute("""
            capacity, contentsWeight, backpack = 0, 0, bag
            assert(math.abs(ss:NPCgetfullSpeedMod() - 0.9) < 0.00001)
        """)

    def test_locked_door_path_does_not_call_removed_opposite_square_api(self):
        self.lua.execute("""
            local square = {getRoom = function() return nil end}
            local adjacent = {getX = function() return 10 end,
                getY = function() return 20 end, getZ = function() return 0 end}
            AdjacentFreeTileFinder = {Find = function() return adjacent end}
            local door = {isLocked = function() return true end,
                isDestroyed = function() return false end}
            ss.inFrontOfDoor = function() return door end
            ss.DebugSay = function() end
            local managed, walked = false, false
            ss.NPC_ManageLockedDoors = function() managed = true end
            ss.WalkToAttempt = function(_, sq) assert(sq == square) end
            ss.WalkToPoint = function(_, x, y, z)
                assert(x == 10 and y == 20 and z == 0)
                walked = true
            end
            ss.StuckDoorTicks = 0
            ss:walkTo(square)
            assert(managed and walked)
        """)


if __name__ == '__main__':
    unittest.main()
