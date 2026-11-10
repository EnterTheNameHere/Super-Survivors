WashSelfTask = {}
WashSelfTask.__index = WashSelfTask

-- Use B42's vanilla actions and reserve water/soap for the whole queued batch.
-- Actions consume and synchronize resources when they execute, not here.
function WashSelfTask:queueWashActions()
    local player = self.parent.player
    local source = self.TargetItem
    if not source or not instanceof(source, "IsoObject") or not source:hasWater() or
       source:getFluidAmount() <= 0 then return false end
    if not luautils.walkAdjObject(player, source, true, true) then return false end
    require "TimedActions/ISWashYourself"
    require "TimedActions/ISWashClothing"
    local inv = player:getInventory()
    local soaps = inv:getSoapList(nil, true)
    local soapRemaining = ISWashClothing.GetSoapRemaining(soaps)
    local waterRemaining = source:getFluidAmount()
    local queued = false
    local selfWater = math.min(ISWashYourself.GetRequiredWater(player), waterRemaining)
    if selfWater > 0 then
        ISTimedActionQueue.add(ISWashYourself:new(player, source))
        waterRemaining = waterRemaining - selfWater
        soapRemaining = math.max(0, soapRemaining - ISWashYourself.GetRequiredSoap(player))
        queued = true
    end
    local items = inv:getItems()
    for i = 0, items:size() - 1 do
        local item = items:get(i)
        local blood, dirt = 0, 0
        if instanceof(item, "Clothing") then
            local parts = BloodClothingType.getCoveredParts(item:getBloodClothingType())
            if parts then
                for j = 0, parts:size() - 1 do blood = blood + item:getBlood(parts:get(j)) end
            end
            dirt = item:getDirtiness()
        elseif instanceof(item, "HandWeapon") then
            blood = item:getBloodLevel()
        end
        if blood > 0 or dirt > 0 then
            local waterRequired = ISWashClothing.GetRequiredWater(item)
            if waterRemaining >= waterRequired then
                local noSoap = soapRemaining <= 0
                ISTimedActionQueue.add(ISWashClothing:new(player, source, item, blood, dirt, noSoap))
                waterRemaining = waterRemaining - waterRequired
                soapRemaining = math.max(0, soapRemaining - ISWashClothing.GetRequiredSoap(item))
                queued = true
            end
        end
    end
    return queued
end

function WashSelfTask:new(superSurvivor)

	local o = {}
	setmetatable(o, self)
	self.__index = self
	
	if(superSurvivor == nil) then return nil end
	o.parent = superSurvivor
	o.Name = "Wash Self"
	o.OnGoing = false
	
	if(not superSurvivor.player:getCurrentSquare()) then
		o.Complete = true
		return nil 
	end
	o.TargetItem = nil
	o.Complete = false
	o.WasSuccessful = false
	
	o.parent:DebugSay(tostring(o.parent:getCurrentTask()).." Started!" )
	superSurvivor:RoleplaySpeak(getActionText("LookForItem_Before").."Wash Water"..getActionText("LookForItem_After"))
	return o

end

function WashSelfTask:isComplete()
	return self.Complete
end

function WashSelfTask:isValid()
	return true 
end

function WashSelfTask:getWasSuccessful()
	return self.WasSuccessful
end

function WashSelfTask:update()

	if(getSpecificPlayer(0):isAsleep()) then return false end
	if(not self:isValid()) or self.parent:getDangerSeenCount() > 0 then
		--self.parent:Speak("completing")
		self.Complete = true
		return false 
	end
	
	if(self.parent:isInAction()) then
		--self.parent:Speak("waiting for non action")
		return false 
	end
	
	
	if(self.TargetItem == nil) then 
		--print("going to WashSelfNearBy:"..self.itemtype)
		self.TargetItem = self.parent:FindThisNearBy("WashWater", "Category")
	end
	
	if(self.TargetItem == nil) then
		self.Complete = true
		if(self.WasSuccessful == false) then 
			self.parent:RoleplaySpeak(getActionText("NoFindItem_Before").."Wash Water"..getActionText("NoFindItem_After")) 
		end
		return false
	end
	
	
	local distance, targetSquare
	if(instanceof(self.TargetItem,"InventoryItem")) and (self.TargetItem:getWorldItem() ~= nil) then 
		targetSquare = self.TargetItem:getWorldItem():getSquare() 
	elseif(instanceof(self.TargetItem,"IsoObject")) and (self.TargetItem:getSquare() ~= nil) then 
		targetSquare = self.TargetItem:getSquare() 
	elseif(instanceof(self.TargetItem,"InventoryItem")) and (self.TargetItem:getContainer() ~= nil) then 
		targetSquare = self.TargetItem:getContainer():getSourceGrid() 
	end
	
	if(not targetSquare) then
		print("error cannot locate location of returned item")
		--self.Complete = true
		self.TargetItem = nil
		self.Complete = true
		return false
	else
		--self.parent:Speak("here i am")
		distance = getDistanceBetween(targetSquare,self.parent:Get())
		
		if(distance > 2.0) then 
			self.parent:walkTo(targetSquare)
		else
            self.WasSuccessful = self:queueWashActions()
            self.Complete = true
		end
		
	end		
	
end
