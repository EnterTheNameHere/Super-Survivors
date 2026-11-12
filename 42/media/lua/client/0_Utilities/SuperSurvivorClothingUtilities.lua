-- Live clothing commands use native action timing, animation and cancellation.
-- Spawn/load appearance setup can still use the immediate WearThis initializer.
SuperSurvivorClothing = {}

function SuperSurvivorClothing.pending(character, item)
    local queue = ISTimedActionQueue.queues[character]
    if queue then
        for _, action in ipairs(queue.queue) do
            if action.clothingAction and (not item or action.item == item) then return action end
        end
    end
end

function SuperSurvivorClothing.queue(character, item, wear)
    if not character or character:isDead() or not item or not character:getInventory():contains(item) then
        return false, "Item is no longer in the NPC inventory"
    end
    if SuperSurvivorClothing.pending(character) then return false, getText("IGUI_SS_Clothing_Busy") end
    require "TimedActions/ISWearClothing"
    require "TimedActions/ISUnequipAction"
    local action
    if wear then
        if not (item:IsClothing() or item:IsInventoryContainer()) then return false, "Item is not wearable clothing" end
        local location
        if item:IsInventoryContainer() then location = item:canBeEquipped()
        else location = item:getBodyLocation() end
        if not location or location == "" then return false, "Item has no wearable body location" end
        action = ISWearClothing:new(character, item)
    else
        if not character:isEquipped(item) then return false, "Item is no longer equipped" end
        -- Match the duration passed by the installed inventory context menu.
        action = ISUnequipAction:new(character, item, 50)
        -- NPC inventory items must not use the real player's hotbar animation.
        action.fromHotbar, action.hotbar = false, nil
    end
    ISTimedActionQueue.add(action)
    return action
end

function SuperSurvivorClothing.cancel(character)
    if not SuperSurvivorClothing.pending(character) then return false end
    -- Same native cancellation as stopping an inventory action: queued work is
    -- cancelled too. No manual equipment mutation or forced completion.
    ISTimedActionQueue.clear(character)
    return true
end
