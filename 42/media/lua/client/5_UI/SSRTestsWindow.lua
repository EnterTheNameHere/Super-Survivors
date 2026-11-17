require "ISUI/ISCollapsableWindow"
require "ISUI/ISRichTextPanel"
require "ISUI/ISComboBox"
require "ISUI/ISTickBox"
require "Testing/SSRTests"
require "Testing/SSRPersistenceTest"

local T = SSRTests
SSRTestsWindow = ISCollapsableWindow:derive("SSRTestsWindow")
local Window = SSRTestsWindow

local function rich(text)
    return tostring(text):gsub("<","["):gsub(">","]"):gsub("\n"," <LINE> ")
end
local function panel(owner,x,y,w,h,scroll)
    local child = ISRichTextPanel:new(x,y,w,h)
    child:initialise()
    child.autosetheight = not scroll
    child.clip = scroll
    child.defaultFont = UIFont.Small
    child.marginLeft,child.marginRight,child.marginTop,child.marginBottom=6,16,6,6
    if scroll then child:addScrollBars() end
    owner:addChild(child)
    return child
end
function Window:new(x,y,w,h)
    local o = ISCollapsableWindow.new(self,x,y,w,h)
    o.title = getText("UI_SS_Tests_Title")
    o.resizable = false
    o.pin = true
    o.backgroundColor = {r=0.08,g=0.08,b=0.08,a=0.95}
    return o
end
function Window:createChildren()
    ISCollapsableWindow.createChildren(self)
    local row = getTextManager():getFontHeight(UIFont.Small)+10
    self.warning = panel(self,10,25,self.width-20,100,false)
    self.warning:setText("<RGB:1,0.55,0.25> "..rich(T.WARNING):gsub(" <LINE> "," <LINE> <RGB:1,1,1> ",1))
    self.warning:paginate()
    local y = self.warning:getBottom()+8
    self.selector = ISComboBox:new(10,y,self.width-20,row,self,self.onSelection)
    self.selector:initialise()
    self:addChild(self.selector)
    y=y+row+6
    local detailsHeight=math.max(100,math.floor(self.height*0.25))
    self.details=panel(self,10,y,self.width-20,detailsHeight,true)
    y=y+detailsHeight+6
    self.consent=ISTickBox:new(10,y,self.width-20,row,"",self,self.onConsent)
    self.consent:initialise()
    self.consent:addOption(getText("UI_SS_Tests_Consent"))
    self:addChild(self.consent)
    y=y+row+6
    local buttonWidth=(self.width-30)/2
    self.runButton=ISButton:new(10,y,buttonWidth,row,getText("UI_SS_Tests_Run"),self,self.onRun)
    self.runButton:initialise();self:addChild(self.runButton)
    self.cancelButton=ISButton:new(20+buttonWidth,y,buttonWidth,row,getText("UI_SS_Tests_Cancel"),self,self.onCancel)
    self.cancelButton:initialise();self:addChild(self.cancelButton)
    y=y+row+6
    self.output=panel(self,10,y,self.width-20,math.max(60,self.height-y-15),true)
    self:refreshRegistry()
end
function Window:resetConsent()
    if self.consent then self.consent:setSelected(1,false) end
end
function Window:refreshRegistry()
    local previous=self.tests and self.tests[self.selector.selected]
    self.tests=T.list()
    self.selector:clear()
    for index,definition in ipairs(self.tests) do
        self.selector:addOption(definition.title)
        if previous and previous.id==definition.id then self.selector.selected=index end
    end
    if #self.tests==0 then self.selector:addOption(getText("UI_SS_Tests_None")) end
    self.seenDefinitions=T.definitionRevision
    self:onSelection()
end
function Window:onSelection()
    self.notice=nil
    self.seenRevision=nil
end
function Window:onConsent() self.seenRevision=nil end
function Window:onRun()
    local definition=self.tests[self.selector.selected]
    local consent=self.consent:isSelected(1)
    self:resetConsent() -- Every attempted new run consumes that acknowledgment.
    local ok,reason=T.start(definition and definition.id,consent)
    self.notice=not ok and reason or nil
    self.seenRevision=nil
end
function Window:onCancel()
    T.cancel("Cancelled by user; world restoration is not guaranteed.")
    self:resetConsent()
end
function Window:close()
    self:onCancel()
    ISCollapsableWindow.close(self)
end
function Window:update()
    ISCollapsableWindow.update(self)
    if not self.selector then return end
    if not T.enabled() then self:close();return end
    if self.seenDefinitions~=T.definitionRevision then self:refreshRegistry() end
    local definition=self.tests[self.selector.selected]
    local available,reason=T.availability(definition)
    local blocked
    if T.cleanupFailure then blocked="Cleanup failed: restart the game before further tests."
    elseif T.active then blocked="Another test is already running."
    elseif not available then blocked=reason
    elseif not self.consent:isSelected(1) then blocked="Acknowledge the warning to enable Run." end
    self.runButton:setEnable(blocked==nil)
    self.runButton.tooltip=blocked
    self.cancelButton:setEnable(T.active~=nil)
    if self.seenRevision==T.revision and self.seenReason==reason and self.seenBlocked==blocked then return end
    self.seenRevision,self.seenReason,self.seenBlocked=T.revision,reason,blocked
    local text=definition and (definition.description.."\nRequirements: "..(definition.requirements or "None stated")
        .."\nMay modify: "..(definition.risk or "World state").."\nAvailability: "..reason) or reason
    self.details:setText(rich(text));self.details:paginate()
    local result=definition and T.results[definition.id]
    local output=self.notice or "No run yet."
    if result then output=result.status.."\n"..table.concat(result.lines,"\n") end
    if self.notice and result then output=self.notice.."\n"..output end
    if blocked then output="Run disabled: "..blocked.."\n"..output end
    self.output:setText(rich(output));self.output:paginate()
end

function T.openWindow()
    if not T.enabled() or isClient() or isServer() or getNumActivePlayers()~=1 then return nil end
    if not T.window then
        local core=getCore()
        local w,h=math.min(760,core:getScreenWidth()-30),math.min(720,core:getScreenHeight()-60)
        T.window=Window:new((core:getScreenWidth()-w)/2,(core:getScreenHeight()-h)/2,w,h)
        T.window:initialise()
        T.window:addToUIManager()
    end
    T.window:resetConsent()
    T.window:refreshRegistry()
    T.window:setVisible(true)
    T.window:bringToTop()
    return T.window
end
local function menu(player,context,worldObjects,test)
    if player~=0 or not T.enabled() or isClient() or isServer() or getNumActivePlayers()~=1 then return end
    if test then return ISWorldObjectContextMenu.setTest() end
    context:addOption(getText("ContextMenu_SS_Tests"),nil,T.openWindow)
end
if T.menuEntryCallback then Events.OnFillWorldObjectContextMenu.Remove(T.menuEntryCallback) end
T.menuEntryCallback=menu
Events.OnFillWorldObjectContextMenu.Add(menu)
if T.windowStartCallback then Events.OnGameStart.Remove(T.windowStartCallback) end
T.windowStartCallback=function()
    if T.window then
        T.window:close()
        T.window:removeFromUIManager()
        T.window=nil
    end
end
Events.OnGameStart.Add(T.windowStartCallback)
