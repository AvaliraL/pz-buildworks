"""Refresh zomboid/WE_submods/upstream (and reset work) to the installed WE version (2026-10-31 update)."""
import os, shutil, datetime
WE = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600\3733324672\mods"
DEST = r"c:\Users\josep\Kiro\zomboid\WE_submods"
SUBMODS = ["World Essentials - Community Buildworks", "World Essentials - TikiTown Buildworks"]
BASE_FILES = [r"42\media\lua\client\KBWCommunity_Destroyable.lua", r"42\media\lua\shared\KBWCommunity_MultiStorey.lua",
              r"42\media\lua\shared\KBWCommunity_TableTop.lua", r"42\media\lua\shared\KBWCommunity_TVScreens.lua",
              r"42\media\lua\shared\KBWCommunity_Viewscreens.lua", r"42\media\lua\shared\WorldEssentialsCommunityGrid.lua",
              r"42\media\lua\shared\WorldEssentialsCommunitySprites.lua", r"42\media\lua\shared\WorldEssentialsCommunitySpriteIds.lua",
              r"42\media\lua\shared\WorldEssentialsCommunityLegacyIds.lua", r"42\media\lua\shared\WorldEssentialsCommunityAssetHealth.lua",
              r"42\media\lua\client\Patches\WorldEssentialsReadIcons.lua"]
out = []
# keep the previous snapshot for reference
old = os.path.join(DEST, "upstream")
prev = os.path.join(DEST, "upstream_2026-10-30")
if os.path.isdir(old) and not os.path.isdir(prev):
    shutil.copytree(old, prev); out.append("kept previous snapshot -> %s" % prev)
for kind in ("upstream", "work"):
    root = os.path.join(DEST, kind)
    if os.path.isdir(root): shutil.rmtree(root)
    for sm in SUBMODS:
        shutil.copytree(os.path.join(WE, sm), os.path.join(root, sm))
    for rel in BASE_FILES:
        s = os.path.join(WE, "World Essentials", rel)
        if os.path.isfile(s):
            d = os.path.join(root, "World Essentials (base, our files only)", rel)
            os.makedirs(os.path.dirname(d), exist_ok=True); shutil.copy2(s, d)
    s = os.path.join(WE, "World Essentials - Knox Buildworks Expansion", "42", "media", "lua", "shared", "WorldEssentialsKnoxTikitown.lua")
    d = os.path.join(root, "World Essentials - Knox Buildworks Expansion (our files only)", "42", "media", "lua", "shared", "WorldEssentialsKnoxTikitown.lua")
    os.makedirs(os.path.dirname(d), exist_ok=True); shutil.copy2(s, d)
    out.append("refreshed %s" % root)
stamp = datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(WE, "World Essentials - Community Buildworks", "42", "mod.info")))
open(os.path.join(DEST, "UPSTREAM_VERSION.txt"), "w", encoding="utf-8").write(
    "upstream/ = untouched copy of World Essentials (Workshop 3733324672), Community submod dated %s\n"
    "work/     = our working copy (reset to upstream on refresh). Diff against upstream/ for hand-offs.\n"
    "upstream_2026-10-30/ = the previous snapshot (before WE's isolated Dylan assets).\n"
    "Never edit the Steam copy.\n" % stamp)
open(r"c:\Users\josep\Kiro\pz_craft_loops\_refresh.txt", "w").write("\n".join(out))
