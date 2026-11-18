"""BuildingCraft's Vegetation tab (trees, shrubs, grass) as Knox Buildworks definitions for
"World Essentials - Knox Buildworks Expansion" (user, 2026-11-17: "since they are vanilla tiles, add them to the
base expansion").

Source: BuildingCraft (Workshop 3459887404) media/lua/shared/AddModTextureBase.lua, read at build time
(ModTextureDataTreePL / TreeL / TreeXL / TreeXXL / Shrub / Grass, their Default* cost blocks) and its builders
(server/BuildingObjects/ISBuildTree / ISBuildTowTileTree / ISBuildShrub, BuildingCraftObject.lua):
  * one-tile trees (DefaultDataPL / L / XL / XXL): IsoTree.new(square, sprite)
  * two-tile trees (DefaultDataPL2 / L2, Sprite = {leaves, trunk}): IsoTree.new(square, trunk) + the leaves as
    an attached sprite
  * shrubs (DefaultDataGM1, Sprite = {leaves, bush[, leaves2]}): an IsoThumpable of the bush sprite with the
    leaves attached
  * grass (DefaultDataGrass): the blends_grassoverlays sprite as a one-tile object (it is an attachedFloor
    sprite, so Knox places it as a floor attachment)
All sprites are vanilla (checked against vanilla's tiledefs at build time).

Trees use World Essentials' own WorldEssentialsKnoxNative.OnCreateTree (stage.worldEssentialsNative
.attachedSprite = the leaves), which the expansion already ships for exactly this. Shrubs use a new
callback, WorldEssentialsKnoxVegetation.OnCreateShrub (VEG_LUA, our file). The test bundle runs without World
Essentials, so it also gets TEST_TREE_SHIM_LUA: a verbatim copy of WE's OnCreateTree, defined only when absent.

Writes:
  zomboid/knox_expansion/10_vegetation.json                       (canonical; test bundle source)
  WE work: World Essentials - Knox Buildworks Expansion (our files only)/42/media/KnoxBuildworks/definitions/
           10_vegetation.json (WE ships it empty and already lists it in its manifest) + VEG_LUA
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BC = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600\3459887404\mods\BuildingCraft\42.0\media"
BC_DATA = os.path.join(BC, "lua", "shared", "AddModTextureBase.lua")
WE_EXP_STEAM = (r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600\3733324672\mods"
                r"\World Essentials - Knox Buildworks Expansion\42\media")
VANILLA_MEDIA = r"C:\Program Files (x86)\Steam\steamapps\common\ProjectZomboid\media"
OUT_DIR = r"c:\Users\josep\Kiro\zomboid\knox_expansion"
OUT_JSON = os.path.join(OUT_DIR, "10_vegetation.json")
WORK_EXP = r"c:\Users\josep\Kiro\zomboid\WE_submods\work\World Essentials - Knox Buildworks Expansion (our files only)"
VEG_LUA = "WorldEssentialsKnoxVegetation.lua"          # shared
TEST_TREE_SHIM_LUA = "KBWTest_WEKnoxTreeShim.lua"     # shared, test bundle only

# menu function -> (size slug, size name, subcategory)
# (user, in game 2026-11-17) giant trees and grass removed; the build ghost of the large / giant trees is drawn
# off the placement square (KBW draws their oversized JumboTrees textures as a normal tile)
MENUS = [("ModTextureDataTreePL", "small", "Small", "Trees"),
         ("ModTextureDataTreeL", "medium", "Medium", "Trees"),
         ("ModTextureDataTreeXL", "large", "Large", "Trees"),
         # giants back (user 2026-11-17, after the leafless tiles were dropped); their ghost offset is fixed by
         # VEG_LUA's preview hook
         ("ModTextureDataTreeXXL", "giant", "Giant", "Trees"),
         ("ModTextureDataShrub", "shrub", None, "Shrubs")]
# leafless tiles of the JUMBOXL / JUMBOXXL sheets (checked by render): 0 = bare, 1 = bare with snow
BARE_TILES = (0, 1)
# large deciduous trees: tile 0 of each JUMBOXL sheet is the bare winter tree (no foliage; 1-5 are spring
# blossom, summer, autumn, late autumn). The evergreens' single entry (tile 0) has needles and stays.
EVERGREEN = {"americanholly", "canadianhemlock", "virginiapine"}
SPECIES = {"americanholly": "American Holly", "canadianhemlock": "Canadian Hemlock", "virginiapine": "Virginia Pine",
           "americanlinden": "American Linden", "carolinasilverbell": "Carolina Silverbell",
           "cockspurhawthorn": "Cockspur Hawthorn", "dogwood": "Dogwood", "easternredbud": "Eastern Redbud",
           "redmaple": "Red Maple", "riverbirch": "River Birch", "yellowwood": "Yellowwood"}
TWO_TILE = {"DefaultDataPL2", "DefaultDataL2"}
SHRUB = {"DefaultDataGM1"}
GRASS = {"DefaultDataGrass"}
# BuildingCraft's NeedTools for every vegetation block: any of these digging tools
DIG_TOOLS = ["Base.Shovel", "Base.Shovel2", "Base.SpadeForged", "Base.SpadeWood", "Base.EntrenchingTool"]
TIMED_ACTION = "BuildLowNoTool"      # vanilla has no digging build action script; the low build animation
TIME = 200
NS = "worldessentials.kbw.veg_"
TAGS = ["world-essentials", "buildingcraft-replacement", "vanilla-sprites", "vegetation"]


def _defaults(t):
    out = {}
    for m in re.finditer(r"local (Default\w+)\s*=\s*\{(.*?)\n\}", t, re.S):
        body = m.group(2)
        out[m.group(1)] = {
            "skill": re.search(r"NeedSkill\s*=\s*Perks\.(\w+)", body).group(1),
            "level": int(re.search(r"NeedSkillLevel\s*=\s*(\d+)", body).group(1)),
            "xp": int(re.search(r"SkillXp\s*=\s*(\d+)", body).group(1)),
            "materials": [(a, int(b)) for a, b in re.findall(r"tMaterial\s*=\s*'([^']+)'\s*,\s*Amount\s*=\s*(\d+)", body)],
            "tools": bool(re.search(r"NeedTools\s*=\s*\{\s*\{\s*'", body)),
        }
    return out


def _menus(t):
    out = {}
    for m in re.finditer(r"local function (ModTextureData\w+)\(\)(.*?)\nend", t, re.S):
        body = "\n".join(l for l in m.group(2).splitlines() if not l.strip().startswith("--"))
        out[m.group(1)] = [(d, re.findall(r"'([^']+)'", s))
                           for d, s in re.findall(r"Default\s*=\s*(Default\w+)\s*,\s*Sprite\s*=\s*\{([^}]*)\}", body)]
    return out


def _vanilla_sprites():
    import glob
    import kbw_tilepatch as k
    have = set()
    for f in glob.glob(os.path.join(VANILLA_MEDIA, "tile_definitions", "*.tiles")) + glob.glob(os.path.join(VANILLA_MEDIA, "*.tiles")):
        try:
            _v, ts, _o = k._parse(open(f, "rb").read())
        except Exception:
            continue
        for sheet, tt in ts.items():
            for i in range(len(tt[6])):
                have.add("%s_%d" % (sheet.decode(), i))
    return have


def _species(sprite):
    m = re.match(r"e_([a-z]+?)(JUMBO\w*)?_\d+_\d+$", sprite)
    return m.group(1) if m else None


def buildables():
    t = open(BC_DATA, encoding="utf-8", errors="replace").read()
    defs, menus = _defaults(t), _menus(t)
    have = _vanilla_sprites()
    out, seen = [], set()
    for fn, slug, size, sub in MENUS:
        entries = menus[fn]
        counters = {}
        for d, spr in entries:
            dd = defs[d]
            if (slug in ("large", "giant") and int(spr[0].rsplit("_", 1)[1]) in BARE_TILES
                    and _species(spr[0]) not in EVERGREEN):
                continue                                  # bare winter tree
            missing = [s for s in spr if s not in have]
            if missing:
                raise RuntimeError("%s entry %s: sprites not in vanilla %s" % (fn, spr, missing))
            native, callbacks, obj = None, None, None
            if d in TWO_TILE:
                leaves, main = spr[0], spr[1]
                native = {"kind": "tree", "attachedSprite": leaves}
            elif d in SHRUB:
                leaves, main = spr[0], spr[1]
                extra = [s for s in spr[2:] if s]
                native = {"kind": "shrub", "attachedSprites": [leaves] + extra}
            else:
                leaves, main = None, spr[0]
                if d not in GRASS:
                    native = {"kind": "tree"}
            if d in GRASS:
                obj = {"isThumpable": False, "dismantable": True, "blockAllSquare": False, "canPassThrough": True}
            elif d in SHRUB:
                callbacks = {"onCreate": "WorldEssentialsKnoxVegetation.OnCreateShrub"}
                obj = {"isThumpable": True, "dismantable": True, "blockAllSquare": False, "canPassThrough": True}
            else:
                callbacks = {"onCreate": "WorldEssentialsKnoxNative.OnCreateTree"}
                obj = {"isThumpable": False, "dismantable": False, "blockAllSquare": False}
            if size:
                sp = _species(main)
                gid, gname = "%s_%s" % (slug, sp), "%s %s" % (size, SPECIES[sp])
            else:
                gid, gname = slug, "Shrubs" if slug == "shrub" else "Grass"
            counters[gid] = counters.get(gid, 0) + 1
            n = counters[gid]
            bid = NS + "%s_%s" % (slug, (leaves or main))
            if bid in seen:
                bid += "_" + main
            assert bid not in seen, bid
            seen.add(bid)
            inputs = []
            if dd["tools"]:
                inputs.append({"id": "tool_dig", "role": "tool", "mode": "keep", "resourceType": "Item",
                               "items": list(DIG_TOOLS), "amount": 1, "flags": ["Prop1"]})
            for j, (item, amt) in enumerate(dd["materials"], 1):
                inputs.append({"id": "source_material_%d" % j, "role": "material", "mode": "consume",
                               "resourceType": "Item", "items": [item], "amount": amt})
            stage = {"id": "built",
                     "geometry": {"faces": {"N": {"layers": [{"rows": [[main]]}]}}},
                     "requirements": {"inputs": inputs, "skills": {dd["skill"]: dd["level"]}},
                     "construction": {"time": TIME, "timedAction": TIMED_ACTION,
                                      "completionSound": "BuildWoodenStructureLarge",
                                      "xp": {dd["skill"]: dd["xp"]}, "category": "Farming"},
                     "object": obj}
            if callbacks:
                stage["callbacks"] = callbacks
            if native:
                stage["worldEssentialsNative"] = native
            out.append({"id": bid, "displayName": "%s %d" % (gname, n), "category": "Vegetation", "subcategory": sub,
                        "iconSprite": leaves or main, "allowSpriteReuse": True,
                        "placement": {"kind": "object", "requiresFloor": True},
                        "group": {"id": NS + gid, "name": gname, "level": n},
                        "tags": list(TAGS), "stages": [stage]})
    return out


SHRUB_LUA = r'''-- Knox Buildworks Expansion vegetation (pz_craft_loops/knox_vegetation.py; BuildingCraft's Vegetation tab).
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
'''


def _we_tree_function():
    src = open(os.path.join(WE_EXP_STEAM, "lua", "shared", "WorldEssentialsKnoxNativeCallbacks.lua"), encoding="utf-8").read()
    rm = re.search(r"local function removePlaceholder\(object\).*?\nend\n", src, re.S).group(0)
    tree = re.search(r"function WorldEssentialsKnoxNative\.OnCreateTree\(params\).*?\nend\n", src, re.S).group(0)
    return rm, tree


def write_test_shim(path):
    rm, tree = _we_tree_function()
    tree = tree.replace("function WorldEssentialsKnoxNative.OnCreateTree(params)",
                        "WorldEssentialsKnoxNative.OnCreateTree = function(params)")
    lua = ("-- TEST BUNDLE ONLY (pz_craft_loops/knox_vegetation.py). The bundle runs without World Essentials; its\n"
           "-- vegetation definitions call WE's WorldEssentialsKnoxNative.OnCreateTree. This is a verbatim copy of\n"
           "-- that function (World Essentials - Knox Buildworks Expansion, WorldEssentialsKnoxNativeCallbacks.lua),\n"
           "-- defined only when WE's is absent.\n"
           "WorldEssentialsKnoxNative = WorldEssentialsKnoxNative or {}\n"
           "if not WorldEssentialsKnoxNative.OnCreateTree then\n" + rm + tree + "end\n")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8", newline="\n").write(lua)


def write_veg_lua(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8", newline="\n").write(SHRUB_LUA)


def main():
    bs = buildables()
    os.makedirs(OUT_DIR, exist_ok=True)
    doc = {"schemaVersion": 1, "buildables": bs}
    json.dump(doc, open(OUT_JSON, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    dst = os.path.join(WORK_EXP, "42", "media", "KnoxBuildworks", "definitions", "10_vegetation.json")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    json.dump(doc, open(dst, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    write_veg_lua(os.path.join(WORK_EXP, "42", "media", "lua", "shared", VEG_LUA))
    from collections import Counter
    print("wrote %s (%d buildables) %s" % (OUT_JSON, len(bs), dict(Counter(b["stages"][0].get("worldEssentialsNative", {}).get("kind", "grass") for b in bs))))
    print("groups", len({b["group"]["id"] for b in bs}))


if __name__ == "__main__":
    main()
