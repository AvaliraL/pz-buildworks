# -*- coding: utf-8 -*-
"""Generate 36_tikitown_tterika_storage.json from Drazion's furniture_storage_tterika_02
(TikiTown pack, mod tikitown_tiles; 8 cols x 6 rows @128x256, art only in tikitown_tiles.pack).

12 single-tile containers: each sheet row holds 2 objects, each object 4 consecutive sprites in
S, E, N, W order (user-confirmed, and checked against the art extracted from the pack). NOTE: the
pack's .tiles Facing for rows 3-5 (idx 24-47) says E,S,W,N -- that metadata is wrong; the art in
those rows follows the same S,E,N,W order as rows 0-2.

Container type / capacity come from the tile where it sets them; tiles with no
ContainerCapacity get 40 (our locker convention). Metal build: cost = half the military crate
(the reinforced versions' cost, see _half_crate_inputs), Welding 4 + Projects in Metal knowledge.
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import counter_variants

SHEET = "furniture_storage_tterika_02"


def _half_crate_inputs():
    """Base cost = HALF the military crate (the reinforced versions' cost), user 2026-08-28.
    Halves every consumed amount / drained use: round DOWN, minimum 1 (user). Tools unchanged.
    Read from the crate's own definition so it stays in sync with the reinforced cost."""
    out = []
    for inp in copy.deepcopy(counter_variants.crate_stage()["requirements"]["inputs"]):
        if inp.get("role") != "tool":
            for k in ("amount", "uses"):
                if isinstance(inp.get(k), int):
                    inp[k] = max(1, inp[k] // 2)
        out.append(inp)
    return out
OUT = r"c:\Users\josep\Kiro\zomboid\tikitown\36_tikitown_tterika_storage.json"

# (base index, display name, subcategory, container type, capacity)
OBJECTS = [
    (0,  "Small Grey Metal Cabinet",   "Lockers", "metal_shelves", 40),
    (4,  "Small Black Footlocker",     "Chests",  "locker",        10),
    (8,  "Green Military Locker",      "Lockers", "militarylocker", 40),
    (12, "Small Olive Military Locker", "Lockers", "locker",       40),
    (16, "Steel Military Locker",      "Lockers", "militarylocker", 40),
    (20, "Small Steel Military Locker", "Lockers", "locker",       40),
    (24, "Pink Locker",                "Lockers", "locker",        40),
    (28, "Red Locker",                 "Lockers", "locker",        40),
    (32, "Grey Locker",                "Lockers", "locker",        40),
    (36, "Green Locker",               "Lockers", "locker",        40),
    (40, "Orange Locker",              "Lockers", "locker",        40),
    (44, "Purple Locker",              "Lockers", "locker",        40),
]
ORDER = ("S", "E", "N", "W")


def _spr(i):
    return "%s_%d" % (SHEET, i)


def _face(i):
    return {"layers": [{"rows": [[_spr(i)]]}]}


def _buildable(base, name, subcat, ctype, cap):
    bid = "worldessentials.tikitown.%s_%d" % (SHEET, base)
    return {
        "id": bid,
        "translationKey": "IGUI_WETiki_%s_%d" % (SHEET, base),
        "displayName": name,
        "tooltipKey": "Tooltip_KBW_Shared_StorageFixture",
        "category": "Containers",
        "subcategory": subcat,
        "material": "Metal",
        "materialTags": ["Metal"],
        "iconSprite": _spr(base),
        "placement": {"kind": "object", "requiresFloor": True},
        # "reinforce": counter_variants.py adds a <id>.reinforced copy (crate cost, capacity 100)
        "tags": ["tikitown", "drazion", "world-essentials", "container", "locker", "reinforce"],
        "stages": [{
            "id": "built",
            "geometry": {"faces": {f: _face(base + k) for k, f in enumerate(ORDER)}},
            "requirements": {
                "inputs": _half_crate_inputs(),
                "skills": {"MetalWelding": 4},
                "knowledge": {
                    "recipes": ["KBWKnowledge_ProjectsInMetal_Diverse"],
                    "hideUntilLearned": True,
                    "needToBeLearned": True,
                    "sources": [{"type": "magazine", "item": "KnoxBuildworks.ProjectsInMetal_Diverse"}],
                    "skillAlternatives": [{"mode": "all", "skills": {"MetalWelding": 6}}],
                },
            },
            "construction": {"time": 75, "timedAction": "BuildWallMetal",
                             "completionSound": "BuildMetalStructureMedium",
                             "category": "Welding", "xp": {"MetalWelding": 50}},
            "object": {"isThumpable": True, "canBePadlocked": True},
            "container": {"type": ctype, "capacity": cap},
        }],
    }


def main():
    doc = {
        "schemaVersion": 1,
        "category": "Containers",
        "source": ("TikiTown furniture_storage_tterika_02 (Drazion's Tilepack): 12 single-tile metal "
                   "containers, 2 per sheet row, each 4 sprites S,E,N,W (the pack's Facing metadata "
                   "for idx 24-47 is wrong; art order verified). Capacity from the tile, else 40."),
        "buildables": [_buildable(*o) for o in OBJECTS],
    }
    json.dump(doc, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    ids = [b["id"] for b in doc["buildables"]]
    assert len(ids) == len(set(ids))
    print("wrote %s (%d buildables)" % (OUT, len(ids)))


if __name__ == "__main__":
    main()
