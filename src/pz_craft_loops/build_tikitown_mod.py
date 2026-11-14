# -*- coding: utf-8 -*-
"""Build the OFFICIAL (non-test) TikiTown KBW mod, matching the Community-pack builder:
single accurate cost tier, real build-menu categories, no TEST routing. Built into the project
(zomboid/tikitown/mod_build) and synced into our WORK copy of World Essentials' bundled submod
(see the OUTPUT note at UPLOAD_ROOT below). The standalone Workshop item is retired.

Layout (mirrors KnoxCommunityTilepack / the TikiTown test bundle):
  <upload>/workshop.txt
  <upload>/PREVIEW_PLACEHOLDER.txt   (user supplies preview.png)
  <upload>/Contents/mods/<ModId>/42/mod.info
  <upload>/Contents/mods/<ModId>/42/media/KnoxBuildworks/manifest.json
  <upload>/Contents/mods/<ModId>/42/media/KnoxBuildworks/definitions/*.json
  <upload>/Contents/mods/<ModId>/42/media/lua/shared/Translate/EN/{IG_UI,Tooltip}.json

Dependencies: KnoxBuildworks + KnoxBuildworksVanillaExpanded + tikitown_tiles (Drazion's Tilepack).
No World Essentials dependency (see REQUIRES). Each buildable keeps its real category/subcategory/group.
This is the shippable counterpart to the TikiTownTestBundle (which routes everything into TEST tabs).

Policy: single mod worked from source (no TEST bundle), single accurate cost tier (no cheap variant).
Where a cheap/accurate pair exists, the ACCURATE file is used; single-tier files are used as-is.
"""
import json, os, shutil

SRC_DIR = r"c:\Users\josep\Kiro\zomboid\tikitown"

# One file per sheet. Use the *_accurate variant where a cheap/accurate pair exists
# (21,26,27,28,31,33,34); the rest are single-tier already.
SRC_FILES = [
    "21_tikitown_walls_accurate.json",
    "22_tikitown_doors.json",
    "23_tikitown_furniture.json",
    "24_tikitown_bookshelves.json",
    "25_tikitown_bedroom.json",
    "26_tikitown_glass_accurate.json",
    "27_tikitown_newburbs_interiors_accurate.json",
    "28_tikitown_newburbs_walls_accurate.json",
    "29_tikitown_garages.json",
    "30_tikitown_shelving.json",
    "31_tikitown_newburbs_roofs_accurate.json",
    "32_tikitown_newburbs_flags.json",
    "33_tikitown_newburbs_doors_accurate.json",
    "34_tikitown_newburbs_windows_accurate.json",
    "35_tikitown_newburbs_trim.json",
    "36_tikitown_tterika_storage.json",
    "37_tikitown_soundproof.json",
    "38_tikitown_props14.json",
    "39_tikitown_wall_overlays.json",
    "40_tikitown_lower_walls.json",
    "41_tikitown_roof_slope_walls.json",
    "42_tikitown_garage_trim.json",
    "43_tikitown_wall_paint_cladding.json",
    "44_tikitown_wall_trim.json",
    "45_tikitown_ladders.json",      # tterika ladder on our copied tiles (ladders.py)
    "46_tikitown_barrel_planters.json",   # tikitown_barrel_planters.py
    "47_tikitown_entertainment.json",     # tikitown_entertainment.py
    "48_tikitown_rugs.json",              # tikitown_rugs.py
    "49_tikitown_signs.json",             # tikitown_signs.py
]

# WE merge 2026-11-10: the WE dev declined these pending a multiplayer review. Not built for WE
# (definition, item scripts, icons, Rotate Lua, item names, Rotate label); the test bundle keeps them.
WE_HOLD_BACK_IDS = {"worldessentials.tikitown.props14_electrical_cabinet"}
WE_HOLD_BACK_IG_KEYS = {"IGUI_WETiki_props14_electrical_cabinet", "IGUI_KBWTikiTown_RotateGenerator"}

MOD_ID   = "TikiTownKBW"
MOD_NAME = "Knox Buildworks - Drazion's Tilepack (TikiTown)"
# Standalone: KBW core + VE (for kbwve.extended.* material groups) + the tile art.
# NO World Essentials. Verified: KBW core natively handles every JSON feature our
# buildables use (groups, roof slopes/faceByEdge, container:counter, knowledge gates,
# material groups); our defs contain zero WE-only callbacks. VE itself ships standalone
# on KBW the same way.
REQUIRES = ["KnoxBuildworks", "KnoxBuildworksVanillaExpanded", "tikitown_tiles"]

# The complete, pre-built translation tables (family + group + per-piece keys) live in the
# test bundle. The official mod ships the SAME tables so names/groups resolve identically.
TEST_TR_DIR = r"C:\Users\josep\Zomboid\Workshop\TikiTownTestBundle\Contents\mods\TikiTownTestBundle\42\media\lua\shared\Translate\EN"

# Namespace World Essentials used when it imported our 26-29 / 31-34 handoff files.
WE_HANDOFF_PREFIX = "worldessentials.tikitown.handoff."

# OUTPUT (2026-10-30): the standalone Workshop item 3828081863 is RETIRED. World Essentials ships
# this content as its bundled submod "World Essentials - TikiTown Buildworks" (same mod id
# TikiTownKBW). The canonical build goes to the PROJECT (never Zomboid\Workshop: a folder there
# with the same mod id shadows WE's copy and fails the server's Lua checksum), then is synced into
# zomboid/WE_submods/work/<submod> by we_sync.py (WE's mod.info / bundled_source.txt untouched).
UPLOAD_ROOT = r"c:\Users\josep\Kiro\zomboid\tikitown\mod_build"     # canonical build (project)
PROJECT_MIRROR = r"c:\Users\josep\Kiro\zomboid\tikitown\mod_upload"  # reference copy in project
LOG = r"c:\Users\josep\Kiro\pz_craft_loops\_tikitownmod.txt"

def main():
    out=[]
    up = os.path.join(UPLOAD_ROOT, MOD_ID)
    if os.path.isdir(up): shutil.rmtree(up)
    mod42 = os.path.join(up, "Contents", "mods", MOD_ID, "42")
    defs_dir = os.path.join(mod42, "media", "KnoxBuildworks", "definitions")
    tr_dir   = os.path.join(mod42, "media", "lua", "shared", "Translate", "EN")
    os.makedirs(defs_dir); os.makedirs(tr_dir)
    # seating fixes for Drazion's broken bed data (tterika double bed) -- see kbw_tilepatch
    import sys as _sys
    _sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from kbw_tilepatch import write_seating_lua
    from kbw_tilepatch import TT_TILEPATCH_NAME as _TT_PATCH_NAME, TT_TILEPATCH_ID as _TT_PATCH_ID
    import tikitown_wall_overlays as _two
    write_seating_lua(os.path.join(mod42, "media", "lua", "shared", "KBWCommunity_Seating.lua"))

    # mod.info
    mi=[
        "name=%s"%MOD_NAME,
        "id=%s"%MOD_ID,
        "description=Knox Buildworks buildables for Drazion's Tilepack (TikiTown). Standalone drop-in; "
        "requires Knox Buildworks, Knox Buildworks Vanilla Expanded, and Drazion's Tilepack. "
        "No World Essentials required.",
        "require=%s"%",".join(REQUIRES),
        "loadModAfter=%s"%",".join(REQUIRES),
        "versionMin=42.0",
        "tags=Build 42,Build",
        "tiledef=%s %d" % (_TT_PATCH_NAME, _TT_PATCH_ID),   # tterika_02 stacking / locker patch
    ] + _two.MODINFO_LINES                                   # copied wall-overlay tiles (8179)
    open(os.path.join(mod42,"mod.info"),"w",encoding="utf-8").write("\n".join(mi)+"\n")

    # definitions: copy each accurate/single-tier source verbatim (real categories preserved)
    manifest_defs=[]
    total=0; dupe_ids=[]; seen=set(); per_file={}; alias_count=[0]
    import name_tooltip_pass
    nt_tooltips={}; nt_report=[]; all_built=[]
    for fn in SRC_FILES:
        src=os.path.join(SRC_DIR, fn)
        doc=json.load(open(src, encoding="utf-8"))
        # held back from World Essentials until the WE dev's MP review (2026-11-10): the
        # Electrical Cabinet Generator. It stays in the test bundle (build_merged_test_mod).
        doc["buildables"]=[b for b in doc.get("buildables", []) if b.get("id") not in WE_HOLD_BACK_IDS]
        builds=doc.get("buildables", [])
        # reinforced counters: military-crate cost, capacity 100 (counter_variants.py)
        import counter_variants
        _cv=counter_variants.add_variants(builds)
        if _cv: out.append("reinforced counters added in %s: %d" % (fn, _cv))
        per_file[fn]=len(builds)
        # dedup ids defensively (should be none across distinct sheets)
        kept=[]
        for b in builds:
            bid=b.get("id")
            if bid in seen:
                dupe_ids.append(bid); continue
            seen.add(bid); kept.append(b)
            # World Essentials imported files 26-29 / 31-34 under its own namespace
            # (worldessentials.tikitown.handoff.<our id>). Objects already built from WE's copy
            # carry that id; a KBW alias (Registry.lua resolves entries[aliases[id]]) keeps them
            # resolving to our definition once WE removes its copy. Ids in 21-25/30 are identical
            # in both mods and need no alias.
            if bid and bid.startswith("tikitown."):
                al=b.setdefault("aliases", [])
                legacy=WE_HANDOFF_PREFIX+bid
                if legacy not in al:
                    al.append(legacy); alias_count[0]+=1
        doc["buildables"]=kept
        # name + tooltip pass (see name_tooltip_pass.py)
        name_tooltip_pass.apply(kept, nt_tooltips, nt_report)
        all_built.extend(kept)
        total+=len(kept)
        # Normalize output filename (drop the _accurate suffix so the shipped name is clean)
        out_fn=fn.replace("_accurate","")
        from kbw_sort_order import md5_order
        md5_order(doc["buildables"])   # keeps KBW's registry sort shallow (kbw_sort_order.py)
        json.dump(doc, open(os.path.join(defs_dir,out_fn),"w",encoding="utf-8"),
                  indent=1, ensure_ascii=False)
        manifest_defs.append("media/KnoxBuildworks/definitions/%s"%out_fn)

    # manifest
    json.dump({"schemaVersion":1,"definitions":manifest_defs},
              open(os.path.join(mod42,"media","KnoxBuildworks","manifest.json"),"w",encoding="utf-8"))

    # Runtime Lua (pick up / place, multi-part, overlay guard, table-top, stage info): since the WE
    # merge of 2026-11-10 World Essentials ships ONE consolidated copy of each in its base folder
    # (WorldEssentialsBuildworksPickup / MultiPart / OverlayGuard / StageInfo.lua, and the TikiTown
    # table-top fix inside KBWCommunity_TableTop.lua). Our per-submod copies are no longer built for
    # WE; changes to that code are ported by hand into work/World Essentials (base, our files only).
    # The test bundle (build_merged_test_mod) still writes its own copies.
    _lua = os.path.join(mod42, "media", "lua")
    # ladders must hang on a wall (onIsValid used by 45_tikitown_ladders.json; ladders.py)
    from ladders import write_ladder_guard_lua, GUARD_LUA_TIKITOWN
    write_ladder_guard_lua(os.path.join(_lua, "shared", GUARD_LUA_TIKITOWN))
    # wall overlays: our own copies of tiles 72-91 (overlay-only props) -- map tiles untouched
    from tikitown_wall_overlays import write_overlay_assets
    # corner / end-cap depth maps go to <mod>/common/media (the only place the game reads them)
    write_overlay_assets(os.path.join(mod42, "media"), os.path.join(os.path.dirname(mod42), "common", "media"))
    # Electrical Cabinet Generator assets (item scripts, icons, Rotate Lua, item names): held back
    # from WE (see WE_HOLD_BACK_IDS); the test bundle builds them.
    # tterika_02 tile-property patch (footlocker stacks 6, small cabinets 2, freestanding lockers)
    # plus the runtime removal of IsTableTop that an additive patch cannot do. Own tiledef; WE adds
    # the tiledef line to its (WE-owned) mod.info.
    from kbw_tilepatch import (write_community_tilepatch, write_removal_lua,
                               TT_TILEPATCH_NAME)
    write_community_tilepatch(os.path.join(mod42, "media", TT_TILEPATCH_NAME + ".tiles"), tikitown_only=True)
    write_removal_lua(os.path.join(_lua, "shared", "KBWTikiTown_TileFixes.lua"), tikitown_only=True)
    import rotation_fix
    _rot, _rot_rep = rotation_fix.build_offsets(all_built, rotation_fix.load_sheets())
    rotation_fix.write_rotation_lua(os.path.join(_lua, "shared", "KBWTikiTown_Rotation.lua"), _rot)
    out.append("rotation: fixed %d pieces (%d sprites), engine already rotates %d; skipped %s" % (
        _rot_rep["fixed"], len(_rot), _rot_rep["already"],
        {k: len(v) for k, v in _rot_rep["skipped"].items()}))

    # translations: ship the complete pre-built tables from the test bundle
    tr_copied=[]
    for tf in ("IG_UI.json","Tooltip.json"):
        src=os.path.join(TEST_TR_DIR, tf)
        if os.path.isfile(src):
            shutil.copyfile(src, os.path.join(tr_dir, tf)); tr_copied.append(tf)
        else:
            # fallback: emit a thin per-piece table from the buildables we shipped
            pass
    # names: definitions are the source of truth (the copied table had stale names, e.g. every
    # garage door "(2 Wide)"); group card titles and other keys are kept from the table
    _ig_path=os.path.join(tr_dir, "IG_UI.json")
    _ig=json.load(open(_ig_path, encoding="utf-8")) if os.path.isfile(_ig_path) else {}
    _ig_changed=0
    for b in all_built:
        tk=b.get("translationKey"); dn=b.get("displayName")
        if tk and dn and _ig.get(tk)!=dn:
            _ig[tk]=dn; _ig_changed+=1
    # group card titles: the definitions win here too (naming pass 2026-11-08 renamed groups; the
    # copied table matched the definitions exactly before that, 0 of 710 differing)
    for b in all_built:
        g=b.get("group") or {}
        if g.get("translationKey") and g.get("name") and _ig.get(g["translationKey"])!=g["name"]:
            _ig[g["translationKey"]]=g["name"]; _ig_changed+=1
    for _k in WE_HOLD_BACK_IG_KEYS:                # generator held back from WE
        _ig.pop(_k, None)
    json.dump(_ig, open(_ig_path,"w",encoding="utf-8"), indent=1, ensure_ascii=False)
    # tooltips: only our type keys now (the old per-piece keys just repeated the name; KBW-owned
    # keys are never shipped -- tooltip_fix still guards that)
    from tooltip_fix import fix_table
    nt_tooltips, _tt_rep = fix_table(nt_tooltips)
    json.dump(nt_tooltips, open(os.path.join(tr_dir,"Tooltip.json"),"w",encoding="utf-8"), indent=1, ensure_ascii=False)
    out.append("name/tooltip pass: %d renames, %d IG_UI names updated, %d tooltip keys; fix: %s"
               % (len(nt_report), _ig_changed, len(nt_tooltips), _tt_rep))
    out.extend("   "+r for r in nt_report)

    # workshop.txt -- published item: https://steamcommunity.com/sharedfiles/filedetails/?id=3828081863
    wt=["version=1","id=3828081863","title=%s"%MOD_NAME,
        "description=Knox Buildworks buildables for Drazion's Tilepack (TikiTown). Standalone drop-in.",
        "description=",
        "description=Requires Knox Buildworks, Knox Buildworks Vanilla Expanded, and Drazion's Tilepack. No World Essentials required.",
        "tags=Build 42;Building","visibility=private"]
    open(os.path.join(up,"workshop.txt"),"w",encoding="utf-8").write("\n".join(wt)+"\n")
    # preview.png: reuse the TikiTown test-bundle preview (our own file) as a stand-in so the
    # item is upload-ready; swap for a bespoke image later. Falls back to a placeholder note.
    prev_src=r"C:\Users\josep\Zomboid\Workshop\TikiTownTestBundle\preview.png"
    if os.path.isfile(prev_src):
        shutil.copyfile(prev_src, os.path.join(up,"preview.png"))
    else:
        open(os.path.join(up,"PREVIEW_PLACEHOLDER.txt"),"w",encoding="utf-8").write(
            "Add a preview.png here before uploading to the Workshop.\n")

    # project mirror
    if os.path.isdir(PROJECT_MIRROR): shutil.rmtree(PROJECT_MIRROR)
    shutil.copytree(up, PROJECT_MIRROR)

    out.append("OFFICIAL TikiTown mod -> %s"%up)
    out.append("definition files: %d"%len(manifest_defs))
    out.append("total buildables: %d"%total)
    out.append("duplicate ids skipped: %d"%len(dupe_ids))
    out.append("WE legacy aliases added: %d"%alias_count[0])
    out.append("translations copied from test bundle: %s"%(", ".join(tr_copied) or "NONE (fallback)"))
    out.append("")
    out.append("per source file:")
    for fn in SRC_FILES:
        out.append("  %5d  %s"%(per_file[fn], fn))
    out.append("")
    from we_sync import sync_to_we_work, TIKITOWN_SUBMOD
    try:
        sync_to_we_work(os.path.join(up, "Contents", "mods", MOD_ID), TIKITOWN_SUBMOD, out)
    except Exception as e:
        out.append("WARN: WE work sync failed: %r" % (e,))
    out.append("")
    out.append("upload tree:")
    for dp,dn,fns in os.walk(up):
        for f in fns:
            out.append("   %s"%os.path.join(dp,f).replace(up,""))
    open(LOG,"w",encoding="utf-8").write("\n".join(out))
    print("done", total, "buildables,", len(manifest_defs), "defs")

if __name__=="__main__":
    main()
