# -*- coding: utf-8 -*-
"""Generate 64_community_dirkies_window_decor.json (user, 2026-08-28) from Dirkies'
fixtures_details_ddd_01 (Community pack, diederiks_tile_palooza), tiles 0-47:

  0-31  exterior window trim: 4 rows = colours (White, Gray, Charcoal, Terracotta), each row 4 styles
        x W/N (even index = west wall, odd = north wall). One card per style, colours as levels.
        Built on OUR COPIES (kbw_tilepatch.FDD_TRIM, KBWCommunityIceShell_90..121): the pack tiles are
        MoveType WindowObject, which KBW / WE turn into a native curtain; the copies are wall
        overlays (WallOverlay + attached flag) that KBW hangs on the host wall, like the tterika wall
        detailing (43/44, confirmed in game, incl. window walls). Fit (user, in game 2026-08-28): the
        trim AND the planters belong to the "Window Frame-Tall" window shape (any colour).
  32-39 window planters (pack: MoveType WallObject + attachedW/N): empty, shrubs, ivy, potted plants.
        The pack tiles could not be placed (WE builds movable WallObjects through its native wall
        attachment, which refuses window walls): built on overlay copies like the trim
        (kbw_tilepatch.FDD_PLANTERS).
  40-47 potted plants (pack: attachedW/N, no MoveType): 40/41 marigold pot and 46/47 flower basket
        have both facings; 42, 43, 44, 45 are four different plants with one facing each (the pack
        pairs them as two items, but the art differs). Walk-through floor decorations. The pack draws
        them against the wall edge, so they looked raised on an open square: built on copies with the
        art centred on the square (kbw_tilepatch.FDD_POTS).
Costs: trim = the wall-trim recipe (hammer, plank, nails, Woodwork 2) doubled; planters = hammer,
2 planks, 4 nails (+2 uses of a dirt bag when planted); pots = 1 clay pot + 1 use of a dirt bag.
NOT yet tested in game.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kbw_tilepatch import FDD_SHEET, FDD_TRIM, decor_copy_name, decor_edge

OUT = r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables\64_community_dirkies_window_decor.json"
COLOURS = ["White", "Gray", "Charcoal", "Terracotta"]                 # rows 0-3
STYLES = [  # (offset in the row, slug, name)
    (0, "arched", "Arched Window Trim"),
    (2, "round_top", "Round-Top Window Trim"),
    (4, "corniced", "Corniced Window Trim"),
    (6, "ornate", "Ornate Window Header and Sill"),
]
PLANTERS = [  # (W index, slug, name, planted)
    (32, "empty", "Empty Window Planter", False),
    (34, "shrubs", "Window Planter (Shrubs)", True),
    (36, "ivy", "Window Planter (Ivy)", True),
    (38, "potted", "Window Planter (Potted Plants)", True),
]
POTS = [  # (slug, name, {face: index})
    ("marigold", "Marigold Pot", {"W": 40, "N": 41}),
    ("golden_shrub", "Golden Shrub Pot", {"W": 42}),
    ("pink_shrub", "Pink Shrub Pot", {"N": 43}),
    ("green_shrub", "Green Shrub Pot", {"W": 44}),
    ("burgundy_shrub", "Burgundy Shrub Pot", {"N": 45}),
    ("flower_basket", "Pink Flower Basket", {"W": 46, "N": 47}),
]
DECOR_OBJECT = {"isThumpable": False, "canPassThrough": True, "blockAllSquare": False, "dismantable": True}


def _spr(i):
    return "%s_%d" % (FDD_SHEET, i)


def _one(s):
    return {"layers": [{"rows": [[s]]}]}


def _hammer():
    return {"id": "tool_hammer", "role": "tool", "mode": "keep", "resourceType": "Item",
            "tags": ["base:hammer"], "amount": 1}


def _item(n, item, amount):
    return {"id": "source_material_%d" % n, "role": "material", "mode": "consume", "resourceType": "Item",
            "items": [item], "amount": amount}


def _dirt(n, uses):
    return {"id": "source_material_%d" % n, "role": "consumable", "mode": "drain", "resourceType": "Item",
            "items": ["Base.Dirtbag"], "amount": 1, "uses": uses}


def _base(slug, name, cat, sub, icon, placement, faces, req, con, group=None, level=None):
    bid = "community.dirkies.window_decor.%s" % slug
    b = {
        "id": bid,
        "allowSpriteReuse": True,
        "translationKey": "IGUI_" + bid.replace(".", "_"),
        "displayName": name,
        "category": cat,
        "subcategory": sub,
        "material": "Wood",
        "materialTags": ["Wood"],
        "iconSprite": icon,
        "placement": placement,
        "tags": ["community-tilepack", "dirkies", "exterior-decor"],
        "pieceClass": "decoration",
        "stages": [{
            "id": "built",
            "geometry": {"faces": {f: _one(s) for f, s in faces.items()}},
            "requirements": req,
            "construction": con,
            "object": dict(DECOR_OBJECT),
        }],
    }
    if group:
        b["group"] = dict(group, level=level)
    return b


def build_document():
    out = []
    trim_req = {"inputs": [_hammer(), _item(1, "Base.Plank", 2), _item(2, "Base.Nails", 2)], "skills": {"Woodwork": 2}}
    trim_con = {"time": 80, "timedAction": "BuildWallHammer", "completionSound": "BuildWoodenStructureLarge",
                "xp": {"Woodwork": 10}, "category": "Carpentry"}
    overlay = {"kind": "overlay", "needToBeAgainstWall": True}
    for off, slug, name in STYLES:
        group = {"id": "community.dirkies.window_decor.trim_%s" % slug, "name": name,
                 "translationKey": "IGUI_community_dirkies_window_decor_trim_%s_group" % slug}
        for row, colour in enumerate(COLOURS):
            w, n = row * 8 + off, row * 8 + off + 1
            assert w in FDD_TRIM and n in FDD_TRIM
            faces = {decor_edge(w, FDD_SHEET): decor_copy_name(w, FDD_SHEET),
                     decor_edge(n, FDD_SHEET): decor_copy_name(n, FDD_SHEET)}
            assert set(faces) == {"W", "N"}
            out.append(_base("trim_%s_%s" % (slug, colour.lower()), "%s %s" % (colour, name), "Wall Trim",
                             "Window Trim", faces["W"], dict(overlay), faces, trim_req, trim_con, group, row + 1))
    pl_con = {"time": 100, "timedAction": "BuildWallHammer", "completionSound": "BuildWoodenStructureSmall",
              "xp": {"Woodwork": 10}, "category": "Carpentry"}
    pl_group = {"id": "community.dirkies.window_decor.planters", "name": "Window Planters",
                "translationKey": "IGUI_community_dirkies_window_decor_planters_group"}
    for level, (w, slug, name, planted) in enumerate(PLANTERS, 1):
        inputs = [_hammer(), _item(1, "Base.Plank", 2), _item(2, "Base.Nails", 4)]
        if planted:
            inputs.append(_dirt(3, 2))
        # our overlay copies (kbw_tilepatch.FDD_PLANTERS): the pack tiles could not be placed on
        # window walls (WE native wall-attachment path); overlays hang like the window trim
        cw, cn = decor_copy_name(w, FDD_SHEET), decor_copy_name(w + 1, FDD_SHEET)
        out.append(_base("planter_%s" % slug, name, "Vegetation", "Window Planters", cw,
                         dict(overlay), {"W": cw, "N": cn}, {"inputs": inputs, "skills": {"Woodwork": 2}},
                         pl_con, pl_group, level))
    pot_con = {"time": 50, "timedAction": "BuildWallNoTool", "completionSound": "BuildWoodenStructureSmall",
               "xp": {"Farming": 5}, "category": "Farming"}
    pot_group = {"id": "community.dirkies.window_decor.pots", "name": "Potted Plants",
                 "translationKey": "IGUI_community_dirkies_window_decor_pots_group"}
    for level, (slug, name, faces) in enumerate(POTS, 1):
        # centred floor copies (kbw_tilepatch.FDD_POTS): the pack draws them against the wall edge
        sp = {f: decor_copy_name(i, FDD_SHEET) for f, i in faces.items()}
        out.append(_base("pot_%s" % slug, name, "Vegetation", "Potted Plants", next(iter(sp.values())),
                         {"kind": "object", "requiresFloor": True}, sp,
                         {"inputs": [_item(1, "Base.ClayPot", 1), _dirt(2, 1)]}, pot_con, pot_group, level))
    return {
        "schemaVersion": 1,
        "category": "Wall Trim",
        "source": ("Dirkies fixtures_details_ddd_01 0-47 (Community pack): exterior window trim on our "
                   "overlay copies (KBWCommunityIceShell_90..121), window planters and potted plants "
                   "(pack tiles). Generated by pz_craft_loops/dirkies_window_decor.py."),
        "buildables": out,
    }


def main():
    doc = build_document()
    ids = [b["id"] for b in doc["buildables"]]
    assert len(ids) == len(set(ids))
    json.dump(doc, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("wrote %s (%d buildables)" % (OUT, len(ids)))


if __name__ == "__main__":
    main()
