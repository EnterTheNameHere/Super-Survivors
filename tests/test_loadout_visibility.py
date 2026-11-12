"""Equipment lists exclude internal bandage visuals without changing equipment."""
from pathlib import Path
import unittest

from lupa.lua51 import LuaRuntime

MODULE = Path(__file__).resolve().parents[1] / '42/media/lua/client/5_UI/SuperSurvivorLoadout.lua'


class LoadoutVisibilityChecks(unittest.TestCase):
    def test_hidden_visuals_are_excluded_from_both_equipment_lists(self):
        lua = LuaRuntime(unpack_returned_tuples=True)
        lua.execute("""
            Node = {
                derive = function(self)
                    local c = {}; c.__index = c
                    return setmetatable(c, {__index = self})
                end,
                new = function(self, x, y, w, h)
                    return setmetatable({width = w, height = h}, {__index = self})
                end,
                clearChildren = function(self) self.children = {} end,
                addChild = function(self, child) table.insert(self.children, child) end,
                addScrollBars = function() end,
                setScrollWithParent = function() end,
                setScrollChildren = function() end,
                setScrollHeight = function(self, height) self.scrollHeight = height end,
            }
            ISPanel, ISButton = Node, Node
            function item(category, equipped, hidden, kind)
                return {getCategory = function() return category end,
                    isEquipped = function() return equipped end,
                    isHidden = function() return hidden end, kind = kind}
            end
            bandage = item('Clothing', true, true)
            woundVisual = item('Clothing', true, true)
            unusedVisual = item('Clothing', false, true)
            jacket = item('Clothing', true, false)
            spareJacket = item('Clothing', false, false)
            bag = item('Container', false, false, 'InventoryContainer')
            weapon = item('Weapon', false, false)
            medicalSupplies = item('Medical', false, false)
            items = {bandage, woundVisual, unusedVisual, jacket,
                spareJacket, bag, weapon, medicalSupplies}
            local inventory = {getItems = function() return {
                size = function() return #items end,
                get = function(_, i) return items[i + 1] end}
            end}
            local member = {player = {isDead = function() return false end,
                getInventory = function() return inventory end}}
            SSM = {Get = function() return {getGroupID = function() return 1 end} end}
            SSGM = {Get = function() return {getMembers = function() return {member} end} end}
            instanceof = function(value, kind) return value.kind == kind end
        """)
        equipped, available = lua.execute(MODULE.read_text() + '\nreturn PanelEquippedItems, PanelEquipableItems')
        lua.globals().equippedPanel = equipped
        lua.globals().availablePanel = available
        lua.execute("""
            equippedPanel.member_index, availablePanel.member_index = 1, 1
            equippedPanel:dupdate()
            availablePanel:dupdate()
            assert(#equippedPanel.children == 1 and equippedPanel.children[1].item == jacket)
            assert(#availablePanel.children == 3)
            assert(availablePanel.children[1].item == spareJacket)
            assert(availablePanel.children[2].item == bag)
            assert(availablePanel.children[3].item == weapon)
            assert(equippedPanel.scrollHeight == 25 and availablePanel.scrollHeight == 75)
            -- Visibility filtering must not remove the visuals or affect wounds.
            assert(#items == 8 and bandage:isEquipped() and woundVisual:isEquipped())
        """)


if __name__ == '__main__':
    unittest.main()
