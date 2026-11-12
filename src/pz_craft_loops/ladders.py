# -*- coding: utf-8 -*-
"""Climbable ladders (user, 2026-08-28): B42's own ladder mechanic on more tiles.

HOW VANILLA DOES IT (read from projectzomboid.jar + media/lua, 2026-08-28). Everything is driven by
the tile flags ladderN / ladderS / ladderE / ladderW (IsoPropertyType.LADDER_*); no Lua is needed:
  * IsoGridSquare.getLadder(): the first object on the square whose sprite has one of the flags;
  * "Climb Ladder" (ISWorldObjectContextMenuLogic, Java): standing on a square with a solid floor that
    holds a ladder. ClimbState keeps climbing while the square above also has a ladder and steps off
    at the top onto the next square past the wall;
  * "Climb Down Ladder": from the upper level, a ladder one level down on an adjacent square that
    faces you (getLadderUnder), with NO solid floor directly above it;
  * footsteps: wood or metal sounds from the tile's material.
Vanilla ladder tiles pair the flag with attachedN/S/E/W, Facing, BlocksPlacement and forceFade.

WHAT THIS FILE BUILDS
  1. TikiTown: Drazion's tterika sewer ladder (location_sewer_tterika_01_0 W / _1 N) carries the OLD
     sheet-rope flags (climbSheetW/N: rope climbing, not the ladder animation). Our OWN COPIES of the
     two tiles (KBWTikiTownLadders_0/1, written by tikitown_wall_overlays.write_overlay_assets) swap
     them for ladderW/ladderN and drop the moveable keys (vanilla ladders are not moveables). The
     pack tiles are untouched, so map-placed tterika ladders keep working as Drazion ships them.
     Depth: vanilla's own sewer-ladder depth (location_sewer_01_32 / _33), as vanilla assigns it to
     its other ladders. -> zomboid/tikitown/45_tikitown_ladders.json
  2. Community submod: the vanilla ladders nothing builds yet (World Essentials already builds the
     sewer ladders): wooden carpentry_02_84-87, the rusty and the dark steel railroad ladders
     industry_railroad_05. Vanilla tiles, no tile work. One "Ladders" card. -> 72_kbwcb_ladders.json
     Same card (user, 2026-08-28): Dirkies' Iron Ladder (edit_ddd_RUS_decor_house_01 16-19, sheet-rope
     flags on the pack) and its Iron Ladder Top (96-99), both on our copies in the ice-shell tileset
     (kbw_tilepatch.DECOR_*): the ladder gets ladderW/N/S/E; the top is a walk-through decoration
     for the open square above a ladder (not climbable; requiresFloor False like the ladders).

Placement: like World Essentials' sewer ladders (object, walk-through, dismantlable), but with
requiresFloor False so a second ladder can be stacked over the open square above the first (KBW then
still requires an adjacent floor). Metal cost = WE's Sewer Ladders (style 2, no landing floor), read
from WE's installed definition with a fallback copy. WE's "Style 1" adds a landing floor through its
own Lua callback; not used here, so the test bundle (no WE) builds the same pieces.
NOT yet tested in game.
"""
import copy
import json
import os

OUT_TT = r"c:\Users\josep\Kiro\zomboid\tikitown\45_tikitown_ladders.json"
WE_STAIRS = (r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600\3733324672\mods"
             r"\World Essentials - Knox Buildworks Expansion\42\media\KnoxBuildworks\definitions\09_stairs.json")
WE_LADDER_ID = "worldessentials.kbw.location_sewer_01_32_stair_312"   # Sewer Ladders - Style 2

CATEGORY, SUBCATEGORY = "Stairs", "Ladders"
PLACEMENT = {"kind": "object", "requiresFloor": False}
# same object block as WE's sewer ladders
OBJECT = {"isThumpable": False, "dismantable": True, "blockAllSquare": False, "canPassThrough": True,
          "isCorner": True}

# ---- 1. TikiTown copies ------------------------------------------------------------------------
SHEET = "location_sewer_tterika_01"
COPY_TILESET = "KBWTikiTownLadders"
LADDER_SRC = (0, 1)                       # 0 = west wall (ladderW), 1 = north wall (ladderN)
_LADDER_FLAG = {0: b"ladderW", 1: b"ladderN"}
_DROP = {b"climbSheetW", b"climbSheetN", b"MoveType", b"PickUpLevel", b"PickUpTool", b"PickUpWeight",
         b"PlaceTool"}
# copy sprite -> sprite whose depth texture it uses (vanilla's sewer ladder, same pose)
DEPTH_OF = {}


def copy_sprite(i):
    """Our copy of location_sewer_tterika_01_<i>."""
    return "%s_%d" % (COPY_TILESET, LADDER_SRC.index(i))


for _i, _d in ((0, "location_sewer_01_32"), (1, "location_sewer_01_33")):
    DEPTH_OF[copy_sprite(_i)] = _d


def copy_props(i, src_props):
    """Tile props for our copy: the pack tile's, sheet-rope + moveable keys swapped for ladder flags."""
    out = [(k, v) for k, v in src_props if k not in _DROP]
    keys = {k for k, _v in out}
    for k in (_LADDER_FLAG[i], b"BlocksPlacement", b"forceFade"):
        if k not in keys:
            out.append((k, b""))
    return sorted(out)


_METAL_FALLBACK = {   # WE Sewer Ladders - Style 2 (read 2026-08-28)
    "requirements": {
        "inputs": [
            {"id": "tool_welding_mask", "role": "tool", "mode": "keep", "resourceType": "Item",
             "tags": ["base:weldingmask"], "amount": 1},
            {"id": "source_material_1", "role": "material", "mode": "consume", "resourceType": "Item",
             "items": ["Base.MetalPipe"], "amount": 2},
            {"id": "source_material_2", "role": "material", "mode": "consume", "resourceType": "Item",
             "items": ["Base.MetalBar"], "amount": 2},
            {"id": "source_material_3", "role": "material", "mode": "consume", "resourceType": "Item",
             "items": ["Base.Screws"], "amount": 2},
            {"id": "source_material_4", "role": "consumable", "mode": "drain", "resourceType": "Item",
             "items": ["Base.WeldingRods"], "amount": 1, "uses": 4},
            {"id": "source_material_5", "role": "consumable", "mode": "drain", "resourceType": "Item",
             "items": ["Base.BlowTorch"], "amount": 1, "uses": 4}],
        "skills": {"MetalWelding": 4}},
    "construction": {"time": 200, "timedAction": "BuildLowMetal", "completionSound": "BuildMetalStructureMedium",
                     "xp": {"MetalWelding": 40}, "category": "Metalworking"},
}
# wooden ladder: hammer + saw, 3 planks + 6 nails, Woodwork 3 (lighter than a wooden stair section)
_WOOD = {
    "requirements": {
        "inputs": [
            {"id": "tool_hammer", "role": "tool", "mode": "keep", "resourceType": "Item",
             "tags": ["base:hammer"], "amount": 1},
            {"id": "tool_saw", "role": "tool", "mode": "keep", "resourceType": "Item",
             "tags": ["base:saw"], "amount": 1},
            {"id": "source_material_1", "role": "material", "mode": "consume", "resourceType": "Item",
             "items": ["Base.Plank"], "amount": 3},
            {"id": "source_material_2", "role": "material", "mode": "consume", "resourceType": "Item",
             "items": ["Base.Nails"], "amount": 6}],
        "skills": {"Woodwork": 3}},
    "construction": {"time": 150, "timedAction": "BuildWoodenStructureMedium",
                     "completionSound": "BuildWoodenStructureMedium", "xp": {"Woodwork": 30},
                     "category": "Carpentry"},
}


def metal_cost():
    """(requirements, construction, source) of WE's Sewer Ladders - Style 2."""
    try:
        d = json.load(open(WE_STAIRS, encoding="utf-8-sig"))
        st = next(x for x in d["buildables"] if x.get("id") == WE_LADDER_ID)["stages"][0]
        return copy.deepcopy(st["requirements"]), copy.deepcopy(st["construction"]), "WE installed"
    except Exception:
        return (copy.deepcopy(_METAL_FALLBACK["requirements"]), copy.deepcopy(_METAL_FALLBACK["construction"]),
                "fallback copy")


def _buildable(bid, tkey, name, faces, cost, material, tags):
    req, con = cost
    first = next(iter(faces.values()))
    return {
        "id": bid,
        "allowSpriteReuse": True,
        "translationKey": tkey,
        "displayName": name,
        "category": CATEGORY,
        "subcategory": SUBCATEGORY,
        "material": material,
        "materialTags": [material],
        "iconSprite": first,
        "placement": dict(PLACEMENT),
        "tags": tags,
        "stages": [{
            "id": "built",
            "geometry": {"faces": {f: {"layers": [{"rows": [[s]]}]} for f, s in faces.items()}},
            "requirements": copy.deepcopy(req),
            "construction": copy.deepcopy(con),
            "object": dict(OBJECT),
        }],
    }


# ---- wall requirement (user, 2026-08-28: "our ladders are free standing ... this is a problem") ----
# The game's climb code only needs the ladder flag; it never checks for a wall, and KBW's own
# needToBeAgainstWall only looks at the square's own west / north wall for non-WallObject tiles, so it
# would refuse every east / south ladder. This onIsValid finds the ladder's wall edge from its TILE
# (ladderW/N/E/S, attached* as fallback) and requires a wall, window wall or door wall there; an east
# or south edge is the west / north wall of the next square. Ladder tops (decoration on the open
# square above) instead require a ladder on the square directly below.
LADDER_ISVALID = "KBWLadderGuard.OnIsValid"
LADDER_TOP_ISVALID = "KBWLadderGuard.OnIsValidTop"
GUARD_LUA_COMMUNITY = "KBWCommunity_LadderGuard.lua"
GUARD_LUA_TIKITOWN = "KBWTikiTown_LadderGuard.lua"
_GUARD_LUA = r'''-- AUTO-GENERATED by pz_craft_loops/ladders.py -- do not edit by hand.
-- Ladders must hang on a wall (Knox Buildworks onIsValid for our ladder buildables). Both submods
-- ship this same code under their own file name; the global is defined once either way.
-- Kahlua-safe: no next, goto, integer division or bitwise operators.
KBWLadderGuard = KBWLadderGuard or {}
local G = KBWLadderGuard

local EDGE_FLAGS = {
    W = { "WallW", "WindowW", "DoorWallW", "WallNW", "WallWTrans" },
    N = { "WallN", "WindowN", "DoorWallN", "WallNW", "WallNTrans" },
}
local DIRS = { "W", "N", "E", "S" }

local function spriteEdge(spriteName)
    if not spriteName then return nil end
    local sprite = getSprite(spriteName)
    local props = sprite and sprite:getProperties() or nil
    if not props then return nil end
    for index = 1, #DIRS do
        if props:has("ladder" .. DIRS[index]) then return DIRS[index] end
    end
    for index = 1, #DIRS do
        if props:has("attached" .. DIRS[index]) then return DIRS[index] end
    end
    return nil
end

local function propsHaveAny(props, flags)
    if not props then return false end
    for index = 1, #flags do
        if props:has(flags[index]) then return true end
    end
    return false
end

local function squareHasEdge(square, flags)
    if propsHaveAny(square:getProperties(), flags) then return true end
    local objects = square:getObjects()
    for index = 0, objects:size() - 1 do
        local object = objects:get(index)
        if object and propsHaveAny(object:getProperties(), flags) then return true end
    end
    return false
end

local function spriteOf(params)
    return params.spriteName or (params.tile and params.tile.sprite) or nil
end

-- true when the wall edge the ladder tile hangs on has a wall
function G.OnIsValid(params)
    local square = params and params.square
    if not square then return false end
    local ok, valid = pcall(function()
        local edge = spriteEdge(spriteOf(params))
        if not edge then return false end
        local target, flags = square, EDGE_FLAGS.W
        if edge == "N" then
            flags = EDGE_FLAGS.N
        elseif edge == "E" then
            target = getCell():getGridSquare(square:getX() + 1, square:getY(), square:getZ())
        elseif edge == "S" then
            target = getCell():getGridSquare(square:getX(), square:getY() + 1, square:getZ())
            flags = EDGE_FLAGS.N
        end
        if not target then return false end
        return squareHasEdge(target, flags)
    end)
    return ok and valid == true
end

-- ladder top: needs a ladder on the square directly below
function G.OnIsValidTop(params)
    local square = params and params.square
    if not square then return false end
    local ok, valid = pcall(function()
        local below = getCell():getGridSquare(square:getX(), square:getY(), square:getZ() - 1)
        return below ~= nil and below:getLadder() ~= nil
    end)
    return ok and valid == true
end
'''


def write_ladder_guard_lua(dest_path):
    body = _GUARD_LUA.replace("-- AUTO-GENERATED", "")
    for bad in ("next(", "goto ", "//", "debug.", "~ ", " & ", " | ", "<<", ">>"):
        if bad in body.replace("~=", ""):
            raise RuntimeError("Kahlua-unsafe construct in ladder guard: %r" % bad)
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    open(dest_path, "w", encoding="utf-8", newline="\n").write(_GUARD_LUA)


def _guard(b, top=False):
    """Hang the wall / ladder-below check on every stage of a ladder buildable."""
    for st in b["stages"]:
        st.setdefault("callbacks", {})["onIsValid"] = LADDER_TOP_ISVALID if top else LADDER_ISVALID
    return b


def build_tikitown_doc():
    req, con, src = metal_cost()
    b = _buildable("worldessentials.tikitown.tterika_ladder", "IGUI_WETiki_tterika_ladder", "Rusted Iron Ladder",
                   {"W": copy_sprite(0), "N": copy_sprite(1)}, (req, con), "Metal",
                   ["tikitown", "drazion", "world-essentials", "ladder"])
    return {
        "schemaVersion": 1,
        "category": CATEGORY,
        "source": ("TikiTown tterika sewer ladder (Drazion's Tilepack) on our own copies of the tiles "
                   "(KBWTikiTownLadders_0/1: ladder flags instead of sheet-rope flags; pack tiles unchanged). "
                   "Cost: WE Sewer Ladders (%s). Generated by pz_craft_loops/ladders.py." % src),
        "buildables": [_guard(b)],
    }


# ---- 2. vanilla ladders for the Community submod ----------------------------------------------
GROUP = {"id": "kbwcb.stairs.ladders", "translationKey": "IGUI_KBWCB_Group_Ladders", "name": "Ladders"}
VANILLA = [  # (stem, name, faces, metal?)
    ("wood", "Wooden Ladder",
     {"W": "carpentry_02_84", "N": "carpentry_02_85", "E": "carpentry_02_86", "S": "carpentry_02_87"}, False),
    ("rusted_metal", "Rusted Metal Ladder",
     {"W": "industry_railroad_05_20", "N": "industry_railroad_05_21",
      "E": "industry_railroad_05_56", "S": "industry_railroad_05_57"}, True),
    ("steel", "Steel Ladder",
     {"W": "industry_railroad_05_36", "N": "industry_railroad_05_37",
      "E": "industry_railroad_05_58", "S": "industry_railroad_05_59"}, True),
]


def _dirkies_entries():
    """Dirkies decor-house ladder + ladder top (user, 2026-08-28), on our copies in the ice-shell
    tileset (kbw_tilepatch.DECOR_*). The 4 'full height' tiles 16-19 are ONE ladder in its 4
    wall orientations (W/N on the far walls, S/E on the near walls)."""
    from kbw_tilepatch import DECOR_LADDERS, DECOR_TOPS, decor_copy_name, decor_edge
    lad = {decor_edge(s): decor_copy_name(s) for s in DECOR_LADDERS}
    top = {decor_edge(s): decor_copy_name(s) for s in DECOR_TOPS}
    return [("iron", "Iron Ladder", lad, True), ("iron_top", "Iron Ladder Top", top, None)]


LADDER_TOP_TIP = "Decorative ladder top for the open square above a ladder. Not climbable; you can walk through it."
# Caged crane ladder (Dirkies edit_ddd_RUS_industry_crane_01 72-77, kbw_tilepatch.CRANE_*): own card.
# Bottom and middle are climbable (stack middles for more floors); the top ring is decoration.
CAGED_GROUP = {"id": "kbwcb.stairs.caged_ladder", "translationKey": "IGUI_KBWCB_Group_CagedLadder",
               "name": "Caged Ladder"}
# ladder top: decoration for the open square above a ladder. Not climbable, walk-through.
TOP_OBJECT = {"isThumpable": False, "dismantable": True, "blockAllSquare": False, "canPassThrough": True}
_TOP_COST = {
    "requirements": {
        "inputs": [
            {"id": "tool_welding_mask", "role": "tool", "mode": "keep", "resourceType": "Item",
             "tags": ["base:weldingmask"], "amount": 1},
            {"id": "source_material_1", "role": "material", "mode": "consume", "resourceType": "Item",
             "items": ["Base.MetalBar"], "amount": 1},
            {"id": "source_material_2", "role": "consumable", "mode": "drain", "resourceType": "Item",
             "items": ["Base.WeldingRods"], "amount": 1, "uses": 2},
            {"id": "source_material_3", "role": "consumable", "mode": "drain", "resourceType": "Item",
             "items": ["Base.BlowTorch"], "amount": 1, "uses": 2}],
        "skills": {"MetalWelding": 2}},
    "construction": {"time": 100, "timedAction": "BuildLowMetal", "completionSound": "BuildMetalStructureMedium",
                     "xp": {"MetalWelding": 15}, "category": "Metalworking"},
}


def build_vanilla_ladder_defs():
    """(buildables, tooltips {key: text}, report) for the Community submod / test bundle:
    the vanilla ladders + the Dirkies iron ladder and its decorative top, one "Ladders" card."""
    from name_tooltip_pass import tooltip_for
    req, con, src = metal_cost()
    out, tips, report = [], {}, ["ladders: metal cost from %s (%s)" % (WE_LADDER_ID, src)]
    for level, (stem, name, faces, metal) in enumerate(VANILLA + _dirkies_entries(), 1):
        if metal is None:          # decorative ladder top
            bid = "kbwcb.stairs.ladder." + stem
            b = _buildable(bid, "IGUI_" + bid.replace(".", "_"), name, faces,
                           (_TOP_COST["requirements"], _TOP_COST["construction"]), "Metal",
                           ["community-tilepack", "dirkies", "ladder", "decoration"])
            b["stages"][0]["object"] = dict(TOP_OBJECT)
            b["group"] = dict(GROUP, level=level)
            b["tooltipKey"], tips["Tooltip_KBWCB_LadderTop"] = "Tooltip_KBWCB_LadderTop", LADDER_TOP_TIP
            out.append(_guard(b, top=True))
            report.append("%-32s %-20s level %d %s" % (bid, name, level, sorted(faces.values())))
            continue
        bid = "kbwcb.stairs.ladder." + stem
        cost = (req, con) if metal else (_WOOD["requirements"], _WOOD["construction"])
        b = _buildable(bid, "IGUI_" + bid.replace(".", "_"), name, faces, cost, "Metal" if metal else "Wood",
                       ["community-tilepack", "dirkies" if stem.startswith("iron") else "vanilla-sprites", "ladder"])
        b["group"] = dict(GROUP, level=level)
        key, text = tooltip_for(b)
        b["tooltipKey"] = key
        if text is not None:
            tips[key] = text
        out.append(_guard(b))
        report.append("%-32s %-20s level %d %s" % (bid, name, level, sorted(faces.values())))
    # caged crane ladder: own card, bottom / middle / top (W and N walls only)
    from kbw_tilepatch import CRANE_SHEET, CRANE_BOTTOM, CRANE_MIDDLE, CRANE_TOP, decor_copy_name, decor_edge
    faces_of = lambda srcs: {decor_edge(s, CRANE_SHEET): decor_copy_name(s, CRANE_SHEET) for s in srcs}
    for level, (stem, name, srcs, is_top) in enumerate([
            ("bottom", "Caged Ladder (Bottom)", CRANE_BOTTOM, False),
            ("middle", "Caged Ladder (Middle)", CRANE_MIDDLE, False),
            ("top", "Caged Ladder Top", CRANE_TOP, True)], 1):
        bid = "kbwcb.stairs.caged_ladder." + stem
        cost = (_TOP_COST["requirements"], _TOP_COST["construction"]) if is_top else (req, con)
        b = _buildable(bid, "IGUI_" + bid.replace(".", "_"), name, faces_of(srcs), cost, "Metal",
                       ["community-tilepack", "dirkies", "ladder"] + (["decoration"] if is_top else []))
        b["group"] = dict(CAGED_GROUP, level=level)
        if is_top:
            b["stages"][0]["object"] = dict(TOP_OBJECT)
            b["tooltipKey"] = "Tooltip_KBWCB_LadderTop"
        else:
            key, text = tooltip_for(b)
            b["tooltipKey"] = key
            if text is not None:
                tips[key] = text
        out.append(_guard(b, top=is_top))
        report.append("%-32s %-20s level %d %s" % (bid, name, level, sorted(b["stages"][0]["geometry"]["faces"])))
    tips.setdefault("Tooltip_KBWCB_LadderTop", LADDER_TOP_TIP)
    return out, tips, report


def main():
    doc = build_tikitown_doc()
    json.dump(doc, open(OUT_TT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("wrote %s (%d buildables)" % (OUT_TT, len(doc["buildables"])))


if __name__ == "__main__":
    main()
