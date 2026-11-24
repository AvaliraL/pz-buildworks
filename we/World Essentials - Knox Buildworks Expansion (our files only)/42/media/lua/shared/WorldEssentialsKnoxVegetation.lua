-- Knox Buildworks Expansion vegetation (pz_craft_loops/knox_vegetation.py; BuildingCraft's Vegetation tab).
-- Trees use World Essentials' WorldEssentialsKnoxNative.OnCreateTree. Shrubs are what BuildingCraft's
-- ISBuildShrub makes: an IsoThumpable of the bush sprite (Knox already built it) with its leaves attached.
WorldEssentialsKnoxVegetation = WorldEssentialsKnoxVegetation or {}

function WorldEssentialsKnoxVegetation.OnCreateShrub(params)
    local object = params and params.thumpable or nil
    local native = params and params.stage and params.stage.worldEssentialsNative or nil
    local sprites = native and native.attachedSprites or nil
    if not object or not sprites or not object.addAttachedAnimSpriteByName then return nil end
    for i = 1, #sprites do
        if sprites[i] and sprites[i] ~= "" then object:addAttachedAnimSpriteByName(sprites[i]) end
    end
    -- nil: Knox transmits the object (with its attached sprites) as usual
    return nil
end

-- Build preview of the big trees. Their JumboTrees textures are 2x / 3x a tile and IsoTree draws them
-- shifted; Knox's preview draws every sprite unshifted, so the ghost stood off the placement square.
-- BuildingCraft's own ISBuildTree:render shifts them by (128, 256) per size step at 2x tiles (Large = 1,
-- Giant = 2). Knox's preview gets each sprite through KBWBuildingObject:getCachedSprite; for these sprites
-- only, we hand back a small stand-in whose RenderGhostTileColor draws the real sprite with that shift.
-- Wrapped in memory only; Knox's files are not edited.
local function jumboStep(name)
    if type(name) ~= "string" then return 0 end
    if string.find(name, "JUMBOXXL_", 1, true) then return 2 end
    if string.find(name, "JUMBOXL_", 1, true) then return 1 end
    return 0
end

local proxies = {}
local function proxyFor(name, sprite, step)
    local p = proxies[name]
    if p and p.sprite == sprite then return p end
    p = {sprite = sprite}
    function p:RenderGhostTileColor(x, y, z, a4, a5, a6, a7, a8, a9)
        local scale = getCore and getCore().getTileScale and getCore():getTileScale() or 2
        local ox, oy = step * 64 * scale, step * 128 * scale
        if a9 ~= nil then        -- (x, y, z, offX, offY, r, g, b, a)
            return sprite:RenderGhostTileColor(x, y, z, a4 + ox, a5 + oy, a6, a7, a8, a9)
        end
        return sprite:RenderGhostTileColor(x, y, z, ox, oy, a4, a5, a6, a7)
    end
    function p:RenderGhostTile(x, y, z)
        local scale = getCore and getCore().getTileScale and getCore():getTileScale() or 2
        return sprite:RenderGhostTileColor(x, y, z, step * 64 * scale, step * 128 * scale, 1, 1, 1, 0.6)
    end
    proxies[name] = p
    return p
end

local function installPreviewShift()
    local ok, KBO = pcall(require, "KnoxBuildworks/BuildingObjects/KBWBuildingObject")
    if not ok or type(KBO) ~= "table" or type(KBO.getCachedSprite) ~= "function" then return end
    -- re-wrap if something replaced the function since (World Essentials copies its own methods in)
    if KBO.getCachedSprite == KBO.__weKnoxJumboPreview then return end
    local orig = KBO.getCachedSprite
    local wrapped = function(self, spriteName)
        local sprite = orig(self, spriteName)
        local step = jumboStep(spriteName)
        if sprite and step > 0 then return proxyFor(spriteName, sprite, step) end
        return sprite
    end
    KBO.getCachedSprite = wrapped
    KBO.__weKnoxJumboPreview = wrapped
end

installPreviewShift()
if Events and Events.OnGameStart then Events.OnGameStart.Add(installPreviewShift) end
