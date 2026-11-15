require "0_Utilities/SuperSurvivorPersistence"

SuperSurvivorManager = {}
SuperSurvivorManager.__index = SuperSurvivorManager

function SuperSurvivorManager:new()

	local o = {}
	setmetatable(o, self)
	self.__index = self
		
	o.SuperSurvivors = {}
	o.SurvivorCount = 0
	o.MainPlayer = 0
	
	return o

end

function SuperSurvivorManager:getRealPlayerID()
	return self.MainPlayer
end

function SuperSurvivorManager:init()
    if not getSpecificPlayer(0) then return end
    if self.SuperSurvivors[0] and self.SuperSurvivors[0]:Get() == getSpecificPlayer(0) then return end
	self.SuperSurvivors[0] = SuperSurvivor:newSet(getSpecificPlayer(0))
	self.SuperSurvivors[0]:setID(0)
    local record = SSPersistence.getRecord(0)
    if record then
        self.SuperSurvivors[0]:setGroupID(record.groupID)
        self.SuperSurvivors[0]:setGroupRole(record.role)
    else self.SuperSurvivors[0]:setGroupID(nil) end
    SSPersistence.observe(self.SuperSurvivors[0])
end
function SuperSurvivorManager:setPlayer(player,ID)
	self.SuperSurvivors[ID] = SuperSurvivor:newSet(player)
	self.SuperSurvivors[0]:setID(ID)
	self.SuperSurvivors[0]:setName("Player " .. tostring(ID))
	
	return self.SuperSurvivors[ID] ;
end

function SuperSurvivorManager:switchPlayer(newID)
	
	self.SuperSurvivors[newID].player:setBlockMovement(false)
	self.SuperSurvivors[newID].player:setNpc(false)
		
	self.SuperSurvivors[self.MainPlayer].player:setBlockMovement(true)
	self.SuperSurvivors[self.MainPlayer].player:setNpc(true)
		
	IsoPlayer.setInstance(self.SuperSurvivors[newID].player)
	IsoPlayer.setLocalPlayer(0,self.SuperSurvivors[newID].player)
	
	self.MainPlayer = newID
	
	getSpecificPlayer(0):initSpritePartsEmpty();
	getPlayerData(0).playerInventory:refreshBackpacks();
	
end

function SuperSurvivorManager:LoadSurvivor(ID, square)

    local record = SSPersistence.getRecord(ID)
    if not record or record.issue or record.state == "dead" or not record.saved or not square then return false end
    local pos = record.saved.position
    if square:getX() ~= math.floor(pos.x) or square:getY() ~= math.floor(pos.y)
        or square:getZ() ~= math.floor(pos.z) then return false end
    if self.SuperSurvivors[ID] then return false end
    local ok, survivor = pcall(SuperSurvivor.newLoad, SuperSurvivor, ID, square)
    if not ok or not survivor or not survivor:Get() then
        local partial = SSPersistence.loading[ID]
        if partial then partial:removeFromWorld(); partial:removeFromSquare() end
        SSPersistence.loading[ID] = nil
        SSPersistence.issue(record, "Native load failed: " .. tostring(survivor))
        return false
    end
    self.SuperSurvivors[ID] = survivor
    SSPersistence.loading[ID] = nil
    survivor:setGroupID(record.groupID)
    survivor:setGroupRole(record.role)
    SSPersistence.runtime[ID] = "loaded"
    record.issue = nil
    survivor:refreshName()
    if survivor:Get():getModData().isHostile == true then survivor:setHostile(true) end
    do

		local meleeWep = self.SuperSurvivors[ID].player:getModData().meleeWeapon
		local gunWep = self.SuperSurvivors[ID].player:getModData().gunWeapon
		if(meleeWep ~= nil) then 
			self.SuperSurvivors[ID].LastMeleeUsed = self.SuperSurvivors[ID].player:getInventory():FindAndReturn(meleeWep)
			if not self.SuperSurvivors[ID].LastMeleeUsed then self.SuperSurvivors[ID].LastMeleeUsed = self.SuperSurvivors[ID]:getBag():FindAndReturn(meleeWep) end
		end		
		if(gunWep ~= nil) then 
			self.SuperSurvivors[ID].LastGunUsed = self.SuperSurvivors[ID].player:getInventory():FindAndReturn(gunWep)
			if not self.SuperSurvivors[ID].LastGunUsed then self.SuperSurvivors[ID].LastGunUsed = self.SuperSurvivors[ID]:getBag():FindAndReturn(gunWep) end
		end
		
		
		if(self.SuperSurvivors[ID]:getAIMode() == "FollowRoute") then
		
			self.SuperSurvivors[ID]:getTaskManager():AddToTop(FollowRouteTask:new(self.SuperSurvivors[ID],0))
			
		elseif(self.SuperSurvivors[ID]:getAIMode() == "Follow") then 
		
			self.SuperSurvivors[ID]:getTaskManager():AddToTop(FollowTask:new(self.SuperSurvivors[ID],nil))
		
		elseif(self.SuperSurvivors[ID]:getAIMode() == "Guard") then 
		
			if self.SuperSurvivors[ID]:getGroup() ~= nil then
				local area = self.SuperSurvivors[ID]:getGroup():getGroupArea("GuardArea")
				if(area) then 		
					self.SuperSurvivors[ID]:getTaskManager():AddToTop(WanderInAreaTask:new(self.SuperSurvivors[ID],area)) 					
					self.SuperSurvivors[ID]:getTaskManager():setTaskUpdateLimit(10)					
				else
					self.SuperSurvivors[ID]:getTaskManager():AddToTop(GuardTask:new(self.SuperSurvivors[ID],self.SuperSurvivors[ID].player:getCurrentSquare()))
				end
			end
			
		elseif(self.SuperSurvivors[ID]:getAIMode() == "Patrol") then 
		
			self.SuperSurvivors[ID]:getTaskManager():AddToTop(PatrolTask:new(self.SuperSurvivors[ID], nil, nil)) 
			
		elseif(self.SuperSurvivors[ID]:getAIMode() == "Wander") then 
		
			self.SuperSurvivors[ID]:getTaskManager():AddToTop(WanderTask:new(self.SuperSurvivors[ID])) 
			
		elseif(self.SuperSurvivors[ID]:getAIMode() == "Stand Ground") then 
		
			self.SuperSurvivors[ID]:getTaskManager():AddToTop(GuardTask:new(self.SuperSurvivors[ID],self.SuperSurvivors[ID].player:getCurrentSquare())) 			
			self.SuperSurvivors[ID]:setWalkingPermitted(false) 
		
		
		elseif(self.SuperSurvivors[ID]:getAIMode() == "Doctor") then 
		
			self.SuperSurvivors[ID]:getTaskManager():AddToTop(DoctorTask:new(self.SuperSurvivors[ID])) 
			
		end
		
			
		local phi = self.SuperSurvivors[ID]:Get():getPrimaryHandItem() -- to trigger onEquipPrimary
		self.SuperSurvivors[ID]:Get():setPrimaryHandItem(nil)
		self.SuperSurvivors[ID]:Get():setPrimaryHandItem(phi)
		
	end
    return survivor
end

function SuperSurvivorManager:spawnSurvivor(isFemale, square)
    if not square then return nil end
    local id = SSPersistence.allocateSurvivor()
    self.SurvivorCount = math.max(self.SurvivorCount, id)
    local survivor = SuperSurvivor:new(isFemale, square)
    if not survivor then return nil end
    survivor:setID(id)
    self.SuperSurvivors[id] = survivor
    SSPersistence.observe(survivor)
    return survivor
end
function SuperSurvivorManager:getRecord(id) return SSPersistence.getRecord(id) end
function SuperSurvivorManager:getState(id) return SSPersistence.getState(id) end

function SuperSurvivorManager:Get(thisID)
	if(not self.SuperSurvivors[thisID]) then
		--print("super survivor #"..tostring(thisID).." was not found")
		return nil
	else
		--print("super survivor #"..tostring(thisID).." is " .. self.SuperSurvivors[thisID]:getName())
		return self.SuperSurvivors[thisID]
	end
end

function SuperSurvivorManager:OnDeath(ID)
	
	SSPersistence.markDead(ID)
	self.SuperSurvivors[ID] = nil

end

function SuperSurvivorManager:update()
	
	for i in pairs(self.SuperSurvivors) do
		if not self.UpdateFilter or self.UpdateFilter(self.SuperSurvivors[i]) then
		if (self.SuperSurvivors[i] ~= nil and self.MainPlayer ~= i) then
			if (self.SuperSurvivors[i].TargetSquare ~= nil and self.SuperSurvivors[i].TargetSquare:getZ() ~= self.SuperSurvivors[i].player:getZ() and getGameSpeed() > 1) then
				print("DANGER ZONE")
				self.SuperSurvivors[i].TargetSquare = nil
				self.SuperSurvivors[i]:DebugSay("SuperSurvivorManager Update() is about to trigger a StopWalk!")
				self.SuperSurvivors[i]:StopWalk()
				self.SuperSurvivors[i]:Wait(10)
				--self.SuperSurvivors[i]:getTaskManager():AddToTop(WanderTask:new(self.SuperSurvivors[i]))
			end
		end
	
		if(self.SuperSurvivors[i] ~= nil) and (self.MainPlayer ~= i) and (self.SuperSurvivors[i]:updateTime()) and (not self.SuperSurvivors[i].player:isAsleep()) and (self.SuperSurvivors[i]:isInCell()) then 
			self.SuperSurvivors[i]:update() 
		--	if(self.SuperSurvivors[i].DebugMode) then print(self.SuperSurvivors[i]:getName() .. " update()") end
		end
		end
	end

end
function SuperSurvivorManager:AsleepHealAll()
	
	for i=1, self.SurvivorCount+1 do	
		if(self.SuperSurvivors[i] ~= nil) and (self.MainPlayer ~= i) and (self.SuperSurvivors[i].player) then 
			self.SuperSurvivors[i].player:getBodyDamage():AddGeneralHealth(10)
		end
	end

end
function SuperSurvivorManager:PublicExecution(SSW,SSV)
	local maxDistance = 20
	
	for i=1, self.SurvivorCount+1 do
		if(self.SuperSurvivors[i] ~= nil) and (self.SuperSurvivors[i]:isInCell()) then 
			local distance = getDistanceBetween(self.SuperSurvivors[i]:Get(),getSpecificPlayer(0))
			if(distance < maxDistance) and (self.SuperSurvivors[i]:Get():CanSee(SSV:Get())) then
				
				if(not self.SuperSurvivors[i]:isInGroup(SSW:Get()) and not self.SuperSurvivors[i]:isInGroup(SSV:Get())) then
					
					if(self.SuperSurvivors[i]:usingGun()) and (ZombRand(2)==1) then
						--chance to attack with gun if see someone near by get executed
						print(self.SuperSurvivors[i]:getName() .. " attacking the murderer with gun")
						self.SuperSurvivors[i]:Get():getModData().hitByCharacter = true
						
					else
						-- flee from the crazy murderer
						print(self.SuperSurvivors[i]:getName() .. " fleeing from the crazy murderer")
						--print("FLEEING FROM1 " .. self.SuperSurvivors[i]:getName())
						self.SuperSurvivors[i]:getTaskManager():AddToTop(FleeFromHereTask:new(self.SuperSurvivors[i],SSW:Get():getCurrentSquare()))
					end
					self.SuperSurvivors[i]:SpokeTo(SSW:Get():getModData().ID)
					self.SuperSurvivors[i]:SpokeTo(SSV:Get():getModData().ID)
					
				end
				
			end
		end
	end
	

end

function SuperSurvivorManager:GunShotHandle(SSW)
	local maxDistance = 20
	local weapon = getSpecificPlayer(0):getPrimaryHandItem()
	if not weapon then return false end
	
	local range = weapon:getSoundRadius();
	for i=1, self.SurvivorCount+1 do
		if(self.SuperSurvivors[i] ~= nil) and (self.SuperSurvivors[i]:isInCell()) then 
			local distance = getDistanceBetween(self.SuperSurvivors[i]:Get(),getSpecificPlayer(0))
			
				
				
				if(self.SuperSurvivors[i].player:getModData().surender) and (distance < maxDistance) and self.SuperSurvivors[i]:Get():CanSee(SSW:Get()) and self.SuperSurvivors[i].player:CanSee(getSpecificPlayer(0)) then
					-- flee from the crazy murderer
					print(self.SuperSurvivors[i]:getName() .. " fleeing from the crazy murderer")
					--print("FLEEING FROM2 " .. self.SuperSurvivors[i]:GetName())
					self.SuperSurvivors[i]:getTaskManager():AddToTop(FleeFromHereTask:new(self.SuperSurvivors[i],SSW:Get():getCurrentSquare()))
					self.SuperSurvivors[i]:SpokeTo(SSW:Get():getModData().ID)
				end
				
				if(self.SuperSurvivors[i].player:getModData().isHostile or self.SuperSurvivors[i]:getCurrentTask() == "Guard" or self.SuperSurvivors[i]:getCurrentTask() == "Patrol") and self.SuperSurvivors[i]:getTaskManager():getCurrentTask() ~= "Surender" and not self.SuperSurvivors[i].player:isDead() and not self.SuperSurvivors[i]:RealCanSee(getSpecificPlayer(0)) and (getDistanceBetween(getSpecificPlayer(0),self.SuperSurvivors[i].player) <= range) then
					print(self.SuperSurvivors[i]:getName().. " adding go check it out task")
					self.SuperSurvivors[i]:getTaskManager():AddToTop(GoCheckItOutTask:new(self.SuperSurvivors[i],getSpecificPlayer(0):getCurrentSquare()))
				end
				
				
			
		end
	end
	

end

function SuperSurvivorManager:GetSurvivorByName(thisName)
	local closestSoFar = 999
	local closestID = 0
	for i=1, self.SurvivorCount+1 do
		if(self.SuperSurvivors[i] ~= nil) and (self.SuperSurvivors[i]:isInCell()) then 
			local distance = getDistanceBetween(self.SuperSurvivors[i]:Get(),getSpecificPlayer(0))
			
			if(distance < closestSoFar) and (thisName == self.SuperSurvivors[i]:getName()) then
			--print("survivor found ".. tostring(self.SuperSurvivors[i]:getName()) .. " = " .. tostring(thisName) .. " !")
				closestID = i
				closestSoFar = distance
			end
		end
	end
	
	if(closestID ~= 0) then return self.SuperSurvivors[closestID]
	else
		--print("could not find survivor by this name" .. tostring(thisName))
		return nil 
	end

end

function SuperSurvivorManager:GetClosest()
	local closestSoFar = 20
	local closestID = 0
	for i=1, self.SurvivorCount+1 do
		if(self.SuperSurvivors[i] ~= nil) and (self.SuperSurvivors[i]:isInCell()) then 
			local distance = getDistanceBetween(self.SuperSurvivors[i]:Get(),getSpecificPlayer(0))
			if(distance < closestSoFar) then
				closestID = i
				closestSoFar = distance
			end
		end
	end
	
	if(closestID ~= 0) then return self.SuperSurvivors[closestID]
	else return nil end

end

function SuperSurvivorManager:GetClosestNonParty()
	local closestSoFar = 20
	local closestID = 0
	for i=1, self.SurvivorCount+1 do
		if(self.SuperSurvivors[i] ~= nil) and (self.SuperSurvivors[i]:isInCell()) then 
			local distance = getDistanceBetween(self.SuperSurvivors[i]:Get(),getSpecificPlayer(0))
			if(distance < closestSoFar) and (self.SuperSurvivors[i]:getGroupID() == nil) then
				closestID = i
				closestSoFar = distance
			end
		end
	end
	
	if(closestID ~= 0) then return self.SuperSurvivors[closestID]
	else return nil end

end

function SuperSurvivorManager:SaveAll()
	
	for i=1, self.SurvivorCount+1 do
		if(self.SuperSurvivors[i] ~= nil) and (self.SuperSurvivors[i]:isInCell()) then 			
			self.SuperSurvivors[i]:SaveSurvivor()
		end
	end

end

SSM = SuperSurvivorManager:new()





