require "Testing/SSRTests"
local T = SSRTests
local KEY = "SSR.Tests.NativePosition"
local REQUIREMENTS = "Living player; normal single-player save; two loaded, free floor tiles nearby; prefer only this mod. Raw NPC construction emits other mods' character events."
local RISK = "Creates isolated test NPCs and uniquely named native snapshot files. Removes test actors best effort; snapshot files remain. Never targets the human player or SSR survivor registry."

local function version() return getCore():getGameVersion():toString() end
local function near(a,b) return math.abs(a-b) < 0.001 end
local function samePosition(a,b) return near(a.x,b.x) and near(a.y,b.y) and near(a.z,b.z) end
local function coords(object)
    return object and {x=object:getX(),y=object:getY(),z=object:getZ()} or nil
end
local function xyz(pos)
    return pos and string.format("%.3f,%.3f,%.3f",pos.x,pos.y,pos.z) or "nil"
end
local function capture(actor)
    local cell, square = getCell(), actor:getCurrentSquare()
    local pos = coords(actor)
    return {actor=tostring(actor), position=pos, square=tostring(square), squarePosition=coords(square),
        squareMatchesPosition=square ~= nil and square:getX()==math.floor(pos.x)
            and square:getY()==math.floor(pos.y) and square:getZ()==math.floor(pos.z),
        squareContains=square ~= nil and square:getMovingObjects():contains(actor),
        inWorld=cell:getObjectList():contains(actor), inAdd=cell:getAddList():contains(actor),
        inRemove=cell:getRemoveList():contains(actor), safeToAdd=cell:isSafeToAdd()}
end
local function record(context,label,observation)
    context:log(label .. ": actor=" .. observation.actor .. "; XYZ=" .. xyz(observation.position))
    context:log("  currentSquare=" .. observation.square .. "; square XYZ=" .. xyz(observation.squarePosition)
        .. "; matches position=" .. tostring(observation.squareMatchesPosition)
        .. "; contains actor=" .. tostring(observation.squareContains))
    context:log("  world/add/remove=" .. tostring(observation.inWorld) .. "/" .. tostring(observation.inAdd)
        .. "/" .. tostring(observation.inRemove) .. "; safeToAdd=" .. tostring(observation.safeToAdd))
end
local function prerequisites()
    if version()~="42.22.2" then return false,"Probe reviewed for installed B42.22.2 only; reinspect this engine build before running." end
    if getCore():isNoSave() then return false, "Use a normal save-enabled disposable world." end
    local human=getSpecificPlayer(0)
    if not human or human:isDead() or human:isNpc() then return false, "A living local human player is required." end
    if IsoWorld.saveoffsetx~=0 or IsoWorld.saveoffsety~=0 then
        return false,"Requires known zero native world save offsets; X/Y="..tostring(IsoWorld.saveoffsetx)
            .."/"..tostring(IsoWorld.saveoffsety)..". Use a fresh unconverted world."
    end
    return true
end
local function squares()
    local player, cell = getSpecificPlayer(0), getCell()
    if not player or not cell then return nil end
    local x,y,z = math.floor(player:getX()),math.floor(player:getY()),math.floor(player:getZ())
    local found = {}
    for _,offset in ipairs({{2,0},{0,2},{-2,0},{0,-2},{3,1},{-3,-1},{1,-3},{-1,3}}) do
        local square = cell:getGridSquare(x+offset[1],y+offset[2],z)
        if square and square:getFloor() and square:isFree(false) then
            found[#found+1] = square
            if #found == 2 then return found end
        end
    end
    return nil
end
local function uniqueFile()
    for attempt=1,20 do
        local token = string.format("%.0f_%.0f_%d",getTimestampMs(),ZombRand(1000000),attempt)
        local file = "SSR_Test_NativePosition_" .. token .. ".bin"
        if not checkSaveFileExists(file) then return file,token end
    end
    error("Could not allocate a unique test snapshot filename")
end
local function safeContext(context, operation)
    context.step = function(self)
        local allowed, reason = prerequisites()
        if not allowed then self:finish("SETUP ERROR",reason); return end
        if not self.cell:isSafeToAdd() then
            if not self.waitLogged then self:log("Waiting for native cell safeToAdd before construction/removal."); self.waitLogged=true end
            return
        end
        local targets = squares()
        if not targets then self:finish("SETUP ERROR","Need two distinct nearby loaded, free floor tiles. Move to an open area."); return end
        self:log("Installed engine: " .. version() .. "; boot/session=" .. T.bootToken)
        self:log("Native world save offsets X/Y="..tostring(IsoWorld.saveoffsetx).."/"..tostring(IsoWorld.saveoffsety))
        local human = assert(getSpecificPlayer(0),"The human player is no longer available")
        local humanBefore, instanceBefore, saveBefore = coords(human), IsoPlayer.getInstance(), human.saveFileName
        local actors, constructing = {}, false
        self.cleanup = function(ctx)
            if getCell() ~= ctx.cell then
                ctx:log("World changed; old actors left to native world teardown, not removed through a different cell.")
                return
            end
            assert(ctx.cell:isSafeToAdd(), "Native cell not safe for immediate cleanup; restart before further tests")
            local failures = {}
            for i=#actors,1,-1 do
                local actor = actors[i]
                local ok, failure = pcall(function()
                    assert(actor ~= human and not actor:isLocalPlayer(), "Refusing to remove a local player")
                    actor:removeFromWorld()
                    actor:removeFromSquare()
                    assert(not ctx.cell:getObjectList():contains(actor) and not ctx.cell:getAddList():contains(actor)
                        and not ctx.cell:getRemoveList():contains(actor), "Test actor still registered after cleanup")
                    assert(actor:getCurrentSquare()==nil,"Test actor still has a current square after cleanup")
                    ctx:log("Cleanup actor="..tostring(actor).."; world/add/remove=false/false/false; currentSquare=nil")
                end)
                if ok then actors[i] = nil else failures[#failures+1]=tostring(failure) end
            end
            assert(#failures == 0, table.concat(failures,"; "))
            assert(not constructing,"Constructor failed before returning its registered actor; cleanup cannot be verified. Restart the game.")
            assert(getSpecificPlayer(0)==human and IsoPlayer.getInstance()==instanceBefore
                and samePosition(coords(human),humanBefore) and human.saveFileName==saveBefore,
                "Human guard changed during cleanup; no restoration attempted")
            ctx:log("Cleanup: isolated actors detached; test snapshot files retained.")
        end
        local function create(square)
            assert(self.cell:isSafeToAdd(),"Cell staging changed during probe")
            local desc = SurvivorFactory.CreateSurvivor()
            desc:setForename("SSR Position Probe")
            constructing = true
            local actor = IsoPlayer.new(self.cell,desc,square:getX(),square:getY(),square:getZ())
            assert(actor,"Native constructor returned no actor")
            actors[#actors+1] = actor -- Own the returned actor before further calls can fail.
            constructing = false
            assert(actor ~= human and not actor:isLocalPlayer(),"Constructor returned a local player")
            actor:setNpc(true)
            actor:setBlockMovement(true)
            local initial=capture(actor)
            assert(initial.inWorld and not initial.inAdd and not initial.inRemove and initial.squareMatchesPosition,
                "Native constructor did not establish the expected safe world/square registration")
            return actor
        end
        local function humanUnchanged()
            return getSpecificPlayer(0)==human and IsoPlayer.getInstance()==instanceBefore
                and samePosition(coords(human),humanBefore) and human.saveFileName==saveBefore
        end
        operation(self,targets,create,humanUnchanged)
    end
    -- Execute only from the runner's next tick; never from a UI click callback.
end
local function roundtrip(context,targets,create,humanUnchanged,manifest)
    local expected, file, token, original
    if manifest then
        expected,file,token,original=manifest.position,manifest.file,manifest.token,manifest.source
        record(context,"Source recorded in earlier session",original)
    else
        file,token=uniqueFile()
        local source=create(targets[1])
        source:getModData().SSRNativePositionToken=token
        original=capture(source);expected=original.position
        record(context,"Source before native save",original)
        context:log("Allocated isolated native snapshot: "..file)
        source:save(getSaveDir()..file)
        assert(checkSaveFileExists(file),"Native snapshot was not written")
        context:log("Unique native snapshot: "..file)
    end
    -- The destination is deliberately different from the saved coordinates.
    local destinationSquare=targets[2]
    if destinationSquare:getX()==math.floor(expected.x) and destinationSquare:getY()==math.floor(expected.y) then
        destinationSquare=targets[1]
    end
    local destination=create(destinationSquare)
    local before=capture(destination)
    local beforeSquare=destination:getCurrentSquare()
    record(context,"Destination constructed before load",before)
    if samePosition(before.position,expected) then
        context:finish("SETUP ERROR","Could not obtain a distinguishable destination position.");return
    end
    local ok, failure=pcall(function() destination:load(getSaveDir()..file) end)
    if not ok then context:finish("FAILED","Native load threw: "..tostring(failure));return end
    -- Deliberately NO setX/setY/setZ/setCurrentSquare or world update after load.
    local after=capture(destination)
    record(context,"Destination immediately after RAW native load",after)
    local sameSquare=beforeSquare==destination:getCurrentSquare()
    context:log("Current-square reference unchanged by load=" .. tostring(sameSquare))
    local axes={x=not near(before.position.x,expected.x),y=not near(before.position.y,expected.y),
        z=not near(before.position.z,expected.z)}
    context:log("Differentiated constructor axes X/Y/Z="..tostring(axes.x).."/"..tostring(axes.y).."/"..tostring(axes.z)
        ..". Unchanged axes are not independent restoration evidence.")
    local restored= samePosition(after.position,expected)
    local marker= destination:getModData().SSRNativePositionToken==token
    context:log("XYZ restored="..tostring(restored).."; snapshot marker restored="..tostring(marker))
    local missing=file..".missing"
    assert(not checkSaveFileExists(missing),"Missing-file case unexpectedly exists")
    local missingOK, missingError=pcall(function() destination:load(getSaveDir()..missing) end)
    local missingUnchanged=samePosition(coords(destination),after.position)
    local missingMarker=destination:getModData().SSRNativePositionToken==token
    context:log("Missing-file load returned="..tostring(missingOK).."; error="..tostring(missingError)
        .."; position unchanged="..tostring(missingUnchanged).."; marker unchanged="..tostring(missingMarker))
    local unchanged=humanUnchanged()
    context:log("Human identity, position, singleton and save filename unchanged="..tostring(unchanged))
    context.observations={source=original,before=before,after=after,positionRestored=restored,markerRestored=marker,
        humanUnchanged=unchanged,differentiatedAxes=axes,squareReferenceUnchanged=sameSquare,
        missingFile={returned=missingOK,positionUnchanged=missingUnchanged,markerUnchanged=missingMarker,error=tostring(missingError)},
        session=manifest and "explicit resume in a different Lua session" or "same-session only"}
    if manifest then
        manifest.lastResult={positionRestored=restored,markerRestored=marker,
            squareMatchesPosition=after.squareMatchesPosition,session=T.bootToken,engineVersion=version()}
    end
    if not restored or not marker or not unchanged or not missingOK or not missingUnchanged or not missingMarker then
        context:finish("FAILED","Controlled native XYZ/identity roundtrip or human-state guard failed; see observations.")
    else
        context:finish("PASSED","Native position/identity roundtrip succeeded. Inspect the differentiated axes and separate square-registration observations; this does not certify SSR persistence.")
    end
end

T.register({id="native-position",order=10,title="Native IsoPlayer position — same session",
    description="Save an isolated NPC, construct another on a different tile, load without manual coordinate/square correction, and record immediate XYZ and world/square membership. PASS requires matching position/marker and unchanged human guards. Differentiated axes and square behavior are reported separately; same-floor tests do not independently demonstrate Z restoration. No world update occurs between load and cleanup.",
    requirements=REQUIREMENTS,risk=RISK,available=prerequisites,
    run=function(context)
        safeContext(context,function(ctx,targets,create,guard) roundtrip(ctx,targets,create,guard) end)
    end})

T.register({id="native-position-stage",order=20,title="Native IsoPlayer position — stage restart probe",
    description="Create one test snapshot and stage a small world-owned manifest. Then save/exit normally, CLOSE the game, restart, and explicitly run the resume test. Replaces any previous test manifest; retains old files. Staging alone is INCONCLUSIVE, not a roundtrip pass.",
    requirements=REQUIREMENTS,risk=RISK.." Requires a normal world save to persist the manifest.",available=prerequisites,
    run=function(context)
        safeContext(context,function(ctx,targets,create,guard)
            local file,token=uniqueFile()
            local source=create(targets[1])
            source:getModData().SSRNativePositionToken=token
            local observation=capture(source)
            record(ctx,"Source staged for later session",observation)
            ctx:log("Allocated isolated staged snapshot: "..file)
            source:save(getSaveDir()..file)
            assert(checkSaveFileExists(file),"Staged native snapshot is missing")
            assert(guard(),"Human guard changed during staging")
            ModData.getOrCreate(KEY).manifest={schema=1,file=file,token=token,position=observation.position,
                source=observation,bootToken=T.bootToken,engineVersion=version()}
            ctx:log("Staged file="..file.."; original boot/session="..T.bootToken)
            ctx:finish("INCONCLUSIVE","Snapshot staged only. Save/exit normally, close the game, restart and explicitly select the resume test. No automatic resume.")
        end)
    end})

local function restartPrerequisites()
    local ok,reason=prerequisites()
    if not ok then return false,reason end
    local data=ModData.get(KEY)
    local m=data and data.manifest
    if not m or m.schema~=1 then return false,"Stage the restart probe in this world, then save/exit and restart." end
    if type(m.token)~="string" or not m.token:match("^%d+_%d+_%d+$")
        or m.file~="SSR_Test_NativePosition_"..m.token..".bin" then
        return false,"Invalid test snapshot manifest. Do not load an arbitrary file."
    end
    if not m.position or not m.source or not checkSaveFileExists(m.file) then return false,"Staged evidence/snapshot is missing." end
    if m.bootToken==T.bootToken then return false,"Still the staging Lua session. Save/exit, close the game and restart first." end
    if m.engineVersion~=version() then return false,"Engine version changed since staging. Stage a new probe." end
    return true
end
T.register({id="native-position-resume",order=30,title="Native IsoPlayer position — resume after restart",
    description="Explicitly read the staged test snapshot in a different Lua session, using a distinct constructor tile. Logs earlier and current session tokens. A changed Lua token alone cannot prove a full process restart: follow the instructions. Does not certify the mod's registry roundtrip.",
    requirements=REQUIREMENTS.." Requires saved staging evidence from this world and a different Lua session.",
    risk=RISK,available=restartPrerequisites,
    run=function(context)
        safeContext(context,function(ctx,targets,create,guard)
            local ok,reason=restartPrerequisites()
            if not ok then ctx:finish("SETUP ERROR",reason);return end
            local manifest=ModData.get(KEY).manifest
            ctx:log("Explicit restart-phase resume; source boot/session="..manifest.bootToken)
            roundtrip(ctx,targets,create,guard,manifest)
        end)
    end})
