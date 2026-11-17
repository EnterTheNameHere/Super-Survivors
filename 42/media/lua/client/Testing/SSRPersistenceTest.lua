require "Testing/SSRTests"
require "0_Utilities/SuperSurvivorPersistence"

local T, P = SSRTests, SSPersistence
SSRTestsLifecycle = SSRTestsLifecycle or {}
local L = SSRTestsLifecycle
L.KEY = "SSR.Tests.PersistenceLifecycle"
local STAGE, RESUME = "ssr-restart-stage", "ssr-restart-resume"
local function data() return ModData.get(L.KEY) end
local function manifest() local d=data();return d and d.manifest end
local function copy(value)
    if type(value)~="table" then return value end
    local out={};for k,v in pairs(value) do out[k]=copy(v) end;return out
end
local function build() return getCore():getGameAndBuildVersion() end
local function near(a,b) return type(a)=="number" and type(b)=="number" and math.abs(a-b)<0.01 end
local function equal(a,b)
    if type(a)=="number" and type(b)=="number" then return near(a,b) end
    if type(a)~=type(b) then return false end
    if type(a)~="table" then return a==b end
    for k,v in pairs(a) do if not equal(v,b[k]) then return false end end
    for k in pairs(b) do if a[k]==nil then return false end end
    return true
end
local function prerequisites()
    if build()~="42.22.2" then return false,"Reviewed for B42.22.2; detected "..tostring(build()) end
    if getCore():isNoSave() then return false,"A normal save-enabled disposable world is required." end
    if tonumber(tostring(IsoWorld.saveoffsetx))~=0 or tonumber(tostring(IsoWorld.saveoffsety))~=0 then
        return false,"Known zero world save offsets are required."
    end
    if not P.data or not SSM or not SSGM or not SSM:Get(0) then return false,"Wait for the real SSR managers/player wrapper to initialize." end
    return true
end
local function guard()
    local human, singleton = assert(getSpecificPlayer(0),"Human player is no longer loaded"), IsoPlayer.getInstance()
    local x,y,z,file=human:getX(),human:getY(),human:getZ(),human.saveFileName
    local slots={};for i=0,3 do slots[i]=getSpecificPlayer(i) end
    return function()
        for i=0,3 do if slots[i]~=getSpecificPlayer(i) then return false end end
        return human==getSpecificPlayer(0) and singleton==IsoPlayer.getInstance() and file==human.saveFileName
            and near(x,human:getX()) and near(y,human:getY()) and near(z,human:getZ())
    end
end
local function each(collection,visit)
    local iterator=collection:iterator()
    while iterator:hasNext() do visit(iterator:next()) end
end
local function countActors(id)
    local seen, count={},0
    for _,list in ipairs({getCell():getObjectList(),getCell():getAddList(),getCell():getRemoveList()}) do
        each(list,function(actor)
            if not actor:hasModData() then return end -- Do not allocate ModData on unrelated moving objects.
            local md=actor:getModData()
            if (md.ID==id or md.SSRIdentity==id) and not seen[actor] then seen[actor]=true;count=count+1 end
        end)
    end
    local wrappers, records=0,0
    for _,w in pairs(SSM.SuperSurvivors) do if w:Get() and w:getID()==id then wrappers=wrappers+1 end end
    for _,r in pairs(P.get().survivors) do if r.id==id then records=records+1 end end
    return {actors=count,wrappers=wrappers,records=records}
end
local function membership(actor)
    local square=actor:getCurrentSquare()
    return {square=square~=nil, matches=square~=nil and square:getX()==math.floor(actor:getX())
        and square:getY()==math.floor(actor:getY()) and square:getZ()==math.floor(actor:getZ()),
        contains=square~=nil and square:getMovingObjects():contains(actor),
        world=getCell():getObjectList():contains(actor),add=getCell():getAddList():contains(actor),
        remove=getCell():getRemoveList():contains(actor)}
end
local function inventory(container)
    local rows, count={},0
    local function scan(c,path,depth)
        assert(depth<=4,"Inventory nesting exceeds this focused test's capture limit")
        local items=c:getItems()
        for i=0,items:size()-1 do
            local item=items:get(i);count=count+1;assert(count<=256,"Inventory exceeds test capture limit")
            local kind=item:getFullType()
            rows[#rows+1]=path..kind..";condition="..item:getCondition()..";count="..item:getCount()
                ..";probe="..tostring(item:getModData().SSRLifecycleItem)
            if instanceof(item,"InventoryContainer") then scan(item:getInventory(),path..kind.."/",depth+1) end
        end
    end
    scan(container,"",0);table.sort(rows);return table.concat(rows," | ")
end
local function capture(actor)
    local md=actor:getModData();local worn={};local items=actor:getWornItems()
    for i=0,items:size()-1 do worn[#worn+1]=items:get(i):getItem():getFullType() end
    table.sort(worn)
    local primary,secondary=actor:getPrimaryHandItem(),actor:getSecondaryHandItem()
    return {id=md.ID,identity=md.SSRIdentity,generation=md.SSRSnapshot,token=md.SSRLifecycleProbe,
        name=md.Name,descriptorName=actor:getDescriptor():getForename(),group=md.Group,role=md.GroupRole,
        x=actor:getX(),y=actor:getY(),z=actor:getZ(),inventory=inventory(actor:getInventory()),
        primary=primary and primary:getFullType() or "none",secondary=secondary and secondary:getFullType() or "none",
        worn=table.concat(worn," | "),axeXP=actor:getXp():getXP(Perks.Axe),axeLevel=actor:getPerkLevel(Perks.Axe),
        health=actor:getBodyDamage():getOverallBodyHealth(),dead=actor:isDead(),
        hunger=actor:getStats():get(CharacterStat.HUNGER),thirst=actor:getStats():get(CharacterStat.THIRST)}
end
local fields={"id","identity","generation","token","name","descriptorName","group","role","x","y","z",
    "inventory","primary","secondary","worn","axeXP","axeLevel","health","dead"}
local function compare(ctx,label,expected,actual)
    local same=true
    for _,key in ipairs(fields) do
        local ok=equal(expected[key],actual[key]);same=same and ok
        ctx:log(label.."."..key..": expected="..tostring(expected[key]).."; actual="..tostring(actual[key]).."; match="..tostring(ok))
    end
    ctx:log(label.." needs (observed, not a live equality gate): hunger="..tostring(actual.hunger).."; thirst="..tostring(actual.thirst))
    return same
end
local function validManifest(m)
    if not m or m.schema~=1 or type(m.id)~="number" or m.id<=0 or m.id%1~=0
        or type(m.groupID)~="number" or m.groupID<0 or m.groupID%1~=0
        or type(m.boot)~="string" or type(m.build)~="string"
        or type(m.token)~="string" or not m.token:match("^%d+_%d+$") then return false end
    local c=m.checkpoint;local saved=c and c.registry and c.registry.saved
    return saved and type(saved.generation)=="number" and saved.generation>=1 and saved.generation%1==0
        and saved.file=="SSR_Survivor_"..m.id.."_"..saved.generation..".bin" and c.actor and c.group
end
local function stageAvailable()
    local ok,reason=prerequisites();if not ok then return false,reason end
    local m=manifest()
    if m and (m.phase=="armed" or m.phase=="saved") then return false,"An existing fixture is pending. Save/restart and resume it first." end
    return true
end
local function resumeAvailable()
    local ok,reason=prerequisites();if not ok then return false,reason end
    local m=manifest()
    if not m or not validManifest(m) then return false,"Stage a fixture and save normally first. "..tostring(m and m.captureError or "No valid OnSave checkpoint.") end
    if m.boot==T.bootToken then return false,"Still the staging Lua session. Save/exit, fully close the game and restart." end
    if m.build~=build() then return false,"Engine build differs from the staged checkpoint." end
    return true
end

-- Append after requiring production persistence. Never call/reorder/replace P.save.
-- Actor/registry baseline is sampled synchronously in the actual OnSave event,
-- after P.save has published its native snapshot; no AI tick occurs between them.
local function onSave()
    local session=L.session;local m=manifest()
    if not session or not m or m.token~=session.token or m.boot~=T.bootToken then return end
    local ctx=session.context
    local ok,reason=pcall(function()
        assert(T.enabled() and getCell()==session.cell,"Testing disabled or world changed before OnSave")
        local w=assert(SSM:Get(m.id),"Owned fixture is not loaded at OnSave")
        local actor=w:Get();assert(not actor:isLocalPlayer() and actor:getModData().SSRLifecycleProbe==m.token,"Fixture ownership mismatch")
        assert(not actor:isDead(),"Fixture died before save; stage a new controlled roundtrip")
        local r=assert(P.getRecord(m.id));local saved=assert(r.saved,"Production OnSave did not publish a snapshot")
        assert(saved.generation>(m.lastGeneration or 0) and actor:getModData().SSRSnapshot==saved.generation,
            "No new production snapshot observed at this OnSave boundary")
        assert(checkSaveFileExists(saved.file),"Published native snapshot is missing")
        local g=assert(P.get().groups[m.groupID],"Group record missing at OnSave")
        local observation=capture(actor);local counts=countActors(m.id);local placed=membership(actor)
        assert(placed.matches and placed.contains and placed.world and not placed.add and not placed.remove,
            "Fixture square/world membership is not settled at OnSave")
        assert(counts.actors==1 and counts.wrappers==1 and counts.records==1,"Duplicate/missing fixture identity at OnSave")
        m.checkpoint={actor=observation,registry=copy(r),group=copy(g),membership=placed,counts=counts,
            boundary="actual OnSave observer after production P.save",worldHours=getGameTime():getWorldAgeHours()}
        m.lastGeneration=saved.generation;m.phase="saved";m.captureError=nil
        ctx:log("ACTUAL OnSave checkpoint: ID="..m.id.."; group="..m.groupID.."; file="..saved.file.."; generation="..saved.generation)
        ctx:log("OnSave XYZ="..observation.x..","..observation.y..","..observation.z.."; inventory="..observation.inventory)
        ctx:log("Checkpoint updated at each normal save in this staging session. Exit normally, fully close/restart, then explicitly resume.")
    end)
    if not ok then
        m.checkpoint=nil;m.phase="capture-error";m.captureError=tostring(reason)
        ctx:log("INCONCLUSIVE OnSave capture: "..tostring(reason)..". No valid checkpoint; do not treat staging as a pass.")
    end
end
if L.saveCallback then Events.OnSave.Remove(L.saveCallback) end
L.saveCallback=onSave;Events.OnSave.Add(onSave)
if L.startCallback then Events.OnGameStart.Remove(L.startCallback) end
L.startCallback=function() L.session=nil end
Events.OnGameStart.Add(L.startCallback)

T.register({id=STAGE,order=10,title="SSR persistence - stage one survivor and group",
    description="Create a real SSR-managed survivor/group with a unique marker, pencil, equipped hammer and Axe XP. The actor remains in the world. Arm observation at actual OnSave (not a staging baseline), then save/exit normally and fully close/restart. Staging is INCONCLUSIVE, not a persistence pass. Do not interact with the fixture or leave its area before saving.",
    requirements="Disposable B42.22.2 single-player world; initialized SSR managers; nearby free loaded floor; normal saves.",
    risk="Creates persistent SSR actor/group/items and native snapshots. Old fixtures remain; no automatic deletion or restoration.",
    available=stageAvailable,
    run=function(ctx)
        ctx.step=function(self)
            if not getCell():isSafeToAdd() then return end
            local allowed,reason=stageAvailable();if not allowed then self:finish("SETUP ERROR",reason);return end
            local human=assert(getSpecificPlayer(0),"Human player is no longer loaded");local tile
            for _,o in ipairs({{2,0},{0,2},{-2,0},{0,-2},{3,1},{-3,-1}}) do
                local s=getCell():getGridSquare(math.floor(human:getX())+o[1],math.floor(human:getY())+o[2],math.floor(human:getZ()))
                if s and s:getFloor() and s:isFree(false) then tile=s;break end
            end
            if not tile then self:finish("SETUP ERROR","Move to an open area with a nearby free floor tile.");return end
            local unchanged=guard();local creating=false
            self.cleanup=function() assert(not creating,"SSR construction threw before returning a handle; inspect disposable world and restart")
                assert(unchanged(),"Human guard changed; no restoration attempted") end
            local token=string.format("%.0f_%.0f",getTimestampMs(),ZombRand(1000000))
            local m={schema=1,token=token,boot=T.bootToken,build=build(),phase="setting-up"}
            ModData.getOrCreate(L.KEY).manifest=m
            local nextID=P.get().nextSurvivorID
            creating=true;local w=SSM:spawnSurvivor(false,tile)
            assert(w and w:Get(),"SSR constructor did not return an actor/wrapper handle")
            creating=false
            assert(w:getID()==nextID and nextID>0,"SSR did not return the newly allocated survivor")
            local actor=w:Get();assert(actor~=human and not actor:isLocalPlayer(),"Refusing to modify a human actor")
            m.id=w:getID();actor:getModData().SSRLifecycleProbe=token
            w:setName("SSR Persistence "..token);w:StopWalk();w:Wait(100000000)
            local pencil=assert(actor:getInventory():AddItem("Base.Pencil"));pencil:getModData().SSRLifecycleItem=token
            local hammer=assert(actor:getInventory():AddItem("Base.Hammer"));hammer:getModData().SSRLifecycleItem=token
            actor:setPrimaryHandItem(hammer);actor:getXp():AddXP(Perks.Axe,50)
            local group=SSGM:newGroup();m.groupID=group:getID()
            group:addMember(w,"Worker");group:setLeader(m.id);group:Save()
            assert(unchanged(),"Human guard changed during fixture setup")
            local record=P.getRecord(m.id);m.lastGeneration=record.saved and record.saved.generation or 0
            m.phase="armed";L.session={token=token,cell=getCell(),context=self}
            self:log("Fixture created via ordinary SSR APIs: survivor="..m.id.."; group="..m.groupID.."; token="..token.."; Z="..actor:getZ())
            self:log("No save baseline yet and no forced P.save. Close this window, save/exit normally, fully close/restart game, reload same world, explicitly select resume.")
            self:finish("INCONCLUSIVE","Fixture staged; waiting for actual game OnSave checkpoint and user-confirmed restart. Fixtures intentionally remain.")
        end
    end})

T.register({id=RESUME,order=20,title="SSR persistence - resume (I fully restarted the game)",maxTicks=600,
    description="Selecting and running this entry explicitly confirms you fully closed and restarted the game after staging. New consent required. Compare the OnSave baseline, exact native snapshot loaded into an isolated reader, registry/group, real SSR reconstructed actor and counts. Never forces production loading or saves; ordinary AI may have changed live state, which is reported as inconclusive drift.",
    requirements="Saved OnSave checkpoint from this world; different Lua session; actual user-confirmed full restart; saved tile loaded.",
    risk="Creates/removes one temporary unplaced native snapshot reader. Real test survivor/group and snapshot files remain. No deletion of other actors/groups.",
    available=resumeAvailable,
    run=function(ctx)
        local m=assert(manifest(),"Staged manifest disappeared");m.phase="compared"
        ctx:log("User confirmed full game restart by running this entry. Lua-session change alone is not process-restart proof.")
        ctx.step=function(self)
            if not getCell():isSafeToAdd() then return end
            local allowed,reason=resumeAvailable();if not allowed then self:finish("SETUP ERROR",reason);return end
            local c=m.checkpoint;local r=P.getRecord(m.id)
            if not r then self:finish("FAILED","Registry: test survivor record missing.");return end
            if r.state=="dead" then self:finish("INCONCLUSIVE","Fixture died after checkpoint; this roundtrip cannot distinguish death from loading drift.");return end
            if r.issue then self:finish("FAILED","Production registry/loading issue: "..r.issue);return end
            if not equal(r.saved,c.registry.saved) then self:finish("INCONCLUSIVE","Native snapshot pointer changed since OnSave checkpoint; a newer save prevents this exact reconstruction comparison.");return end
            local pos=c.actor
            if not getCell():getGridSquare(math.floor(pos.x),math.floor(pos.y),math.floor(pos.z)) then
                self:finish("INCONCLUSIVE","Saved tile is unloaded. Return near saved XYZ "..pos.x..","..pos.y..","..pos.z.." and explicitly retry.");return
            end
            if not checkSaveFileExists(c.registry.saved.file) then self:finish("FAILED","Exact native checkpoint file is missing.");return end
            local w=SSM:Get(m.id)
            if not w then
                if self.ticks<300 then return end
                self:finish("FAILED","Saved tile loaded but ordinary SSR reconstruction did not produce a wrapper after 300 ticks.");return
            end
            local actor=w:Get();assert(actor~=getSpecificPlayer(0) and not actor:isLocalPlayer(),"Fixture points to human; refusing reader setup")
            local unchanged=guard();local reader,constructing
            local function removeReader()
                if not reader then return end
                assert(getCell()==self.cell and self.cell:isSafeToAdd(),"Reader cleanup cannot use a different/unsafe cell")
                assert(reader~=getSpecificPlayer(0) and not reader:isLocalPlayer(),"Refusing local-player cleanup")
                reader:removeFromWorld();reader:removeFromSquare()
                local state=membership(reader)
                assert(not state.world and not state.add and not state.remove and not state.square,"Native reader remains registered")
                reader=nil;self:log("Temporary native reader detached; no real SSR survivor/group removed.")
            end
            self.cleanup=function() removeReader();assert(not constructing,"Reader constructor did not return a handle; restart")
                assert(unchanged(),"Human/slot guard changed; no restoration attempted") end
            assert(checkSaveFileExists(c.registry.saved.file),"Exact checkpoint native file missing")
            constructing=true;reader=IsoPlayer.new(getCell());assert(reader,"Reader constructor returned nil");constructing=false
            assert(not reader:isLocalPlayer(),"Reader is local")
            local initial=membership(reader)
            if initial.world or initial.add or initial.remove or initial.square then
                self:finish("INCONCLUSIVE","Cell-only reader acquired initial world/square membership; raw read branch skipped.");return
            end
            reader:setNpc(true);reader:setBlockMovement(true)
            reader:load(getSaveDir()..c.registry.saved.file)
            local native=capture(reader);removeReader()
            -- Inspect/count the real actor only after the duplicate-ID reader is detached.
            local live=capture(actor);local counts=countActors(m.id);local placed=membership(actor)
            local nativeOK=compare(self,"Native file vs OnSave",c.actor,native)
            local liveOK=compare(self,"SSR actor vs OnSave",c.actor,live)
            local groupRecord=P.get().groups[m.groupID];local group=SSGM:Get(m.groupID)
            local registryOK=r.id==m.id and r.name==c.registry.name and r.groupID==m.groupID and r.role==c.registry.role
                and equal(r.saved.position,{x=pos.x,y=pos.y,z=pos.z})
            local groupOK=equal(groupRecord,c.group) and group and equal(group:getMemberIDs(),c.group.members)
                and group.Leader==c.group.leader
            local membershipOK=placed.matches and placed.contains and placed.world and not placed.add and not placed.remove
            local unique=counts.actors==1 and counts.wrappers==1 and counts.records==1
            local humanOK=unchanged()
            self:log("Registry match="..tostring(registryOK).."; group record/runtime roster/leader match="..tostring(groupOK))
            self:log("ID counts actor/wrapper/record="..counts.actors.."/"..counts.wrappers.."/"..counts.records.."; square/world membership="..tostring(membershipOK))
            self:log("Human identity/XYZ/singleton/save filename/all four slots unchanged="..tostring(humanOK))
            self:log("Saved Z="..pos.z.."; live Z="..live.z..". No forced vertical differential; this is not a general Z-range test.")
            self.observations={nativeMatch=nativeOK,liveMatch=liveOK,registryMatch=registryOK,groupMatch=not not groupOK,
                membership=placed,counts=counts,humanUnchanged=humanOK}
            if not nativeOK or not registryOK or not groupOK or not unique or not humanOK then
                self:finish("FAILED","Checkpoint comparison failed; see native/metadata/group/count evidence. OnSave hooks or later world interactions must be considered before attributing a production defect.")
            elseif not liveOK or not membershipOK then
                self:finish("INCONCLUSIVE","Native checkpoint/metadata match, but live actor differs or moved. Ordinary AI/environment before explicit resume prevents attributing this to reconstruction.")
            else
                self:finish("PASSED","One real SSR survivor/group restart checkpoint matched native file, registry and loaded actor; human guards/reader cleanup passed. Streaming/death/multiple groups remain untested.")
            end
        end
    end})
