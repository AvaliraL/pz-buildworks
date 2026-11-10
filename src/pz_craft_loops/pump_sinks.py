# -*- coding: utf-8 -*-
"""Hand-pump sinks (user, 2026-11-09): the five vanilla counter-top sinks that Knox Buildworks Vanilla
Expanded builds (appliances/bathroom.json: Beige, White, Industrial, Dark Industrial, Chrome), as a
second version that draws water like World Essentials' Large Water Tank (a map hand pump) instead of
the plumbed 20-unit reserve.

  * sprites: our copies of fixtures_sinks_01 in the ice-shell tileset (kbw_tilepatch.PUMP_SINK_SRC),
    same art and counter-top properties, water 999999 / 999999, no waterPiped;
  * stage "well": true -> Knox's own well system (WellSystem.lua), so the server's Knox well
    settings apply. Default WellWaterMode 1 = endless. Mode 2 (finite: WellCapacity, refill per hour,
    rain) attaches the vanilla Base.Well entity, which is only verified on the vanilla well sprite;
  * cost = the Large Water Tank's (WE Knox Buildworks Expansion, worldessentials.kbw.camping_01_64),
    read from WE's installed definition, with the copy below as fallback;
  * one "Hand Pump Sinks" catalog card (colours inside, arrows), category Appliances / Bathroom
    Fixtures next to Knox VE's Sinks card; name "<Sink> (Hand Pump)" like "(Reinforced)";
  * placement as vanilla / Knox VE sinks (they may stand on the floor too; user, 2026-11-09).
Working in game (user, 2026-11-09).
"""
import copy
import json
import os

from kbw_tilepatch import pump_sink_name

VE = (r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600\3772269882\mods"
      r"\KnoxBuildworks_Vanilla_Expanded\42\media\KnoxBuildworks\definitions\appliances")
WE_TANK = (r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600\3733324672\mods"
           r"\World Essentials - Knox Buildworks Expansion\42\media\KnoxBuildworks\definitions\06_furniture.json")
WE_TANK_ID = "worldessentials.kbw.camping_01_64"
VE_PREFIX = "kbw.vanillaexpanded.appliances.bathroom."
ID_PREFIX = "kbwcb.appliances.pump_sink."
TOOLTIP = ("Tooltip_KBWCB_PumpSink",
           "Draws water like a hand pump: no plumbing or water main needed. Follows the server's "
           "Knox Buildworks well settings.")
# (VE suffix, our stem) in VE's own card order
SINKS = [("beige_sink", "beige"), ("white_sink", "white"), ("industrial_sink", "industrial"),
         ("dark_industrial_sink", "dark_industrial"), ("chrome_sink", "chrome")]
VE_GROUP = "kbwve.appliances.sinks"
VE_GROUP_KEY = "IGUI_KBWVE_Group_Sinks"
# Own catalog card (user, 2026-11-09): one "Hand Pump Sinks" entry, colours inside (arrows), next to
# VE's Sinks card in the same Appliances / Bathroom Fixtures list. Joining VE's card from another mod
# was not confirmed and the test bundle could not keep it (its categories differ).
GROUP = {"id": "kbwcb.appliances.pump_sinks", "translationKey": "IGUI_KBWCB_Group_PumpSinks",
         "name": "Hand Pump Sinks"}

# Fallback copy of the Large Water Tank's cost (WE, read 2026-11-09)
_TANK_FALLBACK = {
    "requirements": {
        "inputs": [
            {"id": "tool_welding_mask", "role": "tool", "mode": "keep", "resourceType": "Item",
             "tags": ["base:weldingmask"], "amount": 1},
            {"id": "source_material_1", "role": "material", "mode": "consume", "resourceType": "Item",
             "items": ["Base.SheetMetal"], "amount": 5},
            {"id": "source_material_2", "role": "material", "mode": "consume", "resourceType": "Item",
             "items": ["Base.MetalPipe"], "amount": 3},
            {"id": "source_material_3", "role": "material", "mode": "consume", "resourceType": "Item",
             "items": ["Base.Screws"], "amount": 4},
            {"id": "source_material_4", "role": "consumable", "mode": "drain", "resourceType": "Item",
             "items": ["Base.WeldingRods"], "amount": 1, "uses": 4},
            {"id": "source_material_5", "role": "consumable", "mode": "drain", "resourceType": "Item",
             "items": ["Base.BlowTorch"], "amount": 1, "uses": 4}],
        "skills": {"MetalWelding": 6}},
    "construction": {"time": 200, "timedAction": "BuildLowMetal", "completionSound": "BuildMetalStructureMedium",
                     "xp": {"MetalWelding": 60}, "category": "Metalworking"},
}


def tank_cost():
    """(requirements, construction, source) of WE's Large Water Tank."""
    try:
        d = json.load(open(WE_TANK, encoding="utf-8-sig"))
        b = next(x for x in d["buildables"] if x.get("id") == WE_TANK_ID)
        st = b["stages"][0]
        return copy.deepcopy(st["requirements"]), copy.deepcopy(st["construction"]), "WE installed"
    except Exception:
        return (copy.deepcopy(_TANK_FALLBACK["requirements"]), copy.deepcopy(_TANK_FALLBACK["construction"]),
                "fallback copy")


def _templates():
    t = {}
    for f in os.listdir(VE):
        if f.endswith(".json"):
            t.update(json.load(open(os.path.join(VE, f), encoding="utf-8-sig")).get("templates", {}))
    return t


def _swap_sprites(stage):
    for face in (stage.get("geometry") or {}).get("faces", {}).values():
        for layer in face.get("layers", []):
            layer["rows"] = [[pump_sink_name(int(c.rsplit("_", 1)[1])) for c in row] for row in layer["rows"]]


def build_pump_sink_defs():
    """(buildables, tooltips {key: text}, report)."""
    doc = json.load(open(os.path.join(VE, "bathroom.json"), encoding="utf-8-sig"))
    by_id = {b["id"]: b for b in doc["buildables"]}
    tmpl = _templates()
    req, con, src = tank_cost()
    out, report = [], ["pump sinks: cost from %s (%s)" % (WE_TANK_ID, src)]
    first_level = 1
    for n, (ve_suffix, stem) in enumerate(SINKS):
        ve = by_id[VE_PREFIX + ve_suffix]
        b = copy.deepcopy(ve)
        for k, v in tmpl.get(b.pop("extends", None), {}).items():   # inline VE's template
            b.setdefault(k, copy.deepcopy(v))
        b["id"] = ID_PREFIX + stem
        b["translationKey"] = "IGUI_" + b["id"].replace(".", "_")
        b["displayName"] = "%s (Hand Pump)" % ve["displayName"]
        b["tooltipKey"] = TOOLTIP[0]
        b["tags"] = ["community-tilepack", "bathroom", "water", "hand-pump-sink"]
        b["group"] = dict(GROUP, level=first_level + n)
        st = b["stages"][0]
        _swap_sprites(st)
        icon = b.get("iconSprite")
        if icon and icon.startswith("fixtures_sinks_01_"):
            b["iconSprite"] = pump_sink_name(int(icon.rsplit("_", 1)[1]))
        st["well"] = True
        st["requirements"] = copy.deepcopy(req)
        b["construction"] = copy.deepcopy(con)
        st.pop("construction", None)
        out.append(b)
        report.append("%-40s %-34s level %d sprites %s" % (
            b["id"], b["displayName"], first_level + n,
            sorted({c for f in st["geometry"]["faces"].values() for L in f["layers"] for r in L["rows"] for c in r})))
    return out, dict([TOOLTIP]), report


if __name__ == "__main__":
    bl, tips, rep = build_pump_sink_defs()
    print("\n".join(rep))
    print(json.dumps(bl[0], indent=1)[:2500])
