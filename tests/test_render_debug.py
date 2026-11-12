"""Read-only diagnostics for a spawned but invisible character."""
from pathlib import Path
import unittest

from lupa.lua51 import LuaRuntime

MODULE = Path(__file__).resolve().parents[1] / '42/media/lua/client/Debug/SuperbSurvivorsDebug.lua'


class RenderDebugChecks(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute("""
            debugEnabled, multiplayer = true, false
            function getDebug() return debugEnabled end
            function isClient() return multiplayer end
            function isServer() return false end
            print = function() end
            callbacks = {}
            Events = {OnTick = {
                Add = function(fn) callbacks[fn] = true end,
                Remove = function(fn) callbacks[fn] = nil end}}
            square = {getMovingObjects = function() return {
                size = function() return 1 end, get = function() return npc end} end,
                isCanSee = function() return true end}
            local visual = {getSkinTexture = function() return 'MaleBody01' end,
                            getHairModel = function() return 'Short' end}
            npc = {getCurrentSquare = function() return square end,
                getHumanVisual = function() return visual end,
                getCell = function() return {getLuaObjectList = function() return {npc} end} end,
                getX = function() return 10 end, getY = function() return 20 end,
                getZ = function() return 0 end, isNpc = function() return true end,
                isLocalPlayer = function() return false end, isInvisible = function() return false end,
                isSpriteInvisible = function() return false end, isSceneCulled = function() return true end,
                isAddedToModelManager = function() return false end,
                hasActiveModel = function() return false end, getModelInstance = function() return nil end,
                hasAnimationPlayer = function() return false end, getRenderSquare = function() return nil end,
                getDoRender = function() return true end,
                getAnimationStateName = function() return 'idle' end,
                getCurrentStateName = function() return 'idle' end,
                getOffsetX = function() return 0 end, getOffsetY = function() return 0 end,
                getRenderYOffset = function() return 0 end,
                getAlpha = function() return 0 end, getTargetAlpha = function() return 0 end}
            local observer = {getX = function() return 12 end, getY = function() return 20 end,
                getZ = function() return 0 end, CanSee = function(_, target) return target == npc end}
            function getSpecificPlayer() return observer end
            SSM = {Get = function(_, id)
                if id == 9 then return {Get = function() return npc end} end
            end}
        """)
        self.lua.execute(MODULE.read_bytes())

    def test_inspection_reports_missing_model_without_forcing_visibility(self):
        self.lua.execute("""
            SuperbSurvivorsDebug.lastSpawnedID = 9
            local state = SuperbSurvivorsDebug.inspect()
            assert(state.id == 9 and state.inCell and state.onSquare and state.hasVisual)
            assert(state.sceneCulled and not state.modelRegistered and not state.modelInstance)
            assert(state.alpha == 0 and state.targetAlpha == 0)
            assert(state.doRender)
            assert(not state.hasAnimationPlayer and not state.hasRenderSquare)
            assert(state.observerCanSee and state.squareVisible)
            assert(state.skinTexture == 'MaleBody01' and state.x == 10 and state.observerX == 12)
            -- There are no setters on the character: inspection must stay read-only.
        """)

    def test_deferred_capture_waits_for_ticks_and_replaces_pending_callback(self):
        self.lua.execute("""
            local captures = 0
            SuperbSurvivorsDebug.inspect = function(id) assert(id == 9); captures = captures + 1 end
            assert(SuperbSurvivorsDebug.inspectAfterTicks(9))
            local first = SuperbSurvivorsDebug.pendingInspection
            assert(callbacks[first])
            assert(SuperbSurvivorsDebug.inspectAfterTicks(9))
            assert(not callbacks[first])
            local second = SuperbSurvivorsDebug.pendingInspection
            for i = 1,119 do second() end
            assert(captures == 0 and callbacks[second])
            second()
            assert(captures == 1 and not callbacks[second])
            assert(SuperbSurvivorsDebug.pendingInspection == nil)
        """)

    def test_inspection_uses_character_api_without_indexing_unexposed_animation_object(self):
        self.lua.execute("""
            npc.hasAnimationPlayer = function() return true end
            npc.getAnimationPlayer = function() error('AnimationPlayer is not Lua-exposed') end
            npc.getRenderSquare = function() return square end
            local state = SuperbSurvivorsDebug.inspect(9)
            assert(state.hasAnimationPlayer and state.renderSquareMatches)
        """)

    def test_model_reset_probe_resets_existing_character_then_schedules_capture(self):
        self.lua.execute("""
            local resets = 0
            npc.resetModel = function() resets = resets + 1 end
            assert(SuperbSurvivorsDebug.resetModelProbe(10) == nil)
            assert(resets == 0)
            debugEnabled = false
            assert(SuperbSurvivorsDebug.resetModelProbe(9) == nil)
            debugEnabled = true
            assert(SuperbSurvivorsDebug.resetModelProbe(9))
            assert(resets == 1 and callbacks[SuperbSurvivorsDebug.pendingInspection])
        """)

    def test_model_comparison_reads_opaque_handles_only_through_debug_reflection(self):
        self.lua.execute("""
            local fields, names = {}, {}
            local function opaque(values)
                local object = newproxy(true)
                getmetatable(object).__index = function() error('opaque Java object indexed') end
                fields[object], names[object] = values, {}
                for name in pairs(values) do table.insert(names[object], name) end
                return object
            end
            function getNumClassFields(object) return #names[object] end
            function getClassField(object, index)
                local name = names[object][index + 1]
                return {getName = function() return name end, name = name}
            end
            function getClassFieldVal(object, field) return fields[object][field.name] end
            function getCore() return {isDisplayPlayerModel = function() return true end} end
            local list = {size = function() return 2 end}
            names[list], fields[list] = {}, {}
            local mesh = opaque({fullPath = 'female', hasVbo = true, skinningData = {}})
            local model = opaque({name = 'FemaleBody', mesh = mesh})
            local instance = opaque({model = model, data = {}, scale = 1,
                tintR = 1, tintG = 1, tintB = 1, sub = list})
            local animation = opaque({model = model, skinningData = {}, updateBones = true,
                boneTransformsNeedFirstFrame = false, multiTrack = opaque({tracks = list})})
            local sprite = opaque({modelSlot = opaque({framesSinceStart = 10, active = true, remove = false})})
            local function prepare(character)
                character.getModelInstance = function() return instance end
                character.getAnimationPlayer = function() return animation end
                character.getTextureCreator = function() return nil end
                character.getSprite = function() return sprite end
                character.isLocal = function() return true end
                character.getAnimationDebug = function() return 'idle' end
            end
            prepare(npc)
            prepare(getSpecificPlayer(0))
            local state = SuperbSurvivorsDebug.compareModels(9)
            assert(state.npc.meshVbo and state.npc.scale == 1 and state.npc.animationModelMatches)
            assert(state.npc.tracks == 2 and not state.npc.firstFramePending)
            assert(state.player.slotFrames == 10 and not state.player.slotRemoving)
            assert(not state.npc.textureCreator and state.npc.animationDebug == 'idle')
        """)

    def test_inspection_rejects_unavailable_or_non_debug_survivors(self):
        self.lua.execute("""
            assert(SuperbSurvivorsDebug.inspect() == nil)
            assert(SuperbSurvivorsDebug.inspect(10) == nil)
            debugEnabled = false
            assert(SuperbSurvivorsDebug.inspect(9) == nil)
            debugEnabled, multiplayer = true, true
            assert(SuperbSurvivorsDebug.inspect(9) == nil)
        """)

    def prepare_stationary(self):
        self.lua.execute("""
            visible, free, spawns, stops, waits = true, true, 0, 0, 0
            local observer = getSpecificPlayer(0)
            observer.getCurrentSquare = function() return {} end
            function getCell() return {getGridSquare = function(_, x, y, z)
                if x ~= 13 or y ~= 20 or z ~= 0 then return nil end
                return {isCanSee = function() return visible end,
                        isFree = function() return free end,
                        getFloor = function() return {} end}
            end} end
            survivor = {getID = function() return 9 end,
                StopWalk = function() stops = stops + 1 end,
                Wait = function(_, ticks) assert(ticks == 36000); waits = waits + 1 end}
            SuperbSurvivorsDebug.spawn = function(x, y, z)
                assert(x == 13 and y == 20 and z == 0)
                spawns = spawns + 1
                return survivor
            end
        """)

    def test_stationary_probe_spawns_once_and_holds_before_returning(self):
        self.prepare_stationary()
        self.lua.execute("""
            assert(SuperbSurvivorsDebug.spawnStationary() == survivor)
            assert(spawns == 1 and stops == 1 and waits == 1)
        """)

    def test_stationary_probe_rejects_hidden_or_blocked_tiles(self):
        self.prepare_stationary()
        self.lua.execute("""
            visible = false
            assert(SuperbSurvivorsDebug.spawnStationary() == nil)
            visible, free = true, false
            assert(SuperbSurvivorsDebug.spawnStationary() == nil)
            assert(spawns == 0 and stops == 0 and waits == 0)
        """)

    def test_stationary_probe_preserves_constructor_failure(self):
        self.prepare_stationary()
        self.lua.execute("""
            SuperbSurvivorsDebug.spawn = function() error('stationary constructor failure') end
            local ok, err = pcall(SuperbSurvivorsDebug.spawnStationary)
            assert(not ok and string.find(err, 'stationary constructor failure', 1, true))
            assert(stops == 0 and waits == 0)
        """)


if __name__ == '__main__':
    unittest.main()
