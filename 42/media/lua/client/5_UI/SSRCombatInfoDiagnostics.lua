require "ISUI/ISContextMenu"
require "Testing/SSRCombatTrace"

if SSRCombatInfoDiagnostics then SSRCombatTrace.stop(nil,"information diagnostics module reloaded") end
SSRCombatInfoDiagnostics=SSRCombatInfoDiagnostics or {}
local D,C,R=SSRCombatInfoDiagnostics,SSRCombatSnapshot,SSRCombatTrace
function D.close(window)
    if not window then return end
    R.stop(window,"owning information window closed/rebound")
end
function D.bind(window,wrapper)
    D.close(window)
    window.ssCombatSelection=C.selection(wrapper)
end
local function valid(window,p)
    if window.ssCombatSelection~=p or not window:getIsVisible() then return false,"Information target changed or window closed." end
    return C.available(p)
end
local function status(window,text,reason)
    window.ssCombatStatus=text
    if window.ssCombatButton then
        window.ssCombatButton:setTitle("Diagnostics: "..text:gsub(" %(10s cap%)",""))
        window.ssCombatButton.tooltip=text..". "..(reason or "Observation only; details in console.txt.")
    end
end
function D.log(window,p)
    local ok,reason=valid(window,p)
    if not ok then status(window,"unavailable",reason);return false,reason end
    local result,failure=C.inspect(p)
    status(window,result and result.observations and "logged" or "unavailable",failure)
    return result,failure
end
function D.start(window,p)
    local ok,reason=valid(window,p)
    if not ok then status(window,"unavailable",reason);return nil,reason end
    local result,failure=R.start(p,window)
    status(window,result and "tracing (10s cap)" or "unavailable",failure)
    return result,failure
end
function D.menu(window)
    local p=window.ssCombatSelection
    local ok,reason=valid(window,p)
    if not ok then status(window,"unavailable",reason);return end
    local menu=ISContextMenu.get(0,getMouseX(),getMouseY())
    if not menu then status(window,"unavailable","Context menu unavailable.");return end
    -- Capture this binding, not a future/global selected NPC. Each action revalidates.
    menu:addOption("Log combat state",nil,function() D.log(window,p) end)
    menu:addOption("Start combat trace (up to 10s)",nil,function() D.start(window,p) end)
    menu:addOption("Stop combat trace",nil,function()
        if window.ssCombatSelection==p then R.stop(window,"user stopped trace");status(window,"trace stopped") end
    end)
end
function D.update(window,layout)
    local allowed=window.ssCombatSelection and C.available(window.ssCombatSelection)
    if not allowed or not window:getIsVisible() then D.close(window) end
    if allowed and not window.ssCombatButton then
        window.ssCombatButton=ISButton:new(10,0,window.width-20,25,"Diagnostics",window,D.menu)
        window.ssCombatButton:initialise();window:addChild(window.ssCombatButton)
    end
    if window.ssCombatButton then
        window.ssCombatButton:setVisible(allowed==true)
        layout(allowed==true)
        if window.ssCombatStatus=="tracing (10s cap)" and not (R.active and R.active.owner==window) then status(window,"trace logged") end
    end
end
