"""Transfers must wait for unequipping and cannot mutate ownership early."""
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime


class TransferChecks(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute('''
            package.preload['TimedActions/ISInventoryTransferAction']=function() end
            package.preload['TimedActions/ISUnequipAction']=function() end
            owner={isEquipped=function() return true end}; item={isEquipped=function() return true end,IsClothing=function() return false end}
            source={contains=function(_,i) assert(i==item);return true end}
            room=true
            destination={hasRoomFor=function(_,actor,i) assert(actor==owner and i==item);return room end}
            source.getOutermostContainer=function() return source end
            destination.getOutermostContainer=function() return destination end
            source.getParent=function() return owner end
            destination.getParent=function() return owner end
            function instanceof() return true end
            queued={};ISTimedActionQueue={add=function(a) table.insert(queued,a) end}
            ISUnequipAction={new=function(_,actor,i) assert(actor==owner and i==item);return {kind='unequip'} end}
            ISInventoryTransferAction={new=function(_,actor,i,src,dest)
                assert(actor==owner and i==item and src==source and dest==destination)
                return {kind='transfer',character=actor,isValid=function() return true end,
                    setOnComplete=function(self,f) self.callback=f end}
            end}
        ''')
        path = Path(__file__).resolve().parents[1] / '42/media/lua/client/0_Utilities/SuperSurvivorTransferUtilities.lua'
        self.lua.execute(path.read_bytes())

    def test_unequip_is_queued_before_transfer_with_completion_callback(self):
        self.lua.execute('''
            local a=SuperSurvivorTransfers.queue(owner,item,source,destination,function() done=true end)
            assert(#queued==2 and queued[1].kind=='unequip' and queued[2]==a)
            assert(source:contains(item) and not done)
            a.callback(); assert(done)
        ''')

    def test_full_destination_does_not_even_unequip(self):
        self.lua.execute('''
            room=false
            local action,reason,code=SuperSurvivorTransfers.queue(owner,item,source,destination)
            assert(not action and code=='full' and string.find(reason,'no room'))
            assert(#queued==0)
        ''')

    def test_moving_recipient_invalidates_queued_transfer(self):
        self.lua.execute('''
            local square={isBlockedTo=function() return false end}
            owner.getCurrentSquare=function() return square end
            owner.getX=function() return 0 end;owner.getY=function() return 0 end;owner.getZ=function() return 0 end
            distance=1
            local other={getCurrentSquare=function() return square end,getX=function() return distance end,
                getY=function() return 0 end,getZ=function() return 0 end}
            destination.getParent=function() return other end
            local action=SuperSurvivorTransfers.queue(owner,item,source,destination)
            assert(action:isValid())
            distance=5;assert(not action:isValid())
        ''')
