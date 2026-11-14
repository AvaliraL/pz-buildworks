# -*- coding: utf-8 -*-
"""Generate 47_tikitown_entertainment.json (user, 2026-08-28): pieces from Drazion's
tikitown_entertainment_01.

  Stripper Pole            0 / 1   one piece, the two tiles are its W / N orientations (pack tiles)
  "Cheeky" Neon Sign       18 + 19  2 tiles on the north wall (x0 = 18, x1 = 19)
  "18+ XXX" Neon Sign      22      west wall
  Red Legs Neon Sign       23      north wall + mirrored copy for the west wall
  Ladies Legs Neon Sign    28 + 29 2 tiles on the west wall (y0 = 29, y1 = 28) + mirrored pair for
                                   the north wall (x0 = mirror 29, x1 = mirror 28)
  "GIRLS" Neon Sign        30 + 31 2 tiles on the west wall (y0 = 31, y1 = 30), no mirror (text)
  Hanging Bead Curtain     45 / 46 pack tiles. The pack calls it a "Door" but gives it no door flags and
                                   no open art: it is a walk-through hanging decoration, kept as the pack
                                   defines it (user: "leave it as such"). Nothing blocks movement or sight.
Joins from the pack's SpriteGridPos (consistent with the art).

The neon signs are built on OUR COPIES (tileset KBWTikiTownEntertainment in the TikiTown wall-overlay
pack, written by tikitown_wall_overlays.write_overlay_assets): the pack tiles are WallOverlay
moveables, which World Essentials builds as a bare sprite attached to the wall, so the light could
never work. The copies drop WallOverlay and keep the pack's lightswitch + light colour, so KBW builds
a real light switch object (on / off, needs power). Mirrors are whole-tile flips with the wall and
facing swapped (attachedN <-> attachedW, Facing S <-> E). NOT yet tested in game.
"""
import json
import os

SHEET = "tikitown_entertainment_01"
OUT = r"c:\Users\josep\Kiro\zomboid\tikitown\47_tikitown_entertainment.json"
COPY_TILESET = "KBWTikiTownEntertainment"
MIRROR = 1000
# copy order = index in COPY_TILESET (APPEND only)
COPY_SRC = [18, 19, 22, 23, 23 + MIRROR, 28, 29, 28 + MIRROR, 29 + MIRROR, 30, 31]
_SWAP = {b"attachedN": b"attachedW", b"attachedW": b"attachedN", b"attachedE": b"attachedS",
         b"attachedS": b"attachedE"}
_FACING_SWAP = {b"S": b"E", b"E": b"S", b"N": b"W", b"W": b"N"}


def copy_sprite(s):
    return "%s_%d" % (COPY_TILESET, COPY_SRC.index(s))


def is_mirror(s):
    return s >= MIRROR


def source_index(s):
    return s % MIRROR


# In game 2026-11-13: "18+", "GIRLS" and Ladies Legs did not build as lights, while Cheeky (18/19)
# and Red Legs (23) did. All carry lightswitch + a light colour, but the failing pack tiles are
# hammer WallObject moveables (MoveType = WallObject, Pick/PlaceTool, no IsMoveAble) where the working
# ones are plain IsMoveAble tiles. Our copies of the failing ones get the working tiles' layout.
_WALLOBJECT_SRC = (22, 28, 29, 30, 31)
_WALLOBJECT_DROP = (b"MoveType", b"PickUpTool", b"PlaceTool")
# Default bulb colour (user: GIRLS + 18+ pink, Ladies Legs orange), vanilla LightBulbPink /
# LightBulbOrange ColorRed / Green / Blue.
_PINK = (255, 20, 147)
_ORANGE = (255, 128, 0)
_LIGHT_COLOR = {22: _PINK, 30: _PINK, 31: _PINK, 29: _ORANGE}
# Ladies Legs: only one of its two tiles is a light (user); 28 becomes plain decoration.
_NO_LIGHT_SRC = (28,)
_LIGHT_KEYS = (b"lightswitch", b"LightRadius", b"lightR", b"lightG", b"lightB")


def copy_props(s, src_props):
    """The pack tile's props without WallOverlay (a real light-switch wall object); mirrors swap the
    wall edge and the facing."""
    out = []
    src = source_index(s)
    for k, v in src_props:
        if k == b"WallOverlay":
            continue
        if src in _WALLOBJECT_SRC and k in _WALLOBJECT_DROP:
            continue
        if src in _NO_LIGHT_SRC and k in _LIGHT_KEYS:
            continue
        if src in _LIGHT_COLOR and k in (b"lightR", b"lightG", b"lightB"):
            continue
        if is_mirror(s):
            if k in _SWAP:
                k = _SWAP[k]
            elif k == b"Facing":
                v = _FACING_SWAP.get(v, v)
            elif k == b"SpriteGridPos":       # (0, y) on the west wall -> (y, 0) on the north wall
                a, b = v.split(b",")
                v = b + b"," + a
        out.append((k, v))
    keys = {k for k, _v in out}
    if src in _WALLOBJECT_SRC and b"IsMoveAble" not in keys:
        out.append((b"IsMoveAble", b""))
    if src in _LIGHT_COLOR:
        r, g, b = _LIGHT_COLOR[src]
        out += [(b"lightR", str(r).encode()), (b"lightG", str(g).encode()), (b"lightB", str(b).encode())]
    return sorted(out)


def copy_tiles(tilesets):
    """[(source sprite, copy sprite, props, mirror?)] in tileset order."""
    src = tilesets[SHEET.encode()][6]
    return [("%s_%d" % (SHEET, source_index(s)), copy_sprite(s), copy_props(s, src[source_index(s)]), is_mirror(s))
            for s in COPY_SRC]


def _spr(i):
    return "%s_%d" % (SHEET, i)


def _layers(rows):
    return {"layers": [{"rows": rows}]}


def _item(n, item, amount, drain=False):
    r = {"id": "source_material_%d" % n, "role": "consumable" if drain else "material",
         "mode": "drain" if drain else "consume", "resourceType": "Item", "items": [item], "amount": 1 if drain else amount}
    if drain:
        r["uses"] = amount
    return r


def _tool(tag, ident):
    return {"id": ident, "role": "tool", "mode": "keep", "resourceType": "Item", "tags": [tag], "amount": 1}


def _neon_cost(tiles):
    return {"inputs": [_tool("base:screwdriver", "tool_screwdriver"),
                       _item(1, "Base.ElectricWire", 2 * tiles), _item(2, "Base.ElectronicsScrap", 4 * tiles),
                       _item(3, "Base.SmallSheetMetal", 1), _item(4, "Base.LightBulb", tiles)],
            "skills": {"Electricity": 3}}


NEON_CON = {"time": 120, "timedAction": "BuildWallNoTool", "completionSound": "BuildMetalStructureSmall",
            "xp": {"Electricity": 20}, "category": "Electrical"}
WALL = {"kind": "object", "requiresFloor": True, "needToBeAgainstWall": True}
FLOOR = {"kind": "object", "requiresFloor": True}
DECOR_OBJECT = {"isThumpable": False, "canPassThrough": True, "blockAllSquare": False, "dismantable": True}


def _b(slug, name, cat, sub, faces, req, con, obj, placement, group=None, material="Metal"):
    first = next(iter(faces.values()))["layers"][0]["rows"][0][0]
    b = {"id": "worldessentials.tikitown.entertainment_%s" % slug, "allowSpriteReuse": True,
         "translationKey": "IGUI_WETiki_entertainment_%s" % slug, "displayName": name,
         "category": cat, "subcategory": sub, "material": material, "materialTags": [material],
         "iconSprite": first, "placement": dict(placement),
         "tags": ["tikitown", "drazion", "world-essentials", "entertainment"],
         "stages": [{"id": "built", "geometry": {"faces": faces}, "requirements": req,
                     "construction": dict(con), "object": dict(obj)}]}
    if group:
        b["group"] = group
    return b


def build_document():
    c = copy_sprite
    neon = ("Decorations and Landscaping", "Neon Signs")
    out = []
    pole_req = {"inputs": [_tool("base:wrench", "tool_wrench"), _item(1, "Base.MetalPipe", 2),
                           _item(2, "Base.Screws", 6)], "skills": {"MetalWelding": 1}}
    pole_con = {"time": 100, "timedAction": "BuildLowMetal", "completionSound": "BuildMetalStructureSmall",
                "xp": {"MetalWelding": 10}, "category": "Metalworking"}
    # the two pack tiles are one pole seen from two sides (user, 2026-08-28: orientations, not
    # styles). The pack gives them no Facing: 0 = W, 1 = N.
    out.append(_b("pole", "Stripper Pole", "Furniture and Appliances", "Entertainment",
                  {"W": _layers([[_spr(0)]]), "N": _layers([[_spr(1)]])}, pole_req, pole_con,
                  {"isThumpable": True, "dismantable": True}, FLOOR))
    out.append(_b("neon_cheeky", '"Cheeky" Neon Sign', neon[0], neon[1],
                  {"N": _layers([[c(18), c(19)]])}, _neon_cost(2), NEON_CON, DECOR_OBJECT, WALL))
    out.append(_b("neon_18plus", '"18+ XXX" Neon Sign', neon[0], neon[1],
                  {"W": _layers([[c(22)]])}, _neon_cost(1), NEON_CON, DECOR_OBJECT, WALL))
    out.append(_b("neon_red_legs", "Red Legs Neon Sign", neon[0], neon[1],
                  {"N": _layers([[c(23)]]), "W": _layers([[c(23 + MIRROR)]])}, _neon_cost(1), NEON_CON,
                  DECOR_OBJECT, WALL))
    out.append(_b("neon_ladies_legs", "Ladies Legs Neon Sign", neon[0], neon[1],
                  {"W": _layers([[c(29)], [c(28)]]),
                   "N": _layers([[c(29 + MIRROR), c(28 + MIRROR)]])}, _neon_cost(2), NEON_CON, DECOR_OBJECT, WALL))
    out.append(_b("neon_girls", '"GIRLS" Neon Sign', neon[0], neon[1],
                  {"W": _layers([[c(31)], [c(30)]])}, _neon_cost(2), NEON_CON, DECOR_OBJECT, WALL))
    out.append(_b("bead_curtain", "Hanging Bead Curtain", "Decorations and Landscaping", "Curtains",
                  {"N": _layers([[_spr(45)]]), "W": _layers([[_spr(46)]])},
                  {"inputs": [_item(1, "Base.Twine", 3, drain=True), _item(2, "Base.Plank", 1)]},
                  {"time": 80, "timedAction": "BuildWallNoTool", "completionSound": "BuildWoodenStructureSmall",
                   "xp": {"Woodwork": 5}, "category": "Carpentry"},
                  DECOR_OBJECT, FLOOR, material="Fabric"))
    return {"schemaVersion": 1, "category": "Decorations and Landscaping",
            "source": ("TikiTown tikitown_entertainment_01 (Drazion's Tilepack): stripper poles, neon signs (our "
                       "light-switch copies KBWTikiTownEntertainment_0..10) and the hanging bead curtain. "
                       "Generated by pz_craft_loops/tikitown_entertainment.py."),
            "buildables": out}


def main():
    doc = build_document()
    ids = [b["id"] for b in doc["buildables"]]
    assert len(ids) == len(set(ids))
    json.dump(doc, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("wrote %s (%d buildables)" % (OUT, len(ids)))


if __name__ == "__main__":
    main()
