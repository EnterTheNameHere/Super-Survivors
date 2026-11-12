"""Outfit/constructor checks with typed B42 body-location stubs."""
from pathlib import Path
import unittest

from lupa.lua51 import LuaRuntime

CLIENT = Path(__file__).resolve().parents[1] / '42/media/lua/client'


class OutfitChecks(unittest.TestCase):
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
            function instanceof(item, kind)
                return type(item) == 'table' and
                       (kind == item.kind or (kind == 'InventoryItem' and item.inventory))
            end
            require '3_Other/SuperSurvivor'
            local noop = function() end
            ItemBodyLocation = {JACKET = {}, SHIRT = {}, FANNY_PACK_FRONT = {}}
            local validLocations = {}
            for _, location in pairs(ItemBodyLocation) do validLocations[location] = true end
            worn, owned, data, events = {}, {}, {}, 0
            descriptor = {setForename = function(_, value) forename = value end,
                getForename = function() return forename end, setSurname = noop}
            local inv = {clear = function() owned = {} end,
                AddItem = function(_, item) table.insert(owned, item); return item end}
            local traits = {add = function(_, trait) assert(type(trait) == 'table') end}
            CharacterTrait = {}
            for _, name in ipairs({'INCONSPICUOUS', 'OUTDOORSMAN', 'LIGHT_EATER', 'LOW_THIRST',
                'FAST_HEALER', 'GRACEFUL', 'IRON_GUT', 'KEEN_HEARING'}) do
                CharacterTrait[name] = {}
            end
            CharacterStat = {HUNGER = {}, THIRST = {}}
            local stats = {set = noop}
            player = {clearWornItems = function() worn = {} end,
                getInventory = function() return inv end,
                setWornItem = function(_, location, item)
                    assert(validLocations[location], 'Expected typed ItemBodyLocation')
                    worn[location] = item
                end,
                getWornItem = function(_, location)
                    assert(validLocations[location], 'Expected typed ItemBodyLocation')
                    return worn[location]
                end,
                initSpritePartsEmpty = noop, setSceneCulled = noop, setBlockMovement = noop,
                setNpc = noop, LevelPerk = noop, getCharacterTraits = function() return traits end,
                getStats = function() return stats end, getModData = function() return data end,
                getPerkLevel = function() return 0 end, isFemale = function() return false end,
                setDisplayName = noop, getDescriptor = function() return descriptor end}
            function triggerEvent(name, character)
                assert(name == 'OnClothingUpdated' and character == player)
                events = events + 1
            end
            function item(kind, location)
                return {kind = kind, inventory = true,
                    canBeEquipped = function() return kind == 'InventoryContainer' and location or nil end,
                    getCategory = function() return kind end,
                    getBodyLocation = function() return location end}
            end
            shirt = item('Clothing', ItemBodyLocation.SHIRT)
            bag = item('InventoryContainer', ItemBodyLocation.FANNY_PACK_FRONT)
            local catalog = {['Base.TestShirt'] = shirt, ['Base.TestBag'] = bag}
            function instanceItem(name) return catalog[name] end
            SurvivorRandomSuits = {VeryRare = {TypedTest = {'Base.TestShirt', 'Base.TestBag'}},
                                  Preset = {Preset_Test = {'Base.TestShirt', 'Base.TestBag'}}}
            function getGameTime() return {getWorldAgeHours = function() return 0 end} end
            ss = setmetatable({player = player}, SuperSurvivor)
        """)

    def test_preset_uses_typed_locations_and_preserves_bag_attachment(self):
        self.lua.execute("""
            worn[ItemBodyLocation.JACKET] = {}
            ss:SuitUp('Preset_Test')
            assert(worn[ItemBodyLocation.JACKET] == nil)
            assert(worn[ItemBodyLocation.SHIRT] == shirt)
            assert(worn[ItemBodyLocation.FANNY_PACK_FRONT] == bag)
            assert(#owned == 2 and events == 2)
            -- No local-player inventory UI or forced-back attachment APIs exist.
        """)

    def test_full_new_survivor_reaches_outfit_completion(self):
        self.lua.execute("""
            local noop = function() end
            SurvivorFactory = {CreateSurvivor = function() return descriptor end, randomName = noop}
            IsoPlayer = {new = function() return player end}
            function getWorld() return {getCell = function() return {} end} end
            Perks = {FromString = function(name) return name end}
            function getAPerk() return 'Strength' end
            function getRandomName() return 'Outfit Test' end
            function SuperSurvivorGetOptionValue() return 3 end
            ISTimedActionQueue = {clear = noop}
            TextDrawObject = {new = function() return {setAllowAnyImage = noop,
                setDefaultFont = noop, setDefaultColors = noop, ReadString = noop} end}
            UIFont = {Small = {}, Large = {}}
            TaskManager = {new = function(_, owner) return {parent = owner} end}
            LootTypes, SuperSurvivorBravery = {'Food', 'Water'}, 25
            local square = {isSolidFloor = function() return true end,
                getX = function() return 10 end, getY = function() return 20 end,
                getZ = function() return 0 end}
            local survivor = SuperSurvivor:new(nil, square)
            assert(survivor.player == player and survivor.MyTaskManager.parent == survivor)
            assert(worn[ItemBodyLocation.SHIRT] == shirt)
            assert(worn[ItemBodyLocation.FANNY_PACK_FRONT] == bag)
            assert(data.Name == 'Outfit Test' and data.BravePoints == 25)
            assert(events == 2)
        """)

    def test_missing_or_unlocated_items_never_pass_strings_or_nil_as_locations(self):
        self.lua.execute("""
            assert(ss:WearThis('Base.Missing') == false)
            ss:WearThis(item('Clothing', nil))
            assert(next(worn) == nil)
        """)


if __name__ == '__main__':
    unittest.main()
