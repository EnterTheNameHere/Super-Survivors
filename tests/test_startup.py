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

    def test_spawn_marks_npc_before_initializing_perks(self):
        # Exercise the real spawn path up to perk initialization. This is not
        # a mock of the complete constructor or proof that a live NPC survives.
        self.lua.execute("require '3_Other/SuperSurvivor'")
        self.lua.execute("""
            SurvivorFactory = {CreateSurvivor = function() return {} end,
                               randomName = function() end}
            function getWorld() return {getCell = function() return {} end} end
            Perks = {FromString = function(name) return name end}
            local buddy = {
                setSceneCulled = function() end,
                setBlockMovement = function() end,
                setNpc = function(_, value) npcFlag = value end,
                LevelPerk = function()
                    assert(npcFlag == true)
                    error('reached perk initialization')
                end
            }
            IsoPlayer = {new = function() return buddy end}
            local square = {isSolidFloor = function() return true end,
                            getX = function() return 10 end,
                            getY = function() return 20 end,
                            getZ = function() return 0 end}
            local ok, err = pcall(SuperSurvivor.spawnPlayer, {}, square, nil)
            assert(not ok and string.find(err, 'reached perk initialization', 1, true))
        """)

    def test_spawn_player_initializes_b42_traits_and_stats(self):
        # The game object exposes only the verified B42 trait/stat APIs.
        # Exercise the full spawnPlayer function, not the survivor wrapper/AI.
        self.lua.execute("require '3_Other/SuperSurvivor'")
        self.lua.execute("""
            CharacterTrait = {}
            local expected = {'INCONSPICUOUS', 'OUTDOORSMAN', 'LIGHT_EATER',
                'LOW_THIRST', 'FAST_HEALER', 'GRACEFUL', 'IRON_GUT', 'KEEN_HEARING'}
            for _, name in ipairs(expected) do CharacterTrait[name] = {name = name} end
            setmetatable(CharacterTrait, {__index = function(_, key)
                error('Unknown B42 trait: ' .. key)
            end})
            CharacterStat = {HUNGER = {}, THIRST = {}}
            local added, values, data = {}, {}, {}
            local traits = {add = function(_, trait)
                assert(type(trait) == 'table' and CharacterTrait[trait.name] == trait)
                added[trait.name] = true
            end}
            local stats = {set = function(_, stat, value)
                assert(stat == CharacterStat.HUNGER or stat == CharacterStat.THIRST)
                values[stat] = value
            end}
            local descriptor = {
                setForename = function(_, value) forename = value end,
                setSurname = function(_, value) surname = value end}
            local noop = function() end
            local buddy = {setSceneCulled = noop, setBlockMovement = noop,
                setNpc = function(_, value) npcFlag = value end, LevelPerk = noop,
                getCharacterTraits = function() return traits end,
                getStats = function() return stats end,
                getModData = function() return data end,
                getPerkLevel = function() return 0 end,
                isFemale = function() return false end,
                setDisplayName = function(_, value) displayName = value end,
                getDescriptor = function() return descriptor end}
            SurvivorFactory = {CreateSurvivor = function() return descriptor end,
                               randomName = noop}
            function getWorld() return {getCell = function() return {} end} end
            function ZombRand(first, last) return last and first or 5 end
            function getAPerk() return 'Strength' end
            function getRandomName() return 'Test Survivor' end
            function SuperSurvivorGetOptionValue() return 3 end
            Perks = {FromString = function(name) return name end}
            ISTimedActionQueue = {clear = noop}
            IsoPlayer = {new = function(_, desc, x, y, z)
                assert(desc == descriptor and x == 10 and y == 20 and z == -1)
                return buddy
            end}
            local square = {isSolidFloor = function() return true end,
                            getX = function() return 10 end,
                            getY = function() return 20 end,
                            getZ = function() return -1 end}
            assert(SuperSurvivor:spawnPlayer(square, nil) == buddy)
            assert(npcFlag == true)
            for _, name in ipairs(expected) do assert(added[name]) end
            assert(values[CharacterStat.HUNGER] == 0.05)
            assert(values[CharacterStat.THIRST] == 0.05)
            assert(data.Name == 'Test Survivor' and data.AIMode == 'Random Solo')
            assert(forename == data.Name and displayName == data.Name and surname == '')
        """)

    def test_name_changes_update_descriptor_display_and_saved_name(self):
        self.lua.execute("require '3_Other/SuperSurvivor'")
        self.lua.execute("""
            local data = {}
            local desc = {setForename = function(_, name) forename = name end,
                          setSurname = function(_, name) surname = name end}
            local ss = setmetatable({player = {
                getDescriptor = function() return desc end,
                setDisplayName = function(_, name) displayName = name end,
                getModData = function() return data end},
                userName = {ReadString = function(_, text) label = text end}}, SuperSurvivor)
            ss:setName('New Name')
            assert(ss:getName() == 'New Name' and data.NameRaw == 'New Name')
            assert(forename == 'New Name' and surname == '')
            assert(displayName == 'New Name' and label == 'New Name')
        """)

    def test_needs_thresholds_use_b42_stat_values(self):
        self.lua.execute("require '3_Other/SuperSurvivor'")
        self.lua.execute("""
            CharacterStat = {HUNGER = {}, THIRST = {}}
            local values = {[CharacterStat.HUNGER] = 0.4, [CharacterStat.THIRST] = 0.76}
            local ss = setmetatable({player = {getStats = function()
                return {get = function(_, stat) assert(values[stat]); return values[stat] end}
            end}}, SuperSurvivor)
            assert(ss:isHungry() and not ss:isVHungry() and not ss:isStarving())
            assert(ss:isThirsty() and ss:isVThirsty() and ss:isDyingOfThirst())
            values[CharacterStat.HUNGER], values[CharacterStat.THIRST] = 0.76, 0.15
            assert(ss:isVHungry() and ss:isStarving())
            assert(not ss:isThirsty() and not ss:isVThirsty() and not ss:isDyingOfThirst())
        """)

    def test_running_updates_game_state_without_legacy_npc_methods(self):
        self.lua.execute("require '3_Other/SuperSurvivor'")
        self.lua.execute("""
            local running, moved = false, false
            local ss = setmetatable({player = {
                isRunning = function() return running end,
                setRunning = function(_, value) running = value end,
                setJustMoved = function(_, value) moved = value end}}, SuperSurvivor)
            ss:setRunning(true)
            assert(running and moved)
            ss:setRunning(false)
            assert(not running and not moved)
        """)

    def test_moodle_startup_and_speech_use_b42_constants(self):
        self.lua.execute("""
            require '0_Utilities/SuperSurvivorTextUtilities'
            require '1_Dialogue/SuperSurvivorDialogue'
            MoodleType = {}
            local names = {'ENDURANCE', 'TIRED', 'HUNGRY', 'PANIC', 'SICK',
                'BORED', 'UNHAPPY', 'BLEEDING', 'WET', 'HAS_A_COLD', 'ANGRY',
                'STRESS', 'THIRST', 'INJURED', 'PAIN', 'HEAVY_LOAD', 'DRUNK',
                'ZOMBIE', 'HYPERTHERMIA', 'HYPOTHERMIA', 'FOOD_EATEN'}
            for _, name in ipairs(names) do MoodleType[name] = {name = name} end
            setmetatable(MoodleType, {__index = function(_, key)
                error('Unknown B42 moodle: ' .. key)
            end})
            local moodles = {Update = function() end,
                getMoodleLevel = function(_, moodle)
                    assert(moodle ~= nil)
                    return 2
                end}
            function getPlayer() return {getMoodles = function() return moodles end} end
            Events = {OnLoad = {Add = function(fn) onLoad = fn end},
                OnPlayerUpdate = {Add = function(fn) onUpdate = fn end}}
        """)
        self.load("3_Other/SuperSurvivorSpeakConditions.lua")
        self.lua.execute("""
            onLoad()
            assert(#LMSConditions.MoodleTable == 21)
            for _, level in ipairs(LMSConditions.MoodleTable) do assert(level == 2) end
            local checks = 0
            LMSConditions.doMoodleCheck = function(_, _, moodle)
                assert(moodle and MoodleType[moodle.name] == moodle)
                checks = checks + 1
            end
            onUpdate({isLocalPlayer = function() return false end})
            assert(checks == 33)
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
