-- Explicit console tools for the B42 port. Nothing spawns automatically.
SuperbSurvivorsDebug = SuperbSurvivorsDebug or {}

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
    SuperbSurvivorsDebug.lastSpawnedID = survivor:getID()
    return survivor
end

-- Keep one diagnostic NPC on a currently visible adjacent tile. This explicit
-- debug-only probe pauses its Lua AI without changing rendering/visibility.
function SuperbSurvivorsDebug.spawnStationary()
    if not getDebug() or isClient() or isServer() then
        return unavailable("The stationary probe requires debug single-player mode.")
    end
    local observer = getSpecificPlayer(0)
    if not observer or not observer:getCurrentSquare() then
        return unavailable("Enter a world before running the stationary probe.")
    end
    local x, y, z = math.floor(observer:getX()), math.floor(observer:getY()), math.floor(observer:getZ())
    for _, offset in ipairs({{1, 0}, {0, 1}, {-1, 0}, {0, -1},
        {1, 1}, {-1, 1}, {-1, -1}, {1, -1}}) do
        local tx, ty = x + offset[1], y + offset[2]
        local square = getCell():getGridSquare(tx, ty, z)
        if square and square:isCanSee(0) and square:getFloor() and square:isFree(false) then
            local survivor, reason = SuperbSurvivorsDebug.spawn(tx, ty, z)
            if not survivor then return nil, reason end
            survivor:StopWalk()
            survivor:Wait(36000)
            print("[SuperbSurvivors] Stationary probe " .. tostring(survivor:getID())
                .. "; rendering flags unchanged. Run SuperbSurvivorsDebug.inspect() after a few frames.")
            return survivor
        end
    end
    return unavailable("No visible, free adjacent floor tile; move into an open area.")
end

-- Read-only rendering diagnostics for the latest probe, or an explicit ID.
function SuperbSurvivorsDebug.inspect(id)
    if not getDebug() or isClient() or isServer() then
        return unavailable("Inspection requires debug single-player mode.")
    end
    id = id or SuperbSurvivorsDebug.lastSpawnedID
    if type(id) ~= "number" or not SSM then
        return unavailable("Spawn a probe first, or supply a survivor ID.")
    end
    local survivor = SSM:Get(id)
    local npc = survivor and survivor:Get()
    if not npc then return unavailable("No live character for survivor " .. tostring(id)) end
    local observer = getSpecificPlayer(0)
    local square = npc:getCurrentSquare()
    local visual = npc:getHumanVisual()
    local renderSquare = npc:getRenderSquare()
    local inCell, onSquare = false, false
    for _, object in ipairs(npc:getCell():getLuaObjectList()) do
        if object == npc then inCell = true; break end
    end
    if square then
        local moving = square:getMovingObjects()
        for i = 0, moving:size() - 1 do
            if moving:get(i) == npc then onSquare = true; break end
        end
    end
    local state = {
        id = id, x = npc:getX(), y = npc:getY(), z = npc:getZ(), waitTicks = survivor.WaitTicks,
        npc = npc:isNpc(), localPlayer = npc:isLocalPlayer(),
        invisible = npc:isInvisible(), spriteInvisible = npc:isSpriteInvisible(),
        sceneCulled = npc:isSceneCulled(), modelRegistered = npc:isAddedToModelManager(),
        modelActive = npc:hasActiveModel(), modelInstance = npc:getModelInstance() ~= nil,
        -- AnimationPlayer itself is not Lua-exposed in B42.21. Inspect only
        -- the character API; a non-nil Java handle does not expose its methods.
        doRender = npc:getDoRender(), hasAnimationPlayer = npc:hasAnimationPlayer(),
        animationState = npc:getAnimationStateName(), characterState = npc:getCurrentStateName(),
        hasRenderSquare = renderSquare ~= nil, renderSquareMatches = renderSquare == square,
        offsetX = npc:getOffsetX(), offsetY = npc:getOffsetY(), renderYOffset = npc:getRenderYOffset(),
        alpha = npc:getAlpha(0), targetAlpha = npc:getTargetAlpha(0),
        inCell = inCell, onSquare = onSquare, hasSquare = square ~= nil,
        hasVisual = visual ~= nil,
        skinTexture = visual and visual:getSkinTexture() or "none",
        hair = visual and visual:getHairModel() or "none"
    }
    if observer then
        state.observerX, state.observerY, state.observerZ = observer:getX(), observer:getY(), observer:getZ()
        state.observerCanSee = observer:CanSee(npc)
        if square then state.squareVisible = square:isCanSee(0) end
    end
    print("[SuperbSurvivors] Render inspection for survivor " .. tostring(id))
    for _, key in ipairs({"id", "x", "y", "z", "waitTicks", "npc", "localPlayer", "invisible",
        "spriteInvisible", "sceneCulled", "modelRegistered", "modelActive", "modelInstance",
        "doRender", "hasAnimationPlayer",
        "animationState", "characterState", "hasRenderSquare", "renderSquareMatches",
        "offsetX", "offsetY", "renderYOffset",
        "alpha", "targetAlpha", "inCell", "onSquare", "hasSquare", "hasVisual",
        "skinTexture", "hair", "observerX", "observerY", "observerZ", "observerCanSee", "squareVisible"}) do
        print("[SuperbSurvivors] render." .. key .. "=" .. tostring(state[key]))
    end
    return state
end

-- Capture after actual simulation ticks, even when the console was opened paused.
-- Repeating the command replaces the pending capture instead of stacking callbacks.
function SuperbSurvivorsDebug.inspectAfterTicks(id)
    if not getDebug() or isClient() or isServer() then
        return unavailable("Inspection requires debug single-player mode.")
    end
    id = id or SuperbSurvivorsDebug.lastSpawnedID
    if type(id) ~= "number" or not SSM or not SSM:Get(id) then
        return unavailable("Spawn a probe first, or supply a survivor ID.")
    end
    if SuperbSurvivorsDebug.pendingInspection then
        Events.OnTick.Remove(SuperbSurvivorsDebug.pendingInspection)
    end
    local ticks = 0
    local callback
    callback = function()
        ticks = ticks + 1
        if ticks < 120 then return end
        Events.OnTick.Remove(callback)
        SuperbSurvivorsDebug.pendingInspection = nil
        print("[SuperbSurvivors] Deferred inspection after 120 simulation ticks")
        SuperbSurvivorsDebug.inspect(id)
    end
    SuperbSurvivorsDebug.pendingInspection = callback
    Events.OnTick.Add(callback)
    print("[SuperbSurvivors] Inspection scheduled; close the console and unpause for several seconds.")
    return true
end

-- Explicit diagnostic intervention: rebuild the existing model through the
-- engine's supported reset path, then capture after it has had time to update.
function SuperbSurvivorsDebug.resetModelProbe(id)
    if not getDebug() or isClient() or isServer() then
        return unavailable("The model reset probe requires debug single-player mode.")
    end
    id = id or SuperbSurvivorsDebug.lastSpawnedID
    local survivor = type(id) == "number" and SSM and SSM:Get(id)
    local npc = survivor and survivor:Get()
    if not npc then return unavailable("No live probe to reset.") end
    npc:resetModel()
    print("[SuperbSurvivors] Requested engine model reset for survivor " .. tostring(id))
    return SuperbSurvivorsDebug.inspectAfterTicks(id)
end

-- The vanilla ObjectViewer uses these debug reflection globals. Read declared
-- fields only: never call methods on opaque ModelInstance/AnimationPlayer handles.
local function modelField(object, name)
    if object == nil then return nil end
    for index = 0, getNumClassFields(object) - 1 do
        local field = getClassField(object, index)
        if field:getName() == name then return getClassFieldVal(object, field) end
    end
    return nil
end

local function inspectCharacterModel(character, label)
    local instance = character:getModelInstance()
    local model = modelField(instance, "model")
    local mesh = modelField(model, "mesh")
    local animation = character:getAnimationPlayer()
    local multiTrack = modelField(animation, "multiTrack")
    local tracks = modelField(multiTrack, "tracks")
    local initializer = modelField(instance, "textureInitializer")
    local creator = character:getTextureCreator()
    local slot = modelField(character:getSprite(), "modelSlot")
    local sub = modelField(instance, "sub")
    local state = {
        model = model ~= nil, modelName = modelField(model, "name"),
        mesh = mesh ~= nil, meshPath = modelField(mesh, "fullPath"),
        meshVbo = modelField(mesh, "hasVbo"), meshSkinning = modelField(mesh, "skinningData") ~= nil,
        instanceSkinning = modelField(instance, "data") ~= nil,
        scale = modelField(instance, "scale"), texture = tostring(modelField(instance, "tex")),
        tintR = modelField(instance, "tintR"), tintG = modelField(instance, "tintG"),
        tintB = modelField(instance, "tintB"), subModels = sub and sub:size(),
        animationSkinning = modelField(animation, "skinningData") ~= nil,
        animationModelMatches = modelField(animation, "model") == model,
        firstFramePending = modelField(animation, "boneTransformsNeedFirstFrame"),
        updateBones = modelField(animation, "updateBones"), tracks = tracks and tracks:size(),
        textureCreator = creator ~= nil, textureCreatorRendered = modelField(creator, "rendered"),
        texturesNotReady = tostring(modelField(creator, "texturesNotReady")),
        textureInitializer = initializer ~= nil, initializerRendered = modelField(initializer, "rendered"),
        slotFrames = modelField(slot, "framesSinceStart"), slotActive = modelField(slot, "active"),
        slotRemoving = modelField(slot, "remove"), isLocal = character:isLocal(),
        animationDebug = character:getAnimationDebug()
    }
    for _, key in ipairs({"model", "modelName", "mesh", "meshPath", "meshVbo", "meshSkinning",
        "instanceSkinning", "scale", "texture", "tintR", "tintG", "tintB", "subModels",
        "animationSkinning", "animationModelMatches", "firstFramePending", "updateBones", "tracks",
        "textureCreator", "textureCreatorRendered", "texturesNotReady", "textureInitializer",
        "initializerRendered", "slotFrames", "slotActive", "slotRemoving", "isLocal", "animationDebug"}) do
        print("[SuperbSurvivors] model." .. label .. "." .. key .. "=" .. tostring(state[key]))
    end
    return state
end

function SuperbSurvivorsDebug.compareModels(id)
    if not getDebug() or isClient() or isServer() then
        return unavailable("Model comparison requires debug single-player mode.")
    end
    id = id or SuperbSurvivorsDebug.lastSpawnedID
    local survivor = type(id) == "number" and SSM and SSM:Get(id)
    local npc = survivor and survivor:Get()
    local observer = getSpecificPlayer(0)
    if not npc or not observer then return unavailable("A live probe and player are required.") end
    print("[SuperbSurvivors] Model comparison for survivor " .. tostring(id)
        .. "; displayPlayerModel=" .. tostring(getCore():isDisplayPlayerModel()))
    return {npc = inspectCharacterModel(npc, "npc"), player = inspectCharacterModel(observer, "player")}
end

-- Survivor task observation (kept in this cached debug module for hot reload).
-- Camera following is not implemented: native frame setup overwrites the target.
SuperbSurvivorsWatch = SuperbSurvivorsWatch or {}
local Watch = SuperbSurvivorsWatch
Watch.state = Watch.state or {active = false}
local state = Watch.state

local function removeCallbacks()
    if Watch.tickCallback then Events.OnTick.Remove(Watch.tickCallback) end
    if Watch.renderCallback then Events.OnRenderTick.Remove(Watch.renderCallback) end
    if Watch.drawCallback then Events.OnPostUIDraw.Remove(Watch.drawCallback) end
    if Watch.startCallback then Events.OnGameStart.Remove(Watch.startCallback) end
    if Watch.menuCallback then Events.OnMainMenuEnter.Remove(Watch.menuCallback) end
end
removeCallbacks()
Watch.renderCallback, Watch.followCamera = nil, nil
state.previousCamera = nil

local function message(text)
    print("[SS watch] " .. text)
end

local function loadedCharacter(survivor)
    local cell = getCell()
    local character = survivor and survivor:Get()
    if not cell or not character or character:isDead() or character:isLocalPlayer()
        or not character:getCurrentSquare() or not cell:getObjectList():contains(character) then return nil end
    return character
end

local function supported()
    if not getDebug() then return false, "Start the game with -debug." end
    if isClient() or isServer() or getNumActivePlayers() > 1 then
        return false, "Watch currently supports single-player with one local viewport."
    end
    if not getCell() or not (SSM and SSM.SuperSurvivors) then return false, "Enter a loaded world first." end
    return true
end

function Watch.stop(reason)
    if not state.active then return false end
    state.active, state.character, state.previousCamera = false, nil, nil
    state.survivor, state.id = nil, nil
    state.snapshot, state.lines, state.lastSummary, state.lastPoll = nil, nil, nil, nil
    removeCallbacks()
    message("Stopped" .. (reason and (": " .. reason) or "."))
    return true
end

local function snapshot()
    local survivor, character = state.survivor, state.character
    local manager = survivor:getTaskManager()
    local damage = character:getBodyDamage()
    return {
        id = state.id, name = survivor:getName(),
        task = manager and manager:getCurrentTask() or "unavailable",
        previousTask = manager and manager.LastTask or "None",
        ai = survivor:getAIMode(), role = survivor:getGroupRole(),
        health = damage and damage:getOverallBodyHealth() or nil,
        danger = survivor:getDangerSeenCount(), seen = survivor:getSeenCount(),
        waitTicks = survivor.WaitTicks or 0,
        x = character:getX(), y = character:getY(), z = character:getZ(),
        cameraFollow = false,
    }
end

local function direction(x, y, left, right, up, down)
    local horizontal = x < 0 and left or right
    local vertical = y < 0 and up or down
    if math.abs(y) <= math.abs(x) * 0.41421356237 then return horizontal end
    if math.abs(x) <= math.abs(y) * 0.41421356237 then return vertical end
    return vertical .. "-" .. horizontal
end

local function navigation(info)
    local player = getSpecificPlayer(0)
    if not player then return "To survivor: player position unavailable." end
    local dx, dy = info.x - player:getX(), info.y - player:getY()
    local distance = math.sqrt(dx * dx + dy * dy)
    local floors = info.z - player:getZ()
    info.distance, info.floorDifference = distance, floors
    local heading = distance < 1 and "within one tile"
        or (direction(dx, dy, "west", "east", "north", "south") .. "; screen "
            .. direction(dx - dy, dx + dy, "left", "right", "up", "down"))
    return string.format("To survivor: %.1f tiles; %s | floors: %+.0f", distance, heading, floors)
end

local function refresh()
    local info = snapshot()
    state.snapshot = info
    state.lines = {
        "Monitoring " .. tostring(info.name) .. " [" .. tostring(info.id) .. "]",
        "Task: " .. tostring(info.task) .. " | previous: " .. tostring(info.previousTask),
        "AI: " .. tostring(info.ai) .. " | role: " .. tostring(info.role),
        "Health: " .. (info.health and string.format("%.1f", info.health) or "unknown")
            .. " | seen/danger: " .. tostring(info.seen) .. "/" .. tostring(info.danger),
        string.format("Position: %.1f, %.1f, %.0f | wait: %s", info.x, info.y, info.z, tostring(info.waitTicks)),
        navigation(info),
        "Stop: SuperbSurvivorsWatch.stop()",
        "Monitor only; camera following is not available.",
    }
    local summary = tostring(info.task) .. " | AI=" .. tostring(info.ai) .. " | role=" .. tostring(info.role)
    if state.lastSummary ~= summary then
        state.lastSummary = summary
        message(tostring(info.name) .. " [" .. tostring(info.id) .. "]: " .. summary)
    end
    return info
end

function Watch.list()
    local ok, reason = supported()
    if not ok then message(reason); return nil, reason end
    local result = {}
    for id, survivor in pairs(SSM.SuperSurvivors) do
        if loadedCharacter(survivor) then
            result[#result + 1] = {id = id, name = survivor:getName()}
        end
    end
    table.sort(result, function(a, b) return a.id < b.id end)
    for _, entry in ipairs(result) do message(tostring(entry.id) .. ": " .. tostring(entry.name)) end
    if #result == 0 then message("No living, loaded survivors available.") end
    return result
end

function Watch.start(id)
    local ok, reason = supported()
    if not ok then message(reason); return false, reason end
    if id == nil then
        local origin = getSpecificPlayer(0) or IsoCamera.getCameraCharacter()
        local closest = math.huge
        for candidate, survivor in pairs(SSM.SuperSurvivors) do
            local character = loadedCharacter(survivor)
            if character then
                local distance = origin and ((character:getX() - origin:getX()) ^ 2
                    + (character:getY() - origin:getY()) ^ 2) or 0
                if distance < closest or (distance == closest and (id == nil or candidate < id)) then
                    closest, id = distance, candidate
                end
            end
        end
    end
    local survivor = id and SSM.SuperSurvivors[id]
    local character = loadedCharacter(survivor)
    if not character then
        reason = "Choose a living, loaded NPC ID with SuperbSurvivorsWatch.list()."
        message(reason)
        return false, reason
    end
    state.active, state.id, state.survivor = true, id, survivor
    state.character = character
    state.lastPoll, state.lastSummary = nil, nil
    Watch.installCallbacks()
    refresh()
    message("State monitor active. Camera following is not available; the camera stays with your character.")
    return true, "monitor_only"
end

function Watch.status()
    if not state.active then message("No survivor is being watched."); return nil end
    if loadedCharacter(state.survivor) ~= state.character then Watch.stop("Target died or unloaded."); return nil end
    local info = refresh()
    for _, line in ipairs(state.lines) do message(line) end
    return info
end

function Watch.tick()
    if not state.active then return end
    local ok = supported()
    if not ok then Watch.stop("World or game mode changed."); return end
    if loadedCharacter(state.survivor) ~= state.character then Watch.stop("Target died or unloaded."); return end
    local now = getTimestampMs()
    if not state.lastPoll or now - state.lastPoll >= 250 then
        state.lastPoll = now
        refresh()
    end
end

function Watch.draw()
    if not state.active or not state.lines then return end
    local text = getTextManager()
    local height = text:getFontHeight(UIFont.Small) + 3
    for index, line in ipairs(state.lines) do
        -- The game's post-UI draw event also works over the death-screen UI.
        text:DrawString(UIFont.Small, 15, 15 + (index - 1) * height, line, 1, 1, 1, 1)
    end
end

function Watch.installCallbacks()
    removeCallbacks()
    Watch.tickCallback, Watch.drawCallback = Watch.tick, Watch.draw
    Watch.startCallback = function() Watch.stop("New world started.") end
    Watch.menuCallback = function() Watch.stop("Returned to main menu.") end
    Events.OnTick.Add(Watch.tickCallback)
    Events.OnPostUIDraw.Add(Watch.drawCallback)
    Events.OnGameStart.Add(Watch.startCallback)
    Events.OnMainMenuEnter.Add(Watch.menuCallback)
end

-- Loading debug definitions alone does not start a watch or install idle hooks.
if state.active then Watch.installCallbacks() end
