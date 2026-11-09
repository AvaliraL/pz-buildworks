# -*- coding: utf-8 -*-
"""TikiTown naming pass (approved by user 2026-11-08). Edits the SOURCE JSONs in place, like the
earlier apply_catpass passes. Idempotent: running it again changes nothing. Names / group titles /
subcategories only: ids, recipes, health, materials and translation keys are never touched.

1. Wall sheets (21_tikitown_walls_accurate.json): "Brick Wall - Style 7" -> "Dark Green Brick Wall"
   (+ the piece's own suffix, e.g. " (Window 3)"); group title the same; subcategory by the real
   type (the plain "Walls" sheets #1-#12 are brick / stone; cement gets its own "Concrete" type).
   Lower walls / wall overlays (39 / 40) take their names and types from this file, so regenerate
   them afterwards (tikitown_wall_overlays.py).
2. Furniture group titles: drop the "TikiTown " prefix (25 bedroom, 30 shelving).

Spelling follows vanilla PZ: "Gray". Contact sheets used to pick the names:
_names_walls_1.png / _names_walls_2.png (name_contact_sheet.py).
"""
import json, os, re, shutil, sys

DIR = r"c:\Users\josep\Kiro\zomboid\tikitown"
BACKUP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_naming_backup")
WALLS = "21_tikitown_walls_accurate.json"
GROUP_PREFIX_FILES = ["25_tikitown_bedroom.json", "30_tikitown_shelving.json"]

# sheet -> (style name, type). Type = subcategory word ("Brick" -> "Brick Walls").
STYLES = {
    "tikitown_walls_wood_01": ("Dark Walnut Plank", "Wooden"),
    "tikitown_vanilla_walls_add_01": ("Pink Brick", "Brick"),
    "tikitown_vanilla_walls_add_02": ("Yellow Brick", "Brick"),
    "tikitown_vanilla_walls_add_03": ("Gray Brick", "Brick"),
    "tikitown_vanilla_walls_add_04": ("Pale Blue Brick", "Brick"),
    "tikitown_vanilla_walls_add_05": ("Weathered Red Brick", "Brick"),
    "tikitown_vanilla_walls_add_06": ("Rustic Orange Brick", "Brick"),
    "tikitown_vanilla_walls_add_07": ("Cream Brick", "Brick"),
    "tikitown_vanilla_walls_add_08": ("Sandstone Block", "Stone"),
    "tikitown_vanilla_walls_add_09": ("Gray Stone Block", "Stone"),
    "tikitown_vanilla_walls_add_10": ("Chocolate Brick", "Brick"),
    "tikitown_vanilla_walls_add_11": ("Tan Stone Panel", "Stone"),
    "tikitown_vanilla_walls_add_12": ("Olive Green Brick", "Brick"),
    "tikitown_vanilla_walls_add_bathroom_01": ("White Tiled Wainscot", "Bathroom"),
    "tikitown_walls_bathroom_01": ("White Marble", "Bathroom"),
    "tikitown_walls_bathroom_02": ("Gray Marble Tile", "Bathroom"),
    "tikitown_walls_bathroom_03": ("Navy Shell Pattern", "Bathroom"),
    "tikitown_walls_bathroom_04": ("Black Slate", "Bathroom"),
    "tikitown_walls_brick_01": ("White Brick", "Brick"),
    "tikitown_walls_brick_02": ("Bright Red Brick", "Brick"),
    "tikitown_walls_brick_03": ("Rose Beige Brick", "Brick"),
    "tikitown_walls_brick_04": ("Brown Brick", "Brick"),
    "tikitown_walls_brick_05": ("Black Brick", "Brick"),
    "tikitown_walls_brick_06": ("Burgundy Brick", "Brick"),
    "tikitown_walls_brick_07": ("Dark Green Brick", "Brick"),
    "tikitown_walls_brick_08": ("Bright Orange Brick", "Brick"),
    "tikitown_walls_brick_09": ("Mustard Brick", "Brick"),
    "tikitown_walls_brick_10": ("Navy Brick", "Brick"),
    "tikitown_walls_brick_11": ("Olive Brown Brick", "Brick"),
    "tikitown_walls_brick_12": ("Purple Brick", "Brick"),
    "tikitown_walls_brick_purewhite": ("Pure White Brick", "Brick"),
    "tikitown_walls_brick_standard": ("Classic Red Brick", "Brick"),
    "tikitown_walls_bricks_dirtywhite": ("Dirty White Brick", "Brick"),
    "tikitown_walls_cement_01": ("Concrete", "Concrete"),
    "tikitown_walls_decorative_01": ("Dark Fieldstone", "Decorative"),
    "tikitown_walls_decorative_02": ("Golden Cobblestone", "Decorative"),
    "tikitown_walls_decorative_03": ("Rubble Stone", "Decorative"),
    "tikitown_walls_decorative_04": ("Checkered Stone Tile", "Decorative"),
    "tikitown_walls_decorative_05": ("Dark Wood Panel", "Decorative"),
    "tikitown_walls_interior_01": ("Blue-Gray Painted", "Interior"),
    "tikitown_walls_metal_01": ("Beige Metal Panel", "Industrial"),
    "tikitown_walls_metal_02": ("Gray Corrugated Metal", "Industrial"),
    "tikitown_walls_plaster_01": ("White Plaster", "Plaster"),
    "tikitown_walls_plaster_02": ("Taupe Plaster", "Plaster"),
    "tikitown_walls_siding_01": ("Red Siding", "Siding"),
    "tikitown_walls_siding_02": ("Blue Siding", "Siding"),
    "tikitown_walls_siding_03": ("White Corrugated Siding", "Siding"),
    "tikitown_walls_siding_04": ("Red Corrugated Siding", "Siding"),
    "tikitown_walls_stone_01": ("Gray Fieldstone", "Stone"),
    "tikitown_walls_stone_02": ("Brown Fieldstone", "Stone"),
    "tikitown_walls_wallpaper_01": ("Blue Trellis Wallpaper", "Wallpaper"),
    "tikitown_walls_wallpaper_02": ("Rose Floral Wallpaper", "Wallpaper"),
    "tikitown_walls_wallpaper_03": ("Palm Leaf Wallpaper", "Wallpaper"),
    "tikitown_walls_wallpaper_04": ("Bamboo Wallpaper", "Wallpaper"),
    "tikitown_walls_wallpaper_05": ("Burgundy Damask Wallpaper", "Wallpaper"),
    "tikitown_walls_wallpaper_06": ("Blue Tree Wallpaper", "Wallpaper"),
    "tikitown_walls_wallpaper_07": ("Sage Vine Wallpaper", "Wallpaper"),
    "tikitown_walls_wallpaper_08": ("Faded Rose Wallpaper", "Wallpaper"),
    "tikitown_walls_wallpaper_09": ("Gray Watercolor Wallpaper", "Wallpaper"),
    "tikitown_walls_wallpaper_10": ("Pastel Lilac Wallpaper", "Wallpaper"),
}

# a piece's own suffix after the style name: " (Window 3)", " (Door Frame)", " Corner", " Pillar"
# ---- round 2 (approved 2026-11-08): the other wall styles, doors, beds -------------------------
# type None = keep the piece's current subcategory
STYLES.update({
    "tikitown_commercial_walls_add_01": ("Taupe Cinder Block", "Commercial"),
    "tikitown_commercial_walls_add_02": ("Pale Green Cinder Block", "Commercial"),
    "tikitown_commercial_walls_add_03": ("Khaki Cinder Block", "Commercial"),
    "tikitown_tents_01": ("Tent Canvas", None),
    "tt_melos_tiles_overgrown_ruins_01": ("Overgrown Ruined Brick", "Brick"),
    "walls_exterior_half_tterika_01": ("Blue-Gray Brick Half", "Exterior"),
    "walls_exterior_house_tterika_02": ("Red Plank Siding", "Exterior"),
    "walls_interior_bathroom_tterika_01": ("White Square Tile", "Bathroom"),
    "walls_interior_house_tterika_02": ("Gray-Green Painted", "Interior"),
})

DOORS = "22_tikitown_doors.json"
# contact-sheet order: #0-#32 = fixtures_doors_tterika_01_0..128, #33-#96 = _02_0..252 (step 4)
DOOR_NAMES = [
    "Pale Blue Panel Door", "Black Panel Door", "Tan Panel Door", "Dark Brown Panel Door",
    "Brown Panel Door", "Gray Panel Door", "Blue Panel Door", "Red Panel Door",
    "Dark Green Panel Door", "Yellow Panel Door", "Gray Metal Door", "Gray Metal Door with Window",
    "Navy Metal Door", "Navy Metal Door with Window", "Blue Panel Door with Window",
    "Red Panel Door with Window", "Dark Green Panel Door with Window", "Yellow Panel Door with Window",
    "White Louvered Door", "Brown Louvered Door", "Gray Commercial Door", "Beige Commercial Door",
    "Mustard Commercial Door", "Black Commercial Door", "Gray Commercial Door with Window",
    "Beige Commercial Door with Window", "White Commercial Door", "White Commercial Door with Window",
    "Maroon Glass Door", "Black Glass Door", "White Glass Door", "Green Glass Door",
    "Ochre Kickplate Door",
]
_PAIRS = [  # sheet 02, mirror pairs in order (second of each pair gets " (Mirrored)")
    "White Six-Panel Door", "Mahogany Six-Panel Door", "Sky Blue Arched Panel Door",
    "Black Six-Panel Door", "Tan Six-Panel Door", "Dark Brown Six-Panel Door", "Brown Six-Panel Door",
    "Gray Six-Panel Door", "Blue Six-Panel Door", "Red Six-Panel Door", "Dark Green Six-Panel Door",
    "Yellow Six-Panel Door", "Brown Door with Window", "White Door with Window", "Navy Flush Door",
    "White Flush Door", "Maroon Framed Glass Door", "Black Framed Glass Door",
    "White Framed Glass Door", "Green Framed Glass Door", "Red Framed Glass Door",
    "Blue Framed Glass Door", "Copper Framed Glass Door", "Mahogany Framed Glass Door",
    "Blue Kickplate Door", "Blue Kickplate Door with Window", "Red Kickplate Door",
    "Red Kickplate Door with Window", "Black Kickplate Door", "Black Kickplate Door with Window",
    "Green Kickplate Door", "Mustard Kickplate Door",
]
for _n in _PAIRS:
    DOOR_NAMES += [_n, _n + " (Mirrored)"]
DOOR_IDS = (["worldessentials.tikitown.fixtures_doors_tterika_01_%d" % (i * 4) for i in range(33)]
            + ["worldessentials.tikitown.fixtures_doors_tterika_02_%d" % (i * 4) for i in range(64)])
# 12 type groups (index ranges into DOOR_NAMES); members ordered by level = their order here
DOOR_GROUPS = [
    ("panel", "Panel Door", list(range(0, 10))),
    ("panel_window", "Panel Door with Window", list(range(14, 18))),
    ("metal", "Metal Door", list(range(10, 14))),
    ("louvered", "Louvered Door", [18, 19]),
    ("commercial", "Commercial Door", list(range(20, 28))),
    ("glass", "Glass Door", list(range(28, 32))),
    ("six_panel", "Six-Panel Door", list(range(33, 37)) + list(range(39, 57))),
    ("arched_panel", "Arched Panel Door", [37, 38]),
    ("window", "Door with Window", list(range(57, 61))),
    ("flush", "Flush Door", list(range(61, 65))),
    ("framed_glass", "Framed Glass Door", list(range(65, 81))),
    ("kickplate", "Kickplate Door", [32] + list(range(81, 97))),
]

BEDROOM = "25_tikitown_bedroom.json"
BED_NAMES = {
    "furniture_bedding_tterika_01_double_a": "White Double Bed",
    "furniture_bedding_tterika_01_single_r4": "White Single Bed",
    "furniture_bedding_tterika_01_single_r5": "Pink Single Bed",
    "furniture_bedding_tterika_01_single_r6": "Green Single Bed",
    "furniture_bedding_tterika_01_single_r7": "Blue Single Bed",
    "furniture_bedding_tterika_01_single_r8": "Beige Single Bed",
}
BED_GROUP_TITLES = {"Bedding Single Bed": "Single Bed", "TikiTown Bedding Single Bed": "Single Bed"}

_SUFFIX = re.compile(r"(\s\([^()]*\)|\sCorner|\sPillar)$")


def sheet_of(bid):
    """'...tikitown_walls_brick_01_16' / '..._2_corner' / '..._3_pillar' -> 'tikitown_walls_brick_01'."""
    tail = bid.split("worldessentials.tikitown.", 1)[-1]
    tail = re.sub(r"_(corner|pillar)$", "", tail)
    return tail.rpartition("_")[0]


def _load(fn):
    p = os.path.join(DIR, fn)
    return p, json.load(open(p, encoding="utf-8"))


def _save(p, doc, raw_before):
    os.makedirs(BACKUP, exist_ok=True)
    bk = os.path.join(BACKUP, os.path.basename(p))
    if not os.path.isfile(bk):                      # keep the ORIGINAL (first run only)
        open(bk, "w", encoding="utf-8").write(raw_before)
    json.dump(doc, open(p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)


def rename_walls(report):
    p, doc = _load(WALLS)
    raw = open(p, encoding="utf-8").read()
    changed, seen = 0, set()
    for b in doc["buildables"]:
        sh = sheet_of(b["id"])
        if sh not in STYLES:
            continue
        seen.add(sh)
        style, typ = STYLES[sh]
        base = "%s Wall" % style
        m = _SUFFIX.search(b.get("displayName", ""))
        new = base + (m.group(1) if m else "")
        sub = "%s Walls" % typ if typ else b.get("subcategory")
        before = (b.get("displayName"), (b.get("group") or {}).get("name"), b.get("subcategory"))
        b["displayName"] = new
        if b.get("group"):
            b["group"]["name"] = base
        b["subcategory"] = sub
        if before != (new, (b.get("group") or {}).get("name"), sub):
            changed += 1
    missing = sorted(set(STYLES) - seen)
    if missing:
        raise RuntimeError("style sheets not found in %s: %s" % (WALLS, missing))
    _save(p, doc, raw)
    report.append("%s: %d pieces renamed (%d sheets)" % (WALLS, changed, len(seen)))
    return doc


def rename_doors(report):
    assert len(DOOR_NAMES) == len(DOOR_IDS) == 97
    covered = sorted(i for _s, _t, idx in DOOR_GROUPS for i in idx)
    assert covered == list(range(97)), "door groups must cover every door exactly once"
    p, doc = _load(DOORS)
    raw = open(p, encoding="utf-8").read()
    by_id = {b["id"]: b for b in doc["buildables"]}
    missing = [i for i in DOOR_IDS if i not in by_id]
    if missing:
        raise RuntimeError("doors not found: %s" % missing[:5])
    changed = 0
    for slug, title, idx in DOOR_GROUPS:
        for level, i in enumerate(idx, 1):
            b = by_id[DOOR_IDS[i]]
            grp = {"id": "worldessentials.tikitown.doors_%s" % slug, "name": title,
                   "translationKey": "IGUI_WETiki_doors_%s_group" % slug, "level": level}
            if b.get("displayName") != DOOR_NAMES[i] or b.get("group") != grp:
                changed += 1
            b["displayName"] = DOOR_NAMES[i]
            b["group"] = grp
    _save(p, doc, raw)
    report.append("%s: %d doors renamed / regrouped into %d type groups" % (DOORS, changed, len(DOOR_GROUPS)))
    return doc


def rename_beds(report):
    p, doc = _load(BEDROOM)
    raw = open(p, encoding="utf-8").read()
    n = 0
    for b in doc["buildables"]:
        key = b["id"].split(".")[-1]
        if key in BED_NAMES and b.get("displayName") != BED_NAMES[key]:
            b["displayName"] = BED_NAMES[key]; n += 1
        g = b.get("group") or {}
        if g.get("name") in BED_GROUP_TITLES:
            g["name"] = BED_GROUP_TITLES[g["name"]]; n += 1
    _save(p, doc, raw)
    report.append("%s: %d bed names / titles changed" % (BEDROOM, n))


def drop_group_prefix(report):
    for fn in GROUP_PREFIX_FILES:
        p, doc = _load(fn)
        raw = open(p, encoding="utf-8").read()
        n = 0
        for b in doc["buildables"]:
            g = b.get("group") or {}
            if g.get("name", "").startswith("TikiTown "):
                g["name"] = g["name"][len("TikiTown "):]
                n += 1
        _save(p, doc, raw)
        report.append("%s: %d group titles lost the 'TikiTown ' prefix" % (fn, n))


_GREY = re.compile(r"\bGrey\b")


def vanilla_gray(report):
    """'Grey' -> 'Gray' (vanilla PZ spelling) in names, group titles and subcategories of every
    TikiTown source file. 39 / 40 are regenerated from 21, so they follow automatically."""
    import build_tikitown_mod as bt
    for fn in bt.SRC_FILES:
        if fn.startswith(("39_", "40_")):
            continue
        p = os.path.join(DIR, fn)
        if not os.path.isfile(p):
            continue
        raw = open(p, encoding="utf-8").read()
        if not _GREY.search(raw):
            continue
        doc = json.loads(raw)
        n = 0
        for b in doc["buildables"]:
            for holder, key in ((b, "displayName"), (b, "subcategory"), (b.get("group") or {}, "name")):
                v = holder.get(key)
                if isinstance(v, str) and _GREY.search(v):
                    holder[key] = _GREY.sub("Gray", v)
                    n += 1
        if n:
            _save(p, doc, raw)
            report.append("%s: %d Grey -> Gray" % (fn, n))


def check_unique(doc):
    """Within a subcategory, names must still tell pieces apart."""
    seen = {}
    for b in doc["buildables"]:
        k = (b.get("category"), b.get("subcategory"), b.get("displayName"))
        if k in seen and (b.get("group") or {}).get("id") != (seen[k].get("group") or {}).get("id"):
            raise RuntimeError("duplicate name after renaming: %s (%s, %s)" % (k, b["id"], seen[k]["id"]))
        seen[k] = b


def main():
    report = []
    doc = rename_walls(report)
    check_unique(doc)
    drop_group_prefix(report)
    check_unique(rename_doors(report))
    rename_beds(report)
    vanilla_gray(report)
    print("\n".join(report))


if __name__ == "__main__":
    main()
