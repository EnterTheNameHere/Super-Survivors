"""Dropping uses the current offset helper and never moves invalid items."""
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime


class DropChecks(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute('''
            package.preload['TimedActions/ISBaseTimedAction']=function() end
            package.preload['TimedActions/ISTransferAction']=function() end
            ISBaseTimedAction={derive=function(self) local c={};c.__index=c;return setmetatable(c,{__index=self}) end,
                perform=function() advanced=true end,stop=function() stopped=true end}
            ISInventoryTransferAction={} -- old helper is intentionally unavailable
            ISInventoryPage={}
            present=true; loaded=true
            inventory={contains=function() return present end,setDrawDirty=function() end,
                Remove=function(_,i) assert(i==item);present=false end}
            item={getContainer=function() return inventory end,setJobDelta=function(_,v) delta=v end}
            square={AddWorldInventoryItem=function(_,i,x,y,z)
                assert(i==item and x==.2 and y==.3 and z==0);drops=(drops or 0)+1 end}
            character={getInventory=function() return inventory end,getCurrentSquare=function() if loaded then return square end end}
            ISTransferAction={GetDropItemOffset=function(c,s,i) assert(c==character and s==square and i==item);return .2,.3,0 end}
        ''')
        path = Path(__file__).resolve().parents[1] / '42/media/lua/client/TimedActions/ISDropItemAction.lua'
        self.lua.execute(path.read_bytes())

    def test_drop_moves_one_item_with_current_vanilla_offset_helper(self):
        self.lua.execute('''
            local action=ISDropItemAction:new(character,item,30)
            action:perform()
            assert(drops==1 and not present and advanced and delta==0)
            action:perform();assert(drops==1)
        ''')

    def test_unloaded_square_finishes_without_losing_item(self):
        self.lua.execute('''
            local action=ISDropItemAction:new(character,item,30)
            loaded=false;action:perform()
            assert(present and not drops and advanced)
        ''')

    def test_cancellation_keeps_item_in_inventory(self):
        self.lua.execute('''
            local action=ISDropItemAction:new(character,item,30)
            action:stop()
            assert(stopped and present and not drops and not advanced and delta==0)
        ''')
