# -*- coding: utf-8 -*-
"""Building Menu addon conversions, batch 2 (user, 2026-08-28: "garden, architecture plus, dirkies
floors, ak tufrniture, and the small leftovers"). Rows from ADDON_SPRITE_MAP.csv (map_buildmenu_addons.py).

  74_community_dirkies_architecture.json  Dirkies (Community pack, diederiks_tile_palooza)
      walls_trim_ddd_02  ArchitecturePlus foundation trim: plain + capped brick, 6 pieces each
                         (edge, edge end, sloped edge, short sloped edge, outer corner, corner post),
                         and 2 brick columns.
      misc_ddd_01        5 painted diamond-plate metal floors (W / N).
      shanty_ddd_01      concrete floors (edge, corner edge: 4 facings; jointed: W / N; 2 plain) and
                         a plank floor (W / N).
      edit_ddd_RUS_furniture_storage_03 88-91  hall tree bench (addon "Fancy Dark Wardrobe"), container.
      industry_ddd_01_9  wooden crate, container.
  75_community_tk_outdoor.json  TK (Community pack, tkTiles_01)
      seating_outdoor_tk_01  hammock, couch (2 tiles), lawn chair, shell chair, lawn lounger (2 tiles).
      walls_garage_tk_01     garage door 3 and 4 wide.

Faces: Building Menu's sprite / northSprite / eastSprite / southSprite = KBW W / N / E / S, the pack's
Facing is the opposite direction (as in simonmd_doors_furniture.py). The addon splits each 2-tile piece
into two entries with inconsistent facing pairs (the TK couch pairs W with S), so 2-tile faces are laid
out from the tiles' own Facing + SpriteGridPos instead (row = y, column = x).

Costs:
  * containers: the transpiler's KBW type template (transpile_buildmenu.make_buildable) + "reinforce".
  * floors: WE's own floor setup for the material (Industrial metal / Wooden), concrete = WE's masonry
    floor without the stone blocks. The addon's TwoSpriteFloorRecipe (2 planks) does not fit metal or
    concrete.
  * foundation trim / columns: the addon's ConcreteFloorRecipe (trowel + 1 use of concrete) as masonry.
  * chairs / hammock / lounger: KBW's own material groups (beach chair, metal chair); the addon's metal
    chair recipe (4 bars, 3 sheet metal, 15 sheets, 20 screws) is far above KBW's for a lawn chair.
  * couch: the Dirkies couch cost (dirkies_couches.py), like the other Community couches.
  * garage doors: the addon's GarageDoorRecipe at default sandbox values (simonmd RECIPES["GarageDoor"]).
NOT built here: Dylan garden stuff, lockers and fridge (their sprites are not in WE's WECommunity_Dylan
copies, see we_dylan.py), Dirkies d_doors_01_56 (removed on purpose: rename_dirkies_doors.py).
NOT yet tested in game.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kbw_tilepatch as k                      # noqa: E402
import transpile_buildmenu as tb               # noqa: E402
from simonmd_doors_furniture import RECIPES as SIMON_RECIPES, _construction as simon_construction  # noqa: E402
from dirkies_couches import _wood_recipe, _construction as couch_construction  # noqa: E402

DELIV = r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables"
OUT_DIRKIES = os.path.join(DELIV, "74_community_dirkies_architecture.json")
OUT_TK = os.path.join(DELIV, "75_community_tk_outdoor.json")
KNOWN_ACTIONS = {"BuildWallHammer", "BuildWallMetal", "BuildWallNoTool", "BuildWoodenStructureMedium",
                 "BuildWoodenStructureSmall", "BuildMetalStructureMedium", "BuildLowMetal", "BuildLowNoTool",
                 "BuildLowHammer"}
OPP = {"E": "W", "S": "N", "W": "E", "N": "S"}   # pack Facing -> KBW face


def _s(sheet, i):
    return "%s_%d" % (sheet, i)


def _one(sprite):
    return {"layers": [{"rows": [[sprite]]}]}


def _tkey(bid):
    return "IGUI_" + bid.replace(".", "_")


def _props(ts, sheet, i):
    return {a.decode(): b.decode() for a, b in ts[sheet.encode()][6][i]}


def _tool(i, tags, flags=None):
    d = {"id": i, "role": "tool", "mode": "keep", "resourceType": "Item", "tags": tags, "amount": 1}
    if flags:
        d["flags"] = flags
    return d


def _mat(i, items, n):
    return {"id": i, "role": "material", "mode": "consume", "resourceType": "Item", "items": items, "amount": n}


TROWEL = _tool("tool_masons_trowel", ["base:masonstrowel"], ["Prop1", "MayDegradeLight"])


def _mortar(uses):
    return {"id": "mortar", "role": "consumable", "mode": "drain", "resourceType": "Item",
            "tags": ["base:concrete"], "amount": 1, "uses": uses}


def _masonry(uses, level, time, xp):
    req = {"inputs": [dict(TROWEL), _mortar(uses)], "skills": {"Masonry": level}}
    con = {"time": time, "timedAction": "BuildLowNoTool", "completionSound": "DropSoilFromGravelBag",
           "xp": {"Masonry": xp}, "category": "Masonry"}
    return req, con


def _grid_faces(ts, sheet, idxs):
    """KBW faces for a multi-tile piece from the tiles' Facing + SpriteGridPos."""
    by = {}
    for i in idxs:
        p = _props(ts, sheet, i)
        x, y = (int(v) for v in p["SpriteGridPos"].split(","))
        by.setdefault(OPP[p["Facing"]], {})[(x, y)] = _s(sheet, i)
    faces = {}
    for face, cells in by.items():
        w = max(x for x, _y in cells) + 1
        h = max(y for _x, y in cells) + 1
        assert len(cells) == w * h, (sheet, face, cells)
        faces[face] = {"layers": [{"rows": [[cells[(x, y)] for x in range(w)] for y in range(h)]}]}
    assert set(faces) == {"W", "N", "E", "S"}, (sheet, idxs, sorted(faces))
    return faces


def _single_faces(ts, sheet, idxs):
    """KBW faces for a single-tile piece from the tiles' Facing."""
    faces = {}
    for i in idxs:
        p = _props(ts, sheet, i)
        assert "SpriteGridPos" not in p, (sheet, i)
        faces[OPP[p["Facing"]]] = _one(_s(sheet, i))
    assert len(faces) == len(idxs), (sheet, idxs)
    return faces


def _piece(bid, name, cat, sub, material, icon, placement, faces, req, con, obj, tags, group=None, level=None):
    b = {
        "id": bid, "allowSpriteReuse": True, "translationKey": _tkey(bid), "displayName": name,
        "category": cat, "subcategory": sub, "material": material, "materialTags": [material],
        "iconSprite": icon, "placement": placement, "tags": tags,
        "stages": [{"id": "built", "geometry": {"faces": faces}, "requirements": req, "construction": con,
                    "object": obj}],
    }
    if group:
        b["group"] = {"id": group[0], "name": group[1], "translationKey": _tkey(group[0]) + "_group",
                      "level": level}
    return b


# ---- Dirkies ---------------------------------------------------------------------------------
TRIM = "walls_trim_ddd_02"
# (slug, name, W, N): N = None for one-sprite pieces. Plain brick = 0-9, capped = +16.
TRIM_PIECES = [
    ("edge", "Edge", 0, 1),
    ("edge_end", "Edge End", 4, 5),
    ("sloped_edge", "Sloped Edge", 6, 7),
    ("short_sloped_edge", "Short Sloped Edge", 8, 9),
    ("outer_corner", "Outer Corner", 2, None),
    ("corner_post", "Corner Post", 3, None),
]
TRIM_STYLES = [("brick", "Brick Foundation", 0), ("capped", "Capped Brick Foundation", 16)]
COLUMNS = [("brick", "Brick Column", 14, 15), ("light_brick", "Light Brick Column", 30, 31)]
TRIM_OBJECT = {"isThumpable": True, "canPassThrough": True, "blockAllSquare": False, "isCorner": True,
               "dismantable": True}

FLOOR_METAL = "misc_ddd_01"      # diamond-plate metal planks, W = odd, N = even (addon sprite / northSprite)
METAL_FLOORS = [("gray", "Gray", 17, 16), ("blue", "Blue", 19, 18), ("orange", "Orange", 21, 20),
                ("red", "Red", 23, 22), ("white", "White", 25, 24)]
SHANTY = "shanty_ddd_01"
# (slug, name, kind, {face: index})  faces = addon sprite / northSprite / eastSprite / southSprite
SHANTY_FLOORS = [
    ("concrete_edge", "Concrete Floor (Edge)", "concrete", {"W": 3, "N": 2, "E": 1, "S": 0}),
    ("concrete_corner", "Concrete Floor (Corner Edge)", "concrete", {"W": 7, "N": 6, "E": 5, "S": 4}),
    ("concrete_jointed", "Jointed Concrete Floor", "concrete", {"W": 11, "N": 10}),
    ("concrete_plain", "Plain Concrete Floor", "concrete", {"W": 12}),
    ("concrete_plain_alt", "Plain Concrete Floor (Alt)", "concrete", {"W": 13}),
    ("planks", "Weathered Plank Floor", "wood", {"W": 9, "N": 8}),
]


def _hammer():
    return _tool("tool_hammer", ["base:hammer"], ["Prop1", "MayDegradeVeryLight"])


def _floor_cost(kind):
    if kind == "metal":   # WE's Industrial floors (industry_containers_tterika_01_11)
        req = {"inputs": [_tool("tool_welding_mask", ["base:weldingmask"]),
                          _mat("sheet_metal", ["Base.SmallSheetMetal"], 1),
                          {"id": "torch_fuel", "role": "consumable", "mode": "drain", "resourceType": "Item",
                           "items": ["Base.BlowTorch"], "amount": 1, "uses": 1},
                          {"id": "welding_rods", "role": "consumable", "mode": "drain", "resourceType": "Item",
                           "items": ["Base.WeldingRods"], "amount": 1, "uses": 1}],
               "skills": {"MetalWelding": 2}}
        con = {"time": 200, "timedAction": "BuildLowMetal", "completionSound": "BuildMetalStructureMedium",
               "xp": {"MetalWelding": 20}, "category": "Welding"}
        return "Metal", "Industrial", req, con
    if kind == "wood":    # WE's Wooden floors (floors_interior_tilesandwood_tterika_01_43)
        req = {"inputs": [_hammer(), _mat("lumber", ["Base.Plank"], 1), _mat("fasteners_nails", ["Base.Nails"], 1)],
               "skills": {"Woodwork": 2}}
        con = {"time": 200, "timedAction": "BuildLowHammer", "completionSound": "BuildWoodenStructureSmall",
               "xp": {"Woodwork": 20}, "category": "Carpentry"}
        return "Wood", "Wooden", req, con
    req, con = _masonry(1, 1, 200, 10)   # WE's masonry floor (location_sewer_tterika_01_25) minus the stone
    return "Stone", "Concrete", req, con


def _floor(bid, name, kind, faces, group, level, tags):
    material, sub, req, con = _floor_cost(kind)
    return _piece(bid, name, "Floors", sub, material, faces["W"]["layers"][0]["rows"][0][0],
                  {"kind": "floor"}, faces, req, con, None, tags, group, level)


def _addon_container(pack, cb, recipe, geom, options, name, subcat):
    """A container through the transpiler's make_buildable (same template as 40-42), tagged reinforce."""
    obj = {"cb": cb, "recipe": recipe, "geom": geom, "subst": None, "options": options, "name": name}
    b, err = tb.make_buildable(pack, obj, subcat)
    assert err is None, (geom, err)
    b["tags"].append("reinforce")
    return b


def dirkies(ts):
    out = []
    tags = ["community-tilepack", "dirkies", "architecture"]
    req, con = _masonry(1, 1, 120, 5)
    for style, sname, base in TRIM_STYLES:
        group = ("community.dirkies.architecture.foundation_%s" % style, "%s Trim" % sname)
        for level, (slug, pname, w, n) in enumerate(TRIM_PIECES, 1):
            faces = {"W": _one(_s(TRIM, base + w))}
            if n is not None:
                faces["N"] = _one(_s(TRIM, base + n))
            bid = "community.dirkies.architecture.foundation_%s_%s" % (style, slug)
            out.append(_piece(bid, "%s %s" % (sname, pname), "Wall Trim", "Foundation Trim", "Stone",
                              _s(TRIM, base + w), {"kind": "object", "requiresFloor": False}, faces,
                              json.loads(json.dumps(req)), dict(con), dict(TRIM_OBJECT), list(tags), group, level))
    # brick columns: the pack tiles carry no wall / Facing flags, so KBW's against-wall check could never
    # find the wall; built as free-standing objects (the art already sits on the square's wall edge)
    creq, ccon = _masonry(2, 2, 200, 10)
    cgroup = ("community.dirkies.architecture.columns", "Brick Columns")
    for level, (slug, name, w, n) in enumerate(COLUMNS, 1):
        bid = "community.dirkies.architecture.column_%s" % slug
        out.append(_piece(bid, name, "Wall Trim", "Columns", "Stone", _s(TRIM, w),
                          {"kind": "object", "requiresFloor": False},
                          {"W": _one(_s(TRIM, w)), "N": _one(_s(TRIM, n))},
                          json.loads(json.dumps(creq)), dict(ccon),
                          {"isThumpable": True, "canPassThrough": False, "blockAllSquare": False,
                           "dismantable": True}, list(tags), cgroup, level))
    # floors
    ftags = ["community-tilepack", "dirkies", "floor"]
    mgroup = ("community.dirkies.floors.diamond_plate", "Painted Diamond Plate Floor")
    for level, (slug, cname, w, n) in enumerate(METAL_FLOORS, 1):
        for i in (w, n):
            assert "solidfloor" in _props(ts, FLOOR_METAL, i), i
        out.append(_floor("community.dirkies.floors.diamond_plate_%s" % slug, "%s Diamond Plate Floor" % cname,
                          "metal", {"W": _one(_s(FLOOR_METAL, w)), "N": _one(_s(FLOOR_METAL, n))},
                          mgroup, level, list(ftags)))
    cgroup = ("community.dirkies.floors.concrete", "Shanty Concrete Floor")
    clevel = 0
    for slug, name, kind, fi in SHANTY_FLOORS:
        for i in fi.values():
            assert "solidfloor" in _props(ts, SHANTY, i), i
        faces = {f: _one(_s(SHANTY, i)) for f, i in fi.items()}
        if kind == "concrete":
            clevel += 1
            out.append(_floor("community.dirkies.floors.shanty_%s" % slug, name, kind, faces, cgroup, clevel,
                              list(ftags)))
        else:
            out.append(_floor("community.dirkies.floors.shanty_%s" % slug, name, kind, faces, None, None,
                              list(ftags)))
    # containers. Hall tree: the addon's SmallFurnitureRecipe has no transpiler type; the Dressers
    # subcategory picks the dresser template anyway, so it goes in as LargeFurnitureRecipe.
    out.append(_addon_container(
        "Dirkies", "onBuildWoodenContainer", "LargeFurnitureRecipe",
        '{ sprite = "edit_ddd_RUS_furniture_storage_03_89", northSprite = "edit_ddd_RUS_furniture_storage_03_88", '
        'eastSprite = "edit_ddd_RUS_furniture_storage_03_91", southSprite = "edit_ddd_RUS_furniture_storage_03_90" }',
        "", "Dark Hall Tree Bench", "Dressers"))
    out.append(_addon_container(
        "Dirkies", "onBuildWoodenContainer", "CounterRecipe", '{ sprite = "industry_ddd_01_9" }',
        "canBeLockedByPadlock = true", "Wooden Crate", "Crates"))
    return out


# ---- TK --------------------------------------------------------------------------------------
SEAT = "seating_outdoor_tk_01"
GARAGE = "walls_garage_tk_01"
GARAGE_W = (2, 1, 0)   # GarageDoor part 3, 2, 1 (W rows, north -> south), WallW / doorW
GARAGE_N = (3, 4, 5)   # GarageDoor part 1, 2, 3 (N row), WallN / doorN
CHAIR_KNOWLEDGE = {"recipes": ["KBWKnowledge_FineWoodWorking_Furniture_ChairsBenches"], "hideUntilLearned": True,
                   "needToBeLearned": True,
                   "sources": [{"type": "magazine", "item": "KnoxBuildworks.FineWoodWorking_Furniture_ChairsBenches"}]}


def _group_req(group, skills, alt):
    kn = json.loads(json.dumps(CHAIR_KNOWLEDGE))
    kn["skillAlternatives"] = [{"mode": "all", "skills": alt}]
    return {"materials": group, "skills": skills, "knowledge": kn}


# KBW's beach-chair / metal-chair construction (chairs.json templates); BuildMetalStructureSmall is not in
# KNOWN_ACTIONS, so the metal chair uses BuildMetalStructureMedium
BEACH = ("kbwve.tiles.furniture_chairs.beach_chair", {"Woodwork": 2, "Tailoring": 1}, {"Woodwork": 5, "Tailoring": 4},
         {"time": 250, "timedAction": "BuildWoodenStructureSmall", "completionSound": "BuildWoodenStructureSmall",
          "category": "Carpentry", "xp": {"Woodwork": 5, "Tailoring": 5}}, "Wood")
METALCHAIR = ("kbwve.tiles.furniture_chairs.chair_metal", {"MetalWelding": 2}, {"MetalWelding": 5},
              {"time": 250, "timedAction": "BuildMetalStructureMedium", "completionSound": "BuildMetalStructureMedium",
               "category": "Welding", "xp": {"MetalWelding": 5}}, "Metal")
SEAT_OBJECT = {"isThumpable": True, "dismantable": True, "canPassThrough": True, "isCorner": True}
# (slug, name, tiles, two-tile, cost)
SEATS = [
    ("hammock", "Striped Hammock", range(0, 8), True, BEACH),
    ("couch_old_alley", "Old Alley Couch", range(8, 16), True, "couch"),
    ("lawn_chair", "Lawn Chair", range(16, 20), False, BEACH),
    ("shell_chair", "Shell Lawn Chair", range(20, 24), False, METALCHAIR),
    ("lawn_lounger", "Lawn Lounger", range(24, 32), True, BEACH),
]


def tk(ts):
    out = []
    tags = ["community-tilepack", "tk", "seating"]
    for slug, name, idxs, two, cost in SEATS:
        faces = _grid_faces(ts, SEAT, idxs) if two else _single_faces(ts, SEAT, idxs)
        if cost == "couch":
            req, con, material = _wood_recipe(6, 6, 4), couch_construction(xp=45, time=220), "Wood"
        else:
            group, skills, alt, con, material = cost
            req, con = _group_req(group, skills, alt), dict(con)
        bid = "community.tk.seating.%s" % slug
        out.append(_piece(bid, name, "Furniture and Appliances", "Outdoor Seating", material,
                          faces["W"]["layers"][0]["rows"][0][0], {"kind": "object", "requiresFloor": True},
                          faces, req, con, dict(SEAT_OBJECT), list(tags)))
    for i in GARAGE_W:
        p = _props(ts, GARAGE, i)
        assert "doorW" in p and p.get("GarageDoor"), i
    for i in GARAGE_N:
        p = _props(ts, GARAGE, i)
        assert "doorN" in p and p.get("GarageDoor"), i
    (w3, w2, w1), (n1, n2, n3) = GARAGE_W, GARAGE_N
    group = ("community.tk.garages.plank", "Plank Garage Door")
    for level, width in enumerate((3, 4), 1):
        wrows = [w3] + [w2] * (width - 2) + [w1]
        nrow = [n1] + [n2] * (width - 2) + [n3]
        bid = "community.tk.garages.plank_w%d" % width
        faces = {"W": {"layers": [{"y": -(width - 1), "rows": [[_s(GARAGE, i)] for i in wrows]}]},
                 "N": {"layers": [{"rows": [[_s(GARAGE, i) for i in nrow]]}]}}
        out.append(_piece(bid, "Plank Garage Door (%d Wide)" % width, "Doors", "Garage Doors", "Metal",
                          _s(GARAGE, w2), {"kind": "object", "dontNeedFrame": True}, faces,
                          json.loads(json.dumps(SIMON_RECIPES["GarageDoor"])), simon_construction("GarageDoor", 200),
                          {"isThumpable": True, "dismantable": True},
                          ["community-tilepack", "tk", "garage-door"], group, level))
    return out


def _check(builds):
    ids = [b["id"] for b in builds]
    dups = sorted({i for i in ids if ids.count(i) > 1})
    assert not dups, dups
    for b in builds:
        assert b["translationKey"] == _tkey(b["id"]), b["id"]
        for st in b["stages"]:
            ta = (st.get("construction") or b.get("construction") or {}).get("timedAction")
            assert ta in KNOWN_ACTIONS, (b["id"], ta)
            if st.get("object") is None:
                st.pop("object")
        if b["category"] == "Containers":
            assert "reinforce" in b["tags"], b["id"]


def main():
    _v, ts = k._load_community_tilesets()
    docs = [
        (OUT_DIRKIES, "Wall Trim", dirkies(ts),
         "Dirkies walls_trim_ddd_02 foundation trim + columns, misc_ddd_01 / shanty_ddd_01 floors, hall tree "
         "bench, crate (Community pack). Generated by pz_craft_loops/community_addon_batch2.py."),
        (OUT_TK, "Furniture and Appliances", tk(ts),
         "TK seating_outdoor_tk_01 outdoor seating + walls_garage_tk_01 garage doors (Community pack). "
         "Generated by pz_craft_loops/community_addon_batch2.py."),
    ]
    for path, cat, builds, src in docs:
        _check(builds)
        json.dump({"schemaVersion": 1, "category": cat, "source": src, "buildables": builds},
                  open(path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        print("wrote %s (%d buildables)" % (path, len(builds)))


if __name__ == "__main__":
    main()
