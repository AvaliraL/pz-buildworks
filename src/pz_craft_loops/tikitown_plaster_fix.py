# -*- coding: utf-8 -*-
"""TikiTown walls must not offer plaster / paint / wallpaper finishes (in game 2026-11-08: the Knox
catalog showed a Finish choice on many new walls, and picking one built an unrelated tile).

Cause: gen_walls_accurate.py copied the vanilla brick wall recipe's
onCreate = "BuildRecipeCode.canBePlastered.OnCreate" onto every Brick piece of 21. Knox reads it in
WallFinishes.isPlasterable, then offers Plaster, Plaster + <paint> and Plaster + <wallpaper>
from vanilla's PaintingReference tables, whose tiles are walls_interior_house_* (a different
wall entirely). Vanilla's own world Plaster option reads the same flag. TikiTown art walls are
already finished, so the callback is removed. The lower walls (40) and roof slope walls (41) copy
their callbacks from 21, so a rebuild clears them too.

Only that one callback is removed; other callbacks (onIsValid etc.) stay. Idempotent; the first
run backs the file up.
"""
import json, os

DIR = r"c:\Users\josep\Kiro\zomboid\tikitown"
FILE = "21_tikitown_walls_accurate.json"
BACKUP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_plasterfix_backup")
PLASTER = "BuildRecipeCode.canBePlastered.OnCreate"


def main():
    p = os.path.join(DIR, FILE)
    raw = open(p, encoding="utf-8").read()
    doc = json.loads(raw)
    n = 0
    for b in doc["buildables"]:
        for st in b.get("stages", []):
            cb = st.get("callbacks")
            if isinstance(cb, dict) and cb.get("onCreate") == PLASTER:
                del cb["onCreate"]
                if not cb:
                    del st["callbacks"]
                n += 1
    if n:
        os.makedirs(BACKUP, exist_ok=True)
        bk = os.path.join(BACKUP, FILE)
        if not os.path.isfile(bk):
            open(bk, "w", encoding="utf-8").write(raw)
        json.dump(doc, open(p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    left = json.dumps(doc).count(PLASTER)
    print("%s: removed the plaster onCreate from %d stages; still present: %d" % (FILE, n, left))


if __name__ == "__main__":
    main()
