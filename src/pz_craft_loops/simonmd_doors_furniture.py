# -*- coding: utf-8 -*-
"""Generate Simon MD doors + furniture (user, 2026-11-16) for "World Essentials - Raven Creek Buildworks"
(build_simonmd_mod.py; gated on RavenCreek_B42):
  zomboid/simonmd/02_simonmd_doors.json      2 scrap doors, secret entrance, shipping-container doors 3 / 4 wide
  zomboid/simonmd/03_simonmd_furniture.json  military locker, glass display counter, glass display cabinet,
                                             wall gun rack (2 tiles); all containers -> "reinforce" tag

Pieces, sprites and costs come from the B41 Building Menu Simon MD addon (3137092790,
BuildingMenu_SimonTiles.lua): addDoorsToMenu, addSimonMDSecretEntrancesToMenu, addGarageDoorsToMenu,
addMetalContainersToMenu. Recipes are Building Menu's (BuildingMenu02_Recipes.lua) at its default
sandbox values (the file's own fallbacks: smallObjectsWoodCount 4, smallObjectsNailsCount 6,
glassPaneCount 2, metalBarsCount 4, screwsCount 10, sheetMetalCountForDoors 4,
sheetMetalCountForContainers 4, smallObjectsCarpentrySkill 4; BuildingMenu.round = half up;
weldingRodUses(n) = floor((n + 0.1) / 2)). Glass pane: B42's Base.GlassPanel.
Faces: Building Menu's sprite / northSprite / eastSprite / southSprite = KBW W / N / E / S (the pack's
Facing is the opposite direction, as for every KBW face). Exception: the gun rack, whose addon entry
names the attachedN tiles "sprite"; it is laid out from the tiles' own attachedW / attachedN flags and
SpriteGridPos instead. Garage tiles use the same GarageDoor part numbers as TikiTown's garages, so the
layout copies 29_tikitown_garages.json (W rows south part 1 at the bottom, N row 1-2-3).
NOT built: the Scrap Double Door Gate (fixtures_doors_fences_Simon_MD, not in Raven Creek's copy) and
the corrugated roof pieces on the furniture sheet (78 / 79 / 86 / 87: roofing).
Copies in the submod's own tileset KBWRavenCreek (tiledef 8174; see COPIES): the gun rack without
`solid`, the secret cabinet and glass display counter with depth, and the fill overlays for the rack and
counter (Raven Creek ships the overlay art but registers none). Map copies of the pack tiles are untouched.
The four base containers keep the addon's recipes (counter_variants.HALVE_EXCLUDE, user 2026-11-16).
NOT yet tested in game.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kbw_tilepatch as k   # noqa: E402

OUT_DIR = r"c:\Users\josep\Kiro\zomboid\simonmd"
OUT_DOORS = os.path.join(OUT_DIR, "02_simonmd_doors.json")
OUT_FURN = os.path.join(OUT_DIR, "03_simonmd_furniture.json")
RC_TILES = (r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600\3821823518\mods"
            r"\RavenCreek_B42\common\media\LCB42_SimonMDsTiles.tiles")
DOOR_SHEET, FURN_SHEET, FURN2_SHEET = "fixtures_doors_Simon_MD", "furniture_Simon_MD", "furniture_02_Simon_MD"
PREFIX = "worldessentials.simonmd."


def _tool(i, tags, flags=None):
    d = {"id": i, "role": "tool", "mode": "keep", "resourceType": "Item", "tags": tags, "amount": 1}
    if flags:
        d["flags"] = flags
    return d


def _mat(i, items, n):
    return {"id": i, "role": "material", "mode": "consume", "resourceType": "Item", "items": items, "amount": n}


def _drain(i, item, uses):
    return {"id": i, "role": "consumable", "mode": "drain", "resourceType": "Item", "items": [item], "uses": uses}


def _rods(torch):
    return int((torch + 0.1) / 2)


MASK = _tool("welding_mask", ["base:weldingmask"])
HAMMER = _tool("tool_hammer", ["base:hammer"], ["Prop1", "MayDegradeVeryLight"])
SCREWDRIVER = _tool("tool_screwdriver", ["base:screwdriver"], ["Prop1", "MayDegradeVeryLight"])
BARS = ["Base.MetalBar", "Base.MetalPipe"]


def _recipe(tools, mats, torch, skills):
    return {"inputs": tools + mats + [_drain("torch_fuel", "Base.BlowTorch", torch),
                                      _drain("welding_rods", "Base.WeldingRods", _rods(torch))],
            "skills": skills}


# Building Menu recipes at default sandbox values (see module docstring)
RECIPES = {
    "ScrapDoor1": _recipe([MASK, HAMMER], [
        _mat("planks", ["Base.Plank"], 3), _mat("sheet_metal", ["Base.SheetMetal"], 3),
        _mat("metal_bars", BARS, 2), _mat("nails", ["Base.Nails"], 5), _mat("screws", ["Base.Screws"], 5),
        _mat("door_hinges", ["Base.Hinge"], 2), _mat("door_hardware", ["Base.Doorknob"], 1)], 5,
        {"Woodwork": 4, "MetalWelding": 2}),
    "ScrapDoor2": _recipe([MASK, HAMMER], [
        _mat("planks", ["Base.Plank"], 4), _mat("sheet_metal", ["Base.SheetMetal"], 5),
        _mat("metal_bars", BARS, 4), _mat("nails", ["Base.Nails"], 5), _mat("screws", ["Base.Screws"], 5),
        _mat("door_hinges", ["Base.Hinge"], 2), _mat("door_hardware", ["Base.Doorknob"], 1)], 5,
        {"Woodwork": 4, "MetalWelding": 4}),
    "MetalDoor": _recipe([MASK], [
        _mat("sheet_metal", ["Base.SheetMetal"], 4), _mat("metal_bars", BARS, 3), _mat("screws", ["Base.Screws"], 8),
        _mat("door_hinges", ["Base.Hinge"], 2), _mat("door_hardware", ["Base.Doorknob"], 1)], 5,
        {"MetalWelding": 4}),
    "GarageDoor": _recipe([MASK], [
        _mat("sheet_metal", ["Base.SheetMetal"], 8), _mat("metal_bars", BARS, 4), _mat("screws", ["Base.Screws"], 20),
        _mat("door_hinges", ["Base.Hinge"], 4), _mat("door_hardware", ["Base.Doorknob"], 1)], 10,
        {"MetalWelding": 6}),
    "MetalLocker": _recipe([MASK, SCREWDRIVER], [
        _mat("sheet_metal", ["Base.SheetMetal"], 4), _mat("small_sheet_metal", ["Base.SmallSheetMetal"], 2),
        _mat("screws", ["Base.Screws"], 5), _mat("hinges", ["Base.Hinge"], 2)], 5,
        {"MetalWelding": 5}),
    "MetalGlassCounter": _recipe([MASK, SCREWDRIVER], [
        _mat("glass", ["Base.GlassPanel"], 4), _mat("metal_bars", BARS, 4), _mat("screws", ["Base.Screws"], 10)], 5,
        {"MetalWelding": 4}),
    "MetalCounterSmall": _recipe([MASK, SCREWDRIVER], [
        _mat("sheet_metal", ["Base.SheetMetal"], 3), _mat("small_sheet_metal", ["Base.SmallSheetMetal"], 3),
        _mat("screws", ["Base.Screws"], 5)], 3,
        {"MetalWelding": 2}),
}
# Building Menu's xp: level x 3.5 (MetalWelding) / x 2.5 (Woodwork), rounded half up
XP = {"ScrapDoor1": {"MetalWelding": 7, "Woodwork": 10}, "ScrapDoor2": {"MetalWelding": 14, "Woodwork": 10},
      "MetalDoor": {"MetalWelding": 14}, "GarageDoor": {"MetalWelding": 21}, "MetalLocker": {"MetalWelding": 18},
      "MetalGlassCounter": {"MetalWelding": 14}, "MetalCounterSmall": {"MetalWelding": 7}}


def _construction(recipe, time):
    return {"time": time, "timedAction": "BuildWallMetal" if recipe in ("ScrapDoor1", "ScrapDoor2", "MetalDoor", "GarageDoor")
            else "BuildMetalStructureMedium", "completionSound": "BuildMetalStructureMedium",
            "xp": XP[recipe], "category": "Welding"}


def _s(sheet, i):
    return "%s_%d" % (sheet, i)


def _one(sprite):
    return {"layers": [{"rows": [[sprite]]}]}


def _props(ts, sheet, i):
    t = ts[sheet.encode()][6]
    return {a.decode(): b.decode() for a, b in t[i]}


# ---- doors -----------------------------------------------------------------------------------
# (slug, name, recipe, W closed, N closed, W open, N open) = addon sprite / northSprite / openSprite / openNorthSprite
HINGED = [
    ("door_scrap_1", "Half-Metal Plank Door", "ScrapDoor1", 20, 21, 22, 23),
    ("door_scrap_2", "Reinforced Metal-Plank Door", "ScrapDoor2", 24, 25, 26, 27),
    ("door_secret_cabinet", "Secret Entrance (Metal Cabinet)", "MetalDoor", 28, 29, 30, 31),
]
GARAGE = {"W": (74, 73, 72), "N": (75, 76, 77)}   # GarageDoor part 3, 2, 1 (W: north -> south) / 1, 2, 3


def doors(ts):
    out = []
    for slug, name, recipe, w, n, wo, no in HINGED:
        for i in (w, wo):
            assert "doorW" in _props(ts, DOOR_SHEET, i) or "doorN" in _props(ts, DOOR_SHEET, i), i
        assert "doorW" in _props(ts, DOOR_SHEET, w) and "doorN" in _props(ts, DOOR_SHEET, n), slug
        # the secret cabinet is built on our copies with a depth cell (COPIES 4-7); the others on the pack
        sp = (lambda i: copy_name(DOOR_SHEET, i)) if slug == "door_secret_cabinet" else (lambda i: _s(DOOR_SHEET, i))
        b = {
            "id": PREFIX + slug, "allowSpriteReuse": True,
            "translationKey": "IGUI_WESimon_" + slug, "displayName": name,
            "category": "Doors", "subcategory": "Metal Doors", "material": "Metal", "materialTags": ["Metal", "Wood"]
            if recipe.startswith("Scrap") else ["Metal"],
            "iconSprite": sp(w), "placement": {"kind": "wall", "requiresFloor": False},
            "tags": ["simonmd", "ravencreek", "world-essentials", "door"],
            "stages": [{"id": "built",
                        "geometry": {"faces": {"W": _one(sp(w)), "N": _one(sp(n)),
                                               "E": _one(sp(w)), "S": _one(sp(n))}},
                        "requirements": RECIPES[recipe], "construction": _construction(recipe, 200),
                        "object": {"isThumpable": True, "dismantable": True, "canBarricade": True},
                        # KBW reads callbacks from the stage only (StageConfig.sprite); at buildable
                        # level the door-frame check was ignored (fixed 2026-11-17)
                        "callbacks": {"onIsValid": "KnoxBuildworks.JsonCallbacks.DoorFrame.OnIsValid"},
                        "sprites": {"W_open": sp(wo), "N_open": sp(no), "E_open": sp(wo), "S_open": sp(no)}}],
        }
        if slug.startswith("door_scrap"):
            b["group"] = {"id": PREFIX + "scrap_doors", "name": "Scrap Doors",
                          "translationKey": "IGUI_WESimon_scrap_doors_group", "level": 1 if slug.endswith("1") else 2}
        out.append(b)
    for i in GARAGE["W"]:
        assert "doorW" in _props(ts, FURN_SHEET, i) and _props(ts, FURN_SHEET, i).get("GarageDoor"), i
    for i in GARAGE["N"]:
        assert "doorN" in _props(ts, FURN_SHEET, i) and _props(ts, FURN_SHEET, i).get("GarageDoor"), i
    (w3, w2, w1), (n1, n2, n3) = GARAGE["W"], GARAGE["N"]
    for width, level in ((3, 1), (4, 2)):
        wrows = [w3] + [w2] * (width - 2) + [w1]
        nrow = [n1] + [n2] * (width - 2) + [n3]
        out.append({
            "id": PREFIX + "garage_container_w%d" % width, "allowSpriteReuse": True,
            "translationKey": "IGUI_WESimon_garage_container_w%d" % width,
            "displayName": "Shipping Container Doors (%d Wide)" % width,
            "category": "Doors", "subcategory": "Garage Doors", "material": "Metal", "materialTags": ["Metal"],
            "iconSprite": _s(FURN_SHEET, w2), "placement": {"kind": "object", "dontNeedFrame": True},
            "tags": ["simonmd", "ravencreek", "world-essentials", "garage-door"],
            "stages": [{"id": "built",
                        "geometry": {"faces": {
                            "W": {"layers": [{"y": -(width - 1), "rows": [[_s(FURN_SHEET, i)] for i in wrows]}]},
                            "N": {"layers": [{"rows": [[_s(FURN_SHEET, i) for i in nrow]]}]}}},
                        "requirements": RECIPES["GarageDoor"], "construction": _construction("GarageDoor", 200),
                        "object": {"isThumpable": True, "dismantable": True}}],
            "group": {"id": PREFIX + "garage_container", "name": "Shipping Container Doors",
                      "translationKey": "IGUI_WESimon_garage_container_group", "level": level},
        })
    return out


# ---- furniture (containers) ------------------------------------------------------------------
def _container(ts, sheet, i):
    p = _props(ts, sheet, i)
    return {"type": p["container"], "capacity": int(p["ContainerCapacity"])}


def furniture(ts):
    out = []
    tags = ["simonmd", "ravencreek", "world-essentials", "reinforce"]

    def piece(slug, name, sub, faces, sheet, recipe, container, obj, placement=None, icon=None, extra_tags=()):
        return {
            "id": PREFIX + slug, "allowSpriteReuse": True,
            "translationKey": "IGUI_WESimon_" + slug, "displayName": name,
            "category": "Containers", "subcategory": sub, "material": "Metal",
            "materialTags": ["Metal", "Glass"] if "Glass" in recipe else ["Metal"],
            "iconSprite": icon or faces["W"]["layers"][0]["rows"][0][0],
            "placement": placement or {"kind": "object", "requiresFloor": True},
            "tags": tags + list(extra_tags),
            "stages": [{"id": "built", "geometry": {"faces": faces}, "requirements": RECIPES[recipe],
                        "construction": _construction(recipe, 150), "object": obj, "container": container}],
            # one card per piece: the base, then its "(Reinforced)" sibling (counter_variants)
            "group": {"id": PREFIX + slug, "name": name, "translationKey": "IGUI_WESimon_%s_group" % slug,
                      "level": 1},
        }

    # Military locker: addon sprite / north / east / south = 1 / 0 / 3 / 2
    # W / N on our copies (148 / 149): the fill overlays Simon registers for 0 / 1 (2026-11-17)
    out.append(piece("locker_military_green", "Green Military Locker", "Lockers",
                     {"W": _one(copy_name(FURN_SHEET, 1)), "N": _one(copy_name(FURN_SHEET, 0)),
                      "E": _one(_s(FURN_SHEET, 3)), "S": _one(_s(FURN_SHEET, 2))},
                     FURN_SHEET, "MetalLocker", _container(ts, FURN_SHEET, 1),
                     {"isThumpable": True, "canBePadlocked": True}, extra_tags=("locker",)))
    # Glass display counter (low, drawers): addon sprite / north = 5 / 4. Built on our copies, which
    # carry depth and the fill overlays (COPIES 8 / 9, OVERLAYS)
    out.append(piece("display_counter_glass", "Glass Display Counter", "Counters",
                     {"W": _one(copy_name(FURN_SHEET, 5)), "N": _one(copy_name(FURN_SHEET, 4))},
                     FURN_SHEET, "MetalGlassCounter", _container(ts, FURN_SHEET, 5), {"isThumpable": True}))
    # Tall glass display cabinet: addon sprite / north = 46 / 47 (furniture_02)
    out.append(piece("display_cabinet_glass", "Glass Display Cabinet", "Shelves",
                     # our copies 426 / 427, so the fill overlay registers without touching map cabinets
                     {"W": _one(copy_name(FURN2_SHEET, 46)), "N": _one(copy_name(FURN2_SHEET, 47))},
                     FURN2_SHEET, "MetalGlassCounter", _container(ts, FURN2_SHEET, 46), {"isThumpable": True}))
    # Wall gun rack, 2 tiles: W wall = attachedW tiles by SpriteGridPos y (north -> south), N wall =
    # attachedN tiles by SpriteGridPos x (west -> east)
    rack_w = sorted((int(_props(ts, FURN_SHEET, i)["SpriteGridPos"].split(",")[1]), i) for i in (8, 9))
    rack_n = sorted((int(_props(ts, FURN_SHEET, i)["SpriteGridPos"].split(",")[0]), i) for i in (11, 12))
    for _g, i in rack_w:
        assert "attachedW" in _props(ts, FURN_SHEET, i), i
    for _g, i in rack_n:
        assert "attachedN" in _props(ts, FURN_SHEET, i), i
    # built on our copies without `solid` (COPIES), walk-through like the Future upper cabinets
    out.append(piece("gun_rack_wall", "Military Wall Gun Rack", "Shelves",
                     {"W": {"layers": [{"rows": [[copy_name(FURN_SHEET, i)] for _g, i in rack_w]}]},
                      "N": {"layers": [{"rows": [[copy_name(FURN_SHEET, i) for _g, i in rack_n]]}]}},
                     FURN_SHEET, "MetalCounterSmall", _container(ts, FURN_SHEET, 8),
                     {"isThumpable": True, "canPassThrough": True, "blockAllSquare": False},
                     placement={"kind": "object", "requiresFloor": True, "needToBeAgainstWall": True},
                     icon=copy_name(FURN_SHEET, rack_w[0][1])))
    return out


# ---- our tile copies -------------------------------------------------------------------------
# Raven Creek's copy of the Simon MD sheets ships no depth maps and no container overlays, and its
# gun rack tiles carry `solid`. Our buildables use copies in the Raven Creek submod's own small tileset
# (tiledef 8174, free across every installed mod.info and the game, 2026-11-16). Map copies of the pack
# tiles are left exactly as the pack has them.
RC_PACK = (r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600\3821823518\mods"
           r"\RavenCreek_B42\common\media\texturepacks\LCB42_SimonMDsTiles.pack")
COPY_TILESET = "KBWRavenCreek"
COPY_PACK = "KBWRavenCreek"
COPY_TILEDEF_NAME = "kbwravencreek"
COPY_TILEDEF_ID = 8174
OVL_SHEET = "container_overlays_Simon_MD"   # art present in Raven Creek's pack, but not tiledef'd there
# fixed indices: copy index -> (source sheet, source index)
#   0-3   gun rack: no `solid` (walk-through); wall-plane depth on its wall (RACK_COPIES)
#   4-7   secret-entrance metal cabinet, closed W / N and open: matched vanilla depth (the door frame
#         drew over it, user 2026-11-16)
#   8-9   glass display counter (S / E): matched vanilla depth (base for its overlays)
#   16-27 container overlays 4-15 (counter 4-7, gun rack 8-15), as the standalone Simon MD pack
#         registers them (Simon_MD_WorldFiller.lua); each uses its base's depth cell, art holes filled
#   28-59 marble counter tops, overlays_Simon_MD 56-87 (simonmd_countertops.py, 2026-11-17): Raven Creek
#         ships the art but no tiledef for that sheet. No properties (like vanilla's counter overlays);
#         each takes the depth cell of the vanilla counter shape it sits on (CT_SHAPE_COUNTER)
COPIES = {0: (FURN_SHEET, 8), 1: (FURN_SHEET, 9), 2: (FURN_SHEET, 11), 3: (FURN_SHEET, 12),
          4: (DOOR_SHEET, 28), 5: (DOOR_SHEET, 29), 6: (DOOR_SHEET, 30), 7: (DOOR_SHEET, 31),
          8: (FURN_SHEET, 4), 9: (FURN_SHEET, 5)}
COPIES.update({16 + (n - 4): (OVL_SHEET, n) for n in range(4, 16)})
CT_SHEET = "overlays_Simon_MD"     # standalone Simon MD's counter-top sheet (TileOverlay, IsMoveAble there)
CT_FIRST_SRC, CT_FIRST_COPY = 56, 28
# (slug, name, first source tile): 8 tiles per colour (standalone SimonMDsTiles.tiles names)
CT_COLOURS = [("dark", "Dark Marble", 56), ("white", "White Marble", 64), ("gold", "Gold Marble", 72),
              ("blue", "Blue Marble", 80)]
COPIES.update({CT_FIRST_COPY + (n - CT_FIRST_SRC): (CT_SHEET, n) for n in range(56, 88)})
# shape offset within a colour -> the vanilla counter it fits (fixtures_counters_01, White set 72-79; pixel
# overlap + overlay picture, 2026-11-17). 0-3 straight, 4-7 corner.
CT_SHAPE_COUNTER = {0: 75, 1: 77, 2: 79, 3: 73, 4: 72, 5: 76, 6: 74, 7: 78}
# vanilla Facing of a counter -> shape offset (from CT_SHAPE_COUNTER and the tiles' Facing / GroupName)
CT_SHAPES = {"E": {"straight": 0, "corner": 6}, "S": {"straight": 1, "corner": 5},
             "W": {"straight": 2, "corner": 7}, "N": {"straight": 3, "corner": 4}}
_CT_STRAY_ROWS = 110      # 56 has a stray pixel at the top of its cell; every counter top starts at row ~124
# ---- batch 2 (user, 2026-11-17; simonmd_furniture2.py): copies 60-114 ----
#   60-75   low glass tables furniture_02 30-45 (2 tiles, 4 colours): copies so their fill overlays can be
#           registered without touching map copies
#   76-83   their overlays, container_overlays 36-43 (shared by the 4 colours, Simon_MD_WorldFiller.lua)
#   84-103  speakers decoration_02 8-19, 32-39: Raven Creek ships the art but no tiledef for the sheet
#   104-109 sloped-wall shelves furniture_03 10-15: same (art, no tiledef)
#   110-114 table-top figures decoration_Simon_MD 0, 32, 34, 37, 38: drawn raised (display height) with
#           IsSurfaceOffset but no Surface, so they would float; copies get the Surface their art needs
F3_SHEET, D2_SHEET, D1_SHEET = "furniture_03_Simon_MD", "decoration_02_Simon_MD", "decoration_Simon_MD"
LT_SRC, LT_COPY0 = list(range(30, 46)), 60
LT_OVL_SRC, LT_OVL_COPY0 = list(range(36, 44)), 76
SPK_SRC, SPK_COPY0 = list(range(8, 20)) + list(range(32, 40)), 84
SLOPED_SRC, SLOPED_COPY0 = list(range(10, 16)), 104
FIG_SRC, FIG_COPY0 = [0, 32, 34, 37, 38], 110
COPIES.update({LT_COPY0 + j: (FURN2_SHEET, n) for j, n in enumerate(LT_SRC)})
COPIES.update({LT_OVL_COPY0 + j: (OVL_SHEET, n) for j, n in enumerate(LT_OVL_SRC)})
COPIES.update({SPK_COPY0 + j: (D2_SHEET, n) for j, n in enumerate(SPK_SRC) if n not in (38, 39)})
# 38 / 39 (wall speaker backs, for the S / E walls) are not built: KBW wall pieces hang on W / N only
SPK_WALL = {36: "N", 37: "W"}          # wall speakers: wall-plane depth on that wall, as the gun rack
COPIES.update({SLOPED_COPY0 + j: (F3_SHEET, n) for j, n in enumerate(SLOPED_SRC)})
COPIES.update({FIG_COPY0 + j: (D1_SHEET, n) for j, n in enumerate(FIG_SRC)})
# 115-132 wall shelves honeywood_Simon_MD 116-133 (user 2026-11-17, page SimonMDsTiles112): even = W wall,
#         odd = N wall (art). The pack calls every one "Window Plant", Facing E, solidtrans; the copies get
#         the right Facing and no solid flag (they hang mid-wall, like the gun rack), and wall-plane depth.
HW_SHEET, HW_SRC, HW_COPY0 = "honeywood_Simon_MD", list(range(116, 134)), 115
COPIES.update({HW_COPY0 + j: (HW_SHEET, n) for j, n in enumerate(HW_SRC)})
HW_WALL = {n: ("W" if n % 2 == 0 else "N") for n in HW_SRC}
# 133-143 in-wall shelves furniture_02 88-99 / bar corner shelves 50-51 (user 2026-11-17: they should have
#         fill overlays). Simon's own overlays for them (container_overlays 48-77) are not in Raven Creek's
#         pack, so our copies get vanilla's books re-laid onto their boards (BOOK_BASES, GEN_COPIES below).
#         Wall-plane depth: W / N wall, corners W left half + N right half, pillars the other way round.
INWALL_SRC, INWALL_COPY0 = [88, 89, 90, 93, 94, 96, 97, 98, 99, 50, 51], 133
COPIES.update({INWALL_COPY0 + j: (FURN2_SHEET, n) for j, n in enumerate(INWALL_SRC)})
INWALL_WALL = {88: "W", 94: "W", 97: "W", 89: "N", 93: "N", 98: "N", 90: "C", 96: "C", 99: "C", 50: "C", 51: "C"}
# 2nd pass (user, in game 2026-11-17: the stand-in books drew in front of the shelves, between the boards):
# vanilla's books, re-laid onto OUR boards by shelf_relayout.py, as generated copies (GEN_COPIES). The bar
# corner shelves 50 / 51 are outer-corner pillars (user), with no overlay (the fridge bottles did not fit).
INWALL_WALL[50] = INWALL_WALL[51] = "P"
# vanilla's two book sets for the matched vanilla shelf (WorldFiller.lua: furniture_shelving_01_10 / _9 / _8)
BOOK_SETS = {"W": [("books&misc_01_17", "books&misc_01_19"), ("books&misc_02_17", "books&misc_02_19")],
             "N": [("books&misc_01_16", "books&misc_01_18"), ("books&misc_02_16", "books&misc_02_18")],
             "C": [("books&misc_01_0", "books&misc_01_1"), ("books&misc_02_6", "books&misc_02_7")]}
# base (sheet, index) -> (side, glass, lips key)
BOOK_BASES = {(FURN2_SHEET, 88): ("W", False, "inwall"), (FURN2_SHEET, 94): ("W", False, "inwall"),
              (FURN2_SHEET, 97): ("W", True, "inwall"), (FURN2_SHEET, 89): ("N", False, "inwall"),
              (FURN2_SHEET, 93): ("N", False, "inwall"), (FURN2_SHEET, 98): ("N", True, "inwall"),
              (FURN2_SHEET, 90): ("C", False, "inwall"), (FURN2_SHEET, 96): ("C", False, "inwall"),
              (FURN2_SHEET, 99): ("C", True, "inwall")}
# (the sloped-wall shelves had re-laid vanilla books here for one build; they now use Simon's own
# overlays 160-167, SLOPED_OVERLAYS)
# 148-153 the Green Military Locker (user: should it have an overlay? yes, Simon registers one for its two
#         front-facing tiles 0 / 1, art in Raven Creek's pack): base copies 148 / 149, overlays 150-153
LOCKER_COPY0 = 148
COPIES.update({148: (FURN_SHEET, 0), 149: (FURN_SHEET, 1)})
COPIES.update({150 + j: (OVL_SHEET, n) for j, n in enumerate(range(0, 4))})
# 154+ generated book overlays: GEN_COPIES[c] = (base (sheet, i), set index, tile index in the set)
GEN_COPY0 = 154
# 3rd pass (user 2026-11-17: copy art from the full Simon MD pack): the in-wall shelves take Simon's own
# overlays (SIMON_SHELF_OVERLAYS, copied from the standalone pack). No re-laid vanilla books are built any
# more; copy indices 154-205 stay reserved, unused.
BOOK_BASES = {}
GEN_COPIES = {}
for _b in sorted(BOOK_BASES):
    for _si in range(2):
        for _ti in range(2):
            GEN_COPIES[GEN_COPY0 + len(GEN_COPIES)] = (_b, _si, _ti)


def gen_copy_name(base, si, ti):
    for c, v in GEN_COPIES.items():
        if v == (base, si, ti):
            return "%s_%d" % (COPY_TILESET, c)
    raise KeyError((base, si, ti))


def _book_overlay(base_im, base, si, ti, vcache):
    import shelf_relayout as sr
    side, glass, lk = BOOK_BASES[base]
    ov = Image_open(os.path.join(vcache, BOOK_SETS[side][si][ti] + ".png"))
    lips = sr.INWALL_LIPS if lk == "inwall" else sr.SLOPED_LIPS[lk]
    if side == "C":
        a, _l, _n = sr.relayout(ov, base_im, "W", sr.X_REF["W"], sr.FRONT_X["W"], half="L", lips=lips)
        b, _l, _n = sr.relayout(ov, base_im, "N", sr.X_REF["N"], sr.FRONT_X["N"], half="R", lips=lips)
        a.alpha_composite(b)
        out = a
    else:
        out, _l, _n = sr.relayout(ov, base_im, side, sr.X_REF[side], sr.FRONT_X[side], lips=lips)
    return sr.glassed(out) if glass else out


def Image_open(p):
    from PIL import Image
    return Image.open(p).convert("RGBA")
# 144-147 floor statues (user 2026-11-17: mirrors of both): 144 / 145 copies of decoration_Simon_MD 30
#         (T-800, Facing E) / 33 (Alienation statue, Facing S), 146 / 147 their mirrors (Facing S / E).
#         Depth: best vanilla floor match for the original, flipped for the mirror.
STATUE_SRC, STATUE_COPY0 = [30, 33], 144
COPIES.update({STATUE_COPY0 + j: (D1_SHEET, n) for j, n in enumerate(STATUE_SRC)})
MIRROR_COPIES = {146: (D1_SHEET, 30), 147: (D1_SHEET, 33)}       # copy index -> mirrored source
# 206 / 207 mirrors of the stargate replica and the facehugger (user 2026-11-17), from the figure art
MIRROR_COPIES.update({206: (D1_SHEET, 0), 207: (D1_SHEET, 34)})
LIGHT_ON_TILESET = "KBWRavenCreek_on"      # lit art at the same index (HasLightOnSprite)
# 208-299 floor wedges (user 2026-11-17, page SimonMDsTiles97): floors_Simon_MD, half-square floor overlays
# (FloorOverlay / attachedFloor, built like rugs). 13 hardwoods drawn as north halves 0-12 and east halves
# 16-28 (same order), 10 carpets as north halves only (32-41). Four faces each, all our copies (one depth
# setup): N = north half, S = north half flipped vertically, E = east half, W = east half flipped
# horizontally. Carpets' east half: cut from a full square made of the north half + its vertical flip.
# Depth: vanilla's rug cell (floors_rugs_01_0, a full floor diamond) trimmed to the triangle.
FLOOR_SHEET = "floors_Simon_MD"
WEDGE_WOOD = list(range(0, 13))          # north half n, east half n + 16
WEDGE_CARPET = list(range(32, 42))
WEDGE_FACES = ("N", "E", "S", "W")
WEDGE_COPY0 = 208
WEDGE_COPIES = {}
for _n in WEDGE_WOOD + WEDGE_CARPET:
    for _f in WEDGE_FACES:
        WEDGE_COPIES[WEDGE_COPY0 + len(WEDGE_COPIES)] = (_n, _f)
WEDGE_DEPTH_FROM = ("floors_rugs_01", 0)
# 2nd pass (user, in game 2026-11-17): the W face is mirrored about the diamond's centre (_iso_flip; the plain
# flip left a 2 px jagged gap); the carpets use the pack's own east halves (48-63, missed in the 1st pass)
# and the six carpets 42-47 are added (copies 385-408, after the planters' raised plants)
WEDGE_CARPET2 = list(range(42, 48))
WEDGE_CARPET += WEDGE_CARPET2
for _n in WEDGE_CARPET2:
    for _f in WEDGE_FACES:
        WEDGE_COPIES[385 + len(WEDGE_COPIES) - 92] = (_n, _f)
# ---- batch 3 (user 2026-11-17) ----
# 300 / 301 Imperial Star Destroyer figure (decoration_Simon_MD 36, "Solar Destroyer", table-top) + mirror
FIG_SRC.append(36)
COPIES[300] = (D1_SHEET, 36)
MIRROR_COPIES[301] = (D1_SHEET, 36)
# 302 disco ball (decoration_Simon_MD 137, ceiling-hung, already a light in the pack: lightswitch, light blue,
#     radius 10): a lamp with a lit / unlit pair. Lit = the pack art (KBWRavenCreek_on_302), unlit = dimmed.
#     No solid flag (walk-through). Depth: vanilla ceiling lamp of the best shape.
DISCO_SRC, DISCO_COPY = 137, 302
COPIES[DISCO_COPY] = (D1_SHEET, DISCO_SRC)
DISCO_DIM = 0.45            # unlit: brightness x this
# 303-310 the sloped-wall shelves' own overlays (user: container_overlays 160-167 "match the sloped in
#     wall bookshelves"): in Raven Creek's pack but not registered in Simon_MD_WorldFiller.lua. By overlap:
#     160 / 161 tall N (furniture_03 10), 162 / 163 short N (11), 164 / 165 tall W (15), 166 / 167 short W
#     (14); fuller tile first, as vanilla and Simon list their pairs. They replace the re-laid vanilla books.
COPIES.update({303 + j: (OVL_SHEET, n) for j, n in enumerate(range(160, 168))})
SLOPED_OVERLAYS = {(F3_SHEET, 10): (160, 161), (F3_SHEET, 11): (162, 163),
                   (F3_SHEET, 15): (164, 165), (F3_SHEET, 14): (166, 167)}     # added to OVERLAYS below
# 409-422 the other slope direction (user, in game 2026-11-17: only one set of orientations): mirrored copies
#     of furniture_03 10-15 (409-414, a N-wall tile mirrors into a W-wall one, Facing S <-> E) and of their
#     overlays 160-167 (415-422). Plain 128-wide flip: Simon's own W / N pairs are mirror images under it.
# 2nd pass (user, in game: the "Reversed" ones looked identical): a plain mirror turns a W-wall tile into an
# N-wall tile with the SAME slope direction. Now each tile is reflected along its own wall (stays on that wall,
# its ends swap): flipped left-right about the wall's middle and every column moved along the wall's slope
# (_wall_reflect). Same copy indices.
SLOPED_REFLECT = {409 + j: (F3_SHEET, n) for j, n in enumerate(SLOPED_SRC)}
SLOPED_REFLECT.update({415 + j: (OVL_SHEET, n) for j, n in enumerate(range(160, 168))})
COPIES.update(SLOPED_REFLECT)
SLOPED_WALL = {(F3_SHEET, n): ("N" if n in (10, 11, 12) else "W") for n in SLOPED_SRC}
SLOPED_WALL.update({(OVL_SHEET, n): ("N" if n < 164 else "W") for n in range(160, 168)})
WALL_REFLECT_AXIS = {"N": 190, "W": 64}       # x' = axis - x (N-wall art spans columns ~63-127, W-wall 0-64)


def _wall_reflect(im, wall):
    """Reflect wall-hung art along its own wall. N wall (drops 1 row per 2 columns to the right):
    (x, y) -> (A - x, y + (A - 2x) / 2); W wall (rises to the right): (x, y) -> (A - x, y - (A - 2x) / 2)."""
    import numpy as np
    from PIL import Image
    a = np.array(im.convert("RGBA"))
    out = np.zeros_like(a)
    A = WALL_REFLECT_AXIS[wall]
    for x in range(a.shape[1]):
        nx = A - x
        if not 0 <= nx < a.shape[1]:
            continue
        dy = (A - 2 * x) // 2 * (1 if wall == "N" else -1)
        col = a[:, x]
        if dy >= 0:
            out[dy:, nx] = col[:a.shape[0] - dy]
        else:
            out[:dy, nx] = col[-dy:]
    return Image.fromarray(out, "RGBA")


def reflect_copy_name(sheet, i):
    for c, src in SLOPED_REFLECT.items():
        if src == (sheet, i):
            return "%s_%d" % (COPY_TILESET, c)
    raise KeyError((sheet, i))
# 423-425 the W-wall chalkboard furniture_02 24 / 25 / 26 (user, in game 2026-11-17: white lines on the S-N
#     board; the N-wall one is fine). Simon's tiles end in a light column (24's last, 26's first): drawn over
#     the neighbouring tile they show as a seam. The copies take the next inner column there. Wall-plane
#     depth (W), the pack's properties.
CHALK_W_COPIES = {423: 24, 424: 25, 425: 26}
COPIES.update({c: (FURN2_SHEET, n) for c, n in CHALK_W_COPIES.items()})
# 426-429 the tall Glass Display Cabinet furniture_02 46 / 47 with a fill overlay (user 2026-11-17: overlay
#     44 on page SimonMDsTiles36 matches it). Simon registers 46 -> (45, 44) and 47 -> (47, 46); Raven Creek's
#     pack has only 44. Copies 426 / 427 of the cabinet (so map cabinets stay untouched), 428 = overlay 44
#     (used for both fill levels of 46), 429 = overlay 44 mirrored for 47 (47 is 46 mirrored, silhouette
#     IoU 0.95), cleared over 47's dark frame. Depth: best vanilla container of the same Facing; overlays
#     take their cabinet's.
#     2nd pass (user: copying art from the full Simon MD pack is fine; a standalone version on the full pack
#     will follow): overlays 45-47 are copied from the standalone pack (Workshop 2852704777), so both
#     cabinets get Simon's own pair: 46 -> (45, 44), 47 -> (47, 46). Copies 428-431 = overlays 44-47.
CAB_SRC = {426: 46, 427: 47}
COPIES.update({c: (FURN2_SHEET, n) for c, n in CAB_SRC.items()})
COPIES.update({428 + j: (OVL_SHEET, n) for j, n in enumerate(range(44, 48))})
SIMON_STANDALONE = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600\2852704777\mods\Simon-MDs-Tiles"
# copies whose art is not in Raven Creek's pack: taken from the standalone Simon MD pack
FROM_STANDALONE = {(OVL_SHEET, 45), (OVL_SHEET, 46), (OVL_SHEET, 47)}


# 432-461 Simon's own fill overlays container_overlays 48-77 (standalone pack; Raven Creek lacks them) for the
#     wine shelf, bar corner shelves, barrel table and in-wall shelves (user 2026-11-17: "yes switch them").
#     Pairs as Simon_MD_WorldFiller.lua (fuller tile first). 91 (outer pillar) and 52 (barrel table, other
#     orientation) have none there.
SIMON_OVL2 = list(range(48, 78))
COPIES.update({432 + j: (OVL_SHEET, n) for j, n in enumerate(SIMON_OVL2)})
FROM_STANDALONE |= {(OVL_SHEET, n) for n in SIMON_OVL2}
SIMON_SHELF_OVERLAYS = {48: (50, 48), 49: (51, 49), 50: (53, 52), 51: (53, 52), 53: (55, 54),
                        88: (58, 56), 89: (59, 57), 90: (61, 60), 92: (68, 64), 93: (69, 65), 94: (70, 66),
                        95: (71, 67), 96: (63, 62), 97: (74, 72), 98: (75, 73), 99: (77, 76)}
# 462-466 base copies for the pieces that were on pack tiles (so their overlays register without touching map
#     tiles): wine shelf 48 / 49, barrel table 53, in-wall shelf ends 92 / 95. Wall-plane depth for the wall
#     pieces (wine: 48 hangs on the N wall, 49 on the W, as the art); the barrel table matches a vanilla table.
EXTRA_BASE = {462: 48, 463: 49, 464: 53, 465: 92, 466: 95}
COPIES.update({c: (FURN2_SHEET, n) for c, n in EXTRA_BASE.items()})
INWALL_WALL.update({92: "W", 95: "N"})
# wine shelf (user, in game: clipping like the cabinet door did): it is a deep standing unit, not a flat wall
# piece, so wall-plane depth put its front inside the wall. Depth from the best vanilla container with the
# art's facing (the pack's Facing is the wrong way round: 48 faces south, 49 east), like the cabinet fix.
WINE_FACING = {48: "S", 49: "E"}
# bar corner shelves 50 / 51 (outer-corner pillars; user, in game: they drew behind the straight shelves next
# to them): the box stands out from the corner, so its planes sit PILLAR_DEPTH_BIAS nearer, not 2
PILLAR_DEPTH_BIAS = 16
BAR_POST_BIAS = 8            # steps nearer than the post's front corner (4th pass, _contact_depth "flat")


def _standalone_packs():
    import glob
    return sorted(glob.glob(os.path.join(SIMON_STANDALONE, "**", "*.pack"), recursive=True))
# 2nd pass (user, in game: still dotted lines where the side tiles meet the middle): Simon's seam columns
# carry a dotted light line (423 col 63, 424 cols 2 / 63, every other row). The CHALK_SEAM_W columns at each
# seam side are now redrawn from CHALK_SEAM_FROM columns further in, moved along the W wall's slope (1 row
# per 2 columns), so the grid's horizontal lines and the frame continue through. Outer ends untouched.
CHALK_SEAM_SIDES = {423: ("R",), 424: ("L", "R"), 425: ("L",)}
CHALK_SEAM_W = 4
CHALK_SEAM_FROM = 4          # columns inward (= 2 rows along the slope)
# fill overlays drawn off their base: (sheet, index) -> rows down. container_overlays 20 (White Glass-Front
# Wardrobe, W-wall face, partly filled) is overlay 21 (full) less some items, 10 rows higher (99 % of its
# pixels match 21 at +10; _wardrobe_align.py; user, in game 2026-11-17: too high)
OVL_ROW_SHIFT = {(OVL_SHEET, 20): 10}


CHALK_DOT_LUM = 35           # a seam pixel this much brighter than BOTH horizontal neighbours is the dotted line
CHALK_SEAM_REACH = 3         # columns either side of a seam that are checked


CHALK_DEPTH_BIAS = 12        # = RACK_DEPTH_BIAS


def chalk_seam_fix(im, sides):
    return im                # 3rd pass: art untouched (pixel edits damaged letters); fixed by depth instead


def chalk_seam_fix_board(ims):
    """3rd pass (the 2nd, redrawing seam columns from further in, doubled text and grid lines). The three
    W-wall tiles {copy: image} are assembled as they hang (north tile 425 at x 0, then 424 at -64 / +32, 423 at
    -128 / +64). On the screen columns within CHALK_SEAM_REACH of the two seams, a pixel brighter than both
    its left and right neighbours by CHALK_DOT_LUM is the 1-px dotted line: every tile pixel drawn there takes
    the darker neighbour's colour. The board's own grid lines are 2 px wide, so they are left alone."""
    import numpy as np
    from PIL import Image
    order = [(425, 128, 0), (424, 64, 32), (423, 0, 64)]          # copy, x, y on a 256 x 320 canvas
    arrs = {c: np.array(ims[c].convert("RGBA")) for c, _x, _y in order}
    W, H = 256, 320
    can = np.zeros((H, W, 4), int)
    for c, x, y in reversed(order):                                # south first, as drawn
        a = arrs[c].astype(int)
        m = a[:, :, 3] > 0
        can[y:y + 256, x:x + 128][m] = a[m]
    lum = (can[:, :, 0] * 3 + can[:, :, 1] * 6 + can[:, :, 2]) // 10
    seams = []
    for c, x, _y in order:
        cols = np.nonzero((arrs[c][:, :, 3] > 0).any(0))[0]
        if c in (424, 425):
            seams.append(x + cols[0])
        if c in (423, 424):
            seams.append(x + cols[-1])
    fixed = 0
    for s in seams:
        for X in range(s - CHALK_SEAM_REACH, s + CHALK_SEAM_REACH + 1):
            if X < 1 or X >= W - 1:
                continue
            on = (can[:, X, 3] > 0) & (can[:, X - 1, 3] > 0) & (can[:, X + 1, 3] > 0)
            dot = on & (lum[:, X] > lum[:, X - 1] + CHALK_DOT_LUM) & (lum[:, X] > lum[:, X + 1] + CHALK_DOT_LUM)
            # the seam line is dotted (every other row); a letter's stroke is a solid run: isolated pixels only
            up, dn = np.roll(dot, 1), np.roll(dot, -1)
            dot = dot & ~up & ~dn
            for Y in np.nonzero(dot)[0]:
                nb = X - 1 if lum[Y, X - 1] <= lum[Y, X + 1] else X + 1
                col = can[Y, nb]
                for c, x, y in order:
                    tx, ty = X - x, Y - y
                    if 0 <= tx < 128 and 0 <= ty < 256 and arrs[c][ty, tx, 3] > 0:
                        arrs[c][ty, tx, :3] = col[:3]
                fixed += 1
    print("chalkboard seam: %d dotted-line pixels fixed at seams %s" % (fixed, seams))
    return {c: Image.fromarray(a, "RGBA") for c, a in arrs.items()}
# ---- neon lights (user 2026-11-17, page SimonMDsTiles135): lighting_Simon_MD tiles that have a lit
# partner on lighting_Simon_MD_on (all of 14-53). Our copies: unlit art = the pack tile, lit art in
# KBWRavenCreek_on at the same index; HasLightOnSprite; the pack's `streetlight` flag dropped (vanilla
# lights streetlight tiles on its own schedule); light colour matched to the art (the pack has the cyan
# and pink strips' colours swapped, and the pink dancer tagged teal); wall-plane depth.
NEON_SHEET, NEON_ON_SHEET = "lighting_Simon_MD", "lighting_Simon_MD_on"
NEON_COPY0 = 311
# strips 14-37: two heights (top of the wall 14-25, floor level 26-37), each block of 12:
#   0 / 1 cyan N wall end / run, 2 / 3 cyan W wall run / end, 4-7 the same in pink,
#   8 / 9 cyan / pink inside corner (both walls), 10 / 11 cyan / pink corner cap (the corner point)
NEON_STRIPS = list(range(14, 38))
COPIES.update({NEON_COPY0 + j: (NEON_SHEET, n) for j, n in enumerate(NEON_STRIPS)})       # 311-334
NEON_LADY = {335: 40, 336: 41}                                                              # W / N
COPIES.update({c: (NEON_SHEET, n) for c, n in NEON_LADY.items()})
# "The Italian Bowl" (42-53): two tiles wide, each tile split into green text / white pasta / red bowl.
# Merged into one tile per square (copy -> its layers), W wall north -> south 337, 338; N wall west ->
# east 339, 340 (composited to check, 2026-11-17)
NEON_SIGN = {337: (43, 45, 47), 338: (42, 44, 46), 339: (48, 50, 52), 340: (49, 51, 53)}
COPIES.update({c: (NEON_SHEET, layers[0]) for c, layers in NEON_SIGN.items()})
# its SpriteGridPos per copy, keyed by the copy's first layer: W wall (Facing E) north 0,0 / south 0,1; N wall
# (Facing S) west 0,0 / east 1,0. Each Facing pair is one complete group of its own.
NEON_SIGN_GRID = {43: "0,0", 42: "0,1", 48: "0,0", 49: "1,0"}
# (user, in game 2026-11-17: the strips still gave no light) the pack's 193 / 100 / 100 and 30 / 100 / 100 are
# hue / saturation / brightness, not RGB: as RGB they were a dim teal and a dull red. Real bright cyan / pink now.
NEON_CYAN, NEON_PINK, NEON_WHITE = ("20", "220", "255"), ("255", "60", "200"), ("255", "255", "255")
# ---- honeywood furniture with Simon's fill overlays (user 2026-11-17, page SimonMDsTiles112): our copies
# 341-350 of honeywood_Simon_MD 62-71 (wardrobes 62-65, shop shelves 66-69, clothes racks 70 / 71) and
# 351-370 of their overlays container_overlays 16-35 (all in Raven Creek's pack; Simon_MD_WorldFiller.lua
# pairs). The shop shelves are tagged attachedW in both facings: the S-facing copies get attachedN.
HWF_SRC, HWF_COPY0 = list(range(62, 72)), 341
COPIES.update({HWF_COPY0 + j: (HW_SHEET, n) for j, n in enumerate(HWF_SRC)})
COPIES.update({351 + j: (OVL_SHEET, n) for j, n in enumerate(range(16, 36))})
HWF_OVERLAYS = {(HW_SHEET, 62): (19, 18), (HW_SHEET, 63): (17, 16), (HW_SHEET, 64): (23, 22), (HW_SHEET, 65): (21, 20),
                (HW_SHEET, 66): (25, 24), (HW_SHEET, 67): (27, 26), (HW_SHEET, 68): (29, 28), (HW_SHEET, 69): (31, 30),
                (HW_SHEET, 70): (33, 32), (HW_SHEET, 71): (35, 34)}     # added to OVERLAYS below
# the "Fancy Wooden Shop" shelves 66-69 are wall benches with shoes under the seat (user, in game 2026-11-17):
# seats like vanilla chairs (bed + chair<Facing> + BedType) with a seat position in our seating.txt
# (write_seating), facing away from the wall; the shoe storage stays. Seat (id, x, height, y) in tile units
# from the tile centre (+x east, +y south): just off the wall, at bench height (vanilla couch seats sit at
# 0.12-0.124 for Surface 17; this bench is Surface 13).
BENCH_SRC = (66, 67, 68, 69)
BENCH_SEAT = {"E": ("E", -0.05, 0.095, 0.0), "S": ("S", 0.0, 0.095, -0.05)}
# shop shelves (low, wall-mounted) and clothes racks (wall objects): wall-plane depth
HWF_WALL = {66: "W", 67: "N", 68: "W", 69: "N", 70: "W", 71: "N"}
# ---- planters (user 2026-11-17, pages SimonMDsTiles198-200, vegetation_indoor_Simon_MD): the beds, boxes,
# floor plants and flowers are built on the pack tiles. The plants drawn raised to sit in a planter (low bed
# 21-27, tall bed 96-102) get copies 371-384 WITHOUT the pack's BlocksPlacement, so KBW lets them go onto a
# planter square (its placement refuses BlocksPlacement sprites on a solidtrans square).
VEG_SHEET = "vegetation_indoor_Simon_MD"
# 2nd pass (user 2026-11-18: "cant they handle height automatically?"; both catches accepted): the in-bed
# plants (low 21-27, tall 96-102) were the floor plants drawn 50 / 67 rows higher (_plant_probe.py: every
# plant the same lift, +-2). They are dropped. One plant per kind, a copy of the floor plant with IsTableTop
# (371-377, the retired raised-plant slots); our low and tall bed copies (512-550) carry IsTable + Surface, so
# the game (and KBWRavenCreek_TableTop.lua) lifts a plant built on a bed to the soil. Catches: the bed copies
# need their own depth (_box_depth); a plant on a map-placed bed (the pack tile, no Surface) stays at floor
# level.
VEG_RAISED = []
PLANT_SRC = [1, 2, 3, 4, 5, 6, 19]          # fern, yucca, snake plant, peace lily, boxwood, pothos, purple rose
PLANT_COPIES = {371 + j: n for j, n in enumerate(PLANT_SRC)}
COPIES.update({c: (VEG_SHEET, n) for c, n in PLANT_COPIES.items()})
BED_SRC = {"low": [20] + list(range(28, 43)) + list(range(118, 122)),
           "tall": list(range(60, 75)) + list(range(122, 126))}
BED_LIFT_ROWS = {"low": 50, "tall": 67}     # Simon's in-bed plants: rows above the floor plants (2x art)
BED_SURFACE = {h: str(r // 2) for h, r in BED_LIFT_ROWS.items()}   # renderYOffset units = 2 rows: 25 / 33
# The bed copies are their own small tileset BED_TILESET in the same tiledef file (a tileset holds at most 512
# tiles, the game refuses the file otherwise: KBWRavenCreek is full; user, in game 2026-11-18 at 552)
BED_TILESET = "KBWRavenCreekBeds"
# (user 2026-11-18, before the release: "remove the planters and the associated flowers for the time being, we
# will revisit them later"): PLANTERS_ON False = no raised beds / indoor plants are built (simonmd_furniture2)
# and the bed tileset is not written. True brings both back as tested by composite in round 18.
PLANTERS_ON = False
BED_COPIES = {}                             # bed tileset index -> (height, bed tile)
for _j, (_h, _n) in enumerate([(h, n) for h in ("low", "tall") for n in BED_SRC[h]] if PLANTERS_ON else []):
    BED_COPIES[_j] = (_h, _n)
BED_OF_TILE = {n: h for h, ns in BED_SRC.items() for n in ns}
TILESET_MAX = 512


def bed_copy_name(n):
    for c, (_h, m) in BED_COPIES.items():
        if m == n:
            return "%s_%d" % (BED_TILESET, c)
    raise KeyError(n)
# 467-477 flower buckets (user, in game 2026-11-17: the raised ones should use the game's own table-top
#     mechanic, like crates and the figures). Copies of the floor buckets 43-51 and of 54 / 55 (raised, no
#     floor twin; moved down to the floor, FLOWER_DROP_ROWS) with IsTableTop: on the floor they stand on the
#     floor, on a table the game (and KBWRavenCreek_TableTop.lua) lifts them to its top. 52 / 53 were 48 / 49
#     drawn 61 / 66 rows higher and are dropped.
FLOWER_SRC = list(range(43, 52)) + [54, 55]
FLOWER_COPIES = {467 + j: n for j, n in enumerate(FLOWER_SRC)}
COPIES.update({c: (VEG_SHEET, n) for c, n in FLOWER_COPIES.items()})
FLOWER_DROP_ROWS = {54: 63, 55: 63}       # the mean lift of the 52 / 53 pairs
# (user, in game 2026-11-17: on a table the grass showed through under the pots) Simon's flowers carry a faint
# halo and a dark semi-transparent drop shadow; those pixels win the depth test and hide the table. Cleared on
# our copies: alpha < FIG_ALPHA_MIN (the figures' rule), and semi-transparent pixels darker than this
FLOWER_SHADOW_LUM = 60


# ---- more neon colours (user 2026-11-17: "versions for all the bulbs, grouped into cards by color"): the cyan
# strips' six pieces per height (N end / N run / W run / W end, inside corner, corner cap), recoloured. Every
# pixel of Simon's cyan strip art (unlit and lit) is a saturated cyan (hue 170-210), so the new colours are
# a straight hue change of the whole tile, saturation / brightness / alpha kept (white: saturation removed).
# Light colour = the vanilla bulb's (lightR kept non-zero). Copy indices: the free ones (the retired re-laid
# book range 154-205, the removed reversed sloped shelves 409-422, and 478-511).
NEON_COLORS = [  # (slug, name, art hue in degrees or None for white, light rgb, recipe bulb)
    ("red", "Red", 0, ("255", "20", "20"), "Base.LightBulbRed"),
    ("orange", "Orange", 30, ("255", "128", "20"), "Base.LightBulbOrange"),
    ("yellow", "Yellow", 55, ("255", "255", "20"), "Base.LightBulbYellow"),
    ("green", "Green", 120, ("20", "255", "20"), "Base.LightBulbGreen"),
    ("blue", "Blue", 225, ("20", "20", "255"), "Base.LightBulbBlue"),
    ("purple", "Purple", 270, ("128", "20", "255"), "Base.LightBulbPurple"),
    ("magenta", "Magenta", 300, ("255", "20", "255"), "Base.LightBulbMagenta"),
    ("white", "White", None, ("255", "255", "255"), "Base.LightBulb"),
]
NEON_CYAN_PIECES = (0, 1, 2, 3, 8, 10)     # offsets in a height block of 12 (see NEON_STRIPS)
NEON_FREE = list(range(154, 206)) + list(range(409, 423)) + list(range(478, 512))
NEON_COLOR_COPIES = {}                      # copy -> (cyan source tile, colour slug)
_free = iter(NEON_FREE)
for _slug, _nm, _h, _rgb, _bulb in NEON_COLORS:
    for _base in (14, 26):
        for _o in NEON_CYAN_PIECES:
            NEON_COLOR_COPIES[next(_free)] = (_base + _o, _slug)
NEON_COLOR_INFO = {s: (h, rgb, bulb) for s, _n, h, rgb, bulb in NEON_COLORS}
for _c in NEON_COLOR_COPIES:                # the reversed sloped shelves' slots are reused
    SLOPED_REFLECT.pop(_c, None)
    COPIES.pop(_c, None)
COPIES.update({_c: (NEON_SHEET, _n) for _c, (_n, _s) in NEON_COLOR_COPIES.items()})


def neon_color_name(n, slug):
    for c, v in NEON_COLOR_COPIES.items():
        if v == (n, slug):
            return "%s_%d" % (COPY_TILESET, c)
    raise KeyError((n, slug))


def neon_recolor(im, slug):
    import numpy as np
    from PIL import Image
    hue = NEON_COLOR_INFO[slug][0]
    a = np.array(im.convert("RGBA"))
    hsv = np.array(Image.fromarray(a[:, :, :3], "RGB").convert("HSV")).astype(int)
    if hue is None:
        hsv[:, :, 1] = hsv[:, :, 1] * 8 // 100
    else:
        hsv[:, :, 0] = round(hue * 255 / 360)
    rgb = np.array(Image.fromarray(hsv.astype(np.uint8), "HSV").convert("RGB"))
    out = a.copy()
    out[:, :, :3] = rgb
    return Image.fromarray(out, "RGBA")


def _neon_fill(img, nb, dx, dy, x0, x1):
    """img with nb (shifted by dx, dy) in columns x0..x1-1, wherever nb's pixel is more opaque than img's."""
    import numpy as np
    from PIL import Image
    a = np.array(img.convert("RGBA"))
    s = np.zeros_like(a)
    b = np.array(nb.convert("RGBA"))
    h, w = a.shape[:2]
    ys, xs = slice(max(0, dy), min(h, h + dy)), slice(max(0, dx), min(w, w + dx))
    s[ys, xs] = b[max(0, -dy):min(h, h - dy), max(0, -dx):min(w, w - dx)]
    m = s[:, :, 3] > a[:, :, 3]           # (faint edge pixels of our own must not block the neighbour's line)
    m[:, :x0] = False
    m[:, x1:] = False
    a[m] = s[m]
    return Image.fromarray(a, "RGBA")


def neon_seam_fix(n, load):
    """Strip tile n (14-37) with its joins made whole (user, in game 2026-11-18: the N-S run sat lower than
    the inside corner; the low E-W run looked thinner where two pieces meet). Simon's runs end one row short
    in their own square and rely on the next piece's overhang (the next square's pixels reaching into this
    one); the W run's line also sits one row lower than the corner's W half. Each run now carries, in its
    own square's columns (W wall 0-63, N wall 64-127), the pixels the next run would add: from the run south
    of it (drawn at -64, +32) for W, east of it (+64, +32) for N. The inside corner takes the fixed W run's
    columns 0-63 as its W half and the N run's overhang on its N half. `load(n)` -> that tile's art (unlit
    or lit sheet; the same fix is applied to both)."""
    o, base = (n - 14) % 12, n - (n - 14) % 12
    pink = 4 if o in (4, 5, 6, 7, 9, 11) else 0
    run_w, run_n = base + 2 + pink, base + 1 + pink
    fixed_w = _neon_fill(load(run_w), load(run_w), -64, 32, 0, 64)
    if o in (2, 6):
        return fixed_w
    if o in (1, 5):
        return _neon_fill(load(run_n), load(run_n), 64, 32, 64, 128)
    if o in (8, 9):
        import numpy as np
        from PIL import Image
        a = np.array(load(n).convert("RGBA"))
        a[:, :64] = np.array(fixed_w)[:, :64]
        return _neon_fill(Image.fromarray(a, "RGBA"), load(run_n), 64, 32, 64, 128)
    return load(n)


def neon_role(n):
    """(wall W / N / C, colour (r, g, b)) for a strip tile."""
    o = (n - 14) % 12
    wall = {0: "N", 1: "N", 2: "W", 3: "W", 4: "N", 5: "N", 6: "W", 7: "W"}.get(o, "C")
    cyan = o in (0, 1, 2, 3, 8, 10)
    return wall, NEON_CYAN if cyan else NEON_PINK


def neon_wall(c):
    sh, n = COPIES[c]
    if c in NEON_SIGN:
        return "W" if c in (337, 338) else "N"
    if c in NEON_LADY:
        return "W" if n == 40 else "N"
    return neon_role(n)[0]


def neon_copy_name(n):
    for c, v in COPIES.items():
        if v == (NEON_SHEET, n) and c not in NEON_SIGN:
            return "%s_%d" % (COPY_TILESET, c)
    raise KeyError(n)


def wedge_copy_name(n, face):
    for c, v in WEDGE_COPIES.items():
        if v == (n, face):
            return "%s_%d" % (COPY_TILESET, c)
    raise KeyError((n, face))


def _wedge_art(n, face, load):
    """Art for wedge texture n on face N / E / S / W; load(i) -> the pack's floors_Simon_MD_i image."""
    import numpy as np
    from PIL import Image
    north = load(n)
    if face == "N":
        return north
    if face == "S":
        return _vflip_floor(north)
    east = load(n + 16)                   # every texture's east half is 16 on (carpets 48-63 too)
    return east if face == "E" else _iso_flip(east)


def _vflip_floor(im):
    """Flip a floor tile top-to-bottom about the floor diamond's middle row (rows 192-255 -> same rows)."""
    import numpy as np
    from PIL import Image
    a = np.array(im.convert("RGBA"))
    out = np.zeros_like(a)
    out[192:256] = a[192:256][::-1]
    return Image.fromarray(out, "RGBA")


ISO_AXIS_COLS = 126      # the floor diamond spans columns 0-125 (centre 62.5), not 0-127


def _iso_flip(im):
    """Mirror a tile left-right about the floor diamond's centre column (62.5), so the mirrored art still
    sits on the diamond. A plain 128-wide flip moves it 2 px right (in game: the W floor wedge left a
    jagged gap against its neighbour, user 2026-11-17). Used for floor art only: Simon's own wall-piece
    pairs (furniture_03 15 / 10: columns 0-64 / 63-127) are mirror images under the plain flip, so wall
    and standing pieces keep it."""
    import numpy as np
    from PIL import Image
    a = np.array(im.convert("RGBA"))
    out = np.zeros_like(a)
    out[:, :ISO_AXIS_COLS] = a[:, :ISO_AXIS_COLS][:, ::-1]
    return Image.fromarray(out, "RGBA")
# low tables and the two floor statues do not block movement (user 2026-11-17)
WALKABLE_COPY_SHEETS = {(FURN2_SHEET, n) for n in LT_SRC} | {(D1_SHEET, n) for n in STATUE_SRC}
# Figures follow vanilla's table-top convention (2026-11-17, 2nd pass): 220 of vanilla's 256 IsSurfaceOffset
# table-top tiles are Surface 34 with the art's bottom at row 170. Our copies move the art to that row and
# take Surface 34; depth comes from a vanilla Surface-34 table-top piece of the same shape (small shift only).
# 1st pass (raised art + depth borrowed from anything, shifted up to 79 rows, 12 steps nearer) made the
# facehugger worse and left the BT-BT's notch.
FIG_ROW, FIG_SURFACE_VALUE = 170, 34
FIG_DEPTH_BIAS = 2           # the TV margin, just enough to win against the table under it
FIG_ALPHA_MIN = 64           # halo pixels below this alpha cleared (the kiln fix)
FIG_SHADOW_MAX_ALPHA = 200   # translucent grey drop shadow (the facehugger's) cleared: grey = channel spread
FIG_SHADOW_MAX_SPREAD = 14   # <= this, alpha < FIG_SHADOW_MAX_ALPHA


# Stargate replica as a light (user 2026-11-17): the lit sprite is the pack art; the unlit one has the event
# horizon cut out of the ring (rows GATE_HORIZON_ROWS, filled between the leftmost and rightmost blue pixel
# of each row) and the horizon's blue glow on the platform and the DHD turned back to grey at the same
# brightness. Light: cyan-blue, radius 4; the recipe takes a cyan bulb (vanilla LightBulbCyan 0/255/255).
GATE_SRC = 0
GATE_HORIZON_ROWS = (93, 123)
GATE_RIM = 4                  # (1st pass only)
GATE_HORIZON_B = 140          # horizon = blue pixels brighter than this (the ring's inner rim is dimmer)
GATE_LIGHT = {"lightR": "90", "lightG": "200", "lightB": "255", "LightRadius": "4"}


def _blue(a):
    return (a[:, :, 3] > 0) & (a[:, :, 2] > a[:, :, 0] + 40) & (a[:, :, 2] > a[:, :, 1])


def gate_off_art(im):
    """The stargate with no event horizon and no blue glow (the unlit state)."""
    import numpy as np
    from PIL import Image
    a = np.array(im.convert("RGBA")).astype(int)
    blue = _blue(a)
    on = a[:, :, 3] > 0
    y0, y1 = GATE_HORIZON_ROWS
    # the ring's own colour: its non-blue pixels beside the horizon
    ring_px = a[y0:y1 + 1][on[y0:y1 + 1] & ~blue[y0:y1 + 1]][:, :3]
    ring_rgb = np.median(ring_px, axis=0).astype(int) if len(ring_px) else np.array([60, 60, 70])
    horizon = np.zeros(blue.shape, bool)
    rim = np.zeros(blue.shape, bool)
    # 2nd pass (user, in game 2026-11-17: the cut took the inner side of the ring): the horizon is only the
    # strongly lit blue (B > GATE_HORIZON_B); the dimly lit blue pixels either side are the ring's inner rim,
    # kept and turned back to the ring's colour
    strong = blue & (a[:, :, 2] > GATE_HORIZON_B)
    for y in range(y0, y1 + 1):
        xs = np.nonzero(strong[y])[0]
        if not len(xs):
            continue
        horizon[y, xs.min():xs.max() + 1] = True
        rim[y] = blue[y] & ~horizon[y]
    a[horizon] = 0
    a[rim & blue, :3] = ring_rgb
    glow = (a[:, :, 3] > 0) & (a[:, :, 2] > a[:, :, 0] + 25)
    lum = (a[:, :, 0] * 3 + a[:, :, 1] * 6 + a[:, :, 2]) // 10
    for ch in range(3):
        a[:, :, ch] = np.where(glow, lum, a[:, :, ch])
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def _figure_art(im, ref=None):
    """Figure copy art: halo and drop shadow removed, moved down so its bottom row is FIG_ROW (`ref`: take
    the shift from this image instead, so a lit / unlit pair stays aligned)."""
    import numpy as np
    from PIL import Image
    def clean(x):
        a = np.array(x.convert("RGBA")).astype(int)
        a[a[:, :, 3] < FIG_ALPHA_MIN] = 0
        spread = a[:, :, :3].max(axis=2) - a[:, :, :3].min(axis=2)
        a[(a[:, :, 3] < FIG_SHADOW_MAX_ALPHA) & (spread <= FIG_SHADOW_MAX_SPREAD)] = 0
        return a
    a = clean(im)
    r = clean(ref) if ref is not None else a
    rows = np.nonzero(r[:, :, 3].any(axis=1))[0]
    dy = FIG_ROW - int(rows.max())
    out = np.zeros_like(a)
    if dy >= 0:
        out[dy:] = a[:a.shape[0] - dy]
    else:
        out[:dy] = a[-dy:]
    return Image.fromarray(out.astype(np.uint8), "RGBA")


def mirror_copy_name(sheet, i):
    for c, src in MIRROR_COPIES.items():
        if src == (sheet, i):
            return "%s_%d" % (COPY_TILESET, c)
    raise KeyError((sheet, i))
# Tile properties for sheets Raven Creek does not tiledef: the standalone Simon MD pack's own values
# (SimonMDsTiles.tiles, read 2026-11-17), plus a Facing for the speakers (the pack sets none; from the art:
# in each group of 4 the front shows on the lower-left face (S), lower-right (E), then backs N, W)
_SPK_NAMES = {8: ("Speaker Large", {"CanScrap": "", "ScrapSize": "Large", "Surface": "74", "solid": ""}),
              12: ("Speakers Medium", {"CanScrap": "", "Surface": "53", "solidtrans": ""}),
              16: ("Speakers Small", {"CanScrap": "", "ScrapSize": "Small"}),
              32: ("Speakers Small Standing", {"CanScrap": "", "ScrapSize": "Small"}),
              36: ("Speakers Small Hanging", {"CanScrap": "", "ScrapSize": "Small"})}
PROPS_EXTRA = {}
for _g, (_name, _p) in _SPK_NAMES.items():
    for _j, _f in enumerate("SENW"):
        _d = dict(_p, CustomName=_name, GroupName="Speakers", IsMoveAble="", Facing=_f)
        if _g == 36 and _f in "SE":            # hung on the N / W wall, like vanilla wall objects
            _d["attachedN" if _f == "S" else "attachedW"] = ""
        PROPS_EXTRA[(D2_SHEET, _g + _j)] = _d
PROPS_EXTRA.update({
    (F3_SHEET, 10): {"ContainerCapacity": "40", "CustomName": "Shelves", "Facing": "S", "GroupName": "Oakwood", "container": "shelves", "IsMoveAble": ""},
    (F3_SHEET, 11): {"ContainerCapacity": "20", "CustomName": "Shelves", "Facing": "S", "GroupName": "Oakwood", "container": "shelves", "IsMoveAble": ""},
    (F3_SHEET, 12): {"CustomName": "Shelf Side Panel", "Facing": "S", "IsMoveAble": ""},
    (F3_SHEET, 13): {"CustomName": "Shelf Side Panel", "Facing": "E", "IsMoveAble": ""},
    (F3_SHEET, 14): {"ContainerCapacity": "20", "CustomName": "Shelves", "Facing": "E", "GroupName": "Oakwood", "container": "shelves", "IsMoveAble": ""},
    (F3_SHEET, 15): {"ContainerCapacity": "40", "CustomName": "Shelves", "Facing": "E", "GroupName": "Oakwood", "container": "shelves", "IsMoveAble": ""},
})
# figures: Surface = how far above the floor the art's base is drawn (1x px), so vanilla / KBW / our
# table-top Lua set renderYOffset = table height - Surface: on the floor -Surface, on a table its height.
# Calibrated on the TikiTown desk mic (art bottom row 165 = Surface 29, so floor row 223).
_FIG_FLOOR_ROW = 223
FIG_SURFACE = {}            # source index -> Surface, filled by _figure_props from the art
FIG_DROP = {"solidtrans", "solid"}
_COPY_DROP = {b"solid", b"solidtrans"}
RACK_COPIES = {0: "W", 1: "W", 2: "N", 3: "N"}
# The rack spans two squares. At 2 steps (the Wall Screen TV's margin; the TV is one tile) the
# neighbouring square's wall corner won at the join and cut a notch out of the rack's top (user, in
# game 2026-11-16, one orientation). 12 = the margin that puts the TV in front of light switches.
RACK_DEPTH_BIAS = 12
# base pack tile -> its two overlay tiles (Simon_MD_WorldFiller.lua, standalone Simon MD pack). The
# glass display cabinet (furniture_02_Simon_MD_46 / 47 -> overlays 44-47): Raven Creek's pack has only 44,
# 45-47 come from the standalone pack (CAB_SRC / FROM_STANDALONE).
OVERLAYS = {(FURN_SHEET, 4): (5, 4), (FURN_SHEET, 5): (7, 6), (FURN_SHEET, 8): (10, 8),
            (FURN_SHEET, 9): (11, 9), (FURN_SHEET, 11): (14, 12), (FURN_SHEET, 12): (15, 13)}
# low glass tables (4 colours of the same shape): 30 / 31 / 32 / 33 -> overlays (38, 36) / (39, 37) /
# (42, 40) / (43, 41), +4 per colour (Simon_MD_WorldFiller.lua). The in-wall and wine shelves
# (furniture_02 48-51, 88-99) are NOT here: Raven Creek's pack lacks their overlays 48-77.
for _c in range(4):
    for _j, _ov in enumerate(((38, 36), (39, 37), (42, 40), (43, 41))):
        OVERLAYS[(FURN2_SHEET, 30 + 4 * _c + _j)] = _ov
# Green Military Locker (Simon_MD_WorldFiller.lua): 0 -> (1, 0), 1 -> (3, 2)
OVERLAYS[(FURN_SHEET, 0)] = (1, 0)
OVERLAYS[(FURN_SHEET, 1)] = (3, 2)
OVERLAYS.update(SLOPED_OVERLAYS)
OVERLAYS.update(HWF_OVERLAYS)
OVERLAYS[(FURN2_SHEET, 46)] = (45, 44)     # glass display cabinet (Simon_MD_WorldFiller.lua); 45-47 from
OVERLAYS[(FURN2_SHEET, 47)] = (47, 46)     # the standalone pack (FROM_STANDALONE)
OVERLAYS.update({(FURN2_SHEET, b): v for b, v in SIMON_SHELF_OVERLAYS.items()})
_VANILLA_MEDIA = r"C:\Program Files (x86)\Steam\steamapps\common\ProjectZomboid\media"
_VANILLA_DEPTHMAPS = os.path.join(_VANILLA_MEDIA, "depthmaps")
OVERLAY_LUA_NAME = "KBWRavenCreek_ContainerOverlays.lua"


def copy_name(sheet, i):
    for c, src in COPIES.items():
        if src == (sheet, i):
            return "%s_%d" % (COPY_TILESET, c)
    raise KeyError((sheet, i))


def modinfo_lines():
    return ["pack=%s" % COPY_PACK, "tiledef=%s %d" % (COPY_TILEDEF_NAME, COPY_TILEDEF_ID)]


def _facing(props):
    """The vanilla Facing a piece matches: its own Facing, else E for attachedW / S for attachedN."""
    if props.get("Facing") in ("E", "S", "W", "N"):
        return props["Facing"]
    return "E" if "attachedW" in props else "S" if "attachedN" in props else None


def _vanilla_pool():
    """{Facing: [(sprite, depth cell RGBA, art mask)]}: vanilla single-tile containers with a depth cell."""
    import glob
    import numpy as np
    from PIL import Image
    depth_sheets = {os.path.basename(p)[6:-4] for p in glob.glob(os.path.join(_VANILLA_DEPTHMAPS, "DEPTH_*.png"))}
    found = {"E": [], "S": []}
    for f in glob.glob(os.path.join(_VANILLA_MEDIA, "tile_definitions", "*.tiles")) + glob.glob(os.path.join(_VANILLA_MEDIA, "*.tiles")):
        try:
            _v, ts, _o = k._parse(open(f, "rb").read())
        except Exception:
            continue
        for sheet, t in ts.items():
            sh = sheet.decode()
            if sh not in depth_sheets:
                continue
            for i, pr in enumerate(t[6]):
                p = {a.decode(): b.decode() for a, b in pr}
                if p.get("Facing") in found and "container" in p and "SpriteGridPos" not in p:
                    found[p["Facing"]].append((sh, i))
    cache = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_cache_vanilla_match")
    k._extract_from_pack(k._VANILLA_TILES2X, ["%s_%d" % r for fl in found.values() for r in fl], cache)
    dimgs, pool = {}, {"E": [], "S": []}
    for fc, refs in found.items():
        for sh, i in refs:
            p = os.path.join(cache, "%s_%d.png" % (sh, i))
            ci = k._vanilla_depth_cell_index(sh, i)
            if not os.path.exists(p) or ci is None:
                continue
            if sh not in dimgs:
                dimgs[sh] = Image.open(os.path.join(_VANILLA_DEPTHMAPS, "DEPTH_%s.png" % sh)).convert("RGBA")
            d = dimgs[sh]; cols = d.size[0] // 128
            if (ci // cols + 1) * 256 > d.size[1]:
                continue
            cell = d.crop(((ci % cols) * 128, (ci // cols) * 256, (ci % cols) * 128 + 128, (ci // cols) * 256 + 256))
            if not np.array(cell)[:, :, 3].any():
                continue
            pool[fc].append(("%s_%d" % (sh, i), cell, np.array(Image.open(p).convert("RGBA"))[:, :, 3] > 40))
    return pool


DEPTH_MATCH = {}    # copy index -> (vanilla sprite, overlap), filled by _depth_cells (for the notes)


def _depth_cells(tiles, src_props):
    """{copy index: 128x256 RGBA depth cell} for every copy."""
    import numpy as np
    pool = _vanilla_pool()
    out = {}
    out.update(_batch2_depth_cells(tiles, src_props))
    for c in sorted(tiles):
        if COPIES[c][0] in (OVL_SHEET, CT_SHEET) or c in out:
            continue
        im = tiles[c][1]
        if c in RACK_COPIES:
            out[c] = k._wall_plane_depth(RACK_COPIES[c], im, RACK_DEPTH_BIAS)
            continue
        art = np.array(im)[:, :, 3] > 40
        cands = pool[_facing(src_props[c])]
        score = lambda r: (art & r[2]).sum() / max(1, (art | r[2]).sum())
        best = max(cands, key=score)
        DEPTH_MATCH[c] = (best[0], round(float(score(best)), 3))
        out[c] = k._fill_depth_holes(best[1].copy(), im)
    for base, ovs in OVERLAYS.items():          # an overlay uses its base's cell
        bc = int(copy_name(*base).rsplit("_", 1)[1])
        for n in ovs:
            oc = int(copy_name(OVL_SHEET, n).rsplit("_", 1)[1])
            out[oc] = k._fill_depth_holes(out[bc].copy(), tiles[oc][1])
    out.update(_countertop_depth_cells(tiles))
    return out


_VINDEX = None


def _vanilla_index():
    """[(sprite, props dict, sheet, idx)] for every vanilla tile with properties on a sheet with a depth map."""
    global _VINDEX
    if _VINDEX is None:
        import glob
        depth_sheets = {os.path.basename(p)[6:-4] for p in glob.glob(os.path.join(_VANILLA_DEPTHMAPS, "DEPTH_*.png"))}
        _VINDEX = []
        for f in glob.glob(os.path.join(_VANILLA_MEDIA, "tile_definitions", "*.tiles")) + glob.glob(os.path.join(_VANILLA_MEDIA, "*.tiles")):
            try:
                _v, ts, _o = k._parse(open(f, "rb").read())
            except Exception:
                continue
            for sheet, t in ts.items():
                sh = sheet.decode()
                if sh not in depth_sheets:
                    continue
                for i, pr in enumerate(t[6]):
                    if pr:
                        _VINDEX.append(("%s_%d" % (sh, i), {a.decode(): b.decode() for a, b in pr}, sh, i))
    return _VINDEX


def _batch2_kind(c, p):
    """Candidate filter for a batch-2 copy: a predicate over vanilla tile properties."""
    sh, i = COPIES[c]
    fc = p.get("Facing")
    if sh == VEG_SHEET:            # raised plants: vanilla plants (any), shifted to the raised art
        return lambda q: ("Plant" in (q.get("CustomName") or "") or "plant" in (q.get("GroupName") or "").lower()) \
            and "SpriteGridPos" not in q
    if sh == HW_SHEET:             # honeywood wardrobes / shop shelves: vanilla containers, same Facing
        return lambda q: q.get("Facing") == fc and "container" in q and "SpriteGridPos" not in q
    if sh == FURN2_SHEET and c in CAB_SRC:   # glass display cabinet: vanilla containers, same Facing
        return lambda q: q.get("Facing") == fc and "container" in q and "SpriteGridPos" not in q
    if sh == FURN2_SHEET and i in WINE_FACING:   # wine shelf: vanilla containers facing as the art
        wf = WINE_FACING[i]
        return lambda q: q.get("Facing") == wf and "container" in q and "SpriteGridPos" not in q
    if sh == FURN2_SHEET:          # 2-tile low tables: same Facing and grid position, a table
        return lambda q: (q.get("Facing") == fc and q.get("SpriteGridPos") == p.get("SpriteGridPos")
                          and "IsTable" in q)
    if sh == D1_SHEET and i in FIG_SRC:   # table-top figures: vanilla Surface-34 table-top pieces
        return lambda q: ("IsTableTop" in q and "IsSurfaceOffset" in q and q.get("Surface") == str(FIG_SURFACE_VALUE)
                          and "SpriteGridPos" not in q)
    if sh == D1_SHEET and i == DISCO_SRC:   # disco ball: vanilla's free-hanging indoor ceiling lights
        return lambda q: ("lightswitch" in q and "IsTableTop" not in q and "SpriteGridPos" not in q
                          and "attachedW" not in q and "attachedN" not in q and q.get("MoveType") != "WallObject"
                          and q.get("CustomName") in ("Lights", "Lamp"))
    if sh == D1_SHEET:             # floor statues: vanilla's free-standing statues / mannequins (centred)
        return lambda q: ("SpriteGridPos" not in q
                          and any(w in (q.get("CustomName") or "") for w in ("Statue", "Mannequin")))
    if "attachedN" in p or "attachedW" in p:      # hanging speakers: wall objects, same Facing
        return lambda q: (q.get("Facing") == fc and "SpriteGridPos" not in q
                          and ("attachedN" in q or "attachedW" in q or q.get("MoveType") == "WallObject"))
    return lambda q: q.get("Facing") == fc and "SpriteGridPos" not in q and "IsTableTop" not in q


def _batch2_depth_cells(tiles, src_props):
    """Depth for the batch-2 copies: the vanilla tile (filtered by _batch2_kind) whose art best overlaps,
    after lining up the bottoms of the two arts (raised figures match table-top pieces drawn lower);
    its depth cell is shifted by the same rows, then art holes are filled."""
    import numpy as np
    from PIL import Image
    out = {}
    for c in sorted(tiles):                     # neon: their wall's plane (corner: W left half, N right)
        if COPIES[c][0] == NEON_SHEET:
            wall = neon_wall(c)
            if wall == "C":
                w = np.array(k._wall_plane_depth("W", tiles[c][1], 2))
                n_ = np.array(k._wall_plane_depth("N", tiles[c][1], 2))
                w[:, 64:] = n_[:, 64:]
                out[c] = k._fill_depth_holes(Image.fromarray(w, "RGBA"), tiles[c][1])
            else:
                out[c] = k._wall_plane_depth(wall, tiles[c][1], 2)
            DEPTH_MATCH[c] = ("wall plane " + wall, 1.0)
    for c in sorted(tiles):                     # wall shelves: their wall's plane, 2 steps forward (TV margin)
        if c in SLOPED_REFLECT and COPIES[c][0] == F3_SHEET:     # reversed sloped shelves: their wall's plane
            out[c] = k._wall_plane_depth(SLOPED_WALL[COPIES[c]], tiles[c][1], 2)
            DEPTH_MATCH[c] = ("wall plane " + SLOPED_WALL[COPIES[c]], 1.0)
            continue
        if c in CHALK_W_COPIES:
            # 3rd pass: the dotted lines at the seams are the wall behind showing through on alternate rows
            # (the next square's wall tile reaches 2 columns into this one, at nearly equal depth). The art is
            # left as Simon drew it; the board sits CHALK_DEPTH_BIAS nearer, the gun rack's margin.
            out[c] = k._wall_plane_depth("W", tiles[c][1], CHALK_DEPTH_BIAS)
            DEPTH_MATCH[c] = ("wall plane W", 1.0)
        elif COPIES[c][0] == HW_SHEET and COPIES[c][1] in HW_WALL:
            out[c] = k._wall_plane_depth(HW_WALL[COPIES[c][1]], tiles[c][1], 2)
            DEPTH_MATCH[c] = ("wall plane " + HW_WALL[COPIES[c][1]], 1.0)
        elif COPIES[c][0] == HW_SHEET and COPIES[c][1] in HWF_WALL:
            out[c] = k._wall_plane_depth(HWF_WALL[COPIES[c][1]], tiles[c][1], 2)
            DEPTH_MATCH[c] = ("wall plane " + HWF_WALL[COPIES[c][1]], 1.0)
        elif c >= INWALL_COPY0 and COPIES[c][0] == FURN2_SHEET and COPIES[c][1] in INWALL_WALL:
            wall = INWALL_WALL[COPIES[c][1]]
            if wall == "P":
                # 3rd pass: bar corner shelves are boxes in the near half of their square (_contact_depth).
                # 4th pass (user, in game 2026-11-18, red overlay = the build ghost: the post draws over the
                # straight pieces on both sides): the left face still lost to the west neighbour near the
                # square's west edge. The whole post now stands at its front corner, BAR_POST_BIAS nearer
                out[c] = k._fill_depth_holes(_contact_depth(tiles[c][1], BAR_POST_BIAS, "flat"), tiles[c][1])
                DEPTH_MATCH[c] = ("box, flat at the front corner", 1.0)
                continue
            if wall in ("C", "P"):
                # inside corner: W wall plane on the left half, N on the right. Outer-corner pillar (on the
                # square's NW point, walls coming in from outside): the N plane continues to the left, the W
                # plane to the right
                pb = PILLAR_DEPTH_BIAS if wall == "P" else 2
                w = np.array(k._wall_plane_depth("W", tiles[c][1], pb))
                n_ = np.array(k._wall_plane_depth("N", tiles[c][1], pb))
                if wall == "C":
                    w[:, 64:] = n_[:, 64:]
                else:
                    n_[:, 64:] = w[:, 64:]
                    w = n_
                cell = k._fill_depth_holes(Image.fromarray(w, "RGBA"), tiles[c][1])
            else:
                cell = k._wall_plane_depth(wall, tiles[c][1], 2)
            out[c] = cell
            DEPTH_MATCH[c] = ("wall plane " + wall, 1.0)
    todo = [c for c in sorted(tiles) if c not in out and (COPIES[c][0] in (FURN2_SHEET, D2_SHEET, F3_SHEET, D1_SHEET, VEG_SHEET)
                                                           or (COPIES[c][0] == HW_SHEET and COPIES[c][1] in HWF_SRC))]
    if not todo:
        return out
    idx = _vanilla_index()
    kinds = {c: _batch2_kind(c, src_props[c]) for c in todo}
    cand = {c: [r for r in idx if kinds[c](r[1])] for c in todo}
    names = sorted({r[0] for rs in cand.values() for r in rs})
    cache = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_cache_vanilla_match")
    have = _pack_names(k._VANILLA_TILES2X)
    names = [n for n in names if n in have]
    k._extract_from_pack(k._VANILLA_TILES2X, names, cache)
    masks, dimgs = {}, {}

    def _cell_has_depth(sh, ci):
        if sh not in dimgs:
            dimgs[sh] = np.array(Image.open(os.path.join(_VANILLA_DEPTHMAPS, "DEPTH_%s.png" % sh)).convert("RGBA"))
        d = dimgs[sh]
        cols = d.shape[1] // 128
        cell = d[(ci // cols) * 256:(ci // cols + 1) * 256, (ci % cols) * 128:(ci % cols + 1) * 128, 3]
        return cell.shape == (256, 128) and bool(cell.any())

    def vmask(n):
        if n not in masks:
            p = os.path.join(cache, n + ".png")
            masks[n] = (np.array(Image.open(p).convert("RGBA"))[:, :, 3] > 40) if os.path.exists(p) else None
        return masks[n]

    def shift(a, dy):
        r = np.zeros_like(a)
        if dy > 0:
            r[dy:] = a[:-dy]
        elif dy < 0:
            r[:dy] = a[-dy:]
        else:
            r[:] = a
        return r
    for c in todo:
        if COPIES[c] == (D1_SHEET, DISCO_SRC):
            out[c] = _hanging_depth(tiles[c][1])
            DEPTH_MATCH[c] = ("vertical line through the square's centre", 1.0)
            continue
        if COPIES[c][0] == D2_SHEET and COPIES[c][1] in SPK_WALL:
            out[c] = k._wall_plane_depth(SPK_WALL[COPIES[c][1]], tiles[c][1], 2)
            DEPTH_MATCH[c] = ("wall plane " + SPK_WALL[COPIES[c][1]], 1.0)
            continue
        art = np.array(tiles[c][1])[:, :, 3] > 40
        ab = int(np.nonzero(art.any(axis=1))[0].max())
        # floor pieces stand on the floor like their match: only small shifts; figures are raised
        is_fig = COPIES[c][0] == D1_SHEET and COPIES[c][1] in FIG_SRC
        is_statue = COPIES[c][0] == D1_SHEET and COPIES[c][1] in STATUE_SRC
        max_dy = 40 if (is_statue or (COPIES[c] == (D1_SHEET, DISCO_SRC))) else 90 if COPIES[c][0] == VEG_SHEET else 8
        best = None
        for sprite, _q, sh, i in cand[c]:
            m = vmask(sprite)
            if m is None or not m.any():
                continue
            ci = k._vanilla_depth_cell_index(sh, i)
            if ci is None or not _cell_has_depth(sh, ci):
                continue
            dy = ab - int(np.nonzero(m.any(axis=1))[0].max())
            if abs(dy) > max_dy:
                continue
            ms = shift(m, dy)
            s = (art & ms).sum() / max(1, (art | ms).sum())
            if best is None or s > best[0]:
                best = (s, sprite, sh, ci, dy)
        if best is None:
            raise RuntimeError("no vanilla depth candidate for copy %d %s" % (c, COPIES[c]))
        s, sprite, sh, ci, dy = best
        if sh not in dimgs:
            dimgs[sh] = np.array(Image.open(os.path.join(_VANILLA_DEPTHMAPS, "DEPTH_%s.png" % sh)).convert("RGBA"))
        d = dimgs[sh]
        cols = d.shape[1] // 128
        cell = d[(ci // cols) * 256:(ci // cols + 1) * 256, (ci % cols) * 128:(ci % cols + 1) * 128].copy()
        if cell.shape[:2] != (256, 128) or not cell[:, :, 3].any():
            raise RuntimeError("empty vanilla depth cell %s for copy %d" % (sprite, c))
        cell = shift(cell, dy)
        if is_fig:     # trimmed to the art (no depth where nothing is drawn), then nearer the viewer
            cell[~art] = 0
            on = cell[:, :, 3] > 0
            for ch in range(3):
                v = cell[:, :, ch].astype(int)
                v[on] = np.clip(v[on] - FIG_DEPTH_BIAS, 0, 255)
                cell[:, :, ch] = v.astype(np.uint8)
        DEPTH_MATCH[c] = (sprite + ("" if dy == 0 else " dy%+d" % dy), round(float(s), 3))
        out[c] = k._fill_depth_holes(Image.fromarray(cell, "RGBA"), tiles[c][1])
    return out


def _contact_depth(art, bias=2, contact="art"):
    """Depth for a free-standing box: every column is a vertical face standing where that column's lowest
    art pixel meets the floor. Floor depth there (vanilla: 637 - 2y) plus the vertical depth gradient of
    vanilla's wall planes (their least-squares fit), `bias` steps nearer. (Bar corner shelves, user in game
    2026-11-17: they are boxes filling the near half of their square, front corner 26 rows in front of the
    corner point; the corner-point wall planes put them ~50 steps too far back.)
    contact: "art" = each column's own lowest pixel; "flat" = every column at the art's lowest (front-most)
    row, a face standing at the front corner (nothing of the piece is farther than its front corner);
    "front" = each column at the square's front edges (the diamond's lower edges, y = 224 + x/2 left of
    the centre, 224 + (128 - x)/2 right of it): the nearest a full-square box can be."""
    import numpy as np
    from PIL import Image
    a0, b0, c0 = _floor_plane()
    pre = np.array(Image.open(k._VANILLA_DEPTH_PRESET).convert("RGBA")).astype(float)
    pcols = pre.shape[1] // 128
    cell = pre[(4 // pcols) * 256:(4 // pcols + 1) * 256, (4 % pcols) * 128:(4 % pcols + 1) * 128]
    ys, xs = np.nonzero(cell[:, :, 3] == 255)
    A = np.stack([xs, ys, np.ones_like(xs)], axis=1).astype(float)
    (_ca, cb, _cc), *_ = np.linalg.lstsq(A, cell[ys, xs, 0], rcond=None)
    a = np.array(art.convert("RGBA"))
    on = a[:, :, 3] > 0
    out = np.zeros_like(a)
    y_flat = int(np.nonzero(on.any(axis=1))[0].max())
    for x in np.nonzero(on.any(axis=0))[0]:
        if contact == "flat":
            yb = y_flat
        elif contact == "front":
            yb = int(round(224 + (x if x < 64 else 128 - x) / 2.0))
        else:
            yb = int(np.nonzero(on[:, x])[0].max())
        d0 = a0 * x + b0 * yb + c0
        v = np.clip(np.rint(d0 + cb * (np.arange(256) - yb)) - bias, 0, 255).astype(np.uint8)
        m = on[:, x]
        for ch in range(3):
            out[m, x, ch] = v[m]
        out[m, x, 3] = 255
    return Image.fromarray(out, "RGBA")


def _box_depth(art, lift, bias=2):
    """Depth for a box filling its square with a flat top `lift` rows above the floor (the raised planter
    beds). A pixel at (x, y) is on a front face when y >= yf - lift (yf = the square's front edge under
    column x, y = 224 + x/2 left of the centre, 224 + (128 - x)/2 right of it): the face standing on yf,
    as _contact_depth "front". Above that it is on the top: the point `lift` rows above the floor point
    (x, y + lift), whose depth is the floor's there plus the vertical gradient over `lift` rows (the same
    encoding as the faces). `bias` steps nearer."""
    import numpy as np
    from PIL import Image
    a0, b0, c0 = _floor_plane()
    pre = np.array(Image.open(k._VANILLA_DEPTH_PRESET).convert("RGBA")).astype(float)
    pcols = pre.shape[1] // 128
    cell = pre[(4 // pcols) * 256:(4 // pcols + 1) * 256, (4 % pcols) * 128:(4 % pcols + 1) * 128]
    ys, xs = np.nonzero(cell[:, :, 3] == 255)
    A = np.stack([xs, ys, np.ones_like(xs)], axis=1).astype(float)
    (_ca, cb, _cc), *_ = np.linalg.lstsq(A, cell[ys, xs, 0], rcond=None)
    a = np.array(art.convert("RGBA"))
    on = a[:, :, 3] > 0
    yy, xx = np.mgrid[0:256, 0:128].astype(float)
    yf = 224 + np.minimum(xx, 128 - xx) / 2.0
    front = a0 * xx + b0 * yf + c0 + cb * (yy - yf)
    top = a0 * xx + b0 * (yy + lift) + c0 - cb * lift
    d = np.where(yy >= yf - lift, front, top)
    v = np.clip(np.rint(d) - bias, 0, 255).astype(np.uint8)
    out = np.zeros_like(a)
    for ch in range(3):
        out[:, :, ch] = np.where(on, v, 0)
    out[:, :, 3] = np.where(on, 255, 0)
    return Image.fromarray(out, "RGBA")


FLOOR_CLAMP_BIAS = 2         # steps nearer than the floor under the pixel
_FLOOR_PLANE = []


def _floor_plane():
    """(a, b, c): vanilla floor depth = a*x + b*y + c over the floor diamond (fit of the rug cell; exact,
    a = 0, b = -2, c = 637)."""
    import numpy as np
    from PIL import Image
    if not _FLOOR_PLANE:
        rsh, ri = WEDGE_DEPTH_FROM
        rd = np.array(Image.open(os.path.join(_VANILLA_DEPTHMAPS, "DEPTH_%s.png" % rsh)).convert("RGBA")).astype(float)
        rci = k._vanilla_depth_cell_index(rsh, ri)
        cols = rd.shape[1] // 128
        rug = rd[(rci // cols) * 256:(rci // cols + 1) * 256, (rci % cols) * 128:(rci % cols + 1) * 128]
        ys, xs = np.nonzero(rug[:, :, 3] == 255)
        A = np.stack([xs, ys, np.ones_like(xs)], axis=1).astype(float)
        coef, *_ = np.linalg.lstsq(A, rug[ys, xs, 0], rcond=None)
        _FLOOR_PLANE.extend(float(v) for v in coef)
    return tuple(_FLOOR_PLANE)


def _floor_clamp(cell):
    """No pixel of something standing on (or above) the floor may be behind the floor it is drawn over:
    depth <= floor depth at that pixel - FLOOR_CLAMP_BIAS. Only rows over the floor (y >= 192) can change.
    Wall-plane depth extended below the wall's foot (the bar corner shelf's base) was behind the floor."""
    import numpy as np
    from PIL import Image
    a, b, c0 = _floor_plane()
    d = np.array(cell.convert("RGBA")).astype(int)
    yy, xx = np.mgrid[0:256, 0:128]
    cap = np.rint(a * xx + b * yy + c0).astype(int) - FLOOR_CLAMP_BIAS
    on = d[:, :, 3] > 0
    for ch in range(3):
        v = d[:, :, ch]
        d[:, :, ch] = np.where(on & (v > cap), np.clip(cap, 0, 255), v)
    return Image.fromarray(d.astype(np.uint8), "RGBA")


TT_CAP_FROM_ROW = 140        # table-top figures: only their lower part is capped
TT_CAP_PCT = 90              # cap = this percentile of vanilla's table-top depth at the row
_TT_CAP = {}


def _tabletop_row_cap():
    """{row: depth cap} from vanilla's Surface-34 table-top pieces (IsTableTop + IsSurfaceOffset): the
    TT_CAP_PCT percentile of their depth over all art pixels of each row >= TT_CAP_FROM_ROW, made
    non-increasing downwards (lower on screen = nearer). Placed on the floor, vanilla's pieces draw in
    front of it; ours, with depth borrowed from a piece of another shape, had the lowest rows of the
    stargate's DHD and stairs up to 30 steps farther (and one pixel at 253), and sank into the ground."""
    import json as _json
    import numpy as np
    from PIL import Image
    if _TT_CAP:
        return _TT_CAP
    cache = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_cache_vanilla_match")
    fp = os.path.join(cache, "_tt_row_cap_%d_%d.json" % (TT_CAP_FROM_ROW, TT_CAP_PCT))
    if os.path.isfile(fp):
        _TT_CAP.update({int(r): v for r, v in _json.load(open(fp)).items()})
        return _TT_CAP
    cand = [r for r in _vanilla_index() if "IsTableTop" in r[1] and "IsSurfaceOffset" in r[1]
            and r[1].get("Surface") == str(FIG_SURFACE_VALUE)]
    have = _pack_names(k._VANILLA_TILES2X)
    names = [r[0] for r in cand if r[0] in have]
    k._extract_from_pack(k._VANILLA_TILES2X, names, cache)
    dimgs, per_row = {}, {}
    for sprite, _q, sh, i in cand:
        p = os.path.join(cache, sprite + ".png")
        ci = k._vanilla_depth_cell_index(sh, i)
        if not os.path.exists(p) or ci is None:
            continue
        if sh not in dimgs:
            dp = os.path.join(_VANILLA_DEPTHMAPS, "DEPTH_%s.png" % sh)
            dimgs[sh] = np.array(Image.open(dp).convert("RGBA")).astype(int) if os.path.exists(dp) else None
        d = dimgs[sh]
        if d is None:
            continue
        cols = d.shape[1] // 128
        cell = d[(ci // cols) * 256:(ci // cols + 1) * 256, (ci % cols) * 128:(ci % cols + 1) * 128]
        if cell.shape[:2] != (256, 128):
            continue
        art = (np.array(Image.open(p).convert("RGBA"))[:, :, 3] > 40) & (cell[:, :, 3] > 0)
        ys, xs = np.nonzero(art)
        for y, v in zip(ys, cell[ys, xs, 0]):
            if y >= TT_CAP_FROM_ROW:
                per_row.setdefault(int(y), []).append(int(v))
    cap, run = {}, None
    for y in sorted(per_row):
        if len(per_row[y]) < 50:
            continue
        v = int(np.percentile(per_row[y], TT_CAP_PCT))
        run = v if run is None else min(run, v)
        cap[y] = run
    _json.dump(cap, open(fp, "w"))
    _TT_CAP.update(cap)
    return _TT_CAP


def _tabletop_clamp(cell):
    """Table-top figure depth: rows >= TT_CAP_FROM_ROW no farther than vanilla's (_tabletop_row_cap),
    less FIG_DEPTH_BIAS; rows below vanilla's lowest sampled row take that row's cap."""
    import numpy as np
    from PIL import Image
    cap = _tabletop_row_cap()
    d = np.array(cell.convert("RGBA")).astype(int)
    on = d[:, :, 3] > 0
    last = None
    for y in range(TT_CAP_FROM_ROW, 256):
        if y in cap:
            last = cap[y]
        if last is None:
            continue
        lim = last - FIG_DEPTH_BIAS
        for ch in range(3):
            row = d[y, :, ch]
            d[y, :, ch] = np.where(on[y] & (row > lim), lim, row)
    return Image.fromarray(np.clip(d, 0, 255).astype(np.uint8), "RGBA")


def _hanging_depth(art):
    """Depth for something hanging in the middle of the square (the disco ball): every pixel at the depth of
    a vertical line through the square's centre. Floor depth at the centre (vanilla's rug cell, pixel 64,224)
    plus the vertical depth gradient of vanilla's wall planes (their least-squares fit). 2 steps nearer."""
    import numpy as np
    from PIL import Image
    rsh, ri = WEDGE_DEPTH_FROM
    rd = np.array(Image.open(os.path.join(_VANILLA_DEPTHMAPS, "DEPTH_%s.png" % rsh)).convert("RGBA")).astype(float)
    rci = k._vanilla_depth_cell_index(rsh, ri)
    cols = rd.shape[1] // 128
    rug = rd[(rci // cols) * 256:(rci // cols + 1) * 256, (rci % cols) * 128:(rci % cols + 1) * 128]
    d0 = rug[224, 64, 0]
    pre = np.array(Image.open(k._VANILLA_DEPTH_PRESET).convert("RGBA")).astype(float)
    pcols = pre.size[0] // 128 if hasattr(pre, "size") and not isinstance(pre.size, int) else pre.shape[1] // 128
    cell = pre[(4 // pcols) * 256:(4 // pcols + 1) * 256, (4 % pcols) * 128:(4 % pcols + 1) * 128]
    ys, xs = np.nonzero(cell[:, :, 3] == 255)
    A = np.stack([xs, ys, np.ones_like(xs)], axis=1).astype(float)
    (_ca, cb, _cc), *_ = np.linalg.lstsq(A, cell[ys, xs, 0], rcond=None)
    a = np.array(art.convert("RGBA"))
    out = np.zeros_like(a)
    yy = np.arange(256)
    v = np.clip(np.rint(d0 + cb * (yy - 224)) - 2, 0, 255).astype(np.uint8)
    on = a[:, :, 3] > 0
    for ch in range(3):
        out[:, :, ch] = np.where(on, v[:, None], 0)
    out[:, :, 3] = np.where(on, 255, 0)
    return Image.fromarray(out, "RGBA")


def _pack_names(pack):
    import struct
    out = set()
    with open(pack, "rb") as f:
        def i32():
            return struct.unpack("<i", f.read(4))[0]

        def s():
            return f.read(i32()).decode("utf-8", "replace")
        assert f.read(4) == b"PZPK" and i32() == 1
        for _ in range(i32()):
            s(); nent = i32(); i32()
            for _e in range(nent):
                out.add(s()); f.read(32)
            f.seek(i32(), 1)
    return out


def _countertop_depth_cells(tiles):
    """Counter tops: the depth cell of the vanilla counter shape each one sits on, so the top draws at
    the counter's own depth. Vanilla does the same for its counter overlays (tileDepthTextureAssignments:
    fixtures_overlay_counters_01_* = fixtures_counters_01_0). Drawn as an attached sprite straight after
    the counter, it then covers the counter and loses to anything placed on it (a sink)."""
    from PIL import Image
    sheet = "fixtures_counters_01"
    d = Image.open(os.path.join(_VANILLA_DEPTHMAPS, "DEPTH_%s.png" % sheet)).convert("RGBA")
    cols = d.size[0] // 128
    out = {}
    for c in sorted(tiles):
        if COPIES[c][0] != CT_SHEET:
            continue
        shape = (COPIES[c][1] - CT_FIRST_SRC) % 8
        ci = k._vanilla_depth_cell_index(sheet, CT_SHAPE_COUNTER[shape])
        cell = d.crop(((ci % cols) * 128, (ci // cols) * 256, (ci % cols) * 128 + 128, (ci // cols) * 256 + 256))
        DEPTH_MATCH[c] = ("%s_%d" % (sheet, ci), 1.0)
        out[c] = k._fill_depth_holes(cell, tiles[c][1])
    return out


def _art_bottom(im):
    import numpy as np
    rows = np.nonzero((np.array(im)[:, :, 3] > 40).any(axis=1))[0]
    return int(rows.max()) if len(rows) else None


def _copy_props(ts, sh, i, im):
    """[(name, value)] tile properties of a copy (str pairs, the pack's order where it has one)."""
    if sh in (OVL_SHEET, CT_SHEET):
        return []                                            # overlays: no properties, as vanilla's
    if (sh, i) in PROPS_EXTRA:
        return list(PROPS_EXTRA[(sh, i)].items())
    if sh == VEG_SHEET and i in BED_OF_TILE:                 # raised beds: a table surface at soil height
        return [(a.decode(), b.decode()) for a, b in ts[sh.encode()][6][i]
                if a not in (b"IsTable", b"Surface", b"IsSurfaceOffset", b"IsTableTop")] \
            + [("IsTable", ""), ("Surface", BED_SURFACE[BED_OF_TILE[i]])]
    if sh == VEG_SHEET and (i in FLOWER_SRC or i in PLANT_SRC):   # flowers, plants: the game's table-top mechanic
        return [(a.decode(), b.decode()) for a, b in ts[sh.encode()][6][i] if a not in (b"BlocksPlacement",)] \
            + [("IsTableTop", "")]
    if sh == VEG_SHEET:                                      # raised plants: placeable onto a planter
        return [(a.decode(), b.decode()) for a, b in ts[sh.encode()][6][i] if a not in (b"BlocksPlacement",)]
    if sh == HW_SHEET and i in HWF_SRC:                      # honeywood furniture: the pack's list
        pairs = [(a.decode(), b.decode()) for a, b in ts[sh.encode()][6][i]]
        facing = dict(pairs).get("Facing")
        if facing == "S":                                    # shop shelves: attachedW on the N-wall tile
            pairs = [("attachedN" if a == "attachedW" else a, b) for a, b in pairs]
        if i in BENCH_SRC:                                   # wall bench: a seat, like vanilla chairs
            pairs = [(a, b) for a, b in pairs if a not in ("IsTable", "Surface")]
            pairs += [("bed", ""), ("chair" + facing, ""), ("BedType", "averageBed")]
        return pairs
    if sh == HW_SHEET:                                       # wall shelves: own Facing, walk-through
        facing = "E" if HW_WALL[i] == "W" else "S"
        pairs = [(a.decode(), b.decode()) for a, b in ts[sh.encode()][6][i]]
        return [(a, facing if a == "Facing" else b) for a, b in pairs if a not in ("solidtrans", "solid", "IsLow")]
    pairs = [(a.decode(), b.decode()) for a, b in ts[sh.encode()][6][i]]
    if sh == NEON_SHEET:                                     # neon: lit sprite, own colour, no streetlight
        if i in NEON_STRIPS:
            wall, rgb = neon_role(i)
        elif i in (40, 41):
            wall, rgb = ("W" if i == 40 else "N"), NEON_PINK
        else:
            wall, rgb = ("W" if i in (42, 43) else "N"), NEON_WHITE
        drop = (b"streetlight", b"Facing", b"lightR", b"lightG", b"lightB", b"solid", b"solidtrans")
        pairs = [(a.decode(), b.decode()) for a, b in ts[sh.encode()][6][i] if a not in drop]
        if wall in ("W", "N"):
            pairs.append(("Facing", "E" if wall == "W" else "S"))
        if i in NEON_SIGN_GRID:
            # "The Italian Bowl" (user, in game 2026-11-17: each half lit on its own, like the TikiTown 2-tile
            # wall light): the game links a multi-tile light (one toggle switches every tile) only when each
            # tile of its GroupName + CustomName + Facing group has SpriteGridPos (IsoWorld.LoadTileDefinitions)
            pairs = [(a, b) for a, b in pairs if a not in ("CustomName", "GroupName", "SpriteGridPos")]
            pairs += [("CustomName", "Neon Sign"), ("GroupName", "Italian Bowl"), ("SpriteGridPos", NEON_SIGN_GRID[i])]
        # IsMoveAble (user, in game 2026-11-17: the switch clicked but gave no light): the engine's IsoLightSwitch
        # sets canBeModified from IsMoveAble, and setActive returns early for a light that cannot be modified on
        # a square outside a map room (KnoxBuildworks/World/LightSwitches.lua). The working lamps (Tsargate, disco
        # ball, TikiTown neon) all have it; the pack's neon tiles do not.
        if "IsMoveAble" not in dict(pairs):
            pairs += [("IsMoveAble", ""), ("PickUpWeight", "10")]
        return pairs + [("lightR", rgb[0]), ("lightG", rgb[1]), ("lightB", rgb[2]), ("HasLightOnSprite", "")]
    if (sh, i) == (D1_SHEET, DISCO_SRC):                     # disco ball: its pack light + a lit sprite
        pairs = [(a.decode(), b.decode()) for a, b in ts[sh.encode()][6][i] if a not in (b"solid", b"solidtrans")]
        return pairs + [("HasLightOnSprite", "")]
    if (sh, i) in WALKABLE_COPY_SHEETS:                      # low tables / floor statues: walk-through
        return [(a.decode(), b.decode()) for a, b in ts[sh.encode()][6][i] if a not in (b"solid", b"solidtrans")]
    if sh == D1_SHEET and i in FIG_SRC:                      # figures: vanilla table-top Surface (art moved)
        surface = FIG_SURFACE_VALUE
        FIG_SURFACE[i] = surface
        pairs = [(a, b) for a, b in pairs if a not in FIG_DROP and a not in ("Surface", "IsTableTop", "IsSurfaceOffset", "TileOverlay")]
        pairs += [("IsTableTop", ""), ("IsSurfaceOffset", ""), ("Surface", str(surface))]
        if i == GATE_SRC:                                    # a vanilla table lamp's light flags
            pairs += [("lightswitch", ""), ("HasLightOnSprite", ""), ("BlocksPlacement", "")]
            pairs += list(GATE_LIGHT.items())
    return pairs


def write_copy_assets(media_dir, common_media_dir=None):
    """Write texturepacks/KBWRavenCreek.pack + kbwravencreek.tiles into media_dir, and the depth map
    (+ the minimal tileGeometry.txt the depth loader needs) into common_media_dir. Returns tile count."""
    import struct
    import numpy as np
    from PIL import Image
    cache = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_cache_simonmd")
    k._extract_from_pack(RC_PACK, sorted({_s(sh, i) for sh, i in COPIES.values() if (sh, i) not in FROM_STANDALONE}), cache)
    std_want = {_s(sh, i) for sh, i in FROM_STANDALONE}
    for p in _standalone_packs():                    # art Raven Creek lacks, from the full Simon MD pack
        have = _pack_names(p) & std_want
        if have:
            k._extract_from_pack(p, sorted(have), cache)
            std_want -= have
    if std_want:
        raise RuntimeError("not in the standalone Simon MD pack: %s" % sorted(std_want))
    _v, ts, _o = k._parse(open(RC_TILES, "rb").read())
    tiles, src_props = {}, {}
    for c in sorted(COPIES):
        sh, i = COPIES[c]
        im = Image.open(os.path.join(cache, _s(sh, i) + ".png")).convert("RGBA")
        if sh == CT_SHEET:                                           # stray pixel(s) above the top
            px = im.load()
            for y in range(_CT_STRAY_ROWS):
                for x in range(im.size[0]):
                    px[x, y] = (0, 0, 0, 0)
        tiles[c] = ("%s_%d" % (COPY_TILESET, c), im)
        if c in CHALK_W_COPIES:                                      # W-wall chalkboard: no seam lines
            im = chalk_seam_fix(im, CHALK_SEAM_SIDES[c])
            tiles[c] = ("%s_%d" % (COPY_TILESET, c), im)
        if c in FLOWER_COPIES or c in PLANT_COPIES:                  # flowers, plants: no halo / drop shadow
            a = np.array(im).astype(int)
            lum = a[:, :, :3].mean(axis=2)
            clear = (a[:, :, 3] < FIG_ALPHA_MIN) | ((a[:, :, 3] < 250) & (lum < FLOWER_SHADOW_LUM))
            a[clear] = 0
            im = Image.fromarray(a.astype(np.uint8), "RGBA")
            tiles[c] = ("%s_%d" % (COPY_TILESET, c), im)
        if c in SLOPED_REFLECT:                                      # reversed sloped shelves
            im = _wall_reflect(im, SLOPED_WALL[(sh, i)])
            tiles[c] = ("%s_%d" % (COPY_TILESET, c), im)
        drop = OVL_ROW_SHIFT.get((sh, i)) or (FLOWER_DROP_ROWS.get(i) if c in FLOWER_COPIES else None)
        if c in SLOPED_REFLECT:
            drop = None
        if drop:                                                     # art drawn off its base / raised flowers
            a = np.array(im)
            dy = drop
            out = np.zeros_like(a)
            out[dy:] = a[:a.shape[0] - dy]
            im = Image.fromarray(out, "RGBA")
            tiles[c] = ("%s_%d" % (COPY_TILESET, c), im)
        if sh == D1_SHEET and i in FIG_SRC:                          # vanilla table-top height, no halo / shadow
            raw = im
            im = _figure_art(gate_off_art(raw), ref=raw) if i == GATE_SRC else _figure_art(raw)
            tiles[c] = ("%s_%d" % (COPY_TILESET, c), im)
        if (sh, i) == (D1_SHEET, DISCO_SRC):                         # unlit disco ball: dimmed
            a = np.array(im).astype(float)
            a[:, :, :3] *= DISCO_DIM
            im = Image.fromarray(a.astype(np.uint8), "RGBA")
            tiles[c] = ("%s_%d" % (COPY_TILESET, c), im)
        pairs = _copy_props(ts, sh, i, im)
        if c in NEON_COLOR_COPIES:                                   # recoloured neon: its bulb's light
            rgb = NEON_COLOR_INFO[NEON_COLOR_COPIES[c][1]][1]
            pairs = [(a, {"lightR": rgb[0], "lightG": rgb[1], "lightB": rgb[2]}.get(a, b)) for a, b in pairs]
        src_props[c] = dict(pairs)
        tiles[c] = tiles[c] + (pairs,)
    vcache = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_cache_vanilla_match")
    k._extract_from_pack(k._VANILLA_TILES2X, sorted({t for sets in BOOK_SETS.values() for pair in sets for t in pair}),
                         vcache)
    k._extract_from_pack(RC_PACK, ["%s_%d" % (FLOOR_SHEET, i) for n in WEDGE_WOOD + WEDGE_CARPET for i in (n, n + 16)],
                         cache)
    load = lambda i: Image.open(os.path.join(cache, "%s_%d.png" % (FLOOR_SHEET, i))).convert("RGBA")
    wedge_props = [(a.decode(), b.decode()) for a, b in ts[FLOOR_SHEET.encode()][6][0]]
    for c, (n, face) in sorted(WEDGE_COPIES.items()):             # floor wedges
        tiles[c] = ("%s_%d" % (COPY_TILESET, c), _wedge_art(n, face, load), wedge_props)
        src_props[c] = dict(wedge_props)
    for c, (base, si, ti) in sorted(GEN_COPIES.items()):          # re-laid vanilla books (shelf_relayout.py)
        bc = int(copy_name(*base).rsplit("_", 1)[1])
        im = _book_overlay(tiles[bc][1], base, si, ti, vcache)
        tiles[c] = ("%s_%d" % (COPY_TILESET, c), im, [])
        src_props[c] = {}
    mirrors, lit = {}, {}
    gate_raw = Image.open(os.path.join(cache, _s(D1_SHEET, GATE_SRC) + ".png")).convert("RGBA")
    lit[int(copy_name(D1_SHEET, GATE_SRC).rsplit("_", 1)[1])] = _figure_art(gate_raw)
    lit[DISCO_COPY] = Image.open(os.path.join(cache, _s(D1_SHEET, DISCO_SRC) + ".png")).convert("RGBA")
    # neon: unlit = the pack tile(s), lit = their lighting_Simon_MD_on partners; the sign's three colour
    # layers merged into one tile per square
    neon_srcs = sorted({n for c, (sh, n) in COPIES.items() if sh == NEON_SHEET} | {n for ls in NEON_SIGN.values() for n in ls})
    k._extract_from_pack(RC_PACK, ["%s_%d" % (s_, n) for n in neon_srcs for s_ in (NEON_SHEET, NEON_ON_SHEET)], cache)

    def _stack(sheet, layers):
        out = Image.new("RGBA", (128, 256), (0, 0, 0, 0))
        for n in layers:
            out.alpha_composite(Image.open(os.path.join(cache, "%s_%d.png" % (sheet, n))).convert("RGBA"))
        return out
    for c, (sh, n) in COPIES.items():
        if sh != NEON_SHEET:
            continue
        layers = NEON_SIGN.get(c, (n,))
        if n in NEON_STRIPS and c not in NEON_SIGN:      # strips: joins made whole (neon_seam_fix)
            un = neon_seam_fix(n, lambda m: _stack(NEON_SHEET, (m,)))
            on = neon_seam_fix(n, lambda m: _stack(NEON_ON_SHEET, (m,)))
        else:
            un, on = _stack(NEON_SHEET, layers), _stack(NEON_ON_SHEET, layers)
        tiles[c] = ("%s_%d" % (COPY_TILESET, c), un, tiles[c][2])
        lit[c] = on
        if c in NEON_COLOR_COPIES:
            slug = NEON_COLOR_COPIES[c][1]
            tiles[c] = (tiles[c][0], neon_recolor(tiles[c][1], slug), tiles[c][2])
            lit[c] = neon_recolor(lit[c], slug)
    for c, (sh, i) in sorted(MIRROR_COPIES.items()):             # mirrored copies: art flipped, Facing E <-> S
        raw = Image.open(os.path.join(cache, _s(sh, i) + ".png")).convert("RGBA")
        if sh == D1_SHEET and i in FIG_SRC:                      # figures: from the figure art
            base = _figure_art(gate_off_art(raw), ref=raw) if i == GATE_SRC else _figure_art(raw)
            if i == GATE_SRC:
                lit[c] = _figure_art(raw).transpose(Image.FLIP_LEFT_RIGHT)
        else:
            base = raw
        im = base.transpose(Image.FLIP_LEFT_RIGHT)
        swap = {"E": "S", "S": "E", "N": "W", "W": "N"}
        pairs = [(a, swap.get(b, b) if a == "Facing" else b) for a, b in _copy_props(ts, sh, i, im)]
        mirrors[c] = ("%s_%d" % (COPY_TILESET, c), im, pairs)
    # raised-bed copies (BED_TILESET): the pack art, a table surface at soil height
    k._extract_from_pack(RC_PACK, sorted({_s(VEG_SHEET, n) for _h, n in BED_COPIES.values()}), cache)
    beds = {c: Image.open(os.path.join(cache, _s(VEG_SHEET, n) + ".png")).convert("RGBA")
            for c, (_h, n) in BED_COPIES.items()}
    n = k._write_pack(os.path.join(media_dir, "texturepacks", COPY_PACK + ".pack"), COPY_PACK + "0",
                      [v[:2] for _c, v in sorted(list(tiles.items()) + list(mirrors.items()))]
                      + [("%s_%d" % (LIGHT_ON_TILESET, c), im) for c, im in sorted(lit.items())]
                      + [("%s_%d" % (BED_TILESET, c), im) for c, im in sorted(beds.items())])
    cols = 8
    rows = max(list(tiles) + list(mirrors)) // cols + 1
    if cols * rows > TILESET_MAX:
        raise RuntimeError("%s would have %d tiles; the game allows %d per tileset" % (COPY_TILESET, cols * rows, TILESET_MAX))
    props = [[] for _ in range(cols * rows)]
    for c in tiles:
        sh, i = COPIES[c] if c in COPIES else (None, None)
        if c in GEN_COPIES:
            props[c] = []
        elif c in WEDGE_COPIES:
            props[c] = [(a.encode(), b.encode()) for a, b in tiles[c][2]]
        elif sh in (FURN_SHEET, DOOR_SHEET) and c < 28:   # batch 1 copies: the pack's list without solid / solidtrans
            props[c] = [(a, b) for a, b in ts[sh.encode()][6][i] if a not in _COPY_DROP]
        else:
            props[c] = [(a.encode(), b.encode()) for a, b in tiles[c][2]]
    for c, v in mirrors.items():
        props[c] = [(a.encode(), b.encode()) for a, b in v[2]]
    tiles = {c: v[:2] for c, v in tiles.items()}
    t = [COPY_TILESET.encode(), (COPY_TILESET + ".png").encode(), cols, rows, 1, cols * rows, props]
    # the lit-state tileset: same grid, no properties (the game shows <tileset>_on_<i> for a lit
    # HasLightOnSprite tile), as the TikiTown lights do
    t_on = [LIGHT_ON_TILESET.encode(), (LIGHT_ON_TILESET + ".png").encode(), cols, rows, 2, cols * rows,
            [[] for _ in range(cols * rows)]]
    brows = (max(BED_COPIES) // cols + 1) if BED_COPIES else 0
    if BED_COPIES:
        bprops = [[] for _ in range(cols * brows)]
        for c, (_h, bn) in BED_COPIES.items():
            bprops[c] = [(a.encode(), b.encode()) for a, b in _copy_props(ts, VEG_SHEET, bn, beds[c])]
        t_bed = [BED_TILESET.encode(), (BED_TILESET + ".png").encode(), cols, brows, 3, cols * brows, bprops]
        blob = (b"tdef" + struct.pack("<ii", 1, 3) + k._ser_tileset(t) + k._ser_tileset(t_on)
                + k._ser_tileset(t_bed))
    else:
        blob = b"tdef" + struct.pack("<ii", 1, 2) + k._ser_tileset(t) + k._ser_tileset(t_on)
    k._parse(blob)
    open(os.path.join(media_dir, COPY_TILEDEF_NAME + ".tiles"), "wb").write(blob)
    if common_media_dir:
        cells = _depth_cells({c: v for c, v in tiles.items() if c not in GEN_COPIES and c not in WEDGE_COPIES},
                             src_props)
        rsh, ri = WEDGE_DEPTH_FROM                               # floor wedges: the rug cell, trimmed
        rd = np.array(Image.open(os.path.join(_VANILLA_DEPTHMAPS, "DEPTH_%s.png" % rsh)).convert("RGBA"))
        rci = k._vanilla_depth_cell_index(rsh, ri)
        rcols = rd.shape[1] // 128
        rug = rd[(rci // rcols) * 256:(rci // rcols + 1) * 256, (rci % rcols) * 128:(rci % rcols + 1) * 128]
        for c in WEDGE_COPIES:
            cell = rug.copy()
            cell[np.array(tiles[c][1])[:, :, 3] == 0] = 0
            cells[c] = k._fill_depth_holes(Image.fromarray(cell, "RGBA"), tiles[c][1])
        for c, (base, _si, _ti) in GEN_COPIES.items():          # re-laid books: their shelf's cell
            bc = int(copy_name(*base).rsplit("_", 1)[1])
            if np.array(tiles[c][1])[:, :, 3].any():
                cells[c] = k._fill_depth_holes(cells[bc].copy(), tiles[c][1])
        for c, (sh, i) in MIRROR_COPIES.items():                # a mirror's depth = its original's, flipped
            oc = int(copy_name(sh, i).rsplit("_", 1)[1])
            cells[c] = k._fill_depth_holes(cells[oc].transpose(Image.FLIP_LEFT_RIGHT), mirrors[c][1])
            DEPTH_MATCH[c] = ("mirror of %d" % oc, DEPTH_MATCH.get(oc, ("", 0))[1])
        for base, ovs in (SLOPED_OVERLAYS.items() if SLOPED_REFLECT else ()):   # (reversed shelves: removed)
            bc = int(reflect_copy_name(*base).rsplit("_", 1)[1])
            for n in ovs:
                oc = int(reflect_copy_name(OVL_SHEET, n).rsplit("_", 1)[1])
                cells[oc] = k._fill_depth_holes(cells[bc].copy(), tiles[oc][1])
        # bottoms sinking into the ground (user, in game 2026-11-17: the stargate's DHD and stairs, the bar
        # corner shelf's base; the build ghost, drawn without depth, showed them): figures never farther than
        # vanilla's own table-top pieces at the same row, everything else never behind the floor
        figs = {c for c in cells if (COPIES.get(c) or MIRROR_COPIES.get(c)) in [(D1_SHEET, n) for n in FIG_SRC]}
        for c in list(cells):
            if c in WEDGE_COPIES:
                continue
            cells[c] = _tabletop_clamp(cells[c]) if c in figs else _floor_clamp(cells[c])
        # the gate: its cell also covers the event horizon (lit art); the lit tileset gets the same cells
        on_cells = {}
        for c, im in lit.items():
            cells[c] = k._fill_depth_holes(cells[c], im)
            cells[c] = _tabletop_clamp(cells[c]) if c in figs else _floor_clamp(cells[c])
            on_cells[c] = cells[c]
        depth = Image.new("RGBA", (cols * 128, rows * 256), (0, 0, 0, 0))
        for c, cell in cells.items():
            depth.paste(cell, ((c % cols) * 128, (c // cols) * 256))
        os.makedirs(os.path.join(common_media_dir, "depthmaps"), exist_ok=True)
        depth.save(os.path.join(common_media_dir, "depthmaps", "DEPTH_%s.png" % COPY_TILESET))
        depth_on = Image.new("RGBA", (cols * 128, rows * 256), (0, 0, 0, 0))
        for c, cell in on_cells.items():
            depth_on.paste(cell, ((c % cols) * 128, (c // cols) * 256))
        depth_on.save(os.path.join(common_media_dir, "depthmaps", "DEPTH_%s.png" % LIGHT_ON_TILESET))
        # raised beds: a box filling the square, soil BED_LIFT_ROWS above the floor (_box_depth)
        bed_depth_path = os.path.join(common_media_dir, "depthmaps", "DEPTH_%s.png" % BED_TILESET)
        if BED_COPIES:
            depth_bed = Image.new("RGBA", (cols * 128, brows * 256), (0, 0, 0, 0))
            for c, (h, _bn) in BED_COPIES.items():
                cell = _floor_clamp(k._fill_depth_holes(_box_depth(beds[c], BED_LIFT_ROWS[h]), beds[c]))
                depth_bed.paste(cell, ((c % cols) * 128, (c // cols) * 256))
            depth_bed.save(bed_depth_path)
        elif os.path.isfile(bed_depth_path):
            os.remove(bed_depth_path)
        # wall bench seats (BENCH_SRC): seating.txt, merged with any other tileset's seats in the folder
        seat_blocks = []
        for n in BENCH_SRC:
            c = int(copy_name(HW_SHEET, n).rsplit("_", 1)[1])
            facing = src_props[c].get("Facing")
            seat_blocks.append("        /* %s_%d (wall bench, honeywood %d) */\n        %s"
                               % (COPY_TILESET, c, n, k._seat_block(c % cols, c // cols, [BENCH_SEAT[facing]])))
        k.merge_seating(os.path.join(common_media_dir, "seating.txt"), COPY_TILESET, seat_blocks)
        # the depth-map loader only runs for mods that ship a tileGeometry.txt; never replace one
        tg = os.path.join(common_media_dir, "tileGeometry.txt")
        if not os.path.isfile(tg):
            open(tg, "w", encoding="utf-8").write("tileGeometry\n{\n    VERSION = 2,\n}\n")
    return n


def write_overlay_lua(dest_path):
    """Fill overlays for our copies (gun rack, glass display counter): the same vanilla ContainerOverlays
    registration the standalone Simon MD pack uses for its own tiles (Simon_MD_WorldFiller.lua)."""
    rows = "\n".join('overlayMap["%s"] = {{ name = "other", tiles = {"%s", "%s"} }}'
                     % (copy_name(*base), copy_name(OVL_SHEET, a), copy_name(OVL_SHEET, b))
                     for base, (a, b) in sorted(OVERLAYS.items()))

    # in-wall shelves: vanilla's own entry for the matched vanilla shelf, verbatim (room-based book sets)
    import re
    vanilla = {}
    for line in open(os.path.join(_VANILLA_MEDIA, "lua", "server", "Items", "WorldFiller.lua"), encoding="utf-8", errors="replace"):
        m = re.match(r'\s*overlayMap\["([^"]+)"\]\s*=\s*(.*\S)\s*$', line)
        if m:
            vanilla[m.group(1)] = m.group(2)
    extra = []
    for base in sorted(BOOK_BASES):
        groups = ", ".join('{ name = "other", tiles = {"%s", "%s"} }' % (gen_copy_name(base, si, 0), gen_copy_name(base, si, 1))
                           for si in range(2))
        extra.append('overlayMap["%s"] = {%s}' % (copy_name(*base), groups))
    rows += ("\n-- in-wall and sloped shelves: vanilla's books re-laid onto our boards (shelf_relayout.py;"
             "\n-- Raven Creek lacks Simon's own overlays for them)\n" + "\n".join(extra))
    lua = ("-- AUTO-GENERATED by pz_craft_loops/simonmd_doors_furniture.py -- do not edit by hand.\n"
           "-- Fill overlays for our Simon MD copies (gun rack, glass display counter), as the standalone\n"
           "-- Simon MD pack registers them for its own tiles. Map tiles are not touched.\n"
           "local overlayMap = {}\noverlayMap.VERSION = 1\n%s\n"
           "if not TILEZED and getContainerOverlays then\n"
           "    getContainerOverlays():addOverlays(overlayMap)\nend\n" % rows)
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    open(dest_path, "w", encoding="utf-8", newline="\n").write(lua)


def _write(path, category, source, buildables):
    ids = [b["id"] for b in buildables]
    assert len(ids) == len(set(ids)), ids
    doc = {"schemaVersion": 1, "category": category, "source": source, "buildables": buildables}
    json.dump(doc, open(path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("wrote %s (%d buildables)" % (path, len(ids)))


def main():
    _v, ts, _o = k._parse(open(RC_TILES, "rb").read())
    os.makedirs(OUT_DIR, exist_ok=True)
    _write(OUT_DOORS, "Doors",
           "Simon MD doors (Raven Creek's LCB42_SimonMDsTiles copy): two scrap doors, the metal-wardrobe secret "
           "entrance, shipping-container garage doors 3 / 4 wide; pieces and costs from the B41 Building Menu Simon "
           "MD addon. Generated by pz_craft_loops/simonmd_doors_furniture.py.", doors(ts))
    _write(OUT_FURN, "Containers",
           "Simon MD furniture (Raven Creek's LCB42_SimonMDsTiles copy): military locker, glass display counter and "
           "cabinet, wall gun rack; pieces and costs from the B41 Building Menu Simon MD addon. Generated by "
           "pz_craft_loops/simonmd_doors_furniture.py.", furniture(ts))


if __name__ == "__main__":
    main()
