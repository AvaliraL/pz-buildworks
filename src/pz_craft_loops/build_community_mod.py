# -*- coding: utf-8 -*-
"""Build the standalone Community-pack KBW mod, mirroring the working TikiTown layout
(42/mod.info + 42/media/KnoxBuildworks/{manifest.json,definitions/*} +
42/media/lua/shared/Translate/EN/*):

  KnoxCommunityTilepack   (official / shippable; real KBW categories, single accurate cost tier)

Depends on KnoxBuildworks + KnoxBuildworksVanillaExpanded + the Community Tilepack
(UnofficialMappersCommunityTilePack). Only Community-pack buildables; no TikiTown tiles.

OUTPUT (2026-10-30): the standalone Workshop item 3828080624 is RETIRED. The content ships inside
World Essentials as the bundled submod "World Essentials - Community Buildworks". This builder:
  1. writes the canonical build to OUT_ROOT (zomboid/communitytilepack/mod/KnoxCommunityTilepack)
  2. syncs it into zomboid/WE_submods/work/World Essentials - Community Buildworks (we_sync.py),
     never touching WE-owned files (mod.info, bundled_source.txt, the runtime Lua WE moved into
     main World Essentials).
It no longer writes Zomboid\\Workshop or the subscribed Steam copy.

Policy: single mod worked from source (no TEST bundle), single accurate cost tier (no cheap variant).
"""
import json, os, shutil

SRC_DEFS = [
    r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables\35_community_dirkie_counters.json",
    r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables\40_community_dirkies_containers.json",
    r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables\41_community_dylan_containers.json",
    r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables\42_community_tk_containers.json",
    r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables\43_community_dirkies_walls.json",
    r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables\44_community_dylan_walls.json",
    r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables\45_community_tk_walls.json",
    # doors + gates (Dirkies 46 / Dylan 47 / TK 48): all confirmed in-game 2026-08-28
    r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables\46_community_dirkies_doors.json",
    r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables\47_community_dylan_doors.json",
    r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables\48_community_tk_doors.json",
    r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables\49_community_tk_dumpsters.json",
    r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables\50_community_dylan_futureroom.json",
    r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables\51_community_dylan_obs04_hedges.json",
    r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables\52_community_dylan_pitstop2_carpets.json",
    r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables\53_community_dylan_rf02_misc.json",
    r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables\54_community_dylan_blocktrasher_shelf.json",
    r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables\55_community_dirkies_secret_shelf.json",
    r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables\56_community_fears_workbenches.json",
    r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables\57_community_tk_kitchen_misc.json",
    r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables\58_community_fears_rp.json",
    r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables\59_community_dirkies_fencing.json",
]
OUT_ROOT = r"c:\Users\josep\Kiro\zomboid\communitytilepack\mod"

COMMUNITY_TILES_ID = "UnofficialMappersCommunityTilePack"
REQUIRES = ["KnoxBuildworks", "KnoxBuildworksVanillaExpanded", COMMUNITY_TILES_ID]

import sys as _sys
_sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kbw_tilepatch import (write_community_tilepatch, write_removal_lua, write_tv_screen_lua,
                           write_tv_screen_assets, SCREEN_TILESET, SCREEN_TILEDEF_NAME, SCREEN_TILEDEF_ID,
                           write_destroy_lua, write_viewscreen_assets, add_viewscreen_north_faces,
                           write_viewscreen_lua, write_fears_assets, write_tabletop_lua, write_multistorey_lua,
                           VIEWSCREEN_PACK, VIEWSCREEN_TILEDEF_NAME, VIEWSCREEN_TILEDEF_ID,
                           FEARS_PACK, FEARS_TILEDEF_NAME, FEARS_TILEDEF_ID,
                           TILEPATCH_NAME as _TV_PATCH_NAME, TILEPATCH_ID as _TV_PATCH_ID)
from kbw_tilepatch import (write_cases_assets, add_case_mirror_faces,
                           CASES_PACK, CASES_TILEDEF_NAME, CASES_TILEDEF_ID)
import we_dylan
import name_tooltip_pass
WE_DYLAN_REPORT = []
NT_REPORT = []
# Back-compat alias so existing call sites keep working.
_write_tv_tiledef = write_community_tilepatch

def load_defs():
    docs=[]
    for p in SRC_DEFS:
        docs.append((os.path.basename(p), json.load(open(p,encoding="utf-8"))))
    return docs

def write_mod(mod_id, mod_name, description):
    """Write the mod tree (single official form, real categories)."""
    base=os.path.join(OUT_ROOT, mod_id)
    if os.path.isdir(base): shutil.rmtree(base)
    defs_dir=os.path.join(base,"42","media","KnoxBuildworks","definitions")
    tr_dir  =os.path.join(base,"42","media","lua","shared","Translate","EN")
    os.makedirs(defs_dir); os.makedirs(tr_dir)

    # mod.info
    # TV tiledef PATCH (v2): corrected per the working UsefulBarrelsMP precedent --
    #   * file is a *.patch.tiles in media/  (NOT media/tile_definitions/ -- that path is for the
    #     vanilla game's defs; mod .tiles load from media/)
    #   * registered on its OWN FREE tiledef id (8185), NOT the target pack's 6985 space
    #     (reusing 6985 caused "tiledef fileNumber 6985 used by more than one mod" + cascade)
    #   * the patch tileset keeps name "DylansRandomFurniture02" so it MERGES onto the pack's sheet
    # Adds signal=tv / IsoType=IsoTelevision / CustomItem to the four Wall Mounted TV tiles 36-39.
    mi=[
        "name=%s"%mod_name,
        "id=%s"%mod_id,
        "description=%s"%description,
        "require=%s"%",".join(REQUIRES),
        "loadModAfter=%s"%",".join(REQUIRES),
        "versionMin=42.0",
        "tags=Build 42,Build",
        "tiledef=%s %d"%(_TV_PATCH_NAME, _TV_PATCH_ID),
        "pack=%s"%SCREEN_TILESET,                          # generated wall-TV screen art
        "tiledef=%s %d"%(SCREEN_TILEDEF_NAME, SCREEN_TILEDEF_ID),
        "pack=%s"%VIEWSCREEN_PACK,                         # generated north-wall viewscreens
        "tiledef=%s %d"%(VIEWSCREEN_TILEDEF_NAME, VIEWSCREEN_TILEDEF_ID),
        "pack=%s"%FEARS_PACK,                              # generated Fears workbench orientations
        "tiledef=%s %d"%(FEARS_TILEDEF_NAME, FEARS_TILEDEF_ID),
        "pack=%s"%CASES_PACK,                              # generated military-case 2nd orientation
        "tiledef=%s %d"%(CASES_TILEDEF_NAME, CASES_TILEDEF_ID),
    ] + we_dylan.MODINFO_LINES                             # WE's isolated Dylan sprites (8182)
    open(os.path.join(base,"42","mod.info"),"w",encoding="utf-8").write("\n".join(mi)+"\n")
    # emit the TV patch .tiles into media/ (same dir layout as working tiledef mods)
    _media=os.path.join(base,"42","media"); os.makedirs(_media, exist_ok=True)
    write_tv_screen_assets(_media)
    write_viewscreen_assets(_media)
    # depth maps + tileGeometry load only from <mod>/common/media
    write_fears_assets(_media, os.path.join(base,"common","media"))
    write_cases_assets(_media, os.path.join(base,"common","media"))
    # WE's isolated Dylan sheets (vendored; see we_dylan.py). After write_fears_assets, which
    # creates common/media/tileGeometry.txt that the WECommunity blocks are merged into.
    we_dylan.install_assets(_media, os.path.join(base,"common","media"))
    _write_tv_tiledef(os.path.join(_media, _TV_PATCH_NAME+".tiles"))
    # runtime removal of collision flags the additive .patch.tiles merge cannot remove
    write_removal_lua(os.path.join(_media, "lua", "shared", "KBWCommunity_TileFixes.lua"))
    # vanilla screen overlays for the pack's TVs (pack has no screen art)
    write_tv_screen_lua(os.path.join(_media, "lua", "shared", "KBWCommunity_TVScreens.lua"))
    # sledgehammer destroy for our builds (vanilla blocks d_/e_/f_ sprites)
    write_destroy_lua(os.path.join(_media, "lua", "client", "KBWCommunity_Destroyable.lua"))
    # viewscreen image cycle (frosted -> Earth -> Mars); shared so the timed action exists server-side
    write_viewscreen_lua(os.path.join(_media, "lua", "shared", "KBWCommunity_Viewscreens.lua"))
    # counter-top appliance height (coffee makers / slicer on floor vs counter)
    write_tabletop_lua(os.path.join(_media, "lua", "shared", "KBWCommunity_TableTop.lua"))
    # two-storey wall pieces (top tile one level up) pass KBW's wall-support check
    write_multistorey_lua(os.path.join(_media, "lua", "shared", "KBWCommunity_MultiStorey.lua"))

    # definitions + translations
    manifest_defs=[]
    ig_ui={}; tooltip={}
    # 2026-10-30: Fort Waterfront B42 ships a different dylanstiles under the same tiledef 6985, so
    # the Dylan tile numbers shift on servers with both. We first excluded every Dylan buildable.
    # SUPERSEDED 2026-11-02: WE isolated the sprites as WECommunity_* (tiledef 8182); we now emit
    # those names (we_dylan.rename_buildable below), so the exclusion is off.
    EXCLUDE_DYLANSTILES = False
    dyl_sets = set()
    if EXCLUDE_DYLANSTILES:
        from kbw_tilepatch import _parse
        _dyl = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600\3628736763\mods\CommunityTilePack\common\media\dylanstiles.tiles"
        dyl_sets = {n.decode() for n in _parse(open(_dyl, "rb").read())[1]}
    def _uses_dyl(b):
        s = json.dumps(b)
        return any('"%s_' % t in s for t in dyl_sets)
    excluded = []
    dyl_renamed = [0]; dyl_unmapped = []
    for fname, doc in load_defs():
        d=json.loads(json.dumps(doc))  # deep copy
        if dyl_sets:
            keep = [b for b in d.get("buildables", []) if not _uses_dyl(b)]
            excluded += [b["id"] for b in d.get("buildables", []) if _uses_dyl(b)]
            d["buildables"] = keep
            if not keep:
                continue   # whole file was Dylan tiles: leave it out of the manifest
        
        for _b in d.get("buildables", []):
            add_viewscreen_north_faces(_b)   # generated north-wall viewscreen art
            add_case_mirror_faces(_b)        # generated 2nd orientation for the military cases
            _n, _miss = we_dylan.rename_buildable(_b)   # Dylan sprites -> WE's WECommunity_* copies
            dyl_renamed[0] += _n
            if _miss:
                dyl_unmapped.append((_b.get("id"), sorted(set(_miss))))
        # name + tooltip pass (fixed names, one-line type tooltips; see name_tooltip_pass.py)
        name_tooltip_pass.apply(d.get("buildables", []), tooltip, NT_REPORT)
        json.dump(d, open(os.path.join(defs_dir,fname),"w",encoding="utf-8"), indent=1, ensure_ascii=False)
        manifest_defs.append("media/KnoxBuildworks/definitions/%s"%fname)
        for b in d["buildables"]:
            tk=b.get("translationKey")
            if tk: ig_ui[tk]=b.get("displayName","")
            g=b.get("group") or {}
            if g.get("translationKey") and g.get("name") and g["translationKey"] not in ig_ui:
                ig_ui[g["translationKey"]]=g["name"]   # group card title
    # manifest
    json.dump({"schemaVersion":1,"definitions":manifest_defs},
              open(os.path.join(base,"42","media","KnoxBuildworks","manifest.json"),"w",encoding="utf-8"))
    # translations (simple key:value JSON, EN)
    json.dump(ig_ui,   open(os.path.join(tr_dir,"IG_UI.json"),"w",encoding="utf-8"), indent=1, ensure_ascii=False)
    # shared tooltip keys: never ship KBW-owned keys, generic text for ours (see tooltip_fix.py)
    from tooltip_fix import fix_table
    tooltip, _tt_rep = fix_table(tooltip)
    json.dump(tooltip, open(os.path.join(tr_dir,"Tooltip.json"),"w",encoding="utf-8"), indent=1, ensure_ascii=False)
    open(r"c:\Users\josep\Kiro\pz_craft_loops\_dyl_excluded.txt", "w", encoding="utf-8").write(
        "%d buildables excluded (dylanstiles sprites):\n%s\n" % (len(excluded), "\n".join(excluded)))
    # A Dylan sprite WE has no isolated copy of would render from the shared (shiftable) sheet,
    # or not at all. Fail the build rather than ship it; WE must regenerate its sheet first.
    if dyl_unmapped:
        raise RuntimeError("Dylan sprites missing from WE's WECommunity map: %r" % dyl_unmapped)
    WE_DYLAN_REPORT.append("Dylan sprite refs renamed to WECommunity_*: %d" % dyl_renamed[0])
    return base, len(manifest_defs)

OUT=open(r"c:\Users\josep\Kiro\pz_craft_loops\_commmod.txt","w",encoding="utf-8")
b1,n1=write_mod("KnoxCommunityTilepack",
    "Knox Buildworks - Community Tilepack",
    "Knox Buildworks buildables for the Community Tilepack (abandoned community packs rebundled for B42). Standalone; requires Knox Buildworks + Community Tilepack.")
OUT.write("OFFICIAL mod: %s  (%d definition files)\n"%(b1,n1))
OUT.write("\n".join(WE_DYLAN_REPORT) + "\n")
OUT.write("name/tooltip pass: %d renames\n   %s\n" % (len(NT_REPORT), "\n   ".join(NT_REPORT)))

# ---- WORLD ESSENTIALS SUBMOD SYNC ----
# Our standalone Workshop item (3828080624) is RETIRED. World Essentials ships this content as its
# bundled submod "World Essentials - Community Buildworks" (same mod id KnoxCommunityTilepack).
# We no longer sync a subscribed Steam copy or stage into Zomboid\Workshop: a folder there with
# the same mod id shadows WE's copy and fails the server's Lua checksum (2026-10-30).
# The canonical build stays in OUT_ROOT (project); it is synced into our WORK copy of the WE
# submod (zomboid/WE_submods/work). WE-owned files (mod.info, bundled_source.txt and the runtime
# Lua WE moved into main World Essentials) are never overwritten -- see we_sync.py.
from we_sync import sync_to_we_work, COMMUNITY_SUBMOD
_lines = []
try:
    sync_to_we_work(b1, COMMUNITY_SUBMOD, _lines)
except Exception as e:
    _lines.append("WARN: WE work sync failed: %r" % (e,))
OUT.write("\n".join(_lines) + "\n")
# list tree
OUT.write("\n%s\n"%b1)
for dp,dn,fn in os.walk(b1):
    for f in fn:
        OUT.write("   %s\n"%os.path.join(dp,f).replace(b1,""))
OUT.close()
print("done")
