# -*- coding: utf-8 -*-
"""Generate 67_community_dylan_future_room_extras.json (user, 2026-08-28): the rest of Dylan's
DylansFutureRoom01 (Community pack). File 50 already builds the bed, chest of drawers, laptop and
coffee tables, viewscreens and frosted panels.

All on our copies (kbw_tilepatch.FR_*, KBWCommunityIceShell_176..198): the pack gives these tiles
no properties, and the south-facing-only pieces get a mirrored east-facing copy.
  Wall Screen TV            22 (west wall) / 23 (north wall): a working TV with generated screens,
                            on the 2nd copies KBWCommunityIceShell_205 / 206 (screens 221-254)
  Black / White Fridge      30 / 31 + mirrors: vanilla fridge + freezer. Built as the fridge TIERS
                            (60/30, 80/40, 100/50) in file 70 (align_appliance_costs.FUTURE_FRIDGES)
  Black / White Upper Cabinet  35 / 36 + mirrors: hang high on a wall, over counters and fridges
  Black / White Low Cabinet    37 / 38 + mirrors
  Black Modern Couch        40-47, 2 tiles, 4 facings (joins composited from the art):
                            N = 40 41, W = 43 over 42, E = 45 over 44, S = 46 47; vanilla couch seats
  Future Planter            49
KBW face = opposite of the tile Facing (S-facing source -> face N, its mirror -> face W).
Cabinets get Reinforced versions by the default rule. The fridges get the fridge tiers instead
(a reinforced version would replace the cost with the crate's and drop the compressor). NOT yet tested in game.
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kbw_tilepatch import FR_SHEET, MIRROR, decor_copy_name, walltv_face_sprites  # noqa: E402

DELIV = r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables"
OUT = os.path.join(DELIV, "67_community_dylan_future_room_extras.json")
PREFIX = "community.dylan.future_room."
VE_REFRIG = (r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600\3772269882\mods"
             r"\KnoxBuildworks_Vanilla_Expanded\42\media\KnoxBuildworks\definitions\appliances")
VE_FRIDGE_ID = "kbw.vanillaexpanded.appliances.refrigeration.white_refrigerator"


def _c(i, mirror=False):
    return decor_copy_name(i + (MIRROR if mirror else 0), FR_SHEET)


def _one(s):
    return {"layers": [{"rows": [[s]]}]}


def _from(fn, bid):
    d = json.load(open(os.path.join(DELIV, fn), encoding="utf-8"))
    return copy.deepcopy(next(b for b in d["buildables"] if b["id"] == bid))


def _base(slug, name, cat, sub, faces, req, con, obj, container=None, tags=(), group=None, material="Metal",
          placement=None, tooltip=None):
    bid = PREFIX + slug
    st = {"id": "built", "geometry": {"faces": faces}, "requirements": req, "construction": con, "object": obj}
    if container:
        st["container"] = container
    b = {"id": bid, "allowSpriteReuse": True, "translationKey": "IGUI_" + bid.replace(".", "_"),
         "displayName": name, "category": cat, "subcategory": sub, "material": material,
         "materialTags": [material], "iconSprite": next(iter(faces.values()))["layers"][0]["rows"][0][0],
         "placement": placement or {"kind": "object", "requiresFloor": True},
         "tags": ["community-tilepack", "dylan", "future-room"] + list(tags), "stages": [st]}
    if group:
        b["group"] = group
    if tooltip:
        b["tooltipKey"] = tooltip
    return b


def _metal():
    b = _from("40_community_dirkies_containers.json",
              "community.dirkies.containers.location_community_medical_ddd_01_12")   # Metal Wall Shelves
    return b["stages"][0]["requirements"], b["construction"]


def _fridges():
    import pump_sinks as ps
    doc = json.load(open(os.path.join(VE_REFRIG, "refrigeration.json"), encoding="utf-8-sig"))
    ve = next(b for b in doc["buildables"] if b["id"] == VE_FRIDGE_ID)
    tmpl = ps._templates().get(ve.get("extends"), {})
    st = ve["stages"][0]
    con = copy.deepcopy(ve.get("construction") or tmpl.get("construction"))
    group = {"id": PREFIX + "fridges", "name": "Future Fridges",
             "translationKey": "IGUI_community_dylan_future_room_fridges_group"}
    out = []
    for level, (slug, name, src) in enumerate([("fridge_black", "Black Future Fridge", 30),
                                               ("fridge_white", "White Future Fridge", 31)], 1):
        b = _base(slug, name, tmpl.get("category", "Appliances"), tmpl.get("subcategory", "Refrigeration"),
                  {"N": _one(_c(src)), "W": _one(_c(src, True))}, copy.deepcopy(st["requirements"]),
                  copy.deepcopy(con), copy.deepcopy(st.get("object") or {"isProp": True, "dismantable": True}),
                  tags=["appliance", "fridge"], group=dict(group, level=level),
                  tooltip=ve.get("tooltipKey"))
        b["materialTags"] = ["Metal", "Electrical"]
        out.append(b)
    return out


def build_document():
    req, con = _metal()
    out = []
    # 1. wall screens -> TVs (same cost / object as the Dylan Premium CRT Television)
    tv = _from("53_community_dylan_rf02_misc.json", "community.dylan.rf02.tv_crt_premium")
    tst = tv["stages"][0]
    # (user 2026-11-13) on the 2nd TV copies (kbw_tilepatch.WALLTV_BASE: own screens at +16/+32/+48,
    # depth below the upper cabinets), hung on a wall and walk-through like the viewscreens (file 50)
    tobj = dict(copy.deepcopy(tst.get("object")), isThumpable=False, canPassThrough=True)
    out.append(_base("wall_screen_tv", "Wall Screen TV", tv["category"], tv["subcategory"],
                     {e: _one(s) for e, s in walltv_face_sprites().items()}, copy.deepcopy(tst["requirements"]),
                     copy.deepcopy(tv.get("construction") or tst.get("construction")),
                     tobj, tags=["television", "appliance"], tooltip=tv.get("tooltipKey"),
                     placement={"kind": "object", "needToBeAgainstWall": True}))
    # 2. fridges: built as the fridge tier ladder in 70_kbwcb_refrigeration_tiers.json
    #    (align_appliance_costs.FUTURE_FRIDGES, user 2026-08-28), not here
    # 3. low cabinets, 4. upper cabinets (reinforced by the default rule)
    for level, (slug, name, src, sub) in enumerate([
            ("cabinet_black", "Black Metal Cabinet", 37, "Cabinets"),
            ("cabinet_white", "White Metal Cabinet", 38, "Cabinets"),
            ("upper_cabinet_black", "Black Metal Upper Cabinet", 35, "Upper Counters"),
            ("upper_cabinet_white", "White Metal Upper Cabinet", 36, "Upper Counters")], 1):
        grp = ({"id": PREFIX + "cabinets", "name": "Future Metal Cabinets",
                "translationKey": "IGUI_community_dylan_future_room_cabinets_group", "level": level}
               if sub == "Cabinets" else
               {"id": PREFIX + "upper_cabinets", "name": "Future Metal Upper Cabinets",
                "translationKey": "IGUI_community_dylan_future_room_upper_cabinets_group", "level": level - 2})
        out.append(_base(slug, name, "Containers", sub, {"N": _one(_c(src)), "W": _one(_c(src, True))},
                         copy.deepcopy(req), copy.deepcopy(con), {"isThumpable": True, "dismantable": True},
                         container={"type": "counter", "capacity": 20}, tags=["container", "reinforce"], group=grp))
    # 5. couch (cost / object like the Dirkies couches)
    couch = _from("62_community_dirkies_couches.json", "community.dirkies.couches.couch_blue_comfy")
    cst = couch["stages"][0]
    out.append(_base("couch_black", "Black Modern Couch", couch["category"], couch["subcategory"],
                     {"N": {"layers": [{"rows": [[_c(40), _c(41)]]}]},
                      "W": {"layers": [{"rows": [[_c(43)], [_c(42)]]}]},
                      "E": {"layers": [{"rows": [[_c(45)], [_c(44)]]}]},
                      "S": {"layers": [{"rows": [[_c(46), _c(47)]]}]}},
                     copy.deepcopy(cst["requirements"]),
                     copy.deepcopy(couch.get("construction") or cst.get("construction")),
                     copy.deepcopy(cst.get("object")), tags=["seating", "couch"], material="Wood",
                     tooltip=couch.get("tooltipKey")))
    # 6. planter
    out.append(_base("planter", "Future Planter", "Vegetation", "Potted Plants", {"S": _one(_c(49))},
                     {"inputs": [
                         {"id": "source_material_1", "role": "material", "mode": "consume", "resourceType": "Item",
                          "items": ["Base.SmallSheetMetal"], "amount": 1},
                         {"id": "source_material_2", "role": "consumable", "mode": "drain", "resourceType": "Item",
                          "items": ["Base.Dirtbag"], "amount": 1, "uses": 2}]},
                     {"time": 60, "timedAction": "BuildWallNoTool", "completionSound": "BuildWoodenStructureSmall",
                      "xp": {"Farming": 5}, "category": "Farming"},
                     {"isThumpable": False, "canPassThrough": True, "blockAllSquare": False, "dismantable": True},
                     tags=["vegetation", "decoration"]))
    return {
        "schemaVersion": 1,
        "category": "Furniture and Appliances",
        "source": ("Dylan DylansFutureRoom01 (Community pack): wall screen TV, fridges, cabinets, couch, planter "
                   "on our copies (KBWCommunityIceShell_176..198). Generated by "
                   "pz_craft_loops/dylan_future_room_extras.py."),
        "buildables": out,
    }


def main():
    doc = build_document()
    ids = [b["id"] for b in doc["buildables"]]
    assert len(ids) == len(set(ids))
    json.dump(doc, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("wrote %s (%d buildables)" % (OUT, len(ids)))


if __name__ == "__main__":
    main()
