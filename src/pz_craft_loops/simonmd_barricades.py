# -*- coding: utf-8 -*-
"""Generate zomboid/simonmd/04_simonmd_barricades.json (user, 2026-11-16): Simon MD's heavy barrier fences
and low "Do Not Cross" barriers, sheet barricades_Simon_MD (pack pages SimonMDsTiles32 / 33), for
"World Essentials - Raven Creek Buildworks" (gated on RavenCreek_B42).

The B41 Building Menu Simon MD addon does not use this sheet, so the layout comes from the user (pack
viewer) and the art, and the costs are our own first pass.
The tiles carry no wall flags: each is a solid object filling its square (heavy: `solid`, low: `solidtrans`).

Heavy barrier fences are TWO storeys tall (user): lower tile on the ground floor, its top tile (razor wire)
on the floor above, as two layers of one face (KBW Matrix: layer index = storey):
  lower / top: 56/57, 62/63, 64/65, 58/59, 60/61, 66/67, 68/69, 70/71
  By the art: 58-61 draw on the west half (a north-south run), 68-71 on the north half (east-west run);
  60<->68 and 58<->70 are the same panel for the two walls (pixel counts match), 62<->66 likewise (wider);
  56/57 and 64/65 are free-standing posts.
Low barriers (user): 73+74 one piece, 75+76 another, both two wide. Composited: 73 (west) + 74 (east) join
along the north wall; 76 (north) + 75 (south) along the west wall, so they are the same barrier for the
two walls. 72 and 77 are the low corners.
2026-11-17 (user): inner and outer corners are orientations of ONE piece (heavy 56/57 inner + 64/65 outer;
low 77 inner + 72 outer), and the heavy fence gets a completed 2-wide version (straight 60 + end 58 on
the W wall, 68 + 70 on the N wall, both storeys), costing two singles.
NOT yet tested in game. Raven Creek ships no depth maps for this sheet: the pieces use the pack tiles as
they are; if they show draw-order problems in game, they get depth copies like the secret cabinet.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kbw_tilepatch as k   # noqa: E402

SHEET = "barricades_Simon_MD"
OUT = r"c:\Users\josep\Kiro\zomboid\simonmd\04_simonmd_barricades.json"
RC_TILES = (r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600\3821823518\mods"
            r"\RavenCreek_B42\common\media\LCB42_SimonMDsTiles.tiles")
PREFIX = "worldessentials.simonmd.barricade_"


def _s(i):
    return "%s_%d" % (SHEET, i)


def _tool(i, tags, flags=None):
    d = {"id": i, "role": "tool", "mode": "keep", "resourceType": "Item", "tags": tags, "amount": 1}
    if flags:
        d["flags"] = flags
    return d


def _mat(i, items, n):
    return {"id": i, "role": "material", "mode": "consume", "resourceType": "Item", "items": items, "amount": n}


def _drain(i, item, uses):
    return {"id": i, "role": "consumable", "mode": "drain", "resourceType": "Item", "items": [item], "uses": uses}


# first-pass costs (ours; no source recipe exists for this sheet)
HEAVY = {"inputs": [
    _tool("welding_mask", ["base:weldingmask"]),
    _mat("sheet_metal", ["Base.SheetMetal"], 4), _mat("metal_bars", ["Base.MetalBar", "Base.MetalPipe"], 4),
    _mat("barbed_wire", ["Base.BarbedWire"], 2),
    _drain("concrete", "Base.BucketConcreteFull", 4),
    _drain("torch_fuel", "Base.BlowTorch", 4), _drain("welding_rods", "Base.WeldingRods", 2)],
    "skills": {"MetalWelding": 4, "Masonry": 2}}
POST = {"inputs": [
    _tool("welding_mask", ["base:weldingmask"]),
    _mat("sheet_metal", ["Base.SheetMetal"], 2), _mat("metal_bars", ["Base.MetalBar", "Base.MetalPipe"], 2),
    _mat("barbed_wire", ["Base.BarbedWire"], 1),
    _drain("concrete", "Base.BucketConcreteFull", 2),
    _drain("torch_fuel", "Base.BlowTorch", 2), _drain("welding_rods", "Base.WeldingRods", 1)],
    "skills": {"MetalWelding": 3, "Masonry": 2}}
LOW = {"inputs": [
    _tool("tool_hammer", ["base:hammer"], ["Prop1", "MayDegradeVeryLight"]),
    _mat("planks", ["Base.Plank"], 3), _mat("nails", ["Base.Nails"], 4),
    _drain("concrete", "Base.BucketConcreteFull", 2)],
    "skills": {"Woodwork": 2, "Masonry": 1}}
LOW_SINGLE = {"inputs": [
    _tool("tool_hammer", ["base:hammer"], ["Prop1", "MayDegradeVeryLight"]),
    _mat("planks", ["Base.Plank"], 2), _mat("nails", ["Base.Nails"], 2),
    _drain("concrete", "Base.BucketConcreteFull", 1)],
    "skills": {"Woodwork": 2, "Masonry": 1}}


def _scaled(req, n):
    """`req` with every material / consumable amount times n (tools unchanged)."""
    import copy
    r = copy.deepcopy(req)
    for i in r["inputs"]:
        if i["role"] != "tool":
            key = "uses" if "uses" in i else "amount"
            i[key] = int(round(i[key] * n))
    return r


# the 3-wide heavy fence: 1st pass three singles (12 sheets); halved (user 2026-11-17: "12 sheets for 3 tiles
# is a lot") -> 1.5 singles: 6 sheets, 6 bars, 3 barbed wire, 6 concrete / torch uses, 3 rods
HEAVY_3WIDE = _scaled(HEAVY, 1.5)


def _construction(kind):
    if kind == "heavy2":
        return {"time": 1000, "timedAction": "BuildWallMetal", "completionSound": "BuildMetalStructureMedium",
                "xp": {"MetalWelding": 65, "Masonry": 35}, "category": "Welding"}
    if kind in ("heavy", "post"):
        return {"time": 400 if kind == "heavy" else 250, "timedAction": "BuildWallMetal",
                "completionSound": "BuildMetalStructureMedium",
                "xp": {"MetalWelding": 25, "Masonry": 15} if kind == "heavy" else {"MetalWelding": 15, "Masonry": 10},
                "category": "Welding"}
    return {"time": 250, "timedAction": "BuildWallNoTool", "completionSound": "BuildWoodenStructureLarge",
            "xp": {"Woodwork": 10, "Masonry": 10}, "category": "Masonry"}


def _tall(lower, top):
    """One face, two storeys: the lower tile on the ground floor, its top tile on the floor above."""
    return {"layers": [{"rows": [[_s(lower)]]}, {"rows": [[_s(top)]]}]}


# (slug, name, faces, cost, kind, group slug, level)
PIECES = [
    ("heavy_1", "Heavy Barrier Fence 1", {"W": _tall(60, 61), "N": _tall(68, 69)}, HEAVY, "heavy", "heavy", 1),
    ("heavy_2", "Heavy Barrier Fence 2", {"W": _tall(58, 59), "N": _tall(70, 71)}, HEAVY, "heavy", "heavy", 2),
    ("heavy_wide", "Heavy Barrier Fence (Wide)", {"W": _tall(62, 63), "N": _tall(66, 67)}, HEAVY, "heavy", "heavy", 3),
    # 2 wide, completed (user 2026-11-17, like the scrap fences' 2-tile pieces): straight panel + end panel.
    # 58-61 stand on a square's SOUTH edge and 68-71 on its EAST edge (left / right half of the image), so the
    # run goes west -> east for 58 + 60 and north -> south for 70 + 68 (user, in game: the first layout
    # laid them along the other axis, as two parallel panels). End panels 58 / 70 at the outer ends.
    # 3 wide (user 2026-11-17: "this wall is meant to have 3 wide sections"): the 2-wide run plus the Wide
    # piece at its open end, so both ends have their sloped base. W -> E 58 60 62, N -> S 70 68 66
    ("heavy_3wide", "Heavy Barrier Fence (3 Wide)",
     {"N": {"layers": [{"rows": [[_s(58), _s(60), _s(62)]]}, {"rows": [[_s(59), _s(61), _s(63)]]}]},
      "W": {"layers": [{"rows": [[_s(70)], [_s(68)], [_s(66)]]}, {"rows": [[_s(71)], [_s(69)], [_s(67)]]}]}},
     HEAVY_3WIDE, "heavy2", "heavy", 4),
    # corners (user 2026-11-17): inner and outer are orientations of one piece. Inner = concave toward the
    # viewer (56, low 77), outer = convex (64, low 72)
    ("heavy_corner", "Heavy Barrier Corner", {"W": _tall(56, 57), "N": _tall(64, 65)}, POST, "post", "heavy", 5),
    ("low_sign", "Low Barrier (Do Not Cross)",
     {"N": {"layers": [{"rows": [[_s(73), _s(74)]]}]}, "W": {"layers": [{"rows": [[_s(76)], [_s(75)]]}]}},
     LOW, "low", "low", 1),
    ("low_corner", "Low Barrier Corner", {"W": {"layers": [{"rows": [[_s(77)]]}]},
                                          "N": {"layers": [{"rows": [[_s(72)]]}]}}, LOW_SINGLE, "low", "low", 2),
]
GROUPS = {"heavy": ("Heavy Barrier Fences", "IGUI_WESimon_barricade_heavy_group"),
          "low": ("Low Concrete Barriers", "IGUI_WESimon_barricade_low_group")}


def build():
    _v, ts, _o = k._parse(open(RC_TILES, "rb").read())
    tiles = ts[SHEET.encode()][6]
    flags = lambda i: {a.decode() for a, _b in tiles[i]}
    out = []
    for slug, name, faces, cost, kind, grp, level in PIECES:
        for f in faces.values():
            for L in f["layers"]:
                for row in L["rows"]:
                    for spr in row:
                        i = int(spr.rsplit("_", 1)[1])
                        if not flags(i) & {"solid", "solidtrans"}:
                            raise RuntimeError("%s is not a barricade tile: %s" % (spr, flags(i)))
        gname, gkey = GROUPS[grp]
        out.append({
            "id": PREFIX + slug, "allowSpriteReuse": True,
            "translationKey": "IGUI_WESimon_barricade_" + slug, "displayName": name,
            "category": "Fencing", "subcategory": "High" if kind in ("heavy", "heavy2", "post") else "Low",
            "material": "Metal" if kind != "low" else "Stone",
            "materialTags": ["Metal", "Stone"] if kind != "low" else ["Stone", "Wood"],
            "iconSprite": faces["W"]["layers"][0]["rows"][0][0],
            "placement": {"kind": "object", "requiresFloor": True},
            "tags": ["simonmd", "ravencreek", "world-essentials", "barricade"],
            "stages": [{"id": "built", "geometry": {"faces": faces}, "requirements": cost,
                        "construction": _construction(kind),
                        "object": {"isThumpable": True, "dismantable": True, "blockAllSquare": True}}],
            "group": {"id": PREFIX + grp, "name": gname, "translationKey": gkey, "level": level},
        })
    return out


def main():
    out = build()
    ids = [b["id"] for b in out]
    assert len(ids) == len(set(ids))
    doc = {"schemaVersion": 1, "category": "Fencing",
           "source": ("Simon MD barricades_Simon_MD (Raven Creek's LCB42_SimonMDsTiles copy): two-storey heavy barrier "
                      "fences and posts, low Do Not Cross barriers; layout from the user (pack viewer), costs first "
                      "pass. Generated by pz_craft_loops/simonmd_barricades.py."),
           "buildables": out}
    json.dump(doc, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("wrote %s (%d buildables)" % (OUT, len(ids)))


if __name__ == "__main__":
    main()
