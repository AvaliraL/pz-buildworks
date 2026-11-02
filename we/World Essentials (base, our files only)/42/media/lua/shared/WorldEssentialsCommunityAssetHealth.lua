-- Bounded startup check and explicit inspection/repair. No scans, polling or custom packets.
if not getActivatedMods():contains("KnoxCommunityTilepack") then return end
local sprites = require "WorldEssentialsCommunitySprites"
local expectedIds = require "WorldEssentialsCommunitySpriteIds"
local legacy = require "WorldEssentialsCommunityLegacyIds"
local Health = require "WorldEssentialsPatchHealth"
local function report()
    local count, missing, wrongName = 0, 0, 0
    for _, name in pairs(sprites) do
        count = count + 1
        local sprite = getSprite(name)
        if not sprite then missing = missing + 1
        elseif sprite:getName() ~= name or sprite:getID() ~= expectedIds[name] then wrongName = wrongName + 1 end
    end
    Health.set("Community private assets", missing == 0 and wrongName == 0 and "OK" or "DEGRADED",
        "checked="..count.." missing="..missing.." wrongIdentity="..wrongName.."; fileNumber=8182; all 343 buildables retained")
end
if Events.OnGameStart then Events.OnGameStart.Add(report) end
if Events.OnServerStarted then Events.OnServerStarted.Add(report) end
function WorldEssentialsCommunityInspect(object)
    if not object or not object:getSprite() then return nil end
    local sprite = object:getSprite()
    local kbw = object:getModData().KBW
    local result = {sprite=sprite:getName(), id=sprite:getID(), buildable=kbw and kbw.buildableId}
    print("[WorldEssentials][CommunityInspect] sprite="..tostring(result.sprite).." id="..tostring(result.id).." buildable="..tostring(result.buildable).." television="..tostring(instanceof(object,"IsoTelevision")))
    return result
end
-- Operator-invoked only, on the authoritative side. Never repairs map-authored objects.
function WorldEssentialsCommunityRepair(object)
    if isClient() then return false, "Run on the server" end
    if not object or object:getObjectIndex() < 0 then return false, "Object unavailable" end
    local kbw = object:getModData().KBW
    local sprite = object:getSprite()
    local name = sprite and sprite:getName()
    local allowed = kbw and legacy[kbw.buildableId]
    if not allowed or not allowed[name] or kbw.stageId ~= "built"
        or (kbw.variantId and kbw.variantId ~= "") or (kbw.materialId and kbw.materialId ~= "") then
        return false, "No unambiguous legacy mapping; inspect manually"
    end
    local replacement = sprites[name]
    local target = replacement and getSprite(replacement)
    if not target or target:getID() ~= expectedIds[replacement] then return false, "Replacement unavailable or wrong identity" end
    if string.find(name,"DylansRandomFurniture02_3",1,true) and
        (name == "DylansRandomFurniture02_36" or name == "DylansRandomFurniture02_37" or name == "DylansRandomFurniture02_38" or name == "DylansRandomFurniture02_39")
        and not instanceof(object,"IsoTelevision") then return false,"Wrong object class; inspect manually" end
    local square = object:getSquare()
    if not square then return false,"Square unavailable" end
    object:setSpriteFromName(replacement)
    square:RecalcAllWithNeighbours(true)
    object:transmitUpdatedSpriteToClients()
    return true
end
