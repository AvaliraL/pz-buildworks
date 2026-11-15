# -*- coding: utf-8 -*-
"""Generate 51_tikitown_commercial_glass_walls.json (user, 2026-11-14): storefront glass walls and door
frames from Drazion's walls_commercial_tterika_01/02/03/04/05/07/08.

Source: BuildingCraft's "Erika's tiles" addon (buildingcraft_b42_inventory.py). Drazion's *_tterika_*
sheets are copies of Erika's tiles at the same indices; the addon builds tterika 04/05/07/08 (its
Erika 06/09 have no tterika copy). The user pointed out 02 and 03 have the same layout, and 01 does
too: the tile properties of all seven sheets match at every index (checked below), so every sheet
gets the same pieces. Nothing built any of these tiles before (TILE_COVERAGE_INVENTORY).

Per sheet (one frame colour), with the addon's piece layout:
  glass styles at base 24, 40, 48, 64, 72, 88, 96, 112, one card each:
    base+0 / base+1  glass pane, W / N (windowW / windowN, can be smashed: SmashedTileOffset 4)
    base+2           NW corner (WallNWTrans), also the pane's cornerSprite
    base+3           end post (WallSE), also the pane's pillarSprite
  door frames 0-15, one card: single frames 0/1, 2/3, 4/5, 6/7 (W / N), double-door frame halves
    8/10 (left), 9/11 (right), and with a glass transom 12/14 (left), 13/15 (right). Each half is a
    one-tile door frame like the addon builds it; the tiles carry DoubleDoor1/2 for a double door.
  Not built (as in the addon): the smashed (+4) and glass-removed (+8) states, and tiles 16-23
  (thin trim / overlays).

Piece setup and cost copy our shipped TikiTown storefront glass (26_tikitown_glass_accurate.json,
confirmed): pane = wall with dontNeedFrame + providesWindowFrame + windowGlass onCreate, corner and
post pieces with the same object flags; cost = the vanilla B42 metal window frame (3 small sheet metal,
4 blowtorch uses, MetalWelding 3). The addon's wood cost (2 planks + 4 nails, Woodwork 4) is not used:
these are metal storefront frames and would differ from the glass walls already in the menu.
Door frames use the same cost with KBW's door-frame object flags. NOT yet tested in game.
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kbw_tilepatch as k   # noqa: E402

OUT = r"c:\Users\josep\Kiro\zomboid\tikitown\51_tikitown_commercial_glass_walls.json"
TEMPLATE = r"c:\Users\josep\Kiro\zomboid\tikitown\26_tikitown_glass_accurate.json"
PREFIX = "worldessentials.tikitown.commglass."
SHEETS = {  # sheet number -> frame colour (read from the art)
    1: "Black", 2: "Maroon", 3: "Gray", 4: "White", 5: "Green", 7: "Blue", 8: "Red",
}
STYLES = [  # (base tile, slug, name) - names read from the art
    (24, "window_panel", "Storefront Window"),
    (40, "full", "Full Storefront Window"),
    (48, "transom_panes", "Storefront Window with Transom and Lower Panes"),
    (64, "plain_panel", "Plain Storefront Window"),
    (72, "transom_panel", "Storefront Window with Transom"),
    (88, "full_transom", "Full Storefront Window with Transom"),
    (96, "four_pane", "Four-Pane Storefront Window"),
    (112, "six_pane", "Six-Pane Storefront Window"),
]
DOOR_FRAMES = [  # (W tile, N tile, slug, name)
    (0, 1, "door_frame", "Storefront Door Frame"),
    (2, 3, "door_frame_header", "Storefront Door Frame with Header"),
    (4, 5, "door_frame_transom", "Storefront Door Frame with Glass Transom"),
    (6, 7, "door_frame_tall_transom", "Storefront Door Frame with Tall Glass Transom"),
    (8, 10, "double_left", "Storefront Double Door Frame (Left)"),
    (9, 11, "double_right", "Storefront Double Door Frame (Right)"),
    (12, 14, "double_transom_left", "Storefront Double Door Frame with Glass Transom (Left)"),
    (13, 15, "double_transom_right", "Storefront Double Door Frame with Glass Transom (Right)"),
]
DOOR_OBJECT = {"isThumpable": True, "dismantable": True, "isDoorFrame": True, "canPassThrough": True}


def _sheet(n):
    return "walls_commercial_tterika_%02d" % n


def _templates():
    """Pane / corner / pillar entries of our shipped storefront glass, used for cost and flags."""
    d = json.load(open(TEMPLATE, encoding="utf-8"))
    by = {}
    for b in d["buildables"]:
        by.setdefault(b.get("pieceClass") or "pane", b)
    return by


def _check_tiles(ts):
    """Every sheet has the same tile flags as 04 at every index, and the pieces sit on the right flags."""
    ref = ts[_sheet(4).encode()][6]
    for n in SHEETS:
        t = ts[_sheet(n).encode()][6]
        if [sorted(k_ for k_, _v in p) for p in t] != [sorted(k_ for k_, _v in p) for p in ref]:
            raise RuntimeError("%s does not match the layout of %s" % (_sheet(n), _sheet(4)))
    flags = lambda i: {k_.decode() for k_, _v in ref[i]}
    for base, _s, _n in STYLES:
        if not ({"windowW"} <= flags(base) and "windowN" in flags(base + 1)
                and "WallNWTrans" in flags(base + 2) and "WallSE" in flags(base + 3)):
            raise RuntimeError("glass style %d: unexpected tile flags" % base)
    for w, n, _s, _n in DOOR_FRAMES:
        if not (any(f.startswith("DoorWallW") for f in flags(w)) and any(f.startswith("DoorWallN") for f in flags(n))):
            raise RuntimeError("door frame %d/%d: unexpected tile flags" % (w, n))


def _piece(tmpl, bid, name, faces, group, level, obj=None, pclass=None):
    b = copy.deepcopy(tmpl)
    b["id"] = PREFIX + bid
    b["displayName"] = name
    b["translationKey"] = "IGUI_WETiki_commglass_" + bid
    b["tooltipKey"] = "Tooltip_KBW_Shared_Wall"
    b["iconSprite"] = faces["W"]
    b["tags"] = ["tikitown", "drazion", "world-essentials", "commercial-glass"]
    b["allowSpriteReuse"] = True
    st = b["stages"][0]
    st["geometry"] = {"faces": {f: {"layers": [{"rows": [[s]]}]} for f, s in faces.items()}}
    if obj is not None:
        st["object"] = obj
    b["group"] = dict(group, level=level)
    if pclass:
        b["pieceClass"] = pclass
    else:
        b.pop("pieceClass", None)
    return b


def build():
    _v, ts, _o = k._parse(open(k._TIKITOWN_TILES, "rb").read())
    _check_tiles(ts)
    T = _templates()
    out = []
    for n, colour in SHEETS.items():
        sh = _sheet(n)
        spr = lambda i: "%s_%d" % (sh, i)
        for base, slug, name in STYLES:
            key = "%02d_%s" % (n, slug)
            group = {"id": PREFIX + key, "name": "%s %s" % (colour, name),
                     "translationKey": "IGUI_WETiki_commglass_%s_group" % key}
            pane_obj = dict(T["pane"]["stages"][0]["object"], cornerSprite=spr(base + 2), pillarSprite=spr(base + 3))
            out.append(_piece(T["pane"], key, "%s %s" % (colour, name), {"W": spr(base), "N": spr(base + 1)},
                              group, 1, pane_obj, "window"))
            out.append(_piece(T["corner"], key + "_corner", "%s %s (Corner)" % (colour, name),
                              {"W": spr(base + 2), "N": spr(base + 2)}, group, 2, pclass="corner"))
            out.append(_piece(T["pillar"], key + "_post", "%s %s (Post)" % (colour, name),
                              {"W": spr(base + 3), "N": spr(base + 3)}, group, 3, pclass="pillar"))
        key = "%02d_door_frames" % n
        group = {"id": PREFIX + key, "name": "%s Storefront Door Frames" % colour,
                 "translationKey": "IGUI_WETiki_commglass_%s_group" % key}
        for lvl, (w, nn, slug, name) in enumerate(DOOR_FRAMES, 1):
            b = _piece(T["corner"], "%02d_%s" % (n, slug), "%s %s" % (colour, name), {"W": spr(w), "N": spr(nn)},
                       group, lvl, dict(DOOR_OBJECT), "door")
            out.append(b)
    for b in out:                                  # only panes break like windows (windowGlass onCreate)
        if b.get("pieceClass") != "window":
            b["stages"][0].pop("callbacks", None)
    return out


def main():
    out = build()
    ids = [b["id"] for b in out]
    assert len(ids) == len(set(ids))
    doc = {
        "schemaVersion": 1,
        "category": "Walls and Wall Finishes",
        "source": ("TikiTown walls_commercial_tterika_01/02/03/04/05/07/08 (Drazion's Tilepack): storefront glass "
                   "walls (8 styles: pane, corner, post) and door frames per frame colour, piece layout from "
                   "BuildingCraft's Erika's tiles addon, setup and cost from 26_tikitown_glass_accurate.json. "
                   "Generated by pz_craft_loops/tikitown_commercial_glass_walls.py."),
        "buildables": out,
    }
    json.dump(doc, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("wrote %s (%d buildables)" % (OUT, len(ids)))


if __name__ == "__main__":
    main()
