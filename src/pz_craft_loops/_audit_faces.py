"""Audit every buildable we generated: does each face / corner / pillar sprite land on a tile whose
own flags match its role? Uses the real tile definitions (Drazion's tilepack, Community Tilepack,
vanilla). Faces: W -> W-flag, N -> N-flag (E/S faces use the W/N tiles in KBW wall convention, so
they're checked the same way). Only tiles that carry a directional wall/window/door flag are judged;
furniture etc. without those flags is skipped."""
import sys, os, glob, json, re, collections
sys.path.insert(0, r"c:\Users\josep\Kiro\pz_craft_loops")
import kbw_tilepatch as k
WS = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600"
tiles = {}
for p in glob.glob(os.path.join(WS, "**", "*.tiles"), recursive=True) + \
         [r"C:\Program Files (x86)\Steam\steamapps\common\ProjectZomboid\media\newtiledefinitions.tiles"]:
    try: _, ts, _ = k._parse(open(p, "rb").read())
    except Exception: continue
    for n, t in ts.items(): tiles.setdefault(n.decode(), t)
WFL = {"WallW", "WindowW", "DoorWallW", "WallWTrans", "HoppableW", "TallHoppableW", "attachedW", "collideW", "doorW"}
NFL = {"WallN", "WindowN", "DoorWallN", "WallNTrans", "HoppableN", "TallHoppableN", "attachedN", "collideN", "doorN"}
def fl(spr):
    m = re.match(r"(.+)_(\d+)$", spr or "")
    if not m or m.group(1) not in tiles: return None
    t = tiles[m.group(1)]; i = int(m.group(2))
    if i >= t[5]: return "OUT_OF_RANGE"
    return {a.decode() for a, _ in t[6][i]}
FILES = sorted(glob.glob(r"c:\Users\josep\Kiro\zomboid\tikitown\2[2-9]_*accurate.json") +
               glob.glob(r"c:\Users\josep\Kiro\zomboid\tikitown\3[0-4]_*accurate.json") +
               [f for f in glob.glob(r"c:\Users\josep\Kiro\zomboid\tikitown\[23][0-9]_tikitown_*.json")
                if "accurate" not in f and "TEST" not in f and "before" not in f
                and not os.path.exists(f.replace(".json", "_accurate.json"))] +
               [r"c:\Users\josep\Kiro\zomboid\tikitown\21_tikitown_walls_accurate.json"] +
               glob.glob(r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables\*.json"))
out = []
grand = collections.Counter()
for f in FILES:
    try: bl = json.load(open(f, encoding="utf-8")).get("buildables", [])
    except Exception: continue
    c = collections.Counter(); bad = []
    for b in bl:
        cls = b.get("pieceClass")
        for st in b.get("stages", []):
            faces = (st.get("geometry") or {}).get("faces", {})
            for face, rows in faces.items():
                sprites = [x for L in rows.get("layers", []) for r in L.get("rows", []) for x in r if isinstance(x, str)]
                if len(sprites) != 1 or cls in ("corner", "pillar"): continue
                g = fl(sprites[0])
                if g is None: c["unknown sheet"] += 1; continue
                if g == "OUT_OF_RANGE": c["OUT OF RANGE"] += 1; bad.append((b["id"], face, sprites[0], "index past end of sheet")); continue
                has_w, has_n = bool(g & WFL), bool(g & NFL)
                if not has_w and not has_n: c["no dir flags (skip)"] += 1; continue
                want_w = face in ("W", "E")
                if (want_w and has_w and not has_n) or (not want_w and has_n and not has_w): c["ok"] += 1
                elif has_w and has_n: c["both flags (skip)"] += 1
                else: c["WRONG"] += 1; bad.append((b["id"], face, sprites[0], ",".join(sorted(g & (WFL | NFL)))))
            o = st.get("object", {})
            for key, want in (("cornerSprite", "WallNW"), ("pillarSprite", "WallSE")):
                if o.get(key):
                    g = fl(o[key])
                    if g is None: c["unknown sheet"] += 1
                    elif g == "OUT_OF_RANGE" or want not in g:
                        c["%s WRONG" % key] += 1; bad.append((b["id"], key, o[key], "expected " + want))
                    else: c["%s ok" % key] += 1
    grand.update(c)
    flag = "  <-- CHECK" if any("WRONG" in kk or "OUT" in kk for kk in c) else ""
    out.append("%-55s %s%s" % (os.path.basename(f), dict(c), flag))
    for x in bad[:12]: out.append("      %s  face=%s  %s  (%s)" % x)
    if len(bad) > 12: out.append("      ... %d more" % (len(bad) - 12))
out.append("\nTOTAL: %s" % dict(grand))
open(r"c:\Users\josep\Kiro\pz_craft_loops\_audit_faces.txt", "w", encoding="utf-8").write("\n".join(out))
