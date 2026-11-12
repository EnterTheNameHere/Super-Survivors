"""Audit lexical filtering and verify typed constants against the installed JAR."""
import os
from pathlib import Path
import re
import sys
import unittest
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from audit_lua_names import code_only
from inspect_game_api import members
from audit_b42_keys import audit, item_catalog, without_comments
from tempfile import TemporaryDirectory


class ApiInventoryChecks(unittest.TestCase):
    def test_key_inventory_keeps_strings_and_discards_comments(self):
        source = '"Base.Valid--Item" -- "Base.Old"\n--[[ "Base.Old2" ]]\n"Base.Other"'
        code = without_comments(source)
        self.assertIn('"Base.Valid--Item"', code)
        self.assertNotIn('Base.Old', code)
        self.assertEqual(code.count('\n'), source.count('\n'))

    def test_item_catalog_respects_module_and_ignores_recipe_inputs(self):
        with TemporaryDirectory() as directory:
            path = Path(directory)
            (path / 'items.txt').write_text('module Base { item Axe {} } module Survivors { item Grave {} }')
            (path / 'recipes.txt').write_text('module Base { craftRecipe X { inputs { item 1 Base.Other, } } }')
            self.assertEqual(set(item_catalog(path)), {'Base.Axe', 'Survivors.Grave'})

    @unittest.skipUnless(os.environ.get('PZ_GAME_DIR'), 'Set PZ_GAME_DIR to verify fixed B42 keys')
    def test_fixed_keys_resolve_except_documented_subsystem_ports(self):
        report = audit(Path(os.environ['PZ_GAME_DIR']), ROOT / '42/media')
        self.assertEqual(report['missing_typed_constants'], [])
        self.assertEqual(report['missing_perk_names'], [])
        # These are known non-trivial ports/legacy predicates, not tolerated new typos.
        self.assertEqual({row['key'] for row in report['missing_item_ids']},
                         {'Base.Cigarettes', 'Base.WaterPot', 'Base.WaterBottleFull', 'Base.WoodenLance'})

    def test_inventory_ignores_comments_and_strings_preserving_lines(self):
        source = '--[=[ a:bad()\n b:bad() ]=]\n"c:bad()"\nd:real() -- e:bad()\n'
        code = code_only(source)
        self.assertEqual(re.findall(r':(\w+)\(', code), ['real'])
        self.assertEqual(code.count('\n'), source.count('\n'))

    @unittest.skipUnless(os.environ.get('PZ_GAME_DIR'), 'Set PZ_GAME_DIR to verify game constants')
    def test_active_typed_stat_trait_and_moodle_constants_exist_in_installed_game(self):
        classes = {'CharacterStat': 'zombie/characters/CharacterStat',
                   'CharacterTrait': 'zombie/scripting/objects/CharacterTrait',
                   'MoodleType': 'zombie/scripting/objects/MoodleType'}
        with ZipFile(Path(os.environ['PZ_GAME_DIR']) / 'projectzomboid.jar') as jar:
            fields = {name: {n for k, f, n, d in members(jar.read(cls + '.class'))
                             if k == 'field' and f & 1 and f & 8}
                      for name, cls in classes.items()}
        for path in (ROOT / '42/media/lua').rglob('*.lua'):
            code = code_only(path.read_text(encoding='utf-8-sig'))
            for cls, constant in re.findall(r'\b(CharacterStat|CharacterTrait|MoodleType)\.([A-Z][A-Z_0-9]*)\b', code):
                with self.subTest(file=path.name, constant=cls + '.' + constant):
                    self.assertIn(constant, fields[cls])


if __name__ == '__main__':
    unittest.main()
