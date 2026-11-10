# -*- coding: utf-8 -*-
"""Write every KBW definition file's buildables in md5(id) order (2026-11-10).

KBW's Registry:list() sorts all buildables by id with Kahlua's table.sort: a recursive
first-element-pivot quicksort whose depth explodes on ordered runs. Kahlua tables keep insertion
order, so files written in generation order (long sorted runs) pushed the depth past Kahlua's stack:
"Stack overflow" in partition_comp, and KBW never finished loading (2026-11-08, depth 482).
Files 39-42 were already md5-ordered; with 43/44 added the WE layout reached depth 472 again because
the OTHER files (21, 25, 28, 40, 41, ...) still combine into ordered runs. Simulated
(kbw_sort_depth_check / _depth_options): every file md5-ordered -> depth 20; worst with any one file
dropped 26; worst of 20 random file load orders 37; with 2x the TikiTown content 27.
Menu order is unaffected: KBW orders a group's members by level, then id.
"""
import hashlib


def md5_order(buildables):
    """Sort a buildables list in place by md5(id); returns it."""
    buildables.sort(key=lambda b: hashlib.md5(str(b.get("id", "")).encode("utf-8")).hexdigest())
    return buildables
