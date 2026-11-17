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

    def test_cell_only_constructor_and_separate_public_registration_contracts(self):
        entries, player = self.metadata('zombie/characters/IsoPlayer')
        self.assertIn(('method', 1, '<init>', '(Lzombie/iso/IsoCell;)V'), entries)
        self.calls(player, '<init>(Lzombie/iso/IsoCell;)V', 'zombie/characters/IsoPlayer', '<init>')
        entries, moving = self.metadata('zombie/iso/IsoMovingObject')
        public = {(n, d) for kind, flags, n, d in entries if kind == 'method' and flags & 1}
        self.assertIn(('setCurrentSquare', '(Lzombie/iso/IsoGridSquare;)V'), public)
        self.assertIn(('setMovingSquareNow', '()V'), public)
        self.calls(moving, 'setCurrentSquare(Lzombie/iso/IsoGridSquare;)V', 'zombie/iso/IsoMovingObject', 'setCurrent')
        self.calls(moving, 'setMovingSquareNow()V', 'zombie/iso/IsoMovingObject', 'setMovingSquare')
        _, cell = self.metadata('zombie/iso/IsoCell')
        self.calls(cell, 'addMovingObject(Lzombie/iso/IsoMovingObject;)V', 'zombie/iso/IsoCell', 'isSafeToAdd')

    def test_visual_diagnostic_direct_getters_are_field_reads_not_lazy_initializers(self):
        _, visual = self.metadata('zombie/core/skinnedmodel/visual/HumanVisual')
        for key, return_op in [('getSkinTextureIndex()I', 0xac), ('getBodyHairIndex()I', 0xac),
                               ('getNonAttachedHair()Ljava/lang/String;', 0xb0)]:
            code = visual['bytecode'][key]
            self.assertEqual(len(code), 5, key)
            self.assertEqual(code[:2], bytes([0x2a, 0xb4]), key)  # aload_0/getfield
            self.assertEqual(code[-1], return_op, key)
        _, player = self.metadata('zombie/characters/IsoPlayer')
        self.calls(player, 'isGhostMode()Z', 'zombie/characters/IsoPlayer', 'isInvisible')

    def test_combat_snapshot_direct_flags_and_world_frame_are_pure_field_reads(self):
        checks = {
            'zombie/iso/IsoWorld': ['getFrameNo()I'],
            'zombie/characters/IsoGameCharacter': [
                'isPerformingAttackAnimation()Z', 'isPerformingShoveAnimation()Z', 'isAimAtFloor()Z'],
            'zombie/characters/IsoPlayer': ['isAttackStarted()Z', 'isInitiateAttack()Z', 'isBlockMovement()Z'],
            'zombie/inventory/InventoryItem': ['getCurrentAmmoCount()I'],
            'zombie/inventory/types/HandWeapon': ['isJammed()Z', 'isRoundChambered()Z', 'isContainsClip()Z'],
            'zombie/characters/BodyDamage/BodyPart': ['bandaged()Z'],
        }
        for cls, methods in checks.items():
            _, metadata = self.metadata(cls)
            for method in methods:
                code = metadata['bytecode'][method]
                self.assertEqual(len(code), 5, (cls, method))
                self.assertEqual(code[:2], bytes([0x2a, 0xb4]), (cls, method))
                self.assertEqual(code[-1], 0xac, (cls, method))
        entries, _ = self.metadata('zombie/iso/IsoCell')
        self.assertIn(('method', 1, 'getObjectList', '()Ljava/util/Set;'), entries)

    def test_legacy_npc_control_methods_absent_and_current_control_component_contract(self):
        for cls in ['zombie/characters/IsoGameCharacter', 'zombie/characters/IsoLivingCharacter', 'zombie/characters/IsoPlayer']:
            entries, _ = self.metadata(cls)
            names = {name for kind, _, name, _ in entries if kind == 'method'}
            self.assertTrue(names.isdisjoint({'NPCSetAttack', 'NPCSetAiming', 'NPCGetAiming'}))
        entries, component = self.metadata('zombie/characters/component/AIComponent')
        self.assertIn(('method', 1, 'getHumanControlVars', '()Lzombie/ai/AIBrainPlayerControlVars;'), entries)
        self.calls(component, 'postUpdatePlayer(Lzombie/characters/IsoPlayer;)V',
                   'zombie/characters/IsoPlayer', 'setInitiateAttack')

    def test_build_version_api_includes_suffix_separately_from_game_version(self):
        entries, data = self.metadata('zombie/core/Core')
        public = {(n, d) for kind, flags, n, d in entries if kind == 'method' and flags & 1}
        self.assertIn(('getGameAndBuildVersion', '()Ljava/lang/String;'), public)
        self.assertIn(('getGameVersion', '()Lzombie/core/GameVersion;'), public)
        # Installed source confirms getGameAndBuildVersion appends .2 to 42.22.
        self.assertIn('getGameAndBuildVersion()Ljava/lang/String;', data['bytecode'])

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
