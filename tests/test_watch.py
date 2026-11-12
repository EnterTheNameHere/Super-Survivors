"""Survivor state monitoring does not take control or claim camera following."""
from pathlib import Path
import os
import sys
import unittest
from zipfile import ZipFile
from lupa.lua51 import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from inspect_game_api import members
SOURCE = ROOT / '42/media/lua/client/Debug/SuperbSurvivorsDebug.lua'


class WatchChecks(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute("""
            log, drawn, handlers = {}, {}, {}
            print = function(line) table.insert(log, line) end
            Events = setmetatable({}, {__index = function(t, name)
                handlers[name] = {}
                local event = {
                    Add = function(fn) handlers[name][fn] = true end,
                    Remove = function(fn) handlers[name][fn] = nil end}
                rawset(t, name, event); return event
            end})
            debugMode, client, server, players, clock = true, false, false, 1, 0
            getDebug = function() return debugMode end
            isClient = function() return client end
            isServer = function() return server end
            getNumActivePlayers = function() return players end
            getTimestampMs = function() return clock end
            cell = {getObjectList = function() return {
                contains = function(_, character) return character.loaded end}
            end}
            getCell = function() return cell end
            local function actor(x, localPlayer)
                local a = {x=x, loaded=true, dead=false, health=100}
                a.isDead=function() return a.dead end
                a.isLocalPlayer=function() return localPlayer end
                a.getCell=function() return cell end
                a.getCurrentSquare=function() return a.loaded and {} or nil end
                a.getX=function() return a.x end
                a.getY=function() return a.y or 20 end
                a.getZ=function() return a.z or 0 end
                a.getBodyDamage=function() return {
                    getOverallBodyHealth=function() return a.health end}
                end
                return a
            end
            player, npc, otherNpc = actor(10,true), actor(12,false), actor(40,false)
            getSpecificPlayer=function(index) assert(index==0); return player end
            taskManager={LastTask='Wait',getCurrentTask=function() return 'Patrol' end}
            local function survivor(character, name)
                return {Get=function() return character end,
                    getName=function() return name end,
                    getTaskManager=function() return taskManager end,
                    getAIMode=function() return 'Independent' end,
                    getGroupRole=function() return 'Guard' end,
                    getDangerSeenCount=function() return 2 end,
                    getSeenCount=function() return 3 end,WaitTicks=0}
            end
            SSM={SuperSurvivors={[0]=survivor(player,'Player'),
                [12]=survivor(npc,'Emma'),[13]=survivor(otherNpc,'Robert')}}
            camera, cameraUpdates, cameraOffset = player, 0, player.x
            IsoCamera={
                getCameraCharacter=function() return camera end,
                setCameraCharacter=function(character) camera=character;return true end,
                clearCameraCharacter=function() camera=nil end,
                update=function() cameraUpdates=cameraUpdates+1;cameraOffset=camera.x end}
            UIFont={Small={}}
            getTextManager=function() return {
                getFontHeight=function() return 12 end,
                DrawString=function(_,font,x,y,text,r,g,b,a) table.insert(drawn,text) end}
            end
        """)
        self.lua.execute(SOURCE.read_text())

    def test_dead_player_can_observe_nearest_npc_with_state_overlay(self):
        self.lua.execute("""
            player.dead=true
            assert(SuperbSurvivorsWatch.start())
            assert(camera==player and cameraUpdates==0 and getSpecificPlayer(0)==player and player.dead)
            assert(SuperbSurvivorsWatch.state.id==12)
            local info=SuperbSurvivorsWatch.status()
            assert(info.task=='Patrol' and info.name=='Emma' and info.health==100 and not info.cameraFollow)
            assert(info.danger==2 and info.seen==3)
            taskManager.getCurrentTask=function() return 'Doctor' end
            clock=500
            SuperbSurvivorsWatch.tick()
            SuperbSurvivorsWatch.draw()
            assert(SuperbSurvivorsWatch.state.snapshot.task=='Doctor')
            assert(#drawn==8 and drawn[2]:find('Doctor',1,true))
            assert(taskManager.LastTask=='Wait')
            assert(SuperbSurvivorsWatch.stop() and camera==player)
        """)

    def test_navigation_tracks_distance_screen_direction_and_floor(self):
        self.lua.execute("""
            assert(SuperbSurvivorsWatch.start(12))
            local info=SuperbSurvivorsWatch.status()
            assert(info.distance==2 and info.floorDifference==0)
            assert(SuperbSurvivorsWatch.state.lines[6]:find('east; screen down-right',1,true))
            npc.x=7; npc.y=24; npc.z=1
            clock=500; SuperbSurvivorsWatch.tick()
            info=SuperbSurvivorsWatch.state.snapshot
            assert(info.distance==5 and info.floorDifference==1)
            assert(SuperbSurvivorsWatch.state.lines[6]:find('south-west; screen left',1,true))
            player.x=7; player.y=24; player.z=1
            clock=1000; SuperbSurvivorsWatch.tick()
            assert(SuperbSurvivorsWatch.state.lines[6]:find('within one tile',1,true))
            player=nil
            assert(SuperbSurvivorsWatch.status())
            assert(SuperbSurvivorsWatch.state.lines[6]:find('unavailable',1,true))
        """)

    def test_switching_targets_preserves_original_camera_and_failed_target(self):
        self.lua.execute("""
            assert(SuperbSurvivorsWatch.start(12))
            assert(SuperbSurvivorsWatch.start(13) and camera==player)
            assert(not SuperbSurvivorsWatch.start(999) and camera==player)
            SuperbSurvivorsWatch.stop()
            assert(camera==player and not SuperbSurvivorsWatch.state.active)
            camera=nil
            assert(SuperbSurvivorsWatch.start(12))
            assert(SuperbSurvivorsWatch.start(13))
            SuperbSurvivorsWatch.stop()
            assert(camera==nil and cameraUpdates==0) -- Monitoring never owns the camera.
        """)

    def test_target_death_or_unload_stops_without_touching_other_camera_owner(self):
        self.lua.execute("""
            assert(SuperbSurvivorsWatch.start(12))
            npc.loaded=false
            SuperbSurvivorsWatch.tick()
            assert(not SuperbSurvivorsWatch.state.active and camera==player)
            npc.loaded=true
            assert(SuperbSurvivorsWatch.start(12))
            camera=otherNpc -- Another camera system has taken over.
            npc.dead=true
            assert(SuperbSurvivorsWatch.status()==nil)
            assert(not SuperbSurvivorsWatch.state.active and camera==otherNpc)
        """)

    def test_listing_and_mode_filters_exclude_players_and_unloaded_npcs(self):
        self.lua.execute("""
            npc.loaded=false
            local list=SuperbSurvivorsWatch.list()
            assert(#list==1 and list[1].id==13)
            assert(not SuperbSurvivorsWatch.start(0))
            assert(not SuperbSurvivorsWatch.start(12))
            client=true;assert(not SuperbSurvivorsWatch.start(13));client=false
            server=true;assert(not SuperbSurvivorsWatch.start(13));server=false
            players=2;assert(not SuperbSurvivorsWatch.start(13));players=1
            debugMode=false;assert(not SuperbSurvivorsWatch.start(13))
            assert(camera==player and cameraUpdates==0)
        """)

    def test_monitor_does_not_install_an_ineffective_render_camera_callback(self):
        self.lua.execute("""
            assert(SuperbSurvivorsWatch.start(12))
            for frame=1,3 do
                clock=frame*500
                SuperbSurvivorsWatch.tick()
                assert(camera==player and cameraUpdates==0 and getSpecificPlayer(0)==player)
            end
            npc.x=15
            clock=2000
            SuperbSurvivorsWatch.tick()
            assert(SuperbSurvivorsWatch.state.snapshot.x==15)
            assert(handlers.OnRenderTick==nil or not next(handlers.OnRenderTick))
            SuperbSurvivorsWatch.stop()
            assert(camera==player and cameraUpdates==0)
        """)

    def test_hot_reload_replaces_callbacks_and_menu_exit_stops_watch(self):
        self.lua.execute('assert(SuperbSurvivorsWatch.start(12))')
        self.lua.execute(SOURCE.read_text())
        self.lua.execute("""
            for _, callbacks in pairs(handlers) do
                local count=0
                for callback in pairs(callbacks) do count=count+1 end
                assert(count==1)
            end
            for callback in pairs(handlers.OnMainMenuEnter) do callback() end
            assert(not SuperbSurvivorsWatch.state.active and camera==player)
        """)


@unittest.skipUnless(os.environ.get('PZ_GAME_DIR'), 'Set PZ_GAME_DIR to verify native camera update order')
class NativeCameraOrderChecks(unittest.TestCase):
    def test_render_tick_is_after_world_rendering(self):
        with ZipFile(Path(os.environ['PZ_GAME_DIR']) / 'projectzomboid.jar') as jar:
            metadata = {}
            list(members(jar.read('zombie/GameWindow.class'), metadata))
        pool = metadata['pool']

        def call_position(method, owner, name):
            code = metadata['bytecode'][method]
            positions = []
            for index, reference in enumerate(pool):
                if not isinstance(reference, tuple) or reference[0] not in (10, 11):
                    continue
                class_name = pool[pool[reference[1]]]
                member_name = pool[pool[reference[2]][1]]
                if class_name != owner or member_name != name:
                    continue
                for opcode in range(0xb6, 0xba):
                    position = code.find(bytes([opcode]) + index.to_bytes(2, 'big'))
                    if position >= 0:
                        positions.append(position)
            self.assertTrue(positions, (method, owner, name))
            return min(positions)

        self.assertLess(
            call_position('logic()V', 'zombie/gameStates/GameStateMachine', 'update'),
            call_position('logic()V', 'zombie/iso/IsoCamera', 'updateAll'))
        self.assertLess(
            call_position('frameStep()V', 'zombie/GameWindow', 'logic'),
            call_position('frameStep()V', 'zombie/GameWindow', 'onRender'))
        self.assertLess(
            call_position('frameStep()V', 'zombie/GameWindow', 'renderInternal'),
            call_position('frameStep()V', 'zombie/GameWindow', 'onRender'))


if __name__ == '__main__':
    unittest.main()
