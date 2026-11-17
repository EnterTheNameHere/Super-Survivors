require "Testing/SSRCombatSnapshot"
if SSRCombatTrace and SSRCombatTrace.stop then SSRCombatTrace.stop(nil,"trace module reloaded") end
SSRCombatTrace=SSRCombatTrace or {}
local R,C=SSRCombatTrace,SSRCombatSnapshot
R.active,R.last=nil,nil -- retain table identity for already loaded contextual UI
local MAX_MS,MAX_TICKS,MAX_LINES,MAX_REQUESTS=10000,600,80,30
local function pack(...) return {n=select("#",...),...} end
local function scalar(v)
    local kind=type(v)
    return (v==nil or kind=="boolean" or kind=="number" or kind=="string") and tostring(v):sub(1,160) or "<non-scalar>"
end
local function value(object,method,...)
    local v,ok=C.read(object,method,...)
    return ok and tostring(v) or "UNAVAILABLE"
end
local function state(p)
    local a,npc=p.actor,p.wrapper
    local target=npc.LastEnemeySeen
    local s={started=value(a,"isAttackStarted"),initiate=value(a,"isInitiateAttack"),
        animation=value(a,"isPerformingAttackAnimation"),aiming=value(a,"isAiming"),
        state=value(a,"getCurrentStateName"),task=npc.MyTaskManager and npc.MyTaskManager.Tasks
            and npc.MyTaskManager.Tasks[0] and npc.MyTaskManager.Tasks[0].Name or "None",
        wait=tostring(npc.WaitTicks),cooldown=tostring(npc.AtkTicks),target=target and "present" or "none"}
    local current,known=C.read(a,"getCurrentState")
    local swipe,swipeKnown
    if SwipeStatePlayer then swipeKnown,swipe=pcall(SwipeStatePlayer.instance) end
    s.swing=known and swipeKnown and tostring(current==swipe) or "UNAVAILABLE"
    local x,okx=C.read(target,"getX");local y,oky=C.read(target,"getY");local z,okz=C.read(target,"getZ")
    s.range=okx and oky and okz and value(a,"IsAttackRange",x,y,z) or "UNAVAILABLE"
    return s,target
end
local function textState(s)
    return "started="..s.started.." initiate="..s.initiate.." animation="..s.animation.." swing="..s.swing
        .." aiming="..s.aiming.." state="..s.state.." task="..s.task.." target="..s.target
        .." range="..s.range.." wait="..s.wait.." cooldown="..s.cooldown
end
local function emit(r,line)
    if r.lines>=MAX_LINES then return end
    r.lines=r.lines+1
    line="t="..tostring(getTimestampMs()).." frame="..value(getWorld(),"getFrameNo").." "..line
    r.output[#r.output+1]=line
    print("[SS Tests][combat-existing-trace] "..line)
end
function R.stop(owner,reason)
    local r=R.active
    if not r or (owner and r.owner~=owner) then return false end
    R.active=nil -- detach first, including on callback errors/reentrant cleanup
    if r.wrapper and rawget(r.p.wrapper,"requestCombatAttack")==r.wrapper then
        rawset(r.p.wrapper,"requestCombatAttack",r.originalRaw)
        r.restored=true
    elseif r.wrapper then r.restored=false end -- another owner replaced it; do not overwrite
    for _,binding in ipairs(r.bindings) do pcall(binding.event.Remove,binding.fn) end
    r.reason=reason or "stopped";r.finished=true
    pcall(emit,r,"END "..r.reason.." requests="..r.requests.." swingEvents="..r.swings
        .." hitPointEvents="..r.hitPoints.." sampledFalseToTrue="..r.rises.." ownedWrapperRestored="..tostring(r.restored))
    pcall(emit,r,"INCONCLUSIVE: passive samples/natural requests only; no original setter, successful hit or root cause inferred.")
    R.last=r
    return true
end
local function log(r,line)
    if R.active~=r then return end
    if r.lines>=MAX_LINES-2 then R.stop(r.owner,"log cap reached");return end
    emit(r,line:sub(1,1500))
end
local function sample(r,label,force)
    local s,target=state(r.p)
    local fingerprint=textState(s)
    if r.previous and r.previous.started=="false" and s.started=="true" then r.rises=r.rises+1 end
    if force or fingerprint~=r.fingerprint or target~=r.target then
        log(r,label.." "..fingerprint.." targetRefChanged="..tostring(r.target~=nil and target~=r.target))
    end
    r.previous,r.fingerprint,r.target=s,fingerprint,target
    return s
end
local function protect(r,fn,...)
    local result=pack(pcall(fn,...))
    if not result[1] then pcall(R.stop,r.owner,"observer failure: "..tostring(result[2])) end
    return unpack(result,2,result.n)
end
local function installRequest(r)
    local npc=r.p.wrapper
    local original=npc.requestCombatAttack
    if type(original)~="function" then log(r,"request interception UNAVAILABLE: no Lua requestCombatAttack function");return end
    r.originalRaw=rawget(npc,"requestCombatAttack")
    r.wrapper=function(self,...)
        if self~=npc or R.active~=r then return original(self,...) end
        local allowed=protect(r,C.available,r.p)
        if not allowed then R.stop(r.owner,"selected actor invalid at natural request");return original(self,...) end
        if r.requests>=MAX_REQUESTS then
            R.stop(r.owner,"natural request cap reached")
            return original(self,...)
        end
        r.requests=r.requests+1
        protect(r,sample,r,"REQUEST ENTRY #"..r.requests,true)
        -- No pcall around production: Kahlua pcall converts native Throwables and
        -- has a different error/stack tuple. Let the original error escape intact.
        -- An aborted synchronous call is cleaned up on the next tick/render hook.
        r.inFlight=true
        local result=pack(original(self,...))
        r.inFlight=false
        if R.active==r then
            protect(r,sample,r,"REQUEST POST #"..r.requests,true)
            protect(r,log,r,"REQUEST RETURN #"..r.requests.." values="..result.n
                .." first="..scalar(result[1]).." reason="..scalar(result[2]))
        end
        return unpack(result,1,result.n)
    end
    rawset(npc,"requestCombatAttack",r.wrapper)
    log(r,"Installed instance-only request observer; no natural call forced. Original arguments/results/errors preserved; traceback includes observer frame.")
end
local function add(r,name,fn)
    local event=Events[name]
    if not event or not event.Add or not event.Remove then log(r,name.." UNAVAILABLE: callback API missing");return end
    local guarded=function(...) protect(r,fn,...) end
    r.bindings[#r.bindings+1]={event=event,fn=guarded}
    event.Add(guarded)
end
local function watchdog(r,checkAborted)
    if R.active~=r then return false end
    if checkAborted and r.inFlight then R.stop(r.owner,"natural request did not return normally; original error was not intercepted");return false end
    local allowed,reason=C.available(r.p)
    if not allowed then R.stop(r.owner,"guard: "..tostring(reason));return false end
    if getTimestampMs()>=r.deadline then R.stop(r.owner,"10 second deadline");return false end
    return true
end
function R.start(parameters,owner)
    if R.active then return nil,"Another combat trace is running." end
    local allowed,reason=C.available(parameters)
    if not allowed then return nil,reason end
    local p={};for k,v in pairs(parameters) do p[k]=v end
    local r={p=p,owner=owner or {},deadline=getTimestampMs()+MAX_MS,ticks=0,lines=0,output={},bindings={},
        requests=0,swings=0,hitPoints=0,rises=0}
    R.active=r;R.last=nil
    local ok,failure=pcall(function()
        log(r,"START SSR ID="..p.id.." limits:10s/600ticks/80lines/30natural requests. OnTick samples; request callbacks are synchronous at natural Lua dispatch, not setter interception.")
        local initial=sample(r,"INITIAL",true)
        if initial.started=="true" then log(r,"PREEXISTING attackStarted=true; first setter/false-to-true transition was NOT observed.") end
        installRequest(r)
        add(r,"OnTick",function()
            if not watchdog(r,true) then return end
            r.ticks=r.ticks+1
            if r.ticks>=MAX_TICKS then R.stop(r.owner,"600 tick cap");return end
            sample(r,"TICK",r.ticks%60==0)
        end)
        -- Lightweight deadline/guards only, including when game ticks are paused.
        add(r,"OnRenderTick",function() watchdog(r,true) end)
        add(r,"OnMainMenuEnter",function() R.stop(r.owner,"main menu") end)
        add(r,"OnGameStart",function() R.stop(r.owner,"new gameplay session") end)
        add(r,"OnWeaponSwing",function(attacker)
            if attacker~=p.actor or not watchdog(r) then return end
            r.swings=r.swings+1;log(r,"EVENT OnWeaponSwing owned attacker (state entry, not damage)")
        end)
        add(r,"OnWeaponSwingHitPoint",function(attacker)
            if attacker~=p.actor or not watchdog(r) then return end
            r.hitPoints=r.hitPoints+1;log(r,"EVENT OnWeaponSwingHitPoint owned attacker (collision routine entered, not proof of damage)")
        end)
    end)
    if not ok then R.stop(r.owner,"setup failed: "..tostring(failure));return nil,tostring(failure) end
    return r
end
SSRTests.register({id="combat-existing-trace",order=70,readOnly=true,survivorSelection=true,maxTicks=1200,
    title="Combat - trace existing survivor",description="Explicitly start up to 10 seconds of passive state/natural-request/event tracing for one existing NPC. No attacks or state changes are requested. Preexisting started flags are labeled, not repaired.",
    requirements="B42.22.2, same ownership/SP/living-human guards as combat snapshot. Prefer Diagnostics in that survivor's Information window.",
    risk="Bounded observation overhead and temporary Lua method interception on the selected wrapper only; restored on stop. No world/actor changes.",
    available=function(p) return C.available(p) end,
    run=function(ctx)
        local r,reason=R.start(ctx.parameters,ctx)
        if not r then ctx:finish("SETUP ERROR",reason);return end
        ctx:log("Trace started; compact records logged under [SS Tests][combat-existing-trace].")
        ctx.cleanup=function() R.stop(ctx,"test cancelled/finished") end
        ctx.step=function()
            if r.finished then
                for _,line in ipairs(r.output) do ctx.lines[#ctx.lines+1]=line end
                ctx:finish("INCONCLUSIVE",r.reason.."; passive trace recorded, no root cause or hit inferred.")
            end
        end
    end})
