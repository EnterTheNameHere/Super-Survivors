-- B42's FBO moving-object pass explicitly skips exact IsoPlayer instances.
-- Its player pass visits only IsoPlayer.players (SP) / IDToPlayerMap (MP), so
-- standalone survivor players need submission in the opaque world render phase.
SuperSurvivorRender = SuperSurvivorRender or {}

-- Keep hot reload from registering the callback twice.
if SuperSurvivorRender.callback then
    Events.RenderOpaqueObjectsInWorld.Remove(SuperSurvivorRender.callback)
end
if SuperSurvivorRender.opacityCallback then
    Events.OnTick.Remove(SuperSurvivorRender.opacityCallback)
end

function SuperSurvivorRender.render(playerIndex)
    -- Multiplayer player registration/render ownership needs its own port.
    if isClient() or isServer() or not SSM then return end
    local observer = getSpecificPlayer(playerIndex)
    local cell = getCell()
    if not observer or not cell then return end
    local objects = cell:getObjectList()
    local observerFloor = math.floor(observer:getZ())
    for _, survivor in pairs(SSM.SuperSurvivors) do
        local character = survivor:Get()
        if character and not character:isLocalPlayer() and not character:isDead()
            and objects:contains(character) then
            local square = character:getCurrentSquare()
            -- Upper storeys can be collapsed by B42's cutaway renderer. Submit
            -- only visible squares at/below the observer's floor in this SP port.
            if character:isOnScreen() and square and math.floor(character:getZ()) <= observerFloor
                and square:isCanSee(playerIndex) then
                local light = square:getLightInfo(playerIndex)
                if light then
                    local x, y, z = character:getX(), character:getY(), character:getZ()
                    character:renderShadow(x, y, z)
                    character:render(x, y, z, light, true, false, nil)
                end
            end
        end
    end
end

function SuperSurvivorRender.updateObserverOpacity()
    if isClient() or isServer() or not (SSM and SSM.SuperSurvivors) then return end
    local cell = getCell()
    if not cell then return end
    local objects = cell:getObjectList()
    local hasStandalonePlayer = false
    for _, survivor in pairs(SSM.SuperSurvivors) do
        local character = survivor:Get()
        if character and not character:isLocalPlayer() and not character:isDead()
            and objects:contains(character) then
            hasStandalonePlayer = true
            break
        end
    end
    if not hasStandalonePlayer then return end

    -- Native NPC LOS shares playerIndex 0 and can fade the real observer.
    -- OnTick follows the native world update and precedes player submission.
    -- The opaque render event runs AFTER renderPlayers, too late to repair it.
    for playerIndex = 0, getNumActivePlayers() - 1 do
        local observer = getSpecificPlayer(playerIndex)
        if observer and observer:isLocalPlayer() and not observer:isDead()
            and not observer:isInvisible() and not observer:isSpriteInvisible() and observer:getDoRender() then
            observer:setAlphaAndTarget(playerIndex, 1.0)
        end
    end
end

SuperSurvivorRender.callback = SuperSurvivorRender.render
Events.RenderOpaqueObjectsInWorld.Add(SuperSurvivorRender.callback)
SuperSurvivorRender.opacityCallback = SuperSurvivorRender.updateObserverOpacity
Events.OnTick.Add(SuperSurvivorRender.opacityCallback)
-- Also repair an already-paused session when this file is hot-reloaded.
SuperSurvivorRender.updateObserverOpacity()
