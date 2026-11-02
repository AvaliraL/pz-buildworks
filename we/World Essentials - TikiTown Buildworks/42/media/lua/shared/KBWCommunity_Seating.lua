-- World Essentials audited adaptation of the upstream generated seating repair.
-- Replaces broken seating positions (Rest / Get on bed) in other packs' in-memory seating data
-- with positions copied from matching vanilla tiles. Seating merge is first-wins per tile, so a
-- seating.txt of ours could not override these. Nothing is written to disk.
local FIXES = {
    { "tikitown_tiles", "furniture_bedding_tterika_01", "furniture_bedding_01", { { 16, 16 }, { 17, 17 }, { 18, 18 }, { 19, 19 }, { 20, 20 }, { 21, 21 }, { 22, 22 }, { 23, 23 }, { 24, 24 }, { 25, 25 }, { 26, 26 }, { 27, 27 }, { 28, 28 }, { 29, 29 }, { 30, 30 }, { 31, 31 } } },
}
local PROPS = { "BlockLeft", "BlockRight" }

local function colRow(i) return i % 8, math.floor(i / 8) end

local function registered(sm, mod)
    local ids = sm:getModIDs()
    return ids ~= nil and ids:contains(mod)
end

local function ensureRegistered(sm, mod)
    if registered(sm, mod) then return true end
    if not getActivatedMods():contains(mod) then return false end
    local info = getModInfoByID(mod)
    if info == nil then return false end
    -- Dedicated-server SeatingManager.init runs before loadMods. Initialize only
    -- this pack; never reset the manager or reload other mods' edited data.
    sm:initModData(info)
    return registered(sm, mod)
end

local function apply(source)
    local sm = SeatingManager and SeatingManager.getInstance and SeatingManager.getInstance()
    if not sm then return false end
    local ready, value = pcall(ensureRegistered, sm, "tikitown_tiles")
    if not ready or value ~= true or not registered(sm, "game") then
        print("[KBWCommunitySeating] " .. tostring(source) .. ": unavailable seating registration; no tiles changed")
        return false
    end
    local fixed, failed = 0, 0
    for _, f in ipairs(FIXES) do
        local mod, dst, src = f[1], f[2], f[3]
        for _, pair in ipairs(f[4]) do
            local ok, err = pcall(function()
                local dc, dr = colRow(pair[1])
                local sc, sr = colRow(pair[2])
                local n = sm:getTilePositionCount("game", src, sc, sr)
                if type(n) ~= "number" or n <= 0 then error("vanilla tile has no positions") end
                local count = sm:getTilePositionCount(mod, dst, dc, dr)
                if type(count) ~= "number" or count < 0 then error("destination positions unavailable") end
                -- Read all source data before removing anything from the destination.
                local positions = {}
                for i = 0, n - 1 do
                    local pos = { id=sm:getTilePositionID("game", src, sc, sr, i),
                        translate=sm:getTilePositionTranslate("game", src, sc, sr, i), properties={} }
                    if not pos.id or not pos.translate then error("incomplete vanilla position") end
                    for _, prop in ipairs(PROPS) do pos.properties[prop]=sm:getTilePositionProperty("game", src, sc, sr, i, prop) end
                    positions[i+1]=pos
                end
                for i = count - 1, 0, -1 do
                    sm:removeTilePosition(mod, dst, dc, dr, i)
                end
                for i = 0, n - 1 do
                    local id = positions[i+1].id
                    local idx = sm:addTilePosition(mod, dst, dc, dr, id)
                    sm:getTilePositionTranslate(mod, dst, dc, dr, idx):set(positions[i+1].translate)
                    for _, p in ipairs(PROPS) do
                        local v = positions[i+1].properties[p]
                        if v then sm:setTilePositionProperty(mod, dst, dc, dr, idx, p, v) end
                    end
                end
            end)
            if ok then fixed = fixed + 1 else
                failed = failed + 1
                if failed == 1 then print("[KBWCommunitySeating] first failure: " .. tostring(err)) end
            end
        end
    end
    local merged = pcall(function() sm:mergeAfterEditing() end)
    print(string.format("[KBWCommunitySeating] %s: fixed=%d failed=%d", tostring(source), fixed, failed))
    return failed == 0 and merged
end

local done = false
local function once(source)
    if done then return end
    done = apply(source) == true
end
if Events.OnGameStart then Events.OnGameStart.Add(function() once("OnGameStart") end) end
if Events.OnServerStarted then Events.OnServerStarted.Add(function() once("OnServerStarted") end) end
