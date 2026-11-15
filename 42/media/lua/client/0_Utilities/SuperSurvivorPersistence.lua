-- Fresh-world, single-player registry. Native IsoPlayer owns character encoding.
SSPersistence = SSPersistence or {}
local P = SSPersistence
P.KEY, P.SCHEMA = "SuperSurvivorsReloaded.Registry", 1

local function supported() return not isClient() and not isServer() end
local function report(text) print("[SSR persistence] " .. text) end
local function position(actor)
    return {x = actor:getX(), y = actor:getY(), z = actor:getZ()}
end
local function integer(value, minimum)
    return type(value) == "number" and value >= minimum and value < math.huge and value % 1 == 0
end
local function validSnapshot(record)
    local saved = record.saved
    if type(saved) ~= "table" or not integer(saved.generation, 1) then return false end
    if saved.file ~= "SSR_Survivor_" .. record.id .. "_" .. saved.generation .. ".bin" then return false end
    local pos = saved.position
    if type(pos) ~= "table" then return false end
    for _, field in ipairs({"x", "y", "z"}) do
        if type(pos[field]) ~= "number" or math.abs(pos[field]) >= math.huge or pos[field] ~= pos[field] then return false end
    end
    return true
end
function P.squareKey(x, y, z)
    return math.floor(x) .. ":" .. math.floor(y) .. ":" .. math.floor(z)
end
function P.get()
    assert(P.data, "[SSR persistence] Registry not initialized by OnInitGlobalModData")
    return P.data
end
function P.getRecord(id) return P.get().survivors[id] end
function P.getState(id)
    local record = P.getRecord(id)
    if not record then return nil end
    return record.state == "dead" and "dead" or P.runtime[id] or "unloaded"
end

local function unindex(id)
    local key = P.keys[id]
    if key and P.index[key] then
        P.index[key][id] = nil
        if not next(P.index[key]) then P.index[key] = nil end
    end
    P.keys[id] = nil
end
local function index(id, pos)
    unindex(id)
    if not pos then return end
    local key = P.squareKey(pos.x, pos.y, pos.z)
    P.index[key] = P.index[key] or {}
    P.index[key][id], P.keys[id] = true, key
end
function P.issue(record, reason)
    record.issue = reason
    P.runtime[record.id] = "inconsistent"
    unindex(record.id)
    report("Survivor " .. record.id .. ": " .. reason)
end

function P.init(newGame)
    P.data, P.index, P.keys, P.runtime, P.loading = nil, {}, {}, {}, {}
    if not supported() then return end
    local data = ModData.get(P.KEY)
    if not data then
        data = ModData.getOrCreate(P.KEY)
        data.schema = P.SCHEMA
        data.nextSurvivorID, data.nextGroupID, data.nextSnapshot = 1, 0, 1
        data.survivors, data.groups, data.scenarioGroups = {}, {}, {}
    end
    assert(data.schema == P.SCHEMA, "[SSR persistence] Unsupported registry schema; no legacy import")
    assert(type(data.survivors) == "table" and type(data.groups) == "table"
        and type(data.scenarioGroups) == "table", "[SSR persistence] Invalid registry tables")
    assert(integer(data.nextSurvivorID, 1) and integer(data.nextGroupID, 0)
        and integer(data.nextSnapshot, 1), "[SSR persistence] Invalid allocation counters")
    P.data = data
    for id, record in pairs(data.survivors) do
        assert(type(id) == "number" and id >= 0 and id % 1 == 0 and record.id == id,
            "[SSR persistence] Invalid survivor identity")
        data.nextSurvivorID = math.max(data.nextSurvivorID, id + 1)
        P.runtime[id] = "unloaded"
        if id > 0 and record.state ~= "dead" then
            if not validSnapshot(record) then
                P.issue(record, "Invalid native snapshot manifest; not spawning a replacement")
            elseif not checkSaveFileExists(record.saved.file) then
                P.issue(record, "Referenced native character snapshot is missing; not spawning a replacement")
            else
                record.issue = nil
                index(id, record.saved.position)
            end
        end
    end
    for id, record in pairs(data.groups) do
        assert(type(id) == "number" and id >= 0 and id % 1 == 0 and record.id == id,
            "[SSR persistence] Invalid group identity")
        data.nextGroupID = math.max(data.nextGroupID, id + 1)
    end
    if SSM then SSM.SuperSurvivors, SSM.SurvivorCount = {}, data.nextSurvivorID - 1 end
    if SSGM then SSGM:Load() end
    -- Registry membership is authoritative across unloaded character snapshots.
    -- Report contradictions instead of silently assigning or creating actors.
    for gid, group in pairs(data.groups) do
        group.issue = nil
        local seen = {}
        for _, id in ipairs(group.members) do
            local record = data.survivors[id]
            if seen[id] or not record or record.state == "dead" or record.groupID ~= gid then
                group.issue = "Invalid/duplicate member " .. tostring(id)
                report("Group " .. gid .. ": " .. group.issue)
                if record and record.state ~= "dead" then P.issue(record, "Group membership mismatch") end
            end
            seen[id] = true
        end
        if group.leader ~= -1 and not seen[group.leader] then
            group.issue = "Leader is not a member"
            report("Group " .. gid .. ": " .. group.issue)
        end
    end
    for id, record in pairs(data.survivors) do
        if record.state ~= "dead" and record.groupID ~= nil then
            local group = data.groups[record.groupID]
            local found = false
            for _, member in ipairs(group and group.members or {}) do if member == id then found = true end end
            if not found then P.issue(record, "Missing group or membership") end
        end
    end
    RPresetSpawns = nil
    report("Registry schema " .. data.schema .. " initialized; newGame=" .. tostring(newGame))
end

function P.allocateSurvivor()
    local data = P.get()
    local id = data.nextSurvivorID
    data.nextSurvivorID = id + 1 -- Failed construction must not recycle identity.
    data.survivors[id] = {id = id, kind = "survivor", state = "pending"}
    return id
end
function P.observe(survivor)
    local actor, id = survivor:Get(), survivor:getID()
    local data = P.get()
    local record = data.survivors[id]
    if not record then
        assert(id == 0, "[SSR persistence] Cannot adopt an unregistered NPC")
        record = {id = 0, kind = "player", state = "alive"}
        data.survivors[0] = record
    end
    if record.state == "dead" and (id > 0 or actor:isDead()) then return record end
    record.name, record.groupID, record.role = survivor:getName(), survivor:getGroupID(), survivor:getGroupRole()
    record.lastObserved = {position = position(actor), worldHours = getGameTime():getWorldAgeHours()}
    record.state = "alive"
    P.runtime[id] = "loaded"
    return record
end

function P.saveCharacter(survivor)
    local actor = survivor:Get()
    if not actor or actor:isLocalPlayer() then return false end
    if actor:isDead() then P.markDead(survivor:getID()); return false end
    local record, data = P.observe(survivor), P.get()
    local file, generation
    -- Never overwrite a snapshot referenced by an earlier world checkpoint.
    -- Files orphaned by interrupted saves remain harmless and are not auto-imported.
    repeat
        generation = data.nextSnapshot
        data.nextSnapshot = generation + 1
        file = "SSR_Survivor_" .. record.id .. "_" .. generation .. ".bin"
    until not checkSaveFileExists(file)
    local md = actor:getModData()
    md.SSRIdentity, md.SSRSnapshot = record.id, generation
    actor:save(getSaveDir() .. file)
    assert(checkSaveFileExists(file), "[SSR persistence] Native snapshot was not created: " .. file)
    -- Publish the pointer only after native serialization succeeds.
    record.saved = {file = file, generation = generation, position = position(actor),
        worldHours = getGameTime():getWorldAgeHours()}
    record.issue = nil
    return true
end

function P.markDead(id)
    local record = P.getRecord(id)
    if not record then return end
    record.state, record.deathWorldHours = "dead", getGameTime():getWorldAgeHours()
    P.runtime[id] = "dead"
    unindex(id)
    if SSGM then
        for _, group in pairs(SSGM.Groups) do group:removeMember(id) end
    end
end
function P.unload(id)
    local survivor = SSM and SSM:Get(id)
    if not survivor or id == 0 then return false end
    local actor = survivor:Get()
    if actor:isDead() then P.markDead(id)
    else
        -- Release task/native-action ownership before dropping the live wrapper.
        if survivor.StopWalk then survivor:StopWalk() end
        if survivor.getTaskManager then survivor:getTaskManager():clear() end
        P.saveCharacter(survivor) -- Failure retains the live actor for retry/diagnosis.
        local record = P.getRecord(id)
        index(id, record.saved.position)
        P.runtime[id] = "unloaded"
    end
    actor:removeFromWorld()
    actor:removeFromSquare()
    SSM.SuperSurvivors[id] = nil
    survivor.player = nil
    return true
end

function P.loadSquare(square)
    if not P.data or not square or not SSM or not SSM:Get(0) then return end
    local key = P.squareKey(square:getX(), square:getY(), square:getZ())
    local entries = P.index[key]
    if not entries then return end
    local ids = {}
    for id in pairs(entries) do ids[#ids + 1] = id end
    table.sort(ids)
    for _, id in ipairs(ids) do
        if not SSM:Get(id) then SSM:LoadSurvivor(id, square) end
    end
end

function P.save()
    if not supported() or not P.data then return end
    for id, survivor in pairs(SSM and SSM.SuperSurvivors or {}) do
        if id == 0 then P.observe(survivor)
        elseif survivor:Get():isDead() then P.markDead(id)
        else P.saveCharacter(survivor) end
    end
    if SSGM then SSGM:Save() end
    P.data.checkpointWorldHours = getGameTime():getWorldAgeHours()
    -- GameWindow.save writes global_mod_data.bin after OnSave returns.
end

function P.tick()
    if not P.data or not supported() or not getCell() or not SSM then return end
    if not SSM:Get(0) and getSpecificPlayer(0) then SSM:init() end
    if not SSM:Get(0) then return end
    local unload = {}
    for id, survivor in pairs(SSM.SuperSurvivors) do
        if id > 0 then
            local actor = survivor:Get()
            if actor:isDead() then
                P.markDead(id)
                SSM.SuperSurvivors[id] = nil
            elseif not actor:getCurrentSquare() or
                (not getCell():getObjectList():contains(actor) and not getCell():getAddList():contains(actor)) or
                getCell():getRemoveList():contains(actor) then
                unload[#unload + 1] = id
            else P.observe(survivor) end
        end
    end
    for _, id in ipairs(unload) do P.unload(id) end
    -- Also covers initial squares loaded before the human player's wrapper exists.
    for key, entries in pairs(P.index) do
        local id = next(entries)
        local pos = id and P.getRecord(id).saved.position
        if pos then P.loadSquare(getCell():getGridSquare(math.floor(pos.x), math.floor(pos.y), math.floor(pos.z))) end
    end
end

if Events then
    if Events.OnInitGlobalModData then Events.OnInitGlobalModData.Add(P.init) end
    if Events.OnSave then Events.OnSave.Add(P.save) end
    if Events.OnTick then Events.OnTick.Add(P.tick) end
end
