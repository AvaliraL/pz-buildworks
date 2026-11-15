# -*- coding: utf-8 -*-
"""Implemented-vs-not inventory for the two tile packs we build for (user, 2026-11-09):
Drazion's Tile Pack (TikiTown) and the Unofficial Mappers Community Tilepack.

For every sheet: tiles with art in the pack, and which of them a buildable uses, split by owner:
  ours    = our WE submods (work copy), files 43/44 (paused, not handed off) counted separately
  others  = Knox Buildworks core, Knox VE and WE's Knox Buildworks Expansion
A tile counts as used when a definition names it directly OR through one of our copies
(overlay / detail / soundproof / props mirror copies, WE's WECommunity_* Dylan copies, ice-shell TK tiles).
Unused tiles are classed by their tile properties so the leftovers can be judged at a glance.
Writes zomboid/TILE_COVERAGE_INVENTORY.md (generated; rerun after builds)."""
import collections
import glob
import json
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kbw_tilepatch as k               # noqa: E402
import tikitown_wall_overlays as two    # noqa: E402
import tikitown_wall_detailing as wd    # noqa: E402

WS = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600"
WORK = r"c:\Users\josep\Kiro\zomboid\WE_submods\work"
OUT = r"c:\Users\josep\Kiro\zomboid\TILE_COVERAGE_INVENTORY.md"
OUT_CSV = r"c:\Users\josep\Kiro\zomboid\TILE_COVERAGE_INVENTORY.csv"
PAUSED = {"43_tikitown_wall_paint_cladding.json", "44_tikitown_wall_trim.json"}
COMM = os.path.join(WS, "3628736763", "mods", "CommunityTilePack", "common", "media")
OTHERS = [os.path.join(WS, "3772269882"),
          os.path.join(WS, "3733324672", "mods", "World Essentials - Knox Buildworks Expansion")]
SPRITE = re.compile(r'"([A-Za-z0-9_\-]+_\d+)"')


def pack_names(path):
    """Texture names in a .pack: the PZPK v1 format, or the older headerless one (blackwood, ekron:
    page count first, and each page's PNG runs to its IEND chunk, then a 0xDEADBEEF marker)."""
    names = set()
    data = open(path, "rb").read()
    pos = [0]

    def i32():
        v = struct.unpack_from("<i", data, pos[0])[0]
        pos[0] += 4
        return v

    def s():
        n = i32()
        v = data[pos[0]:pos[0] + n].decode("utf-8", "replace")
        pos[0] += n
        return v

    new = data[:4] == b"PZPK"
    if new:
        pos[0] = 4
        assert i32() == 1
    for _ in range(i32()):
        s(); n = i32(); i32()
        for _e in range(n):
            names.add(s()); pos[0] += 32
        if new:
            ln = i32()          # (not `pos[0] += i32()`: that reads pos before i32 moves it)
            pos[0] += ln
        else:
            end = data.index(b"IEND", pos[0]) + 8
            pos[0] = end + 4 if data[end:end + 4] == b"\xef\xbe\xad\xde" else end
    return names


def tiles_props(path):
    _v, ts, _o = k._parse(open(path, "rb").read())
    return {n.decode(): [dict((kk.decode(), vv.decode("latin-1")) for kk, vv in p) for p in t[6]] for n, t in ts.items()}


# ---- copy sprite -> source sprite
def copy_sources():
    m = {}
    for i, sh in enumerate(two.SHEETS):
        for t in range(two.FIRST, two.FIRST + two.PER_SHEET):
            m[two.overlay_sprite(sh, t)] = "%s_%d" % (sh, t)
    for src, cp, _p in wd.copy_tiles():
        m[cp] = src
    try:
        import tikitown_soundproof as sp
        for i in sp.SOUNDPROOF_SRC:
            m[sp.copy_sprite(i)] = "%s_%d" % (sp.SHEET, i)
    except Exception:
        pass
    try:
        import tikitown_props14 as p14
        for i in p14.MIRRORS:
            m[p14.mirror_sprite(i)] = "%s_%d" % (p14.SHEET, i)
    except Exception:
        pass
    try:
        import we_dylan
        for orig, cp in we_dylan.sprite_map().items():
            m[cp] = orig
    except Exception:
        pass
    for s in k._ICESHELL_SRC:
        m[k.iceshell_name(s)] = "%s_%d" % (k._ICESHELL_SRC_SHEET, s)
    # Community copies in KBWCommunityIceShell (decor copies, 2nd Wall Screen TVs), mirrors, L-couch
    for sh, s, _e, _k, _g in k.DECOR_COPIES:
        m[k.decor_copy_name(s, sh)] = "%s_%d" % (sh, k._src_index(s))
    for n, (s, _edge) in enumerate(k.WALLTV):
        m[k.walltv_name(n)] = "%s_%d" % (k.FR_SHEET, s)
    for src, cp in k.VIEWSCREEN_NORTH.items():
        m[cp] = src
    for s in k._CASES_MIRRORS:
        m[k.cases_mirror_name(s)] = "%s_%d" % (k._CASES_SRC_SHEET, s)
    for s, _f, _g in k._FEARS_MIRRORS:
        m[k.fears_mirror_name(s)] = "fears_workbenches_%d" % s
    # L-couch ends (d_furniture_couches_01; Orange = recoloured Pink) and corners (d_location_sofaking)
    for ci, (cname, cbase) in enumerate(k.L_COUCH_END_SOURCES):
        for j in range(8):
            m[k.orange_couch_tile_name(ci * 8 + j)] = "d_furniture_couches_01_%d" % (cbase + j)
    for ci, (cname, cbase) in enumerate(k.L_COUCH_CORNER_SOURCES):
        for v in range(4):
            m[k.lcouch_corner_name(ci, v)] = "d_location_sofaking_%d" % (cbase + v)
    # TikiTown copy tilesets appended to the wall-overlay pack
    try:
        import ladders as lad
        for i in lad.LADDER_SRC:
            m[lad.copy_sprite(i)] = "%s_%d" % (lad.SHEET, i)
    except Exception:
        pass
    try:
        import tikitown_entertainment as ent
        _v, tts, _o = k._parse(open(k._TIKITOWN_TILES, "rb").read())
        for src_name, copy_name, _p, _mir in ent.copy_tiles(tts):
            m[copy_name] = src_name
    except Exception:
        pass
    return m


def refs(paths):
    out = set()
    for p in paths:
        try:
            out |= set(SPRITE.findall(open(p, encoding="utf-8", errors="replace").read()))
        except OSError:
            pass
    return out


def tile_class(p):
    if not p:
        return "no-props"
    keys = set(p)
    if "container" in keys:
        return "container"
    if keys & {"WallN", "WallW", "WallNW", "WallSE", "WindowN", "WindowW", "DoorWallN", "DoorWallW", "doorN", "doorW"}:
        return "wall/door/window"
    if keys & {"solidfloor", "FloorOverlay", "attachedFloor", "IsFloor"}:
        return "floor"
    if keys & {"WallOverlay", "attachedN", "attachedW", "attachedE", "attachedS", "TileOverlay"}:
        return "overlay"
    if keys & {"RoofWall", "WestRoofB", "WestRoofM", "WestRoofT", "SlopedSurface"} or any(x.startswith("Roof") for x in keys):
        return "roof"
    if "IsMoveAble" in keys:
        return "furniture/prop"
    return "other"


def _ranges(idx):
    """[0,1,2,5,7,8] -> '0-2, 5, 7-8'."""
    out, idx = [], sorted(idx)
    i = 0
    while i < len(idx):
        j = i
        while j + 1 < len(idx) and idx[j + 1] == idx[j] + 1:
            j += 1
        out.append(str(idx[i]) if i == j else "%d-%d" % (idx[i], idx[j]))
        i = j + 1
    return ", ".join(out)


def main():
    cmap = copy_sources()
    ours_files = [p for p in glob.glob(os.path.join(WORK, "*", "42", "media", "KnoxBuildworks", "definitions", "*.json"))
                  if os.path.basename(p) not in PAUSED]
    paused_files = [p for p in glob.glob(os.path.join(WORK, "*", "42", "media", "KnoxBuildworks", "definitions", "*.json"))
                    if os.path.basename(p) in PAUSED]
    other_files = [p for r in OTHERS for p in glob.glob(os.path.join(r, "**", "definitions", "**", "*.json"), recursive=True)]
    # WE's isolated copies keep the source name behind a prefix (WECommunity_<sheet>_<i>)
    def _one(n):
        n = cmap.get(n, n)
        return n[len("WECommunity_"):] if n.startswith("WECommunity_") else n
    resolve = lambda names: {_one(n) for n in names}
    ours, paused, others = resolve(refs(ours_files)), resolve(refs(paused_files)), resolve(refs(other_files))
    # sheet -> our definition files (number prefix) that build any of its tiles
    files_of = collections.defaultdict(set)
    for p in ours_files + paused_files:
        # C = Community submod, T = TikiTown submod (file numbers overlap between the two)
        tag = ("T" if "TikiTown" in p else "C") + os.path.basename(p).split("_", 1)[0]
        for n in resolve(refs([p])):
            files_of[n.rpartition("_")[0]].add(tag)

    packs = {
        "Drazion's Tile Pack (TikiTown)": (
            [k._TIKITOWN_TILES], [two._TIKITOWN_PACK]),
        "Community Tilepack": (
            sorted(glob.glob(os.path.join(COMM, "*.tiles"))), sorted(glob.glob(os.path.join(COMM, "texturepacks", "*.pack")))),
    }
    L = ["# Tile coverage inventory (generated)", "",
         "Generated by `pz_craft_loops/tile_coverage_inventory.py` from the installed packs and the definitions in "
         "`zomboid/WE_submods/work` (ours), Knox core / VE and WE's Knox Buildworks Expansion (others). Rerun after builds.", "",
         "- **ours**: used by our shipped submod definitions (files 43/44, paused and not handed off, are shown as *paused*).",
         "- **others**: used only by Knox / VE / WE's Expansion (already buildable, not by us).",
         "- **unused**: tiles with art that nothing builds, classed by tile properties.",
         "- Status: **complete** = no unused tiles; **partial** = some; **untouched** = nothing builds any tile.",
         "- **our files**: definition files that build the sheet (C = Community submod, T = TikiTown submod, by "
         "file number). Test-bundle-only work (furnace suite, DOOM fridge) is not counted.",
         "- A CSV copy with the index ranges is written next to this file (`TILE_COVERAGE_INVENTORY.csv`).",
         "- Unused counts include tiles skipped on purpose (damaged / burnt variants, fixtures without props, see the "
         "`zomboid/tikitown/TODO_*.md` notes), so *partial* does not always mean work is left.", ""]
    grand = collections.Counter()
    sheet_rows = {}
    detail = collections.defaultdict(list)
    for pack, (tfiles, pfiles) in packs.items():
        props = {}
        for f in tfiles:
            props.update(tiles_props(f))
        art = set()
        for f in pfiles:
            art |= pack_names(f)
        by = collections.defaultdict(set)
        for n in art:
            sh, _s, i = n.rpartition("_")
            if i.isdigit() and sh in props:
                by[sh].add(int(i))
        rows = []
        tot = collections.Counter()
        for sh in sorted(by):
            idx = by[sh]
            name = lambda i: "%s_%d" % (sh, i)
            o = {i for i in idx if name(i) in ours}
            pz = {i for i in idx if name(i) in paused and i not in o}
            ot = {i for i in idx if name(i) in others and i not in o and i not in pz}
            un = sorted(idx - o - pz - ot)
            cls = collections.Counter(tile_class(props[sh][i] if i < len(props[sh]) else {}) for i in un)
            status = "complete" if not un else ("untouched" if not (o or pz or ot) else "partial")
            rows.append((sh, len(idx), len(o), len(pz), len(ot), len(un), status, cls))
            detail[pack].append((sh, status, sorted(o | pz | ot), un,
                                 sorted(files_of.get(sh, ()), key=lambda t: (len(t), t)), cls))
            tot.update({"sheets": 1, "tiles": len(idx), "ours": len(o), "paused": len(pz), "others": len(ot),
                        "unused": len(un), status: 1})
        sheet_rows[pack] = rows
        grand[pack] = tot
    # summary
    L += ["## Summary", "", "| Pack | Sheets | complete | partial | untouched | Tiles | ours | paused | others | unused |",
          "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for pack, t in grand.items():
        L.append("| %s | %d | %d | %d | %d | %d | %d | %d | %d | %d |" % (
            pack, t["sheets"], t["complete"], t["partial"], t["untouched"], t["tiles"], t["ours"], t["paused"],
            t["others"], t["unused"]))
    L.append("")
    for pack, rows in sheet_rows.items():
        # group by sheet family prefix for readability
        L += ["## %s" % pack, ""]
        for status in ("partial", "untouched", "complete"):
            sel = [r for r in rows if r[6] == status]
            if not sel:
                continue
            L += ["### %s (%d sheets)" % (status.capitalize(), len(sel)), "",
                  "| Sheet | tiles | ours | paused | others | unused | unused by type |", "|---|---:|---:|---:|---:|---:|---|"]
            fmap = {d[0]: d[4] for d in detail[pack]}
            L[-2] = "| Sheet | tiles | ours | paused | others | unused | our files | unused by type |"
            L[-1] = "|---|---:|---:|---:|---:|---:|---|---|"
            for sh, n, o, pz, ot, un, _st, cls in sorted(sel, key=lambda r: (-r[5], r[0])):
                L.append("| `%s` | %d | %d | %s | %d | %d | %s | %s |" % (
                    sh, n, o, pz or "", ot, un, " ".join(fmap.get(sh, ())),
                    ", ".join("%s %d" % kv for kv in cls.most_common()) or ""))
            L.append("")
        # partial sheets: exactly which indices are built and which are left
        L += ["### Partial sheets: indices built / left", "",
              "Index ranges per sheet (built = ours, paused or others).", ""]
        for sh, st, built, left, files, _cls in sorted(detail[pack], key=lambda d: (-len(d[3]), d[0])):
            if st != "partial":
                continue
            L.append("- `%s` (files %s)" % (sh, " ".join(files) or "others only"))
            L.append("  - built %d: %s" % (len(built), _ranges(built)))
            L.append("  - left %d: %s" % (len(left), _ranges(left)))
        L.append("")
    open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    # machine-readable copy for the BuildCraft addon mapping step
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        import csv
        w = csv.writer(f)
        w.writerow(["pack", "sheet", "status", "tiles", "built", "left", "our_files", "built_idx", "left_idx",
                    "left_by_type"])
        for pack, ds in detail.items():
            for sh, st, built, left, files, cls in sorted(ds):
                w.writerow([pack, sh, st, len(built) + len(left), len(built), len(left), " ".join(files),
                            _ranges(built), _ranges(left), "; ".join("%s %d" % kv for kv in cls.most_common())])
    for pack, t in grand.items():
        print("%-32s sheets %3d: complete %3d partial %3d untouched %3d | tiles %5d ours %5d paused %4d others %4d unused %5d" % (
            pack, t["sheets"], t["complete"], t["partial"], t["untouched"], t["tiles"], t["ours"], t["paused"], t["others"], t["unused"]))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
