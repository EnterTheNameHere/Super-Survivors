PatrolTask = {}
PatrolTask.__index = PatrolTask

function PatrolTask:new(superSurvivor, square1, square2)

	local o = {}
	setmetatable(o, self)
	self.__index = self		
		
	if(square1 ~= nil) then o.Square1 = square1
	elseif(superSurvivor.player:getModData().PX ~= nil) then 
	o.Square1 = getCell():getGridSquare(superSurvivor.player:getModData().PX,superSurvivor.player:getModData().PY,superSurvivor.player:getModData().PZ)					
	else o.Square1 = superSurvivor.player:getCurrentSquare() end
	if(o.Square1 == nil) then return nil end
	
	if(square2 ~= nil) then o.Square2 = square2
	elseif(superSurvivor.player:getModData().P2X ~= nil) then 
	o.Square2 = getCell():getGridSquare(superSurvivor.player:getModData().P2X,superSurvivor.player:getModData().P2Y,superSurvivor.player:getModData().P2Z)				
	else return nil end	
	if(o.Square2 == nil) then return nil end
	
	superSurvivor.player:getModData().PX = o.Square1:getX()
	superSurvivor.player:getModData().PY = o.Square1:getY()
	superSurvivor.player:getModData().PZ = o.Square1:getZ()
	superSurvivor.player:getModData().P2X = o.Square2:getX()
	superSurvivor.player:getModData().P2Y = o.Square2:getY()
	superSurvivor.player:getModData().P2Z = o.Square2:getZ()
	
	o.parent = superSurvivor
	o.Name = "Patrol"
	o.NextPoint = 1
	o.ArrivalCount = 0
	o.OnGoing = true
	o.parent:DebugSay(tostring(o.parent:getCurrentTask()).." Started!" )
	return o

end

function PatrolTask:isComplete()
	return false
end

function PatrolTask:isValid()
	if (not self.parent) or (not self.Square1) or (not self.Square2) then return false 
	else return true end
end

function PatrolTask:update()
	
	if(not self:isValid()) then return false end
	
	if(self.parent:isInAction() == false) and (self.parent:getDangerSeenCount() == 0) then
	
		local target = self.NextPoint == 1 and self.Square1 or self.Square2
		if self.parent.player:getCurrentSquare() == target then
			self.ArrivalCount = self.ArrivalCount + 1
			self.NextPoint = self.NextPoint == 1 and 2 or 1
			target = self.NextPoint == 1 and self.Square1 or self.Square2
		end
		self.parent:walkToDirect(target)
	
	end

end
