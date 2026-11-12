"""Legacy save IO resolves the current mod ID and diagnoses missing writers."""
from pathlib import Path
import re
import unittest

from lupa.lua51 import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / '42/media/lua/client/0_Utilities/SuperSurvivorTablesUtilities.lua'


class LegacySaveIoChecks(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.globals().expectedModId = re.search(
            r'^id=(.+)$', (ROOT / '42/mod.info').read_text(), re.M)[1].strip()
        self.lua.execute("""
            function getWorld() return {getWorld = function() return 'TestWorld' end} end
            function getFileSeparator() return '/' end
            writes, writerCloses, readerCloses = {}, 0, 0
            writerAvailable, readerAvailable = true, true
            function getModFileWriter(modid, path, create, append)
                assert(modid == expectedModId)
                assert(create and not append)
                lastPath = path
                if not writerAvailable then return nil end
                return {write = function(_, line) table.insert(writes, line) end,
                        close = function() writerCloses = writerCloses + 1 end}
            end
            function getModFileReader(modid, path, create)
                assert(modid == expectedModId)
                if not readerAvailable then return nil end
                return {close = function() readerCloses = readerCloses + 1 end}
            end
        """)
        self.lua.execute(MODULE.read_bytes())

    def test_table_and_map_writers_use_current_mod_id_preserving_legacy_format(self):
        self.lua.execute("""
            table.save({2, 'leader'}, 'group')
            assert(lastPath == 'TestWorld/group.lua')
            assert(writes[1] == '2\\r\\n' and writes[2] == 'leader\\r\\n')
            kvtablesave({[4] = 10}, 'map')
            assert(lastPath == 'TestWorld/map' and writes[3] == '4 10\\r\\n')
            assert(writerCloses == 2)
        """)

    def test_failed_open_reports_context_before_attempting_to_write(self):
        self.lua.execute("""
            writerAvailable = false
            local ok, message = pcall(table.save, {1}, 'group')
            assert(not ok and string.find(message, expectedModId, 1, true))
            assert(string.find(message, 'TestWorld/group.lua', 1, true))
            assert(#writes == 0 and writerCloses == 0)
            ok, message = pcall(kvtablesave, {x = 1}, 'map')
            assert(not ok and string.find(message, 'TestWorld/map', 1, true))
        """)

    def test_existence_probe_closes_reader_and_handles_missing_file(self):
        self.lua.execute("""
            assert(doesFileExist('group.lua') and readerCloses == 1)
            readerAvailable = false
            assert(not doesFileExist('missing.lua') and readerCloses == 1)
        """)

    def prepare_typed_game_mode(self):
        self.lua.execute("""
            local mode = setmetatable({toString = function() return 'Sandbox' end}, {
                __concat = function() error('typed GameMode cannot be concatenated') end})
            function getWorld() return {
                getWorld = function() return 'TestWorld' end,
                getGameMode = function() return mode end} end
            Core = {getMyDocumentFolder = function() return 'UserData' end}
        """)

    def test_client_save_path_converts_typed_game_mode(self):
        self.prepare_typed_game_mode()
        self.assertEqual(self.lua.eval('getSaveDir()'), 'UserData/Saves/Sandbox/TestWorld/')

    def test_shared_save_path_converts_typed_game_mode_when_loaded_last(self):
        self.prepare_typed_game_mode()
        self.lua.execute((ROOT / '42/media/lua/shared/Utilities.lua').read_bytes())
        self.assertEqual(self.lua.eval('getSaveDir()'), 'UserData/Saves/Sandbox/TestWorld/')


if __name__ == '__main__':
    unittest.main()
