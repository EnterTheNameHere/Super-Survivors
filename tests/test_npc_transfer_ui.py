"""Installed vanilla transfers must not use a human loot panel for NPC actors."""
import os
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]
GAME = os.environ.get('PZ_GAME_DIR')
HELPER = ROOT / '42/media/lua/client/0_Utilities/SuperSurvivorTransferUtilities.lua'


@unittest.skipUnless(GAME, 'Set PZ_GAME_DIR to exercise installed transfer action methods')
class NpcTransferUiChecks(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute("""
            package.preload['TimedActions/ISBaseTimedAction'] = function() end
            ISInventoryPage = {}
            ISBaseTimedAction = {
                derive = function(self)
                    local c={};c.__index=c;return setmetatable(c,{__index=self})
                end,
                perform = function() completions=completions+1 end,
            }
            isClient=function() return false end
            instanceof=function() return false end
            CharacterTrait={DESENSITIZED={},HEMOPHOBIC={}}
            Metabolics={LightWork={}}
            calls, selections, facing, completions, moved, callbacks, upstream = 0,0,0,0,0,0,0
            loot=nil
            getPlayerLoot=function(index) assert(index==0);calls=calls+1;return loot end
            parent={}
            source={getParent=function() return parent end,
                contains=function(_,item) return item.owner==source end}
            destination={}
            item={owner=source,setJobDelta=function(_,value) progress=value end}
            local function actor(npc,localPlayer)
                return {isNpc=function() return npc end,
                    isLocalPlayer=function() return localPlayer end,
                    hasTrait=function(_,trait) return trait==CharacterTrait.DESENSITIZED end,
                    isSittingOnFurniture=function() return false end,
                    faceThisObject=function(_,object) assert(object==parent);facing=facing+1 end,
                    shouldBeTurning=function() return true end,
                    getPlayerNum=function() return 0 end,
                    setMetabolicTarget=function(_,target) assert(target==Metabolics.LightWork) end}
            end
            npc,player=actor(true,false),actor(false,true)
            function makeAction(character)
                item.owner=source
                return setmetatable({character=character,item=item,srcContainer=source,
                    destContainer=destination,selectedContainer=source,started=true,
                    queueList={{items={item}}},
                    action={getJobDelta=function() return .4 end,
                        stopTimedActionAnim=function() end,setLoopedAction=function() end},
                    checkQueueList=function() end,isValid=function() return true end,
                    transferItem=function(_,value)
                        assert(value.owner==source);value.owner=destination;moved=moved+1
                    end,
                    playTransferCompleteSound=function() end,
                    playSourceContainerCloseSound=function() end,
                    playDestContainerCloseSound=function() end,
                    stopLoopingSound=function() end,
                    onCompleteFunc=function() callbacks=callbacks+1 end,
                    onCompleteArgs={},
                },ISInventoryTransferAction)
            end
        """)
        vanilla = Path(GAME) / 'media/lua/client/TimedActions/ISInventoryTransferAction.lua'
        self.lua.execute(vanilla.read_text())
        self.lua.execute("""
            package.preload['TimedActions/ISInventoryTransferAction']=function() end
            local vanillaPerform=ISInventoryTransferAction.perform
            -- Model the already-installed theft hook or another chained hook.
            ISInventoryTransferAction.perform=function(self)
                upstream=upstream+1
                return vanillaPerform(self)
            end
        """)

    def install(self):
        self.lua.execute(HELPER.read_text())

    def test_missing_dead_player_ui_reproduces_and_npc_update_preserves_progress(self):
        self.lua.execute("""
            a=makeAction(npc)
            local ok,err=pcall(function() a:update() end)
            assert(not ok and tostring(err):find('nil',1,true))
            calls,facing=0,0
        """)
        self.install()
        self.lua.execute("""
            a:update();a:update()
            assert(calls==0 and facing==2 and progress==.4)
            assert(a.selectedContainer==nil and item.owner==source and moved==0)
            a:perform()
            assert(calls==0 and item.owner==destination and moved==1)
            assert(callbacks==1 and completions==1 and upstream==1 and not a.started)
        """)

    def test_human_transfer_keeps_vanilla_loot_panel_behavior(self):
        self.install()
        self.lua.execute("""
            loot={setForceSelectedContainer=function(_,container) assert(container==source) end,
                selectButtonForContainer=function(_,container)
                    assert(container==source);selections=selections+1
                end}
            local a=makeAction(player)
            a:update()
            assert(a.selectedContainer==source and selections==1 and calls==2)
            a:perform()
            assert(selections==2 and calls==3 and moved==1 and completions==1)
        """)

    def test_hot_reload_keeps_one_upstream_call_and_handles_an_existing_action(self):
        self.lua.execute('a=makeAction(npc)')
        self.install()
        self.install()
        self.lua.execute("""
            a:update()
            a:perform()
            assert(calls==0 and moved==1 and completions==1 and callbacks==1 and upstream==1)
        """)


if __name__ == '__main__':
    unittest.main()
