"""Apply tooltip_fix to the WE WORK copies in place, then list every file that now differs from
upstream (= what to hand the WE dev). Never touches the Steam copy."""
import os, hashlib, json
from tooltip_fix import fix_file, kbw_owned_keys
WORK = r"c:\Users\josep\Kiro\zomboid\WE_submods\work"
UP = r"c:\Users\josep\Kiro\zomboid\WE_submods\upstream"
out = []
kbw = kbw_owned_keys()
out.append("KBW-owned tooltip keys known: %d" % len(kbw))
for sub in ("World Essentials - Community Buildworks", "World Essentials - TikiTown Buildworks"):
    p = os.path.join(WORK, sub, "42", "media", "lua", "shared", "Translate", "EN", "Tooltip.json")
    rep = fix_file(p, kbw)
    out.append("%s: %s" % (sub, rep))
    d = json.load(open(p, encoding="utf-8"))
    out.append("   now: %s" % {k: v for k, v in d.items() if k.startswith("Tooltip_KBW_")})
def sha(p): return hashlib.sha1(open(p, "rb").read()).hexdigest()
out.append("\nwork files differing from upstream:")
for d, _, fs in os.walk(WORK):
    for f in fs:
        w = os.path.join(d, f); rel = os.path.relpath(w, WORK); u = os.path.join(UP, rel)
        if not os.path.isfile(u) or sha(u) != sha(w):
            out.append("   " + rel)
open(r"c:\Users\josep\Kiro\pz_craft_loops\_patch_we.txt", "w", encoding="utf-8").write("\n".join(out))
