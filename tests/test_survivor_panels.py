"""Direct panel navigation preserves survivor identity without the main window."""
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime

CLIENT = Path(__file__).resolve().parents[1] / '42/media/lua/client'


class PanelNavigationChecks(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute('''
            Node={derive=function(self) local c={};c.__index=c;return setmetatable(c,{__index=self}) end,
                new=function(self,x,y,w,h) return setmetatable({x=x,y=y,width=w,height=h},{__index=self}) end,
                addToUIManager=function(self) self.open=true end,
                removeFromUIManager=function(self) self.closed=true end,
                setVisible=function(self,v) self.visible=v end}
            ISPanel=Node;ISButton=Node
            function getCore() return {getScreenWidth=function() return 1920 end,getScreenHeight=function() return 1080 end} end
            a={getID=function() return 11 end,player={isDead=function() return false end}}
            b={getID=function() return 22 end,player={isDead=function() return false end}}
            members={a,b}
            SSM={Get=function() return {getGroupID=function() return 3 end} end}
            SSGM={Get=function(_,id) assert(id==3);return {getMembers=function() return members end} end}
            package.preload['0_Utilities/SuperSurvivorPanelUtilities']=function() end
            package.preload['5_UI/SuperSurvivorInventory']=function() end
            package.preload['5_UI/SuperSurvivorLoadout']=function() end
        ''')
        for path in ('0_Utilities/SuperSurvivorPanelUtilities.lua', '5_UI/SuperSurvivorInventory.lua', '5_UI/SuperSurvivorLoadout.lua'):
            self.lua.execute((CLIENT / path).read_bytes())

    def test_direct_open_and_switch_keep_survivor_and_position(self):
        self.lua.execute('''
            assert(window_super_survivors==nil)
            local inventory=SuperSurvivorPanels.open('inventory',22)
            assert(inventory.open and inventory.member_index==2 and inventory.visible)
            local x,y=inventory.x,inventory.y
            members={b,a}
            local equipment=SuperSurvivorPanels.open('equipment',22,inventory)
            assert(equipment.member_index==1 and inventory.closed)
            assert(equipment.x==x and equipment.y==y)
            local again=SuperSurvivorPanels.open('inventory',22,equipment)
            assert(again.member_index==1 and equipment.closed)
        ''')

    def test_missing_or_dead_member_does_not_close_current_panel(self):
        self.lua.execute('''
            local previous=Node:new(10,10,426,381)
            assert(not SuperSurvivorPanels.open('equipment',99,previous))
            b.player.isDead=function() return true end
            assert(not SuperSurvivorPanels.open('inventory',22,previous))
            assert(not previous.closed)
        ''')

    def test_position_is_clamped_to_the_screen(self):
        self.lua.execute('''
            local x,y=SuperSurvivorPanels.position(950,290,1800,1000)
            assert(x==970 and y==790)
        ''')

    def test_context_menu_factory_is_not_called_without_player_ui_data(self):
        self.lua.execute('''
            getPlayerContextMenu=function() return nil end
            ISContextMenu={get=function() error('factory must not run') end}
            assert(SuperSurvivorPanels.contextMenu(0,10,20)==nil)
            local menu={}
            getPlayerContextMenu=function(index) assert(index==0);return menu end
            ISContextMenu.get=function(index,x,y)
                assert(index==0 and x==10 and y==20);return menu
            end
            assert(SuperSurvivorPanels.contextMenu(0,10,20)==menu)
        ''')

    def test_inventory_transfer_does_not_start_without_local_player(self):
        row = self.lua.execute((CLIENT / '5_UI/SuperSurvivorInventory.lua').read_text() + '\nreturn InventoryRow')
        self.lua.globals().Row = row
        self.lua.execute('''
            getSpecificPlayer=function() return nil end
            getDistanceBetween=function() error('must not use missing player') end
            local row=setmetatable({member_index=1,item={}},Row)
            row:on_click_transfer('>')
            row:on_click_transfer('<')
        ''')
