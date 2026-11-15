# -*- coding: utf-8 -*-
"""What does BuildingCraft (B42, workshop 3459887404, updated 2026-10-22) and its tile-pack addons
offer that our Knox Buildworks side does not build yet? (user, 2026-11-14)

The BuildingCraft data is Lua tables (BuildingData/Building_Data_*.lua; addons call
BuildingCraft_AddItemData from AddModTexture*.lua). They are RUN in a Lua 5.1 sandbox (lupa) with
stubs for the game API, so every entry comes out with its sprites, build function, skill, materials
and tools exactly as the mod defines them. Commented-out entries are not executed, so they are
not counted.

Compared against every sprite a KBW buildable uses: Knox Buildworks core + VE, WE's Knox
Buildworks Expansion and WE's Community / TikiTown submods as shipped, and our WE work copy (with
our copy tilesets resolved to their source tiles, see tile_coverage_inventory.copy_sources).

Writes zomboid/buildcraft/BUILDINGCRAFT_B42_INVENTORY.md and .csv."""
import collections
import csv
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kbw_tilepatch as k                    # noqa: E402
import tile_coverage_inventory as tci        # noqa: E402

WS = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600"
CORE = os.path.join(WS, "3459887404", "mods", "BuildingCraft", "42.0", "media", "lua")
ADDONS = {   # addon -> (workshop id, the tile pack mod id it needs)
    "PertsPartyTiles": "3737104021",
    "Estate 39": "3619014426",
    "RaccoonCity": "3459888193",
    "Erika's tiles": "3488891189",
}
KBW_DEFS = [os.path.join(WS, "3772269882"),
            os.path.join(WS, "3733324672", "mods"),
            r"c:\Users\josep\Kiro\zomboid\WE_submods\work"]
OUT_DIR = r"c:\Users\josep\Kiro\zomboid\buildcraft"
OUT_MD = os.path.join(OUT_DIR, "BUILDINGCRAFT_B42_INVENTORY.md")
OUT_CSV = os.path.join(OUT_DIR, "BUILDINGCRAFT_B42_INVENTORY.csv")

_HARNESS = r'''
local function stub(name)
    return setmetatable({}, {
        __index = function(_, k) return stub(name .. "." .. tostring(k)) end,
        __call = function() return stub(name .. "()") end,
        __tostring = function() return name end,
        __concat = function(a, b) return tostring(a) .. tostring(b) end,
        __stubname = name,
    })
end
STUBNAME = function(v)
    local mt = type(v) == "table" and getmetatable(v)
    return mt and mt.__stubname or nil
end
getText = function(k) return k end
Keyboard = {}
string.split = function(s, sep) local t = {} for p in string.gmatch(s, "[^_]+") do t[#t + 1] = p end return t end
EVENTS = {}
Events = setmetatable({}, { __index = function(t, k)
    local ev = { Add = function(fn) table.insert(EVENTS, { k, fn, CURRENT }) end, Remove = function() end }
    rawset(t, k, ev); return ev end })
require = function() return nil end
CURRENT = "core"
ADDED = {}
BuildingCraft_AddItemData = function(data, tab)
    table.insert(ADDED, { CURRENT, tab, nil, data })
end
local rows = {}
BuildingCraft_AddListData = function(name, icon, tab)
    rows[tab] = (rows[tab] or 100) + 1
    table.insert(ADDED, { CURRENT, tab, rows[tab], nil, name })
    return rows[tab]
end
BuildingCraft_AddItemDataForIndex = function(data, tab, row)
    table.insert(ADDED, { CURRENT, tab, row, data })
end
-- unknown globals are stubs, except the addons' once-only flags (IsErikaAddComplete = X or false):
-- a truthy stub there would make every addon skip its own data
setmetatable(_G, { __index = function(_, k)
    if type(k) == "string" and (k:find("^Is%u") or k:find("Complete$")) then return nil end
    return stub(tostring(k))
end })
'''


def _py(v, depth=0):
    from lupa import lua51
    if depth > 6:
        return None
    t = lua51.lua_type(v)
    if t == "table":
        d = {kk: _py(v[kk], depth + 1) for kk in list(v.keys())}
        if d and all(isinstance(kk, (int, float)) for kk in d):
            return [d[kk] for kk in sorted(d)]
        return d
    if t == "function":
        return "<function>"
    return v


def run():
    from lupa import lua51
    L = lua51.LuaRuntime(unpack_returned_tuples=True)
    L.execute(_HARNESS)
    errors = []

    def load(path, who):
        L.globals().CURRENT = who
        try:
            L.execute(open(path, encoding="utf-8", errors="ignore").read())
        except Exception as e:
            errors.append("%s: %s" % (os.path.basename(path), str(e).splitlines()[0][:160]))

    data_dir = os.path.join(CORE, "server", "BuildingData")
    load(os.path.join(data_dir, "Building_Data.lua"), "core")
    for p in sorted(glob.glob(os.path.join(data_dir, "Building_Data_*.lua"))):
        load(p, "core")
    for addon, wid in ADDONS.items():
        for p in glob.glob(os.path.join(WS, wid, "mods", "**", "AddModTexture*.lua"), recursive=True):
            if os.sep + "42.0" + os.sep in p or not glob.glob(os.path.join(WS, wid, "mods", "*", "42.0", "**", os.path.basename(p)), recursive=True):
                load(p, addon)
    ev = L.globals().EVENTS
    # only the addons' data hooks (core's events are game logic); an instruction budget stops any
    # loop over a stub (a stub is always truthy, so `while it:hasNext()` would never end)
    guarded = L.eval('''function(fn)
        debug.sethook(function() error("instruction budget exceeded") end, "", 50000000)
        local ok, err = pcall(fn)
        debug.sethook()
        if not ok then error(err) end
    end''')
    seen = set()
    for i in range(1, len(ev) + 1):
        if ev[i][3] == "core" or (ev[i][3], ev[i][1]) in seen:
            continue
        seen.add((ev[i][3], ev[i][1]))       # OnGameStart and OnServerStarted run the same adder
        L.globals().CURRENT = ev[i][3]
        try:
            guarded(ev[i][2])
        except Exception as e:
            errors.append("event %s (%s): %s" % (ev[i][1], ev[i][3], str(e).splitlines()[0][:160]))

    bd = L.globals().Building_Data
    tabs = {}
    entries = []

    def add(who, tab, typ, item):
        it = _py(item)
        if not isinstance(it, dict):
            return
        sp = it.get("Sprite") or []
        if isinstance(sp, str):
            sp = [sp]
        mats = [(m.get("tMaterial"), m.get("Amount")) for m in (it.get("NeedMaterials") or []) if isinstance(m, dict)]
        tools = [t if isinstance(t, list) else [t] for t in (it.get("NeedTools") or [])]
        entries.append({
            "source": who, "tab": tab, "type": typ, "sprites": [s for s in sp if isinstance(s, str)],
            "func": L.globals().STUBNAME(item.Func) or "", "skill": L.globals().STUBNAME(item.NeedSkill) or "",
            "level": it.get("NeedSkillLevel"), "materials": mats, "tools": tools,
        })

    bl = bd.BuildingList
    for ti in list(bl.keys()):
        tab = bl[ti]
        tname = tab.TabName
        tabs[ti] = tname
        sub = tab.subBuildData
        if sub is None:
            continue
        for si in list(sub.keys()):
            s = sub[si]
            items = s.ItemDate
            if items is None:
                continue
            for ii in list(items.keys()):
                add("core", tname, s.TypeName, items[ii])
    added = L.globals().ADDED
    new_rows = {}                                   # (tab, row) -> name of an addon's own new type
    for i in range(1, len(added) + 1):
        if added[i][4] is None and added[i][5] is not None:
            new_rows[(added[i][2], added[i][3])] = added[i][5]

    def type_name(tab, ri):
        """BuildingCraft_AddItemData(data, tab) appends data[ri] to the core type subBuildData[ri]."""
        try:
            return bl[tab].subBuildData[ri].TypeName or "type %s" % ri
        except Exception:
            return "type %s" % ri

    for i in range(1, len(added) + 1):
        who, tab, row, data = added[i][1], added[i][2], added[i][3], added[i][4]
        if data is None:
            continue
        tname = tabs.get(tab, str(tab))
        if row is not None:                         # AddItemDataForIndex: all into the new type
            typ = new_rows.get((tab, row), "new type")
        for ri in list(data.keys()):
            group = data[ri]
            if lua51.lua_type(group) != "table":
                continue
            t = typ if row is not None else type_name(tab, ri)
            if group.Sprite is not None:       # flat list: the row itself is an entry
                add(who, tname, t, group)
                continue
            for ii in list(group.keys()):
                if lua51.lua_type(group[ii]) == "table" and group[ii].Sprite is not None:
                    add(who, tname, t, group[ii])
    return entries, errors


def kbw_sprites():
    files = []
    for root in KBW_DEFS:
        files += glob.glob(os.path.join(root, "**", "definitions", "**", "*.json"), recursive=True)
    cmap = tci.copy_sources()
    out = set()
    for n in tci.refs(files):
        n = cmap.get(n, n)
        out.add(n[len("WECommunity_"):] if n.startswith("WECommunity_") else n)
    return out, len(files)


def sheet_owner():
    """sheet -> pack label, from the installed .tiles files."""
    own = {}
    _v, vts, _o = k._parse(open(k._VANILLA_TILES, "rb").read())
    for n in vts:
        own[n.decode()] = "vanilla"
    for p in [k._VANILLA_TILES.replace("tiledefinitions.tiles", n) for n in ("newtiledefinitions.tiles",)]:
        if os.path.isfile(p):
            _v, ts, _o = k._parse(open(p, "rb").read())
            for n in ts:
                own.setdefault(n.decode(), "vanilla")
    for p in glob.glob(os.path.join(WS, "*", "mods", "**", "*.tiles"), recursive=True):
        if p.endswith(".patch.tiles"):
            continue
        try:
            _v, ts, _o = k._parse(open(p, "rb").read())
        except Exception:
            continue
        m = re.search(r"108600[\\/](\d+)[\\/]mods[\\/]([^\\/]+)", p)
        label = "%s (%s)" % (m.group(2), m.group(1)) if m else os.path.basename(p)
        for n in ts:
            own.setdefault(n.decode(), label)
    return own


def _translations():
    tr = {}
    roots = [os.path.dirname(CORE)] + [p for wid in ADDONS.values()
                                       for p in glob.glob(os.path.join(WS, wid, "mods", "*", "*", "media"))]
    for r in roots:
        en = os.path.join(r, "lua", "shared", "Translate", "EN")
        for f in glob.glob(os.path.join(en, "*.json")):          # B42 translation format
            try:
                tr.update(json.load(open(f, encoding="utf-8-sig")))
            except ValueError:
                pass
        for f in glob.glob(os.path.join(en, "*.txt")):           # older key = "value" files
            for line in open(f, encoding="utf-8", errors="ignore"):
                m = re.match(r'\s*([\w.]+)\s*=\s*"(.*)"\s*,?\s*$', line)
                if m:
                    tr[m.group(1)] = m.group(2)
    return tr


def main():
    entries, errors = run()
    tr = _translations()
    for e in entries:
        e["tab"], e["type"] = tr.get(e["tab"], e["tab"]), tr.get(e["type"], e["type"])
    have, nfiles = kbw_sprites()
    own = sheet_owner()
    # Erika's tiles live on in Drazion's TikiTown pack as *_tterika_* copies (user, 2026-11-14).
    # Checked: where the tterika sheet exists, every Erika entry's index has art there and the tile
    # flags its build function needs (walls, windows, doors, floors, counters) at the same index.
    for e in entries:
        if e["source"] != "Erika's tiles":
            continue
        alias = [s.replace("_erika_", "_tterika_") for s in e["sprites"]]
        if alias and alias[0].rpartition("_")[0] in own:
            e["sprites"], e["erika"] = alias, True
    rows = []
    for e in entries:
        sp = e["sprites"]
        primary = sp[0] if sp else ""
        sheet = primary.rpartition("_")[0]
        covered = [s for s in dict.fromkeys(sp) if s in have]
        st = "covered" if sp and len(covered) == len(set(sp)) else ("partly" if covered else "missing")
        rows.append(dict(e, primary=primary, sheet=sheet, pack=own.get(sheet, "not installed"), status=st))
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["source", "tab", "type", "status", "pack", "sheet", "sprites", "func", "skill", "level",
                    "materials", "tools"])
        for r in rows:
            w.writerow([r["source"], r["tab"], r["type"], r["status"], r["pack"], r["sheet"], " ".join(r["sprites"]),
                        r["func"].replace("BuildingCraftObject.", ""), r["skill"].replace("Perks.", ""), r["level"],
                        "; ".join("%s x%s" % m for m in r["materials"]), " | ".join("/".join(t) for t in r["tools"])])
    # ---- report
    by = collections.Counter((r["source"], r["status"]) for r in rows)
    L = ["# BuildingCraft (B42) inventory vs our KBW buildables (generated)", "",
         "Generated by `pz_craft_loops/buildingcraft_b42_inventory.py`. BuildingCraft 3459887404 (core data updated "
         "2026-10-22) and its four tile-pack addons are run in a Lua sandbox, so every active entry is counted with its "
         "own sprites, build function, skill and materials. Compared with every sprite used by %d KBW definition files "
         "(Knox core + VE, WE's Expansion / Community / TikiTown submods, and our WE work copy)." % nfiles, "",
         "- **covered**: every sprite of the entry is already built by some KBW buildable.",
         "- **partly**: some of its sprites are (for example one face of a multi-tile piece).",
         "- **missing**: none are. Full rows with costs: `BUILDINGCRAFT_B42_INVENTORY.csv`.", "",
         "## Totals", "", "| Source | entries | covered | partly | missing |", "|---|---:|---:|---:|---:|"]
    for src in ["core"] + list(ADDONS):
        n = sum(v for (s, _st), v in by.items() if s == src)
        L.append("| %s | %d | %d | %d | %d |" % (src, n, by[(src, "covered")], by[(src, "partly")], by[(src, "missing")]))
    L.append("")
    # the addons need their tile pack: is it installed?
    ids = {}
    for p in glob.glob(os.path.join(WS, "*", "mods", "*", "**", "mod.info"), recursive=True):
        for line in open(p, encoding="utf-8", errors="ignore"):
            if line.startswith("id="):
                ids.setdefault(line[3:].strip(), p.split(os.sep)[p.split(os.sep).index("108600") + 1])
    L += ["## Addon tile packs", "", "| Addon | needs | installed |", "|---|---|---|"]
    for addon, wid in ADDONS.items():
        need = []
        for p in glob.glob(os.path.join(WS, wid, "mods", "*", "*", "mod.info")):
            for line in open(p, encoding="utf-8", errors="ignore"):
                if line.startswith("require="):
                    need += [x.strip().lstrip("\\") for x in line[8:].split(",") if x.strip().lstrip("\\") != "BuildingCraft"]
        need = sorted(set(need))
        L.append("| %s (%s) | %s | %s |" % (addon, wid, ", ".join(need),
                                            ", ".join("yes (%s)" % ids[n] if n in ids else "no" for n in need)))
    L.append("")
    # missing by pack
    miss = [r for r in rows if r["status"] != "covered"]
    L += ["## Not covered, by tile pack", "", "| Tile pack (sheet owner) | entries | sheets |", "|---|---:|---|"]
    bp = collections.defaultdict(list)
    for r in miss:
        bp[r["pack"]].append(r)
    for p, rs in sorted(bp.items(), key=lambda kv: -len(kv[1])):
        shs = collections.Counter(r["sheet"] for r in rs)
        L.append("| %s | %d | %s |" % (p, len(rs), ", ".join("`%s` %d" % kv for kv in shs.most_common(8)) +
                                       (" ..." if len(shs) > 8 else "")))
    L.append("")
    # missing by tab/type for vanilla + installed packs
    L += ["## Not covered, by BuildingCraft tab / type", ""]
    bt = collections.defaultdict(list)
    for r in miss:
        bt[(r["source"], r["tab"], r["type"])].append(r)
    L += ["| Source | Tab | Type | entries | partly | build function | example sprites |", "|---|---|---|---:|---:|---|---|"]
    for (src, tab, typ), rs in sorted(bt.items(), key=lambda kv: (kv[0][0] != "core", -len(kv[1]))):
        fn = collections.Counter(r["func"].replace("BuildingCraftObject.", "") for r in rs)
        L.append("| %s | %s | %s | %d | %d | %s | %s |" % (
            src, tab, typ, len(rs), sum(1 for r in rs if r["status"] == "partly"),
            ", ".join("%s %d" % kv for kv in fn.most_common(3)), ", ".join("`%s`" % r["primary"] for r in rs[:3])))
    L.append("")
    # Community / TikiTown relevance
    ct = [r for r in rows if "CommunityTilePack" in r["pack"] or "tterika" in r["sheet"] or "tikitown" in r["sheet"]]
    L += ["## Community Tilepack / TikiTown sheets", "",
          "Entries on sheets of the two packs we convert: %d. Erika's tiles entries are matched to the "
          "TikiTown `*_tterika_*` copy of their sheet (same index; art and tile flags checked) when that "
          "sheet exists." % len(ct), "",
          "| Sheet | Type | built | partly | not built |", "|---|---|---:|---:|---:|"]
    g = collections.defaultdict(collections.Counter)
    for r in ct:
        g[(r["sheet"], r["type"])][r["status"]] += 1
    for (sh, typ), c in sorted(g.items()):
        L.append("| `%s` | %s | %d | %d | %d |" % (sh, typ, c["covered"], c["partly"], c["missing"]))
    erika_left = sorted({r["sheet"] for r in rows if r["source"] == "Erika's tiles" and not r.get("erika")})
    L += ["", "Erika sheets with no TikiTown copy: %s" % ", ".join("`%s`" % s for s in erika_left), ""]
    L += ["## Checks", "", "- Load / event errors: %d" % len(errors)] + ["  - %s" % e for e in errors]
    open(OUT_MD, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("entries", len(rows), dict(collections.Counter(r["status"] for r in rows)), "errors", len(errors))
    for e in errors:
        print("  ", e)
    print("wrote", OUT_MD)


if __name__ == "__main__":
    main()
