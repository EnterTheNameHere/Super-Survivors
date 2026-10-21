"""Isolated Lua checks; these do not emulate Project Zomboid's Java API.

Run with a Python environment containing lupa==2.6:
    python -m unittest discover -s tests -v
"""
from pathlib import Path
import unittest

from lupa.lua51 import LuaRuntime


CLIENT = Path(__file__).resolve().parents[1] / "42/media/lua/client"


class StartupChecks(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.globals().clientRoot = str(CLIENT)
        self.lua.execute("""
            package.path = clientRoot .. '/?.lua;' .. package.path
            function getActivatedMods()
                return {size = function() return 0 end}
            end
            function getText(key) return key end
            function ZombRand(first, last) return last and first or 0 end
            ImmutableColor = {new = function(r, g, b) return {r, g, b} end}
        """)

    def load(self, name):
        self.lua.execute((CLIENT / name).read_bytes())

    def test_survivor_dependency_chain(self):
        self.lua.execute("require '3_Other/SuperSurvivor'")
        self.lua.execute("""
            assert(type(SuperSurvivor.new) == 'function')
            assert(type(SuperSurvivorPresetSpawnThis) == 'function')
            assert(#PresetSpawns > 0)
            assert(SSGM:Get(0) == HillTopGroup)
            assert(SSGM:Get(5) == Gang2Group)
        """)

    def test_context_menu_registers_without_external_save_module(self):
        self.lua.execute("""
            ISBaseTimedAction = {derive = function() return {} end}
            package.preload['TimedActions/ISBaseTimedAction'] = function() end
            Events = {OnFillWorldObjectContextMenu = {Add = function(callback)
                registeredMenu = callback
            end}}
        """)
        self.load("5_UI/SuperSurvivorsContextMenu.lua")
        self.lua.execute("assert(registeredMenu == SurvivorsFillWorldObjectContextMenu)")

    def prepare_debug(self):
        self.lua.execute("""
            debugEnabled, multiplayer, server = true, false, false
            function getDebug() return debugEnabled end
            function isClient() return multiplayer end
            function isServer() return server end
            player = {
                getCurrentSquare = function() return {} end,
                getX = function() return 10.5 end,
                getY = function() return 20.5 end,
                getZ = function() return -1 end
            }
            function getSpecificPlayer() return player end
            square = {getFloor = function() return {} end,
                      isFree = function() return true end}
            function getCell() return {getGridSquare = function(_, x, y, z)
                coordinates = {x, y, z}
                return square
            end} end
            spawnCount = 0
            survivor = {getID = function() return 4 end}
            SSM = {SuperSurvivors = {[0] = {}}, spawnSurvivor = function(_, _, target)
                assert(target == square)
                spawnCount = spawnCount + 1
                return survivor
            end}
            SurvivorMap = {}
        """)
        self.load("Debug/SuperbSurvivorsDebug.lua")
        self.lua.execute("assert(spawnCount == 0)")

    def test_spawn_requires_debug_and_single_player(self):
        self.prepare_debug()
        self.lua.execute("""
            debugEnabled = false
            assert(SuperbSurvivorsDebug.spawn() == nil)
            debugEnabled, multiplayer = true, true
            assert(SuperbSurvivorsDebug.spawn() == nil)
            multiplayer, server = false, true
            assert(SuperbSurvivorsDebug.spawn() == nil)
            assert(spawnCount == 0)
        """)

    def test_spawn_requires_initialized_world(self):
        self.prepare_debug()
        self.lua.execute("""
            player = nil
            assert(SuperbSurvivorsDebug.spawn() == nil)
            player = {getCurrentSquare = function() return {} end}
            SurvivorMap = nil
            assert(SuperbSurvivorsDebug.spawn() == nil)
            assert(spawnCount == 0)
        """)

    def test_spawn_rejects_partial_coordinates_and_blocked_tiles(self):
        self.prepare_debug()
        self.lua.execute("""
            assert(SuperbSurvivorsDebug.spawn(1) == nil)
            square.isFree = function() return false end
            assert(SuperbSurvivorsDebug.spawn(1, 2, 0) == nil)
            square = nil
            assert(SuperbSurvivorsDebug.spawn(1, 2, 0) == nil)
            assert(spawnCount == 0)
        """)

    def test_spawn_delegates_once_and_preserves_basement_floor(self):
        self.prepare_debug()
        self.lua.execute("""
            assert(SuperbSurvivorsDebug.spawn() == survivor)
            assert(spawnCount == 1)
            assert(coordinates[1] == 12 and coordinates[2] == 20)
            assert(coordinates[3] == -1)
        """)

    def test_spawn_does_not_swallow_api_errors(self):
        self.prepare_debug()
        self.lua.execute("""
            SSM.spawnSurvivor = function() error('constructor API mismatch') end
            local ok, err = pcall(SuperbSurvivorsDebug.spawn)
            assert(not ok and string.find(err, 'constructor API mismatch', 1, true))
        """)


if __name__ == "__main__":
    unittest.main()
