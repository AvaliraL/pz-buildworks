# -*- coding: utf-8 -*-
"""Single MERGED TEST mod combining ALL TikiTown + Community deliverables under a
testing-oriented build-menu taxonomy:

  TOP-LEVEL CATEGORY = "<TilePack> - <In Progress|Completed>"
  SUBCATEGORY        = generic object type (Walls, Doors, Counters, Roofs, Furniture, ...)

Tile packs (pack-level, not per-sheet):
  - TikiTown            (base sheets: 21,22,23,24,25,26,29,30)
  - TikiTown Newburbs   (newburbs sheets: 27,28,31,32,33,34)
  - Dirkies             (Community component pack; 35 counters) + future Community sub-packs
    (Blackwood, Dylans Tiles, Ekron, Fears, TK, Workshop) register here as added.

Status: a source sheet is Completed if listed in COMPLETED_SHEETS, else In Progress.
Rebuild this ALONGSIDE build_tikitown_mod.py / build_community_mod.py so it never drifts.
It is a TEST/dev mod (own ids-namespace clash avoided by reusing the real ids; do NOT run it
alongside the official standalone mods -> duplicate ids).

Output: C:\\Users\\<user>\\Zomboid\\Workshop\\TikiTownCommunityTest  (+ project mirror).
"""
import json, os, shutil, glob
import sys as _sys
_sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kbw_tilepatch import (write_community_tilepatch, write_removal_lua, write_tv_screen_lua,
                           write_tv_screen_assets, SCREEN_TILESET, SCREEN_TILEDEF_NAME, SCREEN_TILEDEF_ID,
                           write_destroy_lua, write_viewscreen_assets, add_viewscreen_north_faces,
                           write_viewscreen_lua, write_seating_lua, write_fears_assets, write_tabletop_lua, write_multistorey_lua,
                           FEARS_PACK, FEARS_TILEDEF_NAME, FEARS_TILEDEF_ID,
                           VIEWSCREEN_PACK, VIEWSCREEN_TILEDEF_NAME, VIEWSCREEN_TILEDEF_ID,
                           TILEPATCH_NAME as _TV_PATCH_NAME, TILEPATCH_ID as _TV_PATCH_ID)
from kbw_tilepatch import (write_cases_assets, add_case_mirror_faces,
                           CASES_PACK, CASES_TILEDEF_NAME, CASES_TILEDEF_ID)
_write_tv_tiledef = write_community_tilepatch   # shared multi-group tile-property patch

TT   = r"c:\Users\josep\Kiro\zomboid\tikitown"
COMM = r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables"



# --- source sheet -> (pack label, status key) -----------------------------------------
# Use the accurate variant where a cheap/accurate pair exists (parity with the official mod).
# key is the sheet-number prefix string.
PACK_OF = {
    "21": "TikiTown", "22": "TikiTown", "23": "TikiTown", "24": "TikiTown",
    "25": "TikiTown", "26": "TikiTown", "29": "TikiTown", "30": "TikiTown",
    "27": "TikiTown Newburbs", "28": "TikiTown Newburbs", "31": "TikiTown Newburbs",
    "32": "TikiTown Newburbs", "33": "TikiTown Newburbs", "34": "TikiTown Newburbs",
    "35": "Dirkies",
    # Community container deliverables (transpiled from the B41 BuildingMenu addons).
    "40": "Dirkies", "41": "Dylan", "42": "TK",
    # Community wall deliverables.
    "43": "Dirkies", "44": "Dylan", "45": "TK",
    # Community door deliverables.
    "46": "Dirkies", "47": "Dylan", "48": "TK",
    # TK merged dumpsters.
    "49": "TK",
    # Dylan Future Room one-offs.
    "50": "Dylan",
    # Dylan Obs_04 hedges + PitStop2 carpets.
    "51": "Dylan", "52": "Dylan",
    # Dylan RandomFurniture02 misc (balls/bags/TVs).
    "53": "Dylan",
    # Dylan Block_Trasher merged bookshelf.
    "54": "Dylan",
    # Dirkies secret-entrance openable bookshelves (option B).
    "55": "Dirkies",
    # Fears workbenches (+ generated E orientations) and single tiles. In Progress until costs
    # (match synced workbench) and storage (pack's 80) are revisited.
    "56": "Fears",
    # TK kitchen_misc_tk_01: slicer, wall shelf, ice machine, deep fryer, coffee makers.
    "57": "TK",
    # Fears RP tiles: raccoon figure.
    "58": "Fears",
    # Dirkies fencing_ddd_01/02 (incl. two-storey louvered fences, z+1 top layer).
    "59": "Dirkies",
}
# Completed = verified in-game; everything else -> In Progress.
# Whole sheets confirmed complete:
COMPLETED_SHEETS = {"21","22","23","24","25","26","27","28","29","31","32","33","34",
                    "35",   # Dirkies counters (26 lower + 5 upper) confirmed
                    "42",   # TK containers confirmed
                    "45",   # TK walls confirmed
                    "48",   # TK doors confirmed
                    "49",   # TK merged dumpsters confirmed
                    # Dylan: every In Progress Dylan sheet confirmed in-game (2026-08-28)
                    "41", "44", "47", "50", "51", "52", "53", "54",
                    "55",   # Dirkies secret-entrance openable bookshelves confirmed (build+storage+open)
                    # Fears: workbenches + singles (56) and RP raccoon figure (58) confirmed (2026-08-28)
                    "56", "58",
                    "57",   # TK kitchen misc (slicer, wall shelf, ice machine, fryer, coffee makers) confirmed
                    "43",   # Dirkies walls confirmed (2026-08-28)
                    "46",   # Dirkies doors + gates confirmed (2026-08-28)
                    "59"}   # Dirkies fencing confirmed, except the broken louvered fence (see below)
# -> In Progress by omission: "30" (shelving), future sheets.

# PER-PIECE status overrides (finer than sheet-level), matched by buildable id PREFIX.
# Used when a sheet is partially confirmed (e.g. Future Room sheet 50).
COMPLETED_ID_PREFIXES = {
    "community.dylan.futureroom.bed",            # Sci-Fi Floor Bed (2-tile) confirmed
    "community.dylan.futureroom.ctable",         # Sci-Fi Laptop Table confirmed
    "community.dylan.futureroom.lowtable",       # Sci-Fi Coffee Table confirmed
    "community.dylan.futureroom.screen_",        # all 9 viewscreens confirmed
}
# EXACT buildable ids confirmed in-game (when a prefix would also catch unconfirmed siblings).
_DC = "community.dirkies.containers."
COMPLETED_IDS = {
    # Dirkies containers (sheet 40), user review 2026-08-28: Medical, Dressers, Crates, Pallets,
    # Shelving, Tool Cabinets all good (Wardrobes/Cabinets/Counters still being reworked)
    _DC + "location_community_medical_ddd_01_8", _DC + "location_community_medical_ddd_01_10",
    _DC + "location_community_medical_ddd_01_16", _DC + "location_community_medical_ddd_01_28",
    _DC + "edit_ddd_RUS_furniture_storage_03_28", _DC + "edit_ddd_RUS_furniture_storage_03_100",
    _DC + "furniture_storage_ddd_01_12", _DC + "furniture_storage_ddd_01_20",
    # green _4 / white _9 cases (stackable) + their military-crate-capacity versions: confirmed
    _DC + "furniture_storage_ddd_01_4", _DC + "furniture_storage_ddd_01_9",
    _DC + "furniture_storage_ddd_01_4.crate", _DC + "furniture_storage_ddd_01_9.crate",
    _DC + "furniture_storage_ddd_01_7", _DC + "furniture_storage_ddd_01_8",
    _DC + "industry_ddd_01_4", _DC + "industry_ddd_01_5", _DC + "industry_ddd_01_6", _DC + "industry_ddd_01_7",
    _DC + "industry_ddd_01_52", _DC + "industry_ddd_01_53", _DC + "industry_ddd_01_54", _DC + "industry_ddd_01_55",
    _DC + "industry_ddd_01_56", _DC + "industry_ddd_01_57", _DC + "industry_ddd_01_58", _DC + "industry_ddd_01_59",
    _DC + "industry_ddd_01_60",
    _DC + "furniture_storage_ddd_01_14", _DC + "furniture_storage_ddd_01_30", _DC + "industry_dirkea_ddd_01_15",
    _DC + "location_community_medical_ddd_01_12", _DC + "furniture_storage_ddd_01_34",
    _DC + "edit_ddd_RUS_location_business_machinery_02_1",
    # Cabinets + Wardrobes confirmed (2026-08-28, after the merge / missing-tile fixes)
    _DC + "edit_ddd_RUS_furniture_storage_03_32", _DC + "edit_ddd_RUS_furniture_storage_03_33",
    _DC + "edit_ddd_RUS_furniture_storage_03_34", _DC + "edit_ddd_RUS_furniture_storage_03_41",
    _DC + "edit_ddd_RUS_furniture_storage_03_80", _DC + "edit_ddd_RUS_furniture_storage_03_81",
    _DC + "edit_ddd_RUS_furniture_storage_03_82",
    _DC + "edit_ddd_RUS_furniture_storage_03_3", _DC + "edit_ddd_RUS_furniture_storage_03_11",
    _DC + "edit_ddd_RUS_furniture_storage_03_67", _DC + "edit_ddd_RUS_furniture_storage_03_75",
    # Counters confirmed (2026-08-28): Sofaking pair + all 16 RUS upper cabinets
    _DC + "d_location_sofaking_10", _DC + "d_location_sofaking_11",
} | {_DC + "edit_ddd_RUS_fixtures_counters_03_%d" % i for c in range(2, 60, 8) for i in (c, c + 1)}
# Pieces explicitly NOT yet confirmed (force In Progress even if a sibling on the sheet is done):
INPROGRESS_ID_PREFIXES = {
}

def piece_status(bid, sheet_status):
    """Resolve a single buildable's status with per-id overrides winning over the sheet default."""
    for pre in INPROGRESS_ID_PREFIXES:
        if bid and bid.startswith(pre):
            return "In Progress"
    if bid in COMPLETED_IDS:
        return "Completed"
    for pre in COMPLETED_ID_PREFIXES:
        if bid and bid.startswith(pre):
            return "Completed"
    return sheet_status

# TikiTown source files (one per sheet; accurate where a pair exists)
TT_FILES = [
    "21_tikitown_walls_accurate.json","22_tikitown_doors.json","23_tikitown_furniture.json",
    "24_tikitown_bookshelves.json","25_tikitown_bedroom.json","26_tikitown_glass_accurate.json",
    "27_tikitown_newburbs_interiors_accurate.json","28_tikitown_newburbs_walls_accurate.json",
    "29_tikitown_garages.json","30_tikitown_shelving.json","31_tikitown_newburbs_roofs_accurate.json",
    "32_tikitown_newburbs_flags.json","33_tikitown_newburbs_doors_accurate.json",
    "34_tikitown_newburbs_windows_accurate.json",
]

MOD_ID   = "TikiTownCommunityTest"
MOD_NAME = "Knox Buildworks - TikiTown + Community (TEST)"
REQUIRES = ["KnoxBuildworks","KnoxBuildworksVanillaExpanded","tikitown_tiles","UnofficialMappersCommunityTilePack"]
TEST_TR_DIR = r"C:\Users\josep\Zomboid\Workshop\TikiTownTestBundle\Contents\mods\TikiTownTestBundle\42\media\lua\shared\Translate\EN"
UPLOAD_ROOT = r"C:\Users\josep\Zomboid\Workshop"
PROJECT_MIRROR = r"c:\Users\josep\Kiro\zomboid\tikitown\merged_test_upload"
LOG = r"c:\Users\josep\Kiro\pz_craft_loops\_mergedtest.txt"

def sheet_key(fname):
    return os.path.basename(fname).split("_")[0]

def generic_type(b):
    """Derive the generic object type (subcategory) from a buildable's real fields."""
    cat = (b.get("category") or "").strip()
    sub = (b.get("subcategory") or "").strip()
    ctype = (b.get("container") or {}).get("type")
    subl = sub.lower()
    if ctype == "counter" or "counter" in subl:         return "Counters"
    if cat == "Walls and Wall Finishes":                return "Walls"
    if cat == "Roofing":                                return "Roofs"
    # KBW Durability classes a wall-placed piece as a fence only if category is Fencing or the
    # subcategory contains "fence" ("Fencing" does not), so keep "Fences" here or test-bundle
    # fences get full wall health (450 base) instead of fence health (250 base).
    if cat in ("Fencing", "Fences & Gates"):            return "Fences"
    if cat == "Windows":                                return "Windows"
    if cat == "Doors":
        return "Garage Doors" if "garage" in subl else "Doors"
    if cat in ("Decorations", "Decorations and Landscaping"):
        return "Flags" if "flag" in subl else "Decorations"
    # Containers keep their own subcategory (Wardrobes, Pallets, Shelving...); only counter pieces
    # were caught above. Lumping all of them under "Counters" hid wardrobes and pallets there.
    if cat == "Containers":                             return sub or "Storage"
    if cat == "Furniture and Appliances":
        if "bed" in subl:   return "Beds"
        if "desk" in subl:  return "Desks"
        if "table" in subl: return "Tables"
        if "storage" in subl or "shelv" in subl or "bookshelf" in subl: return "Storage"
        return "Furniture"
    return cat or "Other"

def load_sources():
    """Yield (pack, status, filename, doc) for every source sheet."""
    for fn in TT_FILES:
        p = os.path.join(TT, fn)
        if not os.path.isfile(p):
            continue
        k = sheet_key(fn)
        yield PACK_OF.get(k, "TikiTown"), ("Completed" if k in COMPLETED_SHEETS else "In Progress"), fn, json.load(open(p, encoding="utf-8"))
    for p in sorted(glob.glob(os.path.join(COMM, "*.json"))):
        fn = os.path.basename(p)
        k = sheet_key(fn)
        yield PACK_OF.get(k, "Community"), ("Completed" if k in COMPLETED_SHEETS else "In Progress"), fn, json.load(open(p, encoding="utf-8"))

def main():
    up = os.path.join(UPLOAD_ROOT, MOD_ID)
    if os.path.isdir(up): shutil.rmtree(up)
    mod42 = os.path.join(up, "Contents", "mods", MOD_ID, "42")
    defs_dir = os.path.join(mod42, "media", "KnoxBuildworks", "definitions")
    tr_dir   = os.path.join(mod42, "media", "lua", "shared", "Translate", "EN")
    os.makedirs(defs_dir); os.makedirs(tr_dir)

    mi=[
        "name=%s"%MOD_NAME, "id=%s"%MOD_ID,
        "description=TEST bundle: every TikiTown + Community Knox Buildworks buildable, grouped by "
        "tile pack and In Progress/Completed status for in-game review. Not for release; do not run "
        "alongside the official standalone mods (duplicate ids).",
        "require=%s"%",".join(REQUIRES),
        "loadModAfter=%s"%",".join(REQUIRES),
        "versionMin=42.0", "tags=Build 42,Build",
        "tiledef=%s %d"%(_TV_PATCH_NAME, _TV_PATCH_ID),   # functional wall-mounted TV patch (v2, free id)
        "pack=%s"%SCREEN_TILESET,                          # generated wall-TV screen art
        "tiledef=%s %d"%(SCREEN_TILEDEF_NAME, SCREEN_TILEDEF_ID),
        "pack=%s"%VIEWSCREEN_PACK,                         # generated north-wall viewscreens
        "tiledef=%s %d"%(VIEWSCREEN_TILEDEF_NAME, VIEWSCREEN_TILEDEF_ID),
        "pack=%s"%FEARS_PACK,                              # generated Fears workbench orientations
        "tiledef=%s %d"%(FEARS_TILEDEF_NAME, FEARS_TILEDEF_ID),
        "pack=%s"%CASES_PACK,                              # generated military-case 2nd orientation
        "tiledef=%s %d"%(CASES_TILEDEF_NAME, CASES_TILEDEF_ID),
    ]
    open(os.path.join(mod42,"mod.info"),"w",encoding="utf-8").write("\n".join(mi)+"\n")
    _media=os.path.join(mod42,"media"); os.makedirs(_media, exist_ok=True)
    write_tv_screen_assets(_media)
    write_viewscreen_assets(_media)
    # depth maps + tileGeometry load only from <mod>/common/media
    write_fears_assets(_media, os.path.join(os.path.dirname(mod42), "common", "media"))
    write_cases_assets(_media, os.path.join(os.path.dirname(mod42), "common", "media"))
    _write_tv_tiledef(os.path.join(_media, _TV_PATCH_NAME+".tiles"))
    # runtime removal of collision flags the additive .patch.tiles merge cannot remove
    write_removal_lua(os.path.join(_media, "lua", "shared", "KBWCommunity_TileFixes.lua"))
    write_tv_screen_lua(os.path.join(_media, "lua", "shared", "KBWCommunity_TVScreens.lua"))
    # sledgehammer destroy for our builds (vanilla blocks d_/e_/f_ sprites)
    write_destroy_lua(os.path.join(_media, "lua", "client", "KBWCommunity_Destroyable.lua"))
    # viewscreen image cycle (frosted -> Earth -> Mars); shared so the timed action exists server-side
    write_viewscreen_lua(os.path.join(_media, "lua", "shared", "KBWCommunity_Viewscreens.lua"))
    # counter-top appliance height (coffee makers / slicer on floor vs counter)
    write_tabletop_lua(os.path.join(_media, "lua", "shared", "KBWCommunity_TableTop.lua"))
    # two-storey wall pieces (top tile one level up) pass KBW's wall-support check
    write_multistorey_lua(os.path.join(_media, "lua", "shared", "KBWCommunity_MultiStorey.lua"))
    # seating fixes for other packs' broken bed data (tterika double bed)
    write_seating_lua(os.path.join(_media, "lua", "shared", "KBWCommunity_Seating.lua"))

    merged=[]
    import name_tooltip_pass
    nt_tooltips={}
    seen=set(); dupes=0
    from collections import Counter
    cat_counts=Counter(); sub_counts=Counter()
    per_pack=Counter()
    for pack, status, fn, doc in load_sources():
        for b in doc.get("buildables", []):
            bid=b.get("id")
            if bid in seen: dupes+=1; continue
            seen.add(bid)
            # per-piece status override (finer than sheet-level)
            pstatus = piece_status(bid, status)
            top = "%s - %s" % (pack, pstatus)
            nb=json.loads(json.dumps(b))         # deep copy
            add_viewscreen_north_faces(nb)       # generated north-wall viewscreen art
            add_case_mirror_faces(nb)            # generated 2nd orientation for the military cases
            # name + tooltip pass, on the REAL categories (before the test regrouping below)
            name_tooltip_pass.apply([nb], nt_tooltips)
            nb["subcategory"]=generic_type(b)    # generic type as subcategory
            nb["category"]=top                   # pack + status as top-level
            # drop any group block so the test menu is a flat type list, not family groups
            nb.pop("group", None)
            merged.append(nb)
            cat_counts[top]+=1; sub_counts[nb["subcategory"]]+=1; per_pack[pack]+=1

    name_tooltip_pass.split_shared_keys(merged)   # unique translationKey per distinct name
    out_doc={"schemaVersion":1,"category":"Walls",
             "source":"MERGED TEST - all TikiTown + Community deliverables; category=<pack> - <status>, subcategory=<generic type>.",
             "buildables":merged}
    out_fn="90_merged_test_all.json"
    json.dump(out_doc, open(os.path.join(defs_dir,out_fn),"w",encoding="utf-8"), indent=1, ensure_ascii=False)
    json.dump({"schemaVersion":1,"definitions":["media/KnoxBuildworks/definitions/%s"%out_fn]},
              open(os.path.join(mod42,"media","KnoxBuildworks","manifest.json"),"w",encoding="utf-8"))

    # ship the complete translation tables (same as official TikiTown mod)
    for tf in ("IG_UI.json","Tooltip.json"):
        src=os.path.join(TEST_TR_DIR, tf)
        if os.path.isfile(src): shutil.copyfile(src, os.path.join(tr_dir, tf))
    # the copied table predates newer sheets and later renames: the merged definitions are the
    # source of truth, so their displayName wins for every key they carry
    _ig_path=os.path.join(tr_dir, "IG_UI.json")
    _ig=json.load(open(_ig_path, encoding="utf-8")) if os.path.isfile(_ig_path) else {}
    _added=_changed=0
    for nb in merged:
        tk=nb.get("translationKey"); dn=nb.get("displayName")
        if not tk or not dn:
            continue
        if tk not in _ig:
            _added+=1
        elif _ig[tk]!=dn:
            _changed+=1
        _ig[tk]=dn
    json.dump(_ig, open(_ig_path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("test translations: added %d, updated %d names" % (_added, _changed))
    # shared tooltip keys: never ship KBW-owned keys, generic text for ours (see tooltip_fix.py)
    from tooltip_fix import fix_file, SHARED_TEXT
    _tt_path = os.path.join(tr_dir, "Tooltip.json")
    # only our name/tooltip-pass type keys (the copied per-piece table just repeated names)
    _tt = dict(nt_tooltips)
    json.dump(_tt, open(_tt_path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("tooltip fix: %s" % (fix_file(_tt_path),))

    # workshop wrapper
    wt=["version=1","id=","title=%s"%MOD_NAME,
        "description=Developer TEST bundle: all TikiTown + Community Knox buildables, grouped by tile pack and status.",
        "description=","description=Requires Knox Buildworks, KBW Vanilla Expanded, Drazion's Tilepack, and the Community Tilepack.",
        "tags=Build 42;Building;WIP","visibility=private"]
    open(os.path.join(up,"workshop.txt"),"w",encoding="utf-8").write("\n".join(wt)+"\n")
    prev=r"C:\Users\josep\Zomboid\Workshop\TikiTownTestBundle\preview.png"
    if os.path.isfile(prev): shutil.copyfile(prev, os.path.join(up,"preview.png"))

    if os.path.isdir(PROJECT_MIRROR): shutil.rmtree(PROJECT_MIRROR)
    shutil.copytree(up, PROJECT_MIRROR)

    rpt=["MERGED TEST mod -> %s"%up, "total buildables: %d"%len(merged),
         "duplicate ids skipped: %d"%dupes, "", "per pack:"]
    for p,n in sorted(per_pack.items()): rpt.append("  %5d  %s"%(n,p))
    rpt.append(""); rpt.append("top-level categories (<pack> - <status>):")
    for c,n in sorted(cat_counts.items()): rpt.append("  %5d  %s"%(n,c))
    rpt.append(""); rpt.append("subcategories (generic type):")
    for s,n in sorted(sub_counts.items()): rpt.append("  %5d  %s"%(n,s))
    open(LOG,"w",encoding="utf-8").write("\n".join(rpt))
    print("done", len(merged), "buildables")

if __name__=="__main__":
    main()
