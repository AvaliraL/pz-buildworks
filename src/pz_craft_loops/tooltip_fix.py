# -*- coding: utf-8 -*-
"""Tooltip table rules for every Tooltip.json we produce (standalone builds, test bundle, and the
World Essentials work copies we hand to the WE dev).

Bug fixed (2026-11-01 bug pass): builders filled each SHARED tooltip key with the displayName of the
first buildable that used it. So all Community storage showed "White Counter, Charcoal Top (Corner)",
and two of those keys are Knox Buildworks' OWN keys, which meant we overwrote KBW's text for every
KBW / Vanilla Expanded / WE piece that uses them.

Rules:
  1. Never ship a key that Knox Buildworks itself defines: KBW's text must win. The list is read
     from the installed KBW translation files, with a static fallback.
  2. Our own shared keys (Tooltip_KBW_Shared_* that KBW does NOT define) get generic text that is
     true for every piece using them.
"""
import glob, json, os

KBW_ITEM = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600\3772269882"
# fallback if KBW isn't installed where expected (both confirmed in KBW's Tooltip.json, 2026-11-01)
_KBW_FALLBACK = {"Tooltip_KBW_Shared_StorageFixture", "Tooltip_KBW_DecorativeWallFixture"}

SHARED_TEXT = {
    "Tooltip_KBW_Shared_Wall": "Wall piece. Connects to neighbouring walls of the same style.",
    "Tooltip_KBW_Shared_Door": "Door or door frame.",
    "Tooltip_KBW_Shared_Vegetation": "Decorative plant. Blocks line of sight.",
    "Tooltip_KBW_Shared_Floor": "Floor covering.",
    "Tooltip_KBW_Shared_Decoration": "Decorative piece.",
    "Tooltip_KBW_Shared_Television": "Working television. Needs power to show a picture.",
}


def kbw_owned_keys():
    keys = set()
    for p in glob.glob(os.path.join(KBW_ITEM, "**", "Translate", "EN", "Tooltip*.json"), recursive=True):
        try:
            keys |= set(json.load(open(p, encoding="utf-8")))
        except Exception:
            pass
    return keys or set(_KBW_FALLBACK)


def fix_table(table, kbw_keys=None):
    """Return (fixed_table, report). Removes KBW-owned keys, rewrites our shared keys."""
    kbw_keys = kbw_owned_keys() if kbw_keys is None else kbw_keys
    out, removed, rewritten = {}, [], []
    for k, v in table.items():
        if k in kbw_keys:
            removed.append(k)
            continue
        if k in SHARED_TEXT and v != SHARED_TEXT[k]:
            rewritten.append(k)
            v = SHARED_TEXT[k]
        out[k] = v
    return out, {"removed_kbw_keys": removed, "rewritten_shared": rewritten}


def fix_file(path, kbw_keys=None):
    """Fix a Tooltip.json in place (keeps indent=1, UTF-8). Returns the report, or None if missing."""
    if not os.path.isfile(path):
        return None
    table = json.load(open(path, encoding="utf-8"))
    fixed, rep = fix_table(table, kbw_keys)
    if rep["removed_kbw_keys"] or rep["rewritten_shared"]:
        json.dump(fixed, open(path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    return rep
