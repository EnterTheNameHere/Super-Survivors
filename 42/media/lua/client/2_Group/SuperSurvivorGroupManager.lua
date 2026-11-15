require "0_Utilities/SuperSurvivorPersistence"
require "2_Group/SuperSurvivorGroup"
require "0_Utilities/SuperSurvivorTextUtilities"

SuperSurvivorGroupManager = {}
SuperSurvivorGroupManager.__index = SuperSurvivorGroupManager
function SuperSurvivorGroupManager:new()
    return setmetatable({Groups = {}, GroupCount = 0}, self)
end
function SuperSurvivorGroupManager:Get(id) return self.Groups[id] end
function SuperSurvivorGroupManager:GetGroupIdFromSquare(square)
    for id, group in pairs(self.Groups) do
        if group:IsInBounds(square) then return id end
    end
    return -1
end
function SuperSurvivorGroupManager:getCount()
    local count = 0
    for _ in pairs(self.Groups) do count = count + 1 end
    return count
end
function SuperSurvivorGroupManager:newGroup()
    local data = SSPersistence.get()
    local id = data.nextGroupID
    data.nextGroupID = id + 1
    local group = SuperSurvivorGroup:new(id)
    self.Groups[id] = group
    self.GroupCount = self:getCount()
    group:Save()
    return group
end
function SuperSurvivorGroupManager:Save()
    for _, group in pairs(self.Groups) do group:Save() end
end
function SuperSurvivorGroupManager:Print()
    for _, group in pairs(self.Groups) do group:Print() end
end
function SuperSurvivorGroupManager:Load()
    self.Groups = {}
    for id in pairs(SSPersistence.get().groups) do
        local group = SuperSurvivorGroup:new(id)
        group:Load()
        self.Groups[id] = group
    end
    self.GroupCount = self:getCount()
end

-- Scenario groups are allocated only when a preset from that scenario is used.
function SuperSurvivorGroupManager:scenarioGroup(key)
    local data = SSPersistence.get()
    local id = data.scenarioGroups[key]
    if id ~= nil then
        assert(self.Groups[id], "[SSR persistence] Missing scenario group " .. key)
        return self.Groups[id]
    end
    local group = self:newGroup()
    data.scenarioGroups[key] = group:getID()
    if key == "HillTop" then
        group:setBounds({11707,11753,7917,7967,0})
        group:setGroupArea("ForageArea",11686,11706,7912,7967,0)
        group:setGroupArea("CorpseStorageArea",11691,11691,7936,7936,0)
        group:setGroupArea("FoodStorageArea",11715,11715,7926,7926,0)
        group:setGroupArea("GuardArea",11707,11711,7938,7946,0)
        group:setGroupArea("ChopTreeArea",11679,11700,7951,7973,0)
        group:setGroupArea("FarmingArea",11741,11746,7939,7949,0)
    elseif key == "Blockade" then
        group:setGroupArea("FarmingArea",12473,12475,4438,4476,0)
        group:setGroupArea("ForageArea",12483,12484,4442,4443,0)
    end
    group:Save()
    return group
end
SSGM = SuperSurvivorGroupManager:new()
