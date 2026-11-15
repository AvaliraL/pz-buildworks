# -*- coding: utf-8 -*-
"""Generate 68_community_blackwood_props.json (user, 2026-11-14): Blackwood one-offs from the
Community pack (Blackwood.tiles, sheets blackwood3 / 5 / 6 / 7). Names are the pack's CustomNames
(typos fixed). The user's blackwood5 numbers run +7 from the sheet index (47 / 51 / 52 / 54 =
40 / 44 / 45 / 47), checked against the art; blackwood7 "24, 24, 25" = 24 / 25 / 26.

  * blackwood3 14 / 15 cosplay armour stands (solid floor pieces, face east): + mirrored copy
    (faces south). Raccoon Figure cost (file 58, confirmed).
  * blackwood3 17 squid poster (west wall) + mirror (north wall); poster cost (TikiTown posters).
  * blackwood5 16 dartboard (west wall) + mirror; 17 Winchester (north wall) + mirror (west wall).
  * table-top pieces (IsTableTop + IsSurfaceOffset, Surface 34): blackwood5 40 / 44 / 45 / 47,
    blackwood6 60, blackwood7 24 / 25 / 26 / 61. On kbw_tilepatch.BLACKWOOD_TABLETOP (floor / table
    height fix). 44 (ocarina) is a static piece (user 2026-11-14: the "Play Ocarina" music is not
    shipped; blackwood_ocarina.py is no longer wired in). 47 (Zora Storage Amulet) is built as a lamp
    only, "Zora Amulet Lamp" (user 2026-11-14): KBW makes the tile's light switch a native lamp,
    which has no storage, so the definition carries no container. Tterika table-lamp cost (file 52).
  * blackwood7 32 "Red suss" figure (floor, walk-through).
Mirrors: our copies in the ice-shell tileset (kbw_tilepatch.BLACKWOOD_MIRRORS). KBW face = the
wall the piece hangs on / the opposite of the way a floor piece faces (east -> W, south -> N).
NOT yet tested in game.
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kbw_tilepatch import blackwood_mirror_name, blackwood_fixed_name, BLACKWOOD_TABLETOP  # noqa: E402

DELIV = r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables"
OUT = os.path.join(DELIV, "68_community_blackwood_props.json")
STATUE_COST_FROM = ("58_community_fears_rp.json", "community.fears.rp.raccoon_figure")
PREFIX = "community.blackwood."


def _sp(sheet, i):
    return "%s_%d" % (sheet, i)


def _one(s):
    return {"layers": [{"rows": [[s]]}]}


def _hammer():
    return {"id": "tool_hammer", "role": "tool", "mode": "keep", "resourceType": "Item",
            "tags": ["base:hammer"], "amount": 1}


def _item(n, item, amount):
    return {"id": "source_material_%d" % n, "role": "material", "mode": "consume", "resourceType": "Item",
            "items": [item], "amount": amount}


def _statue_cost():
    d = json.load(open(os.path.join(DELIV, STATUE_COST_FROM[0]), encoding="utf-8"))
    b = next(x for x in d["buildables"] if x["id"] == STATUE_COST_FROM[1])
    return copy.deepcopy(b["stages"][0]["requirements"]), copy.deepcopy(b["construction"])


LAMP_COST_FROM = r"c:\Users\josep\Kiro\zomboid\tikitown\52_tikitown_lighting.json"


def _lamp_cost():
    """Requirements, construction and tooltip key of the first tterika table lamp (file 52)."""
    d = json.load(open(LAMP_COST_FROM, encoding="utf-8"))
    b = next(x for x in d["buildables"] if x.get("subcategory") == "Table Lamps")
    st = b["stages"][0]
    con = st.get("construction") or b.get("construction")
    return copy.deepcopy(st["requirements"]), copy.deepcopy(con), b.get("tooltipKey")


POSTER_REQ = {"inputs": [_hammer(), _item(1, "Base.Nails", 1)], "skills": {}}
POSTER_CON = {"time": 100, "timedAction": "BuildWoodenStructureSmall", "completionSound": "BuildWoodenStructureSmall",
              "xp": {"Woodwork": 10}, "category": "Carpentry"}
WALL_REQ = {"inputs": [_hammer(), _item(1, "Base.Plank", 1), _item(2, "Base.Nails", 2)], "skills": {"Woodwork": 1}}
SMALL_REQ = {"inputs": [_hammer(), _item(1, "Base.Plank", 1), _item(2, "Base.Nails", 1)], "skills": {"Woodwork": 2}}
SMALL_CON = {"time": 60, "timedAction": "BuildWoodenStructureSmall", "completionSound": "BuildWoodenStructureSmall",
             "xp": {"Woodwork": 5}, "category": "Carpentry"}
WALKTHROUGH = {"isThumpable": False, "blockAllSquare": False, "canPassThrough": True, "dismantable": True}
SOLID = {"isThumpable": True, "dismantable": True}

FLOOR = {"kind": "object", "requiresFloor": True}
WALL = {"kind": "object", "requiresFloor": True, "needToBeAgainstWall": True}

ARMOR_GROUP = {"id": PREFIX + "cosplay_armor", "name": "Cosplay Armor Displays",
               "translationKey": "IGUI_community_blackwood_cosplay_armor_group"}


def _piece(slug, name, sub, faces, placement, req, con, obj, tags, container=None, group=None, level=None):
    bid = PREFIX + slug
    st = {"id": "built", "geometry": {"faces": {f: _one(s) for f, s in faces.items()}},
          "requirements": copy.deepcopy(req), "object": dict(obj)}
    if container:
        st["container"] = dict(container)
    b = {
        "id": bid,
        "allowSpriteReuse": True,
        "translationKey": "IGUI_" + bid.replace(".", "_"),
        "displayName": name,
        "category": "Decorations and Landscaping",
        "subcategory": sub,
        "material": "Wood",
        "materialTags": ["Wood"],
        "iconSprite": next(iter(faces.values())),
        "placement": dict(placement),
        "tags": ["community-tilepack", "blackwood", "decoration"] + tags,
        "construction": copy.deepcopy(con),
        "stages": [st],
    }
    if group:
        b["group"] = dict(group, level=level)
    return b


def _mirrored(sheet, i, own, mirror):
    """{own face: pack tile, mirror face: our mirrored copy}."""
    return {own: _sp(sheet, i), mirror: blackwood_mirror_name(sheet, i)}


TABLETOP = [  # (sheet, index, slug, name, subcategory)
    ("blackwood5", 40, "blue_hedgehog_figure", "Speedy Blue Hedgehog Figure", "Statues"),
    ("blackwood5", 44, "ocarina", "Ocarina of Time", "Decor"),
    ("blackwood5", 45, "hyrule_shield", "Shield of Hyrule", "Decor"),
    ("blackwood6", 60, "gadget_figurine", "Gadget Figurine", "Statues"),
    ("blackwood7", 24, "halo_helmets", "Halo Helmets", "Decor"),
    ("blackwood7", 25, "alien_gun", "Alien Gun", "Decor"),
    ("blackwood7", 26, "needle_guns", "Needle Guns", "Decor"),
    ("blackwood7", 61, "kermit_the_murderer", "Kermit the Murderer Figure", "Statues"),
]


def build_document():
    sreq, scon = _statue_cost()
    out = []
    for level, (i, slug, name) in enumerate([(14, "cosplay_armor_gold", "War on a Star Cosplay (Gold Armor)"),
                                             (15, "cosplay_armor_trooper", "War on a Star Cosplay (Trooper Armor)")], 1):
        # both faces on our copies without the pack's `solid` (user, in game 2026-11-14: they should
        # not block movement), walk-through
        out.append(_piece(slug, name, "Statues",
                          {"W": blackwood_fixed_name("blackwood3", i), "N": blackwood_mirror_name("blackwood3", i)},
                          FLOOR, sreq, scon, WALKTHROUGH, ["statue"], group=ARMOR_GROUP, level=level))
    # west face: our Facing-corrected copy (the pack tile says Facing N, so vanilla's moveable
    # placement looked for a south wall and refused the west wall; in game 2026-11-14)
    out.append(_piece("cosplay_squid_poster", "Cosplay Squid Poster", "Posters",
                      {"W": blackwood_fixed_name("blackwood3", 17), "N": blackwood_mirror_name("blackwood3", 17)},
                      WALL, POSTER_REQ, POSTER_CON, WALKTHROUGH, ["poster"]))
    out.append(_piece("dartboard", "Dartboard", "Decor", _mirrored("blackwood5", 16, "W", "N"), WALL,
                      WALL_REQ, POSTER_CON, WALKTHROUGH, ["wall-decor"]))
    out.append(_piece("winchester", "Ye Ol' Winchester", "Decor", _mirrored("blackwood5", 17, "N", "W"), WALL,
                      WALL_REQ, POSTER_CON, WALKTHROUGH, ["wall-decor"]))
    for sheet, i, slug, name, sub in TABLETOP:
        assert _sp(sheet, i) in BLACKWOOD_TABLETOP
        tags = ["table-top"]
        out.append(_piece(slug, name, sub, {"W": _sp(sheet, i)}, FLOOR, SMALL_REQ, SMALL_CON, WALKTHROUGH, tags))
    # Zora amulet: a lamp only (user, 2026-11-14). The pack tile is a light switch (blue light) AND a
    # Storage 100 container, but KBW builds light-switch sprites as a native IsoLightSwitch, which
    # never creates the tile's containers. No container in the definition (no misleading "100").
    # Cost and card type: the tterika table lamps' (file 52, VE lamp cost).
    assert "blackwood5_47" in BLACKWOOD_TABLETOP
    lreq, lcon, ltip = _lamp_cost()
    amulet = _piece("zora_amulet_lamp", "Zora Amulet Lamp", "Table Lamps", {"W": "blackwood5_47"}, FLOOR,
                    lreq, lcon, WALKTHROUGH, ["table-top", "lamp"])
    amulet["category"] = "Lighting"
    amulet["material"] = "Electronics"
    amulet["materialTags"] = ["Electronics"]
    if ltip:
        amulet["tooltipKey"] = ltip
    out.append(amulet)
    out.append(_piece("red_suss_figure", "Red Suss Figure", "Statues", {"W": "blackwood7_32"}, FLOOR,
                      SMALL_REQ, SMALL_CON, WALKTHROUGH, ["statue"]))
    return {
        "schemaVersion": 1,
        "category": "Decorations and Landscaping",
        "source": ("Blackwood one-offs (Community pack Blackwood.tiles): cosplay armour stands, squid poster, "
                   "dartboard, Winchester (mirrored copies KBWCommunityIceShell_256..260, Facing-fixed poster 261), table-top "
                   "figures and props, Zora Storage Amulet, Red Suss figure. Generated by "
                   "pz_craft_loops/blackwood_props.py."),
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
