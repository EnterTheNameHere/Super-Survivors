"""B42 rejects UI roots that also have a parent; child buttons stay children."""
from pathlib import Path
import unittest

from lupa.lua51 import LuaRuntime

UI = Path(__file__).resolve().parents[1] / '42/media/lua/client/5_UI'


class UiParentingChecks(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute("""
            local noop = function() end
            Node = {}
            Node.__index = Node
            function Node:derive()
                local cls = {}; cls.__index = cls
                return setmetatable(cls, {__index = self})
            end
            function Node:new() return setmetatable({children = {}}, {__index = self}) end
            function Node:addToUIManager()
                assert(not self.parent, 'UI root cannot have parent'); self.root = true
            end
            function Node:addChild(child)
                assert(not child.root, 'child cannot also be a UI root')
                child.parent = self; table.insert(self.children, child)
            end
            for _, method in ipairs({'initialise', 'setEnable', 'setVisible', 'ignoreHeightChange',
                'setOutfitName', 'setState', 'setDirection', 'setIsometric', 'createChildren'}) do
                Node[method] = noop
            end
            ISCollapsableWindow, ISRichTextPanel, ISButton, ISCharacterScreenAvatar = Node, Node, Node, Node
            UIFont, IsoDirections = {Small = {}}, {S = {}}
            function getTextManager() return {getFontHeight = function() return 14 end} end
            function getContextMenuText(key) return key end
            Events = {OnGameStart = {Add = noop}}
            package.preload['ISUI/ISLayoutManager'] = noop
        """)

    def test_dialogue_buttons_belong_only_to_window(self):
        self.lua.execute((UI / 'SSQuestManagerDialogue.lua').read_bytes())
        self.lua.execute("""
            local window = setmetatable(Node:new(), {__index = DialogueWindow})
            window:createChildren()
            assert(window.YesButton.parent == window and not window.YesButton.root)
            assert(window.NoButton.parent == window and not window.NoButton.root)
            assert(window.ContinueButton.parent == window and not window.ContinueButton.root)
        """)

    def test_survivor_call_button_belongs_only_to_window(self):
        self.lua.execute((UI / 'SurvivorInfoWindow.lua').read_bytes())
        self.lua.execute("""
            local window = setmetatable(Node:new(), {__index = SurvivorInfoWindow})
            window:createChildren()
            assert(window.MyCallButton.parent == window and not window.MyCallButton.root)
        """)


if __name__ == '__main__':
    unittest.main()
