# -*- coding: utf-8 -*-
"""Give our functional appliances the exact cost of the KBW Vanilla Expanded appliance they behave
like (re-runnable; re-run if KBW changes those recipes).

Our pieces copy their function from a vanilla tile (kbw_tilepatch._VANILLA_COPIES), so they should
cost what KBW charges for building that same vanilla appliance:
  ice machine  -> vanilla chest freezer (appliances_refrigeration_01_48) -> KBW VE Chest Freezer
  deep fryer   -> vanilla electric oven (appliances_cooking_01_0)        -> KBW VE Green Oven
Copies: stage requirements (materials, skills, magazine knowledge, extra parts) and the template's
construction (time, action, XP). Writes the Community deliverable in its own JSON formatting.
"""
import os, sys, json, copy

VE = (r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600\3772269882\mods"
      r"\KnoxBuildworks_Vanilla_Expanded\42\media\KnoxBuildworks\definitions\appliances")
OURS = r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables\57_community_tk_kitchen_misc.json"
# our id -> (KBW VE file, KBW VE buildable id)
MATCH = {
    "community.tk.kitchen_misc.ice_machine":
        ("refrigeration.json", "kbw.vanillaexpanded.appliances.refrigeration.chest_freezer"),
    "community.tk.kitchen_misc.deep_fryer":
        ("cooking.json", "kbw.vanillaexpanded.appliances.cooking.green_oven"),
}


def _kbw(fname, bid):
    d = json.load(open(os.path.join(VE, fname), encoding="utf-8-sig"))
    b = next(x for x in d["buildables"] if x["id"] == bid)
    templates = {}
    for f in os.listdir(VE):   # templates can live in any VE appliance file (cooking.json has them)
        templates.update(json.load(open(os.path.join(VE, f), encoding="utf-8-sig")).get("templates", {}))
    construction = b.get("construction") or templates[b["extends"]]["construction"]
    return b["stages"][0]["requirements"], construction


# ---- Higher-capacity ice machine tiers (2026-11-02) --------------------------------------------
# Same tile as the base ice machine. Capacity is set the way the Dirkies military crate does it:
# stage "container": {"capacity": N}; KBW's Properties.lua calls part:getContainer():setCapacity(N)
# on the built object (crate confirmed in game: holds 100). 100 is the game's per-container cap.
# Amounts are hand-balanced for carrying (user, 2026-11-02): an average player carries about 75
# weight, so the 100 tier stays just under it. Blowtorch uses stay at the base 5 (a torch holds 10);
# rods and refrigerant stay within one pack/bottle (20 / 10 uses). One compressor at every tier.
# Skills: all of our ice machines are one level above KBW's chest freezer, +1 per tier.
# Build time stays 200 for all (user).
BASE_ID = "community.tk.kitchen_misc.ice_machine"
GROUP = {"id": "kbwcb.appliances.ice_machines", "translationKey": "IGUI_KBWCB_Group_IceMachines",
         "name": "Commercial Ice Machine"}
BASE_SKILLS = (5, 4, 8)   # base ice machine: MetalWelding, Electricity, Electricity without the magazine
# TWO-STAGE (2026-11-02): each tier is built as a shell (stage 1: inert art from our generated
# KBWCommunityIceShell sheet, metal body + insulation, Metalworking only) and then the finished
# ice machine built ON that shell (stage 2: refrigeration + electronics, full skills). KBW
# `previousStage` makes stage 2 placeable only on its own shell (same tile, same facing) and
# replaces the shell. Each build has its own ~75 carry-weight budget.
TIERS = [  # (capacity, id suffix, name, MetalWelding, Electricity, alt Electricity,
           #  shell name, shell xp, shell amounts, unit xp, unit amounts)
    (65, "_65", "Large Commercial Ice Machine", 6, 5, 9,
     "Large Ice Machine Shell", {"MetalWelding": 60},
     {"Base.BlowTorch": 5, "Base.WeldingRods": 10, "Base.SheetMetal": 16, "Base.MetalPipe": 4,
      "Base.Screws": 40, "KnoxBuildworks.InsulationFoam": 6, "KnoxBuildworks.PlasticSheet": 4,
      "KnoxBuildworks.RubberSeal": 4},
     {"MetalWelding": 40, "Electricity": 35},
     {"Base.BlowTorch": 5, "Base.WeldingRods": 5, "Base.SheetMetal": 4, "Base.Screws": 20,
      "Base.ElectronicsScrap": 80, "Base.ElectricWire": 10, "KnoxBuildworks.RefrigeratorCompressor": 1,
      "KnoxBuildworks.RefrigerantBottle": 5, "KnoxBuildworks.ThinCopperPipe": 6}),
    (100, "_100", "Industrial Ice Machine", 7, 6, 10,
     "Industrial Ice Machine Shell", {"MetalWelding": 90},
     {"Base.BlowTorch": 5, "Base.WeldingRods": 15, "Base.SheetMetal": 20, "Base.MetalPipe": 6,
      "Base.Screws": 60, "KnoxBuildworks.InsulationFoam": 8, "KnoxBuildworks.PlasticSheet": 6,
      "KnoxBuildworks.RubberSeal": 6},
     {"MetalWelding": 60, "Electricity": 55},
     {"Base.BlowTorch": 5, "Base.WeldingRods": 10, "Base.SheetMetal": 6, "Base.Screws": 30,
      "Base.ElectronicsScrap": 140, "Base.ElectricWire": 16, "KnoxBuildworks.RefrigeratorCompressor": 1,
      "KnoxBuildworks.RefrigerantBottle": 9, "KnoxBuildworks.ThinCopperPipe": 10}),
]
SHELL_OBJECT = {"isThumpable": True, "dismantable": True, "blockAllSquare": True}   # NOT isProp:
# Placement.findPrevious only matches IsoThumpable objects, so a prop shell could never be finished.
# item weights (game / KBW item scripts, 2026-11-02); drainables count once (one torch/pack/bottle)
WEIGHT = {"Base.SheetMetal": 2.0, "Base.MetalPipe": 1.5, "Base.ElectronicsScrap": 0.1, "Base.ElectricWire": 0.1, "Base.Screws": 0.05,
          "KnoxBuildworks.RefrigeratorCompressor": 5.0, "KnoxBuildworks.InsulationFoam": 0.9,
          "KnoxBuildworks.ThinCopperPipe": 1.25, "KnoxBuildworks.RubberSeal": 0.5,
          "KnoxBuildworks.PlasticSheet": 1.5}
DRAIN_WEIGHT = {"Base.BlowTorch": 1.0, "Base.WeldingRods": 1.5, "KnoxBuildworks.RefrigerantBottle": 1.0}
TOOLS_WEIGHT = 0.5   # screwdriver (welding mask is worn)


def _rows_for(amounts, templates):
    """Requirement rows for exactly the items in `amounts` (plus every tool row), built from the
    KBW chest-freezer rows so ids/roles/modes match KBW's. Items KBW's recipe lacks (metal pipe)
    get a plain consume row."""
    out = [copy.deepcopy(t) for t in templates if t.get("role") == "tool"]
    by_item = {(t.get("items") or [None])[0]: t for t in templates if t.get("role") != "tool"}
    for item, n in amounts.items():
        t = copy.deepcopy(by_item.get(item) or {"id": "kbwcb_" + item.split(".")[-1].lower(),
                                               "role": "material", "mode": "consume", "items": [item]})
        if "uses" in t:
            t["uses"] = n
        else:
            t["amount"] = n
        out.append(t)
    return out


# (2026-08-28, user) KBW-only parts spawn far too rarely for our fridge / freezer tiers, so their
# amounts are HALVED (round down, min 1) in build_fridge_defs and build_freezer_tiers. Vanilla
# metal costs untouched; the compressor is already 1.
HALVE_KBW_PARTS = ("KnoxBuildworks.InsulationFoam", "KnoxBuildworks.PlasticSheet",
                   "KnoxBuildworks.RubberSeal", "KnoxBuildworks.RefrigerantBottle",
                   "KnoxBuildworks.ThinCopperPipe")   # KBW item, not vanilla metal (user)
# Also applied to the ice machines (build_freezer_tiers), incl. the base 30 (own group below).


def _halve_kbw(amounts):
    """Halve the KBW parts: round DOWN, minimum 1 (user)."""
    return {k: (max(1, v // 2) if k in HALVE_KBW_PARTS else v) for k, v in amounts.items()}


def _carry_weight(entries):
    w = TOOLS_WEIGHT
    for e in entries:
        item = (e.get("items") or [None])[0]
        if item in DRAIN_WEIGHT:
            w += DRAIN_WEIGHT[item]
        elif item in WEIGHT:
            w += WEIGHT[item] * e.get("amount", 1)
    return w


def _skills(r, mw, el, alt):
    r["skills"] = {"MetalWelding": mw, "Electricity": el}
    r["knowledge"]["skillAlternatives"] = [{"mode": "all", "skills": {"MetalWelding": mw, "Electricity": alt}}]


def build_freezer_tiers(doc):
    req, cons = _kbw(*MATCH[BASE_ID])
    groups = json.load(open(os.path.join(VE, "refrigeration.json"), encoding="utf-8-sig"))["materialGroups"]
    base_group = groups[req["materials"]]
    bs = doc["buildables"]
    base = next(b for b in bs if b["id"] == BASE_ID)
    base["group"] = dict(GROUP, level=1)
    # all cold storage in one tab: KBW VE files its refrigerators under Appliances > Refrigeration,
    # as do our fridge / freezer tiers. Shells and tiers below are copies of base, so they follow.
    base["category"], base["subcategory"] = "Appliances", "Refrigeration"
    _skills(base["stages"][0]["requirements"], *BASE_SKILLS)
    report = ["%s: capacity 30, MW%d+E%d (alt E%d), carry weight %.1f" % (
        (BASE_ID,) + BASE_SKILLS + (_carry_weight(base_group + req.get("inputs", [])),))]
    from kbw_tilepatch import iceshell_name
    templates = base_group + req.get("inputs", [])
    doc.setdefault("materialGroups", {})
    # drop groups from the single-stage version (freezer65 / freezer100) if present
    for old in ("kbwcb.appliance.freezer65", "kbwcb.appliance.freezer100"):
        doc["materialGroups"].pop(old, None)
    # base 30: own group = KBW chest-freezer recipe with the KBW parts halved (user 2026-08-28)
    base30 = {}
    for row in templates:
        if row.get("role") != "tool":
            base30[row["items"][0]] = row.get("uses", row.get("amount", 1))
    doc["materialGroups"]["kbwcb.appliance.freezer30"] = _rows_for(_halve_kbw(base30), templates)
    br = base["stages"][0]["requirements"]
    br["materials"], br["inputs"] = "kbwcb.appliance.freezer30", []
    report.append("%s: own group kbwcb.appliance.freezer30 (KBW parts halved), carry weight %.1f" % (
        BASE_ID, _carry_weight(doc["materialGroups"]["kbwcb.appliance.freezer30"])))

    def put(t, after_id):
        i = next((k for k, b in enumerate(bs) if b["id"] == t["id"]), None)
        if i is None:
            j = next(k for k, b in enumerate(bs) if b["id"] == after_id)
            bs.insert(j + 1, t)
        else:
            bs[i] = t

    level, prev = 2, BASE_ID
    for cap, suf, name, mw, el, alt, sname, sxp, samounts, uxp, uamounts in TIERS:
        shell_id = BASE_ID + suf + "_shell"
        # ---- stage 1: shell
        sh = copy.deepcopy(base)
        sh["id"] = shell_id
        sh["translationKey"] = base["translationKey"] + suf + "_shell"
        sh["displayName"] = sname
        sh["iconSprite"] = iceshell_name(int(base["iconSprite"].rsplit("_", 1)[1]))
        sh["group"] = dict(GROUP, level=level)
        sh["construction"] = dict(copy.deepcopy(cons), xp=sxp)
        st = sh["stages"][0]
        for face in st["geometry"]["faces"].values():
            for L in face["layers"]:
                L["rows"] = [[iceshell_name(int(c.rsplit("_", 1)[1])) for c in row] for row in L["rows"]]
        st["object"] = dict(SHELL_OBJECT)
        st.pop("container", None)
        gname = "kbwcb.appliance.iceshell%d" % cap
        doc["materialGroups"][gname] = _rows_for(_halve_kbw(samounts), templates)
        r = copy.deepcopy(req)
        r["materials"], r["inputs"] = gname, []
        r["skills"] = {"MetalWelding": mw}
        r["knowledge"]["skillAlternatives"] = [{"mode": "all", "skills": {"MetalWelding": mw, "Electricity": alt}}]
        st["requirements"] = r
        put(sh, prev)
        report.append("%s: shell, MW%d, xp %s, carry weight %.1f" % (
            shell_id, mw, sxp, _carry_weight(doc["materialGroups"][gname])))
        # ---- stage 2: the working ice machine, built on its shell
        t = copy.deepcopy(base)
        t["id"] = BASE_ID + suf
        t["translationKey"] = base["translationKey"] + suf
        t["displayName"] = name
        t["group"] = dict(GROUP, level=level + 1)
        t["construction"] = dict(copy.deepcopy(cons), xp=uxp)          # time stays 200
        gname = "kbwcb.appliance.freezer%d" % cap
        doc["materialGroups"][gname] = _rows_for(_halve_kbw(uamounts), templates)
        r = copy.deepcopy(req)
        r["materials"], r["inputs"] = gname, []
        _skills(r, mw, el, alt)
        t["stages"][0]["requirements"] = r
        t["stages"][0]["container"] = {"capacity": cap}
        t["stages"][0]["previousStage"] = shell_id
        put(t, shell_id)
        report.append("%s: capacity %d on %s, MW%d+E%d (alt E%d), xp %s, carry weight %.1f" % (
            t["id"], cap, shell_id, mw, el, alt, uxp, _carry_weight(doc["materialGroups"][gname])))
        level, prev = level + 2, t["id"]
    return report


# ---- Fridge / freezer tiers (EXPERIMENT 2026-11-02, test bundle only until confirmed) ---------
# User spec (2026-11-02):
#  * the 8 standard 1-tile KBW VE refrigerators: 3 tiers 60/30, 80/40, 100/50 (fridge/freezer)
#  * Mini Refrigerator: 30/8, 40/12, 50/15. Trailer Built-In Fridge: untouched.
#  * Industrial + White Industrial also get FREEZER-ONLY variants (both compartments freeze):
#    30/30, 65/65, 100/100, cost / XP like the ice machine tiers, skills on the fridge ladder.
#  * Chest Freezer: 65 and 100, exactly like the ice machine tiers (KBW's own covers 30).
#  * Tier 1 = single build; tiers 2 and 3 = two-stage (inert shell, then the unit built on it).
#  * Skills +1 per tier: fridges MW6+E4 / MW7+E5 / MW8+E6, mini MW4+E4 / MW5+E5 / MW6+E6,
#    no-magazine alternatives E8 / E9 / E10. Build time 200, blowtorch 5 uses, each stage < 75 weight.
# Capacities: fridges via kbwcbContainerCapacity (both compartments); freezer-only adds
# kbwcbContainerTypes {"fridge": "freezer"}; chest freezer via KBW's own container.capacity
# (single container, same as the ice machines). Shell art: kbw_tilepatch.fridge_shell_name.
_KBW_VE_REFRIG = "kbw.vanillaexpanded.appliances.refrigeration."
_ICE30 = None   # = KBW VE refrigerator recipe (materials + inputs), resolved in build_fridge_defs
_ICE65_SHELL, _ICE65_UNIT, _ICE65_SXP, _ICE65_UXP = TIERS[0][8], TIERS[0][10], TIERS[0][7], TIERS[0][9]
_ICE100_SHELL, _ICE100_UNIT, _ICE100_SXP, _ICE100_UXP = TIERS[1][8], TIERS[1][10], TIERS[1][7], TIERS[1][9]
_FRIDGE_T1 = {"Base.BlowTorch": 5, "Base.WeldingRods": 8, "Base.SheetMetal": 12, "Base.Screws": 30,
              "Base.ElectronicsScrap": 45, "Base.ElectricWire": 6, "KnoxBuildworks.RefrigeratorCompressor": 1,
              "KnoxBuildworks.RefrigerantBottle": 3, "KnoxBuildworks.InsulationFoam": 3,
              "KnoxBuildworks.ThinCopperPipe": 3, "KnoxBuildworks.RubberSeal": 3, "KnoxBuildworks.PlasticSheet": 3}
_MINI_T1 = {"Base.BlowTorch": 5, "Base.WeldingRods": 6, "Base.SheetMetal": 10, "Base.Screws": 25,
            "Base.ElectronicsScrap": 40, "Base.ElectricWire": 5, "KnoxBuildworks.RefrigeratorCompressor": 1,
            "KnoxBuildworks.RefrigerantBottle": 2, "KnoxBuildworks.InsulationFoam": 3,
            "KnoxBuildworks.ThinCopperPipe": 2, "KnoxBuildworks.RubberSeal": 2, "KnoxBuildworks.PlasticSheet": 2}
_MINI_T2_SHELL = {"Base.BlowTorch": 5, "Base.WeldingRods": 6, "Base.SheetMetal": 10, "Base.MetalPipe": 2,
                  "Base.Screws": 25, "KnoxBuildworks.InsulationFoam": 4, "KnoxBuildworks.PlasticSheet": 2,
                  "KnoxBuildworks.RubberSeal": 2}
_MINI_T2_UNIT = {"Base.BlowTorch": 5, "Base.WeldingRods": 3, "Base.SheetMetal": 2, "Base.Screws": 10,
                 "Base.ElectronicsScrap": 50, "Base.ElectricWire": 6, "KnoxBuildworks.RefrigeratorCompressor": 1,
                 "KnoxBuildworks.RefrigerantBottle": 3, "KnoxBuildworks.ThinCopperPipe": 3}
_MINI_T3_SHELL = {"Base.BlowTorch": 5, "Base.WeldingRods": 8, "Base.SheetMetal": 12, "Base.MetalPipe": 3,
                  "Base.Screws": 30, "KnoxBuildworks.InsulationFoam": 5, "KnoxBuildworks.PlasticSheet": 3,
                  "KnoxBuildworks.RubberSeal": 3}
_MINI_T3_UNIT = {"Base.BlowTorch": 5, "Base.WeldingRods": 4, "Base.SheetMetal": 3, "Base.Screws": 15,
                 "Base.ElectronicsScrap": 60, "Base.ElectricWire": 8, "KnoxBuildworks.RefrigeratorCompressor": 1,
                 "KnoxBuildworks.RefrigerantBottle": 4, "KnoxBuildworks.ThinCopperPipe": 4}

# tier = (capacities, MW, E, alt E, single amounts | None, shell amounts, shell xp, unit amounts, unit xp)
#   capacities: (fridge, freezer) for fridges / freezer-only, (freezer,) for the chest freezer
_FRIDGE_TIERS = [
    ((60, 30), 6, 4, 8, _FRIDGE_T1, None, None, None, None),
    ((80, 40), 7, 5, 9, None, _ICE65_SHELL, _ICE65_SXP, _ICE65_UNIT, _ICE65_UXP),
    ((100, 50), 8, 6, 10, None, _ICE100_SHELL, _ICE100_SXP, _ICE100_UNIT, _ICE100_UXP),
]
_MINI_TIERS = [
    ((30, 8), 4, 4, 8, _MINI_T1, None, None, None, None),
    ((40, 12), 5, 5, 9, None, _MINI_T2_SHELL, {"MetalWelding": 40}, _MINI_T2_UNIT,
     {"MetalWelding": 30, "Electricity": 25}),
    ((50, 15), 6, 6, 10, None, _MINI_T3_SHELL, {"MetalWelding": 55}, _MINI_T3_UNIT,
     {"MetalWelding": 40, "Electricity": 35}),
]
_FREEZER_ONLY_TIERS = [   # ice machine cost / XP, both compartments; skills on the FRIDGE ladder
    # (user 2026-11-02: line the freezer-only skills up with the fridges they are built from)
    ((30, 30), 6, 4, 8, "ICE30", None, None, None, None),
    ((65, 65), 7, 5, 9, None, _ICE65_SHELL, _ICE65_SXP, _ICE65_UNIT, _ICE65_UXP),
    ((100, 100), 8, 6, 10, None, _ICE100_SHELL, _ICE100_SXP, _ICE100_UNIT, _ICE100_UXP),
]
_CHEST_TIERS = [          # ice machine tiers 65 / 100 (KBW's Chest Freezer is the 30)
    ((65,), 6, 5, 9, None, _ICE65_SHELL, _ICE65_SXP, _ICE65_UNIT, _ICE65_UXP),
    ((100,), 7, 6, 10, None, _ICE100_SHELL, _ICE100_SXP, _ICE100_UNIT, _ICE100_UXP),
]
# (KBW VE id suffix, our id stem, display name stem, tiers, kind)
FRIDGE_PRODUCTS = [(s, s, n, _FRIDGE_TIERS, "fridge") for s, n in (
    ("white_refrigerator", "White Refrigerator"), ("blue_refrigerator", "Blue Refrigerator"),
    ("steel_refrigerator", "Steel Refrigerator"), ("green_refrigerator", "Green Refrigerator"),
    ("industrial_refrigerator", "Industrial Refrigerator"), ("plain_refrigerator", "Plain Refrigerator"),
    ("red_refrigerator", "Red Refrigerator"),
    ("white_industrial_refrigerator", "White Industrial Refrigerator"))] + [
    ("mini_refrigerator", "mini_refrigerator", "Mini Refrigerator", _MINI_TIERS, "fridge"),
    ("industrial_refrigerator", "industrial_freezer", "Industrial Freezer", _FREEZER_ONLY_TIERS, "freezer2"),
    ("white_industrial_refrigerator", "white_industrial_freezer", "White Industrial Freezer",
     _FREEZER_ONLY_TIERS, "freezer2"),
    ("chest_freezer", "chest_freezer", "Chest Freezer", _CHEST_TIERS, "freezer1"),
]
FRIDGE_ID_PREFIX = "kbwcb.appliances."
TOOLTIP_FRIDGE_SHELL = ("Tooltip_KBWCB_FridgeShell",
                        "Unfinished refrigerator casing. Build the matching refrigerator on it to finish it.")
TOOLTIP_FREEZER_SHELL = ("Tooltip_KBWCB_FreezerShell",
                         "Unfinished freezer casing. Build the matching freezer on it to finish it.")


def _cap_label(caps):
    return "/".join(str(c) for c in caps)


def build_fridge_defs():
    """(buildables, materialGroups, tooltip texts, report) for every fridge / freezer tier."""
    from kbw_tilepatch import fridge_shell_name
    doc = json.load(open(os.path.join(VE, "refrigeration.json"), encoding="utf-8-sig"))
    tmpl = {}
    for f in os.listdir(VE):
        tmpl.update(json.load(open(os.path.join(VE, f), encoding="utf-8-sig")).get("templates", {}))
    by_id = {b["id"]: b for b in doc["buildables"]}
    chest_req, _ = _kbw(*MATCH[BASE_ID])
    templates = doc["materialGroups"][chest_req["materials"]] + chest_req.get("inputs", [])
    ice30 = {}
    for row in templates:
        if row.get("role") != "tool":
            ice30[row["items"][0]] = row.get("uses", row.get("amount", 1))
    out, mg, report = [], {}, []
    tooltips = dict([TOOLTIP_FRIDGE_SHELL, TOOLTIP_FREEZER_SHELL])

    def base_copy(kb_suffix):
        b = copy.deepcopy(by_id[_KBW_VE_REFRIG + kb_suffix])
        for k, v in tmpl[b.pop("extends")].items():     # inline KBW's template
            b.setdefault(k, copy.deepcopy(v))
        b.pop("group", None)
        b["tags"] = ["community-tilepack", "kitchen", "refrigeration"]
        b["stages"][0]["allowSpriteReuse"] = True
        return b

    def requirements(base_req, gname, skills, mw, alt):
        r = copy.deepcopy(base_req)
        r["materials"], r["inputs"] = gname, []
        r["skills"] = skills
        r["knowledge"]["skillAlternatives"] = [{"mode": "all", "skills": {"MetalWelding": mw, "Electricity": alt}}]
        return r

    for kb_suffix, stem, name, tiers, kind in FRIDGE_PRODUCTS:
        base = base_copy(kb_suffix)
        base_req = base["stages"][0]["requirements"]
        # catalog card per product (tiers + shells in build order), like the ice machines
        group = {"id": FRIDGE_ID_PREFIX + stem + "_tiers",
                 "translationKey": "IGUI_KBWCB_Group_" + "".join(w.title() for w in stem.split("_")) + "Tiers",
                 "name": name}
        level = [0]

        def grouped(b):
            level[0] += 1
            b["group"] = dict(group, level=level[0])
            return b
        unit_tooltip = "Tooltip_KBW_Shared_Refrigerator" if kind == "fridge" else "Tooltip_KBW_Shared_Freezer"
        shell_tooltip = TOOLTIP_FRIDGE_SHELL[0] if kind == "fridge" else TOOLTIP_FREEZER_SHELL[0]
        for caps, mw, el, alt, single, shell_amt, shell_xp, unit_amt, unit_xp in tiers:
            label = _cap_label(caps)
            uid = FRIDGE_ID_PREFIX + "%s_%d" % (stem, caps[0])
            if kind == "fridge":
                props = {"kbwcbContainerCapacity": {"fridge": caps[0], "freezer": caps[1]}}
            elif kind == "freezer2":
                props = {"kbwcbContainerCapacity": {"fridge": caps[0], "freezer": caps[1]},
                         "kbwcbContainerTypes": {"fridge": "freezer"}}
            else:
                props = {"container": {"capacity": caps[0]}}
            # ---- the working unit
            u = copy.deepcopy(base)
            u["id"] = uid
            u["translationKey"] = "IGUI_" + uid.replace(".", "_")
            u["displayName"] = "%s %s" % (name, label)
            u["tooltipKey"] = unit_tooltip
            st = u["stages"][0]
            st.pop("container", None)
            st.update(copy.deepcopy(props))
            gname = "kbwcb.appliance.%s_%d" % (stem, caps[0])
            if single is not None:   # tier 1: one build
                amounts = ice30 if single == "ICE30" else single
                mg[gname] = _rows_for(_halve_kbw(amounts), templates)
                st["requirements"] = requirements(base_req, gname, {"MetalWelding": mw, "Electricity": el}, mw, alt)
                u["construction"] = copy.deepcopy(u["construction"])   # KBW's own (time 200) and XP
                out.append(grouped(u))
                report.append("%-52s %-8s MW%d+E%d (alt E%d) single, weight %.1f" % (
                    uid, label, mw, el, alt, _carry_weight(mg[gname])))
                continue
            # ---- stage 1: the shell
            sid = uid + "_shell"
            sh = copy.deepcopy(base)
            sh["id"] = sid
            sh["translationKey"] = "IGUI_" + sid.replace(".", "_")
            sh["displayName"] = "%s %s Shell" % (name, label)
            sh["tooltipKey"] = shell_tooltip
            sh["iconSprite"] = fridge_shell_name(int(sh["iconSprite"].rsplit("_", 1)[1]))
            sh["construction"] = dict(copy.deepcopy(sh["construction"]), xp=shell_xp)
            sst = sh["stages"][0]
            for face in sst["geometry"]["faces"].values():
                for L in face["layers"]:
                    L["rows"] = [[fridge_shell_name(int(c.rsplit("_", 1)[1])) for c in row] for row in L["rows"]]
            sst["object"] = dict(SHELL_OBJECT)
            sst.pop("container", None)
            sg = gname + "_shell"
            mg[sg] = _rows_for(_halve_kbw(shell_amt), templates)
            sst["requirements"] = requirements(base_req, sg, {"MetalWelding": mw}, mw, alt)
            out.append(grouped(sh))
            # ---- stage 2: the unit, built on its shell
            mg[gname] = _rows_for(_halve_kbw(unit_amt), templates)
            st["requirements"] = requirements(base_req, gname, {"MetalWelding": mw, "Electricity": el}, mw, alt)
            st["previousStage"] = sid
            u["construction"] = dict(copy.deepcopy(u["construction"]), xp=unit_xp)
            out.append(grouped(u))
            report.append("%-52s %-8s MW%d+E%d (alt E%d) shell %.1f + unit %.1f weight" % (
                uid, label, mw, el, alt, _carry_weight(mg[sg]), _carry_weight(mg[gname])))
    for b in out:
        if b["construction"].get("time") != 200:
            raise RuntimeError("%s: build time %s, expected 200" % (b["id"], b["construction"].get("time")))
    for g, rows in mg.items():
        w = _carry_weight(rows)
        if w >= 75:
            raise RuntimeError("%s: carry weight %.1f over the 75 budget" % (g, w))
        for row in rows:
            if row.get("items") == ["Base.BlowTorch"] and row.get("uses") != 5:
                raise RuntimeError("%s: blowtorch uses %s, expected 5" % (g, row.get("uses")))
    return out, mg, tooltips, report


def main():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from export_repo import _json_style
    raw = open(OURS, "rb").read()
    style = _json_style(raw)
    doc = json.loads(raw.decode("utf-8-sig"))
    report = []
    for b in doc["buildables"]:
        if b["id"] not in MATCH:
            continue
        req, cons = _kbw(*MATCH[b["id"]])
        old = (b["stages"][0].get("requirements"), b.get("construction"))
        b["stages"][0]["requirements"] = copy.deepcopy(req)
        b["construction"] = copy.deepcopy(cons)
        report.append("%s <- %s (%s): %s" % (b["id"], MATCH[b["id"]][1],
                      "changed" if old != (req, cons) else "already matched", req["materials"]))
    report += build_freezer_tiers(doc)
    if style:
        indent, ascii_, seps, nl, tail, bom = style
        out = json.dumps(doc, indent=indent, ensure_ascii=ascii_, separators=seps).replace("\n", nl) + tail
        open(OURS, "wb").write((b"\xef\xbb\xbf" if bom else b"") + out.encode("utf-8"))
    else:
        json.dump(doc, open(OURS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print("\n".join(report))


if __name__ == "__main__":
    main()
