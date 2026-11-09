# TODO: door handedness (Left / Right) instead of "(Mirrored)"

Opened 2026-11-08 during naming round 2 (`pz_craft_loops/tikitown_naming_pass.py`, `DOOR_NAMES`).

Sheet `fixtures_doors_tterika_02` (doors #33–#96 in `_names_doors_*.png`) is 32 mirror pairs: the
same door with the handle on the other side. For now, the second door of each pair is named
"<Door> (Mirrored)". The user agreed this is fine for now, but wants real handedness later.

To do:
1. In game (test bundle, doors are in their type groups), place each pair side by side and note
   which one hinges on the left when seen from the room side.
2. In `tikitown_naming_pass.py`, replace the `_PAIRS` loop's `" (Mirrored)"` with explicit
   `" (Left)"` / `" (Right)"` names per pair. Not every pair is guaranteed to put the same hand first.
3. Re-run `tikitown_naming_pass.py`, then the builders. Only names change; ids, groups and levels stay.
