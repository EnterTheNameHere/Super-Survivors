-- Explicit console tools for the B42 port. Nothing spawns automatically.
SuperbSurvivorsDebug = {}

local function unavailable(reason)
    print("[SuperbSurvivors] " .. reason)
    return nil, reason
end

function SuperbSurvivorsDebug.spawn(x, y, z)
    if not getDebug() then
        return unavailable("Start the game with -debug to use the spawn check.")
    end
    if isClient() or isServer() then
        return unavailable("The spawn check currently supports single-player only.")
    end
    local player = getSpecificPlayer(0)
    if not player or not player:getCurrentSquare() then
        return unavailable("Enter a world before running the spawn check.")
    end
    if not SSM or not SSM.SuperSurvivors[0] or not SurvivorMap then
        return unavailable("Survivor initialization has not completed; inspect console.txt.")
    end
    -- Either supply all three coordinates, or use a nearby tile on this floor.
    if x == nil and y == nil and z == nil then
        x = math.floor(player:getX()) + 2
        y = math.floor(player:getY())
        z = math.floor(player:getZ())
    end
    if type(x) ~= "number" or type(y) ~= "number" or type(z) ~= "number" then
        return unavailable("Supply x, y and z together, or omit all three.")
    end
    local square = getCell():getGridSquare(x, y, z)
    if not square or not square:getFloor() or not square:isFree(false) then
        return unavailable("Choose a loaded, unoccupied tile with a floor.")
    end
    -- Let constructor/API errors reach the console with their original stack.
    local survivor = SSM:spawnSurvivor(nil, square)
    if not survivor then
        return unavailable("The survivor constructor returned no survivor.")
    end
    print("[SuperbSurvivors] Spawned survivor " .. tostring(survivor:getID())
        .. " at " .. tostring(x) .. "," .. tostring(y) .. "," .. tostring(z))
    return survivor
end
