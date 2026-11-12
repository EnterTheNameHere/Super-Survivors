SuperSurvivorTransfers = SuperSurvivorTransfers or {}

local function inReach(character, container)
    local root = container:getOutermostContainer()
    local other = root and root:getParent()
    if not other or not instanceof(other, "IsoGameCharacter") or other == character then return true end
    local here, there = character:getCurrentSquare(), other:getCurrentSquare()
    if not here or not there or character:getZ() ~= other:getZ() then return false end
    local dx, dy = character:getX() - other:getX(), character:getY() - other:getY()
    return dx*dx + dy*dy <= 4 and not here:isBlockedTo(there)
end

-- Keep an equipped item in its owner's source until un-equipping succeeds.
-- Vanilla validates inventory/capacity; this adapter also checks moving peers.
function SuperSurvivorTransfers.queue(character, item, source, destination, onComplete)
    if not character or not item or not source or not destination or source == destination then return false, "Invalid transfer source/destination", "invalid" end
    if not source:contains(item) then return false, "Item is no longer in the source inventory", "missing" end
    if not destination:hasRoomFor(character, item) then return false, "Destination inventory has no room", "full" end
    if not inReach(character, source) or not inReach(character, destination) then
        return false, "Stand within two tiles on the same floor, without a wall between the actors", "out_of_reach"
    end
    require "TimedActions/ISInventoryTransferAction"
    require "TimedActions/ISUnequipAction"
    if item:isEquipped() then
        if not character:isEquipped(item) then return false, "Equipped item must be transferred by its owner", "wrong_owner" end
        ISTimedActionQueue.add(ISUnequipAction:new(character, item, item:IsClothing() and 50 or 1))
    end
    local action = ISInventoryTransferAction:new(character, item, source, destination)
    local vanillaValid = action.isValid
    function action:isValid()
        if not inReach(self.character, source) or not inReach(self.character, destination) then
            self.ssFailureReason = "Actors moved out of reach or behind a wall"
            return false
        end
        return vanillaValid(self)
    end
    if onComplete then action:setOnComplete(onComplete) end
    ISTimedActionQueue.add(action)
    return action
end

-- selectedContainer is used by vanilla only for facing and the local loot UI.
-- NPCs have no loot panel, even though their player index commonly equals zero.
local function detachNpcLootUI(action, faceContainer)
    local character = action.character
    if not character or not character:isNpc() or character:isLocalPlayer() then return end
    local container = action.selectedContainer or action.ssNpcTransferContainer
    action.ssNpcTransferContainer = container
    action.selectedContainer = nil
    if faceContainer and container then
        local parent = container:getParent()
        if parent and not character:isSittingOnFurniture() then character:faceThisObject(parent) end
    end
end

function SuperSurvivorTransfers.installNpcUIHooks()
    require "TimedActions/ISInventoryTransferAction"
    local hooks = SuperSurvivorTransfers.npcUIHooks or {}
    SuperSurvivorTransfers.npcUIHooks = hooks
    for _, method in ipairs({"update", "perform"}) do
        local base = ISInventoryTransferAction[method]
        local old = hooks[method]
        if old and base == old.wrapper then base = old.base end
        if type(base) == "function" then
            local faceContainer = method == "update"
            local wrapper = function(action, ...)
                detachNpcLootUI(action, faceContainer)
                return base(action, ...)
            end
            hooks[method] = {base = base, wrapper = wrapper}
            ISInventoryTransferAction[method] = wrapper
        end
    end
end

-- Class-level hooks also cover legacy NPC callers and already-running actions.
-- Keep vanilla validation, progress, transfer, cancellation and completion.
SuperSurvivorTransfers.installNpcUIHooks()
