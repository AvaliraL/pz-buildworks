# -*- coding: utf-8 -*-
"""Generate 48_tikitown_rugs.json (user, 2026-11-12): Drazion's tikitown_rugs_01.

Floral rugs (Light Green / Dark Red / Yellow and Black): each colour's 12 tiles are TWO 2x3 rugs,
one laid N/S (rows 0-2 of its block) and one laid E/W (rows 3-5), read from the art and checked by
compositing. Built as a STRAIGHT and a CORNER piece, 4 orientations each, so players lay out any
rug shape (user). Offsets inside a colour block (block start tile b = 4 / 6 / 10, row step 8):
  N/S rug: corners SW b+0, SE b+1, NW b+16, NE b+17; straights W b+8, E b+9
  E/W rug: corners SW b+24, NW b+25, SE b+40, NE b+41; straights S b+32, N b+33
  Straight faces (border side): N b+33, E b+9, S b+32, W b+8
  Corner faces (clockwise, like the straight): N = NW b+16, E = NE b+17, S = SE b+1, W = SW b+0
  (the N/S rug's corner set; its two south corners carry the pineapple end motif).
  Corner (Alt) faces: N = NW b+25, E = NE b+41, S = SE b+40, W = SW b+24 (the E/W rug's set; its
  west / east corners carry the motif). All corner tiles share the same border, so either set joins
  straights on either axis. With the alts every rug tile of the sheet is used.
Street Play Rug (tiles 0-3): one 2x2 piece (user: not built by piece). Layout found by fitting all
24 arrangements (the art covers less than each floor diamond; only one arrangement meets with no
gap or overlap) and checked by compositing: north row 3 2, south row 0 1 (west -> east).

Pack tiles: MoveType FloorRug + solidfloor, no SpriteGridPos / Facing: built on the pack tiles.
Setup and cost follow our existing rugs (Community file 52, the Dylan floor mats, 2 tiles, confirmed
in game): same object flags, tooltip, Tailoring cost and Rugs & Carpets magazine gate, scaled by
tile count (1-tile piece = half a mat, the 2x2 = double). NOT yet tested in game.
"""
import json
import os

SHEET = "tikitown_rugs_01"
OUT = r"c:\Users\josep\Kiro\zomboid\tikitown\48_tikitown_rugs.json"
PREFIX = "worldessentials.tikitown.rug_"
FLORAL = [  # (slug, pack CustomName, colour block start tile)
    ("light_green_floral", "Light Green Floral Rug", 4),
    ("dark_red_floral", "Dark Red Floral Rug", 6),
    ("yellow_black_floral", "Yellow and Black Floral Rug", 10),
]
STRAIGHT = {"N": 33, "E": 9, "S": 32, "W": 8}
CORNER = {"N": 16, "E": 17, "S": 1, "W": 0}
# the E/W rug's own corner set as "Corner (Alt)" (user, 2026-11-12): N = NW +25, E = NE +41,
# S = SE +40, W = SW +24 (its pineapple end motif sits on the west / east ends instead)
CORNER_ALT = {"N": 25, "E": 41, "S": 40, "W": 24}
STREET_PLAY = [[3, 2], [0, 1]]          # rows north -> south, each west -> east
KNOWLEDGE = {
    "recipes": ["KBWKnowledge_ArchitecturalDigest_RugsCarpets"],
    "hideUntilLearned": True,
    "needToBeLearned": True,
    "sources": [{"type": "magazine", "item": "KnoxBuildworks.ArchitecturalDigest_RugsCarpets"}],
    "skillAlternatives": [{"mode": "all", "skills": {"Tailoring": 5}}],
}


def _spr(i):
    return "%s_%d" % (SHEET, i)


def _requirements(tiles):
    """The 2-tile floor mat's cost (fabric 6 uses, thread 4 uses) scaled to `tiles`."""
    return {
        "inputs": [
            {"id": "covering_fabric", "role": "consumable", "mode": "drain", "resourceType": "Item",
             "items": ["Base.FabricRoll_Cotton"], "amount": 1, "uses": 3 * tiles},
            {"id": "tool_cutting", "role": "tool", "mode": "keep", "resourceType": "Item",
             "tags": ["base:scissors", "base:sharpknife"], "amount": 1, "flags": ["MayDegradeLight"]},
            {"id": "tool_sewing_needle", "role": "tool", "mode": "keep", "resourceType": "Item",
             "tags": ["base:sewingneedle", "base:awl"], "amount": 1, "flags": ["Prop2", "MayDegradeLight"]},
            {"id": "thread", "role": "consumable", "mode": "drain", "resourceType": "Item",
             "tags": ["base:thread", "base:twine"], "amount": 1, "uses": 2 * tiles},
        ],
        "skills": {"Tailoring": 2},
        "knowledge": json.loads(json.dumps(KNOWLEDGE)),
    }


def _buildable(bid, name, faces, tiles, group=None):
    first = next(iter(faces.values()))["layers"][0]["rows"][0][0]
    b = {
        "id": PREFIX + bid,
        "allowSpriteReuse": True,
        "translationKey": "IGUI_WETiki_rug_%s" % bid,
        "displayName": name,
        "tooltipKey": "Tooltip_KBW_Shared_Floor",
        "category": "Decorations",
        "subcategory": "Rugs",
        "material": "Fabric",
        "materialTags": ["Fabric"],
        "iconSprite": first,
        "placement": {"kind": "object", "needToBeAgainstWall": False},
        "tags": ["tikitown", "drazion", "world-essentials", "rug"],
        "stages": [{
            "id": "built",
            "object": {"isThumpable": True, "blockAllSquare": False, "canPassThrough": True,
                       "canBarricade": False},
            "geometry": {"faces": faces},
            "requirements": _requirements(tiles),
            "construction": {"time": 100 * tiles, "timedAction": "BuildLowNoTool",
                             "completionSound": "BuildWoodenStructureSmall", "xp": {"Tailoring": 10 * tiles},
                             "category": "Tailoring"},
        }],
    }
    if group:
        b["group"] = group
    return b


def _one(i):
    return {"layers": [{"rows": [[_spr(i)]]}]}


def build():
    out = []
    for slug, name, base in FLORAL:
        group = {"id": PREFIX + slug, "name": name, "translationKey": "IGUI_WETiki_rug_%s_group" % slug}
        out.append(_buildable(slug + "_straight", name + " (Straight)",
                              {f: _one(base + o) for f, o in STRAIGHT.items()}, 1, dict(group, level=1)))
        out.append(_buildable(slug + "_corner", name + " (Corner)",
                              {f: _one(base + o) for f, o in CORNER.items()}, 1, dict(group, level=2)))
        out.append(_buildable(slug + "_corner_alt", name + " (Corner, Alt)",
                              {f: _one(base + o) for f, o in CORNER_ALT.items()}, 1, dict(group, level=3)))
    out.append(_buildable("street_play", "Street Play Rug",
                          {"S": {"layers": [{"rows": [[_spr(i) for i in row] for row in STREET_PLAY]}]}}, 4))
    return out


def _check_sheet(out):
    """Every tile used exists in the pack as a FloorRug of the rug its piece is named after, and every
    rug tile of the sheet is used."""
    import kbw_tilepatch as k
    _v, ts, _o = k._parse(open(k._TIKITOWN_TILES, "rb").read())
    tiles = ts[SHEET.encode()][6]
    used = set()
    for b in out:
        for face in b["stages"][0]["geometry"]["faces"].values():
            for row in face["layers"][0]["rows"]:
                for spr in row:
                    i = int(spr.rsplit("_", 1)[1])
                    p = dict(tiles[i])
                    if p.get(b"MoveType") != b"FloorRug" or not b["displayName"].startswith(p[b"CustomName"].decode()):
                        raise RuntimeError("%s is not a %s FloorRug: %s" % (spr, b["displayName"], p))
                    used.add(i)
    rugs = {i for i, p in enumerate(tiles) if dict(p).get(b"MoveType") == b"FloorRug"}
    return sorted(rugs - used)


def main():
    out = build()
    unused = _check_sheet(out)
    doc = {
        "schemaVersion": 1,
        "category": "Decorations",
        "source": ("TikiTown tikitown_rugs_01 (Drazion's Tilepack): floral rugs as straight + corner pieces "
                   "(4 orientations), the Street Play Rug as one 2x2. Generated by pz_craft_loops/tikitown_rugs.py."),
        "buildables": out,
    }
    ids = [b["id"] for b in out]
    assert len(ids) == len(set(ids))
    json.dump(doc, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("wrote %s (%d buildables); sheet rug tiles not used: %s" % (OUT, len(ids), unused))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
