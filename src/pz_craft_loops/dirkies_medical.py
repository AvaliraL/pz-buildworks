# -*- coding: utf-8 -*-
"""Generate 65_community_dirkies_medical.json (user, 2026-08-28): the rest of Dirkies'
location_community_medical_ddd_01 (Community pack, diederiks_tile_palooza). Already built in
file 40: 8-11 work table / counter with shelves, 12-13 wall shelves, 16-19 Glass Medical Cabinet,
28-31 Medical Drawer Cart.

  0-3 / 4-7  Teal / Red Medical Locker (2x2 lockers in one tile; Facing E,S,W,N = KBW W,N,E,S)
  14-15      Hospital Push Cart (one storage)
  20-23      Large Industrial Sink, open shelf underneath = storage. Four versions in one card:
             plumbed (KBW VE Industrial Sink recipe), Reinforced (crate cost, 100), Hand Pump (our
             water copies, kbw_tilepatch.MED_SINK, WE Large Water Tank cost like the other pump
             sinks) and Hand Pump Reinforced (crate + tank cost added together, 100)
  24-27      Wheelchair: our chair copies (kbw_tilepatch.MED_WHEELCHAIR: bed + chair flags) with the
             pack's own seat positions (our seating.txt), so Rest sits you in it
  32-33 / 34-35  Lab Centrifuge / Lab Analyzer: REMOVED (texture issues in game, user 2026-08-28)
  36-37      Lab Specimen Cabinet: REMOVED for now (user 2026-08-28)
             32-37 are drawn at counter height with no table-top flags (floated on the floor in game):
             built on our copies with the desk mic's table-top flags (kbw_tilepatch.MED_TABLETOP).
  42-47      MRI Scanner: one 2x3 piece, single orientation. Layout from the art (no SpriteGridPos in
             the pack). Rows north to south: 44 47 / 43 46 / 42 45 (user-corrected three times in game
             2026-08-28). 42 / 43 are bed copies (foot / head): the table works as a bed, lying N/S,
             seated facing east.
Every container here is tagged "reinforce" (default rule, user 2026-08-28): counter_variants adds
the "(Reinforced)" sibling with the crate cost and 100 storage. The sink builds its own reinforced
versions (its hand-pump one needs the added tank cost), so it is not tagged.
NOT yet tested in game.
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kbw_tilepatch import MED_SHEET, MED_SINK, MED_WHEELCHAIR, decor_copy_name, decor_edge  # noqa: E402


def _tt(w, n):
    """Table-top copies (kbw_tilepatch.MED_TABLETOP: counter-height art + table-top flags)."""
    return {"W": decor_copy_name(w, MED_SHEET), "N": decor_copy_name(n, MED_SHEET)}

DELIV = r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables"
OUT = os.path.join(DELIV, "65_community_dirkies_medical.json")
PREFIX = "community.dirkies.medical."
VE_SINK = "kbw.vanillaexpanded.appliances.bathroom.industrial_sink"
METAL_COST_FROM = ("40_community_dirkies_containers.json",
                   "community.dirkies.containers.location_community_medical_ddd_01_16")   # Glass Medical Cabinet


def _spr(i):
    return "%s_%d" % (MED_SHEET, i)


def _one(s):
    return {"layers": [{"rows": [[s]]}]}


def _faces(m):
    return {f: _one(_spr(i) if isinstance(i, int) else i) for f, i in m.items()}


def _metal_cost():
    d = json.load(open(os.path.join(DELIV, METAL_COST_FROM[0]), encoding="utf-8"))
    b = next(x for x in d["buildables"] if x["id"] == METAL_COST_FROM[1])
    return copy.deepcopy(b["stages"][0]["requirements"]), copy.deepcopy(b["construction"])


def _base(slug, name, cat, sub, faces, req, con, obj, placement=None, container=None, tags=(), group=None):
    bid = PREFIX + slug
    st = {"id": "built", "geometry": {"faces": faces}, "requirements": req, "construction": con, "object": obj}
    if container:
        st["container"] = container
    b = {
        "id": bid,
        "allowSpriteReuse": True,
        "translationKey": "IGUI_" + bid.replace(".", "_"),
        "displayName": name,
        "category": cat,
        "subcategory": sub,
        "material": "Metal",
        "materialTags": ["Metal"],
        "iconSprite": next(iter(faces.values()))["layers"][0]["rows"][0][0],
        "placement": placement or {"kind": "object", "requiresFloor": True},
        "tags": ["community-tilepack", "dirkies", "medical"] + list(tags),
        "stages": [st],
    }
    if group:
        b["group"] = group
    return b


# ---- sink: four versions ----------------------------------------------------------------------
def _merge_requirements(a, b):
    """a + b: tools once (by tag / item), materials and drainables added together, skills = max.
    Material groups / knowledge are kept from a."""
    out = copy.deepcopy(a)
    rows = out.setdefault("inputs", [])

    def key(r):
        return (r.get("role"), tuple(r.get("tags") or ()), tuple(r.get("items") or ()))
    by_key = {key(r): r for r in rows}
    for r in b.get("inputs", []):
        k = key(r)
        if k in by_key:
            if r.get("role") == "tool":
                continue
            mine = by_key[k]
            for f in ("amount", "uses"):
                if f in r:
                    mine[f] = mine.get(f, 0) + r[f]
        else:
            r2 = copy.deepcopy(r)
            n = 1
            while any(x.get("id") == r2.get("id") for x in rows):
                r2["id"] = "%s_%d" % (r.get("id"), n); n += 1
            rows.append(r2)
            by_key[k] = r2
    skills = out.setdefault("skills", {})
    for s, v in (b.get("skills") or {}).items():
        skills[s] = max(skills.get(s, 0), v)
    return out


def _sink_versions():
    import pump_sinks as ps
    import counter_variants as cv
    VE = ps.VE
    doc = json.load(open(os.path.join(VE, "bathroom.json"), encoding="utf-8-sig"))
    ve = next(b for b in doc["buildables"] if b["id"] == VE_SINK)
    tmpl = ps._templates().get(ve.get("extends"), {})
    st_ve = ve["stages"][0]
    base_req = copy.deepcopy(st_ve["requirements"])
    base_con = copy.deepcopy(ve.get("construction") or tmpl.get("construction"))
    obj = copy.deepcopy(st_ve.get("object") or {"isProp": True, "dismantable": True, "blockAllSquare": True})
    crate = cv.crate_stage()
    tank_req, tank_con, _src = ps.tank_cost()
    plumbed = {"W": _spr(20), "N": _spr(21), "E": _spr(22), "S": _spr(23)}
    pump = {decor_edge(s, MED_SHEET): decor_copy_name(s, MED_SHEET) for s in MED_SINK}
    group = {"id": PREFIX + "industrial_sinks", "translationKey": "IGUI_community_dirkies_medical_industrial_sinks_group",
             "name": "Large Industrial Sinks"}
    cat, sub = tmpl.get("category", "Appliances"), tmpl.get("subcategory", "Bathroom Fixtures")
    pump_reinf_req = _merge_requirements(crate["requirements"], tank_req)
    # cost rule (user, 2026-08-28): a metal base costs half its reinforced version
    if cv.is_metal_cost(base_req):
        base_req = cv.half_crate_requirements(base_req, crate["requirements"])
    if cv.is_metal_cost(tank_req):
        pump_req = cv.half_crate_requirements(tank_req, pump_reinf_req)
    else:
        pump_req = tank_req
    versions = [
        ("industrial_sink", "Large Industrial Sink", plumbed, base_req, base_con, 20, False),
        ("industrial_sink_reinforced", "Large Industrial Sink (Reinforced)", plumbed,
         crate["requirements"], crate["construction"], cv.CAPACITY, False),
        ("industrial_sink_pump", "Large Industrial Sink (Hand Pump)", pump, pump_req, tank_con, 20, True),
        ("industrial_sink_pump_reinforced", "Large Industrial Sink (Hand Pump, Reinforced)", pump,
         pump_reinf_req, tank_con, cv.CAPACITY, True),
    ]
    out = []
    for level, (slug, name, faces, req, con, cap, well) in enumerate(versions, 1):
        b = _base(slug, name, cat, sub, _faces(faces), copy.deepcopy(req), copy.deepcopy(con), dict(obj),
                  placement=copy.deepcopy(tmpl.get("placement")), container={"type": "counter", "capacity": cap},
                  tags=["sink"] + (["hand-pump-sink"] if well else []), group=dict(group, level=level))
        b["materialTags"] = ["Metal", "Plumbing"]
        if well:
            b["stages"][0]["well"] = True
        out.append(b)
    return out


# ---- the rest ---------------------------------------------------------------------------------
def build_document():
    mreq, mcon = _metal_cost()
    locker_obj = {"isThumpable": True, "canBePadlocked": True}
    out = []
    lockers = {"id": PREFIX + "lockers", "translationKey": "IGUI_community_dirkies_medical_lockers_group",
               "name": "Medical Lockers"}
    for level, (slug, name, first) in enumerate([("locker_teal", "Teal Medical Locker", 0),
                                                 ("locker_red", "Red Medical Locker", 4)], 1):
        out.append(_base(slug, name, "Containers", "Lockers",
                         _faces({"W": first, "N": first + 1, "E": first + 2, "S": first + 3}),
                         copy.deepcopy(mreq), copy.deepcopy(mcon), dict(locker_obj),
                         container={"type": "locker", "capacity": 40}, tags=["locker", "reinforce"],
                         group=dict(lockers, level=level)))
    out.append(_base("push_cart", "Hospital Push Cart", "Containers", "Medical", _faces({"W": 14, "N": 15}),
                     copy.deepcopy(mreq), copy.deepcopy(mcon), {"isThumpable": True},
                     container={"type": "shelves", "capacity": 20}, tags=["reinforce"]))
    out.extend(_sink_versions())
    # wheelchair (chair copies)
    wc = {decor_edge(s, MED_SHEET): decor_copy_name(s, MED_SHEET) for s in MED_WHEELCHAIR}
    out.append(_base("wheelchair", "Wheelchair", "Furniture and Appliances", "Seating", _faces(wc),
                     {"inputs": [
                         {"id": "tool_screwdriver", "role": "tool", "mode": "keep", "resourceType": "Item",
                          "tags": ["base:screwdriver"], "amount": 1},
                         {"id": "source_material_1", "role": "material", "mode": "consume", "resourceType": "Item",
                          "items": ["Base.MetalPipe"], "amount": 2},
                         {"id": "source_material_2", "role": "material", "mode": "consume", "resourceType": "Item",
                          "items": ["Base.Screws"], "amount": 6},
                         {"id": "source_material_3", "role": "material", "mode": "consume", "resourceType": "Item",
                          "items": ["Base.RippedSheets"], "amount": 2}],
                      "skills": {"MetalWelding": 2}},
                     {"time": 120, "timedAction": "BuildLowMetal", "completionSound": "BuildMetalStructureMedium",
                      "xp": {"MetalWelding": 20}, "category": "Metalworking"},
                     {"isThumpable": True, "dismantable": True}, tags=["seat"]))
    # lab equipment (decoration) + specimen cabinet
    elec = {"inputs": [
        {"id": "tool_screwdriver", "role": "tool", "mode": "keep", "resourceType": "Item",
         "tags": ["base:screwdriver"], "amount": 1},
        {"id": "source_material_1", "role": "material", "mode": "consume", "resourceType": "Item",
         "items": ["Base.ElectronicsScrap"], "amount": 6},
        {"id": "source_material_2", "role": "material", "mode": "consume", "resourceType": "Item",
         "items": ["Base.ScrapMetal"], "amount": 2},
        {"id": "source_material_3", "role": "material", "mode": "consume", "resourceType": "Item",
         "items": ["Base.Screws"], "amount": 4}],
        "skills": {"Electricity": 2}}
    elec_con = {"time": 100, "timedAction": "BuildLowMetal", "completionSound": "BuildMetalStructureSmall",
                "xp": {"Electricity": 15}, "category": "Electrical"}
    decor_obj = {"isThumpable": False, "canPassThrough": True, "blockAllSquare": False, "dismantable": True}
    lab = {"id": PREFIX + "lab_equipment", "translationKey": "IGUI_community_dirkies_medical_lab_group",
           "name": "Lab Equipment"}
    # Lab Centrifuge (32/33) and Lab Analyzer (34/35) REMOVED (user, in game 2026-08-28): texture
    # issues. Their copies KBWCommunityIceShell_130..133 stay in the tileset (fixed indices) unused.
    # Lab Specimen Cabinet (36/37) REMOVED for now (user, 2026-08-28): neither the table-top nor the
    # wall-mounted version looked right. Copies KBWCommunityIceShell_134/135 stay (fixed indices) unused.
    # MRI scanner: 2 wide x 3 deep, one orientation
    # rows north -> south (user, 2026-08-28: the two north rows were swapped)
    # (2026-08-28, 2nd in-game check with a screenshot: the first and last rows were swapped)
    # (2026-08-28, 3rd check: the two east tiles of the south rows were swapped, 45 <-> 46)
    # 42 / 43 (west column, south two rows) are the patient table: our bed copies (head north,
    # kbw_tilepatch.MED_MRI_BED), so Rest / Sleep work on it.
    bed = lambda s: decor_copy_name(s, MED_SHEET)
    mri_rows = [[_spr(44), _spr(47)], [bed(43), _spr(46)], [bed(42), _spr(45)]]
    mri = _base("mri_scanner", "MRI Scanner", "Furniture and Appliances", "Medical Equipment",
                {"W": {"layers": [{"rows": mri_rows}]}},
                {"inputs": [
                    {"id": "tool_welding_mask", "role": "tool", "mode": "keep", "resourceType": "Item",
                     "tags": ["base:weldingmask"], "amount": 1},
                    {"id": "tool_screwdriver", "role": "tool", "mode": "keep", "resourceType": "Item",
                     "tags": ["base:screwdriver"], "amount": 1},
                    {"id": "source_material_1", "role": "material", "mode": "consume", "resourceType": "Item",
                     "items": ["Base.SheetMetal"], "amount": 8},
                    {"id": "source_material_2", "role": "material", "mode": "consume", "resourceType": "Item",
                     "items": ["Base.ElectronicsScrap"], "amount": 40},
                    {"id": "source_material_3", "role": "material", "mode": "consume", "resourceType": "Item",
                     "items": ["Base.ElectricWire"], "amount": 10},
                    {"id": "source_material_4", "role": "material", "mode": "consume", "resourceType": "Item",
                     "items": ["Base.Screws"], "amount": 20},
                    {"id": "source_material_5", "role": "consumable", "mode": "drain", "resourceType": "Item",
                     "items": ["Base.WeldingRods"], "amount": 1, "uses": 6},
                    {"id": "source_material_6", "role": "consumable", "mode": "drain", "resourceType": "Item",
                     "items": ["Base.BlowTorch"], "amount": 1, "uses": 6}],
                 "skills": {"MetalWelding": 5, "Electricity": 5}},
                {"time": 400, "timedAction": "BuildLowMetal", "completionSound": "BuildMetalStructureMedium",
                 "xp": {"MetalWelding": 40, "Electricity": 40}, "category": "Metalworking"},
                {"isThumpable": True, "dismantable": True}, tags=["decoration"], group=dict(lab, level=1))
    out.append(mri)
    return {
        "schemaVersion": 1,
        "category": "Containers",
        "source": ("Dirkies location_community_medical_ddd_01 (Community pack): the pieces file 40 did not "
                   "cover. Generated by pz_craft_loops/dirkies_medical.py."),
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
