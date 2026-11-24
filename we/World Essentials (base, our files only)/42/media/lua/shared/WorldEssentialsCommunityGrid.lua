-- One event, one object traversal, fixed sprite scope. No timers or network calls.
local Health = require "WorldEssentialsPatchHealth"
local G = { bySprite = {}, failures = 0 }
local slots = {}
local hooked=false
local communityLoad
-- Restrict registration to the exact scope certified by Java LoadGridGate.
local allowed = { tv = {}, tabletop = {} }
for _,name in ipairs({"DylansRandomFurniture02_36","DylansRandomFurniture02_37","DylansRandomFurniture02_38","DylansRandomFurniture02_39","WECommunity_DylansRandomFurniture02_36","WECommunity_DylansRandomFurniture02_37","WECommunity_DylansRandomFurniture02_38","WECommunity_DylansRandomFurniture02_39","KBWCommunityIceShell_176","KBWCommunityIceShell_177","KBWCommunityIceShell_178","KBWCommunityIceShell_179","KBWCommunityIceShell_180","KBWCommunityIceShell_181","KBWCommunityIceShell_205","KBWCommunityIceShell_206","KBWCommunityIceShell_264","KBWCommunityIceShell_265","KBWCommunityIceShell_266","KBWCommunityIceShell_267","KBWCommunityIceShell_268","KBWCommunityIceShell_269"}) do allowed.tv[name] = true end
for _,name in ipairs({"kitchen_misc_tk_01_0","kitchen_misc_tk_01_1","kitchen_misc_tk_01_2","kitchen_misc_tk_01_3","kitchen_misc_tk_01_24","kitchen_misc_tk_01_25","kitchen_misc_tk_01_26","kitchen_misc_tk_01_27","kitchen_misc_tk_01_28","kitchen_misc_tk_01_29","kitchen_misc_tk_01_30","kitchen_misc_tk_01_31","tikitown-props-14_0","tikitown-props-14_1","tikitown-props-14_2","tikitown-props-14_3","tikitown-props-14_4","tikitown-props-14_5","tikitown-props-14_6","tikitown-props-14_7","tikitown-props-14_12","tikitown-props-14_13","tikitown-props-14_14","tikitown-props-14_15","tikitown-props-14_23","tikitown-props-14_27","tikitown-props-14_28","tikitown-props-14_29","tikitown-props-14_30","tikitown-props-14_31","tikitown-props-14_90","tikitown-props-14_91","tikitown-props-14_92","tikitown-props-14_93","tikitown-props-14_104","tikitown-props-14_105","blackwood5_40","blackwood5_44","blackwood5_45","blackwood5_47","blackwood6_60","blackwood7_24","blackwood7_25","blackwood7_26","blackwood7_61"}) do allowed.tabletop[name] = true end
function G.register(key, names, fn)
    if type(fn) ~= "function" or not allowed[key] then return false end
    for name in pairs(names) do if not allowed[key][name] then return false end end
    -- Replace this slot rather than append: repeated loading cannot duplicate work.
    slots[key] = fn
    if not hooked and Events.LoadGridsquare then Events.LoadGridsquare.Add(communityLoad);hooked=true end
    for name in pairs(allowed[key]) do G.bySprite[name] = key end
    return true
end
communityLoad=function(sq)
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
-- Registration is demand-driven by G.register.
Health.set("Community square repair", "OK", "Single load callback; Fixed sprite allowlist; isolated failures; no polling/network")
return G
