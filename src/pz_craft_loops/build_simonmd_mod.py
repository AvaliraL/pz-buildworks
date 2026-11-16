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

    import name_tooltip_pass
    from kbw_sort_order import md5_order
    tooltips, report, built, manifest, seen = {}, [], [], [], set()
    for fn in SRC_FILES:
        doc = json.load(open(os.path.join(SRC_DIR, fn), encoding="utf-8"))
        kept = [b for b in doc["buildables"] if b["id"] not in seen]
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
    try:
        we_sync.sync_to_we_work(mod_root, SUBMOD, out)
    except Exception as e:
        out.append("WARN: WE work sync failed: %r" % (e,))
    out.append("translations: %d names, %d tooltips" % (len(ig), len(tooltips)))
    open(LOG, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("done", len(built), "buildables,", len(manifest), "defs")


if __name__ == "__main__":
    main()
