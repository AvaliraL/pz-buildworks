-- World Essentials add-on patch:
-- Give vanilla Spray Paint the SAME loot spawns as one vanilla house-paint colour
-- (Base.PaintCyan). Vanilla has no loot entries for SprayPaint at all, yet Knox
-- Buildworks' graffiti buildables need it (1 use each).
--
-- Drop into:  World Essentials\42\media\lua\server\Patches\
-- Same style as WorldEssentialsAsphaltDistribution_Server.lua: runs on
-- OnPostDistributionMerge, additive + idempotent, never edits vanilla files.
--
-- Mirrors ONE colour (PaintCyan), not all 15, so a spray can is exactly as
-- common as a single paint colour. PaintCyan lists (Build 42, verified from base game):
--   ProceduralDistributions.list.ArtSupplies            -> 1
--   ProceduralDistributions.list.CratePaint             -> 20
--   ProceduralDistributions.list.CrateRandomJunk        -> 0.4
--   ProceduralDistributions.list.CrateWallFinish        -> 1
--   ProceduralDistributions.list.PaintStudioTools       -> 2
--   ProceduralDistributions.list.ToolStorePaint         -> 20
-- (No PaintCyan entries in Distributions.lua.) Any list another mod adds with
-- PaintCyan is picked up too, since this runs after every mod has merged.
--
-- Kahlua-safe: no next(), goto, //, bitwise ops.

local PATCH_TAG = "[WorldEssentials][SprayPaintDistribution]"
local SPRAY = "SprayPaint"   -- vanilla key style used in the distribution tables
local SOURCE = "PaintCyan"

local applied = false

local function isKey(v, name)
    return v == name or v == "Base." .. name
end

-- Does this items array already contain a spray paint entry? (idempotency)
local function hasSpray(items)
    for i = 1, #items - 1, 2 do
        if isKey(items[i], SPRAY) then return true end
    end
    return false
end

-- For every PaintCyan entry in an items array, add a same-weight SprayPaint entry.
-- Returns number of entries added.
local function mirrorInItems(items)
    if type(items) ~= "table" then return 0 end
    if hasSpray(items) then return 0 end
    local weights = {}
    for i = 1, #items - 1, 2 do
        if isKey(items[i], SOURCE) then
            weights[#weights + 1] = tonumber(items[i + 1]) or 0
        end
    end
    for _, w in ipairs(weights) do
        items[#items + 1] = SPRAY
        items[#items + 1] = w
    end
    return #weights
end

-- Recursively walk a distribution table (also reaches nested .junk sub-lists).
local function mirrorInTable(root, seen)
    if type(root) ~= "table" then return 0 end
    seen = seen or {}
    if seen[root] then return 0 end
    seen[root] = true
    local added = 0
    if type(root.items) == "table" then
        added = added + mirrorInItems(root.items)
    end
    for _, v in pairs(root) do
        if type(v) == "table" then
            added = added + mirrorInTable(v, seen)
        end
    end
    return added
end

local function apply()
    if applied then return end
    applied = true

    local added = 0
    if ProceduralDistributions and ProceduralDistributions.list then
        added = added + mirrorInTable(ProceduralDistributions.list)
    end
    if VehicleDistributions then
        added = added + mirrorInTable(VehicleDistributions)
    end
    if SuburbsDistributions then
        added = added + mirrorInTable(SuburbsDistributions)
    end
    if BagsAndContainers then
        added = added + mirrorInTable(BagsAndContainers)
    end

    print(PATCH_TAG .. " mirrored PaintCyan -> SprayPaint on "
        .. tostring(added) .. " loot entries.")
end

if Events and Events.OnPostDistributionMerge then
    Events.OnPostDistributionMerge.Add(apply)
else
    if Events and Events.OnServerStarted then Events.OnServerStarted.Add(apply) end
    if Events and Events.OnGameStart then Events.OnGameStart.Add(apply) end
end
