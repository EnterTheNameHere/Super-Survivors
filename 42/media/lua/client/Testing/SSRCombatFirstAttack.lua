require "Testing/SSRCombatTrace"
if SSRCombatFirstAttack and SSRCombatFirstAttack.stop then SSRCombatFirstAttack.stop(nil,"observer module reloaded") end
SSRCombatFirstAttack=SSRCombatFirstAttack or {}
local F,C,R=SSRCombatFirstAttack,SSRCombatSnapshot,SSRCombatTrace
F.active,F.last=nil,nil -- preserve table identity held by existing UI callbacks
local MAX_MS,MAX_TICKS,MAX_LINES,MAX_REQUESTS=10000,600,120,8
local function pack(...) return {n=select("#",...),...} end
local function scalar(v)
    local k=type(v)
    if v~=nil and k~="boolean" and k~="number" and k~="string" then return "<non-scalar>" end
    return tostring(v):gsub("[%c]"," "):sub(1,160)
end
local function value(object,method,...)
    local v,ok=C.read(object,method,...)
    return ok and scalar(v) or "UNAVAILABLE"
end
local function state(p)
    local a,npc=p.actor,p.wrapper
    local target=npc.LastEnemeySeen
    local front=npc.MyTaskManager and npc.MyTaskManager.Tasks and npc.MyTaskManager.Tasks[0]
    local s={started=value(a,"isAttackStarted"),initiate=value(a,"isInitiateAttack"),
        animation=value(a,"isPerformingAttackAnimation"),shove=value(a,"isPerformingShoveAnimation"),
        aiming=value(a,"isAiming"),running=value(a,"isRunning"),blocked=value(a,"isBlockMovement"),
        ready=value(a,"isWeaponReady"),state=value(a,"getCurrentStateName"),
        task=scalar(front and front.Name or "None"),cooldown=scalar(npc.AtkTicks),wait=scalar(npc.WaitTicks),
        target=target and "present" or "none",range="UNAVAILABLE",targetPos="UNAVAILABLE"}
    local current,known=C.read(a,"getCurrentState")
    local swipeKnown,swipe
    if SwipeStatePlayer then swipeKnown,swipe=pcall(SwipeStatePlayer.instance) end
    s.swing=known and swipeKnown and tostring(current==swipe) or "UNAVAILABLE"
    local x,xok=C.read(target,"getX");local y,yok=C.read(target,"getY");local z,zok=C.read(target,"getZ")
    if xok and yok and zok and type(x)=="number" and type(y)=="number" and type(z)=="number" then
        s.range=value(a,"IsAttackRange",x,y,z);s.targetPos=scalar(x)..","..scalar(y)..","..scalar(z)
    end
    s.weapon=value(C.read(a,"getPrimaryHandItem"),"getFullType")
    return s,target
end
local function textState(s)
    return "started="..s.started.." initiate="..s.initiate.." animation="..s.animation.." swing="..s.swing
        .." shove="..s.shove.." aiming="..s.aiming.." running="..s.running.." blocked="..s.blocked
        .." ready="..s.ready.." state="..s.state.." task="..s.task.." weapon="..s.weapon
        .." target="..s.target.." targetPos="..s.targetPos.." range="..s.range.." wait="..s.wait.." cooldown="..s.cooldown
end
local function emit(r,line)
    if r.lines>=MAX_LINES then return end
    r.lines=r.lines+1
    line="t="..scalar(getTimestampMs()).." frame="..value(getWorld(),"getFrameNo").." "..line
    r.output[#r.output+1]=line
    print("[SS Combat][first-natural-attack] "..line)
end
function F.stop(owner,reason)
    local r=F.active
    if not r or (owner and r.owner~=owner) then return false end
    F.active=nil
    local restored={}
    for _,hook in ipairs(r.hooks) do
        local owns=rawget(r.p.wrapper,hook.name)==hook.fn
        if owns then rawset(r.p.wrapper,hook.name,hook.raw) end
        restored[#restored+1]=hook.name..":"..tostring(owns)
    end
    for _,binding in ipairs(r.bindings) do pcall(binding.event.Remove,binding.fn) end
    r.finished=true;r.reason=reason or "stopped"
    pcall(emit,r,"END "..r.reason.." requests="..r.requests.." stopWalks="..r.walks.." accepted="..r.accepted
        .." swingEvents="..r.swings.." hitPointEvents="..r.hitPoints.." sampledFalseToTrue="..r.rises
        .." restored="..table.concat(restored,","))
    pcall(emit,r,"INCONCLUSIVE: earliest OBSERVED only; no first-ever provenance, exact setter or attributable damage inferred.")
    F.last=r
    return true
end
local function log(r,line)
    if F.active~=r then return end
    if r.lines>=MAX_LINES-2 then F.stop(r.owner,"120 line cap (censored)");return end
    emit(r,line:sub(1,1600))
end
local function sample(r,label,force)
    local s,target=state(r.p)
    -- Moving targets/timers alone must not spend the pre-request log budget.
    -- Their current values are included whenever an actual state/call is logged.
    local fingerprint=table.concat({s.started,s.initiate,s.animation,s.swing,s.shove,s.aiming,
        s.running,s.blocked,s.ready,s.state,s.task,s.weapon,s.target,s.range},"|")
    if r.previous and r.previous.started=="false" and s.started=="true" then
        r.rises=r.rises+1
        log(r,"SAMPLED false->true at "..label.."; exact native setter NOT observed")
    end
    if force or fingerprint~=r.fingerprint or target~=r.target then
        log(r,label.." "..textState(s).." targetRefChanged="..tostring(target~=r.target))
    end
    r.previous,r.fingerprint,r.target=s,fingerprint,target
end
local function protect(r,fn,...)
    local result=pack(pcall(fn,...))
    if not result[1] then pcall(F.stop,r.owner,"observer failure: "..scalar(result[2])) end
    return unpack(result,2,result.n)
end
local function valid(r)
    local ok,why=C.available(r.p)
    if not ok then return false,why end
    if C.read(r.p.actor,"isNpc")~=true then return false,"actor no longer NPC-controlled" end
    if r.owner.ssCombatSelection~=r.binding or C.read(r.owner,"getIsVisible")~=true then
        return false,"information window hidden or rebound"
    end
    if SSM.MainPlayer~=r.main then return false,"human/control identity changed" end
    for i=0,3 do if getSpecificPlayer(i)~=r.slots[i] then return false,"local player slots changed" end end
    for _,hook in ipairs(r.hooks) do
        if rawget(r.p.wrapper,hook.name)~=hook.fn then return false,"observed Lua method replaced: "..hook.name end
    end
    return true
end
local function watchdog(r,checkAborted)
    if F.active~=r then return false end
    if checkAborted and r.inFlight>0 then F.stop(r.owner,"natural call aborted; original error was not intercepted");return false end
    local ok,why=valid(r)
    if not ok then F.stop(r.owner,"guard: "..scalar(why));return false end
    if getTimestampMs()>=r.deadline then F.stop(r.owner,"10 second deadline");return false end
    return true
end
local function follow(r,why)
    if not r.followAt then r.followAt=r.ticks+3;log(r,"FOLLOW-UP 3 ticks after "..why) end
end
local function install(r,name)
    local npc=r.p.wrapper
    local original=npc[name]
    local hook={name=name,raw=rawget(npc,name)}
    hook.fn=function(self,...)
        if self~=npc or F.active~=r then return original(self,...) end
        local allowed=protect(r,watchdog,r,false)
        if not allowed then return original(self,...) end
        local request=name=="requestCombatAttack"
        if request and r.requests>=MAX_REQUESTS then
            F.stop(r.owner,"8 natural request cap (censored)");return original(self,...)
        end
        if request then r.requests=r.requests+1 else r.walks=r.walks+1 end
        local number=request and r.requests or r.walks
        local label=(request and "REQUEST" or "STOPWALK").." #"..number
        local args=pack(...)
        if request then protect(r,log,r,label.." victimMatchesCached="..tostring(args[1]==npc.LastEnemeySeen)) end
        protect(r,sample,r,label.." ENTRY depth="..r.inFlight,true)
        -- Direct original call, never pcall/rethrow: preserve Kahlua native errors.
        -- Failed synchronous calls leave depth nonzero for deferred owned cleanup.
        r.inFlight=r.inFlight+1
        local result=pack(original(self,...))
        r.inFlight=r.inFlight-1
        if F.active==r and protect(r,watchdog,r,false) then
            protect(r,sample,r,label.." POST depth="..r.inFlight,true)
            protect(r,log,r,label.." RETURN values="..result.n.." first="..scalar(result[1]).." reason="..scalar(result[2]))
            if request and result[1]==true then
                r.accepted=r.accepted+1;protect(r,follow,r,"first accepted natural request")
            end
            if request and r.requests>=MAX_REQUESTS then F.stop(r.owner,"8 natural request cap (censored)") end
        end
        return unpack(result,1,result.n)
    end
    r.hooks[#r.hooks+1]=hook
    rawset(npc,name,hook.fn)
end
local function add(r,name,fn)
    local event=Events[name]
    if not event or not event.Add or not event.Remove then error(name.." observation API unavailable") end
    local guarded=function(...) protect(r,fn,...) end
    r.bindings[#r.bindings+1]={event=event,fn=guarded}
    event.Add(guarded)
end
function F.start(parameters,owner)
    if F.active or R.active then return nil,"Another combat observation is running." end
    local allowed,why=C.available(parameters)
    if not allowed then return nil,why end
    if not owner or owner.ssCombatSelection~=parameters or C.read(owner,"getIsVisible")~=true then
        return nil,"Start from the selected survivor's visible Information window."
    end
    local actor=parameters.actor
    if C.read(actor,"isNpc")~=true then return nil,"Requires a nonlocal NPC-controlled survivor." end
    if C.read(actor,"isAttackStarted")~=false then return nil,"Already attackStarted or unavailable; choose another survivor. No reset performed." end
    if C.read(actor,"isInitiateAttack")~=false or C.read(actor,"isPerformingAttackAnimation")==true then
        return nil,"An initiation/animation is already active; earliest request cannot be observed."
    end
    local current,known=C.read(actor,"getCurrentState")
    local swipeKnown,swipe
    if SwipeStatePlayer then swipeKnown,swipe=pcall(SwipeStatePlayer.instance) end
    if known and swipeKnown and current==swipe then return nil,"Survivor is already in swing state." end
    for _,name in ipairs({"requestCombatAttack","StopWalk"}) do
        if type(parameters.wrapper[name])~="function" then return nil,"Lua method unavailable: "..name end
    end
    local p={id=parameters.id,wrapper=parameters.wrapper,actor=actor,world=parameters.world,cell=parameters.cell}
    local r={p=p,owner=owner,binding=parameters,main=SSM.MainPlayer,slots={},
        ticks=0,lines=0,requests=0,walks=0,accepted=0,swings=0,hitPoints=0,rises=0,inFlight=0,
        output={},hooks={},bindings={},deadline=getTimestampMs()+MAX_MS}
    for i=0,3 do r.slots[i]=getSpecificPlayer(i) end
    F.active=r;F.last=nil
    local ok,failure=pcall(function()
        log(r,"START SSR ID="..p.id.." limits:10s/600ticks/120lines/8natural requests. Observation only; no request forced.")
        log(r,"PROVENANCE earliest OBSERVED only; registry has no verified never-attacked history. False initial flags do not prove first-ever.")
        log(r,"Observe this survivor's natural behavior; keep Information visible. Stop or close to cancel. OnWeaponSwing=entry, HitPoint=collision entry, neither proves damage.")
        sample(r,"INITIAL",true)
        install(r,"requestCombatAttack");install(r,"StopWalk")
        add(r,"OnPlayerUpdate",function(a)
            if a==actor and watchdog(r,false) then sample(r,"EARLY OnPlayerUpdate",false) end
        end)
        add(r,"OnTick",function()
            if not watchdog(r,true) then return end
            r.ticks=r.ticks+1
            sample(r,"TICK",false) -- no repeating heartbeat to exhaust the log before a request
            if F.active~=r then return end
            if r.ticks>=MAX_TICKS then F.stop(owner,"600 tick cap")
            elseif r.followAt and r.ticks>=r.followAt then F.stop(owner,"3 tick follow-up complete") end
        end)
        add(r,"OnRenderTick",function() watchdog(r,true) end) -- deadline/guards, including paused ticks
        add(r,"OnMainMenuEnter",function() F.stop(owner,"main menu") end)
        add(r,"OnGameStart",function() F.stop(owner,"new gameplay session") end)
        add(r,"OnWeaponSwing",function(a)
            if a~=actor or not watchdog(r,false) then return end
            r.swings=r.swings+1;log(r,"EVENT OnWeaponSwing owned actor; state entry, not damage")
            follow(r,"first owned swing event");sample(r,"SWING EVENT",true)
        end)
        add(r,"OnWeaponSwingHitPoint",function(a)
            if a~=actor or not watchdog(r,false) then return end
            r.hitPoints=r.hitPoints+1;log(r,"EVENT OnWeaponSwingHitPoint owned actor; collision entry, not proof of damage")
            follow(r,"first owned hitpoint event");sample(r,"HITPOINT EVENT",true)
        end)
    end)
    if not ok then F.stop(owner,"setup failed: "..scalar(failure));return nil,scalar(failure) end
    if F.active~=r then return nil,"Observation stopped during setup: "..scalar(r.reason) end
    return r
end
