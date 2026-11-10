# Resume: tterika wall detailing (files 43 / 44)

Paused 2026-11-08 at the user's request, mid-verification. Nothing is exported, committed or pushed.
The repo is clean at `85d7d36` (`handoff-2026-11-08-plaster-fix`).

## What's built

Generator: `pz_craft_loops/tikitown_wall_detailing.py`. It's hooked into `_run_all`, `build_tikitown_mod`,
`build_merged_test_mod` (TT_FILES / TT_PACK_OF / TT_KEEP_GROUPS) and `export_repo`.

- `43_tikitown_wall_paint_cladding.json`: 860 pieces (86 colours x 10 pieces), category "Wall Paint & Cladding".
  - Source sheets: interior/exterior detailing tterika_01/02.
  - Uses our own tile copies in tilesets `KBWTikiTownDetail1..3` (512 / 512 / 352), in the existing
    `kbwtikitown_walloverlays` file. No new mod.info lines.
  - Each copy has a facing flag added by its position in the row.
- `44_tikitown_wall_trim.json`: 231 pieces (141 W/N pairs), category "Wall Trim". Uses the pack tiles as they are.
- The user chose: all pieces, the new categories, material costs, and names in the style of the naming pass.
- Built into the WE work copy and the test bundle: TikiTown 7607 / 24 defs, test bundle 8159.

## Checks that passed (`_detail_verify.py`)

- All 1748 sprites resolve, and every copy has exactly one attached* flag.
- The existing overlay, soundproof and props tilesets are unchanged.
- No committed sprite name went missing.
- All translations are present.
- The pack is 15.9 MB.

## RESOLVED 2026-11-10: KBW registry sort depth

All three builders now write every definition file in md5(id) order (`kbw_sort_order.py`).
The WE layout went from 472 to 20 (`_depth_compare`), or 85 by `kbw_sort_depth_check` (KBW+VE alone: 83).
The robustness checks in `_depth_options` (drop any file, random load order, 2x growth) all stay at or below 37.
Side effect: the next hand-off diff reorders every definition file. The data is unchanged; tell the WE dev.
43/44 and the pump sinks are confirmed in game (user, 2026-11-10); 43/44 are marked Completed in the test bundle.

## (history) KBW registry sort depth (`_depth_compare.py`)

| Layout | Depth |
|---|---|
| Test bundle (merged file) | 82, fine |
| WE layout, live upstream | 288 |
| WE layout, pushed hand-off | 80 |
| WE layout, NOW with 43/44 | **469**. Overflow happened at 482. DO NOT ship like this. |

- Every file is shallow alone (≤24). The depth comes from how the files combine in load order:
  - dropping 21 or 25 → about 40–53
  - dropping 44 → 113
- Next: run `_depth_options.py` (written, not run yet). It simulates writing EVERY definition file of
  both submods in md5(id) order, plus robustness checks (drop any one file, random file order, growth).
- If that stays low (around 80–90), apply md5 ordering to all files at build time, then re-verify.
  That's best done in one place (the we_sync step, or each builder's write step).
  - Reordering existing files makes a big but data-neutral diff. Tell the WE dev.

## In-game findings (2026-11-10)

- Corners work (dismantlable thumpables, with depth).
- The earlier "corner draws over the fridge" report also cleared after leaving the area and coming
  back, so it was probably the same stale render, not missing depth. The `tileDepthTextureAssignments.txt`
  (vanilla presets for our copies) is kept because it matches vanilla. Possible test: remove it,
  rebuild, check corner + fridge after a reload. If that still looks right, the file can be dropped.
- Wall panels "don't build" at first: KBW attaches the sprite but never marks the render chunk dirty,
  so it shows only after a redraw (leaving the area and coming back fixes it). This affects file 39
  panels too. Reported for the KBW dev in `zomboid/knoxbuildworks/DEV_BUG_REPORT_attached_sprite_redraw.md`.
  A stopgap on our side (wrap AttachedSprites.attach/remove) is possible but untested.

## After that

1. User tests in game, using the test bundle:
   - a few colours: lower panel, top band, corner, end cap, window / door-frame pieces
   - one cladding type
   - trim pairs
2. The 44 trim profile names are automatic (Baseboard / Chair Rail / Crown Molding / Wainscot Panel /
   Corner Trim, from each tile's bbox). Review them in game; adjust `_trim_profile` / `_trim_colour` if needed.
3. Hand-off notes section + commit `we/` alone, then tag, then `src/` + `notes/`. Push only when asked.

Scratch files (delete when done):
- `_tterika_detailing_*.py/txt`, `_detail_*.py/txt/png`, `_depth_*.py`
- `_sheet_*detailing*.png`, `_cache_walldetail/`
