# -*- coding: utf-8 -*-
"""Window / door-frame walls must not merge into the plain corner sprite (in game 2026-11-08: two
'Khaki Cinder Block Wall (Window 2)' placed as a corner became the sheet's solid corner tile).

KBW (KBWBuildingObject:connectWallParts) replaces BOTH edges with the definition's cornerSprite
when two copies of the SAME buildable meet on one square (identity = buildableId + stage +
variant + material). In 21 every window / door-frame variant carried the sheet's plain wall
corner (tile 2), so the windows / openings vanished. Vanilla never merges same-square edges at
all; it only drops a gap filler into the diagonal square, which is KBW's pillarSprite: kept.

Removes cornerSprite from window and door-frame pieces of 21 only. Plain walls keep it (two plain
walls still join into the corner tile). Sheet 26 (glass) is left alone: each glass piece's
cornerSprite is that style's own glass corner. Idempotent; first run backs the file up.
"""
import json, os

DIR = r"c:\Users\josep\Kiro\zomboid\tikitown"
FILE = "21_tikitown_walls_accurate.json"
BACKUP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_cornerfix_backup")


def is_opening(b):
    o = (b.get("stages") or [{}])[0].get("object") or {}
    n = b.get("displayName", "")
    return (b.get("pieceClass") in ("window", "door") or o.get("isDoorFrame")
            or "(Window" in n or "(Door Frame" in n)


def main():
    p = os.path.join(DIR, FILE)
    raw = open(p, encoding="utf-8").read()
    doc = json.loads(raw)
    n = 0
    for b in doc["buildables"]:
        if not is_opening(b):
            continue
        for st in b.get("stages", []):
            o = st.get("object") or {}
            if "cornerSprite" in o:
                del o["cornerSprite"]
                n += 1
    if n:
        os.makedirs(BACKUP, exist_ok=True)
        bk = os.path.join(BACKUP, FILE)
        if not os.path.isfile(bk):
            open(bk, "w", encoding="utf-8").write(raw)
        json.dump(doc, open(p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    left = sum(1 for b in doc["buildables"] if is_opening(b)
               and any("cornerSprite" in (st.get("object") or {}) for st in b["stages"]))
    plain = sum(1 for b in doc["buildables"] if not is_opening(b)
                and any("cornerSprite" in (st.get("object") or {}) for st in b["stages"]))
    print("%s: removed cornerSprite from %d window / door-frame pieces; openings still with it: %d; "
          "plain walls keeping it: %d" % (FILE, n, left, plain))


if __name__ == "__main__":
    main()
