require "Testing/SSRTests"

-- One user-run observation; no callbacks, actor mutations or test fixtures.
SSRCombatSnapshot=SSRCombatSnapshot or {}
local C=SSRCombatSnapshot
local ID="combat-existing-snapshot"
local function read(object,method,...)
    if not object then return nil,false,"object absent" end
    local args={...}
    local ok,found,value=pcall(function()
        local fn=object[method]
        if not fn then return false,nil end
        return true,fn(object,unpack(args))
    end)
    if not ok then return nil,false,"getter failed: "..tostring(found) end
    return value,found,not found and "getter unavailable: "..method or nil
end
local function existingModData(actor)
    local has,known=read(actor,"hasModData")
    if not known or not has then return nil end
    local md,ok=read(actor,"getModData") -- guarded: never allocate actor ModData
    return ok and md or nil
end
local function validate(p)
    local id=p and p.id
    if type(id)~="number" or id~=id or id<1 or id>2147483647 or id~=math.floor(id) then
        return nil,"Explicitly select an existing SSR survivor ID > 0."
    end
    if p.world~=getWorld():getWorld() or p.cell~=getCell() then return nil,"Selection belongs to another world/session; refresh survivors." end
    local wrapper=SSM and SSM.SuperSurvivors and SSM.SuperSurvivors[id]
    local actor=wrapper and wrapper.player
    if not actor or wrapper~=p.wrapper or actor~=p.actor then return nil,"Selected survivor unloaded/replaced; refresh and select again." end
    if not instanceof(actor,"IsoPlayer") then return nil,"Selected SSR actor is not an IsoPlayer survivor." end
    if actor==IsoPlayer.getInstance() or id==SSM.MainPlayer then return nil,"Human/control actor cannot be inspected as an NPC." end
    for i=0,3 do if actor==getSpecificPlayer(i) then return nil,"Local player cannot be inspected as an NPC." end end
    local localPlayer,localKnown=read(actor,"isLocalPlayer")
    if not localKnown or localPlayer~=false then return nil,"Cannot verify selected actor is nonlocal." end
    local dead,deadKnown=read(actor,"isDead")
    if not deadKnown or dead~=false then return nil,"Selected survivor is dead or life state unavailable." end
    local cell=read(actor,"getCell")
    local square=read(actor,"getCurrentSquare")
    if cell~=getCell() or not square then return nil,"Selected survivor is not loaded in this cell." end
    local objects=read(cell,"getObjectList") -- native Set; no traversal or global Objects rewrite
    local members=read(square,"getMovingObjects")
    if read(objects,"contains",actor)~=true or read(members,"contains",actor)~=true then
        return nil,"Selected survivor is not registered in world/square."
    end
    local md=existingModData(actor)
    if not md or md.ID~=id then return nil,"SSR wrapper/actor ID ownership cannot be verified." end
    return {id=id,actor=actor,wrapper=wrapper,md=md,square=square}
end

function C.choices()
    local result,scanned,limited={},0,false
    if not getCell() or not getWorld() then return result,false end
    for id,wrapper in pairs(SSM and SSM.SuperSurvivors or {}) do
        scanned=scanned+1
        if scanned>256 or #result>=128 then limited=true;break end
        if type(wrapper)=="table" then
            local p={id=id,wrapper=wrapper,actor=wrapper.player,cell=getCell(),world=getWorld():getWorld()}
            local ok,selection=pcall(validate,p)
            if ok and selection then
                local name=selection.md.Name
                p.label="ID "..id..(type(name)=="string" and (" - "..name:sub(1,60)) or "")
                result[#result+1]=p
            end
        end
    end
    table.sort(result,function(a,b) return a.id<b.id end)
    return result,limited
end
local function available(parameters)
    if getCore():getGameAndBuildVersion()~="42.22.2" then return false,"Snapshot getter safety reviewed for B42.22.2 only." end
    local selection,reason=validate(parameters)
    return selection~=nil,reason or "Available: one read-only snapshot; capture while observing the symptom."
end
C.read=read
C.validate=validate
function C.selection(wrapper)
    local actor=wrapper and wrapper.player
    local md=existingModData(actor)
    return {id=md and md.ID,wrapper=wrapper,actor=actor,cell=getCell(),world=getWorld():getWorld()}
end
function C.available(parameters)
    return SSRTests.availability(SSRTests.definitions[ID],parameters)
end
local function capture(ctx)
    local selection,reason=validate(ctx.parameters)
    if not selection then ctx:finish("SETUP ERROR",reason);return end
    local actor,npc,md=selection.actor,selection.wrapper,selection.md
    local target=npc.LastEnemeySeen
    local fields={}
    local function put(name,value,known,why)
        if known==false then fields[name]="UNAVAILABLE ("..tostring(why)..")"
        elseif value==nil then fields[name]="<null>"
        elseif type(value)=="number" or type(value)=="boolean" or type(value)=="string" then fields[name]=tostring(value):sub(1,320)
        else fields[name]="UNAVAILABLE (not scalar)" end
    end
    local function get(name,object,method,...)
        local value,known,why=read(object,method,...);put(name,value,known,why)
        return value,known
    end
    local function cached(name,value) put(name,value,value~=nil,"cached field unset") end
    put("capture.timestampMs",getTimestampMs())
    put("capture.world",ctx.world)
    put("capture.engine",getCore():getGameAndBuildVersion())
    get("capture.frame",getWorld(),"getFrameNo")
    cached("capture.modRenderCounter",OnTickTicks)
    if getGameSpeed then put("capture.gameSpeed",getGameSpeed()) else put("capture.gameSpeed",nil,false,"getGameSpeed unavailable") end
    get("capture.worldHours",getGameTime(),"getWorldAgeHours")
    local human=getSpecificPlayer(0)
    get("human.dead",human,"isDead");get("human.asleep",human,"isAsleep")
    local humanSquare,humanSquareKnown=read(human,"getCurrentSquare")
    put("human.squarePresent",humanSquare~=nil,humanSquareKnown,"human square getter unavailable")
    put("ownership.ssrID",selection.id);put("ownership.wrapperActorMatchesSelection",true)
    put("ownership.actorClass","IsoPlayer")
    put("ownership.worldSquareMembershipVerified",true);put("ownership.localSlotsExcluded",true)
    cached("policy.groupID",md.Group);cached("policy.role",md.GroupRole);cached("policy.AIMode",md.AIMode)
    cached("policy.followCharID",md.FollowCharID);cached("policy.followDistance",GFollowDistance)
    cached("policy.attackRange",npc.AttackRange)
    cached("policy.bravery",md.BravePoints);cached("policy.felldown",md.felldown)
    put("policy.needToFollow",nil,false,"policy predicate deliberately not executed")
    put("policy.tooScaredToFight",nil,false,"policy predicate deliberately not executed; cached inputs reported")
    put("policy.groupBraveryBonus",nil,false,"group policy predicate deliberately not executed")
    local group=SSGM and SSGM.Groups and SSGM.Groups[md.Group]
    cached("policy.groupROE",group and group.ROE)
    put("scheduler.AIEnabled",npc.MyTaskManager and npc.MyTaskManager.AIEnabled~=false)
    put("scheduler.updateFilterPresent",SSM.UpdateFilter~=nil)
    put("scheduler.updateFilterAccepted",nil,false,"callback deliberately not invoked")
    cached("scheduler.MainPlayer",SSM.MainPlayer)
    for _,key in ipairs({"Reducer","UpdateDelayTicks","WaitTicks","AtkTicks","WalkingPermitted","TriggerHeldDown","SwipeStateTicks"}) do
        cached("scheduler."..key,npc[key])
    end
    for _,key in ipairs({"seenCount","dangerSeenCount","EnemiesOnMe"}) do cached("perception."..key,npc[key]) end
    put("perception.targetPresent",target~=nil)
    local function position(prefix,object)
        local x=get(prefix..".x",object,"getX")
        local y=get(prefix..".y",object,"getY")
        local z=get(prefix..".z",object,"getZ")
        return x,y,z
    end
    local x,y,z=position("actor",actor)
    local tx,ty,tz=position("target",target)
    local targetSquare=read(target,"getCurrentSquare")
    local room,roomKnown=read(selection.square,"getRoom")
    local targetRoom,targetRoomKnown=read(targetSquare,"getRoom")
    put("actor.roomPresent",room~=nil,roomKnown,"room getter unavailable")
    put("target.roomPresent",targetRoom~=nil,targetRoomKnown,"no target square/room getter")
    put("target.sameRoom",room==targetRoom,roomKnown and targetRoomKnown,"room comparison unavailable")
    if target then
        put("target.class",instanceof(target,"IsoZombie") and "IsoZombie" or (instanceof(target,"IsoPlayer") and "IsoPlayer" or "other"))
        get("target.dead",target,"isDead")
        if type(x)=="number" and type(y)=="number" and type(z)=="number" and type(tx)=="number" and type(ty)=="number" and type(tz)=="number" then
            put("target.distance",math.sqrt((x-tx)^2+(y-ty)^2+2*(z-tz)^2))
            put("target.deltaZ",tz-z)
            get("native.IsAttackRange",actor,"IsAttackRange",tx,ty,tz)
        else put("native.IsAttackRange",nil,false,"target/actor coordinates unavailable") end
    else put("target.class","none at snapshot");put("native.IsAttackRange",nil,false,"no target at snapshot") end
    local tm=npc.MyTaskManager
    cached("queue.taskCount",tm and tm.TaskCount);cached("queue.updateCount",tm and tm.TaskUpdateCount)
    cached("queue.updateLimit",tm and tm.TaskUpdateLimit)
    local front=tm and tm.Tasks and tm.Tasks[0]
    put("queue.front",front and front.Name or "None")
    local count=tm and tm.TaskCount
    if type(count)=="number" and count>=0 and count==math.floor(count) then
        for i=0,math.min(count,12)-1 do cached("queue."..i,tm.Tasks and tm.Tasks[i] and tm.Tasks[i].Name) end
        put("queue.truncated",count>12)
    else put("queue.names",nil,false,"task count unavailable/invalid") end
    local primary,primaryKnown=read(actor,"getPrimaryHandItem")
    put("weapon.primaryPresent",primary~=nil,primaryKnown,"primary getter unavailable")
    local handWeapon=primary and instanceof(primary,"HandWeapon") or false
    put("weapon.equippedHandWeapon",handWeapon,primaryKnown,"primary getter unavailable")
    get("weapon.fullType",primary,"getFullType");get("weapon.condition",primary,"getCondition")
    if handWeapon then
        for _,method in ipairs({"isAimedFirearm","getCurrentAmmoCount","isContainsClip","isRoundChambered","isJammed"}) do
            get("weapon."..method,primary,method)
        end
    else put("weapon.ammoState",nil,false,"no equipped HandWeapon") end
    for _,method in ipairs({"isNpc","isLocalPlayer","isDead","isAsleep","isRunning","isBlockMovement",
        "isAiming","isAttackStarted","isInitiateAttack","isPerformingAttackAnimation","isPerformingShoveAnimation",
        "isAimAtFloor","isDoShove","isAuthorizedHandToHand","isAuthorizedHandToHandAction",
        "canPerformHandToHandCombat","isWeaponReady","getCurrentStateName"}) do get("native."..method,actor,method) end
    put("native.AIComponent.controlVars",nil,false,"no verified Lua Class token for getECSComponent(AIComponent.class); no reflection or state mutation attempted")
    local state,stateKnown=read(actor,"getCurrentState")
    local swipe,swipeKnown
    if SwipeStatePlayer then swipeKnown,swipe=pcall(SwipeStatePlayer.instance) end
    put("native.swingState",state==swipe,stateKnown and swipeKnown==true,"state getter/SwipeStatePlayer unavailable")
    local body=read(actor,"getBodyDamage")
    get("actor.health",body,"getOverallBodyHealth")
    local parts=read(body,"getBodyParts")
    local size,sizeKnown=read(parts,"size")
    local injuries,injuriesKnown=0,sizeKnown and type(size)=="number" and size>=0 and size<=64
    if injuriesKnown then
        for i=0,size-1 do
            local part=read(parts,"get",i)
            local injured,injuredKnown=read(part,"HasInjury")
            local bandaged,bandagedKnown=read(part,"bandaged")
            injuriesKnown=injuriesKnown and injuredKnown and bandagedKnown
            if injured and not bandaged then injuries=injuries+1 end
        end
    end
    put("actor.unbandagedInjuries",injuries,injuriesKnown==true,"body-part getters unavailable/invalid count; no injury predicate executed")
    -- Recheck ownership after all reads. A disappearing/replaced actor is not adopted.
    local stillValid=validate(ctx.parameters)
    if not stillValid then ctx:finish("INCONCLUSIVE","Selection changed during observation; snapshot discarded.");return end
    local names={};for name in pairs(fields) do names[#names+1]=name end;table.sort(names)
    for _,name in ipairs(names) do ctx:log(name.."="..fields[name]) end
    ctx.observations={id=selection.id,fields=fields,targetPresent=target~=nil,fieldCount=#names}
    ctx:log("Cached AI data sampled without refreshing perception or executing predicates/tasks. Native flags describe this instant, not an observed attack attempt/animation/hit history.")
    ctx:finish("INCONCLUSIVE",target and "Existing target/task/weapon/native state recorded. Request entry/rejection and transient cancellation are not traced; no cause or successful hit inferred."
        or "No target at snapshot. This alone does not prove broken perception; observe the NPC near a zombie and run another explicit snapshot.")
end
-- Dedicated observation endpoint for contextual UI. Does not start/bypass a
-- test, change consent, or alter SSRTests.active/results/cleanupFailure.
function C.inspect(parameters)
    local allowed,reason=C.available(parameters)
    if not allowed then return nil,reason end
    local ctx={parameters=parameters,world=getWorld():getWorld(),lines={}}
    function ctx:log(line)
        self.lines[#self.lines+1]=line
        print("[SS Tests]["..ID.."] "..line)
    end
    function ctx:finish(status,summary) self.status=status;self.summary=summary;self:log(status..": "..summary) end
    ctx:log("RUNNING: Combat - inspect existing survivor (explicit contextual observation; no test started)")
    local ok,failure=pcall(capture,ctx)
    if not ok then return nil,"Observation unavailable: "..tostring(failure) end
    return ctx
end
SSRTests.register({id=ID,order=60,readOnly=true,survivorSelection=true,title="Combat - inspect existing survivor",
    description="Explicitly select a loaded SSR NPC below, then Run while you observe the combat problem. Reads cached perception/task/weapon and verified native flags once. Does not force perception, task decisions, attacks or hits. No target at snapshot does not prove broken perception.",
    requirements="Single-player, one human, B42.22.2, existing owned loaded living SSR ID > 0 outside all local slots. Refresh survivors if the selected actor unloaded or changed.",
    risk="Observation only. No world/save/AI/actor changes, fixtures, automatic sampling or combat requests. Existing per-run acknowledgment remains.",
    available=available,run=capture})
