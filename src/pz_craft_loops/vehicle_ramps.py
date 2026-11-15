# -*- coding: utf-8 -*-
"""Generate 73_kbwcb_vehicle_ramps.json (user, 2026-11-14): vanilla B42's drivable car ramps
(ramps_01, defined in media/tile_definitions/tiledefinitions_b42chunkcaching.tiles, art in
B42ChunkCaching2x.pack) as one KBW buildable with four faces.

Each ramp is a straight run of 20 tiles that climbs exactly one storey. Every tile carries the
vehicle physics shape (PhysicsMesh ramp20segment<n><dir>), SlopedSurfaceDirection (the HIGH end)
and SlopedSurfaceHeightMin/Max stepping 5 per tile (0..100), plus solidfloor.
  0-19  rises to the north   24-43 rises to the south
  48-67 rises to the west    72-91 rises to the east       (23 = a plain solidfloor tile, unused)
Layout copies BuildingCraft's ISBuildRamp (B42), which places the same 20 tiles in a line: index
0 / 24 / 48 / 72 is the low end. KBW geometry rows run north -> south and columns west -> east.

Placed like BuildingCraft's: plain IsoObjects (KBW isProp -> ISMoveableSpriteProps, falling back
to IsoObject + AddTileObject), on the ground floor, all 20 squares clear. BuildingCraft can also
delete the floor one storey up along the run; KBW has no such step, so the upper end needs open air
above it and a floor to drive onto (build the ramp before the deck, or remove that floor first).
Cost: BuildingCraft's (30 stones, 20 stone blocks, 4 full concrete buckets = 16 uses, club hammer,
Masonry 2). NOT yet tested in game.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kbw_tilepatch as k  # noqa: E402

OUT = r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables\73_kbwcb_vehicle_ramps.json"
SHEET = "ramps_01"
TILES = r"C:\Program Files (x86)\Steam\steamapps\common\ProjectZomboid\media\tile_definitions\tiledefinitions_b42chunkcaching.tiles"
RUNS = {"N": 0, "S": 24, "W": 48, "E": 72}      # KBW face (= the high end) -> low-end index


def _sp(i):
    return "%s_%d" % (SHEET, i)


def _check():
    """The tiles are what the layout assumes: 20 segments per run, rising toward the face."""
    _v, ts, _o = k._parse(open(TILES, "rb").read())
    t = ts[SHEET.encode()]
    for face, base in RUNS.items():
        for n in range(20):
            p = {a.decode(): b.decode() for a, b in t[6][base + n]}
            assert p.get("SlopedSurfaceDirection") == face, (face, base + n, p)
            assert p.get("PhysicsMesh") == "ramp20segment%d%s" % (n + 1, face.lower()), (base + n, p)
            assert p.get("SlopedSurfaceHeightMax") == str(5 * (n + 1)), (base + n, p)


def _faces():
    f = {}
    run = lambda base: [_sp(base + n) for n in range(20)]          # low -> high
    f["N"] = {"layers": [{"rows": [[s] for s in reversed(run(RUNS["N"]))]}]}   # high end north (top row)
    f["S"] = {"layers": [{"rows": [[s] for s in run(RUNS["S"])]}]}             # high end south (last row)
    f["W"] = {"layers": [{"rows": [list(reversed(run(RUNS["W"])))]}]}         # high end west (first column)
    f["E"] = {"layers": [{"rows": [run(RUNS["E"])]}]}                         # high end east (last column)
    return f


def build_document():
    _check()
    req = {"inputs": [
        {"id": "tool_clubhammer", "role": "tool", "mode": "keep", "resourceType": "Item",
         "tags": ["base:clubhammer"], "amount": 1},
        {"id": "source_material_1", "role": "material", "mode": "consume", "resourceType": "Item",
         "items": ["Base.Stone2"], "amount": 30},
        {"id": "source_material_2", "role": "material", "mode": "consume", "resourceType": "Item",
         "items": ["Base.StoneBlock"], "amount": 20},
        # 4 full buckets (UseDelta 0.25 = 4 uses each); KBW totals uses across buckets
        {"id": "source_material_3", "role": "consumable", "mode": "drain", "resourceType": "Item",
         "items": ["Base.BucketConcreteFull"], "amount": 16, "uses": 16},
    ], "skills": {"Masonry": 2}}
    b = {
        "id": "kbwcb.stairs.vehicle_ramp",
        "allowSpriteReuse": True,
        "translationKey": "IGUI_kbwcb_stairs_vehicle_ramp",
        "displayName": "Vehicle Ramp (20 Tiles, One Storey)",
        "category": "Stairs",
        "subcategory": "Ramps",
        "material": "Stone",
        "materialTags": ["Stone"],
        "iconSprite": _sp(RUNS["N"] + 10),
        "placement": {"kind": "object", "requiresFloor": True},
        "tags": ["kbwcb", "vanilla-tiles", "ramp", "vehicle"],
        "construction": {"time": 1200, "timedAction": "BuildLowHammer",
                         "completionSound": "BuildWoodenStructureLarge", "xp": {"Masonry": 40},
                         "category": "Masonry"},
        "stages": [{"id": "built", "geometry": {"faces": _faces()}, "requirements": req,
                    "object": {"isProp": True, "dismantable": True, "blockAllSquare": False,
                               "canPassThrough": True}}],
    }
    return {"schemaVersion": 1, "category": "Stairs",
            "source": ("Vanilla B42 ramps_01 drivable car ramps (20 tiles, one storey, four directions), "
                       "laid out like BuildingCraft's ISBuildRamp. Generated by pz_craft_loops/vehicle_ramps.py."),
            "buildables": [b]}


REMOVE_LUA_NAME = "KBWCommunity_RampRemove.lua"

# Removing a built ramp (user, 2026-11-14: "the ramps can't be destroyed"). Nothing in the game can:
# vanilla ISDestroyCursor:canDestroy only destroys a solidfloor object above ground (z > 0), KBW's
# dismantle needs an IsoThumpable (these are plain props), and ramps_01 has no IsMoveAble. Same as
# BuildingCraft, which ships its own "Delete Ramp" option (BuildingCraftMenu.DeleteRamp). Ours:
# right-click a ramp tile that Knox Buildworks built (modData.KBW; map ramps and BuildingCraft ramps
# never match), with a destroy tool (vanilla's set: sledgehammer, stone maul, club hammer, pickaxe),
# removes the whole 20-tile strip. Strip math = BuildingCraft's, which our layout matches exactly.
_REMOVE_LUA = r'''-- AUTO-GENERATED by pz_craft_loops/vehicle_ramps.py -- do not edit by hand.
-- "Remove Vehicle Ramp": the vanilla sledgehammer never destroys a ground-level floor tile, and the
-- ramps_01 tiles can't be picked up, so a built ramp had no way to be removed. Only ramps built with
-- Knox Buildworks (modData.KBW) get the option; map ramps and BuildingCraft ramps are left alone.
-- Kahlua-safe: no next, goto, integer division or bitwise operators.
local PREFIX = "ramps_01_"

local function rampIndex(obj)
    local sprite = obj and obj:getSprite()
    local name = sprite and sprite:getName()
    if not name or string.sub(name, 1, string.len(PREFIX)) ~= PREFIX then return nil end
    return tonumber(string.sub(name, string.len(PREFIX) + 1))
end

local function isOurRamp(obj)
    if not rampIndex(obj) or not obj:hasModData() then return false end
    return obj:getModData().KBW ~= nil
end

-- The 20 squares of the strip the clicked tile belongs to (BuildingCraft's layout).
local function stripSquares(x, y, index)
    local out = {}
    for i = 0, 19 do
        if index >= 0 and index <= 19 then out[#out + 1] = {x, y + index - i}
        elseif index >= 24 and index <= 43 then out[#out + 1] = {x, y + 43 - index - 19 + i}
        elseif index >= 48 and index <= 67 then out[#out + 1] = {x + index - 48 - i, y}
        elseif index >= 72 and index <= 91 then out[#out + 1] = {x + 91 - index - 19 + i, y}
        end
    end
    return out
end

local function isDestroyTool(item)
    return not item:isBroken() and (item:hasTag(ItemTag.SLEDGEHAMMER) or item:hasTag(ItemTag.STONE_MAUL)
        or item:hasTag(ItemTag.CLUB_HAMMER) or item:hasTag(ItemTag.PICK_AXE))
end

local function removeTile(obj)
    if isClient() then
        sledgeDestroy(obj)
    else
        obj:getSquare():transmitRemoveItemFromSquare(obj)
    end
end

local function onRemove(playerObj, square, index)
    local z = square:getZ()
    local cells = stripSquares(square:getX(), square:getY(), index)
    for c = 1, #cells do
        local sq = getCell():getGridSquare(cells[c][1], cells[c][2], z)
        if sq then
            local objects = sq:getObjects()
            for i = objects:size() - 1, 0, -1 do
                local obj = objects:get(i)
                if isOurRamp(obj) then removeTile(obj) end
            end
        end
    end
end

local function onFill(playerNum, context, worldObjects, test)
    if test then return end
    local square
    for i = 1, #worldObjects do
        square = worldObjects[i] and worldObjects[i]:getSquare()
        if square then break end
    end
    if not square then return end
    local objects = square:getObjects()
    for i = 0, objects:size() - 1 do
        local obj = objects:get(i)
        if isOurRamp(obj) then
            local playerObj = getSpecificPlayer(playerNum)
            local label = getTextOrNull("ContextMenu_KBWCB_RemoveVehicleRamp") or "Remove Vehicle Ramp"
            local option = context:addOption(label, playerObj, onRemove, square, rampIndex(obj))
            if not playerObj:getInventory():getFirstEvalRecurse(isDestroyTool) then
                option.notAvailable = true
                local tip = ISWorldObjectContextMenu.addToolTip()
                tip.description = getTextOrNull("Tooltip_KBWCB_RemoveVehicleRamp")
                    or "Needs a sledgehammer, stone maul, club hammer or pickaxe."
                option.toolTip = tip
            end
            return
        end
    end
end

Events.OnFillWorldObjectContextMenu.Add(onFill)
'''


def write_ramp_remove_lua(dest_path):
    for bad in ("next(", "goto ", "//", "debug.", " & ", " | ", "<<", ">>"):
        if bad in _REMOVE_LUA.replace("~=", ""):
            raise RuntimeError("Kahlua-unsafe construct in ramp remove Lua: %r" % bad)
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    open(dest_path, "w", encoding="utf-8", newline="\n").write(_REMOVE_LUA)


def main():
    doc = build_document()
    json.dump(doc, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("wrote %s (%d buildables)" % (OUT, len(doc["buildables"])))


if __name__ == "__main__":
    main()
