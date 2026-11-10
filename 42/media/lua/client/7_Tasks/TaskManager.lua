TaskManager = {}
TaskManager.__index = TaskManager

function TaskManager:new(superSurvivor)
    return setmetatable({parent = superSurvivor, Tasks = {}, TaskCount = 0,
        TaskUpdateCount = 0, TaskUpdateLimit = 0, CurrentTask = "None",
        LastTask = "None", LastLastTask = "None"}, self)
end

-- Keep the historical zero-based public queue; always detach before cleanup.
local function cancel(task)
    local cleanup = task and (task.OnCancel or task.ForceComplete or task.ForceFinish or task.OnComplete)
    if cleanup then cleanup(task) end
end

local function cancelAll(tasks)
    local firstError
    for _, task in ipairs(tasks) do
        local ok, reason = pcall(cancel, task)
        if not ok and not firstError then firstError = reason end
    end
    -- Release all remaining tasks even if one cleanup fails; retain the error.
    if firstError then error(firstError) end
end

function TaskManager:setTaskUpdateLimit(value)
    self.TaskUpdateLimit = value
    self.TaskUpdateCount = 0
end

function TaskManager:AddToTop(task)
    if not task then return false end
    self.LastLastTask = self.LastTask
    self.LastTask = self:getCurrentTask()
    for i = self.TaskCount, 1, -1 do self.Tasks[i] = self.Tasks[i - 1] end
    self.Tasks[0] = task
    self.TaskCount = self.TaskCount + 1
    self.TaskUpdateCount = 0
    self.CurrentTask = task.Name
end

function TaskManager:AddToBottom(task)
    if not task then return false end
    self.Tasks[self.TaskCount] = task
    self.TaskCount = self.TaskCount + 1
    self.CurrentTask = self:getCurrentTask()
end

function TaskManager:Display()
    for i = 0, self.TaskCount - 1 do
        if self.Tasks[i] then print(self.Tasks[i].Name) end
    end
end

function TaskManager:clear()
    local previous = {}
    for i = 0, self.TaskCount - 1 do
        if self.Tasks[i] then table.insert(previous, self.Tasks[i]) end
    end
    self.Tasks, self.TaskCount = {}, 0
    self.TaskUpdateCount, self.TaskUpdateLimit = 0, 0
    self.CurrentTask = "None"
    cancelAll(previous)
end

function TaskManager:removeCurrent(cancelled)
    local previous = self.Tasks[0]
    for i = 1, self.TaskCount - 1 do self.Tasks[i - 1] = self.Tasks[i] end
    self.Tasks[math.max(0, self.TaskCount - 1)] = nil
    self.TaskCount = math.max(0, self.TaskCount - 1)
    self.TaskUpdateCount = 0
    self.CurrentTask = self:getCurrentTask()
    if cancelled then cancel(previous)
    elseif previous and previous.OnComplete then previous:OnComplete() end
end

function TaskManager:moveDown()
    while self.TaskCount > 0 do
        local task = self.Tasks[0]
        if task and not task:isComplete() then break end
        self:removeCurrent(false)
    end
    self.TaskUpdateCount = 0
    return false
end

function TaskManager:getCurrentTask()
    return self.Tasks[0] and self.Tasks[0].Name or "None"
end

function TaskManager:getTask() return self.Tasks[0] end
function TaskManager:getThisTask(index) return self.Tasks[index] end

function TaskManager:removeTaskFromName(name)
    local remaining, removed = {}, {}
    local count = 0
    for i = 0, self.TaskCount - 1 do
        local task = self.Tasks[i]
        if task and task.Name == name then table.insert(removed, task)
        elseif task then remaining[count] = task; count = count + 1 end
    end
    local activeChanged = remaining[0] ~= self.Tasks[0]
    self.Tasks, self.TaskCount = remaining, count
    self.CurrentTask = self:getCurrentTask()
    if activeChanged then self.TaskUpdateCount = 0 end
    cancelAll(removed)
end

function TaskManager:getTaskFromName(name)
    for i = 0, self.TaskCount - 1 do
        if self.Tasks[i] and self.Tasks[i].Name == name then return self.Tasks[i] end
    end
end

function TaskManager:update()
    -- Explicit task execution can be separated from autonomous decisions.
    if self.AIEnabled ~= false then
        self = AIManager(self)
        if not self then return end
    end
    local task = self.Tasks[0]
    if not task then self:moveDown(); return end
    if task.isValid and not task:isValid() then
        self:removeCurrent(true)
    elseif task:isComplete() then
        self:moveDown()
    elseif self.TaskUpdateLimit and self.TaskUpdateLimit > 0 and self.TaskUpdateCount >= self.TaskUpdateLimit then
        self:removeCurrent(true)
    else
        task:update()
        -- An update can insert/replace tasks; don't charge the new task for it.
        if self.Tasks[0] == task then self.TaskUpdateCount = self.TaskUpdateCount + 1 end
    end
end
