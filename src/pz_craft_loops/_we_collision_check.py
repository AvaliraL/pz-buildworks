"""Read-only: check our work/ additions against the WHOLE installed World Essentials (all submods),
not just the files we track. Looks for: tiledef/pack id clashes, duplicate item/recipe names,
same-path file shadowing, duplicate translation keys, KBW definition id clashes."""
import os, re, json, glob

WE = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600\3733324672\mods"
WORK = r"c:\Users\josep\Kiro\zomboid\WE_submods\work"
UP = r"c:\Users\josep\Kiro\zomboid\WE_submods\upstream"
WORKSHOP = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600"
OUT = r"c:\Users\josep\Kiro\pz_craft_loops\_we_collision.txt"
MAP = {"World Essentials (base, our files only)": "World Essentials",
       "World Essentials - Knox Buildworks Expansion (our files only)": "World Essentials - Knox Buildworks Expansion"}
lines = []
p = lines.append


def walk(root):
    for d, _, fs in os.walk(root):
        for f in fs:
            yield os.path.join(d, f)


def rd(path):
    try:
        return open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return ""


# ---- 1. files we add that already exist in Steam WE (we would overwrite/shadow WE's own file)
p("== 1. our ADDED files that already exist in the installed WE")
ours_added = []
for top in os.listdir(WORK):
    for f in walk(os.path.join(WORK, top)):
        rel = os.path.relpath(f, os.path.join(WORK, top))
        if os.path.isfile(os.path.join(UP, top, rel)):
            continue
        ours_added.append((top, rel, f))
        steam = os.path.join(WE, MAP.get(top, top), rel)
        if os.path.isfile(steam):
            p("   CLASH  %s\\%s" % (top, rel))
# same filename anywhere else in WE lua (Lua require/load is by path under media/lua/<side>/)
p("   (checked %d added files)" % len(ours_added))
p("== 1b. added Lua whose media/lua-relative path exists in ANOTHER WE submod (load-order shadowing)")
for top, rel, f in ours_added:
    if not rel.endswith(".lua"):
        continue
    m = re.search(r"media\\lua\\(.*)$", rel)
    if not m:
        continue
    for sm in os.listdir(WE):
        for v in ("", "42"):
            q = os.path.join(WE, sm, v, "media", "lua", m.group(1))
            if os.path.isfile(q) and sm != MAP.get(top, top):
                p("   SHADOW %s  also in %s" % (m.group(1), sm))

# ---- 2. tiledef ids / pack names across all installed workshop mods
p("== 2. tiledef numbers / pack names")
ours_td = {}
for f in glob.glob(os.path.join(WORK, "*", "42", "mod.info")):
    for m in re.finditer(r"^tiledef\s*=\s*(\S+)\s+(\d+)", rd(f), re.M):
        ours_td[m.group(2)] = m.group(1)
for n, name in (("8179", "kbwtikitown_walloverlays"), ("8178", "kbwcommunity_lcouch"),
                ("8180", "kbwtikitown_tterika.patch"), ("8181", "kbwcommunity_iceshell")):
    ours_td.setdefault(n, name)
seen = {}
for f in glob.glob(os.path.join(WORKSHOP, "*", "mods", "*", "**", "mod.info"), recursive=True):
    for m in re.finditer(r"^tiledef\s*=\s*(\S+)\s+(\d+)", rd(f), re.M):
        seen.setdefault(m.group(2), set()).add("%s (%s)" % (m.group(1), os.path.relpath(f, WORKSHOP).split(os.sep)[0] + "/" + os.path.relpath(f, WORKSHOP).split(os.sep)[2]))
for n, name in sorted(ours_td.items()):
    others = sorted(x for x in seen.get(n, ()) if not x.startswith(name + " "))
    p("   %s %-28s %s" % (n, name, ("CLASH with " + "; ".join(others)) if others else "free"))
packs = {}
for f in glob.glob(os.path.join(WORKSHOP, "*", "mods", "*", "**", "*.pack"), recursive=True):
    packs.setdefault(os.path.basename(f).lower(), []).append(os.path.relpath(f, WORKSHOP).split(os.sep)[0])
for pk in ("kbwtikitownwalloverlays.pack", "kbwcommunitylcouch.pack", "kbwcommunityiceshell.pack"):
    p("   pack %-30s installed in workshop items: %s" % (pk, sorted(set(packs.get(pk, []))) or "none (only ours)"))

# ---- 3. item / recipe / fixing names in our scripts vs every WE script
p("== 3. script names (items / craftRecipes) defined by us AND by installed WE")
NAME = re.compile(r"^\s*(item|craftRecipe|recipe|fixing|model|sound)\s+([A-Za-z0-9_.]+)", re.M)
MODULE = re.compile(r"^\s*module\s+([A-Za-z0-9_]+)", re.M)


def script_names(path):
    t = rd(path)
    mods = MODULE.findall(t) or ["Base"]
    return {(k, mods[0] + "." + n) for k, n in NAME.findall(t)}


ours = {}
for top, rel, f in ours_added:
    if f.endswith(".txt") and "\\scripts\\" in f:
        for k in script_names(f):
            ours[k] = rel
weall = {}
for f in walk(WE):
    if f.endswith(".txt") and "\\scripts\\" in f:
        for k in script_names(f):
            weall.setdefault(k, []).append(os.path.relpath(f, WE))
p("   our script names: %d" % len(ours))
for k, rel in sorted(ours.items()):
    if k in weall:
        p("   DUP %s %s  ours=%s  WE=%s" % (k[0], k[1], rel, weall[k]))
# looser: same bare name in any module
bare = {}
for (kind, full), fl in weall.items():
    bare.setdefault((kind, full.split(".", 1)[1]), []).extend(fl)
for (kind, full), rel in sorted(ours.items()):
    b = (kind, full.split(".", 1)[1])
    if b in bare and (kind, full) not in weall:
        p("   SAME-NAME other module %s %s  WE=%s" % (kind, full, bare[b][:3]))
# spray paint / generator items referenced by us must exist somewhere
p("== 3b. items referenced by our recipes/distribution that are not defined by us or WE or vanilla-looking")
refs = set()
for top, rel, f in ours_added:
    if f.endswith((".txt", ".lua")):
        refs |= set(re.findall(r"\b((?:Base|WorldEssentials|TikiTownKBW|KnoxBuildworks|KBW)\.[A-Za-z0-9_]+)", rd(f)))
defined = {n for (_, n) in weall} | {n for (_, n) in ours}
missing = sorted(r for r in refs if not r.startswith("Base.") and r not in defined)
p("   non-Base refs not defined in WE or ours: %s" % (missing or "none"))

# ---- 4. translation keys we add that WE also defines (any submod)
p("== 4. translation keys we add/change that WE defines elsewhere")


def tkeys(path):
    t = rd(path)
    try:
        return set(json.loads(t).keys())
    except Exception:
        return set(re.findall(r"^\s*([A-Za-z0-9_]+)\s*=", t, re.M))


we_keys = {}
for f in walk(WE):
    if "\\Translate\\EN\\" in f:
        for k in tkeys(f):
            we_keys.setdefault(k, set()).add(os.path.relpath(f, WE).split(os.sep)[0])
cnt = 0
for top in os.listdir(WORK):
    for f in walk(os.path.join(WORK, top)):
        if "\\Translate\\EN\\" not in f:
            continue
        rel = os.path.relpath(f, os.path.join(WORK, top))
        upk = tkeys(os.path.join(UP, top, rel)) if os.path.isfile(os.path.join(UP, top, rel)) else set()
        for k in tkeys(f) - upk:
            others = we_keys.get(k, set()) - {MAP.get(top, top)}
            if others:
                cnt += 1
                if cnt <= 30:
                    p("   %s  (%s) also in %s" % (k, rel.split(os.sep)[-1], sorted(others)))
p("   total new keys duplicated elsewhere in WE: %d" % cnt)

# ---- 5. KBW definition ids: ours vs every other WE definitions folder
p("== 5. KBW buildable ids we add that another WE submod also defines")
def ids(path):
    try:
        d = json.loads(rd(path))
    except Exception:
        return set()
    items = d if isinstance(d, list) else d.get("buildables", d.get("definitions", []))
    return {x.get("id") for x in items if isinstance(x, dict) and x.get("id")}
we_ids = {}
for f in glob.glob(os.path.join(WE, "*", "42", "media", "KnoxBuildworks", "definitions", "*.json")):
    sm = os.path.relpath(f, WE).split(os.sep)[0]
    for i in ids(f):
        we_ids.setdefault(i, set()).add(sm)
dup = 0
for top in os.listdir(WORK):
    mine = set()
    for f in glob.glob(os.path.join(WORK, top, "42", "media", "KnoxBuildworks", "definitions", "*.json")):
        mine |= ids(f)
    for i in mine:
        o = we_ids.get(i, set()) - {MAP.get(top, top)}
        if o:
            dup += 1
            if dup <= 20:
                p("   %s also in %s" % (i, sorted(o)))
p("   total: %d" % dup)

# ---- 6. WE files newer than our upstream snapshot date, outside tracked files (FYI)
p("== 6. WE submod list and file counts (FYI)")
for sm in sorted(os.listdir(WE)):
    n = sum(1 for _ in walk(os.path.join(WE, sm)))
    p("   %-50s %5d files" % (sm, n))
open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
