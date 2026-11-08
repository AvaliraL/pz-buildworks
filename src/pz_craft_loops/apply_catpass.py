# -*- coding: utf-8 -*-
"""
Dev-scheme category/subcategory/group + naming pass for TikiTown deliverables.
Mirrors live KBW 20_tikitown.json conventions.

Rules (locked with user):
 - category: 21/26/27/28 -> "Walls"; 22/29 -> "Doors"; 23/24/25 -> "Furniture and Appliances".
 - subcategory: strip leading "TikiTown " prefix. Specific remaps for 23/24/25 per below.
 - group: one group PER SPRITE FAMILY (style). All pieces of that family
   (base + windows + door frame + corner + pillar + fence) share one group.id and
   get an incremental `level`. Group fields = {id, name, translationKey, level}.
   id    = worldessentials.tikitown.family_<slug>
   name  = representative label for the family (the base piece's display name)
   tkey  = IGUI_WETiki_family_<slug>
 - Single-item families (e.g. the one bookshelf, lone tents wall) get NO group.
 - Naming fixes:
     * "Wall Wall - Style N" -> "Wall - Style N"
     * bedroom color prefix remap: Oak->Pink Wood, Dark Wood->Blue Wood, White->White Wood
       (Light Wood kept). Then strip a redundant "Light Wood " that follows the color prefix.
 - Garages (29): KEEP existing per-color grouping & structure; ONLY set category/subcategory
   (category "Doors", subcategory "Garage Doors"). Do not re-group.
"""
import json, os, re, hashlib, collections

DIR = r"c:\Users\josep\Kiro\zomboid\tikitown"

def slug(s):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:16]

def fam_of(b):
    icon = b.get("iconSprite","") or ""
    m = re.match(r"^(.*)_(\d+)$", icon)
    if m: return m.group(1)
    # fallback to id tail family (strip trailing _NN or _suffix index)
    tail = b.get("id","").rsplit(".",1)[-1]
    m = re.match(r"^(.*)_(\d+)$", tail)
    return m.group(1) if m else tail

def strip_tikitown(sub):
    if sub and sub.startswith("TikiTown "):
        return sub[len("TikiTown "):]
    return sub

# ---- by-color subcategory for Newburbs tiles (27 interiors, 28 walls) ----
# Dev convention: subcategory = color name ONLY (no sheet number, no generic bucket).
WALL_COLOR_LABEL = {
    "white": "White", "warmgray": "Warm Grey", "red": "Red", "orange": "Orange",
    "redbrown": "Red Brown", "yellow": "Yellow", "blue": "Blue", "pink": "Pink",
    "coolgray": "Cool Grey", "black": "Black",
}

# Stable interiors color map keyed by (sheet, c-token) from the id -- NOT displayName
# (displayName is cosmetic and gets rewritten, so can't be the source of truth).
INTERIOR_CMAP = {
    ("01","c1"):"White",("01","c2"):"Pink",("01","c3"):"Tan",("01","c4"):"Pale Silver",
    ("02","c1"):"Blue",("02","c2"):"Smoke",("02","c3"):"Morning Blue",("02","c4"):"Rhythm",
    ("03","c1"):"Cream",("03","c2"):"Black",("03","c3"):"Cinereous",("03","c4"):"Grey Asparagus",
    ("04","c1"):"Granite Grey",("04","c2"):"Spanish Grey",("04","c3"):"Grullo",("04","c4"):"Granite Grey Dark",
}

def newburbs_interiors_color(b):
    """27: color from id (sheet, c-token) via INTERIOR_CMAP -- stable across renames."""
    m = re.search(r"tt_newburbs_interiors_(\d+)_(c\d+)_", b.get("id",""))
    if not m:
        return None
    return INTERIOR_CMAP.get((m.group(1), m.group(2)))

def newburbs_walls_color(b):
    """28: color = id token tt_newburbs_walls_NN_<tok>_ mapped to label."""
    m = re.search(r"tt_newburbs_walls_\d+_([a-z]+)_", b.get("id", ""))
    if not m:
        return None
    return WALL_COLOR_LABEL.get(m.group(1), m.group(1))

# filename -> color-deriver (durable by-color subcat rule; see TODO_color_subcategories.md)
COLOR_SUBCAT = {
    "27_tikitown_newburbs_interiors.json": newburbs_interiors_color,
    "28_tikitown_newburbs_walls.json": newburbs_walls_color,
}

# ---- naming fixes ----
def fix_wall_wall(dn):
    if dn and dn.startswith("Wall Wall - Style"):
        return dn.replace("Wall Wall - Style", "Wall - Style", 1)
    return dn

COLOR_REMAP = [
    ("Dark Wood", "Blue Wood"),   # check multi-word first
    ("Light Wood", "Light Wood"),
    ("Oak", "Pink Wood"),
    ("White", "White Wood"),
]

def fix_bedroom_name(dn):
    if not dn: return dn
    # Bunk beds use literal fabric colors (Green/Yellow/Blue/Oak Bunk Bed) and the
    # "Bedding ..." names are untouched -- do NOT color-remap those.
    if "Bunk Bed" in dn or dn.startswith("Bedding "):
        return dn
    # idempotent: a name that already carries a remapped color is done. Without this,
    # "White Wood Bed" matched the "White" rule again on every run (-> "White Wood Wood Wood ...").
    for _old, new in COLOR_REMAP:
        if dn == new or dn.startswith(new + " "):
            return dn
    newcolor = None; rest = None
    for old, new in COLOR_REMAP:
        if dn == old or dn.startswith(old + " "):
            newcolor = new
            rest = dn[len(old):].lstrip()
            break
    if newcolor is None:
        return dn
    # strip a redundant "Light Wood " material word anywhere in the rest (may follow
    # a modifier like 'Hanging' or 'Small'), e.g. 'Hanging Light Wood Shelves' -> 'Hanging Shelves'
    rest = re.sub(r"\bLight Wood\b\s*", "", rest).strip()
    rest = re.sub(r"\s{2,}", " ", rest)
    return (newcolor + " " + rest).strip()

def bedroom_type_key(dn):
    """Derive an object-type key by stripping the (already-remapped) color prefix,
    so colors of the SAME object type group together (dev scheme)."""
    for new in ("Light Wood", "Pink Wood", "Blue Wood", "White Wood"):
        if dn == new or dn.startswith(new + " "):
            return dn[len(new):].strip()
    return dn  # bunk beds / bedding keep their own key

# subcategory remaps per file (after stripping TikiTown)
SUBMAP_23 = {
    "Counters": "Counters",
    "Desks": "Desks",
    "Decorations": "Posters",
}
SUBMAP_25 = {
    "Beds": "Beds",
    "Bedroom Storage": "Storage",
    "Bedroom Furniture": "Small Tables",
    "Bedroom Decor": "Posters",
}

# Top-level category. Wall files use the live KBW string "Walls and Wall Finishes"
# (confirmed against live KBW defs), NOT bare "Walls" (which the menu treats as a separate cat).
WALLS_CAT = "Walls and Wall Finishes"
CATEGORY = {
    "21_tikitown_walls.json": WALLS_CAT,
    "22_tikitown_doors.json": "Doors",
    "23_tikitown_furniture.json": "Furniture and Appliances",
    "24_tikitown_bookshelves.json": "Furniture and Appliances",
    "25_tikitown_bedroom.json": "Furniture and Appliances",
    "26_tikitown_glass.json": WALLS_CAT,
    "27_tikitown_newburbs_interiors.json": WALLS_CAT,
    "28_tikitown_newburbs_walls.json": WALLS_CAT,
    "29_tikitown_garages.json": "Doors",
    # ACCURATE (high-cost) pair -- SAME cosmetic treatment; recipes/costs untouched.
    "21_tikitown_walls_accurate.json": WALLS_CAT,
    "26_tikitown_glass_accurate.json": WALLS_CAT,
}

report = []

def process_grouped(fn, d, bedroom=False, submap=None):
    """Standard files: set category/subcategory, strip TikiTown, group per sprite family, fix names."""
    cat = CATEGORY[fn]
    color_fn = COLOR_SUBCAT.get(fn)
    bs = d["buildables"]
    # group members by family (preserve original order for level)
    fam_members = collections.OrderedDict()
    for b in bs:
        fam_members.setdefault(fam_of(b), []).append(b)
    for b in bs:
        # category
        b["category"] = cat
        # subcategory -- by-color for Newburbs tiles, else strip TikiTown + submap
        if color_fn is not None:
            color = color_fn(b)
            b["subcategory"] = color if color else strip_tikitown(b.get("subcategory"))
            sub = b["subcategory"]
        else:
            sub = strip_tikitown(b.get("subcategory"))
            if submap and sub in submap:
                sub = submap[sub]
            b["subcategory"] = sub
        # posters are wall decorations -> Decorations and Landscaping (dev convention), not Furniture
        if (sub or "").strip().lower() == "posters":
            b["category"] = "Decorations and Landscaping"
        # naming
        dn = b.get("displayName")
        dn = fix_wall_wall(dn)
        if bedroom:
            dn = fix_bedroom_name(dn)
        b["displayName"] = dn
    # grouping per family
    for fam, members in fam_members.items():
        if len(members) < 2:
            # single-item family: no group
            members[0].pop("group", None)
            continue
        sl = slug(fam)
        gid = f"worldessentials.tikitown.family_{sl}"
        tkey = f"IGUI_WETiki_family_{sl}"
        # representative name = first base piece's display name, else first member
        base = next((m for m in members if "window" not in (m.get("displayName","").lower())
                     and "corner" not in (m.get("displayName","").lower())
                     and "pillar" not in (m.get("displayName","").lower())
                     and "door frame" not in (m.get("displayName","").lower())
                     and "post" not in (m.get("displayName","").lower())
                     and "fence" not in (m.get("displayName","").lower())), members[0])
        gname = base.get("displayName")
        for i, m in enumerate(members):
            m["group"] = {"id": gid, "name": gname, "translationKey": tkey, "level": i + 1}
    report.append((fn, len(bs), len([f for f,ms in fam_members.items() if len(ms)>=2]),
                   len([f for f,ms in fam_members.items() if len(ms)<2])))

def process_bedroom(fn, d, submap):
    """Bedroom: group by OBJECT TYPE across the 4 wood colors (dev scheme), e.g.
    'TikiTown Fancy Floor Bed' spans Light/Pink/Blue/White Wood. Bunk beds group together;
    'Bedding' single/double stay as their own groups by type."""
    cat = CATEGORY[fn]
    bs = d["buildables"]
    # first fix category/subcategory/names
    for b in bs:
        b["category"] = cat
        sub = strip_tikitown(b.get("subcategory"))
        if submap and sub in submap:
            sub = submap[sub]
        b["subcategory"] = sub
        if (sub or "").strip().lower() == "posters":
            b["category"] = "Decorations and Landscaping"
        b["displayName"] = fix_bedroom_name(b.get("displayName"))
    # group by (subcategory, type-key); but bunk beds all together; bedding by type
    typed = collections.OrderedDict()
    for b in bs:
        dn = b["displayName"]
        if "Bunk Bed" in dn:
            key = "Bunk Bed"
        elif dn.startswith("Bedding "):
            # 'Bedding Double Bed', 'Bedding Single Bed R4..' -> group singles together, double alone
            key = "Bedding Single Bed" if "Single" in dn else "Bedding Double Bed"
        else:
            key = bedroom_type_key(dn)
        typed.setdefault(key, []).append(b)
    gcount = 0; singles = 0
    for key, members in typed.items():
        if len(members) < 2:
            members[0].pop("group", None); singles += 1; continue
        sl = slug("bedroom::" + key)
        gid = f"worldessentials.tikitown.family_{sl}"
        tkey = f"IGUI_WETiki_family_{sl}"
        gname = "TikiTown " + key
        for i, m in enumerate(members):
            m["group"] = {"id": gid, "name": gname, "translationKey": tkey, "level": i + 1}
        gcount += 1
    report.append((fn, len(bs), gcount, singles))

# ---- Newburbs color-variant files (27 interiors, 28 walls): by-color subcat, original-vocab
#      displayNames, per-color grouping. Matches apply_color_subcat.py + fill_walls_28.py +
#      rename_interiors_27.py outputs so a full catpass re-run stays consistent. ----
# id suffix -> (TypeWord, Qualifier)  shared taxonomy for both interiors and walls
NEWBURBS_SUFFIX_NAME = {
    "wall": ("Wall", None), "window": ("Window Frame", None), "doorframe": ("Door Frame", None),
    "wide_window_l": ("Window Frame", "Wide Left"), "wide_window_c": ("Window Frame", "Wide Center"),
    "wide_window_r": ("Window Frame", "Wide Right"), "tall_window": ("Window Frame", "Tall"),
    "wide_tall_l": ("Window Frame", "Wide Tall Left"), "wide_tall_c": ("Window Frame", "Wide Tall Center"),
    "wide_tall_r": ("Window Frame", "Wide Tall Right"), "garage_l": ("Door Frame", "Garage Left"),
    "garage_c": ("Door Frame", "Garage Center"), "garage_r": ("Door Frame", "Garage Right"),
    "corner": ("Corner Wall", None), "pillar": ("Pillar", None),
    # roof-trim walls (28 only): name = the type words directly (no qualifier)
    "wall_b": ("Wall", None), "wall_c": ("Wall", None), "wall_d": ("Wall", None),
    "pillar_b": ("Pillar", None),
}
# roof-trim suffix -> explicit type words (for the roof pieces that aren't in the table above)
def _roof_typeword(suf):
    m = re.match(r"roof_slope_(\d+)$", suf)
    if m: return f"Roof Slope Wall {m.group(1)}"
    m = re.match(r"roof_end_(small|medium|big)$", suf)
    if m: return "Roof End " + m.group(1).capitalize()
    m = re.match(r"roof_steep_slope_(\d+)$", suf)
    if m: return f"Roof Steep Slope Wall {m.group(1)}"
    m = re.match(r"roof_steep_end_(.+)$", suf)
    if m: return "Roof Steep End " + " ".join(w.capitalize() for w in m.group(1).split("_"))
    return None

def _newburbs_suffix(bid, fam_token):
    # id tail after the color/sheet token, e.g. ..._01_white_<suf>  or  ..._01_c1_<suf>
    m = re.search(fam_token + r"_(.+)$", bid)
    return m.group(1) if m else None

# ---- SMARTER NEWBURBS WALL GROUPING: group by PIECE TYPE within each color (not one giant
# per-color group). Returns (type_key, label_suffix). Roof slope walls split by FACING:
#   slope 1-3 = N/W, slope 4-6 = S/E; steep slope 1-6 = N/W, steep 7-12 = S/E (user spec).
def newburbs_wall_group_type(suf):
    if suf is None:
        return ("misc", "Misc")
    # window variants -> Window Frames
    if suf == "window" or suf.startswith("wide_window_") or suf == "tall_window" or suf.startswith("wide_tall_"):
        return ("windows", "Window Frames")
    # door frame + garage frame variants -> Door Frames
    if suf == "doorframe" or suf.startswith("garage_"):
        return ("doorframes", "Door Frames")
    # plain walls (incl roof-trim wall_b/c/d)
    if suf == "wall" or suf in ("wall_b", "wall_c", "wall_d"):
        return ("walls", "Walls")
    if suf in ("corner",):
        return ("corners", "Corners")
    if suf in ("pillar", "pillar_b"):
        return ("pillars", "Pillars")
    # roof slope walls split by facing
    m = re.match(r"roof_slope_(\d+)$", suf)
    if m:
        n = int(m.group(1))
        return ("roof_slope_nw", "Roof Slope Walls N/W") if n <= 3 else ("roof_slope_se", "Roof Slope Walls S/E")
    m = re.match(r"roof_steep_slope_(\d+)$", suf)
    if m:
        n = int(m.group(1))
        return ("roof_steep_nw", "Roof Steep Slope Walls N/W") if n <= 6 else ("roof_steep_se", "Roof Steep Slope Walls S/E")
    if suf.startswith("roof_end_"):
        return ("roof_ends", "Roof Ends")
    if suf.startswith("roof_steep_end_"):
        return ("roof_steep_ends", "Roof Steep Ends")
    return (suf, suf.replace("_", " ").title())

def process_newburbs_by_color(fn, d, interiors):
    """27/28: category=WALLS_CAT. ONE subcategory per file (NOT per color): interiors ->
    'Newburbs Interior', exterior walls -> 'Newburbs Exterior'. Color is still used for the
    original-vocab displayName and the per-color group name; only the SUBCATEGORY is collapsed
    (per-color subcats flooded the menu list -- user: 'thats too much')."""
    cat = CATEGORY[fn]
    color_fn = COLOR_SUBCAT[fn]
    bs = d["buildables"]
    joiner = " " if interiors else " Clapboard "  # interiors: '<Color> Wall'; walls: '<Color> Clapboard Wall'
    fixed_sub = "Newburbs Interior" if interiors else "Newburbs Exterior"
    meta = {}   # id(b) -> (color, gtype, glabel)
    for b in bs:
        b["category"] = cat
        color = color_fn(b) or strip_tikitown(b.get("subcategory"))
        b["subcategory"] = fixed_sub
        # derive suffix
        if interiors:
            suf = _newburbs_suffix(b["id"], r"tt_newburbs_interiors_\d+_c\d+")
        else:
            m = re.search(r"tt_newburbs_walls_\d+_[a-z]+", b["id"])
            suf = b["id"][m.end()+1:] if m else None
        gtype, glabel = newburbs_wall_group_type(suf)
        meta[id(b)] = (color, gtype, glabel)
        tw = None; q = None
        if suf in NEWBURBS_SUFFIX_NAME:
            tw, q = NEWBURBS_SUFFIX_NAME[suf]
        elif suf:
            tw = _roof_typeword(suf)
        if tw:
            b["displayName"] = f"{color}{joiner}{tw}" + (f" - {q}" if q else "")
    # group per (COLOR, PIECE TYPE) -> small cycles instead of one 15/46-deep per-color group.
    # Group label: '<Color>[ Clapboard] <TypeLabel>' (e.g. 'White Clapboard Window Frames',
    # 'Blue Roof Slope Walls N/W'). Singletons (e.g. a lone Corner) get NO group.
    tag = "interiors" if interiors else "walls"
    mat = "" if interiors else " Clapboard"
    bykey = collections.OrderedDict()
    for b in bs:
        color, gtype, glabel = meta[id(b)]
        bykey.setdefault((color, gtype, glabel), []).append(b)
    ngroups = 0
    for (color, gtype, glabel), members in bykey.items():
        if len(members) < 2:
            members[0].pop("group", None)
            continue
        sl = slug(f"newburbs_{tag}::{color}::{gtype}")
        gid = f"worldessentials.tikitown.family_{sl}"
        tkey = f"IGUI_WETiki_family_{sl}"
        gname = f"{color}{mat} {glabel}"
        for i, m in enumerate(members):
            m["group"] = {"id": gid, "name": gname, "translationKey": tkey, "level": i + 1}
        ngroups += 1
    report.append((fn, len(bs), ngroups, 0))

def process_garages(fn, d):
    """Garages: only set category/subcategory + strip TikiTown. Keep existing groups/structure."""
    cat = CATEGORY[fn]
    for b in d["buildables"]:
        b["category"] = cat
        b["subcategory"] = strip_tikitown(b.get("subcategory"))  # 'TikiTown Garage Doors' -> 'Garage Doors'
    report.append((fn, len(d["buildables"]), "KEPT-EXISTING-GROUPS", 0))

# ---- COUNTER SCHEMA ALIGNMENT (file 23) ----
# Match the live KBW wooden-counter schema (KBW_VE Dark Oak Counter, containers/extended_storage.json)
# for every Counters-subcategory buildable: category Containers, material Wood, KBW construction,
# kbwve.extended.wood material group + FineWoodWorking knowledge gate, explicit container:counter.
# Preserves each piece's geometry (incl 2-face floating counters), group, object flags, sprites.
# Runs AFTER process_grouped so it overrides the generic Furniture/Appliances treatment.
COUNTER_CONSTRUCTION = {
    "time": 75,
    "timedAction": "BuildWoodenStructureMedium",
    "completionSound": "BuildWoodenStructureMedium",
    "category": "Furniture",
    "xp": {"Woodwork": 40},
}
COUNTER_REQUIREMENTS = {
    "materials": "kbwve.extended.wood",
    "skills": {"Woodwork": 4},
    "knowledge": {
        "recipes": ["KBWKnowledge_FineWoodWorking_Furniture_Counters"],
        "hideUntilLearned": True,
        "needToBeLearned": True,
        "sources": [{"type": "magazine", "item": "KnoxBuildworks.FineWoodWorking_Furniture_Counters"}],
        "skillAlternatives": [{"mode": "all", "skills": {"Woodwork": 6}}],
    },
}
def counter_schema_pass(d):
    n = 0
    for b in d["buildables"]:
        if (b.get("subcategory") or "") != "Counters":
            continue
        b["category"] = "Containers"
        b["material"] = "Wood"
        b["materialTags"] = ["Wood"]
        b["tooltipKey"] = "Tooltip_KBW_Shared_StorageFixture"
        b["allowSpriteReuse"] = True
        st = b["stages"][0]
        st["construction"] = dict(COUNTER_CONSTRUCTION)
        st["requirements"] = json.loads(json.dumps(COUNTER_REQUIREMENTS))  # deep copy
        # keep existing object flags but ensure isThumpable; counters are storage
        obj = st.get("object", {}) or {}
        obj["isThumpable"] = True
        st["object"] = obj
        st["container"] = {"type": "counter"}
        n += 1
    report.append(("23 counter-schema-pass", n, "Containers/Counters KBW schema", 0))
    return n

FILES = {
    "21_tikitown_walls.json": dict(),
    "22_tikitown_doors.json": dict(),
    "23_tikitown_furniture.json": dict(submap=SUBMAP_23),
    "24_tikitown_bookshelves.json": dict(submap={"Shelving (fill-overlay)": "Storage"}),
    "25_tikitown_bedroom.json": dict(bedroom=True, submap=SUBMAP_25),
    "26_tikitown_glass.json": dict(),
    "27_tikitown_newburbs_interiors.json": dict(),
    "28_tikitown_newburbs_walls.json": dict(),
}

NEWBURBS_BYCOLOR = {
    "27_tikitown_newburbs_interiors.json": True,   # interiors (no 'Clapboard')
    "28_tikitown_newburbs_walls.json": False,      # exterior clapboard walls
}

def main():
    """Rewrites the TikiTown source JSONs in place. Only runs when executed directly, so importing
    this module (e.g. for fix_bedroom_name) never re-applies the pass."""
    for fn, kw in FILES.items():
        p = os.path.join(DIR, fn)
        d = json.load(open(p, encoding="utf-8"))
        # also set file-level category (26 had None)
        d["category"] = CATEGORY[fn]
        if fn == "25_tikitown_bedroom.json":
            process_bedroom(fn, d, submap=kw.get("submap"))
        elif fn in NEWBURBS_BYCOLOR:
            process_newburbs_by_color(fn, d, interiors=NEWBURBS_BYCOLOR[fn])
        else:
            process_grouped(fn, d, bedroom=False, submap=kw.get("submap"))
        # file 23: align Counters-subcategory buildables to the KBW counter schema (durable).
        if fn == "23_tikitown_furniture.json":
            counter_schema_pass(d)
        json.dump(d, open(p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    # garages
    fn = "29_tikitown_garages.json"
    p = os.path.join(DIR, fn)
    d = json.load(open(p, encoding="utf-8"))
    d["category"] = CATEGORY[fn]
    process_garages(fn, d)
    json.dump(d, open(p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    out = open(r"c:\Users\josep\Kiro\pz_craft_loops\_catpass_report.txt", "w", encoding="utf-8")
    out.write("file | buildables | grouped-families | singletons\n")
    for r in report:
        out.write(" | ".join(str(x) for x in r) + "\n")
    out.close()
    print("done")


if __name__ == "__main__":
    main()
