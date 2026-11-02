# Newburbs tilepack — coverage status (what we've converted vs what's left)

Scope: the `tt_newburbs_*` family in Drazion's merged tilepack (`tikitown_tiles`), which carries
the ExtraNoise Newburbs art. Geometry/recipes are lifted from the ExtraNoise addon Lua
(`BuildingMenu_ExtraNoisesNewburbs.lua`) where a build section exists. "No source" = the addon has
no build recipes for that sheet, so there is no authoritative geometry to lift.

## Drazion tt_newburbs_* sheet inventory (36 sheets, 6 families)
| Family | Sheets | Status |
|---|---|---|
| `tt_newburbs_walls` | 10 (colors) | DONE — file 28 (+accurate), 46 pieces/color incl roof-trim walls |
| `tt_newburbs_interiors` | 4 (16 colors) | DONE — file 27 (+accurate), 15 pieces/color |
| `tt_newburbs_roofs` | 12 (6 colors x a/b) | DONE — file 31 (+accurate), A+B sheets, 53 tiles/color + 6 multi-height/color |
| `tt_newburbs_doors` (garages_01) | 1 | DONE — file 29 (garage doors, 8 colors x widths 2-6) |
| `tt_newburbs_doors` (doors_01) | 1 | DONE — file 33 (+accurate): 18 wooden doors + 3 sliding |
| `tt_newburbs_details` (flags) | 1 | DONE — file 32: 8 decorative flags (Decorations/Newburbs Flags) |
| `tikitown_newburbs_windows_01` (windows) | 1 | DONE — file 34 (+accurate): 13 standalone windows (NOTE tikitown_ prefix, not tt_newburbs_) |
| `tt_newburbs_trim` | 7 (colors) | NOT DONE — **no addon source** (wall trim, see below) |

## Addon menu sections vs our coverage
The ExtraNoise addon defines these build sections (from `addCategoriesToBuildingMenu`):
- `addExtraNoisesNewburbsFlagsToMenu` (details_01) -> DONE (file 32).
- `addDoorsToMenu` (doors_01: wooden + sliding) -> DONE (file 33).
- `addGarageDoorsToMenu` (doors_garages_01) -> DONE (file 29).
- `addExtraNoisesNewburbsColouredWallsToMenu` (interiors) -> DONE (file 27).
- `addExtraNoisesNewburbsClapboardWallsToMenu` (walls) -> DONE (file 28).
- `addRoofingToMenu` (roofs a+b) -> DONE (file 31).
- `addWindowsPlusToMenu` (windows) -> DONE (file 34).

So EVERY buildable addon section is now converted. The only remaining Newburbs art with no
deliverable is the wall trim (`tt_newburbs_trim_*`), which has NO addon build source at all.

---

## DONE: Windows+ (`addWindowsPlusToMenu`) -> file 34
The addon's Windows+ section builds 13 standalone windows (W/N pairs: 0/4, 8/12, 16/22, 17/21,
18/20, 19/23, 48/54, 49/53, 50/52, 51/55, 80/86, 81/85, 82/84; `onBuildWindow`).

**Initially mis-flagged BLOCKED, now DONE.** The sheet exists in Drazion but under an INCONSISTENT
name: Drazion renamed `en_newburbs_windows_01` to **`tikitown_newburbs_windows_01`** (note the
`tikitown_` prefix, NOT the `tt_newburbs_` prefix the rest of the family uses). My first tiledef
check only searched for `tt_newburbs_windows_01` and missed it. Re-verified with
`find_windows_sheet.py` -> `_windows_sheet.txt`: Drazion `tikitown_newburbs_windows_01` PRESENT
(8x16, 128 tiles), same dims as ExtraNoise `en_newburbs_windows_01`.

Shipped as `34_tikitown_newburbs_windows.json` (+accurate): 13 windows, category `Windows`,
subcategory `Newburbs Windows`, wall placement W/N, `windowsframe` flags (thumpable/barricade/
hoppable), cheap WW4 / accurate WW2. Sprites map `en_newburbs_windows_01_<i>` ->
`tikitown_newburbs_windows_01_<i>` (index-preserving, same as every other Newburbs family).
Emitter: `emit_windows_34.py`; geometry `_windows_geom.json`.

LESSON: Drazion's merge prefixes are NOT uniformly `tt_newburbs_` — at least the windows sheet uses
`tikitown_newburbs_`. When a sheet seems "missing", search for `*newburbs*<family>*` broadly before
concluding it was dropped.

---

## NO SOURCE: Trim (`tt_newburbs_trim_*`, 7 sheets)
Trim colors present in Drazion: `01_white`, `02_red`, `05_darkgreen`, `06_darkblue`, `08_black`,
`trim_add_01_brightred`, `trim_add_01_orange` (all 8x16, 128 tiles).

**Problem:** NO addon anywhere defines trim builds. Verified by searching every installed addon Lua
for `newburbs_trim` / `en_newburbs_trim` — zero references. So unlike walls/interiors/roofs/doors/
flags, there is **no authoritative geometry or recipe to lift** for trim. The sheets are art
Drazion merged but which no Building Menu mod ever wired up.

**What this trim IS:** EXTERIOR WALL TRIM — decorative trim pieces that go on/around wall edges
(corner boards, window/door casing, belt courses / banding, etc.). It is NOT roof trim. Roof trim
(fascia/gutters/apex) is the ExtraNoise roofs "B" sheets and is ALREADY DONE in file 31. Do not
confuse the two: `tt_newburbs_trim_*` = wall trim; `tt_newburbs_roofs_*b_*` = roof fascia/gutter.

Implication: converting wall trim means **authoring geometry from scratch** by reading the sprite
sheets (what each tile is, facing/pairing, which pieces are corner boards vs edge casing vs
banding). That is exactly the kind of guess-work that produced the N-face bugs we had to fix on
hand-built files, so it needs a deliberate visual pass, not a mechanical lift. Recommend a dedicated
wall-trim session: open each trim PNG, map the layout, decide the piece set + placement with the
owner, then emit. Likely target category: `Walls and Wall Finishes` (as a trim/accent subcategory),
NOT Roofing.

---

## Reusable artifacts (pz_craft_loops/)
- `list_newburbs_sheets.py` -> `_newburbs_sheets.txt` : full tt_newburbs_* sheet inventory.
- `check_fdw_sheets.py` -> `_fdw_sheets.txt` : flags/doors/windows sheet presence (Drazion vs ExtraNoise).
- `extract_flags_doors_geom.py` -> `_flags_doors_geom.json` : flags + doors geometry.
- `emit_flags_doors.py` : emits files 32 (flags) + 33 (doors, +accurate).
- `extract_roofs_geom.py`, `emit_roofs_31.py` : roofs.
- Deliverables: 27, 28, 31, 32, 33 (+ _accurate pairs for 27/28/31/33) in zomboid/tikitown/.
