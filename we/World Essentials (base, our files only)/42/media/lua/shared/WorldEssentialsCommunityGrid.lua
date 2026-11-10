-- One event, one object traversal, fixed sprite scope. No timers or network calls.
local Health = require "WorldEssentialsPatchHealth"
local G = { bySprite = {}, failures = 0 }
local slots = {}
-- Restrict registration to the exact scope certified by Java LoadGridGate.
local allowed = { tv = {}, tabletop = {} }
for i = 36, 39 do allowed.tv["DylansRandomFurniture02_"..i] = true; allowed.tv["WECommunity_DylansRandomFurniture02_"..i] = true end
for _,i in ipairs({0,1,2,3,24,25,26,27,28,29,30,31}) do
    allowed.tabletop["kitchen_misc_tk_01_"..i] = true
end
for _,i in ipairs({0,1,2,3,4,5,6,7,12,13,14,15,23,27,28,29,30,31}) do allowed.tabletop["tikitown-props-14_"..i] = true end
function G.register(key, names, fn)
    if type(fn) ~= "function" or not allowed[key] then return false end
    for name in pairs(names) do if not allowed[key][name] then return false end end
    -- Replace this slot rather than append: repeated loading cannot duplicate work.
    slots[key] = fn
    for name in pairs(allowed[key]) do G.bySprite[name] = key end
    return true
end
local function communityLoad(sq)
    local objects = sq and sq:getObjects()
    if not objects then return end
    for i = 0, objects:size()-1 do
        local object = objects:get(i)
        local sprite = object and object:getSprite()
        local key = sprite and G.bySprite[sprite:getName()]
        local fn = key and slots[key]
        if fn then
            local ok = pcall(fn, object, "LoadGridsquare")
            if not ok then
                G.failures = G.failures + 1
                Health.counter("Community square repair", "failures", 1)
                if G.failures == 1 then
                    print("[WorldEssentials][Community] square repair failed; further failures counted in health report")
                end
            end
        end
    end
end
G.onSquare = communityLoad
if Events.LoadGridsquare then Events.LoadGridsquare.Add(communityLoad) end
Health.set("Community square repair", "OK", "Single load callback; Fixed sprite allowlist; isolated failures; no polling/network")
return G
