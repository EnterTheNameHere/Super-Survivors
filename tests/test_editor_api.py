"""Native editor definitions preserve inheritance and real receiver types."""
import os
from pathlib import Path
import sys
import unittest

from lupa.lua51 import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from generate_editor_api import generate

GAME = os.environ.get('PZ_GAME_DIR')


@unittest.skipUnless(GAME, 'Set PZ_GAME_DIR to inspect the installed game JAR')
class EditorApiChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = generate(Path(GAME) / 'projectzomboid.jar')

    def test_interfaces_events_and_constructors_are_available(self):
        self.assertIn('function IsoPlayer:getVariableBoolean(', self.source)
        self.assertIn('function IsoPlayer.new(', self.source)
        self.assertIn('---@field LoadGridsquare PZEvent', self.source)
        self.assertIn('---@field RenderOpaqueObjectsInWorld PZEvent', self.source)
        LuaRuntime().execute('assert(loadstring(...))', self.source)

    def test_subclass_apis_are_not_invented_on_base_types(self):
        self.assertIn('---@class HandWeapon: InventoryItem', self.source)
        self.assertIn('function HandWeapon:isAimedFirearm(', self.source)
        self.assertNotIn('function InventoryItem:isAimedFirearm(', self.source)
        self.assertNotIn('function IsoPlayer:getAngle(', self.source)
        self.assertNotIn('function IsoDirections.reverse(', self.source)
        self.assertNotIn('function IsoObject:getOppositeSquare(', self.source)
        self.assertIn('function InventoryContainer:getItemContainer(', self.source)
        self.assertNotIn('function InventoryItem:getItemContainer(', self.source)


if __name__ == '__main__':
    unittest.main()
