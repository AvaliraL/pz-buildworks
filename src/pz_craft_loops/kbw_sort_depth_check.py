"""Simulate Kahlua's table.sort (stdlib.lua quicksort, first-element pivot, left side non-tail)
on KBW's registry order (= definition registration order, LinkedHashMap) and report max depth."""
import json, os, sys, glob
sys.setrecursionlimit(100000)

WS = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600"
MODS = [
    os.path.join(WS, "3772269882", "mods", "KnoxBuildworks", "42"),
    os.path.join(WS, "3772269882", "mods", "KnoxBuildworksVanillaExpanded", "42"),
]


def find_mod(mid):
    for p in glob.glob(os.path.join(WS, "*", "mods", "*", "42", "mod.info")) + \
             glob.glob(os.path.join(WS, "*", "mods", "*", "mod.info")):
        try:
            if ("id=%s" % mid) in open(p, encoding="utf-8", errors="replace").read().splitlines():
                return os.path.dirname(p)
        except OSError:
            pass
    return None


def ids_of(mod42):
    out = []
    man = os.path.join(mod42, "media", "KnoxBuildworks", "manifest.json")
    if not os.path.isfile(man):
        return out
    for rel in json.load(open(man, encoding="utf-8")).get("definitions", []):
        p = os.path.join(mod42, rel)
        if os.path.isfile(p):
            d = json.load(open(p, encoding="utf-8"))
            out += [b["id"] for b in d.get("buildables", []) if isinstance(b, dict) and b.get("id")]
    return out


def depth(lst):
    best = [0]

    def qs(t, left, right, d):
        while right > left:                      # right side is a tail call: loop
            best[0] = max(best[0], d)
            pval = t[left]
            t[left], t[right] = t[right], pval
            store = left
            for v in range(left, right):
                if t[v] < pval:
                    t[v], t[store] = t[store], t[v]
                    store += 1
            t[store], t[right] = t[right], t[store]
            qs(t, left, store - 1, d + 1)        # non-tail recursion
            left = store + 1
    qs(list(lst), 0, len(lst) - 1, 1)
    return best[0]


def registry(mod_dirs):
    seen, order = set(), []
    for m in mod_dirs:
        for i in ids_of(m):
            if i not in seen:
                seen.add(i); order.append(i)
    return order


if __name__ == "__main__":
    kbw = [m for m in MODS if os.path.isdir(m)]
    if len(kbw) < 2:
        kbw = [find_mod("KnoxBuildworks"), find_mod("KnoxBuildworksVanillaExpanded")]
    test = r"C:\Users\josep\Zomboid\Workshop\TikiTownCommunityTest\Contents\mods\TikiTownCommunityTest\42"
    core = registry(kbw)
    full = registry(kbw + [test])
    print("KBW core+VE: %d ids, depth %d" % (len(core), depth(core)))
    print("+ test bundle (current): %d ids, depth %d" % (len(full), depth(full)))
    no_new = [i for i in full if ".lowerwall." not in i and ".walloverlay." not in i]
    print("  without lower walls / overlays: %d ids, depth %d" % (len(no_new), depth(no_new)))
    only_ov = [i for i in full if ".lowerwall." not in i]
    print("  without lower walls only: %d ids, depth %d" % (len(only_ov), depth(only_ov)))
    print("  fully shuffled-sorted reference (ascending): depth %d" % depth(sorted(full)))

    tb = ids_of(test)
    print("test bundle alone, file order: depth %d | sorted: depth %d" % (depth(tb), depth(sorted(tb))))
    full_sorted_tb = registry(kbw) + [i for i in sorted(tb) if i not in set(core)]
    print("KBW+VE + test bundle written in id order: %d ids, depth %d" % (len(full_sorted_tb), depth(full_sorted_tb)))
    # the shipped WE setup: KBW + VE + our TikiTown submod (work copy) + Community submod (work copy)
    W = r"c:\Users\josep\Kiro\zomboid\WE_submods\work"
    subs = [os.path.join(W, "World Essentials - Community Buildworks", "42"),
            os.path.join(W, "World Essentials - TikiTown Buildworks", "42")]
    we = registry(kbw + subs)
    print("KBW+VE + WE Community + TikiTown submods (file order): %d ids, depth %d" % (len(we), depth(we)))
    we_sorted = registry(kbw) + [i for s in subs for i in sorted(ids_of(s))]
    print("  same, each submod file set in id order: depth %d" % depth(we_sorted))
    for s in subs:
        ids = ids_of(s)
        print("  %s: %d ids, depth alone %d" % (os.path.basename(os.path.dirname(s)), len(ids), depth(ids)))

    import hashlib
    hk = lambda i: hashlib.md5(i.encode("utf-8")).hexdigest()
    tb_sh = registry(kbw) + [i for i in sorted(tb, key=hk) if i not in set(core)]
    print("KBW+VE + test bundle in md5(id) order: depth %d" % depth(tb_sh))
    we_sh = registry(kbw) + [i for s in subs for i in sorted(ids_of(s), key=hk)]
    print("KBW+VE + WE submods, each in md5(id) order: depth %d" % depth(we_sh))
    # stress: core in its real order + 3x our content (future growth)
    big = registry(kbw) + sorted(tb + [x + ".dup%d" % k for k in range(2) for x in tb], key=hk)
    print("growth check, %d ids in md5 order: depth %d" % (len(big), depth(big)))

    # targeted: only files 39 / 40 (new, no WE baseline) written in md5(id) order
    def tgt(ids):
        new = [i for i in ids if ".lowerwall." in i or ".walloverlay." in i]
        old = [i for i in ids if i not in set(new)]
        return old + sorted(new, key=hk)     # 39/40 load last in our manifests
    print("TARGETED 39/40 md5 order -> test bundle registry depth %d" % depth(registry(kbw) + [i for i in tgt(tb) if i not in set(core)]))
    print("TARGETED 39/40 md5 order -> WE submods registry depth %d" % depth(registry(kbw) + [i for s in subs for i in tgt(ids_of(s))]))
