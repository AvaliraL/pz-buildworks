# -*- coding: utf-8 -*-
"""Name + tooltip pass for the Community and TikiTown buildables (2026-11-02).

Applied at build time by build_community_mod.py, build_tikitown_mod.py and
build_merged_test_mod.py, so the source deliverables stay untouched.

NAMES  - fixes by rule (doubled words, raw sheet names, cross-pack duplicates) and by id (pieces
         identified from their art). IG_UI must be written from the final displayName.
TOOLTIPS - KBW shows I18n.text(tooltipKey) as the build-menu description, then appends the
         storage lines itself (from the tile's `container`/ContainerCapacity), so tooltips never
         repeat the name or the capacity. One short sentence per piece TYPE, like KBW's own.
         Keys:
           * KBW-owned keys where the text fits (never shipped by us; KBW defines them),
           * our own `Tooltip_KBWCB_*` keys otherwise. We no longer use `Tooltip_WETiki_*`
             (WE's Knox Buildworks Expansion defines 379 of those itself) or the old
             `Tooltip_KBW_Shared_*` names (KBW's namespace).
"""
import re

PREFIX = "Tooltip_KBWCB_"

# ---------------------------------------------------------------- names
NAME_BY_ID = {
    # Dylan RandomFurniture03 lab furniture (art-checked; the pack only named the sheet)
    "community.dylan.containers.DylansRandomFurniture03_37": "Hydroponics Lab Bench",
    "community.dylan.containers.DylansRandomFurniture03_49": "Hydroponics Lab Bench (Open)",
    "community.dylan.containers.DylansRandomFurniture03_45": "Steel Lab Sink Counter",
    "community.dylan.containers.DylansRandomFurniture03_59": "Blue Lab Cabinet",
    "community.dylan.containers.DylansRandomFurniture03_34": "Steel Lab Hotplate Counter",
    "community.dylan.containers.DylansRandomFurniture03_54": "Glass Lab Shelving",
    "community.dylan.containers.DylansRandomFurniture03_60": "Glass Lab Shelving (Alt)",
    # Dylan GardenStuff02 trellis fencing
    "community.dylan.walls.DylansGardenStuff02_8": "Wooden Garden Trellis",
    "community.dylan.walls.DylansGardenStuff02_10": "Wooden Garden Trellis Corner",
    "community.dylan.walls.DylansGardenStuff02_11": "White Garden Trellis",
    "community.dylan.walls.DylansGardenStuff02_13": "White Garden Trellis Corner",
    # duplicates told apart by art
    "community.dylan.containers.DylansBar01_42": "Bar Counter (Corner)",
    "community.dylan.containers.Block_Trasher_51": "Blue Shop Counter",
    "community.dylan.containers.Block_Trasher_50": "Blue Shop Counter (Corner)",
    "community.dylan.containers.Bookies_Store_13": "Wooden Bookstore Shelf",
    "community.dylan.containers.Bookies_Store_45": "Metal Bookstore Shelf",
    "community.dylan.containers.Block_Trasher_60": "Angled Shop Display Shelf",
    "community.dirkies.secret_shelf.d_doors_02_68": "Secret Entrance Bookshelf (Half Empty)",
    # wrong object: the art is a wall-mounted fire extinguisher box (container extinguisher_box)
    "community.tk.containers.industry_tk_02_25": "Fire Extinguisher Cabinet",
    # TikiTown duplicates told apart by art
    "worldessentials.tikitown.walls_interior_bathroom_tterika_01_10": "Bathroom Wall - Style 6 (Door Frame, White)",
    "worldessentials.tikitown.walls_interior_bathroom_tterika_01_14": "Bathroom Wall - Style 6 (Door Frame, Beige)",
    "worldessentials.tikitown.walls_interior_bathroom_tterika_01_26": "Bathroom Wall - Style 6 (Door Frame, Grey)",
    "worldessentials.tikitown.walls_exterior_house_tterika_02_12": "Exterior Wall - Style 2 (Door Frame, Red Plank)",
    "worldessentials.tikitown.walls_exterior_house_tterika_02_25": "Exterior Wall - Style 2 (Door Frame, Grey)",
    "worldessentials.tikitown.walls_interior_house_tterika_02_12": "Interior Wall - Style 2 (Door Frame, Grey)",
    "worldessentials.tikitown.walls_interior_house_tterika_02_25": "Interior Wall - Style 2 (Door Frame, Light Grey)",
    "tikitown.newburbs_doors.tt_newburbs_doors_01_sliding_87": "Newburbs Sliding Glass Door Side Wall (Divided)",
}
# Newburbs clapboard wall variants (_b vent, _c utility box, _d small box; pillar_b is a thick post)
_CLAP_SUFFIX = {"_wall_b": " (Vent)", "_wall_c": " (Utility Box)", "_wall_d": " (Small Utility Box)",
                "_pillar_b": " (Thick)"}


def fix_name(b):
    bid, n = b.get("id", ""), b.get("displayName") or ""
    if bid in NAME_BY_ID:
        return NAME_BY_ID[bid]
    n = n.replace("Corner Wall Corner", "Corner Wall").replace("Corner Wall Pillar", "Corner Pillar")
    n = n.replace("Door Frame Frame", "Door Frame")
    # TK industrial blue is a paler, ribbed blue than Dirkies' (both were "Blue Industrial ...")
    if bid.startswith("community.tk.") and n.startswith("Blue Industrial"):
        n = "Pale " + n
    # Dirkies RUS sheet-03 uppers vs Dirkie sheet-01 uppers shared colour names
    if bid.startswith("community.dirkies.containers.edit_ddd_RUS_fixtures_counters_03_"):
        n = n.replace("Upper Cabinet", "Wall Cupboard")
    if bid.startswith("tikitown.newburbs_walls."):
        for suf, add in _CLAP_SUFFIX.items():
            if bid.endswith(suf) and not n.endswith(add):
                n += add
    # "Counter - Brown Countertop Modern Corner" -> "... Modern (Corner)" (same style as Community)
    if n.startswith("Counter - ") and n.endswith(" Corner"):
        n = n[:-len(" Corner")] + " (Corner)"
    return re.sub(r"\s+", " ", n).strip()


# ---------------------------------------------------------------- tooltips
KBW_KEYS = {  # type -> KBW-owned key (text confirmed in KBW's EN Tooltip.json, 2026-11-02)
    "Dresser": "Tooltip_KBW_Shared_Dresser",
    "Hedge": "Tooltip_KBW_Shared_Hedge",
    "Rug": "Tooltip_KBW_Shared_Rug",
    "Poster": "Tooltip_KBW_Shared_Poster",
    "Window": "Tooltip_KBW_Shared_Window",
    "Roof": "Tooltip_KBW_Shared_RoofSection",
}
TEXT = {
    "Wall": "{a}wall section.",
    "WallCorner": "{a}corner wall section.",
    "WallWindow": "{a}wall section with a window opening.",
    "WallDoorway": "{a}wall section with a doorway for a door.",
    "HalfWall": "Low glass wall section.",
    "Pillar": "Pillar for finishing wall ends and corners.",
    "Trellis": "Garden trellis fence section.",
    "GlassPanel": "Fixed glass panel that goes beside a sliding door.",
    "Door": "Door that opens and closes.",
    "GlassDoor": "Door with glass panes. Opens and closes.",
    "DoubleDoor": "One half of a double door. Build the left and right halves side by side.",
    "Gate": "Fence gate that opens and closes.",
    "GarageDoor": "Garage door for vehicle access.",
    "FenceHigh": "Tall fence section.",
    "FenceLow": "Low fence section.",
    "FenceTwoStorey": "Two-storey fence section.",
    "FenceCorner": "Corner fence section.",
    "FencePost": "Fence post for finishing fence ends.",
    "FenceHalf": "Half-width fence section for closing gaps.",
    "Counter": "Counter with storage underneath.",
    "UpperCabinet": "Wall-mounted cabinet. Can hang above a counter.",
    "BarCounter": "Bar counter with storage underneath.",
    "Pallet": "Pallet of goods. Can be used as storage.",
    "Crate": "Storage crate.",
    "StackCase": "Stackable storage case. Up to six can be stacked.",
    "Bin": "Waste bin. Items can be stored inside.",
    "Cabinet": "Cabinet for storing household items.",
    "Wardrobe": "Wardrobe for storing clothes.",
    "LabStorage": "Laboratory furniture with storage.",
    "Shelf": "Open shelving for storage.",
    "Bookshelf": "Bookshelf with storage.",
    "ToolStorage": "Metal tool storage.",
    "Medical": "Medical furniture with storage.",
    "ExtinguisherBox": "Wall-mounted fire extinguisher cabinet.",
    "KitchenShelf": "Wall-mounted kitchen shelf with storage.",
    "Storage": "Furniture with storage.",
    "Bed": "Bed for resting and sleeping.",
    "Desk": "Desk for an office or study.",
    "Table": "Table for placing items on.",
    "Workbench": "Workbench with storage.",
    "WorkshopEquipment": "Workshop equipment.",
    "IceMachine": "Commercial ice machine. Works as a freezer when powered.",
    "DeepFryer": "Commercial deep fryer. Cooks like an oven when powered.",
    "CoffeeMaker": "Counter-top coffee maker.",
    "Slicer": "Counter-top deli slicer.",
    "Viewscreen": "Wall-mounted viewscreen. Right-click it to change the image.",
    "Television": "Working television. Needs power to show a picture.",
    "Gym": "Gym equipment for decoration.",
    "Flag": "Decorative flag.",
    "Figure": "Decorative figure.",
    "Decoration": "Decorative piece.",
}
TYPE_BY_ID = {
    "community.dirkies.containers.furniture_storage_ddd_01_4": "StackCase",
    "community.dirkies.containers.furniture_storage_ddd_01_4.crate": "StackCase",
    "community.dirkies.containers.furniture_storage_ddd_01_9": "StackCase",
    "community.dirkies.containers.furniture_storage_ddd_01_9.crate": "StackCase",
    "community.tk.containers.industry_tk_02_25": "ExtinguisherBox",
    "community.tk.containers.kitchen_misc_tk_01_12": "Shelf",
    "community.tk.kitchen_misc.ice_machine": "IceMachine",
    "community.tk.kitchen_misc.ice_machine_65": "IceMachine",
    "community.tk.kitchen_misc.ice_machine_100": "IceMachine",
    "community.tk.kitchen_misc.deep_fryer": "DeepFryer",
    "community.tk.kitchen_misc.coffee_maker": "CoffeeMaker",
    "community.tk.kitchen_misc.coffee_machine": "CoffeeMaker",
    "community.tk.kitchen_misc.deli_slicer": "Slicer",
    "community.tk.kitchen_misc.wall_shelf": "KitchenShelf",
    "community.dylan.rf02.exercise_ball": "Gym",
    "community.dylan.rf02.punching_bag": "Gym",
}
SUB_TYPE = {
    "Counters": "Counter", "Upper Counters": "UpperCabinet", "Restaurant": "BarCounter",
    "Pallets": "Pallet", "Crates": "Crate", "Trash Cans": "Bin", "Cabinets": "Cabinet",
    "Wardrobes": "Wardrobe", "Dressers": "Dresser", "Lockers": "LabStorage", "Shelves": "Shelf",
    "Shelving": "Shelf", "Metal Containers": "ToolStorage", "Tool Cabinets": "ToolStorage",
    "Medical": "Medical", "Kitchen Storage": "KitchenShelf", "Storage": "Storage",
    "Beds": "Bed", "Desks": "Desk", "Tables": "Table", "Small Tables": "Table",
    "Space Viewscreens": "Viewscreen", "Frosted Panels": "Viewscreen", "Statues": "Figure",
    "Rugs": "Rug", "Hedges": "Hedge", "Posters": "Poster", "Newburbs Flags": "Flag",
    "Newburbs Windows": "Window", "Decor": "Decoration", "Radios & TVs": "Television",
}


def _wall_adj(sub):
    """'Brick Walls' -> 'Brick ', 'Newburbs Exterior' -> 'Newburbs exterior ', 'Walls' -> ''."""
    a = re.sub(r"\b(Walls?|Wall Finishes)\b", "", sub or "").strip()
    if not a:
        return ""
    words = a.split()
    words = [w if (i == 0 or w == "Newburbs") else w.lower() for i, w in enumerate(words)]
    return " ".join(words) + " "


def piece_type(b):
    """(type, wall-adjective) for one buildable."""
    bid = b.get("id", "")
    if bid in TYPE_BY_ID:
        return TYPE_BY_ID[bid], ""
    sub, cat = b.get("subcategory") or "", b.get("category") or ""
    n = (b.get("displayName") or "").lower()
    pc = b.get("pieceClass") or ""
    natives = [((st.get("nativeObject") or {}).get("type")) for st in b.get("stages") or []]
    if "television" in natives:
        return "Television", ""
    if sub in SUB_TYPE and not cat.startswith(("Walls", "Doors", "Fencing", "Roofing")):
        t = SUB_TYPE[sub]
        if t == "Shelf" and "bookshelf" in n:
            t = "Bookshelf"
        if t == "LabStorage" and "shelving" in n:
            t = "Shelf"
        return t, ""
    if sub == "Workbenches":
        return ("Workbench" if "workbench" in n else "WorkshopEquipment"), ""
    if "Roof" in sub or cat == "Roofing":
        return "Roof", ""
    if cat.startswith("Fencing"):
        if "post" in n: return "FencePost", ""
        if "corner" in n: return "FenceCorner", ""
        if "half" in n: return "FenceHalf", ""
        return {"Low": "FenceLow", "Two-Storey": "FenceTwoStorey"}.get(sub, "FenceHigh"), ""
    if cat.startswith("Doors"):
        if "side wall" in n: return "GlassPanel", ""
        if "frame" in n: return "WallDoorway", ""
        if "garage" in n or "Garage" in sub: return "GarageDoor", ""
        if "gate" in n or sub == "Gates": return "Gate", ""
        if "double" in n: return "DoubleDoor", ""
        if "glass" in n or sub == "Glass Doors": return "GlassDoor", ""
        return "Door", ""
    if cat.startswith("Walls") or "Wall" in sub:
        a = _wall_adj(sub)
        if "trellis" in n: return "Trellis", ""
        if "Half-Wall" in sub: return "HalfWall", ""
        if "door frame" in n or pc in ("doorframe", "door"): return "WallDoorway", a
        if "window" in n or pc in ("window", "windowsframe"): return "WallWindow", a
        if pc == "pillar" or "pillar" in n or "post" in n: return "Pillar", ""
        if pc == "corner" or "corner" in n: return "WallCorner", a
        return "Wall", a
    if cat.startswith("Windows"):
        return "Window", ""
    return SUB_TYPE.get(sub, "Decoration"), ""


def tooltip_for(b):
    """(key, text or None). text None = KBW-owned key, not shipped by us."""
    t, a = piece_type(b)
    if t in KBW_KEYS:
        return KBW_KEYS[t], None
    if "{a}" in TEXT[t] and a:
        key = PREFIX + t + "_" + re.sub(r"[^A-Za-z0-9]+", "", a.title())
        text = TEXT[t].format(a=a)
    else:
        key = PREFIX + t
        text = TEXT[t].format(a="")
    return key, text[0].upper() + text[1:]


def apply(buildables, tooltip_table, report=None):
    """Fix names + tooltipKeys in place; add our tooltip texts to tooltip_table.
    Returns (renamed, retooled) counts."""
    renamed = retooled = 0
    for b in buildables:
        new = fix_name(b)
        if new and new != b.get("displayName"):
            if report is not None:
                report.append("name  %s: %r -> %r" % (b.get("id"), b.get("displayName"), new))
            b["displayName"] = new
            renamed += 1
        key, text = tooltip_for(b)
        if b.get("tooltipKey") != key:
            b["tooltipKey"] = key
            retooled += 1
        if text is not None:
            tooltip_table[key] = text
    split_shared_keys(buildables, report)
    return renamed, retooled


def split_shared_keys(buildables, report=None):
    # One translationKey can only hold one name: pieces sharing a key but named differently
    # (e.g. TikiTown garage doors 2..6 wide) all showed the first name in game. Split them.
    by_tk = {}
    for b in buildables:
        if b.get("translationKey"):
            by_tk.setdefault(b["translationKey"], []).append(b)
    for tk, group in by_tk.items():
        if len({b.get("displayName") for b in group}) > 1:
            for b in group:
                b["translationKey"] = tk + "_" + re.sub(r"[^A-Za-z0-9]+", "_", b["id"].rsplit("_", 1)[-1])
                if report is not None:
                    report.append("key   %s: %s -> %s" % (b["id"], tk, b["translationKey"]))
