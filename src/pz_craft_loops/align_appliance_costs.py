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
# Cost = the chest-freezer recipe scaled up (more per unit of storage each step); tools unchanged,
# one compressor at every tier. Skills +1 per tier; build time stays 200 (user, 2026-11-02).
BASE_ID = "community.tk.kitchen_misc.ice_machine"
GROUP = {"id": "kbwcb.appliances.ice_machines", "translationKey": "IGUI_KBWCB_Group_IceMachines",
         "name": "Commercial Ice Machine"}
TIERS = [  # (capacity, id suffix, name, material multiplier, MetalWelding, Electricity, alt Electricity, xp)
    (65, "_65", "Large Commercial Ice Machine", 2.5, 5, 4, 8, {"MetalWelding": 100, "Electricity": 35}),
    (100, "_100", "Industrial Ice Machine", 4.5, 6, 5, 9, {"MetalWelding": 150, "Electricity": 55}),
]
KEEP_AMOUNT = {"tool"}                       # tools are kept: never scale
KEEP_ITEMS = {"KnoxBuildworks.RefrigeratorCompressor"}   # one compressor per freezer


def _scale(entries, mult):
    import math
    out = []
    for e in entries:
        e = copy.deepcopy(e)
        if e.get("role") not in KEEP_AMOUNT and not (set(e.get("items") or []) & KEEP_ITEMS):
            for k in ("amount", "uses"):
                if k in e:
                    e[k] = int(math.ceil(e[k] * mult))
        out.append(e)
    return out


def build_freezer_tiers(doc):
    req, cons = _kbw(*MATCH[BASE_ID])
    groups = json.load(open(os.path.join(VE, "refrigeration.json"), encoding="utf-8-sig"))["materialGroups"]
    base_group = groups[req["materials"]]
    bs = doc["buildables"]
    base = next(b for b in bs if b["id"] == BASE_ID)
    base["group"] = dict(GROUP, level=1)
    report = []
    doc.setdefault("materialGroups", {})
    for cap, suf, name, mult, mw, el, alt, xp in TIERS:
        gname = "kbwcb.appliance.freezer%d" % cap
        doc["materialGroups"][gname] = _scale(base_group, mult)
        t = copy.deepcopy(base)
        t["id"] = BASE_ID + suf
        t["translationKey"] = base["translationKey"] + suf
        t["displayName"] = name
        t["group"] = dict(GROUP, level=TIERS.index((cap, suf, name, mult, mw, el, alt, xp)) + 2)
        t["construction"] = dict(copy.deepcopy(cons), xp=xp)          # time stays 200
        r = copy.deepcopy(req)
        r["materials"] = gname
        r["inputs"] = _scale(req.get("inputs", []), mult)
        r["skills"] = {"MetalWelding": mw, "Electricity": el}
        r["knowledge"]["skillAlternatives"] = [{"mode": "all", "skills": {"MetalWelding": mw, "Electricity": alt}}]
        t["stages"][0]["requirements"] = r
        t["stages"][0]["container"] = {"capacity": cap}
        i = next((k for k, b in enumerate(bs) if b["id"] == t["id"]), None)
        if i is None:
            bs.insert(bs.index(base) + 1 + TIERS.index((cap, suf, name, mult, mw, el, alt, xp)), t)
        else:
            bs[i] = t
        report.append("%s: capacity %d, x%.1f materials, MW%d+E%d (alt E%d), xp %s" % (t["id"], cap, mult, mw, el, alt, xp))
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
