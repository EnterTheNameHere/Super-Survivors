"""Actual installed clothing actions retain timing and change gear only on complete."""
import os
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]
GAME = os.environ.get('PZ_GAME_DIR')


@unittest.skipUnless(GAME, 'Set PZ_GAME_DIR to exercise installed clothing actions')
class ClothingChecks(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute('''
            function getText(key) return key end
            function isClient() return false end
            function isServer() return false end
            function instanceof() return false end
            function getPlayerHotbar() return nil end
            function triggerEvent() end
            function sendEquip() end
            function isForceDropHeavyItem() return false end
            ItemBodyLocation=setmetatable({}, {__index=function(t,k) rawset(t,k,k);return k end})
            ItemTag={WEARABLE={},REPLACE_PRIMARY={}}
            ISInventoryPage={}
            local noop=function() end
            ISBaseTimedAction={derive=function(self) local c={};c.__index=c;return setmetatable(c,{__index=self}) end,
                new=function(self,chr) return setmetatable({character=chr},{__index=self}) end,
                setActionAnim=function(_,anim) animation=anim end,setAnimVariable=noop,setOverrideHandModels=noop,
                getJobDelta=function() return .4 end,stop=function() stopped=true end,perform=noop}
            package.preload['TimedActions/ISBaseTimedAction']=noop
            package.preload['TimedActions/ISWearClothing']=noop
            package.preload['TimedActions/ISUnequipAction']=noop
            package.preload['0_Utilities/SuperSurvivorClothingUtilities']=noop
            present=true;worn=false
            inv={contains=function() return present end,setDrawDirty=noop}
            item={IsClothing=function() return true end,IsInventoryContainer=function() return false end,
                isBroken=function() return false end,getBodyLocation=function() return ItemBodyLocation.JACKET end,
                getClothingItem=function() return {} end,
                hasTag=function() return false end,canBeEquipped=function() return '' end,
                getCategory=function() return 'Clothing' end,getName=function() return 'Jacket' end,
                getEquipSound=function() return nil end,getUnequipSound=function() return nil end,
                setJobType=noop,setJobDelta=function(_,v) delta=v end,getJobDelta=function() return delta or 0 end,
                canBeActivated=function() return false end,getContainer=function() return inv end}
            character={isDead=function() return false end,getInventory=function() return inv end,
                isEquipped=function() return worn end,getWornItem=function() if worn then return item end end,
                getWornItems=function() return {contains=function() return worn end} end,
                getPrimaryHandItem=function() end,getSecondaryHandItem=function() end,
                isTimedActionInstant=function() return false end,
                reportEvent=function(_,e) event=e end,playSound=function() return 1 end,
                getEmitter=function() return {isPlaying=function() return false end,stopSound=noop} end,
                getPlayerNum=function() return 0 end,
                getHumanVisual=function() return {getHairModel=function() return {contains=function() return false end} end} end,
                setWornItem=function(_,slot,i) assert(slot==ItemBodyLocation.JACKET and i==item);worn=true end,
                removeWornItem=function(_,i) assert(i==item);worn=false end}
            nativeQueue={queue={}}
            ISTimedActionQueue={queues={[character]=nativeQueue},add=function(a) table.insert(nativeQueue.queue,a) end,
                clear=function() for _,a in ipairs(nativeQueue.queue) do a:stop() end;nativeQueue.queue={} end}
        ''')
        game = Path(GAME) / 'media/lua/shared/TimedActions'
        for name in ('ISWearClothing.lua', 'ISUnequipAction.lua'):
            self.lua.execute((game / name).read_bytes())
        self.lua.execute((ROOT / '42/media/lua/client/0_Utilities/SuperSurvivorClothingUtilities.lua').read_bytes())

    def test_wear_progress_and_cancel_do_not_equip(self):
        self.lua.execute('''
            local a=SuperSurvivorClothing.queue(character,item,true)
            assert(a.maxTime==50 and not worn)
            a:start();a:update()
            assert(animation=='WearClothing' and event=='EventWearClothing' and delta==.4 and not worn)
            assert(SuperSurvivorClothing.cancel(character))
            assert(stopped and delta==0 and not worn and #nativeQueue.queue==0)
        ''')

    def test_equipment_changes_only_on_vanilla_complete(self):
        self.lua.execute('''
            local a=SuperSurvivorClothing.queue(character,item,true)
            a:start();assert(not worn);assert(a:complete() and worn)
            nativeQueue.queue={}
            local b=SuperSurvivorClothing.queue(character,item,false)
            assert(b.maxTime==50 and b.fromHotbar==false and b.hotbar==nil)
            b:start();b:update();assert(worn)
            assert(b:complete() and not worn)
        ''')

    def test_missing_item_and_duplicate_clothing_commands_are_rejected(self):
        self.lua.execute('''
            present=false;assert(not SuperSurvivorClothing.queue(character,item,true))
            present=true;assert(SuperSurvivorClothing.queue(character,item,true))
            assert(not SuperSurvivorClothing.queue(character,item,true))
            assert(#nativeQueue.queue==1)
        ''')

    def test_nonwearable_container_cannot_be_equipped_as_clothing(self):
        self.lua.execute('''
            item.IsClothing=function() return false end
            item.IsInventoryContainer=function() return true end
            item.canBeEquipped=function() return nil end
            item.getBodyLocation=function() return nil end
            assert(not SuperSurvivorClothing.queue(character,item,true))
            assert(#nativeQueue.queue==0)
        ''')

    def test_loadout_row_displays_native_progress_and_cancels_on_click(self):
        self.lua.execute('''
            Node={derive=function(self) local c={};c.__index=c;return setmetatable(c,{__index=self}) end,
                new=function(self) return setmetatable({},{__index=self}) end}
            ISPanel=Node;ISButton=Node
        ''')
        source = (ROOT / '42/media/lua/client/5_UI/SuperSurvivorLoadout.lua').read_text()
        self.lua.globals().Row = self.lua.execute(source + '\nreturn InventoryRow')
        self.lua.execute('''
            local a=SuperSurvivorClothing.queue(character,item,true)
            a.action={};a:start();a:update()
            local row=setmetatable({member={player=character},item=item,direction='^',
                actionButton={setTitle=function(_,s) title=s end}},Row)
            row:update();assert(string.find(title,'40%%') and string.find(title,'Cancel'))
            row:on_click_transfer('^');assert(not worn and #nativeQueue.queue==0)
            row:update();assert(title=='ContextMenu_Wear')
        ''')
