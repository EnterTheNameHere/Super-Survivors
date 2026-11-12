"""Combat/fluid regression checks with strict game-object stubs.

Set PZ_GAME_DIR to additionally exercise the installed vanilla water action.
These checks do not run game combat, animation or pathfinding.
"""
import os
from pathlib import Path
import unittest

from lupa.lua51 import LuaRuntime

CLIENT = Path(__file__).resolve().parents[1] / '42/media/lua/client'
GAME = os.environ.get('PZ_GAME_DIR')


class CombatWaterChecks(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.globals().clientRoot = str(CLIENT)
        self.lua.execute("""
            package.path = clientRoot .. '/?.lua;' .. package.path
            print = function() end
            function getActivatedMods() return {size = function() return 0 end} end
            function getText(key) return key end
            function ZombRand(first, last) return last and first or 0 end
            ImmutableColor = {new = function() return {} end}
            function instanceof(obj, kind) return obj and obj.kind == kind end
            require '3_Other/SuperSurvivor'
            function list(items)
                return {size = function() return #items end,
                        get = function(_, i) return items[i + 1] end,
                        isEmpty = function() return #items == 0 end}
            end
        """)

    def test_gun_tasks_prepare_the_actual_held_weapon(self):
        self.lua.execute("""
            local held = {}
            weapon = {} -- A global must not supply the selected weapon.
            for _, name in ipairs({'AttackTask', 'PursueTask', 'ThreatenTask'}) do
                require('7_Tasks/' .. name)
                local parent = {
                    player = {getPrimaryHandItem = function() return held end},
                    isWalkingPermitted = function() return true end,
                    NPC_MovementManagement = function() end,
                    hasGun = function() return true end,
                    needToReadyGun = function(_, item)
                        assert(item == held, 'wrong weapon passed to readiness check')
                        return true
                    end,
                    ReadyGun = function(_, item)
                        assert(item == held, 'wrong weapon passed to gun preparation')
                        error('ready reached')
                    end,
                    setRunning = function() end,
                }
                local task = setmetatable({parent = parent,
                    isValid = function() return true end,
                    isComplete = function() return false end}, {__index = _G[name]})
                local ok, err = pcall(function() task:update() end)
                assert(not ok and tostring(err):find('ready reached', 1, true), tostring(err))
            end
        """)

    def test_ammo_lookup_can_become_unavailable_between_weapon_setup_calls(self):
        self.lua.execute("""
            local data = {}
            local weapon = {
                isAimedFirearm=function() return true end,
                getMagazineType=function() return nil end,
                getType=function() return 'TestGun' end,
            }
            local inventory = {AddItem=function() return weapon end}
            local ss = setmetatable({player={getInventory=function() return inventory end,
                getModData=function() return data end},
                setGunWep=function() end, setMeleeWep=function() end}, SuperSurvivor)
            isModEnabled=function() return false end
            MeleeWeapons={'Base.Axe'}
            local lookups = 0
            getAmmoBullets=function()
                lookups=lookups+1
                if lookups==1 then return {'Base.TestAmmo'} end
                return nil
            end
            getAmmoBox=function() return nil end
            ss:giveWeapon('Base.TestGun', false)
            assert(lookups==2 and data.ammoCount==0)
        """)

    def prepare_combat(self):
        self.lua.execute("""
            local noop = function() end
            requests, pending, active, running = 0, false, false, false
            ready, canAttack, inRange, ranged, acceptAttack = true, true, true, false, true
            local data = {bWalking = true, Running = true}
            player = {setPath2 = noop, getModData = function() return data end,
                isRunning = function() return running end,
                setRunning = function(_, value) running = value end,
                setSneaking = noop, setJustMoved = noop, StopAllActionQueue = noop,
                setInitiateAttack = function(_, value) pending = value end,
                setAttackTargetSquare = function(_, value) targetSquare = value end,
                setIsAiming = function(_, value) aiming = value end,
                faceThisObject = function(_, value) faced = value end,
                isAttackStarted = function() return active end,
                isInitiateAttack = function() return pending end,
                pressedAttack = function()
                    requests = requests + 1
                    pending, active = acceptAttack, acceptAttack
                end}
            targetSquare = {}
            victim = {kind = 'IsoZombie', isDead = function() return false end,
                      getCurrentSquare = function() return victimSquare end}
            victimSquare = {}
            ss = setmetatable({player = player, AtkTicks = 0, UsingFullAuto = false,
                TriggerHeldDown = true, DebugSay = noop,
                CanAttackAlt = function() return canAttack end,
                isEnemyInRange = function() return inRange end,
                WeaponReady = function() return ready end,
                usingGun = function() return ranged end}, SuperSurvivor)
            ISTimedActionQueue = {clear = noop}
            IsoPlayer = {getCoopPVP = function() return false end}
            function SurvivorTogglePVP() pvpEnabled = true end
        """)

    def test_melee_delegates_once_and_never_applies_manual_damage(self):
        self.prepare_combat()
        self.lua.execute("""
            -- victim deliberately has no Hit method.
            assert(ss:NPC_Attack(victim))
            assert(requests == 1 and faced == victim and targetSquare == victimSquare)
            assert(not aiming and ss.AtkTicks == 2)
            assert(not ss:NPC_Attack(victim) and requests == 1 and ss.AtkTicks == 1)
        """)

    def test_ranged_attack_uses_engine_and_preserves_hostile_pvp(self):
        self.prepare_combat()
        self.lua.execute("""
            victim.kind, ranged, ss.UsingFullAuto = 'IsoPlayer', true, true
            assert(ss:Attack(victim))
            assert(requests == 1 and aiming and pvpEnabled and ss.TriggerHeldDown)
        """)

    def test_attacks_reject_invalid_busy_and_out_of_range_targets(self):
        self.prepare_combat()
        self.lua.execute("""
            assert(not ss:NPC_Attack(nil))
            assert(not ss:NPC_Attack({kind = 'IsoObject'}))
            active = true; assert(not ss:NPC_Attack(victim)); active = false
            running = true; assert(not ss:NPC_Attack(victim)); running = false
            inRange = false; assert(not ss:NPC_Attack(victim)); inRange = true
            canAttack = false; assert(not ss:NPC_Attack(victim)); canAttack = true
            ready = false; assert(not ss:NPC_Attack(victim))
            assert(requests == 0)
        """)

    def test_engine_rejection_and_errors_are_not_reported_as_attacks(self):
        self.prepare_combat()
        self.lua.execute("""
            acceptAttack = false
            assert(not ss:NPC_Attack(victim) and ss.AtkTicks == 0)
            player.pressedAttack = function() error('combat API error') end
            local ok, err = pcall(ss.NPC_Attack, ss, victim)
            assert(not ok and string.find(err, 'combat API error', 1, true))
        """)

    def test_stopping_cancels_pending_intent_without_resetting_active_animation(self):
        self.prepare_combat()
        self.lua.execute("""
            for _, stop in ipairs({ss.StopWalk, ss.iStopMovement}) do
                pending, active, aiming, running = true, true, true, true
                ss.TriggerHeldDown = true
                stop(ss)
                assert(not pending and not aiming and not running)
                assert(targetSquare == nil and not ss.TriggerHeldDown)
                assert(active) -- The engine owns completion of the active attack.
            end
        """)

    def test_swing_event_does_not_consume_npc_ammo_twice(self):
        self.lua.execute("""
            Events = setmetatable({}, {__index = function(t, name)
                local event = {Add = function() end}; rawset(t, name, event); return event
            end})
        """)
        self.lua.execute((CLIENT / '3_Other/SuperSurvivorsMod.lua').read_bytes())
        self.lua.execute("""
            local weapon = {isRanged = function() return true end}
            local localPlayer = false
            local player = {isLocalPlayer = function() return localPlayer end,
                            getModData = function() return {ID = 0} end}
            local survivor = {}
            local reactions = 0
            SSM = {Get = function() return survivor end,
                GunShotHandle = function(_, ss) assert(ss == survivor); reactions = reactions + 1 end}
            -- No ammo/chamber setters are exposed by the stub weapon.
            SuperSurvivorsOnSwing(player, weapon)
            assert(reactions == 0)
            localPlayer = true
            SuperSurvivorsOnSwing(player, weapon)
            assert(reactions == 1)
        """)

    def prepare_water(self):
        self.lua.execute("""
            thirst, available, water, reachable, tainted = 0.6, 2, true, true, true
            queue = {}
            local stats = {get = function(_, stat) assert(stat == CharacterStat.THIRST); return thirst end}
            CharacterStat = {THIRST = {}}
            player = {getStats = function() return stats end}
            source = {getSquare = function() return {} end,
                hasWater = function() return water end,
                getFluidAmount = function() return available end,
                isTaintedWater = function() return tainted end}
            ss = setmetatable({player = player, Speak = function() end}, SuperSurvivor)
            luautils = {walkAdjObject = function(_, object, a, b)
                assert(object == source and a and b); return reachable
            end}
            ISTimedActionQueue = {add = function(action) table.insert(queue, action) end}
            package.preload['TimedActions/ISTakeWaterAction'] = function() end
            ISTakeWaterAction = {new = function(_, ...)
                assert(select('#', ...) == 4)
                local character, item, object, isTainted = ...
                assert(character == player and item == nil and object == source)
                assert(isTainted == tainted)
                return {waterObject = object}
            end}
        """)

    def test_drinking_queues_b42_action_without_consuming_at_queue_time(self):
        self.prepare_water()
        self.lua.execute("""
            assert(ss:DrinkFromObject(source) and #queue == 1)
            assert(thirst == 0.6 and available == 2)
        """)

    def test_drinking_rejects_empty_nonwater_unreachable_or_unneeded_sources(self):
        self.prepare_water()
        self.lua.execute("""
            assert(not ss:DrinkFromObject(nil))
            available = 0; assert(not ss:DrinkFromObject(source)); available = 2
            water = false; assert(not ss:DrinkFromObject(source)); water = true
            reachable = false; assert(not ss:DrinkFromObject(source)); reachable = true
            thirst = 0; assert(not ss:DrinkFromObject(source))
            assert(#queue == 0)
        """)

    def test_wash_water_search_uses_fluid_volume(self):
        self.prepare_water()
        self.lua.execute("""
            available, tainted = 9999, false
            player.getX = function() return 10 end
            player.getY = function() return 20 end
            player.getZ = function() return 0 end
            source.getContainer = function() return nil end
            local square = {getObjects = function() return list({source}) end,
                            getRoom = function() return nil end}
            function getCell() return {getGridSquare = function(_, _, _, z)
                return z == 0 and square or nil
            end} end
            SpiralSearch = {new = function() return {
                forMax = function() return 0 end,
                getX = function() return 10 end, getY = function() return 20 end,
                next = function() end} end}
            ss.GoFindThisCounter = 0
            assert(ss:FindThisNearBy('WashWater', 'Category') == source)
        """)

    def test_washing_reserves_shared_water_and_soap_with_b42_signatures(self):
        self.lua.execute((CLIENT / '7_Tasks/WashSelfTask.lua').read_bytes())
        self.lua.execute("""
            local cloth = {kind = 'Clothing', getBloodClothingType = function() return {} end,
                           getDirtiness = function() return 10 end}
            local inv = {getSoapList = function(_, filter, recursive)
                assert(filter == nil and recursive); return list({{}})
            end, getItems = function() return list({cloth, cloth}) end}
            player = {getInventory = function() return inv end}
            source = {kind = 'IsoObject', hasWater = function() return true end,
                      getFluidAmount = function() return 6 end}
            luautils = {walkAdjObject = function() return true end}
            BloodClothingType = {getCoveredParts = function() return list({}) end}
            package.preload['TimedActions/ISWashYourself'] = function() end
            package.preload['TimedActions/ISWashClothing'] = function() end
            ISWashYourself = {GetRequiredWater = function() return 2 end,
                GetRequiredSoap = function() return 1 end,
                new = function(_, ...)
                    assert(select('#', ...) == 2)
                    local character, object = ...
                    assert(character == player and object == source)
                    return {kind = 'self'}
                end}
            ISWashClothing = {GetSoapRemaining = function(soaps) return soaps:size() end,
                GetRequiredWater = function() return 4 end,
                GetRequiredSoap = function() return 1 end,
                new = function(_, ...)
                    assert(select('#', ...) == 6)
                    local character, object, item, blood, dirt, noSoap = ...
                    assert(character == player and object == source and item == cloth)
                    assert(blood == 0 and dirt == 10 and noSoap)
                    return {kind = 'clothing'}
                end}
            queue = {}
            ISTimedActionQueue = {add = function(action) table.insert(queue, action) end}
            local task = setmetatable({parent = {player = player}, TargetItem = source}, WashSelfTask)
            assert(task:queueWashActions())
            assert(#queue == 2 and queue[1].kind == 'self' and queue[2].kind == 'clothing')
            -- Exactly six liters reserved; the second cloth is not queued.
            assert(source:getFluidAmount() == 6)
        """)

    @unittest.skipUnless(GAME, 'Set PZ_GAME_DIR to test the installed vanilla water action')
    def test_installed_vanilla_water_action_consumes_once_and_preserves_fluid(self):
        self.prepare_water()
        self.lua.execute("""
            ISBaseTimedAction = {derive = function(self)
                local cls = {}; cls.__index = cls
                return setmetatable(cls, {__index = self})
            end, new = function(self, character)
                return setmetatable({character = character}, {__index = self})
            end}
            package.preload['TimedActions/ISBaseTimedAction'] = function() end
            player.isTimedActionInstant = function() return false end
            player.DrinkFluid = function(_, fluid, fraction)
                assert(fluid.tainted and fraction == 1)
                thirst = thirst - fluid.amount / 2
            end
            source.moveFluidToTemporaryContainer = function(_, amount)
                local taken = math.min(amount, available)
                available = available - taken
                return {amount = taken, tainted = tainted}
            end
            FluidContainer = {DisposeContainer = function() disposed = true end}
        """)
        vanilla = Path(GAME) / 'media/lua/shared/TimedActions/ISTakeWaterAction.lua'
        self.lua.execute(vanilla.read_bytes())
        self.lua.execute("""
            assert(ss:DrinkFromObject(source))
            local action = queue[1]
            assert(action.waterUnit == 1.2 and action.maxTime == 135)
            action:updateUse(0.5)
            assert(math.abs(thirst - 0.3) < 0.00001)
            assert(action:complete() and disposed)
            assert(math.abs(thirst) < 0.00001 and math.abs(available - 0.8) < 0.00001)
            action:complete()
            assert(math.abs(available - 0.8) < 0.00001)
            -- A nearly empty source caps consumption rather than inventing water.
            thirst, available = 0.6, 0.25
            assert(ss:DrinkFromObject(source))
            assert(queue[2]:complete())
            assert(available == 0 and math.abs(thirst - 0.475) < 0.00001)
        """)

    @unittest.skipUnless(GAME, 'Set PZ_GAME_DIR to test installed vanilla wash actions')
    def test_installed_vanilla_wash_constructors_accept_the_queued_arguments(self):
        self.lua.execute("""
            ISBaseTimedAction = {derive = function(self)
                local cls = {}; cls.__index = cls
                return setmetatable(cls, {__index = self})
            end, new = function(self, character)
                return setmetatable({character = character}, {__index = self})
            end}
            package.preload['TimedActions/ISBaseTimedAction'] = function() end
            package.preload['TimedActions/ISWashYourself'] = function() end
            package.preload['TimedActions/ISWashClothing'] = function() end
            local part = {}
            BloodBodyPartType = {MAX = {index = function() return 1 end},
                                FromIndex = function() return part end}
            BloodClothingType = {getCoveredParts = function() return list({part}) end}
            Math = {ceil = math.ceil}
            local soap = {kind = 'DrainableComboItem', getCurrentUses = function() return 2 end}
            cloth = {kind = 'Clothing', getBloodClothingType = function() return {} end,
                     getDirtiness = function() return 10 end,
                     getDirt = function() return 0.3 end, getBlood = function() return 0 end}
            local inv = {getSoapList = function() return list({soap}) end,
                         getItems = function() return list({cloth, cloth}) end}
            player = {isTimedActionInstant = function() return true end,
                getInventory = function() return inv end,
                getHumanVisual = function() return {getBlood = function() return 0.2 end,
                                                   getDirt = function() return 0 end} end}
            source = {kind = 'IsoObject', hasWater = function() return true end,
                      getFluidAmount = function() return 6 end}
            luautils = {walkAdjObject = function() return true end}
            queue = {}
            ISTimedActionQueue = {add = function(action) table.insert(queue, action) end}
        """)
        for filename in ('ISWashClothing.lua', 'ISWashYourself.lua'):
            self.lua.execute((Path(GAME) / 'media/lua/shared/TimedActions' / filename).read_bytes())
        self.lua.execute((CLIENT / '7_Tasks/WashSelfTask.lua').read_bytes())
        self.lua.execute("""
            local task = setmetatable({parent = {player = player}, TargetItem = source}, WashSelfTask)
            assert(task:queueWashActions() and #queue == 2)
            assert(queue[1].sink == source and queue[1].character == player)
            assert(queue[2].sink == source and queue[2].item == cloth and not queue[2].noSoap)
            assert(queue[2].bloodAmount == 0 and queue[2].dirtAmount == 10)
        """)


if __name__ == '__main__':
    unittest.main()
