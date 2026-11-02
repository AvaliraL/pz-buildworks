# TikiTown Structural Walls — Knox Buildworks Expansion (candidate addition)

**Deliverable:** `21_tikitown_walls.json` — 75 new structural wall buildables for the World
Essentials "Knox Buildworks Expansion" build menu, drawn from Drazions Tile Pack
(`tikitown_tiles`) wall sheets that the WE author's `20_tikitown.json` does not cover.

This is an **investigation artifact**, not a live edit. It is written here under `zomboid/`
and does NOT touch any installed mod file. If adopted, it would be dropped into the WE Knox
Buildworks Expansion `definitions/` folder as a new numbered file.

## Why this exists

The WE Knox Buildworks Expansion integrates a large slice of TikiTown's tiles
(`20_tikitown.json`, 381 buildables), but every one of them is a floor, curtain, poster,
canopy, mural, or furniture piece. The diff below shows the gap.

| Set | Count |
|---|---|
| Distinct sprites referenced by WE `20_tikitown.json` | 949 |
| Distinct **structural wall** sprites in the TikiTown tile pack | 487 (across 75 wall sheets) |
| Structural wall sprites WE already references | **0** |

So the entire structural-wall catalogue is an expansion target. This file covers one clean
build-menu entry per wall **sheet/style** (75 total), rather than emitting every orientation
tile — matching how the WE author shapes `11_walls.json` (one buildable = one style, with
W + N faces + corner/pillar).

## Source of the tiles

- **Mod:** Drazions Tile Pack — workshop id `3046728955`.
- **Tile definitions:** `common/media/tikitown_tiles.tiles` (the full copy; the `media/`
  copy is an older 34-sheet subset and should NOT be used).
- Wall sheets are the ones whose tiles carry `WallW` / `WallN` facing flags or
  `WallType = wall`.

## Schema basis

Entries mirror the WE author's own structural-wall convention from
`World Essentials - Knox Buildworks Expansion/.../definitions/11_walls.json`, cross-checked
against the Knox base pack `definitions/vanilla/walls.json` (mod `3772269882`):

- `placement.kind = "wall"`, `requiresFloor: false`
- `stages[0].geometry.faces.W / .N` → the sheet's index-0 (W-face) and index-1 (N-face) sprites
- `object.cornerSprite / pillarSprite` → the sheet's index-2 (corner/pillar) sprite
- `health: 800`, `skillBaseHealth: 70` (from the base pack brick-wall example)
- tags `["tikitown","drazion","world-essentials"]`, keys `IGUI_WETiki_<sprite>` /
  `Tooltip_WETiki_<sprite>` (matching `20_tikitown.json`)

### Build recipes by material (matched to WE conventions)

| Material class | Tool | Materials | Skill | Action |
|---|---|---|---|---|
| Wood / siding / wallpaper / plaster / bathroom / decorative / interior / exterior | Hammer | 2 Plank + 4 Nails | Woodwork 4 | BuildWallHammer |
| Metal / industrial / commercial | Welding mask | 2 SheetMetal + 4 Screws + WeldingRods + BlowTorch | MetalWelding 4 | BuildWallMetal |
| Brick / stone / cement | Mason's trowel | 4 ClayBrick + mortar (concrete) | Masonry 5 | BuildWallNoTool |

## Important caveat on sprite naming (verified)

The `.tiles` records store an authoring token that *looks* like a sprite name
(e.g. `tikitown_walls_wall_burnt_0`) but is a copy-paste artifact — it is identical across
unrelated sheets. The **real** sprite id is `"<sheetName>_<tileIndex>"`, consistent with how
WE's existing `20_tikitown.json` references sprites (e.g. `fixtures_windows_curtains_tterika_01_124`).
This file uses the `<sheet>_<index>` form. The per-sheet tile layout is consistent across all
wall sheets: index 0 = W face, 1 = N face, 2 = corner/pillar, 3 = SE corner, 4+ = window/door
frame variants.

## Known limitations / for the mod author to review

- One sheet (`industry_containers_tterika_01`) has only 2 wall tiles, so its corner/pillar
  falls back to the N sprite. Harmless but not ideal.
- Only solid wall segments are emitted. Window-frame and door-frame variants (indices 4+) are
  intentionally omitted to keep the menu clean; they could be added as separate entries if
  desired.
- `displayName` "Style N" numbering is per-subcategory and sequential; the author may prefer
  descriptive names (e.g. "Red Brick", "White Wallpaper").
- Not verified in a running game. Sprite ids and schema are derived from the installed files;
  in-game placement should be smoke-tested before shipping.

## Scratch / provenance (under `pz_craft_loops/`)

- `parse_tiles_v3.py` → `_wall_sheets_v3.json` — authoritative per-sheet tile layout + flags.
- `parse_we_tiki.py` → `_we_tiki_sprites.txt` — the 949 sprites WE already references.
- `diff_walls.py` → `_diff_walls_out.txt` — coverage diff (0/487).
- `gen_wall_defs.py` — generator that produced `21_tikitown_walls.json`.
- `validate_walls.py` — structural validation (0 errors).
