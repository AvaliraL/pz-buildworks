# -*- coding: utf-8 -*-
"""Build the Raven Creek Knox Buildworks submod: "World Essentials - Raven Creek Buildworks", mod id
RavenCreekKBW (user, 2026-11-15; first built 2026-11-14 as "Simon MD Buildworks" / SimonMDKBW). Buildables
on Raven Creek's tiles (RavenCreek_B42: its RCBucho sheets and its LCB42_SimonMDsTiles copy of Simon MD).
Gated by require=RavenCreek_B42, so none of it shows up without Raven Creek.

Like build_tikitown_mod.py: definitions from zomboid/simonmd/*.json (SRC_FILES), names + tooltips
from name_tooltip_pass, translation tables built from the definitions, canonical build in the
project (zomboid/simonmd/mod_build, never Zomboid\\Workshop), then synced into
zomboid/WE_submods/work/<submod>/ by we_sync. This is a NEW submod: its work folder and mod.info are
created here the first time (proposed to the WE dev; after that mod.info is WE-owned like the others).
"""
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SRC_DIR = r"c:\Users\josep\Kiro\zomboid\simonmd"
SRC_FILES = [
    "01_simonmd_fencing.json",    # simonmd_fencing.py
    "02_simonmd_doors.json",      # simonmd_doors_furniture.py (2026-11-16)
    "03_simonmd_furniture.json",  # simonmd_doors_furniture.py (2026-11-16): containers, "reinforce"
    "04_simonmd_barricades.json", # simonmd_barricades.py (2026-11-16): heavy barrier fences, low barriers
    "05_simonmd_countertops.json", # simonmd_countertops.py (2026-11-17): marble tops built onto counters
    "06_simonmd_furniture2.json",  # simonmd_furniture2.py (2026-11-17): tables, in-wall / wine / sloped shelves
    "07_simonmd_decor.json",       # simonmd_furniture2.py (2026-11-17): speakers, cart, statues, figures, posters
    "08_simonmd_floor_wedges.json",  # simonmd_furniture2.py (2026-11-17): half-square floor overlays
    "09_simonmd_planters.json",      # simonmd_furniture2.py (2026-11-17): planter beds, boxes, plants, flowers
]
# 2026-11-15 (user): the submod covers all of Raven Creek's tiles (RCBucho + its Simon MD copy), and it
# stays gated on Raven Creek: require=RavenCreek_B42 means it can't be enabled without it, so its
# buildables never show up as blank entries. WE had merged the fencing into Knox Buildworks Expansion
# (35_simonmd_fencing.json, no gate); the hand-off asks to move it back here. Buildable ids stay
# worldessentials.simonmd.* so fences already built keep their link.
MOD_ID = "RavenCreekKBW"
SUBMOD = "World Essentials - Raven Creek Buildworks"
OLD_SUBMODS = ["World Essentials - Simon MD Buildworks"]    # earlier name of this work folder
REQUIRES = ["WorldEssentials", "KnoxBuildworks", "KnoxBuildworksVanillaExpanded", "RavenCreek_B42"]
UPLOAD_ROOT = r"c:\Users\josep\Kiro\zomboid\simonmd\mod_build"
LOG = r"c:\Users\josep\Kiro\pz_craft_loops\_simonmdmod.txt"
MODINFO = [
    "name=%s" % SUBMOD,
    "id=%s" % MOD_ID,
    "description=Knox Buildworks buildables for Raven Creek's tiles (its RCBucho sheets and its copy of "
    "Simon MD's tiles). Bundled World Essentials submod; requires Knox Buildworks, Knox Buildworks Vanilla "
    "Expanded and Raven Creek, so nothing shows up without Raven Creek.",
    "require=%s" % ",".join(REQUIRES),
    "loadModAfter=%s" % ",".join(REQUIRES),
    "versionMin=42.0",
    "tags=Build 42,Build",
]
# our own small tileset (gun rack copies without `solid`; simonmd_doors_furniture.py, 2026-11-16)
import simonmd_doors_furniture as _sdf   # noqa: E402
MODINFO += _sdf.modinfo_lines()


def main():
    out = []
    up = os.path.join(UPLOAD_ROOT, MOD_ID)
    if os.path.isdir(up):
        shutil.rmtree(up)
    mod_root = os.path.join(up, "Contents", "mods", MOD_ID)
    mod42 = os.path.join(mod_root, "42")
    defs_dir = os.path.join(mod42, "media", "KnoxBuildworks", "definitions")
    tr_dir = os.path.join(mod42, "media", "lua", "shared", "Translate", "EN")
    os.makedirs(defs_dir)
    os.makedirs(tr_dir)
    os.makedirs(os.path.join(mod_root, "common"))
    open(os.path.join(mod42, "mod.info"), "w", encoding="utf-8").write("\n".join(MODINFO) + "\n")
    out.append("  tile copies: %d (%s)" % (_sdf.write_copy_assets(os.path.join(mod42, "media"),
                                                                  os.path.join(mod_root, "common", "media")),
                                           _sdf.COPY_TILESET))
    _sdf.write_overlay_lua(os.path.join(mod42, "media", "lua", "server", "Items", _sdf.OVERLAY_LUA_NAME))
    # counter-top callbacks: shared, KBW resolves onIsValid / onCreate on both sides
    import simonmd_countertops as _sct
    _sct.write_lua(os.path.join(mod42, "media", "lua", "shared", _sct.LUA_NAME))
    # raised table-top figures keep their height on load / pick-up (own copy of the Community fix)
    import simonmd_furniture2 as _sf2
    _sf2.write_tabletop_lua(os.path.join(mod42, "media", "lua", "shared", _sf2.TABLETOP_LUA_NAME))
    _sf2.write_placement_lua(os.path.join(mod42, "media", "lua", "shared", _sf2.PLACEMENT_LUA_NAME))
    _sf2.write_neon_link_lua(os.path.join(mod42, "media", "lua", "shared", _sf2.NEON_LINK_LUA_NAME))
    out.append("  depth matches: %s" % ", ".join("%d=%s (%.2f)" % (c, n, s) for c, (n, s) in sorted(_sdf.DEPTH_MATCH.items())))

    import name_tooltip_pass
    from kbw_sort_order import md5_order
    tooltips, report, built, manifest, seen = {}, [], [], [], set()
    for fn in SRC_FILES:
        doc = json.load(open(os.path.join(SRC_DIR, fn), encoding="utf-8"))
        kept = [b for b in doc["buildables"] if b["id"] not in seen]
        # reinforced containers: military-crate cost, capacity 100 (counter_variants.py; the
        # "reinforce" tag, as in the Community / TikiTown builders)
        import counter_variants
        n_rf = counter_variants.add_variants(kept)
        if n_rf:
            out.append("  reinforced variants added in %s: %d" % (fn, n_rf))
        seen.update(b["id"] for b in kept)
        name_tooltip_pass.apply(kept, tooltips, report)
        doc["buildables"] = kept
        md5_order(doc["buildables"])
        json.dump(doc, open(os.path.join(defs_dir, fn), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        manifest.append("media/KnoxBuildworks/definitions/%s" % fn)
        built += kept
        out.append("  %4d  %s" % (len(kept), fn))
    json.dump({"schemaVersion": 1, "definitions": manifest},
              open(os.path.join(mod42, "media", "KnoxBuildworks", "manifest.json"), "w", encoding="utf-8"))
    # translations straight from the definitions (piece names + card titles) and our tooltip texts
    ig = {}
    for b in built:
        if b.get("translationKey"):
            ig[b["translationKey"]] = b["displayName"]
        g = b.get("group") or {}
        if g.get("translationKey") and g.get("name"):
            ig[g["translationKey"]] = g["name"]
    json.dump(ig, open(os.path.join(tr_dir, "IG_UI.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    from tooltip_fix import fix_table
    tooltips, _rep = fix_table(tooltips)
    json.dump(tooltips, open(os.path.join(tr_dir, "Tooltip.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    # WE work copy: a new submod gets its folder + proposed mod.info once; later syncs leave it alone
    import we_sync
    work = os.path.join(we_sync.WORK, SUBMOD)
    for old in OLD_SUBMODS:     # our own generated folder under its earlier name (never shipped by WE)
        old_dir = os.path.join(we_sync.WORK, old)
        if os.path.isdir(old_dir) and not os.path.isdir(work):
            shutil.move(old_dir, work)
            shutil.copyfile(os.path.join(mod42, "mod.info"), os.path.join(work, "42", "mod.info"))
            out.append("renamed work submod %s -> %s (mod.info rewritten)" % (old, SUBMOD))
    if not os.path.isdir(work):
        os.makedirs(os.path.join(work, "42"))
        shutil.copyfile(os.path.join(mod42, "mod.info"), os.path.join(work, "42", "mod.info"))
        out.append("created new WE work submod %s (proposed mod.info)" % work)
    elif not os.path.isdir(os.path.join(we_sync.UPSTREAM, SUBMOD)):
        # WE doesn't ship this submod yet, so its mod.info is still ours: keep the proposal current
        shutil.copyfile(os.path.join(mod42, "mod.info"), os.path.join(work, "42", "mod.info"))
    try:
        we_sync.sync_to_we_work(mod_root, SUBMOD, out)
    except Exception as e:
        out.append("WARN: WE work sync failed: %r" % (e,))
    out.append("translations: %d names, %d tooltips" % (len(ig), len(tooltips)))
    open(LOG, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("done", len(built), "buildables,", len(manifest), "defs")


if __name__ == "__main__":
    main()
