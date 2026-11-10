# -*- coding: utf-8 -*-
"""Reinforced counters (2026-11-02): a second version of every counter with the Dirkies military
crate's cost and capacity 100.

Applied at build time by build_community_mod.py, build_tikitown_mod.py and
build_merged_test_mod.py (sources untouched). For every buildable whose displayName contains
"Counter" and that has a stage container, add `<id>.reinforced`:
  * requirements + construction = the military crate's, read from its own definition
    (community.dirkies.containers.furniture_storage_ddd_01_4.crate) so they stay in sync;
  * stage container: same type, capacity 100 (KBW sets it on the built object; proven with the
    crate and the ice machines). Multi-tile counters get 100 per tile;
  * same art, allowSpriteReuse on both; joins the base's group at the next free level.
"""
import os, json, copy

CRATE_SRC = r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables\40_community_dirkies_containers.json"
CRATE_ID = "community.dirkies.containers.furniture_storage_ddd_01_4.crate"
SUFFIX = ".reinforced"
CAPACITY = 100

_CRATE = None


def crate_stage():
    global _CRATE
    if _CRATE is None:
        d = json.load(open(CRATE_SRC, encoding="utf-8"))
        b = next(x for x in d["buildables"] if x["id"] == CRATE_ID)
        _CRATE = b["stages"][0]
    return _CRATE


def _final_name(b):
    """The name the piece ships with (name_tooltip_pass runs after us; use its result so e.g. the
    mislabelled 'Industrial Steel Counter' -> Fire Extinguisher Cabinet is not treated as a
    counter, and corner pieces get distinct names)."""
    import name_tooltip_pass
    return name_tooltip_pass.fix_name(b) or b.get("displayName") or ""


MATCH_WORDS = ("Counter", "Upper Cabinet", "Wall Cupboard")   # counters + upper cabinets (2026-11-02)


OPT_IN_TAG = "reinforce"   # any container tagged this also gets a reinforced version (2026-08-28)


# Bookshelves (user, 2026-11-09): every bookshelf / bookcase, in-wall ones included, also gets a
# reinforced version (capacity 100, military-crate cost). By final name or by id (the Dirkies
# "<colour> Wall Shelf" pieces are in-wall bookcases: id ..._bookcase_wall). The secret-entrance
# bookshelves are doors, not storage furniture: excluded.
BOOK_WORDS = ("Bookshelf", "Bookcase", "Bookstore Shelf")
BOOK_ID_WORDS = ("bookcase", "bookshelf", "bookshelves")
BOOK_EXCLUDE = ("Secret",)


def _is_bookshelf(b, name):
    if any(w in name for w in BOOK_EXCLUDE):
        return False
    bid = (b.get("id") or "").lower()
    return any(w in name for w in BOOK_WORDS) or any(w in bid for w in BOOK_ID_WORDS)


def _is_counter(b):
    name = _final_name(b)
    wanted = (any(w in name for w in MATCH_WORDS) or OPT_IN_TAG in (b.get("tags") or [])
              or _is_bookshelf(b, name))
    return (wanted and not b.get("id", "").endswith(SUFFIX)
            and any(st.get("container") is not None for st in b.get("stages") or []))


def _reinforced_name(name):
    if name.endswith(")"):
        return name[:-1] + ", Reinforced)"
    return name + " (Reinforced)"


def add_variants(buildables):
    """Insert a reinforced sibling after each counter in `buildables` (in place). Returns count."""
    crate = crate_stage()
    existing = {b.get("id") for b in buildables}
    max_level = {}
    for b in buildables:
        g = b.get("group") or {}
        if g.get("id"):
            max_level[g["id"]] = max(max_level.get(g["id"], 0), int(g.get("level") or 1))
    out, added = [], 0
    for b in buildables:
        out.append(b)
        if not _is_counter(b) or (b["id"] + SUFFIX) in existing:
            continue
        v = copy.deepcopy(b)
        v["id"] = b["id"] + SUFFIX
        if v.get("translationKey"):
            v["translationKey"] = v["translationKey"] + "_reinforced"
        v["displayName"] = _reinforced_name(_final_name(b))
        v["allowSpriteReuse"] = True
        b["allowSpriteReuse"] = True         # both definitions share the art
        for st in b.get("stages") or []:
            st["allowSpriteReuse"] = True
        v["material"], v["materialTags"] = "Metal", ["Metal"]
        g = v.get("group")
        if g and g.get("id"):
            max_level[g["id"]] += 1
            g["level"] = max_level[g["id"]]
        v.pop("construction", None)          # the crate's construction lives on its stage
        for st in v.get("stages") or []:
            st["allowSpriteReuse"] = True
            st["requirements"] = copy.deepcopy(crate["requirements"])
            st["construction"] = copy.deepcopy(crate["construction"])
            if st.get("container") is not None:
                st["container"] = dict(st["container"], capacity=CAPACITY)
        out.append(v)
        added += 1
    buildables[:] = out
    return added
