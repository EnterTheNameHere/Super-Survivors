"""Exercise mod option registration against the installed B42 GameOption helper."""
import os
from pathlib import Path
import unittest

from lupa.lua51 import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]
GAME = os.environ.get('PZ_GAME_DIR')


@unittest.skipUnless(GAME, 'Set PZ_GAME_DIR to use installed vanilla option definitions')
class OptionsChecks(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.globals().gameLua = str(Path(GAME) / 'media/lua')
        self.lua.execute("""
            package.path = gameLua .. '/client/?.lua;' .. gameLua .. '/shared/?.lua;' .. package.path
            package.preload.defines = function() return true end
            print = function() end
            isTable = function(value) return type(value) == 'table' end
            DebugType = {GameOption = {warn = function() error('Option rejected') end,
                trace = function() end}}
            luautils = {indexOf = function(items, value)
                for i, item in ipairs(items) do if item == value then return i - 1 end end
                return -1
            end}
            require 'OptionScreens/GameOption'
            vanillaGameOption, vanillaGameOptions = GameOption, GameOptions
            globalOption = {marker = 'vanilla global'}
            gameOption = globalOption
            Orders, OrderDisplayName = {}, {}
            keyBinding = {{value = 'Shout'}}
            getFileReader = function() return nil end
            getOptionText = function(key) return key end
            MainOptions = {keyText = {}, translatorPane = {getHeight = function() return 0 end}}
            events = {}
            MainOptions.create = function(self)
                table.insert(events, 'vanilla')
                self.gameOptions = GameOptions:new()
            end
            MainOptions.getWidth = function() return 900 end
            MainOptions.addPage = function(self, name)
                assert(events[1] == 'vanilla')
                table.insert(events, name)
                self.mainPanel = {setScrollHeight = function() end}
            end
            MainOptions.addCombo = function(_, x, y, width, height, label, options, selected)
                return {isCombobox = true, options = options, selected = selected,
                    setToolTipMap = function() end}
            end
            panel = setmetatable({}, {__index = MainOptions})
        """)
        self.lua.execute((ROOT / '42/media/lua/client/5_UI/SuperSurvivorOptions.lua').read_text())
        self.lua.execute("""
            persistOption = SuperSurvivorSetOption
            writes, refreshed = {}, 0
            SuperSurvivorSetOption = function(id, value) writes[id] = value end
            SuperSurvivorsRefreshSettings = function() refreshed = refreshed + 1 end
        """)

    def memory_files(self):
        self.lua.execute(r'''
            files, readerCloses, writerCloses = {}, 0, 0
            getFileReader = function(name, create)
                assert(create == false)
                local data = files[name]
                if data == nil then return nil end
                local lines = {}
                for line in (data .. '\n'):gmatch('(.-)\n') do
                    table.insert(lines, (line:gsub('\r$', '')))
                end
                local index = 0
                return {readLine = function() index=index+1;return lines[index] end,
                    close = function() readerCloses=readerCloses+1 end}
            end
            getFileWriter = function(name, create, append)
                assert(name == 'SurvivorOptions.txt' and create and not append)
                if writerUnavailable then return nil end
                local chunks = {}
                return {write=function(_,text) table.insert(chunks,text) end,
                    close=function()
                        files[name]=table.concat(chunks)
                        writerCloses=writerCloses+1
                    end}
            end
        ''')

    def test_options_round_trip_to_allowed_text_file(self):
        self.memory_files()
        self.lua.execute("""
            SuperSurvivorOptions = {SpawnRate=7, WifeSpawn=2}
            assert(persistOption('SpawnRate',9))
            assert(writerCloses==1 and files['SurvivorOptions.lua']==nil)
            local loaded=LoadSurvivorOptions()
            assert(loaded.SpawnRate==9 and loaded.WifeSpawn==2 and readerCloses==1)
            assert(doesOptionsFileExist() and readerCloses==2)
        """)

    def test_legacy_options_migrate_on_save_without_overwriting_original(self):
        self.memory_files()
        self.lua.execute(r'''
            local legacy='SpawnRate 8\n\nWifeSpawn 2\nbroken\nBadNumber nope\n'
            files['SurvivorOptions.lua']=legacy
            SuperSurvivorOptions=LoadSurvivorOptions()
            assert(SuperSurvivorOptions.SpawnRate==8 and SuperSurvivorOptions.WifeSpawn==2)
            assert(SuperSurvivorOptions.BadNumber==nil and readerCloses==1)
            assert(persistOption('SpawnRate',10))
            assert(files['SurvivorOptions.lua']==legacy and writerCloses==1)
            -- The new text file takes precedence over the legacy file.
            assert(LoadSurvivorOptions().SpawnRate==10 and readerCloses==2)
        ''')

    def test_unavailable_writer_reports_failure_and_restores_previous_value(self):
        self.memory_files()
        self.lua.execute("""
            SuperSurvivorOptions={SpawnRate=7}
            files['SurvivorOptions.txt']='SpawnRate 7'
            writerUnavailable=true
            local ok,err=pcall(function() persistOption('SpawnRate',9) end)
            assert(not ok and tostring(err):find('Cannot open SurvivorOptions.txt',1,true))
            assert(SuperSurvivorOptions.SpawnRate==7 and files['SurvivorOptions.txt']=='SpawnRate 7')
            assert(writerCloses==0)
        """)

    def test_page_wraps_vanilla_and_registers_options_with_current_lifecycle(self):
        self.lua.execute("""
            panel:create()
            assert(events[1] == 'vanilla' and events[2] == 'Superb Survivors')
            assert(#panel.gameOptions.options > 20)
            assert(GameOption == vanillaGameOption and GameOptions == vanillaGameOptions)
            assert(gameOption == globalOption)
            panel.gameOptions:storeCurrentValues()
            panel.gameOptions:restoreOriginalValues()
            panel.gameOptions:toUI()
            assert(panel.gameOptions:get('SpawnRate').control.selected == 7)
        """)

    def test_combo_changes_are_independent_and_only_apply_saves_them(self):
        self.lua.execute("""
            panel.gameOptions = GameOptions:new()
            SuperSurvivorOptions.First, SuperSurvivorOptions.Second = 1, 2
            panel:addCustomCombo('First', 0, 0, 200, 'First', {'off', 'on'})
            panel:addCustomCombo('Second', 0, 0, 200, 'Second', {'off', 'on'})
            panel.gameOptions:toUI()
            local first = panel.gameOptions:get('First')
            local second = panel.gameOptions:get('Second')
            assert(first ~= second and first.control.selected == 1 and second.control.selected == 2)
            first.control.selected = 2
            first.control.onChange(first.control.target, first.control)
            assert(panel.gameOptions.changed and next(writes) == nil)
            panel.gameOptions:apply()
            assert(writes.First == 2 and writes.Second == 2 and refreshed == 2)
            assert(gameOption == globalOption)
        """)


if __name__ == '__main__':
    unittest.main()
