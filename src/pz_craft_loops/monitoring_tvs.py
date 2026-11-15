# -*- coding: utf-8 -*-
"""Working TV versions of vanilla's Monitoring Station ("Terminal", security_01_0..3, Facing S/E/N/W,
two angled screens) and Monitoring Bank ("Monitors", security_01_4 / 5, wall objects, Facing S / E,
four screens) (user, 2026-11-14).

Same machinery as the Future Wall Screen TV (kbw_tilepatch WALLTV): our copies in the Community
ice-shell tileset at FIXED indices whose +16 / +32 / +48 hold their own screen frames (vanilla's
screen layout: IsoTelevision.setupDefaultScreens adds the sprites at the TV's index +16/+32/+48,
and WE's KBWCommunity_TVScreens.lua table maps each TV to the same three).

Screens are found in the art, not measured by hand: the screen glass is a pale green-grey that
the casing (white / grey) and bezel (near black) never use. Each connected patch of it is one
screen; its quad is the smallest parallelogram along two of the isometric directions (slope +1/2,
-1/2 or vertical) that holds it. A vanilla TV screen frame (appliances_television_01, the series
of the Facing whose slant is closest) is affine-warped onto that quad and masked to the patch,
so it keeps the art's rounded corners and bezel.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kbw_tilepatch as k  # noqa: E402

SHEET = "security_01"
STATION = [0, 1, 2, 3]          # Facing S, E, N, W
BANK = [4, 5]                   # Facing S, E (wall objects)
_HERE = os.path.dirname(os.path.abspath(__file__))
_CACHE = os.path.join(_HERE, "_cache_mon")
_DIRS = {"down": (2.0, 1.0), "up": (2.0, -1.0), "vert": (0.0, 1.0)}


def art(i):
    """Vanilla art of security_01_<i> (128x256 RGBA)."""
    return _art(i)


def _art(i):
    from PIL import Image
    k._extract_from_pack(k._VANILLA_TILES2X_PACK, {"%s_%d" % (SHEET, j) for j in STATION + BANK}, _CACHE)
    return Image.open(os.path.join(_CACHE, "%s_%d.png" % (SHEET, i))).convert("RGBA")


def _screen_mask(im):
    """Boolean mask of screen-glass pixels (pale green-grey)."""
    import numpy as np
    a = np.asarray(im).astype(int)
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    return (al > 200) & (g >= r + 4) & (g >= b + 2) & (g > 70) & (g < 215) & (abs(r - b) < 40)


def _components(mask, min_px=12):
    """Connected patches (4-neighbour) of the mask, largest first: [list of (x, y)]."""
    import numpy as np
    h, w = mask.shape
    seen = np.zeros_like(mask)
    out = []
    for y in range(h):
        for x in range(w):
            if mask[y, x] and not seen[y, x]:
                stack, comp = [(x, y)], []
                seen[y, x] = True
                while stack:
                    cx, cy = stack.pop()
                    comp.append((cx, cy))
                    for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                        if 0 <= nx < w and 0 <= ny < h and mask[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True
                            stack.append((nx, ny))
                if len(comp) >= min_px:
                    out.append(comp)
    return sorted(out, key=len, reverse=True)


def _quad(comp):
    """Smallest parallelogram along two isometric directions holding the patch:
    ((tl), (tr), (bl)) in tile pixels, and the pair of directions used."""
    import itertools
    import numpy as np
    pts = np.array(comp, dtype=float) + 0.5
    best = None
    for (nu, u), (nv, v) in itertools.combinations(_DIRS.items(), 2):
        M = np.array([u, v]).T
        st = np.linalg.solve(M, pts.T).T             # p = s*u + t*v
        s0, s1 = st[:, 0].min() - 0.5 / np.hypot(*u), st[:, 0].max() + 0.5 / np.hypot(*u)
        t0, t1 = st[:, 1].min() - 0.5 / np.hypot(*v), st[:, 1].max() + 0.5 / np.hypot(*v)
        area = abs(np.linalg.det(M)) * (s1 - s0) * (t1 - t0)
        if best is None or area < best[0]:
            corners = [M @ np.array(c) for c in ((s0, t0), (s1, t0), (s0, t1), (s1, t1))]
            best = (area, corners, (nu, nv))
    _area, corners, dirs = best
    # visual orientation: the two leftmost corners are the left edge, the higher of each pair is top
    cs = sorted(corners, key=lambda c: (c[0], c[1]))
    left, right = sorted(cs[:2], key=lambda c: c[1]), sorted(cs[2:], key=lambda c: c[1])
    tl, bl, tr = left[0], left[1], right[0]
    return (tuple(tl), tuple(tr), tuple(bl)), dirs


def screens(i):
    """[(quad, mask image)] for every screen of security_01_<i>."""
    import numpy as np
    from PIL import Image
    im = _art(i)
    mask = _screen_mask(im)
    out = []
    for comp in _components(mask):
        m = np.zeros(mask.shape, dtype=np.uint8)
        for x, y in comp:
            m[y, x] = 255
        q, _dirs = _quad(comp)
        out.append((q, Image.fromarray(m, "L")))
    return out


def screen_frames(i):
    """The three screen overlay tiles (128x256 RGBA) for security_01_<i>: every screen warped from
    vanilla's screen frame k of the series whose slant matches (S series for screens leaning down to
    the right, E series otherwise)."""
    from PIL import Image
    k._extract_vanilla_screens()
    frames = [Image.new("RGBA", (128, 256), (0, 0, 0, 0)) for _ in range(3)]
    for quad, m in screens(i):
        (x0, y0), (x1, y1), _bl = quad
        facing = "S" if y1 >= y0 else "E"
        idxs, src = k._VANILLA_SCREENS[facing]
        coeffs = k._affine_inverse(src, quad)
        for f, vi in enumerate(idxs):
            sim = Image.open(os.path.join(k._SCREEN_CACHE, "appliances_television_01_%d.png" % vi)).convert("RGBA")
            w = sim.transform((128, 256), Image.AFFINE, coeffs, resample=Image.BILINEAR)
            a = w.split()[3]
            from PIL import ImageChops
            w.putalpha(ImageChops.multiply(a, m))
            frames[f].alpha_composite(w)
    return frames


def preview(path):
    from PIL import Image, ImageDraw
    ids = STATION + BANK
    sheet = Image.new("RGBA", (128 * len(ids), 256 * 4), (60, 60, 60, 255))
    d = ImageDraw.Draw(sheet)
    for n, i in enumerate(ids):
        base = _art(i)
        sheet.alpha_composite(base, (n * 128, 0))
        for f, fr in enumerate(screen_frames(i)):
            im = base.copy()
            im.alpha_composite(fr)
            sheet.alpha_composite(im, (n * 128, 256 * (f + 1)))
        for quad, _m in screens(i):
            tl, tr, bl = quad
            br = (tr[0] + bl[0] - tl[0], tr[1] + bl[1] - tl[1])
            d.line([tl, tr, br, bl, tl], fill=(255, 0, 255, 255))
        d.text((n * 128 + 4, 4), "%s_%d: %d screens" % (SHEET, i, len(screens(i))), fill=(255, 255, 0, 255))
    sheet.save(path)


# ------------------------------------------------------------------------------------ definitions
OUT = r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables\69_community_monitoring_tvs.json"
# KBW face = the opposite of the tile's Facing (Oak cabinet rule; a wall piece hangs on that wall)
_FACE_OF = {"S": "N", "E": "W", "N": "S", "W": "E"}
_KNOWLEDGE = {"recipes": ["KBWKnowledge_PopularMechanics_HomeAppliances"], "hideUntilLearned": True,
              "needToBeLearned": True,
              "sources": [{"type": "magazine", "item": "KnoxBuildworks.PopularMechanics_HomeAppliances"}],
              "skillAlternatives": [{"mode": "all", "skills": {"Electricity": 4}}]}


def _req(scrap, wire, sheets, small, skill):
    """The Dylan CRT TV's recipe (file 53, a working TV) scaled per screen, plus the casing metal."""
    inputs = [{"id": "tool_screwdriver", "role": "tool", "mode": "keep", "resourceType": "Item",
               "tags": ["base:screwdriver"], "amount": 1}]
    n = 1
    for item, amount in (("Base.ElectronicsScrap", scrap), ("Base.ElectricWire", wire),
                         ("Base.SheetMetal", sheets), ("Base.SmallSheetMetal", small), ("Base.Screws", 4)):
        if amount:
            inputs.append({"id": "source_material_%d" % n, "role": "material", "mode": "consume",
                           "resourceType": "Item", "items": [item], "amount": amount})
            n += 1
    import copy as _c
    return {"inputs": inputs, "skills": {"Electricity": skill}, "knowledge": _c.deepcopy(_KNOWLEDGE)}


def _one(s):
    return {"layers": [{"rows": [[s]]}]}


def build_document():
    facing = lambda i: dict((a.decode(), b.decode()) for a, b in k._vanilla_props(SHEET, i)).get("Facing")
    con = {"time": 200, "timedAction": "BuildWallMetal", "completionSound": "BuildMetalStructureMedium",
           "xp": {"Electricity": 40}, "category": "Electrical"}
    out = [
        {"id": "community.kbwcb.monitoring_station", "allowSpriteReuse": True,
         "translationKey": "IGUI_community_kbwcb_monitoring_station", "displayName": "Monitoring Station",
         "category": "Appliances", "subcategory": "Radios & TVs", "material": "Metal", "materialTags": ["Metal"],
         "iconSprite": k.mon_tv_name(0), "placement": {"kind": "object", "requiresFloor": True},
         "tags": ["community-tilepack", "kbwcb", "television", "vanilla-tiles"],
         "construction": dict(con),
         "stages": [{"id": "built",
                     "geometry": {"faces": {_FACE_OF[facing(i)]: _one(k.mon_tv_name(i)) for i in STATION}},
                     # two screens: twice the CRT's electronics, plus the desk casing
                     "requirements": _req(12, 4, 2, 2, 3),
                     # as the confirmed working CRT TVs (file 53); the desk's solidtrans still blocks
                     "object": {"isProp": True, "dismantable": True, "blockAllSquare": False},
                     "nativeObject": {"type": "television"}}]},
        {"id": "community.kbwcb.monitoring_bank", "allowSpriteReuse": True,
         "translationKey": "IGUI_community_kbwcb_monitoring_bank", "displayName": "Monitoring Bank",
         "category": "Appliances", "subcategory": "Radios & TVs", "material": "Metal", "materialTags": ["Metal"],
         "iconSprite": k.mon_tv_name(4),
         "placement": {"kind": "object", "requiresFloor": True, "needToBeAgainstWall": True},
         "tags": ["community-tilepack", "kbwcb", "television", "vanilla-tiles"],
         "construction": dict(con, time=300),
         "stages": [{"id": "built",
                     "geometry": {"faces": {_FACE_OF[facing(i)]: _one(k.mon_tv_name(i)) for i in BANK}},
                     # four screens: four CRTs' electronics, plus the wall rack
                     "requirements": _req(24, 8, 2, 4, 4),
                     "object": {"isProp": True, "dismantable": True, "blockAllSquare": False,
                                "canPassThrough": True},
                     "nativeObject": {"type": "television"}}]},
    ]
    return {"schemaVersion": 1, "category": "Appliances",
            "source": ("Vanilla security_01 Monitoring Station (Terminal, 0-3) and Monitoring Bank (Monitors, "
                       "4-5) as working TVs, on our copies KBWCommunityIceShell_264..269 with generated screen "
                       "frames at +16/+32/+48. Generated by pz_craft_loops/monitoring_tvs.py."),
            "buildables": out}


def main():
    import json
    doc = build_document()
    json.dump(doc, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("wrote %s (%d buildables)" % (OUT, len(doc["buildables"])))


if __name__ == "__main__":
    for i in STATION + BANK:
        print(i, [[tuple(round(c, 1) for c in p) for p in q] for q, _m in screens(i)])
    preview(os.path.join(_HERE, "_mon_tv_preview.png"))
    main()
