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
    r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables\60_community_dirkies_stairs.json",
    r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables\61_community_dirkies_bedroom.json",
    r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables\62_community_dirkies_couches.json",
    r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables\63_community_dirkies_decor_house.json",
    r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables\64_community_dirkies_window_decor.json",
    r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables\65_community_dirkies_medical.json",
    r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables\66_community_dylan_gun_racks.json",
    r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables\67_community_dylan_future_room_extras.json",
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
from kbw_tilepatch import (write_orange_couch_assets, write_sofaking_depth_override, ORANGE_COUCH_PACK,
                           ORANGE_COUCH_TILEDEF_NAME, ORANGE_COUCH_TILEDEF_ID)
from kbw_tilepatch import (write_iceshell_assets, ICESHELL_PACK, ICESHELL_TILEDEF_NAME,
                           ICESHELL_TILEDEF_ID)
import we_dylan
import name_tooltip_pass
import counter_variants
CV_REPORT = {}
WE_DYLAN_REPORT = []
FR_REPORT = []
BT_REPORT = []
ROT_REPORT = []
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
    ] + we_dylan.MODINFO_LINES + [                         # WE's isolated Dylan sprites (8182)
        "pack=%s"%ORANGE_COUCH_PACK,                       # generated single-tile L-couch end pieces
        "tiledef=%s %d"%(ORANGE_COUCH_TILEDEF_NAME, ORANGE_COUCH_TILEDEF_ID),
        "pack=%s"%ICESHELL_PACK,                           # generated inert ice-machine shell (stage 1)
        "tiledef=%s %d"%(ICESHELL_TILEDEF_NAME, ICESHELL_TILEDEF_ID),
    ]
    open(os.path.join(base,"42","mod.info"),"w",encoding="utf-8").write("\n".join(mi)+"\n")
    # emit the TV patch .tiles into media/ (same dir layout as working tiledef mods)
    _media=os.path.join(base,"42","media"); os.makedirs(_media, exist_ok=True)
    write_tv_screen_assets(_media)
    write_viewscreen_assets(_media)
    # depth maps + tileGeometry load only from <mod>/common/media
    write_fears_assets(_media, os.path.join(base,"common","media"))
    write_cases_assets(_media, os.path.join(base,"common","media"))
    write_orange_couch_assets(_media)
    write_sofaking_depth_override(os.path.join(base,"common","media"))
    # inert shell art (stage 1 of the two-stage ice machines and fridge / freezer tiers) + depth map
    write_iceshell_assets(_media, os.path.join(base,"common","media"), include_fridges=True)
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
    # wall overlays: the cursor also runs World Essentials' attachment check (no mid-build errors)
    from kbw_tilepatch import write_overlay_guard_lua
    write_overlay_guard_lua(os.path.join(_media, "lua", "shared", "KBWCommunity_OverlayGuard.lua"))
    # KBW stage properties: per-type container capacity, container retype (container_caps.py)
    from container_caps import (write_container_caps_lua, LUA_NAME as _CC_LUA, write_stage_info_lua,
                                INFO_LUA_NAME as _SI_LUA, write_pickup_lua, PICKUP_LUA_NAME as _PU_LUA)
    write_container_caps_lua(os.path.join(_media, "lua", "shared", _CC_LUA))
    # build-menu capacity text + inventory tooltip for picked-up builds (client only)
    write_stage_info_lua(os.path.join(_media, "lua", "client", _SI_LUA))
    # pick up / place keeps our builds' storage (shared: runs where the moveable action runs)
    write_pickup_lua(os.path.join(_media, "lua", "shared", _PU_LUA))
    from container_caps import write_multipart_lua, MULTIPART_LUA_NAME as _MP_LUA
    write_multipart_lua(os.path.join(_media, "lua", "shared", _MP_LUA))
    # ladders must hang on a wall (onIsValid used by 72_kbwcb_ladders.json; ladders.py)
    from ladders import write_ladder_guard_lua, GUARD_LUA_COMMUNITY
    write_ladder_guard_lua(os.path.join(_media, "lua", "shared", GUARD_LUA_COMMUNITY))
    # gun rack fill overlays for our copies (66_community_dylan_gun_racks.json)
    from kbw_tilepatch import write_gunrack_overlay_lua, GUNRACK_LUA_NAME
    write_gunrack_overlay_lua(os.path.join(_media, "lua", "server", "Items", GUNRACK_LUA_NAME))
    # workbench built-in tools + bench craft menu (bench_tools.py): HELD BACK from World Essentials
    # (WE merge 2026-11-10: the WE dev declined them pending a multiplayer review). Not applied to
    # the definitions, no Lua, no labels here; the test bundle (build_merged_test_mod) keeps them.
    import bench_tools
    WE_HOLD_BACK_BENCH_TOOLS = True

    # definitions + translations
    manifest_defs=[]
    ig_ui={}; tooltip={}; all_buildables=[]
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
        
        # reinforced counters: military-crate cost, capacity 100 (counter_variants.py)
        CV_REPORT[fname] = counter_variants.add_variants(d.get("buildables", []))
        # workbenches: runtime tool set + one-of-each-core-tool build cost (bench_tools.py)
        if not WE_HOLD_BACK_BENCH_TOOLS:
            _bt = bench_tools.apply_to_buildables(d.get("buildables", []))
            if _bt:
                BT_REPORT.extend(_bt)
        for _b in d.get("buildables", []):
            add_viewscreen_north_faces(_b)   # generated north-wall viewscreen art
            add_case_mirror_faces(_b)        # generated 2nd orientation for the military cases
            _n, _miss = we_dylan.rename_buildable(_b)   # Dylan sprites -> WE's WECommunity_* copies
            dyl_renamed[0] += _n
            if _miss:
                dyl_unmapped.append((_b.get("id"), sorted(set(_miss))))
        # name + tooltip pass (fixed names, one-line type tooltips; see name_tooltip_pass.py)
        name_tooltip_pass.apply(d.get("buildables", []), tooltip, NT_REPORT)
        from kbw_sort_order import md5_order
        md5_order(d.setdefault("buildables", []))   # keeps KBW's registry sort shallow (kbw_sort_order.py)
        json.dump(d, open(os.path.join(defs_dir,fname),"w",encoding="utf-8"), indent=1, ensure_ascii=False)
        manifest_defs.append("media/KnoxBuildworks/definitions/%s"%fname)
        for b in d["buildables"]:
            tk=b.get("translationKey")
            if tk: ig_ui[tk]=b.get("displayName","")
            g=b.get("group") or {}
            if g.get("translationKey") and g.get("name") and g["translationKey"] not in ig_ui:
                ig_ui[g["translationKey"]]=g["name"]   # group card title
        all_buildables.extend(d["buildables"])
    # tiered 1-tile fridges / freezers built from the KBW VE refrigerators (align_appliance_costs)
    from align_appliance_costs import build_fridge_defs
    _fr, _fr_groups, _fr_tips, _fr_rep = build_fridge_defs()
    _fr_doc = {"schemaVersion": 1, "category": "Furniture and Appliances",
               "source": "Tiered 1-tile fridges / freezers (KBW VE refrigerators); "
                         "generated by pz_craft_loops/align_appliance_costs.build_fridge_defs.",
               "materialGroups": _fr_groups, "buildables": _fr}
    _fr_fn = "70_kbwcb_refrigeration_tiers.json"
    from kbw_sort_order import md5_order
    _fr_doc["buildables"] = md5_order(list(_fr))
    json.dump(_fr_doc, open(os.path.join(defs_dir, _fr_fn), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    manifest_defs.append("media/KnoxBuildworks/definitions/%s" % _fr_fn)
    tooltip.update(_fr_tips)
    for b in _fr:
        ig_ui[b["translationKey"]] = b["displayName"]
        g = b.get("group") or {}
        if g.get("translationKey") and g.get("name") and g["translationKey"] not in ig_ui:
            ig_ui[g["translationKey"]] = g["name"]
    all_buildables.extend(_fr)
    FR_REPORT.extend(_fr_rep)
    # hand-pump sinks: the KBW VE counter-top sinks on our copied tiles with well water (pump_sinks.py)
    from pump_sinks import build_pump_sink_defs
    _ps, _ps_tips, _ps_rep = build_pump_sink_defs()
    _ps_doc = {"schemaVersion": 1, "category": "Appliances",
               "source": "Hand-pump versions of the KBW VE counter-top sinks (our copied tiles, Knox well water, "
                         "Large Water Tank cost); generated by pz_craft_loops/pump_sinks.py.",
               "buildables": _ps}
    _ps_fn = "71_kbwcb_pump_sinks.json"
    _ps_doc["buildables"] = md5_order(list(_ps))
    json.dump(_ps_doc, open(os.path.join(defs_dir, _ps_fn), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    manifest_defs.append("media/KnoxBuildworks/definitions/%s" % _ps_fn)
    tooltip.update(_ps_tips)
    for b in _ps:
        ig_ui[b["translationKey"]] = b["displayName"]
        g = b.get("group") or {}
        if g.get("translationKey") and g.get("name"):
            ig_ui[g["translationKey"]] = g["name"]      # "Hand Pump Sinks" card title
    all_buildables.extend(_ps)
    FR_REPORT.extend(_ps_rep)
    # vanilla ladders nothing builds yet: wooden + railroad (ladders.py; B42 ladder flags on the tiles)
    from ladders import build_vanilla_ladder_defs
    _ld, _ld_tips, _ld_rep = build_vanilla_ladder_defs()
    _ld_doc = {"schemaVersion": 1, "category": "Stairs",
               "source": "Vanilla wooden and railroad ladders (B42 climbable ladder tiles; WE Sewer Ladders "
                         "cost for metal); generated by pz_craft_loops/ladders.py.",
               "buildables": md5_order(list(_ld))}
    _ld_fn = "72_kbwcb_ladders.json"
    json.dump(_ld_doc, open(os.path.join(defs_dir, _ld_fn), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    manifest_defs.append("media/KnoxBuildworks/definitions/%s" % _ld_fn)
    tooltip.update(_ld_tips)
    for b in _ld:
        ig_ui[b["translationKey"]] = b["displayName"]
        g = b.get("group") or {}
        if g.get("translationKey") and g.get("name"):
            ig_ui[g["translationKey"]] = g["name"]      # "Ladders" card title
    all_buildables.extend(_ld)
    FR_REPORT.extend(_ld_rep)
    # moveable rotation for pieces whose tile pack groups the facings badly (rotation_fix.py)
    import rotation_fix
    _rot, _rot_rep = rotation_fix.build_offsets(all_buildables, rotation_fix.load_sheets())
    rotation_fix.write_rotation_lua(os.path.join(_media, "lua", "shared", rotation_fix.LUA_NAME), _rot)
    ROT_REPORT.append("rotation: fixed %d pieces (%d sprites), engine already rotates %d; skipped %s" % (
        _rot_rep["fixed"], len(_rot), _rot_rep["already"],
        {k: len(v) for k, v in _rot_rep["skipped"].items()}))
    # "Build first: <shell name>" instead of the raw previous-stage id (two-stage ice machines)
    from container_caps import previous_stage_names
    ig_ui.update(previous_stage_names(all_buildables))
    if not WE_HOLD_BACK_BENCH_TOOLS:
        ig_ui.update(bench_tools.TRANSLATIONS["IG_UI"])   # right-click "open <Category> crafting" labels
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
OUT.write("reinforced counters added: %d %s\n" % (sum(CV_REPORT.values()), {k: v for k, v in CV_REPORT.items() if v}))
OUT.write("fridge / freezer tier units: %d\n   %s\n" % (len(FR_REPORT), "\n   ".join(FR_REPORT)))
OUT.write("\n".join(ROT_REPORT) + "\n")
OUT.write("bench tools on: %s\n" % BT_REPORT)

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
# table-top height list lives in WE's own KBWCommunity_TableTop.lua (WE-owned, consolidated for both
# submods): add our new table-top sprites to OUR WORK copy of it (flag to the WE dev in the notes)
from kbw_tilepatch import sync_we_tabletop_sprites
_we_tt = os.path.join(r"c:\Users\josep\Kiro\zomboid\WE_submods\work", "World Essentials (base, our files only)",
                      "42", "media", "lua", "shared", "KBWCommunity_TableTop.lua")
_lines.append("WE table-top list: added %s" % (sync_we_tabletop_sprites(_we_tt) or "nothing (up to date)"))
# same for the TV screen list (WE-owned KBWCommunity_TVScreens.lua): our Future Room wall TVs
from kbw_tilepatch import sync_we_tv_screens
_we_tv = os.path.join(os.path.dirname(_we_tt), "KBWCommunity_TVScreens.lua")
_lines.append("WE TV screen list: added %s" % (sync_we_tv_screens(_we_tv) or "nothing (up to date)"))
OUT.write("\n".join(_lines) + "\n")
# list tree
OUT.write("\n%s\n"%b1)
for dp,dn,fn in os.walk(b1):
    for f in fn:
        OUT.write("   %s\n"%os.path.join(dp,f).replace(b1,""))
OUT.close()
print("done")
