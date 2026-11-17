-- Small opt-in registry/executor. No test runs during module loading.
SSRTests = SSRTests or {}
local T = SSRTests
T.definitions, T.results = T.definitions or {}, T.results or {}
T.revision = T.revision or 0
T.WARNING = "Warning — World Modifications\nTests may irreversibly alter this game world, including characters, items, objects and zombies. Use a disposable world. Restoration is not guaranteed."
local statuses = {PASSED=true, FAILED=true, INCONCLUSIVE=true, ["SETUP ERROR"]=true}

function T.enabled()
    return SuperSurvivorGetOption ~= nil and SuperSurvivorGetOption("DebugOptions") == 2
end
function T.register(definition)
    assert(type(definition.id) == "string" and type(definition.title) == "string"
        and type(definition.run) == "function", "Invalid SS test definition")
    T.definitions[definition.id] = definition
    T.definitionRevision = (T.definitionRevision or 0) + 1
    T.revision = T.revision + 1
end
function T.unregister(id)
    assert(not T.active or T.active.id ~= id, "Cancel an active test before removing it")
    T.definitions[id] = nil
    T.definitionRevision = (T.definitionRevision or 0) + 1
    T.revision = T.revision + 1
end
function T.list()
    local result = {}
    for _, definition in pairs(T.definitions) do result[#result+1] = definition end
    table.sort(result, function(a,b)
        if (a.order or 0) ~= (b.order or 0) then return (a.order or 0) < (b.order or 0) end
        return a.id < b.id
    end)
    return result
end
function T.availability(definition,parameters)
    if not definition then return false, "No test selected." end
    if not T.enabled() then return false, "Enable Debug Options in the mod options." end
    if isClient() or isServer() or getNumActivePlayers() ~= 1 then
        return false, "Single-player with one local viewport is required."
    end
    local player = getSpecificPlayer(0)
    if not getCell() or not player or player:isDead() or not player:getCurrentSquare() then
        return false, "Enter gameplay with a living player in a loaded world."
    end
    if definition.available then
        local ok, allowed, reason = pcall(definition.available,parameters)
        if not ok then return false, "Prerequisite error: " .. tostring(allowed) end
        if not allowed then return false, reason or "Test prerequisites are not satisfied." end
    end
    return true, "Available"
end

local function changed() T.revision = T.revision + 1 end
function T.start(id, consent,parameters)
    if T.active then return false, "Another test is already running." end
    if parameters~=nil and type(parameters)~="table" then return false,"Test parameters must be a table." end
    local definition = T.definitions[id]
    if T.cleanupFailure and not (definition and definition.readOnly) then
        return false, "Cleanup failed. Restart the game before running further mutating tests."
    end
    if consent ~= true then return false, "Acknowledge the world-modification warning for this run." end
    local allowed, reason = T.availability(definition,parameters)
    if not allowed then return false, reason end
    -- Observation and diagnostic-metadata capture need no native-fixture token
    -- or gameplay RNG draw. diagnosticWrite does not bypass cleanup-failure gating.
    if not definition.readOnly and not definition.diagnosticWrite then
        T.bootToken = T.bootToken or string.format("%.0f_%.0f",getTimestampMs(),ZombRand(1000000))
    end
    local context = {id=id, definition=definition, status="RUNNING", lines={}, ticks=0,
        cell=getCell(), world=getWorld():getWorld()}
    -- Freeze the explicit selection's flat input table; references remain session-only.
    if parameters then
        context.parameters={}
        for key,value in pairs(parameters) do context.parameters[key]=value end
    end
    function context:log(line)
        line = tostring(line)
        self.lines[#self.lines+1] = line
        if #self.lines > 200 then table.remove(self.lines, 1) end
        print("[SS Tests][" .. self.id .. "] " .. line)
        changed()
    end
    function context:finish(status, summary)
        assert(statuses[status], "Invalid SS test result")
        if self.status ~= "RUNNING" then return end
        self.status, self.summary = status, tostring(summary)
        if self.cleanup then
            local ok, failure = pcall(self.cleanup, self)
            if not ok then
                self.status = "INCONCLUSIVE"
                self.summary = self.summary .. "; cleanup failed: " .. tostring(failure)
                T.cleanupFailure = self
            end
        end
        self:log(self.status .. ": " .. self.summary)
        if T.active == self then T.active = nil end
        changed()
    end
    T.active, T.results[id] = context, context
    context:log("RUNNING: " .. definition.title .. " (user consent received)")
    return true
end
function T.cancel(reason)
    if T.active then T.active:finish("INCONCLUSIVE", reason or "Cancelled; restoration is not guaranteed.") end
end
function T.tick()
    local context = T.active
    if not context then return end
    if not T.enabled() or getCell() ~= context.cell or getWorld():getWorld() ~= context.world then
        T.cancel("Testing was disabled or the world changed."); return
    end
    local human=getSpecificPlayer(0)
    if isClient() or isServer() or getNumActivePlayers()~=1 or not human
        or human:isDead() or not human:getCurrentSquare() then
        T.cancel("Player or game-mode requirements changed during the run.");return
    end
    context.ticks = context.ticks + 1
    if context.ticks > (context.definition.maxTicks or 300) then
        context:finish("INCONCLUSIVE", "Timed out waiting for valid test conditions."); return
    end
    local ok, failure = pcall(function()
        if not context.started then
            context.started = true
            context.definition.run(context)
        elseif context.step then context:step()
        else context:finish("SETUP ERROR", "Test supplied neither a result nor a next step.") end
    end)
    if not ok then context:finish("SETUP ERROR", "Exception: " .. tostring(failure)) end
end

-- Reload-safe callbacks. A new world never resumes a destructive test silently.
if T.tickCallback then Events.OnTick.Remove(T.tickCallback) end
if T.menuCallback then Events.OnMainMenuEnter.Remove(T.menuCallback) end
if T.startCallback then Events.OnGameStart.Remove(T.startCallback) end
T.tickCallback = T.tick
T.menuCallback = function() T.cancel("Returned to the main menu.") end
T.startCallback = function()
    T.cancel("A new gameplay session started.")
    T.cleanupFailure = nil
    T.results = {}
    changed()
end
Events.OnTick.Add(T.tickCallback)
Events.OnMainMenuEnter.Add(T.menuCallback)
Events.OnGameStart.Add(T.startCallback)
