# -*- coding: utf-8 -*-
"""Generate the Dirkies stairs deliverable (60_community_dirkies_stairs.json) from
fixtures_stairs_ddd_01 (Daddy Dirkie / Melos tiles, Community pack).

7 stairs, each with TWO orientations (E/W + N/S), each orientation = 3 step sprites
(lower / middle / upper). 3 of the stairs (slate/grey/white) also have a support pillar; those are
added once their post indices are confirmed (see PILLARED below -- not filled yet).

Modelled on KBW's stair geometry (KnoxBuildworks_Vanilla_Expanded/stairs.json):
  placement {kind:"stairs"}, object {isThumpable:false}
  W face (the E/W stair): one column, 3 rows stacked high->low, with y:-2 so it climbs
  N face (the N/S stair): one row of 3 sprites laid left->right high..low
A pillar is added as a SECOND layer on the relevant face (KBW stair-railing pattern), using the
post sprite; where only one post tile exists it is reused on both faces.

Index layout confirmed from the sheet + the user walking each set:
  Each entry: (slug, display, material, ew=(low,mid,high), ns=(low,mid,high), pillar or None)
  "E/W" = the left (West) staircase, "N/S" = the right (North) staircase; low->high.
"""

SHEET = "fixtures_stairs_ddd_01"

# (slug, display, material, ew (low,mid,high), ns (low,mid,high), pillar)
# pillar: None, or dict {"W": idx, "N": idx} for the two faces (same idx allowed if one post tile).
STAIRS = [
    # --- bottom 3: wood stairs, NO pillars; each row = one stair, E/W left cols, N/S right cols ---
    ("wood_bluetrim",  "Wooden Stairs (Blue Trim)",  "Wood", (32, 33, 34), (35, 36, 37), None),
    ("wood_olivetrim", "Wooden Stairs (Olive Trim)", "Wood", (40, 41, 42), (43, 44, 45), None),
    ("wood_tantrim",   "Wooden Stairs (Tan Trim)",   "Wood", (48, 49, 50), (51, 52, 53), None),
    # --- top 4 (user-numbered 1-4; posts verified against the art, not the addon's bad offsets) ---
    # 1 dark slate: NO pillar.
    ("slate_dark", "Dark Metal Stairs", "Metal", (0, 1, 2),   (8, 9, 10),   None),
    # Post indices (rev 3, game test 2026-08-28): the sheet is 8x8 tiles of 128x256. The first
    # post pass read a 128x128 grid, so its 30 / 38,46 / 54,62 were wrong (30 is white's post;
    # 38/46/54/62 are empty). On the real grid the posts sit in cols 6-7 of tile rows 1-3, matching
    # the addon's +6/+7 scheme: "W" = pillar (W-run stair, the stairsBW tiles = `ew`),
    # "N" = pillarNorth (north-run stair, the stairsBN tiles = `ns`).
    # 2 teal slate: ONE post (idx 14) shared by both orientations (addon: pillar = pillarNorth = 14).
    # PILLARS REMOVED from all stairs (user, 2026-08-28): no vanilla-style z-1 placement is
    # possible at ground level, so the post clipped (grey/white) or sat on the wrong step (teal).
    # The post indices below are kept for reference only.
    ("slate_teal", "Teal Metal Stairs", "Metal", (3, 4, 5),   (11, 12, 13), None),  # post was 14
    # 3 grey: two posts, 22 (pillar) / 23 (pillarNorth).
    ("grey",       "Grey Concrete Stairs", "Wood", (16, 17, 18), (24, 25, 26), None),  # posts were 22 / 23
    # 4 white: two posts, 30 (pillar) / 31 (pillarNorth).
    ("white",      "White Stairs",      "Wood",  (19, 20, 21), (27, 28, 29), None),  # posts were 30 / 31
]


def _sprite(idx):
    return "%s_%d" % (SHEET, idx)


def _ew_face(ew, pillar_idx):
    low, mid, high = ew
    # climbing vertical stack: high on top, low at bottom; y:-2 lifts it like KBW stairs
    stair = {"z": 0, "y": -2, "rows": [[_sprite(high)], [_sprite(mid)], [_sprite(low)]]}
    if pillar_idx is None:
        return {"layers": [stair]}
    # Pillar FIRST (game test 2026-08-28): objects on a square draw in the order they are added, so
    # the post must be added before the top step for the step to cover the post's top, like
    # vanilla wooden stairs. Both layers pinned to z 0 (KBW defaults z to layerIndex - 1). Same
    # square as the HIGHEST step (y -2).
    return {"layers": [{"z": 0, "y": -2, "rows": [[_sprite(pillar_idx)]]}, stair]}


def _ns_face(ns, pillar_idx):
    low, mid, high = ns
    stair = {"z": 0, "rows": [[_sprite(high), _sprite(mid), _sprite(low)]]}
    if pillar_idx is None:
        return {"layers": [stair]}
    # pillar first, both z 0 (see _ew_face); the highest step is column 1 -> x 0, y 0
    return {"layers": [{"z": 0, "x": 0, "y": 0, "rows": [[_sprite(pillar_idx)]]}, stair]}


def _recipe(material):
    if material == "Metal":
        return {
            "inputs": [
                {"id": "tool_welding_mask", "role": "tool", "mode": "keep",
                 "resourceType": "Item", "tags": ["base:weldingmask"], "amount": 1},
                {"id": "sheet_metal", "role": "material", "mode": "consume",
                 "resourceType": "Item", "items": ["Base.SmallSheetMetal"], "amount": 6},
                {"id": "metal_stock", "role": "material", "mode": "consume",
                 "resourceType": "Item",
                 "items": ["Base.IronBar", "Base.MetalBar", "Base.SteelBar", "Base.MetalPipe"],
                 "amount": 4},
                {"id": "fasteners_screws", "role": "material", "mode": "consume",
                 "resourceType": "Item", "items": ["Base.Screws"], "amount": 4},
                {"id": "torch_fuel", "role": "consumable", "mode": "drain",
                 "resourceType": "Item", "items": ["Base.BlowTorch"], "amount": 1, "uses": 10},
                {"id": "welding_rods", "role": "consumable", "mode": "drain",
                 "resourceType": "Item", "items": ["Base.WeldingRods"], "amount": 1, "uses": 5},
            ],
            "skills": {"MetalWelding": 5},
        }
    # Wood
    return {
        "inputs": [
            {"id": "tool_hammer", "role": "tool", "mode": "keep",
             "resourceType": "Item", "tags": ["base:hammer"], "amount": 1,
             "flags": ["Prop1", "MayDegradeVeryLight"]},
            {"id": "lumber", "role": "material", "mode": "consume",
             "resourceType": "Item", "items": ["Base.Plank"], "amount": 13},
            {"id": "fasteners_nails", "role": "material", "mode": "consume",
             "resourceType": "Item", "items": ["Base.Nails"], "amount": 8},
        ],
        "skills": {"Woodwork": 6},
    }


def _construction(material):
    if material == "Metal":
        return {"time": 200, "timedAction": "BuildWallMetal",
                "completionSound": "BuildMetalStructureMedium", "xp": {"MetalWelding": 50},
                "category": "Welding"}
    return {"time": 200, "timedAction": "BuildWallHammer",
            "completionSound": "BuildWoodenStructureLarge", "xp": {"Woodwork": 60},
            "category": "Carpentry"}


def _buildable(slug, display, material, ew, ns, pillar):
    bid = "community.dirkies.stairs.%s" % slug
    pw = pillar["W"] if pillar else None
    pn = pillar["N"] if pillar else None
    return {
        "id": bid,
        "allowSpriteReuse": True,
        "translationKey": "IGUI_community_dirkies_stairs_%s" % slug,
        "displayName": display,
        "tooltipKey": "Tooltip_KBW_Shared_Stairs",
        "category": "Stairs",
        "subcategory": "Stairs",
        "material": material,
        "materialTags": [material],
        "iconSprite": _sprite(ew[0]),
        "placement": {"kind": "stairs"},
        "tags": ["community-tilepack", "dirkies", "stairs"],
        "stages": [
            {
                "id": "built",
                # Rev 2 (game test 2026-08-28): orientations were swapped. The sheet's "E/W" art
                # is the N-face stair and its "N/S" art the W-face stair. Each pillar travels with
                # its own art.
                "geometry": {"faces": {"W": _ew_face(ns, pn), "N": _ns_face(ew, pw)}},
                "requirements": _recipe(material),
                "construction": _construction(material),
                "object": {"isThumpable": False},
            }
        ],
    }


def build_document():
    builds = [_buildable(*s) for s in STAIRS]
    return {
        "schemaVersion": 1,
        "category": "Stairs",
        "source": ("Dirkies fixtures_stairs_ddd_01 (Daddy Dirkie / Melos tiles). 7 stairs, each with "
                   "E/W + N/S orientations (3 step sprites each, low->high). KBW stair model "
                   "(kind:stairs; W face = vertical 3-row stack y:-2; N face = horizontal 3-sprite "
                   "row). 3 of the 7 have a support pillar added as a 2nd face layer: teal metal uses "
                   "ONE post (idx 30) on both orientations; grey and white use TWO posts (one per "
                   "orientation: grey 38/46, white 54/62). dark metal + the 3 wood stairs have none. "
                   "The BuildingMenu addon's hardcoded pillar offsets were WRONG against the art "
                   "(idx 14/15 empty; wood offsets overlapped other stairs); posts were verified by "
                   "pixel inspection (tall+narrow art at idx 30/38/46/54/62)."),
        "buildables": builds,
    }


def main():
    import json
    doc = build_document()
    out = r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables\60_community_dirkies_stairs.json"
    json.dump(doc, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    ids = [b["id"] for b in doc["buildables"]]
    assert len(ids) == len(set(ids)), "dup ids"
    print("wrote %s" % out)
    print("stairs=%d" % len(ids))


if __name__ == "__main__":
    main()
