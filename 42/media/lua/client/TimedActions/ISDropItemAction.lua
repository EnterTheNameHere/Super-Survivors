--***********************************************************
--**                    ROBERT JOHNSON                     **
--***********************************************************

require "TimedActions/ISBaseTimedAction"

ISDropItemAction = ISBaseTimedAction:derive("ISDropItemAction");

function ISDropItemAction:isValid()
	return self.item ~= nil and self.character:getCurrentSquare() ~= nil
		and self.character:getInventory():contains(self.item);
end

function ISDropItemAction:update()
	self.item:setJobDelta(self:getJobDelta());
end

function ISDropItemAction:start()
	self.item:setJobType(getText("IGUI_JobType_Dropping"));
	self.item:setJobDelta(0.0);
end

function ISDropItemAction:stop()
    ISBaseTimedAction.stop(self);
    self.item:setJobDelta(0.0);

end

function ISDropItemAction:perform()
    -- The square/item can disappear while this action is queued. Always advance
    -- the queue without moving an invalid item or leaving an action stuck.
    if not self:isValid() then
        if self.item then self.item:setJobDelta(0.0) end
        ISBaseTimedAction.perform(self)
        return
    end
    self.item:getContainer():setDrawDirty(true);
    self.item:setJobDelta(0.0);

	local square = self.character:getCurrentSquare()
	require "TimedActions/ISTransferAction"
	local dropX,dropY,dropZ = ISTransferAction.GetDropItemOffset(self.character, square, self.item)
	if(dropX == nil)  then dropX = 0.0 end
	if(dropY == nil)  then dropY = 0.0 end
	if(dropZ == nil)  then dropZ = 0.0 end
	if(square ~= nil) then
		square:AddWorldInventoryItem(self.item, dropX, dropY, dropZ);
		self.character:getInventory():Remove(self.item);

		ISInventoryPage.renderDirty = true
		
		-- needed to remove from queue / start next.
		ISBaseTimedAction.perform(self);
	else
			print("drop square on Drop item action perform was nil")
	end
end

function ISDropItemAction:new (character, item, time)
	local o = {}
	setmetatable(o, self)
	self.__index = self
	o.character = character;
	o.item = item;
	o.stopOnWalk = false;
	o.stopOnRun = false;
	o.maxTime = time;
	return o
end
