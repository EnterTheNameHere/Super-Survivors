-- B42's FBO moving-object pass explicitly skips exact IsoPlayer instances.
-- Its player pass visits only IsoPlayer.players (SP) / IDToPlayerMap (MP), so
-- standalone survivor players need submission in the opaque world render phase.
SuperSurvivorRender = SuperSurvivorRender or {}

-- Keep hot reload from registering the callback twice.
if SuperSurvivorRender.callback then
    Events.RenderOpaqueObjectsInWorld.Remove(SuperSurvivorRender.callback)
end

function SuperSurvivorRender.render(playerIndex)
    -- Multiplayer player registration/render ownership needs its own port.
    if isClient() or isServer() or not SSM then return end
    local observer = getSpecificPlayer(playerIndex)
    local cell = getCell()
    if not observer or not cell then return end
    local objects = cell:getObjectList()
    local observerFloor = math.floor(observer:getZ())
    local hasStandalonePlayer = false
    for _, survivor in pairs(SSM.SuperSurvivors) do
        local character = survivor:Get()
        if character and not character:isLocalPlayer() and not character:isDead()
            and objects:contains(character) then
            hasStandalonePlayer = true
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
    -- Standalone IsoPlayers still run native updateLOS using playerIndex 0.
    -- Their view can fade the real player in that viewport. Restore only the
    -- living local observer's own opacity; other characters keep engine LOS.
    -- Preserve explicit invisibility/render flags and the death fade.
    if hasStandalonePlayer and observer:isLocalPlayer() and not observer:isDead()
        and not observer:isInvisible() and not observer:isSpriteInvisible() and observer:getDoRender() then
        observer:setAlphaAndTarget(playerIndex, 1.0)
    end
end

SuperSurvivorRender.callback = SuperSurvivorRender.render
Events.RenderOpaqueObjectsInWorld.Add(SuperSurvivorRender.callback)
