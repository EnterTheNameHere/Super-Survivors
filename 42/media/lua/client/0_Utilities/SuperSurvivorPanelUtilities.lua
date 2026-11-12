SuperSurvivorPanels = {}

function SuperSurvivorPanels.contextMenu(playerIndex, x, y)
    -- The vanilla factory dereferences this before returning. Do not call it
    -- while the player's UI data is unavailable (startup/teardown).
    if not getPlayerContextMenu(playerIndex) then return nil end
    return ISContextMenu.get(playerIndex, x, y)
end

function SuperSurvivorPanels.position(width, height, x, y)
    local screen = getCore()
    if x == nil then x = window_super_survivors and (window_super_survivors.x + window_super_survivors.width + 8) or (screen:getScreenWidth() - width) / 2 end
    if y == nil then y = window_super_survivors and window_super_survivors.y or (screen:getScreenHeight() - height) / 2 end
    return math.max(0, math.min(x, screen:getScreenWidth() - width)), math.max(0, math.min(y, screen:getScreenHeight() - height))
end

function SuperSurvivorPanels.open(kind, survivorID, previous)
    local main = SSM and SSM:Get(0)
    local group = main and SSGM:Get(main:getGroupID())
    if not group then return false end
    for index, member in ipairs(group:getMembers()) do
        if type(member) == "table" and member:getID() == survivorID and member.player and not member.player:isDead() then
            local x, y = previous and previous.x, previous and previous.y
            local panel
            if kind == "inventory" then
                require "5_UI/SuperSurvivorInventory"
                panel = create_panel_inventory_transfer(index, x, y)
            elseif kind == "equipment" then
                require "5_UI/SuperSurvivorLoadout"
                panel = create_panel_loadout(index, x, y)
            else return false end
            if panel and previous then previous:removeFromUIManager() end
            return panel
        end
    end
    return false
end
