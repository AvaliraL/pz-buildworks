# -*- coding: utf-8 -*-
"""Static bug pass over the INSTALLED World Essentials copy of our work (read-only):
  * World Essentials - Community Buildworks   (id KnoxCommunityTilepack)
  * World Essentials - TikiTown Buildworks    (id TikiTownKBW)
  * the WE base / Knox Expansion files that came from our work
Writes zomboid/WE_submods/BUG_PASS_<date>.md. Never modifies WE.

Checks
  A  structure: JSON parses, manifest <-> files, duplicate ids, duplicate aliases, alias == real id
  B  sprites: every referenced sprite has a tile definition AND a texture (any loaded mod / vanilla)
  C  tile roles: W/N faces, corner and pillar sprites match the tile's own flags
  D  translations: translationKey / tooltipKey / group keys exist; shared tooltip text sanity
  E  containers: definition capacity vs the tile's ContainerCapacity (tooltip mismatch)
  F  sprite reuse: same sprite used by several buildables without allowSpriteReuse
  G  tiledef numbers: collisions across every installed mod
  H  Lua: Kahlua-unsafe constructs; sprite names referenced in Lua that don't exist
"""
import os, re, json, glob, struct, collections, datetime, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kbw_tilepatch as k

WS = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600"
GAME = r"C:\Program Files (x86)\Steam\steamapps\common\ProjectZomboid"
WE = WS + r"\3733324672\mods"
SUBS = {"Community": WE + r"\World Essentials - Community Buildworks",
        "TikiTown": WE + r"\World Essentials - TikiTown Buildworks"}
# mods whose tiles/textures our content can legitimately use
TILE_MODS = [WS + r"\3046728955", WS + r"\3628736763", WE, GAME + r"\media"]
REPORT = r"c:\Users\josep\Kiro\zomboid\WE_submods\BUG_PASS_%s.md" % datetime.date.today().isoformat()

R = collections.OrderedDict((k_, []) for k_ in "ABCDEFGH")
def add(sec, sev, msg): R[sec].append((sev, msg))

# ---------------------------------------------------------------- load tiles + texture names
tiles = {}          # tileset -> (ntiles, props list)
for root in TILE_MODS:
    for p in glob.glob(os.path.join(root, "**", "*.tiles"), recursive=True):
        try: _, ts, _ = k._parse(open(p, "rb").read())
        except Exception: continue
        for n, t in ts.items():
            name = n.decode()
            if name not in tiles or t[5] > tiles[name][0]:
                tiles[name] = (t[5], t[6])
tex = set()
def pack_names(p):
    with open(p, "rb") as f:
        def i32(): return struct.unpack("<i", f.read(4))[0]
        def s(): return f.read(i32()).decode("utf-8", "replace")
        if f.read(4) != b"PZPK": return None
        ver = i32()
        for _ in range(i32()):
            s(); n = i32(); i32()
            for _e in range(n):
                tex.add(s()); f.read(32)
            if ver >= 1: f.seek(i32(), 1)
            else: return None
    return True
skipped_packs = []
for root in TILE_MODS:
    for p in glob.glob(os.path.join(root, "**", "*.pack"), recursive=True):
        try:
            if pack_names(p) is None: skipped_packs.append(p)
        except Exception:
            skipped_packs.append(p)
def tile_of(spr):
    m = re.match(r"(.+)_(\d+)$", spr or "")
    if not m: return None, None
    return m.group(1), int(m.group(2))
def props(spr):
    ts, i = tile_of(spr)
    if ts not in tiles: return None
    n, pl = tiles[ts]
    if i >= n: return "OOR"
    return {a.decode(): b.decode() for a, b in pl[i]}

# ---------------------------------------------------------------- load definitions
defs = {}   # (sub, file) -> buildables
for sub, root in SUBS.items():
    mpath = os.path.join(root, "42", "media", "KnoxBuildworks", "manifest.json")
    try:
        man = [os.path.basename(x) for x in json.load(open(mpath, encoding="utf-8"))["definitions"]]
    except Exception as e:
        add("A", "ERROR", "%s: manifest unreadable: %r" % (sub, e)); man = []
    ddir = os.path.join(root, "42", "media", "KnoxBuildworks", "definitions")
    present = sorted(os.path.basename(x) for x in glob.glob(os.path.join(ddir, "*.json")))
    for f in man:
        if f not in present: add("A", "ERROR", "%s: manifest lists missing file %s" % (sub, f))
    for f in present:
        if f not in man: add("A", "WARN", "%s: %s is on disk but not in the manifest (never loads)" % (sub, f))
        try:
            defs[(sub, f)] = json.load(open(os.path.join(ddir, f), encoding="utf-8")).get("buildables", [])
        except Exception as e:
            add("A", "ERROR", "%s/%s: JSON error %r" % (sub, f, e))

ids, aliases = collections.Counter(), collections.defaultdict(list)
for (sub, f), bl in defs.items():
    for b in bl:
        ids[b.get("id")] += 1
        for a in b.get("aliases") or []: aliases[a].append(b.get("id"))
for i, n in ids.items():
    if n > 1: add("A", "ERROR", "duplicate buildable id %s (x%d)" % (i, n))
for a, owners in aliases.items():
    if len(owners) > 1: add("A", "ERROR", "alias %s claimed by %s" % (a, owners))
    if a in ids: add("A", "ERROR", "alias %s equals a real id" % a)

# ---------------------------------------------------------------- per-buildable checks
def sprites_of(b):
    out = []
    def walk(o, path):
        if isinstance(o, dict):
            for kk, v in o.items(): walk(v, path + [kk])
        elif isinstance(o, list):
            for v in o: walk(v, path)
        elif isinstance(o, str) and re.match(r"^[A-Za-z][\w]*_\d+$", o) and "." not in o:
            if any(x in path for x in ("rows", "iconSprite", "cornerSprite", "pillarSprite", "cutSpritesW",
                                       "cutSpritesN", "sprites", "openSprites", "openSprite", "sprite",
                                       "frameSprite", "overlay", "overlaySprite")) or path[-1:] == ["iconSprite"]:
                out.append(o)
    walk(b, [])
    return out
WFL = {"WallW", "WindowW", "DoorWallW", "WallWTrans", "HoppableW", "TallHoppableW"}
NFL = {"WallN", "WindowN", "DoorWallN", "WallNTrans", "HoppableN", "TallHoppableN"}
sprite_users = collections.defaultdict(set)
tr = {}
for sub, root in SUBS.items():
    for f in ("IG_UI.json", "Tooltip.json"):
        p = os.path.join(root, "42", "media", "lua", "shared", "Translate", "EN", f)
        if os.path.isfile(p):
            try: tr.update(json.load(open(p, encoding="utf-8")))
            except Exception as e: add("D", "ERROR", "%s %s unreadable: %r" % (sub, f, e))
for p in glob.glob(WE + r"\World Essentials*\42\media\lua\shared\Translate\EN\*.json"):
    try: tr.update({kk: v for kk, v in json.load(open(p, encoding="utf-8")).items() if kk not in tr})
    except Exception: pass
kbw_tr = {}
for p in glob.glob(WS + r"\3772269882\**\Translate\EN\*.json", recursive=True):
    try: kbw_tr.update(json.load(open(p, encoding="utf-8")))
    except Exception: pass

missing_sprite = collections.Counter()
for (sub, f), bl in defs.items():
    for b in bl:
        bid = b.get("id")
        # B: sprite existence
        geo = set()
        for st in b.get("stages", []):
            for fv in ((st.get("geometry") or {}).get("faces", {}) or {}).values():
                geo |= {x for L in fv.get("layers", []) for r in L.get("rows", []) for x in r if isinstance(x, str)}
        for spr in geo:   # only placed geometry; shared corner/pillar refs are intended
            sprite_users[spr].add((bid, bool(b.get("allowSpriteReuse"))))
        for spr in set(sprites_of(b)):
            ts, i = tile_of(spr)
            pr = props(spr)
            if pr is None and spr not in tex:
                missing_sprite[(sub, f)] += 1
                if missing_sprite[(sub, f)] <= 8:
                    add("B", "ERROR", "%s/%s %s: sprite %s has no tile definition or texture" % (sub, f, bid, spr))
            elif pr == "OOR":
                add("B", "ERROR", "%s/%s %s: sprite %s index past end of sheet" % (sub, f, bid, spr))
            elif spr not in tex:
                add("B", "WARN", "%s/%s %s: sprite %s has a tile but no texture found in scanned packs" % (sub, f, bid, spr))
        # C: tile roles
        cls = b.get("pieceClass")
        for st in b.get("stages", []):
            faces = (st.get("geometry") or {}).get("faces", {})
            for face, fv in faces.items():
                sp = [x for L in fv.get("layers", []) for r in L.get("rows", []) for x in r if isinstance(x, str)]
                if len(sp) != 1 or cls in ("corner", "pillar"): continue
                pr = props(sp[0])
                if not isinstance(pr, dict): continue
                w, n = bool(set(pr) & WFL), bool(set(pr) & NFL)
                if w == n: continue
                if (face in ("W", "E") and n) or (face in ("N", "S") and w):
                    add("C", "ERROR", "%s/%s %s: face %s uses %s (%s)" % (sub, f, bid, face, sp[0], "N-flag" if n else "W-flag"))
            o = st.get("object", {})
            for key, want in (("cornerSprite", "WallNW"), ("pillarSprite", "WallSE")):
                if o.get(key):
                    pr = props(o[key])
                    both_dirs = bool(set(pr) & WFL) and bool(set(pr) & NFL) if isinstance(pr, dict) else False
                    if key == "cornerSprite" and both_dirs:
                        pass   # a corner post of a hoppable/low wall carries both N and W flags: correct
                    elif isinstance(pr, dict) and pr and want not in pr and (set(pr) & (WFL | NFL | {"WallNW", "WallSE"})):
                        add("C", "ERROR", "%s/%s %s: %s %s is a %s tile" % (sub, f, bid, key, o[key],
                            ",".join(sorted(set(pr) & (WFL | NFL | {"WallNW", "WallSE"})))))
            # E: container capacity vs tile
            c = st.get("container")
            if isinstance(c, dict) and c.get("capacity") is not None:
                for face, fv in faces.items():
                    sp = [x for L in fv.get("layers", []) for r in L.get("rows", []) for x in r if isinstance(x, str)]
                    if not sp: continue
                    pr = props(sp[0])
                    if isinstance(pr, dict) and pr.get("ContainerCapacity") and str(c["capacity"]) != pr["ContainerCapacity"]:
                        add("E", "WARN", "%s/%s %s: defines capacity %s but tile %s says %s (tooltip shows the tile)" % (
                            sub, f, bid, c["capacity"], sp[0], pr["ContainerCapacity"]))
                        break
        # D: translations
        for key in ("translationKey", "tooltipKey"):
            v = b.get(key)
            if v and v not in tr and v not in kbw_tr:
                add("D", "WARN", "%s/%s %s: %s %s missing" % (sub, f, bid, key, v))
        g = b.get("group") or {}
        if g.get("translationKey") and g["translationKey"] not in tr and g["translationKey"] not in kbw_tr:
            add("D", "WARN", "%s/%s %s: group key %s missing" % (sub, f, bid, g["translationKey"]))
for (sub, f), n in missing_sprite.items():
    if n > 8: add("B", "ERROR", "%s/%s: %d more missing sprites (first 8 listed)" % (sub, f, n - 8))
# D: shared tooltip keys overriding KBW / holding a single piece's name
for key in ("Tooltip_KBW_Shared_StorageFixture", "Tooltip_KBW_DecorativeWallFixture"):
    for sub, root in SUBS.items():
        p = os.path.join(root, "42", "media", "lua", "shared", "Translate", "EN", "Tooltip.json")
        if os.path.isfile(p):
            d = json.load(open(p, encoding="utf-8"))
            if key in d and key in kbw_tr and d[key] != kbw_tr[key]:
                add("D", "ERROR", "%s overrides KBW core key %s: %r (KBW: %r)" % (sub, key, d[key], kbw_tr[key]))
for sub, root in SUBS.items():
    p = os.path.join(root, "42", "media", "lua", "shared", "Translate", "EN", "Tooltip.json")
    if os.path.isfile(p):
        for kk, v in json.load(open(p, encoding="utf-8")).items():
            if kk.startswith("Tooltip_KBW_Shared_") and kk not in kbw_tr:
                add("D", "WARN", "%s shared tooltip %s = %r (one piece's name shown on every piece using it)" % (sub, kk, v))

# F: sprite reuse
for spr, users in sprite_users.items():
    ids_ = {u for u, _ in users}
    if len(ids_) > 1 and not all(a for _, a in users):
        add("F", "WARN", "sprite %s used by %d buildables without allowSpriteReuse on all: %s" % (spr, len(ids_), sorted(ids_)[:4]))

# G: tiledef collisions across all installed mods
td = collections.defaultdict(set)
for p in glob.glob(os.path.join(WS, "**", "mod.info"), recursive=True):
    t = open(p, encoding="utf-8", errors="replace").read()
    mid = ([l.split("=", 1)[1].strip() for l in t.splitlines() if l.startswith("id=")] or ["?"])[0]
    for l in t.splitlines():
        m = re.match(r"\s*tiledef\s*=\s*(\S+)\s+(\d+)", l)
        if m: td[int(m.group(2))].add((mid, m.group(1)))
ours_nums = set()
for sub, root in SUBS.items():
    for l in open(os.path.join(root, "42", "mod.info"), encoding="utf-8").read().splitlines():
        m = re.match(r"\s*tiledef\s*=\s*(\S+)\s+(\d+)", l)
        if m: ours_nums.add(int(m.group(2)))
for n in sorted(ours_nums):
    users = {u for u in td[n]}
    files = {f for _, f in users}
    if len(files) > 1:
        add("G", "ERROR", "tiledef %d used by different files: %s" % (n, sorted(users)))
for n, users in sorted(td.items()):
    files = {f for _, f in users}; mods = {m for m, _ in users}
    if len(mods) > 1 and n in (6985, 830, 7001):
        add("G", "WARN", "tiledef %d (%s) registered by several mods: %s (different layouts can shift tile numbers)" % (
            n, ",".join(sorted(files)), sorted(mods)))

# H: Lua
lua_files = glob.glob(os.path.join(SUBS["Community"], "**", "*.lua"), recursive=True) + \
            glob.glob(os.path.join(SUBS["TikiTown"], "**", "*.lua"), recursive=True) + \
            [p for p in glob.glob(WE + r"\World Essentials\42\media\lua\**\*.lua", recursive=True)
             if re.search(r"KBWCommunity|WorldEssentialsCommunity|ReadIcons", os.path.basename(p))] + \
            glob.glob(WE + r"\World Essentials - Knox Buildworks Expansion\42\media\lua\shared\WorldEssentialsKnoxTikitown.lua")
BAD = [(r"\bnext\s*\(", "next() is not available in Kahlua"), (r"\bgoto\b", "goto (Lua 5.2+)"),
       (r"[^-/]//[^/]", "integer division // (Lua 5.3)"), (r"\bdebug\.", "debug library")]
for p in lua_files:
    raw = open(p, encoding="utf-8", errors="replace").read()
    code = "\n".join(l.split("--", 1)[0] for l in raw.split("\n"))
    code = re.sub(r'"[^"\n]*"|\'[^\'\n]*\'', '""', code)
    for pat, why in BAD:
        for m in re.finditer(pat, code):
            line = code[:m.start()].count("\n") + 1
            add("H", "ERROR", "%s:%d %s" % (p[len(WE):], line, why))
    for spr in set(re.findall(r'"([A-Za-z]\w*_\d+)"', raw)):
        if spr in tiles: continue   # a tileset name (e.g. furniture_bedding_01), not a sprite
        if props(spr) is None and spr not in tex and not spr.startswith(("IGUI", "Tooltip", "UI_")):
            add("H", "WARN", "%s references sprite %s which has no tile/texture" % (p[len(WE):], spr))

# ---------------------------------------------------------------- report
lines = ["# World Essentials bug pass (our submods)", "",
         "Generated %s by `pz_craft_loops/we_bug_pass.py` against the installed Steam copy (read-only)." % datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
         "", "Scanned: %d buildables in %d files; %d tilesets; %d texture names; %d Lua files." % (
             sum(len(v) for v in defs.values()), len(defs), len(tiles), len(tex), len(lua_files)), ""]
if skipped_packs:
    lines.append("Texture packs not indexed (old format): %d. Sprites only in those show as 'no texture' warnings." % len(skipped_packs))
TITLES = {"A": "Structure", "B": "Sprites exist", "C": "Tile roles (faces, corners, pillars)", "D": "Translations",
          "E": "Container capacity vs tile", "F": "Sprite reuse", "G": "Tiledef numbers", "H": "Lua"}
summary = []
for sec, items in R.items():
    e = sum(1 for s, _ in items if s == "ERROR"); w = len(items) - e
    summary.append("| %s %s | %d | %d |" % (sec, TITLES[sec], e, w))
lines += ["| Check | Errors | Warnings |", "|---|---:|---:|"] + summary + [""]
for sec, items in R.items():
    lines.append("## %s. %s" % (sec, TITLES[sec]))
    if not items: lines.append("No issues found."); lines.append(""); continue
    for s, m in items[:120]:
        lines.append("- **%s** %s" % (s, m))
    if len(items) > 120: lines.append("- ... %d more" % (len(items) - 120))
    lines.append("")
open(REPORT, "w", encoding="utf-8").write("\n".join(lines))
print(REPORT)
