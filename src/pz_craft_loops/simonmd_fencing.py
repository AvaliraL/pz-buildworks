# -*- coding: utf-8 -*-
"""Generate zomboid/simonmd/01_simonmd_fencing.json (user, 2026-11-14): Simon MD's scrap fences.

New World Essentials submod "World Essentials - Simon MD Buildworks" (build_simonmd_mod.py). It
requires Raven Creek (RavenCreek_B42), whose LCB42_SimonMDsTiles copy is what the server runs; a
version for the standalone B42 Simon MD pack can follow if the server adds it. Raven Creek's copy
has the same sheet names, indices, tile properties and art as the standalone pack for the sheets it
defines (checked 2026-11-14, pz_craft_loops/_simon_compare.txt), and it defines fencing_Simon_MD.

Pieces and costs come from the B41 Building Menu Simon MD addon (3137092790, category Fencing /
"Scrap High Fences"), read by running it in map_buildmenu_addons' Lua sandbox:
  2 styles x high fence, high fence post, low fence, low fence post, high fence (back), low fence (back)
  = 12 pieces. The fence pieces are 2 tiles wide (sprite + sprite2 / northSprite + northSprite2),
  laid out like Building Menu's own 2-tile fences in KBW Vanilla Expanded (W face rows
  [[sprite], [sprite2]], N face [[northSprite, northSprite2]]). The "back" versions show the brace
  on the other side; the high ones use the addon's corner tile 70.
  The posts (leaning brace / thin pole) have no tile properties in the pack; built as KBW pillars.
  NOT built: the addon's Scrap Double Door Gate (fixtures_doors_fences_Simon_MD, which Raven Creek's
  copy does not define).
Costs: the addon's two recipes at Building Menu's default sandbox values (BuildingMenu02_Recipes.lua):
  BigScrapHighFenceRecipe (high fences): 9 planks, 5 sheet metal, 4 metal bars or pipes, 10 screws,
    6 nails, blowtorch 6 uses, welding rods 3 uses; welding mask, screwdriver, hammer, saw;
    MetalWelding 7, Woodwork 9
  SmallScrapLowFenceRecipe (low fences and every post): 4 planks, 3 sheet metal, 2 metal bars or pipes,
    8 screws, 4 nails, blowtorch 2 uses, welding rods 1 use; welding mask, hammer, saw;
    MetalWelding 4, Woodwork 4
NOT yet tested in game.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kbw_tilepatch as k   # noqa: E402

SHEET = "fencing_Simon_MD"
OUT = r"c:\Users\josep\Kiro\zomboid\simonmd\01_simonmd_fencing.json"
RC_TILES = (r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600\3821823518\mods"
            r"\RavenCreek_B42\common\media\LCB42_SimonMDsTiles.tiles")
PREFIX = "worldessentials.simonmd.fence_"
# (style, slug, name, recipe, W [sprite, sprite2], N [north, north2], corner) from the addon
FENCES = [
    (1, "high", "Scrap High Fence", "big", (32, 31), (36, 37), None),
    (1, "high_post", "Scrap High Fence Post", "small", (30,), (38,), None),
    (1, "low", "Scrap Low Fence", "small", (35, 34), (39, 40), None),
    (1, "low_post", "Scrap Low Fence Post", "small", (33,), (41,), None),
    (1, "high_back", "Scrap High Fence (Back)", "big", (55, 54), (58, 59), 70),
    (1, "low_back", "Scrap Low Fence (Back)", "small", (57, 56), (60, 61), None),
    (2, "high", "Scrap High Fence", "big", (44, 43), (48, 49), None),
    (2, "high_post", "Scrap High Fence Post", "small", (42,), (50,), None),
    (2, "low", "Scrap Low Fence", "small", (47, 46), (51, 52), None),
    (2, "low_post", "Scrap Low Fence Post", "small", (45,), (53,), None),
    (2, "high_back", "Scrap High Fence (Back)", "big", (63, 62), (66, 67), 70),
    (2, "low_back", "Scrap Low Fence (Back)", "small", (65, 64), (68, 69), None),
]


def _tool(i, tags, flags=None):
    d = {"id": i, "role": "tool", "mode": "keep", "resourceType": "Item", "tags": tags, "amount": 1}
    if flags:
        d["flags"] = flags
    return d


def _mat(i, items, n):
    return {"id": i, "role": "material", "mode": "consume", "resourceType": "Item", "items": items, "amount": n}


def _drain(i, item, uses):
    return {"id": i, "role": "consumable", "mode": "drain", "resourceType": "Item", "items": [item], "uses": uses}


def _requirements(kind):
    big = kind == "big"
    tools = [_tool("welding_mask", ["base:weldingmask"])]
    if big:
        tools.append(_tool("tool_screwdriver", ["base:screwdriver"], ["Prop1", "MayDegradeVeryLight"]))
    tools += [_tool("tool_hammer", ["base:hammer"], ["Prop1", "MayDegradeVeryLight"]),
              _tool("tool_saw", ["base:saw", "base:crudesaw"], ["Prop2", "MayDegradeLight"])]
    return {
        "inputs": tools + [
            _mat("planks", ["Base.Plank"], 9 if big else 4),
            _mat("sheet_metal", ["Base.SheetMetal"], 5 if big else 3),
            _mat("metal_bars", ["Base.MetalBar", "Base.MetalPipe"], 4 if big else 2),
            _mat("screws", ["Base.Screws"], 10 if big else 8),
            _mat("nails", ["Base.Nails"], 6 if big else 4),
            _drain("torch_fuel", "Base.BlowTorch", 6 if big else 2),
            _drain("welding_rods", "Base.WeldingRods", 3 if big else 1),
        ],
        "skills": {"MetalWelding": 7, "Woodwork": 9} if big else {"MetalWelding": 4, "Woodwork": 4},
    }


def _construction(kind):
    return {"time": 300 if kind == "big" else 150, "timedAction": "BuildWallMetal",
            "completionSound": "BuildMetalStructureMedium",
            "xp": {"MetalWelding": 25, "Woodwork": 22} if kind == "big" else {"MetalWelding": 14, "Woodwork": 10},
            "category": "Welding"}


def _spr(i):
    return "%s_%d" % (SHEET, i)


def build():
    _v, ts, _o = k._parse(open(RC_TILES, "rb").read())
    tiles = ts[SHEET.encode()][6]
    flags = lambda i: {a.decode() for a, _b in tiles[i]} if i < len(tiles) else set()
    out = []
    for style, slug, name, recipe, w, n, corner in FENCES:
        post = len(w) == 1
        if not post:   # every fence tile is a wall on its edge (W tiles WallW*, N tiles WallN*)
            for i in w:
                if not any(f.startswith("WallW") for f in flags(i)):
                    raise RuntimeError("%s is not a west fence tile: %s" % (_spr(i), flags(i)))
            for i in n:
                if not any(f.startswith("WallN") for f in flags(i)):
                    raise RuntimeError("%s is not a north fence tile: %s" % (_spr(i), flags(i)))
        low = slug.startswith("low")
        if post:
            faces = {"W": {"layers": [{"rows": [[_spr(w[0])]]}]}, "N": {"layers": [{"rows": [[_spr(n[0])]]}]}}
            obj = {"dismantable": True, "blockAllSquare": False, "canPassThrough": True, "canBarricade": False,
                   "isCorner": True}
        else:
            faces = {"W": {"layers": [{"rows": [[_spr(w[0])], [_spr(w[1])]]}]},
                     "N": {"layers": [{"rows": [[_spr(n[0]), _spr(n[1])]]}]}}
            obj = {"isThumpable": True, "dismantable": True, "blockAllSquare": False, "hoppable": False}
            if corner is not None:
                obj["cornerSprite"] = _spr(corner)
        bid = "%d_%s" % (style, slug)
        b = {
            "id": PREFIX + bid,
            "allowSpriteReuse": True,
            "translationKey": "IGUI_WESimon_fence_" + bid,
            "displayName": "%s %d" % (name, style) if "(" not in name else name.replace(" (", " %d (" % style),
            "tooltipKey": "Tooltip_KBW_Shared_Wall",
            "category": "Fencing",
            "subcategory": "Low" if low else "High",
            "material": "Metal",
            "materialTags": ["Metal", "Wood"],
            "iconSprite": _spr(w[0]),
            "placement": {"kind": "wall"},
            "tags": ["simonmd", "ravencreek", "world-essentials", "scrap-fence"],
            "stages": [{"id": "built", "geometry": {"faces": faces}, "requirements": _requirements(recipe),
                        "construction": _construction(recipe), "object": obj}],
            "group": {"id": PREFIX + "style_%d" % style, "name": "Scrap Fences %d" % style,
                      "translationKey": "IGUI_WESimon_fence_style_%d_group" % style,
                      "level": [f[1] for f in FENCES if f[0] == style].index(slug) + 1},
        }
        if post:
            b["pieceClass"] = "pillar"
        out.append(b)
    return out


def main():
    out = build()
    ids = [b["id"] for b in out]
    assert len(ids) == len(set(ids))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    doc = {"schemaVersion": 1, "category": "Fencing",
           "source": ("Simon MD fencing_Simon_MD (Raven Creek's LCB42_SimonMDsTiles copy): scrap high / low fences, "
                      "posts and back versions, 2 styles, pieces and costs from the B41 Building Menu Simon MD addon. "
                      "Generated by pz_craft_loops/simonmd_fencing.py."),
           "buildables": out}
    json.dump(doc, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("wrote %s (%d buildables)" % (OUT, len(ids)))


if __name__ == "__main__":
    main()
