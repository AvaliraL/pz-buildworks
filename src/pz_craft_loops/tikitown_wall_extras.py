# -*- coding: utf-8 -*-
"""Generate the rest of the standard TikiTown wall sheets (user, 2026-11-08: "we didn't implement the
full sheet"): per sheet, the 27 roof-slope / gable walls and the 3 garage door frame trims.

  41_tikitown_roof_slope_walls.json  "<Style> Roof Slope Wall 1..27", one group per sheet
  42_tikitown_garage_trim.json       "<Style> Garage Door Frame - Left / Center / Right"

Models copied from in-game-confirmed Newburbs pieces (28 / 27):
  * roof slope wall = the sheet's own wall stage (cost, health, callbacks, object minus the
    corner / pillar sprites), placement kind wall requiresFloor false, pieceClass wall, own group.
  * garage trim = Newburbs "Door Frame - Garage Left/Center/Right": kind wall, object
    {isThumpable false, dismantable, isDoorFrame, canPassThrough}, pieceClass door, cost = the
    sheet's own door frame piece (no new prices).

Tile layout (identical on every standard sheet; flags checked per sheet at generation):
  roof slope W 30-47 + 96-98, 104-106, 112-114 / N 48-63, 70, 71 + 99-101, 107-109, 115-117.
  Pairs = what KBW shows when the piece is rotated W -> N (same height profile left to right),
  derived by slope_pairing.py from tikitown_walls_brick_01 and validated against the six
  confirmed Newburbs roof slope pairs; every sheet is re-checked for contradictions.
  garage trim (WallOverlay, CutawayHint DoubleDoorLeft / GarageDoorMiddle / DoubleDoorRight):
  W 64 / 65 / 66 with N 69 / 68 / 67 (same reversed N order as the confirmed Newburbs trims).

Not covered here (own layouts or no tile properties): the tents / Melos ruins / tterika sheets,
the vanilla_walls_add / siding wall fixtures (92-95 vents + electrical box, 102/103, 110/111,
118/119 meters; art only, no tile properties) and the siding posts (120-127).
"""
import copy, hashlib, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kbw_tilepatch as k
import tikitown_wall_overlays as two
import tikitown_naming_pass as tnp

DIR = r"c:\Users\josep\Kiro\zomboid\tikitown"
OUT_SLOPES = os.path.join(DIR, "41_tikitown_roof_slope_walls.json")
OUT_GARAGE = os.path.join(DIR, "42_tikitown_garage_trim.json")

SLOPE_PAIRS = [(30, 70), (31, 71), (32, 48), (33, 49), (34, 50), (35, 51), (36, 52), (37, 53),
               (38, 62), (39, 63), (40, 56), (41, 57), (42, 58), (43, 59), (44, 60), (45, 61),
               (46, 54), (47, 55),
               (96, 107), (97, 108), (98, 109), (104, 99), (105, 100), (106, 101),
               (112, 117), (113, 116), (114, 115)]
GARAGE = [("left", "Left", 64, 69), ("center", "Center", 65, 68), ("right", "Right", 66, 67)]
GARAGE_OBJ = {"isThumpable": False, "dismantable": True, "isDoorFrame": True, "canPassThrough": True}

# the 63 sheets with the standard slope + garage block (sheet_coverage.py); the 6 others differ
SHEETS = list(two.SHEETS)
assert len(SHEETS) == 63


def _faces(w, n):
    return {"W": {"layers": [{"rows": [[w]]}]}, "N": {"layers": [{"rows": [[n]]}]}}


def _sources():
    """sheet -> (primary wall buildable, door frame buildable) from the walls file."""
    d = json.load(open(two.WALLS, encoding="utf-8"))["buildables"]
    walls, frames = {}, {}
    for b in d:
        sh = tnp.sheet_of(b["id"])
        if b.get("pieceClass") == "wall" and sh not in walls and not b["id"].endswith(("_corner", "_pillar")):
            if "(" not in b.get("displayName", ""):
                walls[sh] = b
        if b.get("pieceClass") == "door" and "(Door Frame" in b.get("displayName", "") and sh not in frames:
            frames[sh] = b
    return walls, frames


def _check_flags(ts, sheet):
    """Every tile we use must carry the expected wall / overlay flags on this sheet."""
    t = ts[sheet.encode()][6]
    flags = lambda i: {a for a, _v in t[i]} if i < len(t) else set()
    bad = []
    for w, n in SLOPE_PAIRS:
        if b"WallW" not in flags(w) or b"WallN" not in flags(n):
            bad.append((w, n))
    for _s, _l, w, n in GARAGE:
        if b"WallOverlay" not in flags(w) or b"WallOverlay" not in flags(n):
            bad.append((w, n))
    return bad


def _check_pairing(sheet):
    """Re-run the shape matcher; any confident pair that contradicts SLOPE_PAIRS is an error."""
    import slope_pairing as sp
    canon = dict(SLOPE_PAIRS)
    ws = [w for w, _n in SLOPE_PAIRS]
    ns = [n for _w, n in SLOPE_PAIRS]
    got, _uw, _un = sp.pair(sheet, ws, ns, min_score=0.85)
    return [(w, n) for w, n, _s in got if canon.get(w) != n]


def _base(b, bid, key, name, sub, icon, pclass, group):
    return {
        "id": bid, "allowSpriteReuse": True, "translationKey": key, "displayName": name,
        "category": b.get("category", "Walls and Wall Finishes"), "subcategory": sub,
        "material": b.get("material", "Wood"), "iconSprite": icon,
        "placement": {"kind": "wall", "requiresFloor": False},
        "tags": ["tikitown", "drazion", "world-essentials"], "pieceClass": pclass, "group": group,
    }


def build():
    walls, frames = _sources()
    _v, ts, _o = k._parse(open(k._TIKITOWN_TILES, "rb").read())
    slopes, garage, problems = [], [], []
    for sh in SHEETS:
        wall = walls.get(sh)
        if not wall:
            problems.append("%s: no source wall" % sh); continue
        bad = _check_flags(ts, sh)
        if bad:
            problems.append("%s: tiles without the expected flags %s" % (sh, bad)); continue
        contra = _check_pairing(sh)
        if contra:
            problems.append("%s: shape matcher contradicts the slope pairs %s" % (sh, contra)); continue
        style = (wall.get("group") or {}).get("name") or wall["displayName"]   # "<Style> Wall"
        sub = wall.get("subcategory")
        st0 = wall["stages"][0]
        # ---- roof slope walls
        gid = "worldessentials.tikitown.roofslope.%s" % sh
        gname = "%s Roof Slope Walls" % style[:-len(" Wall")] if style.endswith(" Wall") else style + " Roof Slope Walls"
        gname = gname.replace(" Walls Walls", " Walls")
        for level, (w, n) in enumerate(SLOPE_PAIRS, 1):
            st = copy.deepcopy(st0)
            st["geometry"] = {"faces": _faces("%s_%d" % (sh, w), "%s_%d" % (sh, n))}
            obj = st.get("object") or {}
            for drop in ("cornerSprite", "pillarSprite", "cutSpritesW", "cutSpritesN"):
                obj.pop(drop, None)
            slug = "%s_%d" % (sh, w)
            nm = "%s Roof Slope Wall %d" % (style[:-len(" Wall")] if style.endswith(" Wall") else style, level)
            b = _base(wall, "worldessentials.tikitown.roofslope.%s" % slug, "IGUI_WETiki_roofslope_%s" % slug,
                      nm, sub, "%s_%d" % (sh, w), "wall",
                      {"id": gid, "name": gname, "translationKey": "IGUI_WETiki_roofslope_%s_group" % sh,
                       "level": level})
            if wall.get("tooltipKey"):
                b["tooltipKey"] = wall["tooltipKey"]
            b["stages"] = [st]
            slopes.append(b)
        # ---- garage door frame trims
        frame = frames.get(sh)
        if not frame:
            problems.append("%s: no door frame piece (garage trim skipped)" % sh)
            continue
        fst0 = frame["stages"][0]
        base_name = style[:-len(" Wall")] if style.endswith(" Wall") else style
        for level, (slug_s, label, w, n) in enumerate(GARAGE, 1):
            st = {"id": "built", "geometry": {"faces": _faces("%s_%d" % (sh, w), "%s_%d" % (sh, n))},
                  "requirements": copy.deepcopy(fst0.get("requirements") or {}),
                  "construction": copy.deepcopy(fst0.get("construction") or {}),
                  "object": dict(GARAGE_OBJ)}
            for hk in ("health", "skillBaseHealth"):
                if hk in fst0:
                    st[hk] = fst0[hk]
            slug = "%s_%s" % (sh, slug_s)
            b = _base(frame, "worldessentials.tikitown.garagetrim.%s" % slug, "IGUI_WETiki_garagetrim_%s" % slug,
                      "%s Garage Door Frame - %s" % (base_name, label), sub, "%s_%d" % (sh, w), "door",
                      {"id": "worldessentials.tikitown.garagetrim.%s" % sh,
                       "name": "%s Garage Door Frame" % base_name,
                       "translationKey": "IGUI_WETiki_garagetrim_%s_group" % sh, "level": level})
            b["stages"] = [st]
            garage.append(b)
    return slopes, garage, problems


def _write(path, buildables, source):
    ids = [b["id"] for b in buildables]
    assert len(ids) == len(set(ids)), "duplicate ids in " + path
    # md5(id) order: keeps KBW's Kahlua quicksort shallow (see tikitown_wall_overlays.main)
    buildables.sort(key=lambda b: hashlib.md5(b["id"].encode("utf-8")).hexdigest())
    json.dump({"schemaVersion": 1, "category": "Walls and Wall Finishes", "source": source,
               "buildables": buildables}, open(path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("wrote %s (%d buildables)" % (path, len(ids)))


def main():
    slopes, garage, problems = build()
    _write(OUT_SLOPES, slopes, "TikiTown wall sheets: roof slope / gable walls (tiles 30-71, 96-117), "
                               "modeled on the confirmed Newburbs roof slope walls. Cost = the sheet's wall.")
    _write(OUT_GARAGE, garage, "TikiTown wall sheets: garage door frame trim (tiles 64-69), modeled on the "
                               "confirmed Newburbs garage door frames. Cost = the sheet's door frame.")
    for p in problems:
        print("PROBLEM:", p)


if __name__ == "__main__":
    main()
