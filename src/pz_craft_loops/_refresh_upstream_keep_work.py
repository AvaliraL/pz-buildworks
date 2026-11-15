"""Refresh zomboid/WE_submods/upstream to the installed World Essentials WITHOUT touching work/
(2026-11-14: WE merged most of our hand-offs; work/ holds the rest, so it must not be reset).
The old snapshot is kept as upstream_<date of the old baseline>/. For the base and Expansion folders,
upstream tracks the same file list as before plus any file work/ tracks there."""
import os, shutil, sys
WE = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600\3733324672\mods"
D = r"c:\Users\josep\Kiro\zomboid\WE_submods"
# the previous snapshot is kept as upstream_<date>; pass the date of the baseline being replaced
KEEP_AS = os.path.join(D, "upstream_" + (sys.argv[1] if len(sys.argv) > 1 else "2026-11-10"))
FULL = ["World Essentials - Community Buildworks", "World Essentials - TikiTown Buildworks"]
PARTIAL = {"World Essentials (base, our files only)": "World Essentials",
           "World Essentials - Knox Buildworks Expansion (our files only)": "World Essentials - Knox Buildworks Expansion"}
up = os.path.join(D, "upstream")
out = []
if os.path.isdir(KEEP_AS):
    sys.exit("refusing: %s already exists" % KEEP_AS)
shutil.copytree(up, KEEP_AS)
out.append("kept old snapshot -> %s" % KEEP_AS)


def rels(root):
    s = set()
    if os.path.isdir(root):
        for dp, _dn, fn in os.walk(root):
            for f in fn:
                s.add(os.path.relpath(os.path.join(dp, f), root))
    return s


for sm in FULL:
    shutil.rmtree(os.path.join(up, sm))
    shutil.copytree(os.path.join(WE, sm), os.path.join(up, sm))
    out.append("copied %s (%d files)" % (sm, len(rels(os.path.join(up, sm)))))
for ours, inst in PARTIAL.items():
    tracked = rels(os.path.join(KEEP_AS, ours)) | rels(os.path.join(D, "work", ours))
    shutil.rmtree(os.path.join(up, ours), ignore_errors=True)
    n = 0
    for rel in sorted(tracked):
        s = os.path.join(WE, inst, rel)
        if os.path.isfile(s):
            d = os.path.join(up, ours, rel)
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(s, d)
            n += 1
        else:
            out.append("   not in WE (ours only): %s/%s" % (ours, rel))
    out.append("copied %d tracked files for %s" % (n, ours))
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "_refresh_keep_work.txt"), "w", encoding="utf-8").write("\n".join(out))
print("\n".join(out))
