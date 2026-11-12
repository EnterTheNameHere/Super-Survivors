"""Vision scans must use B42's one-based Lua snapshot, not an indexed Set."""
from pathlib import Path
import unittest

from lupa.lua51 import LuaRuntime

CLIENT = Path(__file__).resolve().parents[1] / '42/media/lua/client'


class VisionChecks(unittest.TestCase):
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
            function character(kind, distance, enemy, visible, dead)
                return {kind = kind, distance = distance, enemy = enemy, visible = visible,
                    isDead = function() return dead or false end,
                    getZ = function() return 0 end,
                    setAlpha = function(self, value) self.alpha = value end,
                    setTargetAlpha = function(self, value) self.targetAlpha = value end}
            end
            player = character('IsoPlayer', 0, true, true)
            local data = {GroupRole = 'Companion'}
            player.getModData = function() return data end
            -- The old getObjectList/size/get APIs deliberately do not exist.
            player.getCell = function() return {getLuaObjectList = function() return objects end} end
            animal = character('IsoAnimal', 0.1, true, true)
            dead = character('IsoPlayer', 0.2, true, true, true)
            friend = character('IsoPlayer', 0.3, false, true)
            near = character('IsoZombie', 0.6, true, true)
            human = character('IsoPlayer', 2, true, false)
            far = character('IsoZombie', 7, true, true)
            objects = {player, animal, dead, friend, near, human, far}
            function getDistanceBetween(candidate) return candidate.distance end
            ss = setmetatable({player = player, AttackRange = 0.5, GroupRole = 'Companion',
                seenCount = 0, dangerSeenCount = 0, EnemiesOnMe = 0,
                isEnemy = function(_, candidate) return candidate.enemy end,
                RealCanSee = function(_, candidate) return candidate.visible end,
                getCurrentTask = function() return 'Attack' end,
                usingGun = function() return false end,
                DebugSay = function() end}, SuperSurvivor)
        """)

    def test_vision_selects_nearest_enemy_and_preserves_danger_counts(self):
        self.lua.execute("""
            assert(ss:DoVision() == near and ss.LastEnemeySeen == near)
            assert(ss.seenCount == 2 and ss.dangerSeenCount == 2 and ss.EnemiesOnMe == 1)
            assert(ss.UpdateDelayTicks == 10 and player:getModData().seenZombie)
        """)

    def test_empty_snapshot_clears_stale_vision_state(self):
        self.lua.execute("""
            ss:DoVision()
            objects = {}
            assert(ss:DoVision() == nil and ss.LastEnemeySeen == nil)
            assert(ss.seenCount == 0 and ss.dangerSeenCount == 0 and ss.EnemiesOnMe == 0)
            assert(ss.UpdateDelayTicks == 20)
        """)

    def test_human_scan_keeps_its_human_only_detection(self):
        self.lua.execute("""
            assert(ss:DoHumanEntityScan() == human)
            assert(ss.LastEnemeySeen == human and ss.seenCount == 1)
        """)

    def test_companion_scan_finds_unseen_enemy_and_counts_close_threats(self):
        self.lua.execute("""
            assert(ss:Companion_DoSixthSenseScan() == human)
            assert(ss.LastEnemeySeen == human and ss.seenCount == 1)
            assert(ss.dangerSeenCount == 2 and ss.EnemiesOnMe == 1)
        """)

    def test_debug_player_scan_uses_snapshot_and_excludes_self_and_animals(self):
        self.lua.execute("""
            Events = setmetatable({}, {__index = function(t, key)
                local event = {Add = function() end}; rawset(t, key, event); return event
            end})
            DebugOptions = true
            player.isLocalPlayer = function() return true end
            spotted = {}
            player.spotted = function(_, candidate) spotted[candidate] = true end
        """)
        self.lua.execute((CLIENT / '3_Other/SuperSurvivorUpdate.lua').read_bytes())
        self.lua.execute("""
            SuperSurvivorGlobalUpdate(player)
            assert(spotted[near] and spotted[human] and spotted[friend])
            assert(not spotted[player] and not spotted[animal])
            assert(near.alpha == 1 and near.targetAlpha == 1)
        """)


if __name__ == '__main__':
    unittest.main()
