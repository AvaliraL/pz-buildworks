# -*- coding: utf-8 -*-
"""TikiTown tterika wall detailing sheets as KBW wall overlays (user, 2026-11-08: build "all" pieces,
new categories, material costs, descriptive names like the naming pass).

  43_tikitown_wall_paint_cladding.json  "Wall Paint & Cladding"
      walls_interior_detailing_tterika_01 (32 rows) / _02 (13 rows): paint and wallpaper
      walls_exterior_detailing_tterika_01 (32 rows) / _02 (9 rows):  brick / stone / wood / siding
      Every sheet repeats one 16-tile row per colour (layout = vanilla walls_interior_detailing_01,
      measured on every row 2026-11-08: bbox + top-edge slope):
        0 W / 1 N lower panel (dado height, 0.52-0.88 of the frame; a full wall is 0.00-0.88)
        2 corner (NW)        3 end cap (SE)
        4 W / 5 N top band (0.00-0.21)   6 corner   7 end cap
        8 W / 9 N lower panel for window walls    10 W / 11 N lower panel for door-frame walls
        12 W outer / 13 W inner / 14 N inner / 15 N outer: the door-frame panel's two halves
      The pack tiles carry WallOverlay but (mostly) no attachedN/W. KBW only hangs a sprite on a host
      wall when it has an attached* flag (AttachedSprites.isWallDecorationSprite); without it the piece
      would be placed as a loose object. So these four sheets use OUR OWN COPIES with the facing flag
      added by position (pack tiles untouched; a tile patch would change every map-placed copy too).
      The copies go into the existing kbwtikitown_walloverlays tiles file / KBWTikiTownWallOverlays
      pack as three more tilesets (KBWTikiTownDetail1..3, each <= 512 tiles): no new mod.info lines.

  44_tikitown_wall_trim.json  "Wall Trim"
      walls_detailing_tterika_01 (320) / _02 (52): baseboards, chair rails, crown, wainscot panels,
      corner trim. These pack tiles already carry attachedN/W/E (+ CornerNorthWall on corners), so they
      are used as they are. W/N pairs are matched by mirrored bbox + colour; corners and end caps are
      walk-through props like file 39.

Placement (file 39 model, confirmed in game): faces = overlay against a wall; corner = prop with
KBWCommunityCornerTrim.OnIsValid (walls on both sides); end cap = prop.
Costs: paint = paintbrush + 1-2 uses of the nearest vanilla paint; wallpaper = 1 use of a roll;
cladding = the matching TikiTown wall's recipe (brick / stone / wood / siding) scaled by piece size;
trim = the wood wall recipe scaled to a quarter.
"""
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tikitown_wall_overlays as two  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_PAINT = r"c:\Users\josep\Kiro\zomboid\tikitown\43_tikitown_wall_paint_cladding.json"
OUT_TRIM = r"c:\Users\josep\Kiro\zomboid\tikitown\44_tikitown_wall_trim.json"
CACHE = os.path.join(HERE, "_cache_walldetail")
CAT_PAINT = "Wall Paint & Cladding"
CAT_TRIM = "Wall Trim"
TOOLTIP = "Tooltip_KBW_DecorativeWallFixture"
TAGS = ["tikitown", "drazion", "world-essentials", "wall-overlay", "wall-detailing"]

# ---------------------------------------------------------------------------------------------
# copied sheets: (sheet, rows, tileset, first copy index). APPEND only: positions fix sprite names.
COPY_SHEETS = [
    ("walls_interior_detailing_tterika_01", 32, "KBWTikiTownDetail1", 0),
    ("walls_exterior_detailing_tterika_01", 32, "KBWTikiTownDetail2", 0),
    ("walls_interior_detailing_tterika_02", 13, "KBWTikiTownDetail3", 0),
    ("walls_exterior_detailing_tterika_02", 9, "KBWTikiTownDetail3", 13 * 16),
]
# facing flag of our copy, by position in the 16-tile row (measured; see module doc)
POS_FACING = ["attachedW", "attachedN", "attachedNW", "attachedSE",
              "attachedW", "attachedN", "attachedNW", "attachedSE",
              "attachedW", "attachedN", "attachedW", "attachedN",
              "attachedW", "attachedW", "attachedN", "attachedN"]


def copy_sprite(sheet, tile):
    for sh, rows, ts, first in COPY_SHEETS:
        if sh == sheet:
            assert 0 <= tile < rows * 16, (sheet, tile)
            return "%s_%d" % (ts, first + tile)
    raise KeyError(sheet)


def copy_tiles():
    """[(source sprite, copy sprite, props)] for every copied tile, in tileset order."""
    out = []
    for sh, rows, _ts, _first in COPY_SHEETS:
        for t in range(rows * 16):
            out.append(("%s_%d" % (sh, t), copy_sprite(sh, t),
                        [(b"WallOverlay", b""), (POS_FACING[t % 16].encode(), b"")]))
    return out


# ---------------------------------------------------------------------------------------------
# row styles: (name, kind). kind: paint | wallpaper | brick | stone | wood | siding
STYLES = {
    "walls_interior_detailing_tterika_01": [
        ("Silver Stripe Wallpaper", "wallpaper"), ("Slate Gray Paint", "paint"), ("Burgundy Paint", "paint"),
        ("Olive Green Paint", "paint"), ("Mint Green Paint", "paint"), ("Burnt Orange Paint", "paint"),
        ("Steel Blue Paint", "paint"), ("Cream Paint", "paint"), ("Apricot Paint", "paint"),
        ("Gray Textured Wallpaper", "wallpaper"), ("Pale Khaki Paint", "paint"),
        ("Lavender Stripe Wallpaper", "wallpaper"), ("Purple Paint", "paint"), ("Taupe Paint", "paint"),
        ("Sage Green Paint", "paint"), ("Mauve Paint", "paint"), ("Warm Gray Paint", "paint"),
        ("Mustard Paint", "paint"), ("Raspberry Paint", "paint"), ("Sea Green Paint", "paint"),
        ("Beige Grain Wallpaper", "wallpaper"), ("Golden Tan Paint", "paint"),
        ("Cornflower Blue Paint", "paint"), ("Chocolate Brown Paint", "paint"), ("Caramel Paint", "paint"),
        ("Periwinkle Paint", "paint"), ("Plum Paint", "paint"), ("Off-White Paint", "paint"),
        ("Charcoal Paint", "paint"), ("Black Floral Wallpaper", "wallpaper"), ("Dusty Pink Paint", "paint"),
        ("Salmon Paint", "paint")],
    "walls_interior_detailing_tterika_02": [
        ("Dark Gray Paint", "paint"), ("Gray Paint", "paint"), ("Light Gray Paint", "paint"),
        ("Forest Green Paint", "paint"), ("Beige Damask Wallpaper", "wallpaper"), ("Pale Sage Paint", "paint"),
        ("Slate Blue Paint", "paint"), ("Rust Paint", "paint"), ("Blue Gray Paint", "paint"),
        ("Blush Pink Paint", "paint"), ("Lilac Paint", "paint"), ("Teal Paint", "paint"),
        ("Moss Green Paint", "paint")],
    "walls_exterior_detailing_tterika_01": [
        ("Blue-Gray Brick Cladding", "brick"), ("Orange Brick Cladding", "brick"),
        ("Gray-Brown Siding", "siding"), ("Beige Stone Cladding", "stone"), ("Gray Brick Cladding", "brick"),
        ("Cream Siding", "siding"), ("Sandstone Cladding", "stone"), ("Red-Brown Brick Cladding", "brick"),
        ("Sage Siding", "siding"), ("Brown Plank Cladding", "wood"), ("Dark Wood Board Cladding", "wood"),
        ("Pale Board Siding", "siding"), ("Red Siding", "siding"), ("Brown Siding", "siding"),
        ("Light Brown Siding", "siding"), ("Gray Siding", "siding"), ("Green Siding", "siding"),
        ("Dark Red Board Cladding", "wood"), ("Rose Brick Cladding", "brick"), ("White Siding", "siding"),
        ("Dark Brick Cladding", "brick"), ("Tan Brick Cladding", "brick"), ("Light Blue Siding", "siding"),
        ("Golden Stone Cladding", "stone"), ("Mossy Stone Cladding", "stone"), ("Pink Siding", "siding"),
        ("Tan Plank Cladding", "wood"), ("Mahogany Board Cladding", "wood"),
        ("Dark Brown Plank Cladding", "wood"), ("Light Cream Siding", "siding"), ("Mauve Siding", "siding"),
        ("Off-White Siding", "siding")],
    "walls_exterior_detailing_tterika_02": [
        ("Barn Red Siding", "siding"), ("White Board and Batten", "siding"), ("Tan Board and Batten", "siding"),
        ("Green Board and Batten", "siding"), ("Blue Board and Batten", "siding"),
        ("Gray Fieldstone Cladding", "stone"), ("Blue Block Cladding", "stone"),
        ("Brown Brick Cladding", "brick"), ("Dark Brown Brick Cladding", "brick")],
}
SUBCAT = {"paint": "Paint", "wallpaper": "Wallpaper", "brick": "Brick Cladding",
          "stone": "Stone Cladding", "wood": "Wood Cladding", "siding": "Siding"}
SOURCE_WALL = {"brick": "tikitown_walls_brick_01", "stone": "tikitown_walls_stone_01",
               "wood": "tikitown_walls_wood_01", "siding": "tikitown_walls_siding_01"}

# pieces per row: (slug, label, {face: position}, placement kind, cost factor, level)
_OVERLAY = {"kind": "overlay", "needToBeAgainstWall": True}
_PROP = {"kind": "object", "requiresFloor": False}
ROW_PIECES = [
    ("panel", "Lower Panel", {"W": 0, "N": 1}, _OVERLAY, 0.5),
    ("panel_corner", "Lower Panel Corner", {"W": 2}, _PROP, 0.5),
    ("panel_cap", "Lower Panel End Cap", {"W": 3}, _PROP, 0.25),
    ("band", "Top Band", {"W": 4, "N": 5}, _OVERLAY, 0.25),
    ("band_corner", "Top Band Corner", {"W": 6}, _PROP, 0.25),
    ("band_cap", "Top Band End Cap", {"W": 7}, _PROP, 0.25),
    ("window", "Lower Panel (Window)", {"W": 8, "N": 9}, _OVERLAY, 0.5),
    ("doorframe", "Lower Panel (Door Frame)", {"W": 10, "N": 11}, _OVERLAY, 0.25),
    ("edge_outer", "Lower Panel Door Edge (Outer)", {"W": 12, "N": 15}, _OVERLAY, 0.25),
    ("edge_inner", "Lower Panel Door Edge (Inner)", {"W": 13, "N": 14}, _OVERLAY, 0.25),
]
_OBJ = {"isThumpable": False, "canPassThrough": True, "blockAllSquare": False, "dismantable": True}

# vanilla paint buckets and rough colours (for the nearest-paint cost)
PAINTS = {"PaintWhite": (240, 240, 235), "PaintBlack": (35, 35, 38), "PaintGrey": (128, 128, 128),
          "PaintBlue": (45, 75, 160), "PaintLightBlue": (150, 185, 225), "PaintBrown": (105, 65, 35),
          "PaintLightBrown": (185, 145, 95), "PaintCyan": (40, 190, 200), "PaintTurquoise": (60, 150, 140),
          "PaintGreen": (70, 120, 60), "PaintYellow": (235, 210, 90), "PaintOrange": (215, 120, 45),
          "PaintRed": (165, 40, 45), "PaintPink": (230, 155, 170), "PaintPurple": (125, 80, 150)}
# vanilla paint per colour name (nearest-RGB matched badly: charcoal -> green, khaki -> pink)
PAINT_FOR = {
    "Slate Gray": "PaintGrey", "Burgundy": "PaintRed", "Olive Green": "PaintGreen", "Mint Green": "PaintGreen",
    "Burnt Orange": "PaintOrange", "Steel Blue": "PaintBlue", "Cream": "PaintWhite", "Apricot": "PaintOrange",
    "Pale Khaki": "PaintLightBrown", "Purple": "PaintPurple", "Taupe": "PaintLightBrown",
    "Sage Green": "PaintGreen", "Mauve": "PaintPurple", "Warm Gray": "PaintGrey", "Mustard": "PaintYellow",
    "Raspberry": "PaintPink", "Sea Green": "PaintTurquoise", "Golden Tan": "PaintLightBrown",
    "Cornflower Blue": "PaintLightBlue", "Chocolate Brown": "PaintBrown", "Caramel": "PaintLightBrown",
    "Periwinkle": "PaintLightBlue", "Plum": "PaintPurple", "Off-White": "PaintWhite", "Charcoal": "PaintBlack",
    "Dusty Pink": "PaintPink", "Salmon": "PaintPink",
    "Dark Gray": "PaintGrey", "Gray": "PaintGrey", "Light Gray": "PaintWhite", "Forest Green": "PaintGreen",
    "Pale Sage": "PaintGreen", "Slate Blue": "PaintBlue", "Rust": "PaintRed", "Blue Gray": "PaintLightBlue",
    "Blush Pink": "PaintPink", "Lilac": "PaintPurple", "Teal": "PaintTurquoise", "Moss Green": "PaintGreen",
}
WALLPAPERS = ["Base.Wallpaper_BeigeStripe", "Base.Wallpaper_BlackFloral", "Base.Wallpaper_BlueStripe",
              "Base.Wallpaper_GreenDiamond", "Base.Wallpaper_GreenFloral", "Base.Wallpaper_PinkChevron",
              "Base.Wallpaper_PinkFloral"]
WALLPAPER_MATCH = {"Black Floral Wallpaper": ["Base.Wallpaper_BlackFloral"]}


def _extract(names):
    import kbw_tilepatch as k
    k._extract_from_pack(two._TIKITOWN_PACK, set(names), CACHE)


def _img(name):
    from PIL import Image
    return Image.open(os.path.join(CACHE, name + ".png")).convert("RGBA")


def _mean_rgb(name):
    from PIL import ImageStat
    im = _img(name)
    a = im.split()[3].point(lambda v: 255 if v > 200 else 0)
    if not a.getbbox():
        return None
    return tuple(int(x) for x in ImageStat.Stat(im.convert("RGB"), mask=a).mean)


def _nearest_paint(rgb):
    return min(PAINTS, key=lambda p: sum((a - b) ** 2 for a, b in zip(PAINTS[p], rgb)))


def _paint_requirements(item, uses):
    return {"inputs": [
        {"id": "tool_paintbrush", "role": "tool", "mode": "keep", "resourceType": "Item",
         "tags": ["base:paintbrush"], "amount": 1},
        {"id": "finish_paint", "role": "consumable", "mode": "drain", "resourceType": "Item",
         "items": item if isinstance(item, list) else ["Base." + item], "amount": 1, "uses": uses}]}


def _paint_construction(f):
    return {"time": max(60, int(round(160 * f))), "timedAction": "BuildWallNoTool",
            "completionSound": "BuildWoodenStructureSmall"}


def _stage(sprites, req, con, piece_kind):
    # corners: dismantlable thumpable like file 39's (removable inside PhunInteriors rooms)
    obj = dict(two._CORNER_OBJ if piece_kind == "corner" else _OBJ)
    stage = {"id": "built", "geometry": {"faces": two._faces(sprites)},
             "requirements": req, "construction": con, "object": obj}
    if piece_kind == "corner":
        stage["health"] = 150
        stage["callbacks"] = {"onIsValid": two.CORNER_ISVALID}
    elif piece_kind == "cap":
        stage["health"] = 150
    return stage


def _entry(bid, tkey, name, cat, sub, material, sprites, placement, group, level, stage):
    return {"id": bid, "allowSpriteReuse": True, "translationKey": tkey, "displayName": name,
            "tooltipKey": TOOLTIP, "category": cat, "subcategory": sub, "material": material,
            "iconSprite": next(iter(sprites.values())), "placement": dict(placement), "tags": list(TAGS),
            "pieceClass": "decoration",
            "group": dict(group, level=level), "stages": [stage]}


def build_paint_cladding():
    src = two._wall_sources()
    _extract(["%s_%d" % (sh, r * 16 + 1) for sh, rows, _t, _f in COPY_SHEETS for r in range(rows)])
    builds, report = [], []
    for sh, rows, _ts, _first in COPY_SHEETS:
        styles = STYLES[sh]
        assert len(styles) == rows, (sh, len(styles), rows)
        for r, (style, kind) in enumerate(styles):
            sub = SUBCAT[kind]
            base = sh.replace("walls_", "").replace("_detailing_tterika", "")      # interior_01 ...
            gslug = "%s_%02d" % (base, r)
            group = {"id": "worldessentials.tikitown.walldetail.%s" % gslug, "name": style,
                     "translationKey": "IGUI_WETiki_walldetail_%s_group" % gslug}
            if kind == "paint":
                paint = PAINT_FOR[style[:-len(" Paint")]]
                material = "Paint"
            elif kind == "wallpaper":
                paint = WALLPAPER_MATCH.get(style, WALLPAPERS)
                material = "Wallpaper"
            else:
                wall = src[SOURCE_WALL[kind]]
                st0 = wall["stages"][0]
                material = wall.get("material", "Wood")
            for level, (pslug, label, faces, placement, f) in enumerate(ROW_PIECES, 1):
                sprites = {fc: copy_sprite(sh, r * 16 + pos) for fc, pos in faces.items()}
                pkind = "corner" if pslug.endswith("_corner") else ("cap" if pslug.endswith("_cap") else "face")
                if kind in ("paint", "wallpaper"):
                    req = _paint_requirements(paint, 2 if f >= 0.5 else 1)
                    con = _paint_construction(f)
                else:
                    req = two._scaled_requirements(st0.get("requirements") or {}, f)
                    con = two._scaled_construction(st0.get("construction") or {}, f)
                slug = "%s_%s" % (gslug, pslug)
                builds.append(_entry(
                    "worldessentials.tikitown.walldetail.%s" % slug, "IGUI_WETiki_walldetail_%s" % slug,
                    "%s %s" % (style, label), CAT_PAINT, sub, material, sprites, placement, group, level,
                    _stage(sprites, req, con, pkind)))
    return {"schemaVersion": 1, "category": CAT_PAINT,
            "source": ("TikiTown tterika wall detailing (interior paint / wallpaper, exterior cladding) as WALL "
                       "OVERLAYS on our own copied tiles (KBWTikiTownDetail1..3 in the kbwtikitown_walloverlays "
                       "tiles file, facing flags added by position; pack tiles unchanged)."),
            "buildables": builds}, report


# ---------------------------------------------------------------------------------------------
# trim (pack tiles as they are)
TRIM_SHEETS = ["walls_detailing_tterika_01", "walls_detailing_tterika_02"]


def _trim_colour(rgb):
    r, g, b = rgb
    lum = 0.3 * r + 0.59 * g + 0.11 * b
    sat = max(rgb) - min(rgb)
    if lum > 185 and sat < 40:
        return "White"
    if sat < 25:
        return "Black" if lum < 60 else "Gray"
    if r > 150 and b < 100 and r - b > 80 and g < 100:
        return "Red"
    if b > r and b > g:
        return "Slate Blue"
    if lum < 70:
        return "Dark Wood"
    if lum < 105:
        return "Walnut"
    return "Light Wood"


def _trim_profile(bb, w, h):
    x0, y0, x1, y1 = bb[0] / float(w), bb[1] / float(h), bb[2] / float(w), bb[3] / float(h)
    ht = y1 - y0
    if ht > 0.55:
        return "Corner Trim", "Corner Trim"
    if y0 < 0.06 and ht < 0.3:
        return "Crown Molding", "Crown Molding"
    if y1 > 0.84 and ht <= 0.14:
        return "Baseboard", "Baseboards"
    if y1 > 0.84:
        return "Wainscot Panel", "Wainscot Panels"
    return "Chair Rail", "Chair Rails"


def build_trim():
    from build_rename_map import parse
    props = parse(two_tiles_path())
    names = []
    for sh in TRIM_SHEETS:
        names += ["%s_%d" % (sh, i) for i in range(len(props[sh]["tiles"]))]
    import kbw_tilepatch as k
    have = set()
    try:
        k._extract_from_pack(two._TIKITOWN_PACK, set(names), CACHE)
        have = set(names)
    except Exception:   # some indices have no art: extract the ones the pack has
        import sheet_coverage as sc
        have = set(names) & set(sc.pack_names(two._TIKITOWN_PACK))
        k._extract_from_pack(two._TIKITOWN_PACK, have, CACHE)
    pieces = []   # dicts: sheet, idx, facing, bbox, colour, profile
    for sh in TRIM_SHEETS:
        for i, p in enumerate(props[sh]["tiles"]):
            n = "%s_%d" % (sh, i)
            if n not in have or not p:
                continue
            im = _img(n)
            bb = im.split()[3].getbbox()
            if not bb:
                continue
            if "CornerNorthWall" in p or "attachedNW" in p:
                facing = "C"
            elif "attachedE" in p or "attachedSE" in p:
                facing = "E"
            elif "attachedW" in p:
                facing = "W"
            elif "attachedN" in p:
                facing = "N"
            else:
                continue
            prof, plural = _trim_profile(bb, im.size[0], im.size[1])
            pieces.append({"sheet": sh, "idx": i, "sprite": n, "facing": facing, "bb": bb, "size": im.size,
                           "profile": prof, "plural": plural})
    # Colour per 16-tile block: a W face is drawn darker than its N twin, so a per-tile colour split
    # real pairs. The block's brightest piece (lit N face) names the colour for the whole block.
    block_rgb = {}
    for pc in pieces:
        rgb = _mean_rgb(pc["sprite"])
        if rgb is None:
            continue
        key = (pc["sheet"], pc["idx"] // 16)
        if key not in block_rgb or sum(rgb) > sum(block_rgb[key]):
            block_rgb[key] = rgb
    for pc in pieces:
        pc["colour"] = _trim_colour(block_rgb.get((pc["sheet"], pc["idx"] // 16), (128, 128, 128)))
    # pair each W with the next unused N of the same sheet / colour / profile whose bbox mirrors it
    used = set()
    units = []    # (kind, [pieces])
    for a in pieces:
        if a["facing"] != "W" or a["sprite"] in used:
            continue
        w = a["size"][0]
        best = None
        for b in pieces:
            if (b["facing"] != "N" or b["sprite"] in used or b["sheet"] != a["sheet"]
                    or b["profile"] != a["profile"] or b["idx"] < a["idx"] or b["idx"] - a["idx"] > 8):
                continue
            mx = abs((w - a["bb"][2]) - b["bb"][0]) + abs((w - a["bb"][0]) - b["bb"][2])
            my = abs(a["bb"][1] - b["bb"][1]) + abs(a["bb"][3] - b["bb"][3])
            score = mx + my
            if score <= 12 and (best is None or score < best[0] or (score == best[0] and b["idx"] < best[1]["idx"])):
                best = (score, b)
        if best:
            used.update([a["sprite"], best[1]["sprite"]])
            units.append(("pair", [a, best[1]]))
    for a in pieces:
        if a["sprite"] in used:
            continue
        used.add(a["sprite"])
        units.append(({"W": "single", "N": "single", "C": "corner", "E": "cap"}[a["facing"]], [a]))
    units.sort(key=lambda u: (u[1][0]["sheet"], u[1][0]["idx"]))
    src = two._wall_sources()["tikitown_walls_wood_01"]
    st0 = src["stages"][0]
    req = two._scaled_requirements(st0.get("requirements") or {}, 0.25)
    con = two._scaled_construction(st0.get("construction") or {}, 0.25)
    builds, counters = [], {}
    for kind, ps in units:
        a = ps[0]
        fam = "%s %s" % (a["colour"], a["profile"])
        counters[fam] = counters.get(fam, 0) + 1
        n = counters[fam]
        sheet_slug = a["sheet"].replace("walls_detailing_tterika_", "trim")
        if kind == "pair":
            sprites, placement, label, pk = {"W": ps[0]["sprite"], "N": ps[1]["sprite"]}, _OVERLAY, "", "face"
        elif kind == "single":
            sprites, placement, label, pk = {a["facing"]: a["sprite"]}, _OVERLAY, "", "face"
        elif kind == "corner":
            sprites, placement, label, pk = {"W": a["sprite"]}, _PROP, " Corner", "corner"
        else:
            sprites, placement, label, pk = {"W": a["sprite"]}, _PROP, " End Cap", "cap"
        slug = "%s_%d" % (sheet_slug, a["idx"])
        gslug = "%s_%s" % (sheet_slug, fam.lower().replace(" ", "_"))
        group = {"id": "worldessentials.tikitown.walltrim.%s" % gslug, "name": fam,
                 "translationKey": "IGUI_WETiki_walltrim_%s_group" % gslug}
        builds.append(_entry("worldessentials.tikitown.walltrim.%s" % slug, "IGUI_WETiki_walltrim_%s" % slug,
                             "%s %d%s" % (fam, n, label), CAT_TRIM, a["plural"], "Wood", sprites, placement,
                             group, n, _stage(sprites, json.loads(json.dumps(req)),
                                              json.loads(json.dumps(con)), pk)))
    return {"schemaVersion": 1, "category": CAT_TRIM,
            "source": ("TikiTown tterika wall trim sheets (walls_detailing_tterika_01/02) as WALL OVERLAYS on the "
                       "pack's own tiles (they already carry attachedN/W/E). Cost: the wood wall recipe x 1/4."),
            "buildables": builds}, ["trim units: %d (pairs %d)" % (len(units), sum(1 for u in units if u[0] == "pair"))]


def two_tiles_path():
    return (r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600\3046728955\mods"
            r"\Drazions Tile Pack\common\media\tikitown_tiles.tiles")


def main():
    for build, out in ((build_paint_cladding, OUT_PAINT), (build_trim, OUT_TRIM)):
        doc, report = build()
        ids = [b["id"] for b in doc["buildables"]]
        assert len(ids) == len(set(ids)), "duplicate ids"
        # md5(id) order: keeps KBW Registry:list()'s Kahlua quicksort shallow (see tikitown_wall_overlays)
        doc["buildables"].sort(key=lambda b: hashlib.md5(b["id"].encode("utf-8")).hexdigest())
        json.dump(doc, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        print("wrote %s (%d buildables)" % (out, len(ids)))
        for line in report:
            print("   " + line)


if __name__ == "__main__":
    main()
