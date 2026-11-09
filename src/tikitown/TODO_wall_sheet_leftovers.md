# TikiTown wall sheets: what is deliberately NOT built (decided 2026-11-08)

The full-sheet pass (`pz_craft_loops/tikitown_wall_extras.py`, files 41 / 42) covers 53 of the 69
style sheets completely. `pz_craft_loops/sheet_coverage.py` lists every tile without a buildable.
The leftovers below are **skipped on purpose** (user decision), not forgotten.

## Skipped, no plan to build
- **Wall fixtures** on the 8 `tikitown_vanilla_walls_add_01..06, _10, _12` sheets and
  `tikitown_walls_siding_01 / _02`: tiles 92–95 (vents, electrical box), 102/103, 110/111,
  118/119 (gas / electric meters). They're art only (no tile properties) and near-identical
  across sheets.
- **Siding posts**: `tikitown_walls_siding_01 / _02` tiles 120–127.

## Skipped for now (own layouts, need their own look later)
- `tikitown_tents_01`
- `tt_melos_tiles_overgrown_ruins_01`
- `walls_exterior_half_tterika_01`, `walls_exterior_house_tterika_02`,
  `walls_interior_bathroom_tterika_01`, `walls_interior_house_tterika_02`

These six only have their main wall / window / door pieces (sheet 21). To pick them up later:
render each sheet with `python pz_craft_loops/sheet_full_view.py <sheet>`, map the tile layout,
and extend `tikitown_wall_extras.py` with a per-sheet layout instead of the standard one.

## Expected `sheet_coverage.py` result while this stands
53 sheets fully used, and 10 sheets with only the fixture / post tiles above unused. The 6 sheets
listed above stay mostly unused.
