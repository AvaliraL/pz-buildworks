# -*- coding: utf-8 -*-
"""Sprite-level map of the B41 Building Menu addons onto the Community Tilepack sheets
(user, 2026-11-13: "finish mapping the buildcraft addons we have to the community tilepack sheets
to aid in mass conversion").

Instead of re-parsing each addon's factories by regex (transpile_buildmenu.py handles only some of
them), the addon Lua is RUN in a Lua 5.1 sandbox (lupa) against a mock Building Menu API:
  * the core Building Menu's own recipe file (BuildingMenu02_Recipes.lua) is loaded for real, so
    every recipe table the addons point at has its real materials / tools / skills;
  * BuildingMenu.createObject / addObjectsToCategories are replaced by recorders;
  * anything else (onBuild callbacks, UI helpers, sandbox flags) resolves to a named stub.
All sandbox feature flags are on, so every menu entry is produced, and each entry keeps its tab /
category / subcategory, display name, recipe and sprites.

Then each sprite is matched to a Community sheet + index, and joined with TILE_COVERAGE_INVENTORY.csv
(tile_coverage_inventory.py; rerun that first) to say what is already built.
Writes:
  zomboid/communitytilepack/ADDON_SPRITE_MAP.md   per-sheet summary + conversion queue
  zomboid/communitytilepack/ADDON_SPRITE_MAP.csv  one row per addon entry (machine-readable)
  zomboid/communitytilepack/ADDON_RECIPES.json    every recipe table the entries use
"""
import collections
import csv
import json
import os
import re

WS = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600"
CORE = os.path.join(WS, "3067798182", "mods", "BuildingMenu", "media")
ADDONS = {
    "Dirkies": os.path.join(WS, "3137091536", "mods", "BuildingMenuDaddyDirkieAddon", "media"),
    "Dylan": os.path.join(WS, "3137091698", "mods", "BuildingMenuDylanAddon", "media"),
    "TK": os.path.join(WS, "3246568083", "mods", "BuildingMenuThrottlekittysAddon", "media"),
}
COVERAGE = r"c:\Users\josep\Kiro\zomboid\TILE_COVERAGE_INVENTORY.csv"
OUT_DIR = r"c:\Users\josep\Kiro\zomboid\communitytilepack"
OUT_MD = os.path.join(OUT_DIR, "ADDON_SPRITE_MAP.md")
OUT_CSV = os.path.join(OUT_DIR, "ADDON_SPRITE_MAP.csv")
OUT_RECIPES = os.path.join(OUT_DIR, "ADDON_RECIPES.json")
# (addon, menu category) left out of the conversion queue by decision, with the reason
SKIPPED = {("Dylan", "Barricades"): "user 2026-11-19: junk piles, effectively clutter; not wanted for now"}
# Dylan entries using a dylanstiles sprite that World Essentials' WECommunity_Dylan copies don't cover
DYLAN_UNMAPPED_WHY = ("Dylan entries with a sprite outside WE's WECommunity_Dylan copies: not built (user "
                      "2026-08-28). The raw dylanstiles numbers shift with Fort Waterfront B42 (we_dylan.py).")
_WE_DYLAN = None


def _we_dylan_map():
    global _WE_DYLAN
    if _WE_DYLAN is None:
        import we_dylan
        _WE_DYLAN = we_dylan.sprite_map()
    return _WE_DYLAN


# single entries left out by decision, keyed by any of their sprites
SKIPPED_SPRITES = {"d_doors_01_56": "Grey Door (Bloodied): removed on purpose, the blood texture never shows "
                                    "in game (rename_dirkies_doors.py)"}

# Lua side: stubs + recorders. Runs in plain Lua 5.1 (not Kahlua); only used to read data.
_HARNESS = r'''
local function stub(name)
    local s = {}
    return setmetatable(s, {
        __index = function(_, k) return stub(name .. "." .. tostring(k)) end,
        __call = function() return stub(name .. "()") end,
        __tostring = function() return "<" .. name .. ">" end,
        __concat = function(a, b) return tostring(a) .. tostring(b) end,
        __stubname = name,
    })
end
STUBNAME = function(v)
    local mt = type(v) == "table" and getmetatable(v)
    return mt and mt.__stubname or nil
end
local function permissive(name)
    return setmetatable({}, { __index = function(t, k) return stub(name .. "." .. tostring(k)) end })
end
BM = setmetatable({}, { __index = function(_, k) return stub("BuildingMenu." .. tostring(k)) end })
BM.round = function(x) return math.floor(x + 0.5) end
BM.Tabs = {}
BM.ObjectCounts = {}
EVENTS = {}
Events = setmetatable({}, { __index = function(t, k)
    local ev = { Add = function(fn) table.insert(EVENTS, { k, fn, CURRENT_ADDON }) end, Remove = function() end }
    rawset(t, k, ev)
    return ev
end })
-- filled from the mods' sandbox-options.txt defaults (Python side); feature flags forced on
SandboxVars = setmetatable({
    BuildingMenu = setmetatable({}, { __index = function() return true end }),
    BuildingMenuRecipes = {},
}, { __index = function() return setmetatable({}, { __index = function() return true end }) end })
table.newarray = function() return {} end
getText = function(k) return k end
getTextOrNull = function(k) return nil end
isClient = function() return true end
isServer = function() return false end
getActivatedMods = function() return { contains = function() return true end } end
MODULES = { BuildingMenu01_Main = BM }
require = function(name)
    if MODULES[name] == nil then MODULES[name] = permissive(name) end
    return MODULES[name]
end
setmetatable(_G, { __index = function(_, k) return stub(tostring(k)) end })

RECORDS = {}
CURRENT_ADDON = "?"
BM.createObject = function(displayName, description, action, recipe, isRecipeKnown, options, sprites, nameID)
    local r = { addon = CURRENT_ADDON, displayName = displayName, description = description,
                action = STUBNAME(action) or tostring(action), recipe = recipe, options = options,
                sprites = sprites, placed = false }
    table.insert(RECORDS, r)
    return r
end
BM.addObjectsToCategories = function(tabName, categoryName, categoryIcon, subcategoryName, subCategoryIcon, objects)
    for i = 1, #(objects or {}) do
        local o = objects[i]
        if type(o) == "table" and o.addon then
            o.placed = true
            o.tab, o.category, o.subcategory = tabName, categoryName, subcategoryName
        end
    end
end
'''


def _lua_to_py(v, depth=0):
    """lupa table -> plain dict / list (stubs -> their name)."""
    from lupa import lua51
    if depth > 8:
        return None
    if lua51.lua_type(v) == "table":
        out = {}
        for k in list(v.keys()):
            out[k] = _lua_to_py(v[k], depth + 1)
        if out and all(isinstance(k, (int, float)) for k in out):
            return [out[k] for k in sorted(out)]
        return out
    if lua51.lua_type(v) == "function":
        return "<function>"
    return v


def _sprites(tab, path=""):
    """Every sprite name in a sprites table, with its key path (sprite, northSprite, ...)."""
    out = []
    if isinstance(tab, dict):
        for k, v in tab.items():
            out += _sprites(v, "%s.%s" % (path, k) if path else str(k))
    elif isinstance(tab, list):
        for i, v in enumerate(tab):
            out += _sprites(v, "%s[%d]" % (path, i))
    elif isinstance(tab, str) and re.match(r"^[A-Za-z][\w\- ]*_\d+$", tab):
        out.append((path, tab))
    return out


def _translations():
    tr = {}
    roots = [CORE] + list(ADDONS.values())
    for r in roots:
        d = os.path.join(r, "lua", "shared", "Translate", "EN")
        if not os.path.isdir(d):
            continue
        for f in os.listdir(d):
            for line in open(os.path.join(d, f), encoding="utf-8", errors="ignore"):
                m = re.match(r'\s*([\w.]+)\s*=\s*"(.*)"\s*,?\s*$', line)
                if m:
                    tr[m.group(1)] = m.group(2)
    return tr


def run_addons():
    from lupa import lua51
    L = lua51.LuaRuntime(unpack_returned_tuples=True)
    L.execute(_HARNESS)
    errors = []
    # sandbox defaults: recipe numbers as the mod ships them; menu feature flags all on (above)
    sv = L.globals().SandboxVars
    for root in [CORE] + list(ADDONS.values()):
        p = os.path.join(root, "sandbox-options.txt")
        if not os.path.isfile(p):
            continue
        txt = open(p, encoding="utf-8", errors="ignore").read()
        for m in re.finditer(r"option\s+(\w+)\.(\w+)\s*\{(.*?)\}", txt, re.S):
            page, key, body = m.group(1), m.group(2), m.group(3)
            t = re.search(r"type\s*=\s*(\w+)", body)
            d = re.search(r"default\s*=\s*([^,\n]+)", body)
            if not d or page == "BuildingMenu" and t and t.group(1) == "boolean":
                continue
            raw = d.group(1).strip()
            val = (raw == "true") if t and t.group(1) == "boolean" else (float(raw) if re.match(r"^-?[\d.]+$", raw) else raw)
            if t and t.group(1) in ("integer", "enum") and isinstance(val, float):
                val = int(val)
            if sv[page] is None or page not in ("BuildingMenu", "BuildingMenuRecipes"):
                L.execute("SandboxVars[%r] = SandboxVars[%r] or {}" % (page, page))
            sv[page][key] = val

    def load(path, addon):
        L.globals().CURRENT_ADDON = addon
        src = open(path, encoding="utf-8", errors="ignore").read()
        try:
            L.execute(src)
        except Exception as e:      # report and keep going
            errors.append("%s: %s" % (os.path.relpath(path, WS), str(e).splitlines()[0][:200]))

    load(os.path.join(CORE, "lua", "client", "BuildingMenu02_Recipes.lua"), "core")
    # addon files: shared first (patches / recipes), then client, skipping UI-only timed actions
    for addon, root in ADDONS.items():
        files = []
        for sub in ("shared", "client"):
            d = os.path.join(root, "lua", sub)
            for dp, _dn, fn in os.walk(d):
                if "TimedActions" in dp or "Translate" in dp:
                    continue
                files += [os.path.join(dp, f) for f in sorted(fn) if f.endswith(".lua")]
        for f in files:
            load(f, addon)
    # fire the events in registration order: core recipes first, then the addons' menu builders
    events = L.globals().EVENTS
    n = len(events)
    ordered = sorted(range(1, n + 1), key=lambda i: 0 if "Recipe" in str(events[i][1]) else 1)
    owner = {}
    for i in ordered:
        name, fn = events[i][1], events[i][2]
        L.globals().CURRENT_ADDON = events[i][3]     # entries belong to the addon that registered the event
        try:
            fn()
        except Exception as e:
            errors.append("event %s #%d: %s" % (name, i, str(e).splitlines()[0][:200]))
    # recipe table -> its BuildingMenu key
    rev = L.eval('''function()
        local r = {}
        for k, v in pairs(BM) do if type(v) == "table" and type(k) == "string" and k:find("Recipe") then r[v] = k end end
        return r end''')()
    recipes = {}
    rows = []
    recs = L.globals().RECORDS
    for i in range(1, len(recs) + 1):
        r = recs[i]
        rname = rev[r.recipe] if r.recipe is not None and rev[r.recipe] is not None else None
        if rname is None:
            sn = L.globals().STUBNAME(r.recipe) if r.recipe is not None else None
            # a recipe table built in place: keep it under the entry's own name
            rname = sn or (("inline:%s" % r.displayName) if r.recipe is not None else "")
        if rname and rname not in recipes and r.recipe is not None and not str(rname).startswith("BuildingMenu."):
            recipes[rname] = _lua_to_py(r.recipe)
        rows.append({
            "addon": r.addon, "placed": bool(r.placed), "tab": r.tab or "", "category": r.category or "",
            "subcategory": r.subcategory or "", "displayName": r.displayName or "", "action": r.action or "",
            "recipe": rname, "options": _lua_to_py(r.options) or {}, "sprites": _sprites(_lua_to_py(r.sprites)),
        })
    return rows, recipes, errors


def _ranges(idx):
    out, idx = [], sorted(set(idx))
    i = 0
    while i < len(idx):
        j = i
        while j + 1 < len(idx) and idx[j + 1] == idx[j] + 1:
            j += 1
        out.append(str(idx[i]) if i == j else "%d-%d" % (idx[i], idx[j]))
        i = j + 1
    return ", ".join(out)


def _parse_ranges(s):
    out = set()
    for part in (s or "").split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-")
            out.update(range(int(a), int(b) + 1))
        else:
            out.add(int(part))
    return out


def main():
    rows, recipes, errors = run_addons()
    tr = _translations()
    cov = {r["sheet"]: r for r in csv.DictReader(open(COVERAGE, encoding="utf-8")) if r["pack"] == "Community Tilepack"}
    built = {sh: _parse_ranges(r["built_idx"]) for sh, r in cov.items()}
    left = {sh: _parse_ranges(r["left_idx"]) for sh, r in cov.items()}
    # entry -> sprites on Community sheets
    per_sheet = collections.defaultdict(lambda: {"entries": [], "idx": set()})
    other_sheets = collections.Counter()
    out_rows = []
    for r in rows:
        name = tr.get(r["displayName"], r["displayName"])
        comm, status = [], []
        for path, sp in r["sprites"]:
            sh, _s, i = sp.rpartition("_")
            if sh in cov:
                i = int(i)
                comm.append((sh, i, path))
                per_sheet[sh]["idx"].add(i)
            else:
                other_sheets[sh] += 1
        sheets = sorted({c[0] for c in comm})
        n_built = sum(1 for sh, i, _p in comm if i in built.get(sh, ()))
        st = ("no community sprite" if not comm else "built" if n_built == len(comm)
              else "not built" if n_built == 0 else "partly built")
        if st in ("not built", "partly built") and (
                (r["addon"], tr.get(r["category"], r["category"])) in SKIPPED
                or any(sp in SKIPPED_SPRITES for _p, sp in r["sprites"])
                or (r["addon"] == "Dylan" and any(sh in cov and "%s_%d" % (sh, i) not in _we_dylan_map()
                                                  for sh, i, _p in comm))):
            st = "skipped"
        for sh in sheets:
            per_sheet[sh]["entries"].append((r, name, st))
        out_rows.append([r["addon"], r["tab"], r["category"], r["subcategory"], name, r["displayName"], r["action"],
                         r["recipe"], st, "; ".join(sheets),     # (a sheet name can hold a space)
                         " ".join("%s=%s" % (p, s) for p, s in r["sprites"]),
                         json.dumps(r["options"], ensure_ascii=False, sort_keys=True)])
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["addon", "tab", "category", "subcategory", "name", "name_key", "action", "recipe", "status",
                    "community_sheets", "sprites", "options"])
        w.writerows(out_rows)
    json.dump(recipes, open(OUT_RECIPES, "w", encoding="utf-8"), indent=1, ensure_ascii=False, sort_keys=True)

    # ---- markdown ----
    st_count = collections.Counter(r[8] for r in out_rows)
    by_addon = collections.Counter((r[0], r[8]) for r in out_rows)
    L = ["# Building Menu addons -> Community Tilepack sheets (generated)", "",
         "Generated by `pz_craft_loops/map_buildmenu_addons.py`. The three B41 Building Menu addons are run in a Lua "
         "sandbox against a mock Building Menu API (all sandbox options on), so every menu entry is listed with its "
         "real sprites and recipe. Built status comes from `zomboid/TILE_COVERAGE_INVENTORY.csv` "
         "(rerun `tile_coverage_inventory.py` first).", "",
         "- **built**: every Community sprite of the entry is already used by a buildable.",
         "- **partly built** / **not built**: some / none of its sprites are. These are the mass-conversion queue.",
         "- Full rows (sprites per face, options): `ADDON_SPRITE_MAP.csv`. Recipes: `ADDON_RECIPES.json`.", "",
         "## Totals", "", "| Addon | entries | built | partly built | not built | no community sprite |",
         "|---|---:|---:|---:|---:|---:|"]
    for a in ADDONS:
        L.append("| %s | %d | %d | %d | %d | %d |" % (
            a, sum(v for (aa, _s), v in by_addon.items() if aa == a), by_addon[(a, "built")],
            by_addon[(a, "partly built")], by_addon[(a, "not built")], by_addon[(a, "no community sprite")]))
    L.append("| **all** | %d | %d | %d | %d | %d |" % (len(out_rows), st_count["built"], st_count["partly built"],
                                                      st_count["not built"], st_count["no community sprite"]))
    L.append("")
    if st_count["skipped"]:
        L.append("**Skipped by decision** (not in the queue): %s." % "; ".join(
            "%s %s, %d entries (%s)" % (a, c, sum(1 for r in out_rows if r[0] == a and r[8] == "skipped"
                                               and (tr.get(r[2], r[2]) or "?") == c), why)
            for (a, c), why in sorted(SKIPPED.items())))
        for sp, why in sorted(SKIPPED_SPRITES.items()):
            L.append("- single entry with %s: %s" % (sp, why))
        L.append("- %s" % DYLAN_UNMAPPED_WHY)
        L.append("")
    # queue by the addon's own category: batches of the same kind of piece (one KBW template each)
    q = collections.defaultdict(lambda: [0, set(), collections.Counter()])
    for r in out_rows:
        if r[8] in ("built", "no community sprite", "skipped"):
            continue
        key = (r[0], tr.get(r[2], r[2]) or "?")
        q[key][0] += 1
        q[key][1].update(s for s in r[9].split("; ") if s)
        q[key][2][r[6].replace("BuildingMenu.", "")] += 1
    L += ["## Queue by addon category", "",
          "Not-built entries per addon menu category: a batch of one kind of piece. Action = the addon's build "
          "callback (what kind of object it makes).", "",
          "| Addon | Category | entries | sheets | actions |", "|---|---|---:|---|---|"]
    for (a, cat), (n, shs, acts) in sorted(q.items(), key=lambda kv: -kv[1][0]):
        L.append("| %s | %s | %d | %s | %s |" % (a, cat, n, ", ".join("`%s`" % s for s in sorted(shs)),
                                                 ", ".join("%s %d" % kv for kv in acts.most_common())))
    L.append("")
    # per sheet
    L += ["## Per sheet", "",
          "Addon-covered = indices any addon entry uses. Queue = addon-covered but not built. "
          "No addon = left tiles no addon covers (would need hand authoring).", "",
          "| Sheet | tiles | built | addon-covered | queue (entries) | queue tiles | left, no addon |",
          "|---|---:|---:|---:|---:|---:|---:|"]
    sheet_lines = []
    for sh in sorted(cov, key=lambda s: -len(per_sheet[s]["idx"] - built.get(s, set()))):
        ps = per_sheet.get(sh)
        covered = ps["idx"] if ps else set()
        q_idx = covered - built.get(sh, set())
        q_ent = sum(1 for _r, _n, st in (ps["entries"] if ps else []) if st != "built")
        no_addon = left.get(sh, set()) - covered
        if not covered:
            continue
        L.append("| `%s` | %s | %d | %d | %d | %d | %d |" % (sh, cov[sh]["tiles"], len(built.get(sh, ())), len(covered),
                                                            q_ent, len(q_idx), len(no_addon)))
        sheet_lines.append((sh, ps, q_idx, no_addon))
    untouched = [sh for sh in cov if sh not in per_sheet]
    L += ["", "Sheets no addon touches (%d): %s" % (len(untouched), ", ".join("`%s`" % s for s in sorted(untouched))), ""]
    # queue detail
    L += ["## Conversion queue by sheet", "",
          "Entries not (fully) built, grouped by the addon's own menu placement. "
          "Format: name - recipe - action - sprite indices on this sheet.", ""]
    for sh, ps, q_idx, no_addon in sheet_lines:
        ents = [(r, n, st) for r, n, st in ps["entries"] if st != "built"]
        if not ents:
            continue
        L.append("### `%s` (%d entries, tiles %s)" % (sh, len(ents), _ranges(q_idx)))
        L.append("")
        grp = collections.defaultdict(list)
        for r, n, st in ents:
            grp[(r["addon"], tr.get(r["category"], r["category"]), tr.get(r["subcategory"], r["subcategory"]))].append((r, n, st))
        for (a, cat, sub), es in sorted(grp.items()):
            L.append("- **%s / %s / %s**" % (a, cat or "?", sub or "?"))
            for r, n, st in es:
                idx = sorted(int(sp.rpartition("_")[2]) for _p, sp in r["sprites"] if sp.rpartition("_")[0] == sh)
                L.append("  - %s - %s - %s - %s%s" % (n, r["recipe"] or "no recipe", r["action"].replace("BuildingMenu.", ""),
                                                     _ranges(idx), " (partly built)" if st == "partly built" else ""))
        L.append("")
    if other_sheets:
        L += ["## Sprites on non-Community sheets", "",
              "Vanilla or other-pack sheets the addons also use (not part of this map): " +
              ", ".join("`%s` %d" % kv for kv in other_sheets.most_common(30)), ""]
    unplaced = [r for r in rows if not r["placed"]]
    L += ["## Checks", "",
          "- Entries created but never added to a menu category: %d" % len(unplaced),
          "- Load / event errors: %d" % len(errors)]
    L += ["  - %s" % e for e in errors]
    open(OUT_MD, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("entries %d: %s" % (len(out_rows), dict(st_count)))
    print("errors %d" % len(errors))
    for e in errors:
        print("  ", e)
    print("wrote", OUT_MD)


if __name__ == "__main__":
    main()
