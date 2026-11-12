"""Submit standalone SP players in B42's opaque world-render event."""
from pathlib import Path
import unittest

from lupa.lua51 import LuaRuntime

MODULE = Path(__file__).resolve().parents[1] / '42/media/lua/client/3_Other/SuperSurvivorRender.lua'


class RenderBridgeChecks(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute("""
            callbacks, tickCallbacks = {}, {}
            Events = {RenderOpaqueObjectsInWorld = {
                Add = function(fn) callbacks[fn] = true end,
                Remove = function(fn) callbacks[fn] = nil end},
                OnTick = {Add = function(fn) tickCallbacks[fn] = true end,
                    Remove = function(fn) tickCallbacks[fn] = nil end}}
            multiplayer, server = false, false
            function isClient() return multiplayer end
            function isServer() return server end
            light, renders, shadows = {}, 0, 0
            visible, member, onScreen, dead, localPlayer = true, true, true, false, false
            npcZ, observerZ = 0, 0
            opacityWrites, playerAlpha, playerTargetAlpha = 0, 1, 1
            function getNumActivePlayers() return 1 end
            playerDead, playerInvisible, playerSpriteInvisible, playerRender = false, false, false, true
            square = {isCanSee = function(_, index) assert(index == 0); return visible end,
                getLightInfo = function(_, index) assert(index == 0); return light end}
            npc = {isLocalPlayer = function() return localPlayer end,
                isDead = function() return dead end, isOnScreen = function() return onScreen end,
                getCurrentSquare = function() return square end,
                getX = function() return 10.5 end, getY = function() return 20.5 end,
                getZ = function() return npcZ end,
                renderShadow = function(_, x,y,z)
                    assert(x == 10.5 and y == 20.5 and z == npcZ); shadows = shadows + 1 end,
                render = function(_, ...)
                    assert(select('#', ...) == 7)
                    local x,y,z,color,wall,attached,shader = ...
                    assert(x == 10.5 and y == 20.5 and z == npcZ and color == light)
                    assert(wall == true and attached == false and shader == nil)
                    renders = renders + 1
                end}
            function getSpecificPlayer(index)
                assert(index == 0)
                return {getZ = function() return observerZ end,
                    isLocalPlayer = function() return true end,
                    isDead = function() return playerDead end,
                    isInvisible = function() return playerInvisible end,
                    isSpriteInvisible = function() return playerSpriteInvisible end,
                    getDoRender = function() return playerRender end,
                    setAlphaAndTarget = function(_, view, alpha)
                        assert(view == 0 and alpha == 1)
                        playerAlpha, playerTargetAlpha = alpha, alpha
                        opacityWrites = opacityWrites + 1 end}
            end
            function getCell() return {getObjectList = function() return {
                contains = function(_, character) assert(character == npc); return member end} end} end
            SSM = {SuperSurvivors = {[9] = {Get = function() return npc end}}}
        """)
        self.lua.execute(MODULE.read_bytes())
        self.lua.execute('opacityWrites = 0')

    def test_visible_registered_npc_is_submitted_to_engine_render(self):
        self.lua.execute("""
            SuperSurvivorRender.render(0)
            assert(renders == 1 and shadows == 1)
        """)

    def test_skips_multiplayer_local_players_unloaded_hidden_and_upper_floor_characters(self):
        self.lua.execute("""
            multiplayer = true; SuperSurvivorRender.render(0); multiplayer = false
            server = true; SuperSurvivorRender.render(0); server = false
            localPlayer = true; SuperSurvivorRender.render(0); localPlayer = false
            member = false; SuperSurvivorRender.render(0); member = true
            visible = false; SuperSurvivorRender.render(0); visible = true
            onScreen = false; SuperSurvivorRender.render(0); onScreen = true
            dead = true; SuperSurvivorRender.render(0); dead = false
            npcZ = 1; SuperSurvivorRender.render(0); npcZ = 0
            light = nil; SuperSurvivorRender.render(0)
            assert(renders == 0 and shadows == 0)
        """)

    def test_hot_reload_replaces_callback(self):
        old = self.lua.eval('SuperSurvivorRender.callback')
        self.lua.globals().oldCallback = old
        self.lua.execute('oldTickCallback = SuperSurvivorRender.opacityCallback')
        self.lua.execute(MODULE.read_bytes())
        self.lua.execute("""
            assert(not callbacks[oldCallback])
            local count = 0
            for callback in pairs(callbacks) do count = count + 1; callback(0) end
            assert(count == 1 and renders == 1)
            assert(not tickCallbacks[oldTickCallback])
            count = 0
            for callback in pairs(tickCallbacks) do count = count + 1 end
            assert(count == 1)
        """)

    def test_standalone_players_restore_only_local_observer_self_opacity_even_when_offscreen(self):
        self.lua.execute("""
            onScreen = false
            SuperSurvivorRender.updateObserverOpacity()
            assert(opacityWrites == 1 and renders == 0)
            member = false
            SuperSurvivorRender.updateObserverOpacity()
            assert(opacityWrites == 1)
            member, multiplayer = true, true
            SuperSurvivorRender.updateObserverOpacity()
            assert(opacityWrites == 1)
        """)

    def test_self_opacity_guard_preserves_explicit_flags_and_death(self):
        self.lua.execute("""
            playerDead = true; SuperSurvivorRender.updateObserverOpacity(); playerDead = false
            playerInvisible = true; SuperSurvivorRender.updateObserverOpacity(); playerInvisible = false
            playerSpriteInvisible = true; SuperSurvivorRender.updateObserverOpacity(); playerSpriteInvisible = false
            playerRender = false; SuperSurvivorRender.updateObserverOpacity()
            assert(opacityWrites == 0)
        """)

    def test_opacity_is_restored_before_player_submission_not_in_late_render_event(self):
        self.lua.execute("""
            for frame = 1, 3 do
                -- Native world/NPC LOS update can fade the observer each frame.
                playerAlpha, playerTargetAlpha = 0, 0
                for callback in pairs(tickCallbacks) do callback(frame) end
                -- Installed engine submits the real player before the opaque event.
                assert(playerAlpha == 1 and playerTargetAlpha == 1)
                local writesAtPlayerSubmission = opacityWrites
                SuperSurvivorRender.render(0)
                assert(opacityWrites == writesAtPlayerSubmission)
            end
            assert(opacityWrites == 3 and renders == 3)
        """)

    def test_hot_reload_repairs_already_invisible_observer_without_a_tick(self):
        self.lua.execute('playerAlpha, playerTargetAlpha = 0, 0')
        self.lua.execute(MODULE.read_bytes())
        self.lua.execute('assert(playerAlpha == 1 and playerTargetAlpha == 1)')

    def test_opacity_guard_skips_server_and_missing_or_dead_standalone_characters(self):
        self.lua.execute("""
            server = true; SuperSurvivorRender.updateObserverOpacity(); server = false
            dead = true; SuperSurvivorRender.updateObserverOpacity(); dead = false
            localPlayer = true; SuperSurvivorRender.updateObserverOpacity(); localPlayer = false
            member = false; SuperSurvivorRender.updateObserverOpacity(); member = true
            SSM = nil; SuperSurvivorRender.updateObserverOpacity()
            assert(opacityWrites == 0)
        """)

    def test_each_local_observer_is_written_only_in_its_own_view(self):
        self.lua.execute("""
            local writes = {}
            getNumActivePlayers = function() return 2 end
            getSpecificPlayer = function(index)
                return {isLocalPlayer = function() return true end,
                    isDead = function() return false end,
                    isInvisible = function() return false end,
                    isSpriteInvisible = function() return false end,
                    getDoRender = function() return true end,
                    setAlphaAndTarget = function(_, view, alpha)
                        assert(view == index and alpha == 1)
                        writes[index] = (writes[index] or 0) + 1
                    end}
            end
            SuperSurvivorRender.updateObserverOpacity()
            assert(writes[0] == 1 and writes[1] == 1)
        """)


if __name__ == '__main__':
    unittest.main()
