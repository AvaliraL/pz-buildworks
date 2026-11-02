# -*- coding: utf-8 -*-
"""One-off (re-runnable): vendor World Essentials' isolated Dylan assets into the project.

WE (not us) isolated the Dylan sprites the Community submod uses into its own WECommunity_*
tilesets (tiledef 8182) so Fort Waterfront's different dylanstiles layout can't shift them.
WE generated them with its own tools/build-community-isolated-assets.py (not in our tree), so we
copy them verbatim from the upstream snapshot. Re-run after refreshing upstream/ if WE changes them.
"""
import os, re, shutil, hashlib

UP = r"c:\Users\josep\Kiro\zomboid\WE_submods\upstream"
SUB = os.path.join(UP, "World Essentials - Community Buildworks")
BASE_LUA = os.path.join(UP, "World Essentials (base, our files only)", "42", "media", "lua", "shared",
                        "WorldEssentialsCommunitySprites.lua")
DST = r"c:\Users\josep\Kiro\zomboid\communitytilepack\vendor_we"

os.makedirs(DST, exist_ok=True)
log = []
for rel in (r"42\media\wecommunity_dylan.tiles", r"42\media\texturepacks\WECommunityDylan.pack"):
    src = os.path.join(SUB, rel)
    shutil.copy2(src, os.path.join(DST, os.path.basename(rel)))
    log.append("copied %s (%s)" % (rel, hashlib.sha1(open(src, "rb").read()).hexdigest()[:10]))
shutil.copy2(BASE_LUA, os.path.join(DST, "WorldEssentialsCommunitySprites.lua"))

# tileGeometry: keep only WE's WECommunity_* tileset blocks (between the header and the final '}').
tg = open(os.path.join(SUB, "common", "media", "tileGeometry.txt"), encoding="utf-8").read()
start = tg.index("tileset")
end = tg.rstrip().rfind("}")
inner = tg[start:end].rstrip() + "\n"
names = re.findall(r"name = (\w+),", inner)
assert names and all(n.startswith("WECommunity_") for n in names), names
open(os.path.join(DST, "tileGeometry_WECommunity.txt"), "w", encoding="utf-8").write(inner)
log.append("tileGeometry blocks: %s" % names)

m = dict(re.findall(r'\["([^"]+)"\]="([^"]+)"', open(BASE_LUA, encoding="utf-8").read()))
assert all(v == "WECommunity_" + k for k, v in m.items())
log.append("sprite map entries: %d (all plain WECommunity_ prefix)" % len(m))
open(os.path.join(DST, "VENDORED.txt"), "w", encoding="utf-8").write(
    "Copied verbatim from World Essentials (upstream snapshot). Do not edit; re-run "
    "pz_craft_loops/_vendor_we_dylan.py after an upstream refresh.\n" + "\n".join(log) + "\n")
print("\n".join(log))
