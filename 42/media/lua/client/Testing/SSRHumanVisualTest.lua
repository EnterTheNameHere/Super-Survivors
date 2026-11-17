require "Testing/SSRTests"

local T=SSRTests
SSRHumanVisualDiagnostics=SSRHumanVisualDiagnostics or {}
local H=SSRHumanVisualDiagnostics
local BASE,CHANGED,INVISIBLE="human-visual-baseline","human-visual-changed","human-visual-invisible"
local function unavailable(reason) return {available=false,reason=reason} end
local function scalar(value)
    if value==nil then return {available=true,kind="null",value="<null>"} end
    local kind=type(value)
    if kind=="number" and (value~=value or math.abs(value)==math.huge) then return unavailable("non-finite number") end
    if kind~="string" and kind~="number" and kind~="boolean" then return unavailable("not a scalar") end
    return {available=true,kind=kind,value=value}
end
local function read(object,method,...)
    if not object then return unavailable("object absent") end
    local args={...}
    local ok,found,value=pcall(function()
        local fn=object[method]
        if not fn then return false,nil end
        return true,fn(object,unpack(args))
    end)
    if not ok then return unavailable(tostring(found)) end
    return found and scalar(value) or unavailable("getter unavailable: "..method)
end
local function objectRead(object,method)
    if not object then return nil,false end
    local ok,found,value=pcall(function()
        local fn=object[method];if not fn then return false,nil end
        return true,fn(object)
    end)
    if not ok or not found then return nil,false end
    return value,true
end
local function debugEnabled() return getDebug~=nil and getDebug()==true end
local function raw(object,name)
    if not object then return false,nil,"object absent" end
    if not debugEnabled() then return false,nil,"raw field requires native -debug; lazy public getter deliberately not called" end
    if not getNumClassFields or not getClassField or not getClassFieldVal then return false,nil,"reflection unavailable" end
    local ok,found,value=pcall(function()
        for i=0,getNumClassFields(object)-1 do
            local field=getClassField(object,i)
            if field:getName()==name then return true,getClassFieldVal(object,field) end
        end
        return false,nil
    end)
    if not ok then return false,nil,"raw field unavailable: "..tostring(found) end
    if value=="<private>" then return false,nil,"field access denied" end
    return found,value,found and nil or "field not declared on this class"
end
local function rawScalar(object,name,number)
    local ok,value,reason=raw(object,name)
    if not ok then return unavailable(reason) end
    if number and value~=nil then value=tonumber(tostring(value));if value==nil then return unavailable("raw numeric field unreadable") end end
    return scalar(value)
end
local function rawColor(object,name)
    local ok,color,reason=raw(object,name)
    if not ok then return unavailable(reason) end
    if color==nil then return scalar(nil) end
    local parts={}
    for _,method in ipairs({"getRedFloat","getGreenFloat","getBlueFloat","getAlphaFloat"}) do
        local component=read(color,method)
        if not component.available or component.kind~="number" then return unavailable("color component unavailable") end
        parts[#parts+1]=string.format("%.6f",component.value)
    end
    return scalar(table.concat(parts,","))
end
local function visualFields(out,prefix,visual,owner,readable)
    out[prefix..".present"]=readable and scalar(visual~=nil) or unavailable("HumanVisual getter unavailable")
    out[prefix..".skinTextureIndex"]=read(visual,"getSkinTextureIndex") -- direct field; no randomization
    out[prefix..".bodyHairIndex"]=read(visual,"getBodyHairIndex")
    out[prefix..".nonAttachedHair"]=read(visual,"getNonAttachedHair")
    for _,name in ipairs({"skinTextureName","hairModel","beardModel"}) do out[prefix.."."..name]=rawScalar(visual,name) end
    for _,name in ipairs({"skinColor","hairColor","beardColor","naturalHairColor","naturalBeardColor"}) do
        out[prefix.."."..name]=rawColor(visual,name)
    end
    local ok,actualOwner,reason=raw(visual,"owner")
    out[prefix..".ownerMatches"]=ok and scalar(actualOwner==owner) or unavailable(reason)
end
local function summarizeList(list,worn)
    if not list then return unavailable("list absent") end
    local ok,value=pcall(function()
        local rows={};local total=list:size()
        for i=0,math.min(total,64)-1 do
            local item=list:get(i);if worn then item=item:getItem() end
            rows[#rows+1]=item:getFullType()..(worn and "" or ";count="..item:getCount()..";condition="..item:getCondition())
        end
        table.sort(rows)
        return ("total="..total.."; sampled="..math.min(total,64).."; "..table.concat(rows," | ")):sub(1,2400)
    end)
    return ok and scalar(value) or unavailable(tostring(value))
end
local function capture()
    local actor=assert(getSpecificPlayer(0),"No local player in slot 0")
    local descriptor,descriptorReadable=objectRead(actor,"getDescriptor")
    local visual,visualReadable=objectRead(actor,"getHumanVisual")
    local descVisual,descVisualReadable=objectRead(descriptor,"getHumanVisual")
    local model,modelReadable=objectRead(actor,"getModelInstance") -- pure field lookup, unlike getAnimationPlayer
    local creator,creatorReadable=objectRead(actor,"getTextureCreator")
    local refs={actor=actor,descriptor=descriptor,visual=visual,model=model,creator=creator,slots={}}
    local out={}
    out["identity.descriptorPresent"]=descriptorReadable and scalar(descriptor~=nil) or unavailable("getter unavailable")
    out["identity.descriptorID"]=read(descriptor,"getID")
    out["identity.forename"]=read(descriptor,"getForename");out["identity.surname"]=read(descriptor,"getSurname")
    out["identity.isLocalPlayer"]=read(actor,"isLocalPlayer");out["identity.isNpc"]=read(actor,"isNpc")
    out["identity.playerNum"]=read(actor,"getPlayerNum");out["identity.female"]=read(actor,"isFemale")
    out["identity.descriptorFemale"]=read(descriptor,"isFemale")
    local singleton=IsoPlayer.getInstance();refs.singleton=singleton
    out["identity.singletonPresent"]=scalar(singleton~=nil);out["identity.singletonIsSlot0"]=scalar(singleton==actor)
    for i=0,3 do
        refs.slots[i]=getSpecificPlayer(i)
        out["identity.slot"..i..".present"]=scalar(refs.slots[i]~=nil)
        out["identity.slot"..i..".isCapturedActor"]=scalar(refs.slots[i]==actor)
    end
    visualFields(out,"visual.actor",visual,actor,visualReadable)
    visualFields(out,"visual.descriptor",descVisual,descriptor,descVisualReadable)
    out["visual.actorSharesDescriptorVisual"]=visual and descVisual and scalar(visual==descVisual) or unavailable("visual absent")
    for _,method in ipairs({"isInvisible","isGhostMode","isGodMod","isNoClip","isSpriteInvisible","isSceneCulled","getDoRender"}) do
        out["visibility."..method]=read(actor,method)
    end
    out["visibility.alpha0"]=read(actor,"getAlpha",0);out["visibility.targetAlpha0"]=read(actor,"getTargetAlpha",0)
    out["render.modelInstancePresent"]=modelReadable and scalar(model~=nil) or unavailable("getter unavailable")
    out["render.textureCreatorPresent"]=creatorReadable and scalar(creator~=nil) or unavailable("getter unavailable")
    -- Do not call getAnimationPlayer: it can allocate/rebind the player's animation state.
    out["render.animationPlayer"]=unavailable("getter may allocate/rebind; not called")
    local ok,nativeModel,reason=raw(model,"model")
    out["render.modelName"]=ok and rawScalar(nativeModel,"name") or unavailable(reason)
    for _,name in ipairs({"tintR","tintG","tintB"}) do out["render."..name]=rawScalar(model,name,true) end
    local textureOK,texture,textureReason=raw(model,"tex")
    out["render.textureName"]=textureOK and (texture and read(texture,"getName") or scalar(nil)) or unavailable(textureReason)
    out["render.textureCreatorRendered"]=rawScalar(creator,"rendered")
    out["context.x"]=read(actor,"getX");out["context.y"]=read(actor,"getY");out["context.z"]=read(actor,"getZ")
    local inventory=objectRead(actor,"getInventory")
    out["context.inventoryTopLevel"]=summarizeList(objectRead(inventory,"getItems"),false)
    out["context.wornTypes"]=summarizeList(objectRead(actor,"getWornItems"),true)
    for _,slot in ipairs({{"primary","getPrimaryHandItem"},{"secondary","getSecondaryHandItem"}}) do
        local item,known=objectRead(actor,slot[2])
        out["context."..slot[1]]=known and (item and read(item,"getFullType") or scalar(nil)) or unavailable("getter unavailable")
    end
    local xp=objectRead(actor,"getXp")
    for _,name in ipairs({"Axe","Strength","Fitness"}) do
        local perk=Perks and Perks[name]
        out["context.xp."..name]=perk and read(xp,"getXP",perk) or unavailable("perk unavailable")
        out["context.level."..name]=perk and read(actor,"getPerkLevel",perk) or unavailable("perk unavailable")
    end
    local stats=objectRead(actor,"getStats")
    for _,name in ipairs({"HUNGER","THIRST","ENDURANCE"}) do
        local stat=CharacterStat and CharacterStat[name]
        out["context.stat."..name]=stat and read(stats,"get",stat) or unavailable("stat unavailable")
    end
    out["context.health"]=read(objectRead(actor,"getBodyDamage"),"getOverallBodyHealth")
    out["context.worldHours"]=read(getGameTime(),"getWorldAgeHours")
    out["context.nativeDebug"]=scalar(debugEnabled())
    assert(getSpecificPlayer(0)==actor,"Local actor changed during capture; snapshot discarded")
    return {time=tostring(getTimestampMs()),cell=getCell(),world=getWorld():getWorld(),fields=out,refs=refs}
end
local function prerequisites()
    if getCore():getGameAndBuildVersion()~="42.22.2" then return false,"Human getter safety reviewed for B42.22.2 only." end
    return true
end
local function afterAvailable()
    local ok,reason=prerequisites();if not ok then return false,reason end
    local baseline=H.baseline
    if not baseline then return false,"Capture a known-good human baseline in this gameplay session first." end
    if baseline.cell~=getCell() or baseline.world~=getWorld():getWorld() then
        return false,"Baseline belongs to another world/gameplay session; explicitly capture a new one."
    end
    return true
end
local function display(value)
    if not value or not value.available then return "UNAVAILABLE ("..tostring(value and value.reason or "not recorded")..")" end
    return tostring(value.value)
end
local function keys(fields)
    local result={};for name in pairs(fields) do result[#result+1]=name end;table.sort(result);return result
end
local function same(a,b)
    if not a or not b or not a.available or not b.available then return nil end
    if a.kind~=b.kind then return false end
    if a.kind=="number" then return math.abs(a.value-b.value)<0.00001 end
    return a.value==b.value
end
local function logSnapshot(ctx,snapshot,baseline)
    ctx:log("Capture timestamp(ms)="..snapshot.time.."; baseline="..tostring(baseline and baseline.time or "new").."; world="..tostring(snapshot.world))
    local changes={identity=0,visual=0,visibility=0,render=0,context=0,unavailable=0}
    for _,name in ipairs(keys(snapshot.fields)) do
        local value=snapshot.fields[name];local previous=baseline and baseline.fields[name]
        if not baseline then ctx:log(name.."="..display(value))
        else
            local match=same(previous,value)
            local status=match==nil and "UNAVAILABLE" or (match and "UNCHANGED" or "CHANGED")
            ctx:log(status.." "..name..": baseline="..display(previous).."; current="..display(value))
            if match==nil then changes.unavailable=changes.unavailable+1
            elseif not match then local category=name:match("^([^%.]+)");changes[category]=changes[category]+1 end
        end
    end
    return changes
end
local function compare(ctx,kind)
    local allowed,reason=afterAvailable();if not allowed then ctx:finish("SETUP ERROR",reason);return end
    local baseline=H.baseline;local snapshot=capture()
    local identitySame=snapshot.refs.actor==baseline.refs.actor
    local function refMatch(a,b) return a and b and tostring(a==b) or "UNAVAILABLE (reference absent)" end
    ctx:log("Same-session human actor reference unchanged="..tostring(identitySame).."; descriptor ref unchanged="..refMatch(snapshot.refs.descriptor,baseline.refs.descriptor)
        .."; visual ref unchanged="..refMatch(snapshot.refs.visual,baseline.refs.visual).."; model ref unchanged="..refMatch(snapshot.refs.model,baseline.refs.model))
    local slotsSame=true
    for i=0,3 do
        local match=snapshot.refs.slots[i]==baseline.refs.slots[i];slotsSame=slotsSame and match
        ctx:log("Local slot "..i.." reference unchanged="..tostring(match))
    end
    ctx:log("Singleton reference unchanged="..tostring(snapshot.refs.singleton==baseline.refs.singleton))
    local refChanges=0
    for _,name in ipairs({"descriptor","visual","model","creator"}) do
        local before,after=baseline.refs[name],snapshot.refs[name]
        if before and after and before~=after then refChanges=refChanges+1 end
    end
    local changes
    if identitySame then changes=logSnapshot(ctx,snapshot,baseline)
    else
        ctx:log("IDENTITY CHANGE: slot 0 now refers to a different actor. Current data follows; visual differences are not attributed to the original human.")
        logSnapshot(ctx,snapshot)
    end
    local flag=snapshot.fields["visibility.isInvisible"]
    ctx:log("CURRENT isInvisible="..display(flag)..". Ghost mode aliases this flag on installed IsoPlayer; no toggle performed.")
    ctx:log("Dynamic XP/equipment/inventory/needs/position differences are context, not failure invariants. These fields do not fingerprint rendered pixels.")
    H.history=H.history or {}
    H.history[#H.history+1]={time=snapshot.time,kind=kind,fields=snapshot.fields,sameActor=identitySame,changes=changes}
    if #H.history>4 then table.remove(H.history,1) end
    ctx.observations={sameActor=identitySame,slotsUnchanged=slotsSame,changes=changes,currentInvisible=flag,
        baselineTimestamp=baseline.time,currentTimestamp=snapshot.time,referenceChanges=refChanges}
    if not identitySame or not slotsSame or snapshot.refs.singleton~=baseline.refs.singleton then
        ctx:finish("INCONCLUSIVE","Actor/slot/singleton identity changed. Baseline preserved; verify intentional character change before rebaselining.")
    elseif changes and (refChanges>0 or changes.identity>0 or changes.visual>0 or changes.visibility>0 or changes.render>0) then
        ctx:finish("INCONCLUSIVE","Observed identity/visual/visibility/render-state or reference changes; see categories. No cause or repair inferred.")
    elseif changes and changes.unavailable>0 then
        ctx:finish("INCONCLUSIVE","Readable stable fields unchanged; some visual/render fields unavailable. A visible symptom can still be a rendering issue; no cause established.")
    else ctx:finish("PASSED","Comparison recorded; readable stable fields unchanged. This is not proof the displayed appearance is correct.") end
end
local requirements="Intended local human in a single-player gameplay session. Session-only baseline; recapture after world reload/new character. Full raw hair/color detail requires native -debug; never enabled by this test."
local risk="Observation only. Stores bounded data in Lua memory, not the save. No appearance/control/visibility/model/inventory changes. Existing shared-window acknowledgment remains."
T.register({id=BASE,order=30,readOnly=true,title="Human appearance - capture baseline",
    description="Run ONLY when your human looks correct. Capture stable visual/descriptor/identity and visibility fields plus dynamic inventory/XP context. Explicitly replaces the session baseline; later comparisons never overwrite it. Unsafe lazy getters are skipped, with missing data marked unavailable.",
    requirements=requirements,risk=risk,available=prerequisites,
    run=function(ctx)
        local snapshot=capture();H.baseline=snapshot;H.history={}
        logSnapshot(ctx,snapshot)
        ctx:log("Baseline is session-only: no reliable public stable human-save identity getter was verified. No raw Java references written to ModData.")
        ctx:finish("PASSED","Known-good baseline captured at your request; coverage limits listed. No appearance validation or changes applied.")
    end})
T.register({id=CHANGED,order=40,readOnly=true,title="Human appearance - compare changed",
    description="Run after a visible appearance change. Compare with your known-good baseline; record current state separately (last four AFTER captures). Dynamic skills/equipment/inventory are observations. Unavailable fields are not treated as matching. No automatic capture, reset or root-cause attribution.",
    requirements=requirements,risk=risk,available=afterAvailable,run=function(ctx) compare(ctx,"appearance changed") end})
T.register({id=INVISIBLE,order=50,readOnly=true,title="Human appearance - diagnose invisible",
    description="Run while your human is invisible. Record current isInvisible, ghost/sprite/culling/draw flags, opacity for viewport 0 and model presence; compare data with baseline. Does NOT call setInvisible, refresh/resetModel or getAnimationPlayer. Captures current data at execution time, not the exact earlier rendered frame.",
    requirements=requirements,risk=risk,available=afterAvailable,run=function(ctx) compare(ctx,"invisible symptom") end})
if H.startCallback then Events.OnGameStart.Remove(H.startCallback) end
H.startCallback=function() H.baseline=nil;H.history={} end -- Clear own memory only; never capture on startup.
Events.OnGameStart.Add(H.startCallback)
