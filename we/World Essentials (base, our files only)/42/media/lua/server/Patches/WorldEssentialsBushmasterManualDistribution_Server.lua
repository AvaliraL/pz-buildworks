-- World Essentials add-on patch:
-- Add the '97 ADI Bushmaster's "Bushmaster Auto Manual" (Base.97BushmasterMagazine) to the general
-- loot tables. The Bushmaster mod only places its manual in the glovebox of a Bushmaster, so the 17
-- Bushmaster part recipes (hood, doors, front windshield, ...) can't be learned without finding a
-- Bushmaster first.
--
-- Drop into:  World Essentials\42\media\lua\server\Patches\
-- Same style as WorldEssentialsAsphaltDistribution_Server.lua / ...SprayPaintDistribution_Server.lua:
-- runs on OnPostDistributionMerge, additive + idempotent, never edits vanilla or mod files, and
-- no-ops if the Bushmaster mod is not active.
--
-- STANDALONE: it does not need the M998 mod (or any other mod except the Bushmaster). The lists and
-- weights below are the same ones the M998 mod uses for its own magazine
-- (Base.92amgeneralM998Magazine, 42.13 / 42.20), copied here as fixed values.
--
-- Only ProceduralDistributions (general container loot) is touched. No vehicle tables. The Bushmaster's
-- own glovebox entry (BUSHGloveBox, weight 80) is left as the mod ships it.
--
-- Kahlua-safe: no next(), goto, //, bitwise ops, load(), debug library.

local PATCH_TAG = "[WorldEssentials][BushmasterManualDistribution]"
local BUSHMASTER_MOD_ID = "97bushmaster"
local ITEM = "Base.97BushmasterMagazine"

-- { ProceduralDistributions list name, weight }
local SPAWNS = {
    { "BookstoreMisc",        0.3 },
    { "CrateMagazines",       0.3 },
    { "MagazineRackMixed",    0.3 },
    { "MechanicShelfBooks",   0.5 },
    { "PostOfficeMagazines",  0.2 },
}

local applied = false

local function isModActive(modId)
    if type(getActivatedMods) ~= "function" then return false end
    local active = getActivatedMods()
    if active == nil then return false end
    if type(active.contains) == "function" then return active:contains(modId) end
    if type(active.size) == "function" and type(active.get) == "function" then
        for i = 0, active:size() - 1 do
            if tostring(active:get(i)) == modId then return true end
        end
    end
    return false
end

-- Does this items array already contain the manual? (idempotency; also catches the bare-key form)
local function hasItem(items)
    for i = 1, #items - 1, 2 do
        if items[i] == ITEM or items[i] == "97BushmasterMagazine" then return true end
    end
    return false
end

local function apply()
    if applied then return end
    applied = true

    if not isModActive(BUSHMASTER_MOD_ID) then
        print(PATCH_TAG .. " Bushmaster mod not active; manual distribution patch skipped.")
        return
    end
    if not (ProceduralDistributions and type(ProceduralDistributions.list) == "table") then
        print(PATCH_TAG .. " ProceduralDistributions not available; nothing added.")
        return
    end

    local added = 0
    local missing = 0
    for _, spawn in ipairs(SPAWNS) do
        local list = ProceduralDistributions.list[spawn[1]]
        if type(list) == "table" and type(list.items) == "table" then
            if not hasItem(list.items) then
                list.items[#list.items + 1] = ITEM
                list.items[#list.items + 1] = spawn[2]
                added = added + 1
            end
        else
            missing = missing + 1
            print(PATCH_TAG .. " list '" .. spawn[1] .. "' not found; skipped.")
        end
    end

    print(PATCH_TAG .. " added the Bushmaster Auto Manual to " .. tostring(added)
        .. " loot lists (" .. tostring(missing) .. " not found).")
end

-- OnPostDistributionMerge fires after every mod has merged its loot tables.
if Events and Events.OnPostDistributionMerge then
    Events.OnPostDistributionMerge.Add(apply)
else
    -- Fallback for older API: apply at server start.
    if Events and Events.OnServerStarted then Events.OnServerStarted.Add(apply) end
    if Events and Events.OnGameStart then Events.OnGameStart.Add(apply) end
end
