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
TIERS = [  # (capacity, id suffix, name, MetalWelding, Electricity, alt Electricity, xp, amounts)
    (65, "_65", "Large Commercial Ice Machine", 6, 5, 9, {"MetalWelding": 100, "Electricity": 35},
     {"Base.BlowTorch": 5, "Base.WeldingRods": 10, "Base.SheetMetal": 12, "Base.ElectronicsScrap": 60,
      "Base.ElectricWire": 8, "Base.Screws": 40, "KnoxBuildworks.RefrigeratorCompressor": 1,
      "KnoxBuildworks.RefrigerantBottle": 5, "KnoxBuildworks.InsulationFoam": 4,
      "KnoxBuildworks.ThinCopperPipe": 4, "KnoxBuildworks.RubberSeal": 4, "KnoxBuildworks.PlasticSheet": 3}),
    (100, "_100", "Industrial Ice Machine", 7, 6, 10, {"MetalWelding": 150, "Electricity": 55},
     {"Base.BlowTorch": 5, "Base.WeldingRods": 15, "Base.SheetMetal": 16, "Base.ElectronicsScrap": 100,
      "Base.ElectricWire": 12, "Base.Screws": 60, "KnoxBuildworks.RefrigeratorCompressor": 1,
      "KnoxBuildworks.RefrigerantBottle": 8, "KnoxBuildworks.InsulationFoam": 6,
      "KnoxBuildworks.ThinCopperPipe": 4, "KnoxBuildworks.RubberSeal": 6, "KnoxBuildworks.PlasticSheet": 4}),
]
# item weights (game / KBW item scripts, 2026-11-02); drainables count once (one torch/pack/bottle)
WEIGHT = {"Base.SheetMetal": 2.0, "Base.ElectronicsScrap": 0.1, "Base.ElectricWire": 0.1, "Base.Screws": 0.05,
          "KnoxBuildworks.RefrigeratorCompressor": 5.0, "KnoxBuildworks.InsulationFoam": 0.9,
          "KnoxBuildworks.ThinCopperPipe": 1.25, "KnoxBuildworks.RubberSeal": 0.5,
          "KnoxBuildworks.PlasticSheet": 1.5}
DRAIN_WEIGHT = {"Base.BlowTorch": 1.0, "Base.WeldingRods": 1.5, "KnoxBuildworks.RefrigerantBottle": 1.0}
TOOLS_WEIGHT = 0.5   # screwdriver (welding mask is worn)


def _with_amounts(entries, amounts):
    out = []
    for e in entries:
        e = copy.deepcopy(e)
        item = (e.get("items") or [None])[0]
        if e.get("role") != "tool" and item in amounts:
            e["uses" if "uses" in e else "amount"] = amounts[item]
        out.append(e)
    return out


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
    _skills(base["stages"][0]["requirements"], *BASE_SKILLS)
    report = ["%s: capacity 30, MW%d+E%d (alt E%d), carry weight %.1f" % (
        (BASE_ID,) + BASE_SKILLS + (_carry_weight(base_group + req.get("inputs", [])),))]
    doc.setdefault("materialGroups", {})
    for n, (cap, suf, name, mw, el, alt, xp, amounts) in enumerate(TIERS):
        gname = "kbwcb.appliance.freezer%d" % cap
        doc["materialGroups"][gname] = _with_amounts(base_group, amounts)
        t = copy.deepcopy(base)
        t["id"] = BASE_ID + suf
        t["translationKey"] = base["translationKey"] + suf
        t["displayName"] = name
        t["group"] = dict(GROUP, level=n + 2)
        t["construction"] = dict(copy.deepcopy(cons), xp=xp)          # time stays 200
        r = copy.deepcopy(req)
        r["materials"] = gname
        r["inputs"] = _with_amounts(req.get("inputs", []), amounts)
        _skills(r, mw, el, alt)
        t["stages"][0]["requirements"] = r
        t["stages"][0]["container"] = {"capacity": cap}
        i = next((k for k, b in enumerate(bs) if b["id"] == t["id"]), None)
        if i is None:
            bs.insert(bs.index(base) + 1 + n, t)
        else:
            bs[i] = t
        report.append("%s: capacity %d, MW%d+E%d (alt E%d), xp %s, carry weight %.1f" % (
            t["id"], cap, mw, el, alt, xp, _carry_weight(doc["materialGroups"][gname] + r["inputs"])))
    return report


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
