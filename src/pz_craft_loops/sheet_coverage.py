"""Which tiles of each TikiTown wall sheet does no buildable use? Read-only report.
Tiles that exist = have an image in tikitown_tiles.pack. Used = any sprite in our built defs."""
import json, os, glob, re, struct, sys, collections as c
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tikitown_wall_overlays as two
import tikitown_naming_pass as tnp
import kbw_tilepatch as k

DEFS = r"c:\Users\josep\Kiro\zomboid\tikitown\mod_build\TikiTownKBW\Contents\mods\TikiTownKBW\42\media\KnoxBuildworks\definitions"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_sheet_coverage.txt")


def pack_names(path):
    names = set()
    with open(path, "rb") as f:
        i32 = lambda: struct.unpack("<i", f.read(4))[0]
        s = lambda: f.read(i32()).decode("utf-8", "replace")
        assert f.read(4) == b"PZPK" and i32() == 1
        for _ in range(i32()):
            s(); n = i32(); i32()
            for _e in range(n):
                names.add(s()); f.read(32)
            f.seek(i32(), 1)
    return names


def used_sprites():
    used = set()
    for p in glob.glob(os.path.join(DEFS, "*.json")):
        used |= set(re.findall(r'"([A-Za-z0-9_\-]+_\d+)"', open(p, encoding="utf-8").read()))
    return used


def main():
    have = pack_names(two._TIKITOWN_PACK)
    used = used_sprites()
    _v, ts, _o = k._parse(open(k._TIKITOWN_TILES, "rb").read())
    by_sheet = c.defaultdict(set)
    for n in have:
        sh, _s, i = n.rpartition("_")
        if i.isdigit():
            by_sheet[sh].add(int(i))
    L = []
    pattern = c.Counter()
    for sh in sorted(tnp.STYLES):
        tiles = by_sheet.get(sh, set())
        miss = sorted(i for i in tiles if "%s_%d" % (sh, i) not in used)
        rows = []
        for i in miss:
            props = dict(ts.get(sh.encode(), [None] * 7)[6][i]) if sh.encode() in ts and i < len(ts[sh.encode()][6]) else {}
            keys = sorted(x.decode() for x in props if x not in (b"CustomName", b"GroupName"))
            rows.append("%d[%s]" % (i, ",".join(keys)[:60]))
        pattern[tuple(miss)] += 1
        L.append("%-42s tiles %3d  used %3d  UNUSED %3d" % (sh, len(tiles), len(tiles) - len(miss), len(miss)))
        L.append("    " + "  ".join(rows))
    L.append("")
    L.append("most common unused index sets:")
    for k_, n in pattern.most_common(6):
        L.append("  %2d sheets: %s" % (n, list(k_)))
    open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    tot = sum(len(by_sheet.get(sh, ())) for sh in tnp.STYLES)
    un = sum(len([i for i in by_sheet.get(sh, ()) if "%s_%d" % (sh, i) not in used]) for sh in tnp.STYLES)
    print("%d style sheets: %d tiles, %d unused -> %s" % (len(tnp.STYLES), tot, un, OUT))


if __name__ == "__main__":
    main()
