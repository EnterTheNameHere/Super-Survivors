"""Test-session flags must block spawn sources without marking squares consumed."""
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime

CLIENT = Path(__file__).resolve().parents[1] / '42/media/lua/client'


class IsolationChecks(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)

    def test_automatic_random_and_raid_paths_return_before_spawning(self):
        self.lua.execute('''
            package.preload['0_Utilities/SuperSurvivorWeaponsList']=function() end
            Events=setmetatable({}, {__index=function(self,key)
                local event={Add=function() end};rawset(self,key,event);return event end})
            SSM={AutoSpawnsSuspended=true}
        ''')
        self.lua.execute((CLIENT / '3_Other/SuperSurvivorsMod.lua').read_bytes())
        self.lua.execute('''
            SuperSurvivorDoRandomSpawns()
            SuperSurvivorsRaiderManager()
            SurvivorMap={}
            local data={}
            local square={getX=function() return 1 end,getY=function() return 2 end,getZ=function() return 0 end,
                getModData=function() return data end}
            SuperSurvivorsLoadGridsquare(square)
            assert(data.SurvivorSquareLoaded==nil)
        ''')

    def test_manager_filter_pauses_other_lua_ai_without_touching_local_player(self):
        self.lua.execute((CLIENT / '3_Other/SuperSurvivorManager.lua').read_bytes())
        self.lua.execute('''
            local function npc()
                return {player={isAsleep=function() return false end},isInCell=function() return true end,
                    updateTime=function(self) self.ticks=(self.ticks or 0)+1;return true end,
                    update=function(self) self.updates=(self.updates or 0)+1 end}
            end
            local normal,chosen,main=npc(),npc(),npc()
            SSM.SuperSurvivors={[0]=main,[1]=normal,[2]=chosen}
            SSM.UpdateFilter=function(s) return s==chosen end
            SSM:update()
            assert(chosen.updates==1 and normal.ticks==nil and main.ticks==nil)
            SSM.UpdateFilter=nil;SSM:update()
            assert(normal.updates==1 and chosen.updates==2 and main.ticks==nil)
        ''')

    def test_preset_paths_do_not_consume_a_square_when_suppressed(self):
        self.lua.globals().clientRoot = str(CLIENT)
        self.lua.execute('''
            package.path=clientRoot..'/?.lua;'..package.path
            function getActivatedMods() return {size=function() return 0 end} end
            function getText(key) return key end
            function ZombRand(first,last) return last and first or 0 end
            ImmutableColor={new=function() return {} end}
            require '3_Other/SuperSurvivor'
            SSM={AutoSpawnsSuspended=true}
            -- Nil arguments prove both paths exit before touching any world object.
            assert(SuperSurvivorPresetSpawn(nil)==false)
            assert(SuperSurvivorPresetSpawnThis(nil)==false)
        ''')
