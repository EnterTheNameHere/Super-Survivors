"""Installed-JAR API/order evidence only; these checks do not execute the engine."""
from pathlib import Path
from zipfile import ZipFile
import os
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from inspect_game_api import members


@unittest.skipUnless(os.environ.get('PZ_GAME_DIR'), 'Set PZ_GAME_DIR to inspect the installed engine')
class InstalledPersistenceApiChecks(unittest.TestCase):
    def metadata(self, name):
        metadata = {}
        with ZipFile(Path(os.environ['PZ_GAME_DIR']) / 'projectzomboid.jar') as jar:
            entries = list(members(jar.read(name + '.class'), metadata))
        return entries, metadata

    def calls(self, metadata, method, owner, member):
        pool, code = metadata['pool'], metadata['bytecode'][method]
        positions = []
        for index, ref in enumerate(pool):
            if not isinstance(ref, tuple) or ref[0] not in (10, 11):
                continue
            if pool[pool[ref[1]]] != owner or pool[pool[ref[2]][1]] != member:
                continue
            for opcode in range(0xb6, 0xba):
                start = 0
                token = bytes([opcode]) + index.to_bytes(2, 'big')
                while (pos := code.find(token, start)) >= 0:
                    positions.append(pos)
                    start = pos + len(token)
        self.assertTrue(positions, (method, owner, member))
        return positions

    def test_global_data_load_precedes_initialization_callback_and_world_save_precedes_data_write(self):
        _, data = self.metadata('zombie/world/moddata/GlobalModData')
        self.assertIn('OnInitGlobalModData', data['pool'])
        self.assertLess(max(self.calls(data, 'init()V', 'zombie/world/moddata/GlobalModData', 'load')),
                        min(self.calls(data, 'init()V', 'zombie/Lua/LuaEventManager', 'triggerEvent')))
        _, world = self.metadata('zombie/GameWindow')
        self.assertIn('OnSave', world['pool'])
        # Both OnSave call sites (client early return and normal save) precede
        # the normal GlobalModData write. Source review distinguishes the paths.
        self.assertLess(max(self.calls(world, 'save(Z)V', 'zombie/Lua/LuaEventManager', 'triggerEvent')),
                        min(self.calls(world, 'save(Z)V', 'zombie/world/moddata/GlobalModData', 'save')))

    def test_native_character_and_moddata_entry_points_still_exist(self):
        entries, _ = self.metadata('zombie/characters/IsoPlayer')
        public = {(n, d) for kind, flags, n, d in entries if kind == 'method' and flags & 1}
        self.assertIn(('save', '(Ljava/lang/String;)V'), public)
        self.assertIn(('load', '(Ljava/lang/String;)V'), public)
        entries, _ = self.metadata('zombie/world/moddata/ModData')
        public = {(n, d) for kind, flags, n, d in entries if kind == 'method' and flags & 1 and flags & 8}
        for name in ('get', 'getOrCreate'):
            self.assertIn((name, '(Ljava/lang/String;)Lse/krka/kahlua/vm/KahluaTable;'), public)

    def test_moving_object_native_position_fields_are_saved_and_restored(self):
        _, data = self.metadata('zombie/iso/IsoMovingObject')
        for axis in ('X', 'Y', 'Z'):
            self.calls(data, 'save(Ljava/nio/ByteBuffer;Z)V', 'zombie/iso/IsoMovingObject', 'get'+axis)
            self.calls(data, 'load(Ljava/nio/ByteBuffer;IZ)V', 'zombie/iso/IsoMovingObject', 'set'+axis)
        self.calls(data, 'save(Ljava/nio/ByteBuffer;Z)V', 'java/nio/ByteBuffer', 'putFloat')
        # Source review also follows the setters and observes that they do not
        # update currentSquare. This check alone does not execute a native load.
        self.calls(data, 'load(Ljava/nio/ByteBuffer;IZ)V', 'java/nio/ByteBuffer', 'getFloat')


if __name__ == '__main__':
    unittest.main()
