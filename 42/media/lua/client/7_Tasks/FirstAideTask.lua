FirstAideTask = {}
FirstAideTask.__index = FirstAideTask

function FirstAideTask:new(superSurvivor)
    local o = setmetatable({parent = superSurvivor, Name = "First Aide"}, self)
    superSurvivor:StopWalk()
    return o
end

function FirstAideTask:isComplete()
    return not self.parent or not self.parent:HasInjury()
end

function FirstAideTask:isValid()
    return self.parent ~= nil and self.parent:Get() ~= nil
end

function FirstAideTask:OnCancel()
    if self.myTimedAction then
        ISTimedActionQueue.clear(self.parent:Get())
        self.myTimedAction = nil
    end
end

function FirstAideTask:update()
    if not self:isValid() or self.parent:isInAction() then return false end
    local player = self.parent:Get()
    local parts = player:getBodyDamage():getBodyParts()
    for i = 0, parts:size() - 1 do
        local part = parts:get(i)
        if part:HasInjury() and not part:bandaged() then
            local item = player:getInventory():getItemFromType("RippedSheets")
            -- Preserve the historical supply policy; the action owns consumption.
            if not item then item = player:getInventory():AddItem("Base.RippedSheets") end
            if not item then return false end
            require "TimedActions/ISApplyBandage"
            self.parent:StopWalk()
            self.myTimedAction = ISApplyBandage:new(player, player, item, part, true)
            ISTimedActionQueue.add(self.myTimedAction)
            -- Never force a treatment after a frame counter. A stuck native
            -- action must remain observable rather than silently healing/freeing it.
            return true
        end
    end
end
