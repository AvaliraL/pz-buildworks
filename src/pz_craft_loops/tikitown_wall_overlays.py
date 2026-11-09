# -*- coding: utf-8 -*-
"""TikiTown lower walls + wall overlays from tiles 72-91 of 60 TikiTown wall sheets, five heights
(3/4, 2/3, 1/2, 1/3, 1/4) x panel / corner / pillar. Two separate versions (user, 2026-08-28):

  40_tikitown_lower_walls.json   LOWER WALLS   "Walls and Wall Finishes" / "<Type> Lower Walls"
      The pack tiles as the pack defines them: real low walls (wall type, WallWTrans/WallNTrans,
      HoppableW/N, WallSE). Built like our confirmed walls: panel = kind wall + W/N faces +
      cornerSprite/pillarSprite (White Glass Fence model); corner = the wall Corner model; pillar =
      the wall Pillar model. Like any wall they take the wall edge (on an existing wall they replace it).

  39_tikitown_wall_overlays.json WALL OVERLAYS "Decorations and Landscaping" / "<Type> Wall Overlays"
      OUR OWN COPIES of the same tiles (tileset KBWTikiTownWallOverlays, tiledef
      kbwtikitown_walloverlays 8179), carrying only overlay properties like KBW Vanilla Expanded's
      working lower-wall panels (walls_commercial_03_60/61/63: WallOverlay + attachedW/N/E). Map tiles
      are never changed. (Rev 2 stripped the PACK tiles at load instead: refused, because a tile
      patch changes every map-placed copy of the sprite too.) Panel = overlay against a wall;
      corner = walk-through prop + KBWCommunityCornerTrim.OnIsValid (walls on both W and N sides);
      pillar = walk-through prop.

Layout (identical on every sheet, tile data checked 2026-08-28): group base 72 = 3/4, 76 = 2/3,
80 = 1/2, 84 = 1/3, 88 = 1/4 (user-confirmed order); base+0 W panel, +1 N panel, +2 corner, +3 pillar.
Cost: the sheet's own wall recipe (21_tikitown_walls_accurate.json, piece 0) with material amounts,
time and xp scaled by the height (rounded up, at least 1); pillars half of that. Tools and skills
unchanged. Skipped: siding_burnt_01 (not in pack), wall_burnt_01 (burnt variant), the 1/2-high
pillars some sheets have. Copied tiles need a full game restart to load (like all new tile art).
"""
import hashlib
import io
import json
import math
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

WALLS = r"c:\Users\josep\Kiro\zomboid\tikitown\21_tikitown_walls_accurate.json"
OUT_OVERLAYS = r"c:\Users\josep\Kiro\zomboid\tikitown\39_tikitown_wall_overlays.json"
OUT_WALLS = r"c:\Users\josep\Kiro\zomboid\tikitown\40_tikitown_lower_walls.json"
CORNER_ISVALID = "KBWCommunityCornerTrim.OnIsValid"   # shared OverlayGuard Lua (kbw_tilepatch)

OVERLAY_TILESET = "KBWTikiTownWallOverlays"
OVERLAY_PACK = "KBWTikiTownWallOverlays"
OVERLAY_TILEDEF_NAME = "kbwtikitown_walloverlays"
OVERLAY_TILEDEF_ID = 8179   # free (8170-8199 scanned 2026-08-28; 8178, 8180-8189 taken)

SHEETS = (["tikitown_walls_wood_01"]
          + ["tikitown_vanilla_walls_add_%02d" % i for i in range(1, 13)]
          + ["tikitown_vanilla_walls_add_bathroom_01"]
          + ["tikitown_walls_bathroom_%02d" % i for i in range(1, 5)]
          + ["tikitown_walls_brick_%02d" % i for i in range(1, 13)]
          + ["tikitown_walls_brick_purewhite", "tikitown_walls_brick_standard",
             "tikitown_walls_bricks_dirtywhite", "tikitown_walls_cement_01"]
          + ["tikitown_walls_decorative_%02d" % i for i in range(1, 6)]
          + ["tikitown_walls_interior_01", "tikitown_walls_metal_01", "tikitown_walls_metal_02",
             "tikitown_walls_plaster_01", "tikitown_walls_plaster_02"]
          + ["tikitown_walls_siding_%02d" % i for i in range(1, 5)]
          + ["tikitown_walls_stone_01", "tikitown_walls_stone_02"]
          + ["tikitown_walls_wallpaper_%02d" % i for i in range(1, 11)]
          # added 2026-11-08 (full-sheet pass): same 72-91 lower-wall block. APPENDED, never
          # inserted: a sheet's position fixes its copied overlay tile numbers.
          + ["tikitown_commercial_walls_add_%02d" % i for i in range(1, 4)])

FIRST = 72      # tiles 72..91 per sheet are copied, in order
PER_SHEET = 20

# (group base tile, id slug, label, height fraction), tallest first
HEIGHTS = [(72, "34", "3/4", 3 / 4.0), (76, "23", "2/3", 2 / 3.0), (80, "12", "1/2", 1 / 2.0),
           (84, "13", "1/3", 1 / 3.0), (88, "14", "1/4", 1 / 4.0)]

# props of our copies, by position in the group of 4 (W panel, N panel, corner, pillar)
_COPY_PROPS = [[(b"WallOverlay", b""), (b"attachedW", b"")],
               [(b"WallOverlay", b""), (b"attachedN", b"")],
               [(b"WallOverlay", b""), (b"attachedNW", b"")],
               [(b"WallOverlay", b""), (b"attachedSE", b"")]]


# The game allows at most 512 tiles per TILESET ("invalid number of tiles 1208, must be from 0 to
# 512", world load refused, 2026-11-08). The copies are split over several tilesets in the one
# .tiles file: 24 sheets x 20 tiles = 480 per tileset -> KBWTikiTownWallOverlays1..3.
SHEETS_PER_TILESET = 24
MAX_TILES_PER_TILESET = 512


def overlay_tileset(sheet_index):
    return "%s%d" % (OVERLAY_TILESET, sheet_index // SHEETS_PER_TILESET + 1)


def overlay_sprite(sheet, tile):
    """Our copy of <sheet>_<tile> (tile 72..91)."""
    i = SHEETS.index(sheet)
    return "%s_%d" % (overlay_tileset(i), (i % SHEETS_PER_TILESET) * PER_SHEET + (tile - FIRST))


# ---------------------------------------------------------------------------------------------
# costs
def _scale(n, f):
    return max(1, int(math.ceil(n * f - 1e-9)))


def _scaled_requirements(req, f):
    out = json.loads(json.dumps(req))
    for inp in out.get("inputs", []):
        if inp.get("role") == "tool" and inp.get("mode") == "keep":
            continue
        if isinstance(inp.get("amount"), (int, float)):
            inp["amount"] = _scale(inp["amount"], f)
        if isinstance(inp.get("uses"), (int, float)):
            inp["uses"] = _scale(inp["uses"], f)
    return out


def _scaled_construction(con, f):
    out = json.loads(json.dumps(con))
    if isinstance(out.get("time"), (int, float)):
        out["time"] = max(60, int(round(out["time"] * f)))
    for skill, xp in list((out.get("xp") or {}).items()):
        out["xp"][skill] = max(5, int(round(xp * f)))
    return out


def _wall_sources():
    """sheet -> its primary wall buildable (piece 0) from the confirmed walls file."""
    d = json.load(open(WALLS, encoding="utf-8"))
    src = {}
    for b in d["buildables"]:
        try:
            spr = b["stages"][0]["geometry"]["faces"]["W"]["layers"][0]["rows"][0][0]
        except (KeyError, IndexError, TypeError):
            continue
        sheet = spr.rpartition("_")[0]
        if b.get("pieceClass") == "wall" and sheet not in src:
            src[sheet] = b
    return src


def _faces(sprites):
    return {fc: {"layers": [{"rows": [[s]]}]} for fc, s in sprites.items()}


def _style(wall):
    return (wall.get("group") or {}).get("name") or wall["displayName"]


def _family_name(style, label):
    """Naming pass (2026-08-28): one menu entry per sheet + piece type, heights inside it.
    ('Brick Wall - Style 1', 'Lower Wall Corner') -> 'Brick Lower Wall Corner - Style 1';
    ('Wall - Style 2', 'Wall Overlay') -> 'Wall Overlay - Style 2'."""
    prefix, sep, suffix = style.partition(" - ")
    mat = prefix[:-len("Wall")].strip() if prefix.endswith("Wall") else prefix
    name = ("%s %s" % (mat, label)).strip()
    return "%s - %s" % (name, suffix) if sep else name


def _type_word(wall):
    """'Brick Walls' -> 'Brick', 'Walls' -> '' ."""
    wsub = (wall.get("subcategory") or "Walls").strip()
    return "" if wsub == "Walls" else wsub.replace(" Walls", "")


# ---------------------------------------------------------------------------------------------
# LOWER WALLS (pack tiles, real walls)
_LW_PIECES = [  # (key, label, plural, cost factor, pieceClass)
    ("wall", "Lower Wall", "Lower Walls", 1.0, "wall"),
    ("corner", "Lower Wall Corner", "Lower Wall Corners", 1.0, "corner"),
    ("pillar", "Lower Wall Pillar", "Lower Wall Pillars", 0.5, "pillar"),
]


# shared OverlayGuard Lua (kbw_tilepatch): refuse an edge that already has a wall
_FREE_EDGE = {"wall": "KBWCommunityFreeEdge.OnIsValid", "corner": "KBWCommunityFreeEdge.OnIsValidCorner"}


def build_lower_walls():
    src = _wall_sources()
    builds, missing = [], []
    for sheet in SHEETS:
        wall = src.get(sheet)
        if not wall:
            missing.append(sheet)
            continue
        style, tw = _style(wall), _type_word(wall)
        sub = ("%s Lower Walls" % tw).strip()
        st0 = wall["stages"][0]
        for key, label, plural, cost, pclass in _LW_PIECES:
            gid = "worldessentials.tikitown.lowerwall.%s_%s" % (sheet, key)
            for base, hslug, hlabel, frac in HEIGHTS:
                f = frac * cost
                s = lambda o: "%s_%d" % (sheet, base + o)
                if key == "wall":
                    sprites, obj = {"W": s(0), "N": s(1)}, {
                        "isThumpable": True, "dismantable": True,
                        "cornerSprite": s(2), "pillarSprite": s(3)}
                elif key == "corner":
                    sprites, obj = {"W": s(2), "N": s(2)}, {"isThumpable": True, "dismantable": True}
                else:
                    sprites, obj = {"W": s(3), "N": s(3)}, {
                        "dismantable": True, "blockAllSquare": False, "canPassThrough": True,
                        "canBarricade": False, "isCorner": True}
                stage = {"id": "built", "geometry": {"faces": _faces(sprites)},
                         "requirements": _scaled_requirements(st0.get("requirements") or {}, f),
                         "construction": _scaled_construction(st0.get("construction") or {}, f),
                         "object": obj}
                for hk in ("health", "skillBaseHealth"):
                    if isinstance(st0.get(hk), (int, float)):
                        stage[hk] = max(10, int(round(st0[hk] * frac)))
                cb = dict(st0["callbacks"]) if isinstance(st0.get("callbacks"), dict) else {}
                # e.g. brick canBePlastered.OnCreate is kept. The panel and corner must not replace
                # a player-built wall on their edge (KBW swaps those out): refuse occupied edges.
                # The pillar is walk-through, so KBW never replaces with it; it may stand by walls.
                if key in _FREE_EDGE:
                    assert "onIsValid" not in cb, (sheet, cb)
                    cb["onIsValid"] = _FREE_EDGE[key]
                if cb:
                    stage["callbacks"] = cb
                slug = "%s_%s_%s" % (sheet, key, hslug)
                builds.append({
                    "id": "worldessentials.tikitown.lowerwall.%s" % slug,
                    "allowSpriteReuse": True,
                    "translationKey": "IGUI_WETiki_lowerwall_%s" % slug,
                    "displayName": "%s (%s)" % (_family_name(style, label), hlabel),
                    "category": "Walls and Wall Finishes",
                    "subcategory": sub,
                    "material": wall.get("material", "Wood"),
                    "iconSprite": sprites["W"],
                    "placement": {"kind": "wall", "requiresFloor": False},
                    "tags": ["tikitown", "drazion", "world-essentials", "lower-wall"],
                    "pieceClass": pclass,
                    "group": {"id": gid, "name": _family_name(style, label),
                              "translationKey": "IGUI_WETiki_lowerwall_%s_%s_group" % (sheet, key),
                              "level": 1},
                    "stages": [stage],
                })
    return {"schemaVersion": 1, "category": "Walls and Wall Finishes",
            "source": ("TikiTown wall sheets, tiles 72-91 as REAL low walls (pack tiles unchanged): "
                       "3/4, 2/3, 1/2, 1/3, 1/4 height wall / corner / pillar, 60 sheets. Cost = the "
                       "sheet's wall recipe scaled by height."),
            "buildables": builds}, missing


# ---------------------------------------------------------------------------------------------
# WALL OVERLAYS (our copied tiles)
_PANEL_PLACE = {"kind": "overlay", "needToBeAgainstWall": True}
_PROP_PLACE = {"kind": "object", "requiresFloor": False}
_OVERLAY_OBJ = {"isThumpable": False, "canPassThrough": True, "blockAllSquare": False, "dismantable": True}
_OV_PIECES = [  # (key, label, plural, {face: offset}, placement, cost factor)
    ("panel", "Wall Overlay", "Wall Overlays", {"W": 0, "N": 1}, _PANEL_PLACE, 1.0),
    ("corner", "Wall Overlay Corner", "Wall Overlay Corners", {"W": 2}, _PROP_PLACE, 1.0),
    ("pillar", "Wall Overlay Pillar", "Wall Overlay Pillars", {"W": 3}, _PROP_PLACE, 0.5),
]


def build_overlays():
    src = _wall_sources()
    builds, missing = [], []
    for sheet in SHEETS:
        wall = src.get(sheet)
        if not wall:
            missing.append(sheet)
            continue
        style, tw = _style(wall), _type_word(wall)
        sub = ("%s Wall Overlays" % tw).strip()
        st0 = wall["stages"][0]
        for key, label, plural, faces, placement, cost in _OV_PIECES:
            gid = "worldessentials.tikitown.walloverlay.%s_%s" % (sheet, key)
            for base, hslug, hlabel, frac in HEIGHTS:
                f = frac * cost
                sprites = {fc: overlay_sprite(sheet, base + off) for fc, off in faces.items()}
                stage = {"id": "built", "geometry": {"faces": _faces(sprites)},
                         "requirements": _scaled_requirements(st0.get("requirements") or {}, f),
                         "construction": _scaled_construction(st0.get("construction") or {}, f),
                         "object": dict(_OVERLAY_OBJ)}
                if key != "panel":
                    stage["health"] = 150
                if key == "corner":
                    stage["callbacks"] = {"onIsValid": CORNER_ISVALID}
                slug = "%s_%s_%s" % (sheet, key, hslug)
                builds.append({
                    "id": "worldessentials.tikitown.walloverlay.%s" % slug,
                    "allowSpriteReuse": True,
                    "translationKey": "IGUI_WETiki_walloverlay_%s" % slug,
                    "displayName": "%s (%s)" % (_family_name(style, label), hlabel),
                    "tooltipKey": "Tooltip_KBW_DecorativeWallFixture",
                    "category": "Decorations and Landscaping",
                    "subcategory": sub,
                    "material": wall.get("material", "Wood"),
                    "iconSprite": next(iter(sprites.values())),
                    "placement": dict(placement),
                    "tags": ["tikitown", "drazion", "world-essentials", "wall-overlay"],
                    "pieceClass": "decoration",
                    "group": {"id": gid, "name": _family_name(style, label),
                              "translationKey": "IGUI_WETiki_walloverlay_%s_%s_group" % (sheet, key),
                              "level": 1},
                    "stages": [stage],
                })
    return {"schemaVersion": 1, "category": "Decorations and Landscaping",
            "source": ("TikiTown wall sheets, tiles 72-91 as WALL OVERLAYS on our own copied tiles "
                       "(KBWTikiTownWallOverlays, overlay-only props; pack tiles unchanged): 3/4 .. 1/4 "
                       "height panel / corner / pillar, 60 sheets. Needs pack=KBWTikiTownWallOverlays + "
                       "tiledef=kbwtikitown_walloverlays 8179 in mod.info."),
            "buildables": builds}, missing


# ---------------------------------------------------------------------------------------------
# copied tile art + tiledef
_TIKITOWN_PACK = (r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600\3046728955\mods"
                  r"\Drazions Tile Pack\common\media\texturepacks\tikitown_tiles.pack")
_PAGE = 2048


def _write_pack_multi(dest_path, tiles):
    """PZPK v1 texture pack with as many 2048x2048 pages as needed. tiles: [(name, RGBA Image)]."""
    from PIL import Image
    crops = []
    for name, im in tiles:
        bbox = im.getbbox() or (0, 0, 1, 1)
        crops.append((name, im.crop(bbox), bbox, im.size))
    pages, cur, x, y, rowh = [], [], 0, 0, 0
    for name, c, bbox, full in crops:
        if x + c.width > _PAGE:
            x, y, rowh = 0, y + rowh + 1, 0
        if y + c.height > _PAGE:
            pages.append(cur)
            cur, x, y, rowh = [], 0, 0, 0
        cur.append((name, c, x, y, bbox, full))
        x += c.width + 1
        rowh = max(rowh, c.height)
    if cur:
        pages.append(cur)

    def s(v):
        b = v.encode("utf-8")
        return struct.pack("<i", len(b)) + b
    out = bytearray(b"PZPK") + struct.pack("<ii", 1, len(pages))
    for pi, placed in enumerate(pages):
        h = 1
        while h < max(py + c.height for _n, c, _x, py, _b, _f in placed):
            h *= 2
        page = Image.new("RGBA", (_PAGE, h), (0, 0, 0, 0))
        for name, c, px, py, bbox, full in placed:
            page.paste(c, (px, py))
        buf = io.BytesIO()
        page.save(buf, "PNG", optimize=True)
        out += s("%s%d" % (OVERLAY_PACK, pi)) + struct.pack("<ii", len(placed), 1)
        for name, c, px, py, bbox, full in placed:
            out += s(name) + struct.pack("<8i", px, py, c.width, c.height, bbox[0], bbox[1], full[0], full[1])
        png = buf.getvalue()
        out += struct.pack("<i", len(png)) + png
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    open(dest_path, "wb").write(bytes(out))
    return len(pages), len(crops), len(out)


def write_overlay_assets(media_dir):
    """Copy tiles 72-91 of every sheet into KBWTikiTownWallOverlays: pack + tiledef in media_dir."""
    from PIL import Image
    import kbw_tilepatch as k
    cache = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_cache_walloverlays")
    names = ["%s_%d" % (sh, t) for sh in SHEETS for t in range(FIRST, FIRST + PER_SHEET)]
    k._extract_from_pack(_TIKITOWN_PACK, set(names), cache)
    tiles = []
    tilesets = {}    # tileset name -> {index: props}, in creation order

    def add(sprite, im, props):
        tsname, _sep, idx = sprite.rpartition("_")
        tilesets.setdefault(tsname, {})[int(idx)] = props
        tiles.append((sprite, im))

    for sh in SHEETS:
        for t in range(FIRST, FIRST + PER_SHEET):
            im = Image.open(os.path.join(cache, "%s_%d.png" % (sh, t))).convert("RGBA")
            add(overlay_sprite(sh, t), im, list(_COPY_PROPS[(t - FIRST) % 4]))
    # soundproofing copies (tikitown-props-14): their own small tileset in the same file
    import tikitown_soundproof as sp
    sp_names = {"%s_%d" % (sp.SHEET, i) for i in sp.SOUNDPROOF_SRC}
    k._extract_from_pack(_TIKITOWN_PACK, sp_names, cache)
    _v, tts, _o = k._parse(open(k._TIKITOWN_TILES, "rb").read())
    sp_src = tts[sp.SHEET.encode()][6]
    for i in sp.SOUNDPROOF_SRC:
        im = Image.open(os.path.join(cache, "%s_%d.png" % (sp.SHEET, i))).convert("RGBA")
        add(sp.copy_sprite(i), im, sp.copy_props(i, sp_src[i]))
    # mirrored props-14 tiles (Electrical Cabinet Generator's second facing): own tileset, same file
    import tikitown_props14 as p14
    from PIL import ImageOps
    m_names = {"%s_%d" % (p14.SHEET, i) for i in p14.MIRRORS}
    k._extract_from_pack(_TIKITOWN_PACK, m_names, cache)
    p14_src = tts[p14.SHEET.encode()][6]
    for i in p14.MIRRORS:
        im = Image.open(os.path.join(cache, "%s_%d.png" % (p14.SHEET, i))).convert("RGBA")
        # whole-tile left-right flip: the object stays centred on its square, only the facing changes
        add(p14.mirror_sprite(i), ImageOps.mirror(im), list(p14_src[i]))
    assert len({n for n, _im in tiles}) == len(tiles), "duplicate copied sprite names"
    npages, ntiles, size = _write_pack_multi(
        os.path.join(media_dir, "texturepacks", OVERLAY_PACK + ".pack"), tiles)
    cols = 8
    body = b""
    for ordinal, (tsname, by_index) in enumerate(tilesets.items(), 1):
        n = max(by_index) + 1
        rows = (n + cols - 1) // cols
        props = [by_index.get(j, []) for j in range(cols * rows)]
        if len(props) > MAX_TILES_PER_TILESET:
            raise RuntimeError("%s has %d tiles; the game allows %d per tileset"
                               % (tsname, len(props), MAX_TILES_PER_TILESET))
        # firstId: a unique ordinal per tileset within this file (as in the pack's own .tiles)
        body += k._ser_tileset([tsname.encode(), (tsname + ".png").encode(), cols, rows, ordinal,
                                cols * rows, props])
    blob = b"tdef" + struct.pack("<ii", 1, len(tilesets)) + body
    _v2, parsed, _o2 = k._parse(blob)
    assert all(t[5] <= MAX_TILES_PER_TILESET for t in parsed.values())
    open(os.path.join(media_dir, OVERLAY_TILEDEF_NAME + ".tiles"), "wb").write(blob)
    print("wall overlay tiles: %d tiles in %d tilesets (%s), %d pages, pack %.1f MB" % (
        ntiles, len(parsed), ", ".join("%s=%d" % (n.decode(), t[5]) for n, t in parsed.items()),
        npages, size / 1048576.0))
    return ntiles


MODINFO_LINES = ["pack=%s" % OVERLAY_PACK, "tiledef=%s %d" % (OVERLAY_TILEDEF_NAME, OVERLAY_TILEDEF_ID)]


def main():
    for build, out in ((build_overlays, OUT_OVERLAYS), (build_lower_walls, OUT_WALLS)):
        doc, missing = build()
        ids = [b["id"] for b in doc["buildables"]]
        assert len(ids) == len(set(ids)), "duplicate ids"
        # Write the buildables in a fixed pseudo-random order (md5 of the id), NOT generation order.
        # KBW's Registry:list() sorts every buildable by id with Kahlua's table.sort: a recursive
        # first-element-pivot quicksort whose recursion depth explodes on ordered runs. Kahlua
        # tables keep insertion order (LinkedHashMap), so these 900-entry families went in as
        # long ordered runs and pushed the depth past Kahlua's 3000-slot stack: "Stack overflow"
        # in partition_comp, KBW never finished loading (2026-11-08). Simulated depth: 482 in
        # generation order, 82 in this order (same as KBW + VE alone). Menu order is unaffected:
        # KBW sorts group members by level, then id.
        doc["buildables"].sort(key=lambda b: hashlib.md5(b["id"].encode("utf-8")).hexdigest())
        json.dump(doc, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        print("wrote %s (%d buildables)" % (out, len(ids)))
        if missing:
            print("MISSING wall source for: %s" % missing)


if __name__ == "__main__":
    main()
