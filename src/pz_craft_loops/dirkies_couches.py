# -*- coding: utf-8 -*-
"""
Generator: Dirkies couches + corner couches -> KBW buildables.

Sources (Community Tile Pack / Daddy Dirkie BuildingMenu addon):
  d_furniture_couches_01  (8 cols x 16 rows tileset; firstId 9):
      9 color/style variants, each with a 2-TILE couch + a 1-TILE armchair.
      The addon registered 27 "objects" because its build fn handles only 2 facings at a
      time, so it split each 2-tile couch into two entries (S/E pair + N/W pair). The .tiles
      metadata (GroupName/CustomName/Facing/SpriteGridPos) shows they are ONE couch each:
        couch (Custom=Couch):  S = [idx@(0,0), idx@(1,0)]  (horizontal row)
                               E = [idx@(0,0); idx@(0,1)]  (vertical column)
                               N = [idx@(0,0), idx@(1,0)]
                               W = [idx@(0,0); idx@(0,1)]
        armchair (Custom=Chair): 1 tile, 4 facings  S=base, E=base+1, W=base+2, N=base+3.
      So we emit 9 two-tile couches + 9 armchairs (merged, all 4 facings), not 27.

  d_location_sofaking (8 cols x 8 rows tileset; firstId 10):
      4 single-tile 90-degree CORNER couches (teal/purple/pink/orange). Each color is a block
      of 4 consecutive cells = its 4 corner facings. The addon never built these as couches
      (it mis-used other cells as counters); this is net-new content. Facing order per the
      user-annotated art (left->right in the sheet): base+0 = S, +1 = N, +2 = E, +3 = W.
        Teal 28-31, Purple 36-39, Pink 44-47, Orange 52-55 (cells are 128x256).
      (Pack tags teal/purple/pink IsMoveAble+GroupName="Couch Corner" all with Facing=S;
       orange 60-63 carry no props. We set all 4 faces explicitly, so neither matters for
       rendering/placement.)

Corner couches combine with the straight couches to build L- and C-shapes.

NOT SHIPPING AS-IS (user, 2026-08-28): the 4 standalone corner pieces stay test-only (forced
In Progress in build_merged_test_mod). Plan: custom 3-tile L-shaped couches per color = the
2 tiles of the same-color Comfy couch as the two ends + this corner tile in the middle. No
straight middle-couch tile exists, so each L is limited to 3 tiles. Exclude the corner_* pieces
from any shipping builder (build_community_mod SRC_DEFS) until the L couches replace them.

Model mirrors dirkies_bedroom.py. Couches are furniture (no container); object =
{isThumpable, canPassThrough, isCorner, dismantable}, matching the addon couch props.

NOT yet game-tested: the per-facing 2-tile sprite arrangement (S/N horizontal, E/W vertical)
is derived from SpriteGridPos; verify in game and swap row/col order here if a facing is wrong.
"""

COUCH_SHEET = "d_furniture_couches_01"
SOFA_SHEET = "d_location_sofaking"

OUT = r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables\62_community_dirkies_couches.json"

# ---------------------------------------------------------------------------
# 9 two-tile couches. Per variant we give the 4 facings as (a, b) sprite pairs, where a is the
# SpriteGridPos=(0,0) tile and b is the second tile. S/N pairs are a HORIZONTAL row [[a, b]];
# E/W pairs are a VERTICAL column [[a],[b]].  (Order confirmed from SpriteGridPos.)
#   Blue Comfy    S(0,1)  E(3,2)  N(6,7)  W(5,4)
# For every group the offsets within the group's 12-index block are identical, so we derive them
# from a single base once the base is known. Group blocks (addon order), base = S-left index:
# Derived from the pack .tiles Facing + SpriteGridPos (see _couch_all_pairs.py). Order per entry:
# (name, S_a, S_b, E_a, E_b, N_a, N_b, W_a, W_b). S/N are a horizontal row, E/W a vertical column.
COUCH_VARIANTS = [
    ("Blue Comfy",       0, 1, 3, 2, 6, 7, 5, 4),
    ("Purple Comfy",     16, 17, 19, 18, 22, 23, 21, 20),
    ("Blue Lazy",        24, 25, 27, 26, 30, 31, 29, 28),
    ("Pink Lazy",        40, 41, 43, 42, 46, 47, 45, 44),
    ("Pink Comfy",       48, 49, 51, 50, 54, 55, 53, 52),
    ("Dark Blue Comfy",  66, 67, 65, 64, 70, 71, 69, 68),
    ("Dark Brown Comfy", 82, 83, 81, 80, 86, 87, 85, 84),
    ("Dark Green Comfy", 90, 91, 89, 88, 94, 95, 93, 92),
    ("Dark Red Comfy",   106, 107, 105, 104, 110, 111, 109, 108),
]

# 9 armchairs: explicit (name, S, E, W, N) indices -- the facing layout is NOT uniform across
# groups (Comfy + *_Lazy start at S; the Dirk* Lazy groups start at E), so take Facing straight
# from the pack .tiles instead of assuming an offset pattern.
ARMCHAIR_VARIANTS = [
    # name,              S,   E,   W,   N
    ("Blue Comfy",       12,  13,  14,  15),
    ("Purple Comfy",     8,   9,   10,  11),
    ("Blue Lazy",        36,  37,  38,  39),
    ("Pink Lazy",        32,  33,  34,  35),
    ("Pink Comfy",       56,  57,  58,  59),
    ("Dark Blue Lazy",   73,  72,  74,  75),
    ("Dark Brown Lazy",  77,  76,  78,  79),
    ("Dark Green Lazy",  97,  96,  98,  99),
    ("Dark Red Lazy",    101, 100, 102, 103),
]

# Corner couches on sofaking: (name, S_base) with N=base+1, E=base+2, W=base+3.
# Rev 2 (game test): sofaking cells are 128x256 (1792px = 7 rows), not 128x224. The earlier
# 36/44/52/60 bases were one row late in game (teal showed purple, ..., orange showed nothing).
CORNER_COLORS = [
    ("Teal", 28),
    ("Purple", 36),
    ("Pink", 44),
    ("Orange", 52),
]


def _spr(sheet, idx):
    return "%s_%d" % (sheet, idx)


def _one(sheet, idx):
    return {"layers": [{"rows": [[_spr(sheet, idx)]]}]}


def _row2(sheet, a, b):
    # two tiles side by side (horizontal) -> one row of 2
    return {"layers": [{"rows": [[_spr(sheet, a), _spr(sheet, b)]]}]}


def _col2(sheet, a, b):
    # two tiles stacked (vertical) -> two rows of 1
    return {"layers": [{"rows": [[_spr(sheet, a)], [_spr(sheet, b)]]}]}


def _wood_recipe(planks, nails, thread, wood=4):
    return {
        "inputs": [
            {"id": "tool_hammer", "role": "tool", "mode": "keep",
             "resourceType": "Item", "tags": ["base:hammer"], "amount": 1},
            {"id": "source_material_1", "role": "material", "mode": "consume",
             "resourceType": "Item", "items": ["Base.Plank"], "amount": planks},
            {"id": "source_material_2", "role": "material", "mode": "consume",
             "resourceType": "Item", "items": ["Base.Nails"], "amount": nails},
            {"id": "source_material_3", "role": "material", "mode": "consume",
             "resourceType": "Item", "items": ["Base.Thread"], "amount": thread},
        ],
        "skills": {"Woodwork": wood},
    }


def _construction(xp=40, time=200):
    return {"time": time, "timedAction": "BuildWoodenStructureSmall",
            "completionSound": "BuildWoodenStructureLarge", "xp": {"Woodwork": xp},
            "category": "Carpentry"}


def _base(slug, display, icon_sprite):
    bid = "community.dirkies.couches.%s" % slug
    return {
        "id": bid,
        "allowSpriteReuse": True,
        "translationKey": "IGUI_dirkies_couches_%s" % slug,
        "displayName": display,
        "tooltipKey": "Tooltip_craft_couchDesc",
        "category": "Furniture and Appliances",
        "subcategory": "Seating",
        "material": "Wood",
        "materialTags": ["Wood"],
        "iconSprite": icon_sprite,
        "placement": {"kind": "object", "requiresFloor": True},
        "tags": ["community-tilepack", "dirkies", "couches"],
    }


def _couch_object():
    return {"isThumpable": True, "dismantable": True,
            "canPassThrough": True, "isCorner": True}


def _slug(name):
    return name.lower().replace(" ", "_")


def _two_couch(v):
    name, sa, sb, ea, eb, na, nb, wa, wb = v
    slug = "couch_%s" % _slug(name)
    b = _base(slug, "%s Couch" % name, _spr(COUCH_SHEET, sa))
    b["stages"] = [{
        "id": "built",
        "geometry": {"faces": {
            "S": _row2(COUCH_SHEET, sa, sb),
            "N": _row2(COUCH_SHEET, na, nb),
            "E": _col2(COUCH_SHEET, ea, eb),
            "W": _col2(COUCH_SHEET, wa, wb),
        }},
        "requirements": _wood_recipe(6, 6, 4),
        "construction": _construction(xp=45, time=220),
        "object": _couch_object(),
    }]
    return b


def _armchair(name, s, e, w, n):
    slug = "armchair_%s" % _slug(name)
    b = _base(slug, "%s Armchair" % name, _spr(COUCH_SHEET, s))
    b["stages"] = [{
        "id": "built",
        "geometry": {"faces": {
            "S": _one(COUCH_SHEET, s),
            "E": _one(COUCH_SHEET, e),
            "W": _one(COUCH_SHEET, w),
            "N": _one(COUCH_SHEET, n),
        }},
        "requirements": _wood_recipe(4, 4, 3),
        "construction": _construction(xp=30, time=150),
        "object": _couch_object(),
    }]
    return b


def _corner_couch(color_word, base):
    # S=base+0, N=base+1, E=base+2, W=base+3
    s, n, e, w = base, base + 1, base + 2, base + 3
    slug = "corner_%s" % color_word.lower()
    b = _base(slug, "%s Corner Couch" % color_word, _spr(SOFA_SHEET, s))
    b["stages"] = [{
        "id": "built",
        "geometry": {"faces": {
            "S": _one(SOFA_SHEET, s),
            "N": _one(SOFA_SHEET, n),
            "E": _one(SOFA_SHEET, e),
            "W": _one(SOFA_SHEET, w),
        }},
        "requirements": _wood_recipe(5, 5, 4),
        "construction": _construction(xp=40, time=200),
        "object": _couch_object(),
    }]
    return b


# ---------------------------------------------------------------------------
# L-SHAPED CORNER COUCHES (user 2026-08-28): corner + right end + left end, equal sides, 3 tiles.
# Each color = sofaking corner tile + the same-colour Comfy couch's two END tiles. Orange has no
# matching straight couch, so only teal / purple / pink are built.
#   (name, corner base (S,N,E,W = +0..+3), Comfy couch base: S a,b = +0,+1  E = +3,+2  N = +6,+7  W = +5,+4)
#   The end tiles come from the generated single-tile tileset KBWCommunityLCouch (colour*8 + offset:
#   Teal 0, Purple 8, Pink 16, Orange 24 = recoloured Pink). Copies of the Comfy end tiles WITHOUT
#   the 2-tile sprite grid, so they ghost / pick up as single tiles.
_LC = "KBWCommunityLCouch"
L_COUCHES = [("Teal", 28, 0, _LC), ("Purple", 36, 8, _LC), ("Pink", 44, 16, _LC), ("Orange", 52, 24, _LC)]
# corner tiles: copies of these sofaking bases at KBWCommunityLCouch_32 + colour*4 (same order)
_CORNER_BASES = [28, 36, 44, 52]
# The compositor render (_lcomp) shows ONE corner variant makes a clean L per rotation:
#   rot0 corner NW -> S(+0)   rot1 NE -> W(+3)   rot2 SE -> N(+1)   rot3 SW -> E(+2)
# KBW face keys cycle W,N,E,S in game, so W=rot0 N=rot1 E=rot2 S=rot3 (clockwise).
# 'A' = arm along x (S/N-facing couch end), 'B' = arm along y (E/W-facing couch end), both
# the end tile pointing AWAY from the corner. The corner is always the anchor cell (dx 0, dy 0);
# `false` = KBW's empty-cell token.
#   rot0: backs N+W  A = S-face east end (+1)   B = E-face south end (+2)   [[C,A],[B,_]]
#   rot1: backs N+E  A = S-face west end (+0)   B = W-face south end (+4)   [[A,C],[_,B]]  x -1
#   rot2: backs S+E  A = N-face west end (+6)   B = W-face north end (+5)   [[_,B],[A,C]]  x -1 y -1
#   rot3: backs S+W  A = N-face east end (+7)   B = E-face north end (+3)   [[B,_],[C,A]]  y -1


def _l_faces(corner_base, couch_base, couch_sheet=None):
    sheet = couch_sheet or COUCH_SHEET

    def c(v):
        # our depth-free copy of the sofaking corner (kbw_tilepatch.L_COUCH_CORNER_SOURCES), not
        # the pack tile: the pack's depth map made the teal corner render wrong (2026-08-28)
        return "%s_%d" % (_LC, 32 + _CORNER_BASES.index(corner_base) * 4 + v)

    def k(off):
        return _spr(sheet, couch_base + off)

    F = False
    return {
        "W": {"layers": [{"rows": [[c(0), k(1)], [k(2), F]]}]},
        "N": {"layers": [{"x": -1, "rows": [[k(0), c(3)], [F, k(4)]]}]},
        "E": {"layers": [{"x": -1, "y": -1, "rows": [[F, k(5)], [k(6), c(1)]]}]},
        "S": {"layers": [{"y": -1, "rows": [[k(3), F], [c(2), k(7)]]}]},
    }


def _l_couch(color_word, corner_base, couch_base, couch_sheet=None):
    slug = "lcouch_%s" % color_word.lower()
    b = _base(slug, "%s L-Shaped Couch" % color_word,
              "%s_%d" % (_LC, 32 + _CORNER_BASES.index(corner_base) * 4))
    b["stages"] = [{
        "id": "built",
        "geometry": {"faces": _l_faces(corner_base, couch_base, couch_sheet)},
        "requirements": _wood_recipe(11, 11, 8),
        "construction": _construction(xp=60, time=260),
        "object": _couch_object(),
    }]
    return b


def build_document():
    builds = []
    for v in COUCH_VARIANTS:
        builds.append(_two_couch(v))
    for name, s, e, w, n in ARMCHAIR_VARIANTS:
        builds.append(_armchair(name, s, e, w, n))
    # the standalone single-tile corner couches (_corner_couch) are NOT shipped: only the L couches
    for color_word, cbase, kbase, ksheet in L_COUCHES:
        builds.append(_l_couch(color_word, cbase, kbase, ksheet))
    return {
        "schemaVersion": 1,
        "category": "Furniture and Appliances",
        "source": ("Dirkies d_furniture_couches_01 (9 two-tile couches + 9 armchairs, merged to "
                   "all-4-facings from the addon's split S/E and N/W entries) + d_location_sofaking "
                   "corner couches (4 colors teal/purple/pink/orange, 1-tile 4-facing 90-degree "
                   "corners for L/C-shape designs). Facings/grid from the pack .tiles "
                   "(Facing/SpriteGridPos); corners net-new (addon never built them). Props mirror "
                   "the addon couch: isThumpable/canPassThrough/isCorner."),
        "buildables": builds,
    }


def main():
    import json
    doc = build_document()
    json.dump(doc, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    ids = [b["id"] for b in doc["buildables"]]
    dups = sorted(set(i for i in ids if ids.count(i) > 1))
    assert not dups, "dup ids: %s" % dups
    print("wrote %s" % OUT)
    print("two-tile couches: %d  armchairs: %d  corners: %d  total=%d  unique=%d"
          % (len(COUCH_VARIANTS), len(ARMCHAIR_VARIANTS), 0, len(ids), len(set(ids))))


if __name__ == "__main__":
    main()
