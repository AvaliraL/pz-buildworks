# -*- coding: utf-8 -*-
"""Generate the Dirkies bedroom deliverable (61_community_dirkies_bedroom.json) from the 5
d_furniture_bedroom_0{1..5} sheets (Daddy Dirkie / Melos tiles, Community pack).

Rev 2 (after in-game test): 12 pieces per sheet -- 2-tile floor bed, 4-tile large floor bed,
2-tile wardrobe (each ONE piece with 4 facings; the addon had split each into two entries),
plus the single-tile nightstand, dressers and bookcases. Names by sheet color. Modelled on our own
TikiTown bedroom (25_tikitown_bedroom.json):
  beds           kind:object requiresFloor, multi-tile, NO container (BedRecipe-style wood recipe)
  dressers       kind:object requiresFloor, object{isProp,canBePadlocked}, container{dresser,20}
  nightstand     kind:object requiresFloor, simple furniture, NO container
  bookcase       container{shelves,40}; the wall bookcase is needToBeAgainstWall
Multi-tile faces: see LAYOUT_STD / LAYOUT_S4 below (SpriteGridPos (x,y) -> row y, col x).
4-facing dresser: sprite(W)/northSprite(N)/eastSprite(E)/southSprite(S), one sprite per face.
"""

SHEETS = [
    ("d_furniture_bedroom_01", "Cream"),
    ("d_furniture_bedroom_02", "Grey"),
    ("d_furniture_bedroom_03", "Oak"),
    ("d_furniture_bedroom_04", "Weathered"),
    ("d_furniture_bedroom_05", "Birch"),
]

# ---------------------------------------------------------------------------------------------
# Multi-tile layouts (rev 2, after in-game test: all multi-tile pieces were wrong).
# The addon split each multi-tile piece into two entries (2 facings each); they are really ONE
# piece with 4 facings:  2-tile bed = idx 0-7, 4-tile bed = idx 8-23, wardrobe = idx 40-47.
# Rule (from the in-game-confirmed TikiTown bedroom, same tile layout): a sprite with
# SpriteGridPos (x,y) goes to row y, col x. Beds: KBW face = opposite of the tile Facing
# (Facing S -> face N, N -> S, E -> W, W -> E); wardrobe: face = Facing.
# Sheets 1/2/3/5 copy the confirmed TikiTown table verbatim (their own .tiles has typos, e.g.
# idx 7/10/11 all "W 1,1"). Sheet 4 is a different bed design with its own order, derived from
# its .tiles with the same rule (one typo: idx 19 says 0,1, taken as 1,0) -- verify in game.
# Faces: {face: rows}
LAYOUT_STD = {
    "bed":      {"N": [[1], [0]], "S": [[5], [4]], "W": [[2, 3]], "E": [[6, 7]]},
    "bed4":     {"E": [[9, 11], [8, 10]], "S": [[13, 15], [12, 14]],
                 "N": [[17, 19], [16, 18]], "W": [[21, 23], [20, 22]]},
    "wardrobe": {"S": [[40, 41]], "E": [[43], [42]], "W": [[45], [44]], "N": [[46, 47]]},
}
LAYOUT_S4 = {
    "bed":      {"N": [[1], [0]], "W": [[2, 3]], "S": [[13], [12]], "E": [[14, 15]]},
    "bed4":     {"N": [[5, 7], [4, 6]], "W": [[10, 11], [8, 9]],
                 "S": [[17, 19], [16, 18]], "E": [[22, 23], [20, 21]]},
    "wardrobe": LAYOUT_STD["wardrobe"],
}

def _spr(sheet, idx):
    return "%s_%d" % (sheet, idx)


def _one(sheet, idx):
    return {"layers": [{"rows": [[_spr(sheet, idx)]]}]}


def _wood_recipe(planks, nails, wood=5):
    return {
        "inputs": [
            {"id": "tool_hammer", "role": "tool", "mode": "keep",
             "resourceType": "Item", "tags": ["base:hammer"], "amount": 1},
            {"id": "source_material_1", "role": "material", "mode": "consume",
             "resourceType": "Item", "items": ["Base.Plank"], "amount": planks},
            {"id": "source_material_2", "role": "material", "mode": "consume",
             "resourceType": "Item", "items": ["Base.Nails"], "amount": nails},
        ],
        "skills": {"Woodwork": wood},
    }


def _construction(xp=50, time=240):
    return {"time": time, "timedAction": "BuildWoodenStructureSmall",
            "completionSound": "BuildWoodenStructureLarge", "xp": {"Woodwork": xp},
            "category": "Carpentry"}


def _base(sheet, slug, display, subcat, icon_idx):
    bid = "community.dirkies.bedroom.%s_%s" % (sheet, slug)
    return {
        "id": bid,
        "allowSpriteReuse": True,
        "translationKey": "IGUI_%s_%s" % (sheet, slug),
        "displayName": display,
        "tooltipKey": "Tooltip_KBW_Shared_StorageFixture",
        "category": "Furniture and Appliances",
        "subcategory": subcat,
        "material": "Wood",
        "materialTags": ["Wood"],
        "iconSprite": _spr(sheet, icon_idx),
        "placement": {"kind": "object", "requiresFloor": True},
        "tags": ["community-tilepack", "dirkies", "bedroom"],
    }


def _faces_from(sheet, layout):
    return {f: {"layers": [{"rows": [[_spr(sheet, i) for i in row] for row in rows]}]}
            for f, rows in layout.items()}


def _multi_bed(sheet, color_word, slug, name, layout, planks, nails, wood, xp):
    icon = layout["N"][0][0]
    b = _base(sheet, slug, "%s %s" % (color_word, name), "Beds", icon)
    b["tooltipKey"] = "Tooltip_craft_bedDesc"
    b["stages"] = [{
        "id": "built",
        "geometry": {"faces": _faces_from(sheet, layout)},
        "requirements": _wood_recipe(planks, nails, wood),
        "construction": _construction(xp=xp),
        "object": {"isThumpable": True, "dismantable": True},
    }]
    return b


def _wardrobe(sheet, color_word, layout):
    b = _base(sheet, "wardrobe", "%s Wardrobe" % color_word, "Wardrobes", layout["S"][0][0])
    b["tooltipKey"] = "Tooltip_KBW_Shared_StorageFixture"
    b["stages"] = [{
        "id": "built",
        "geometry": {"faces": _faces_from(sheet, layout)},
        "requirements": _wood_recipe(8, 6, 4),
        "construction": _construction(xp=40, time=200),
        "object": {"isThumpable": True, "dismantable": True, "isProp": True, "canBePadlocked": True},
        "container": {"type": "wardrobe", "capacity": 25},
    }]
    return b


def _simple(sheet, color_word, slug, name, subcat, w_idx, n_idx):
    # nightstand / simple furniture, no container; 2 orientations
    b = _base(sheet, slug, "%s %s" % (color_word, name), subcat, w_idx)
    b["tooltipKey"] = "Tooltip_craft_smallTableDesc"
    b["stages"] = [{
        "id": "built",
        "geometry": {"faces": {"W": _one(sheet, w_idx), "N": _one(sheet, n_idx)}},
        "requirements": _wood_recipe(4, 4, 4),
        "construction": _construction(xp=30, time=150),
        "object": {"isThumpable": True, "dismantable": True},
    }]
    return b


def _container4(sheet, color_word, slug, name, subcat, ctype, cap, w, n, e, s, against_wall=False, tooltip=None):
    b = _base(sheet, slug, "%s %s" % (color_word, name), subcat, w)
    if tooltip:
        b["tooltipKey"] = tooltip
    pl = {"kind": "object", "requiresFloor": True}
    if against_wall:
        pl["needToBeAgainstWall"] = True
    b["placement"] = pl
    faces = {"W": _one(sheet, w), "N": _one(sheet, n)}
    if e is not None:
        faces["E"] = _one(sheet, e)
    if s is not None:
        faces["S"] = _one(sheet, s)
    b["stages"] = [{
        "id": "built",
        "geometry": {"faces": faces},
        "requirements": _wood_recipe(6, 6, 4),
        "construction": _construction(xp=40, time=150),
        "object": {"isThumpable": True, "dismantable": True, "isProp": True, "canBePadlocked": True},
        "container": {"type": ctype, "capacity": cap},
    }]
    return b


def build_sheet(sheet, color_word, n):
    lay = LAYOUT_S4 if n == 4 else LAYOUT_STD
    out = []
    out.append(_multi_bed(sheet, color_word, "bed", "Floor Bed", lay["bed"], 8, 6, 5, 50))
    out.append(_multi_bed(sheet, color_word, "bed_large", "Large Floor Bed", lay["bed4"], 12, 8, 6, 60))
    # names match the art (user 2026-08-28); ids unchanged
    out.append(_simple(sheet, color_word, "nightstand", "Small Table", "Furniture", 58, 59))
    out.append(_container4(sheet, color_word, "dresser_1", "Low Cabinet", "Dressers", "dresser", 20, 62, 63, None, None, tooltip="Tooltip_Dresser"))
    out.append(_container4(sheet, color_word, "dresser_2", "Dresser with Mirror", "Dressers", "dresser", 20, 25, 24, 26, 27, tooltip="Tooltip_Dresser"))
    out.append(_container4(sheet, color_word, "dresser_3", "Wide Dresser", "Dressers", "dresser", 20, 29, 28, 30, 31, tooltip="Tooltip_Dresser"))
    out.append(_container4(sheet, color_word, "dresser_4", "Small Chest of Drawers", "Dressers", "dresser", 20, 33, 32, 34, 35, tooltip="Tooltip_Dresser"))
    out.append(_container4(sheet, color_word, "dresser_5", "Bedside Table", "Dressers", "sidetable", 10, 37, 36, 38, 39, tooltip="Tooltip_Dresser"))
    out.append(_container4(sheet, color_word, "dresser_6", "Low Shelf", "Shelving", "shelves", 20, 53, 52, 54, 55, tooltip="Tooltip_craft_bookcaseDesc"))
    out.append(_wardrobe(sheet, color_word, lay["wardrobe"]))
    out.append(_container4(sheet, color_word, "bookcase", "Bookcase", "Shelving", "shelves", 40, 49, 48, 50, 51, tooltip="Tooltip_craft_bookcaseDesc"))
    out.append(_container4(sheet, color_word, "bookcase_wall", "Wall Shelf", "Shelving", "shelves", 40, 56, 57, None, None, against_wall=True, tooltip="Tooltip_craft_bookcaseDesc"))
    return out


def build_document():
    builds = []
    for i, (sheet, word) in enumerate(SHEETS, start=1):
        builds.extend(build_sheet(sheet, word, i))
    return {
        "schemaVersion": 1,
        "category": "Furniture and Appliances",
        "source": ("Dirkies d_furniture_bedroom_01..05 (Daddy Dirkie / Melos tiles), rev 2. 12 pieces/"
                   "sheet x 5 = 60: 2-tile floor bed, 4-tile large floor bed, 2-tile wardrobe (each one "
                   "piece with 4 facings), nightstand, 6 dressers, bookcase, wall bookcase. Names by "
                   "sheet color (Cream/Grey/Oak/Weathered/Birch). Multi-tile layouts copied from the "
                   "in-game-confirmed TikiTown bedroom; sheet 4 (Weathered) derived from its .tiles."),
        "buildables": builds,
    }


def main():
    import json
    doc = build_document()
    out = r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables\61_community_dirkies_bedroom.json"
    json.dump(doc, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    ids = [b["id"] for b in doc["buildables"]]
    assert len(ids) == len(set(ids)), "dup ids: %s" % [i for i in ids if ids.count(i) > 1]
    print("wrote %s" % out)
    print("sheets=%d pieces/sheet=12 total=%d unique_ids=%d" % (len(SHEETS), len(ids), len(set(ids))))


if __name__ == "__main__":
    main()
