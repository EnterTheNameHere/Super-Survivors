-- Explicit disposable-world stations; this directory is excluded from releases.
SuperbSurvivorsTests = SuperbSurvivorsTests or {stations = {}, actors = {}}
local tests = SuperbSurvivorsTests
tests.actors = tests.actors or {}

local function available()
    if not getDebug() or isClient() or isServer() then
        error("[SS tests] Stations require debug single-player mode.")
    end
    if not getSpecificPlayer(0) or not SSM or not SSM:Get(0) then
        error("[SS tests] Enter a disposable world and wait for survivor initialization.")
    end
end

local function message(text, speak)
    print("[SS tests] " .. text)
    local player = getSpecificPlayer(0)
    if speak and player then player:Say("[SS test] " .. text) end
end

local function step(active, index, total, instruction)
    if active.step and active.step >= index then return end
    active.step = index
    message(active.name .. " - step " .. index .. "/" .. total .. ": " .. instruction, true)
end

function tests.beginSession()
    available()
    if tests.session then return end
    tests.session = {manager = SSM, autoSpawns = SSM.AutoSpawnsSuspended, filter = SSM.UpdateFilter}
    SSM.AutoSpawnsSuspended = true
    SSM.UpdateFilter = function(survivor) return survivor ~= nil and tests.actors[survivor] ~= nil end
    message("Session started: new mod spawns/raids suppressed; other managed Lua AI paused.", true)
    message("Existing zombies/native actor updates and saving remain active. Use a disposable world.")
end

local function actor(slot, near)
    require "Debug/SuperbSurvivorsDebug"
    tests.slots = tests.slots or {}
    local survivor = tests.slots[slot] and SSM:Get(tests.slots[slot])
    if not survivor or not survivor:Get() or survivor:Get():isDead() then
        local reason
        if near then
            local character = near:Get()
            local x, y, z = math.floor(character:getX()), math.floor(character:getY()), math.floor(character:getZ())
            for _, offset in ipairs({{1,0}, {0,1}, {-1,0}, {0,-1}, {1,1}, {-1,1}, {-1,-1}, {1,-1}}) do
                local square = getCell():getGridSquare(x + offset[1], y + offset[2], z)
                if square and square:getFloor() and square:isFree(false) and square:isCanSee(0) then
                    survivor, reason = SuperbSurvivorsDebug.spawn(x + offset[1], y + offset[2], z)
                    break
                end
            end
        end
        if not survivor then survivor, reason = SuperbSurvivorsDebug.spawnStationary() end
        if not survivor then error(reason or "No free visible tile for test NPC") end
        tests.slots[slot] = survivor:getID()
    end
    local manager = survivor:getTaskManager()
    if not tests.actors[survivor] then
        tests.actors[survivor] = {ai = manager.AIEnabled, wait = survivor.WaitTicks}
    end
    manager:clear()
    manager.AIEnabled = false
    ISTimedActionQueue.clear(survivor:Get())
    survivor:StopWalk()
    survivor:Wait(0)
    message("Fixture " .. slot .. ": NPC " .. tostring(survivor:getID()))
    return survivor
end

local function parkActors()
    for survivor in pairs(tests.actors) do
        if survivor:Get() and not survivor:Get():isDead() then
            survivor:getTaskManager():clear()
            ISTimedActionQueue.clear(survivor:Get())
            survivor:StopWalk()
            survivor:Wait(36000)
        end
    end
end

local function finish(passed, note, manual)
    local active = tests.active
    active.result = (passed and "PASS" or "FAIL") .. (manual and " (observed)" or " (state checks)")
    active.note = note
    tests.lastResult = active
    tests.active = nil
    -- Restore session ownership before cleanup so a cleanup error cannot restart polling.
    parkActors()
    message(active.name .. ": " .. active.result .. ". " .. tostring(note or ""), true)
    if tests.sequence and passed then
        tests.sequenceIndex = tests.sequenceIndex + 1
        tests.pendingStation = tests.sequence[tests.sequenceIndex]
        if not tests.pendingStation then
            tests.sequence = nil
            message("Sequence complete. Run SuperbSurvivorsTests.endSession() to restore normal spawning/AI.", true)
        end
    else
        tests.sequence, tests.pendingStation = nil, nil
        message("Next: start another station, or SuperbSurvivorsTests.endSession() to restore normal spawning/AI.")
    end
end

tests.stations.stationary = {
    expected = "NPC and player stay visible for at least one minute; no errors.",
    setup = function(active)
        local survivor = actor("primary")
        survivor:Wait(36000)
        step(active, 1, 1, "Watch both characters for one minute. Record the result using the console command printed below.")
        message('Run SuperbSurvivorsTests.record(true, "Both visible") or SuperbSurvivorsTests.record(false, "What went wrong").')
        return survivor
    end,
}

tests.stations.patrol = {
    expected = "NPC reaches A, B, then A without turning back midway.",
    setup = function(active)
        require "7_Tasks/PatrolTask"
        local survivor = actor("primary")
        local character = survivor:Get()
        local x, y, z = math.floor(character:getX()), math.floor(character:getY()), math.floor(character:getZ())
        local first, second = character:getCurrentSquare(), nil
        for _, offset in ipairs({{1,0}, {0,1}, {-1,0}, {0,-1}}) do
            local clear = true
            for distance = 1, 5 do
                local square = getCell():getGridSquare(x + offset[1]*distance, y + offset[2]*distance, z)
                if not square or not square:getFloor() or not square:isFree(false) then clear = false; break end
            end
            if clear then
                second = getCell():getGridSquare(x + offset[1]*5, y + offset[2]*5, z)
                break
            end
        end
        if not second then error("Move to open ground with a clear five-tile lane, then retry.") end
        active.task = PatrolTask:new(survivor, first, second)
        survivor:getTaskManager():AddToTop(active.task)
        step(active, 1, 3, "Stand aside. NPC starts at A; watch the walk to B and back.")
        message("A=" .. x .. "," .. y .. "; B=" .. second:getX() .. "," .. second:getY())
        return survivor
    end,
    check = function(active)
        local count = active.task.ArrivalCount
        if count >= 3 then return true, "A/B/A arrivals recorded. Visual appearance still needs observation." end
        step(active, math.min(3, count + 1), 3, count >= 2 and "B reached; now returning to A." or "Travelling to B; do not block the lane.")
    end,
}

tests.stations.inventory = {
    expected = "Three fixture nails leave the player inventory and enter the NPC inventory exactly once.",
    setup = function(active)
        require "0_Utilities/SuperSurvivorTransferUtilities"
        local survivor = actor("primary")
        local source = getSpecificPlayer(0):getInventory()
        local destination = survivor:Get():getInventory()
        active.source, active.destination, active.items = source, destination, {}
        for i = 1, 3 do
            local item = source:AddItem("Base.Nails")
            if not item then error("Cannot create Base.Nails fixture") end
            table.insert(active.items, item)
        end
        active.queued = 0
        step(active, 1, 3, "Stand within two tiles of the NPC, on the same floor without a wall between you.")
        return survivor
    end,
    check = function(active)
        while active.queued < #active.items do
            local item = active.items[active.queued + 1]
            local action, reason, code = SuperSurvivorTransfers.queue(active.survivor:Get(), item, active.source, active.destination)
            if not action then
                if code == "out_of_reach" then return end
                return false, reason or "Transfer rejected"
            end
            active.queued = active.queued + 1
        end
        local transferred = 0
        for _, item in ipairs(active.items) do
            local source, destination = active.source:contains(item), active.destination:contains(item)
            if source and destination then return false, "Fixture item belongs to both inventories." end
            if not source and not destination then return false, "Fixture item disappeared from both inventories." end
            if destination then transferred = transferred + 1 end
        end
        if transferred == 3 and not active.survivor:isInAction() then
            step(active, 3, 3, "Three nails received; checking item ownership.")
            return true, "All three item identities transferred once; source contains none."
        end
        step(active, 2, 3, "Transfer in progress. Keep both actors adjacent until the result prints.")
    end,
}

tests.stations.medical = {
    expected = "NPC self-bandages a prepared scratch; one ripped sheet is consumed by the vanilla action.",
    setup = function(active)
        require "7_Tasks/FirstAideTask"
        local survivor = actor("primary")
        local character = survivor:Get()
        character:getBodyDamage():RestoreToFullHealth()
        local part = character:getBodyDamage():getBodyPart(BodyPartType.ForeArm_L)
        part:setScratched(true, false)
        part:setBleedingTime(0)
        active.part, active.inventory = part, character:getInventory()
        if not active.inventory:AddItem("Base.RippedSheets") then error("Cannot create medical supply") end
        active.supplyCount = active.inventory:getItemCount("Base.RippedSheets", false)
        survivor:getTaskManager():AddToTop(FirstAideTask:new(survivor))
        step(active, 1, 2, "NPC has a nonbleeding scratch and a sheet. Watch self-bandaging; no action needed.")
        return survivor
    end,
    check = function(active)
        if not active.part:bandaged() then return end
        step(active, 2, 2, "Bandage applied; checking resource consumption and action completion.")
        if active.survivor:isInAction() then return end
        local remaining = active.inventory:getItemCount("Base.RippedSheets", false)
        return remaining == active.supplyCount - 1, "Bandaged=true; sheet count " .. active.supplyCount .. " -> " .. remaining
    end,
}

tests.stations.doctor = {
    expected = "Doctor disinfects and bandages a second NPC; one bandage is consumed.",
    setup = function(active)
        require "7_Tasks/DoctorTask"
        require "TimedActions/ISDisinfect"
        require "TimedActions/ISApplyBandage"
        local doctor = actor("primary")
        local patient = actor("patient", doctor)
        active.patient = patient
        patient:Wait(36000)
        local damage = patient:Get():getBodyDamage()
        damage:RestoreToFullHealth()
        active.part = damage:getBodyPart(BodyPartType.ForeArm_L)
        active.part:setScratched(true, false)
        active.part:setBleedingTime(0)
        active.inventory = doctor:Get():getInventory()
        if not active.inventory:FindAndReturn("AlcoholWipes") then
            if not active.inventory:AddItem("Base.AlcoholWipes") then error("Cannot create alcohol wipes") end
        end
        if not active.inventory:AddItem("Base.Bandage") then error("Cannot create bandage") end
        active.supplyCount = active.inventory:getItemCount("Base.Bandage", false)
        local task = DoctorTask:new(doctor)
        task.Patient = patient:Get()
        doctor:getTaskManager():AddToTop(task)
        step(active, 1, 3, "Doctor will approach the patient if needed, then disinfect and bandage. Stay nearby.")
        return doctor
    end,
    check = function(active)
        if active.patient and (not active.patient:Get() or active.patient:Get():isDead()) then
            return false, "Patient died or unloaded"
        end
        if active.patient and getDistanceBetween(active.survivor:Get(), active.patient:Get()) < 2 then
            step(active, 2, 3, "Doctor is beside the patient. Watch disinfection and bandaging.")
        end
        if not active.part:bandaged() then return end
        step(active, 3, 3, "Patient bandaged; checking disinfection and bandage consumption.")
        if active.survivor:isInAction() then return end
        local remaining = active.inventory:getItemCount("Base.Bandage", false)
        local disinfected = active.part:getAlcoholLevel() > 0
        return disinfected and remaining == active.supplyCount - 1,
            "Disinfected=" .. tostring(disinfected) .. "; bandages " .. active.supplyCount .. " -> " .. remaining
    end,
}

function tests.list()
    available()
    for name, station in pairs(tests.stations) do message(name .. ": " .. station.expected) end
end

function tests.start(name)
    available()
    local station = tests.stations[name]
    if not station then error("Unknown station: " .. tostring(name)) end
    if tests.active then error("Record or stop the active station first.") end
    tests.beginSession()
    local active = {name = name, result = "awaiting observation", started = getTimestampMs()}
    tests.active = active
    message("Testing " .. name .. ". Expected: " .. station.expected)
    -- Cleanup on setup failure, then preserve the original stack/error for diagnosis.
    local ok, survivor = pcall(station.setup, active)
    if not ok then
        tests.active = nil
        local cleaned, cleanupError = pcall(parkActors)
        if not cleaned then message("Setup cleanup also failed: " .. tostring(cleanupError)) end
        error(survivor)
    end
    active.survivor, active.survivorID = survivor, survivor:getID()
    return survivor
end

function tests.status()
    available()
    if not tests.active then message("No active station."); return nil end
    message(tests.active.name .. ": " .. tests.active.result .. "; step " .. tostring(tests.active.step))
    return tests.active
end

function tests.record(passed, note)
    available()
    if type(passed) ~= "boolean" or not tests.active then error("Supply true/false for the active station.") end
    finish(passed, note, true)
end

function tests.stop()
    available()
    tests.sequence, tests.pendingStation = nil, nil
    if tests.active then finish(false, "Aborted by user", true) else parkActors() end
end

function tests.runAll()
    available()
    if tests.active or tests.pendingStation then error("Stop the active test sequence first.") end
    tests.sequence = {"stationary", "patrol", "inventory", "medical", "doctor"}
    tests.sequenceIndex = 1
    tests.start(tests.sequence[1])
end

function tests.endSession()
    available()
    local cleaned, cleanupError = pcall(tests.stop)
    local session = tests.session
    if not session then
        if not cleaned then error(cleanupError) end
        return
    end
    -- The manager is captured to avoid restoring flags onto a different world.
    session.manager.AutoSpawnsSuspended = session.autoSpawns
    session.manager.UpdateFilter = session.filter
    for survivor, previous in pairs(tests.actors) do
        if survivor:Get() then
            survivor:getTaskManager().AIEnabled = previous.ai
            survivor:Wait(previous.wait or 0)
        end
    end
    tests.session, tests.actors = nil, {}
    message("Session ended. Previous spawning and Lua AI settings restored.", true)
    if not cleaned then error(cleanupError) end
end

function tests.tick()
    if tests.pendingStation and not tests.active then
        local name = tests.pendingStation
        tests.pendingStation = nil
        local ok, reason = pcall(tests.start, name)
        if not ok then
            tests.sequence = nil
            message("Sequence stopped during setup: " .. tostring(reason), true)
            error(reason)
        end
        return
    end
    local active = tests.active
    if not active or not active.survivor then return end
    local now = getTimestampMs()
    if active.lastPoll and now - active.lastPoll < 250 then return end
    active.lastPoll = now
    if not active.survivor:Get() or active.survivor:Get():isDead() then finish(false, "Fixture NPC died or unloaded"); return end
    local check = tests.stations[active.name].check
    if check then
        local ok, passed, note = pcall(check, active)
        if not ok then finish(false, "Check raised: " .. tostring(passed)); error(passed) end
        if passed ~= nil then finish(passed, note); return end
        if now - active.started > 120000 then finish(false, "Timed out after 120 seconds; inspect console.txt"); return end
    end
end

-- No startup spawn. Hot reload preserves session state and replaces one observer.
if tests.callback then Events.OnTick.Remove(tests.callback) end
tests.callback = tests.tick
Events.OnTick.Add(tests.callback)

function tests.resetWorld()
    if tests.session then
        tests.session.manager.AutoSpawnsSuspended = tests.session.autoSpawns
        tests.session.manager.UpdateFilter = tests.session.filter
    end
    tests.active, tests.session, tests.lastResult = nil, nil, nil
    tests.sequence, tests.pendingStation = nil, nil
    tests.actors, tests.slots = {}, {}
end
if tests.worldCallback then Events.OnGameStart.Remove(tests.worldCallback) end
tests.worldCallback = tests.resetWorld
Events.OnGameStart.Add(tests.worldCallback)
