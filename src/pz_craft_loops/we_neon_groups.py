"""World Essentials' own neon lights, one card per colour (user, 2026-11-19: "it seems to just be 2 entries with 24
light objects each, we should have one grouping per color").

WE's Knox Buildworks Expansion files 41 pieces under subcategory "Neon Signs" in two "Neon Light" cards (its
99_catalogue_finish.json patches): 24 theatre neon tubes (vanilla location_entertainment_theatre_01) and 17
BuildingCraft lights. Colours come from each tile's own light properties (_neon_colours2.py) and, for the string
lights, from the art (_bar_probe/bc_lights.png):
  theatre: red 136-153, orange 160-177, blue 184-201, green 208-225, pink 232-249, white 256-273 (4 pieces each);
  BuildingCraft: GIRLS / SHOWS signs pink (48, 50) and blue (56, 58), "Rusty Rifle" sign yellow (12), string
  lights multicolour (0-3), fairy (4-7), white bulbs (8-11).

Knox collects every bundle's `patches` in manifest order and deep-merges them (Definitions/Overrides.lua collect,
TableUtil.merge), so a small patch file listed AFTER 99_catalogue_finish.json re-files these pieces without
touching WE's 3.5 MB single-line catalogue file. Writes into work/ (WE-owned manifest: one line added, WE's own
layout kept): definitions/99b_neon_colour_groups.json + manifest.json. Display names are unchanged.
"""
import json
import os

WE_EXP = (r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600\3733324672\mods"
          r"\World Essentials - Knox Buildworks Expansion\42\media\KnoxBuildworks")
WORK_EXP = (r"c:\Users\josep\Kiro\zomboid\WE_submods\work\World Essentials - Knox Buildworks Expansion (our files only)"
            r"\42\media\KnoxBuildworks")
PATCH_NAME = "99b_neon_colour_groups.json"
AFTER = "media/KnoxBuildworks/definitions/99_catalogue_finish.json"
NS = "worldessentials.kbw."
FAMILY = "worldessentials.family.decorations_and_landscaping_neon_signs_"
TH = "location_entertainment_theatre_01_"
BC = "buildingcraft_light_"
GROUPS = [  # (slug, card name, pieces in card order)
    ("red_neon", "Red Neon", [TH + "136", TH + "137", TH + "152", TH + "153"]),
    ("orange_neon", "Orange Neon", [TH + "160", TH + "161", TH + "176", TH + "177"]),
    ("yellow_neon", "Yellow Neon", [BC + "12"]),
    ("green_neon", "Green Neon", [TH + "208", TH + "209", TH + "224", TH + "225"]),
    ("blue_neon", "Blue Neon", [TH + "184", TH + "185", TH + "200", TH + "201", BC + "56", BC + "58"]),
    ("pink_neon", "Pink Neon", [TH + "232", TH + "233", TH + "248", TH + "249", BC + "48", BC + "50"]),
    ("white_neon", "White Neon", [TH + "256", TH + "257", TH + "272", TH + "273"]),
    ("string_lights_colored", "Colored String Lights", [BC + "0", BC + "1", BC + "2", BC + "3"]),
    ("string_lights_fairy", "Fairy Lights", [BC + "4", BC + "5", BC + "6", BC + "7"]),
    ("string_lights_white", "White String Lights", [BC + "8", BC + "9", BC + "10", BC + "11"]),
]


def patches():
    cat = json.load(open(os.path.join(WE_EXP, "definitions", "99_catalogue_finish.json"), encoding="utf-8-sig"))["patches"]
    old = {i for i, v in cat.items() if (v.get("group") or {}).get("name") == "Neon Light"}
    out, seen = {}, set()
    for slug, name, pieces in GROUPS:
        for level, p in enumerate(pieces, 1):
            bid = NS + p
            if bid not in cat:
                raise RuntimeError("%s is not in WE's catalogue" % bid)
            out[bid] = {"group": {"id": FAMILY + slug, "name": name, "level": level}}
            seen.add(bid)
    if old - seen:
        raise RuntimeError("WE neon pieces with no colour card: %s" % sorted(old - seen))
    return out


def write():
    p = patches()
    d = os.path.join(WORK_EXP, "definitions")
    os.makedirs(d, exist_ok=True)
    json.dump({"schemaVersion": 1, "patches": p}, open(os.path.join(d, PATCH_NAME), "w", encoding="utf-8", newline="\n"),
              indent=2, ensure_ascii=False)
    raw = open(os.path.join(WE_EXP, "manifest.json"), "rb").read().decode("utf-8")
    line = '    "media/KnoxBuildworks/definitions/%s",' % PATCH_NAME
    nl = "\r\n" if "\r\n" in raw else "\n"
    if PATCH_NAME not in raw:
        anchor = '"%s",' % AFTER
        if anchor not in raw:
            raise RuntimeError("manifest: %s not found" % AFTER)
        i = raw.index(anchor) + len(anchor)
        raw = raw[:i] + nl + line + raw[i:]
    json.loads(raw)
    open(os.path.join(WORK_EXP, "manifest.json"), "wb").write(raw.encode("utf-8"))
    return len(p), len(GROUPS)


if __name__ == "__main__":
    print("patched %d pieces into %d cards" % write())
