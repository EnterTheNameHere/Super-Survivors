SuperSurvivorTransfers = {}

local function inReach(character, container)
    local root = container:getOutermostContainer()
    local other = root and root:getParent()
    if not other or not instanceof(other, "IsoGameCharacter") or other == character then return true end
    local here, there = character:getCurrentSquare(), other:getCurrentSquare()
    if not here or not there or character:getZ() ~= other:getZ() then return false end
    local dx, dy = character:getX() - other:getX(), character:getY() - other:getY()
    return dx*dx + dy*dy <= 4 and not here:isBlockedTo(there)
end

-- Keep an equipped item in its owner's source until unequipping succeeds.
-- Vanilla validates inventory/capacity; this adapter also checks moving peers.
function SuperSurvivorTransfers.queue(character, item, source, destination, onComplete)
    if not character or not item or not source or not destination or source == destination then return false end
    if not source:contains(item) or not destination:hasRoomFor(character, item) then return false end
    if not inReach(character, source) or not inReach(character, destination) then return false end
    require "TimedActions/ISInventoryTransferAction"
    require "TimedActions/ISUnequipAction"
    if item:isEquipped() then
        if not character:isEquipped(item) then return false end
        ISTimedActionQueue.add(ISUnequipAction:new(character, item, 1))
    end
    local action = ISInventoryTransferAction:new(character, item, source, destination)
    local vanillaValid = action.isValid
    function action:isValid()
        return inReach(self.character, source) and inReach(self.character, destination) and vanillaValid(self)
    end
    if onComplete then action:setOnComplete(onComplete) end
    ISTimedActionQueue.add(action)
    return action
end
