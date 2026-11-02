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
    if style:
        indent, ascii_, seps, nl, tail, bom = style
        out = json.dumps(doc, indent=indent, ensure_ascii=ascii_, separators=seps).replace("\n", nl) + tail
        open(OURS, "wb").write((b"\xef\xbb\xbf" if bom else b"") + out.encode("utf-8"))
    else:
        json.dump(doc, open(OURS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print("\n".join(report))


if __name__ == "__main__":
    main()
