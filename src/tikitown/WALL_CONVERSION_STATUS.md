# TikiTown WALL Sheets - Conversion Status

> ## GARAGE DOORS COMPLETE (in-game verified) - 2026-08-28
> `29_tikitown_garages.json` - 40 buildables = 8 colors x widths 2-6 (gen_tikitown_garages.py),
> from tt_newburbs_doors_garages_01. Confirmed working in-game. Modeled EXACTLY on KBW's own
> garage doors (and our GarageDoorKnox_B): multi-tile fixed-width, grouped per color (arrow between
> sizes). Geometry = plain-string sprites by array index (NOT dx/dy object tokens - that caused the
> gap/diagonal bug): W-face vertical rows with layer y=-(width-1), REVERSED order (end..start);
> N-face horizontal single row (start..end). 2-wide omits center = [left,right]. center repeats for
> wider. E triple (base+0/1/2)->W-face, S triple (base+3/4/5)->N-face. kind:object dontNeedFrame
> allowSpriteReuse. Metal welding recipe scales per tile. Closed-only (matches KBW).

> ## NEWBURBS WALLS COMPLETE (in-game verified) - 2026-08-28
> `28_tikitown_newburbs_walls.json` fully REBUILT v2 to match newburbs INTERIORS parity
> (gen_newburbs_walls_v2.py) and confirmed working in-game. 150 buildables = 15 per sheet
> x 10 color sheets (tt_newburbs_walls_01_white .. 18_black). Single color/sheet, base 0,
> no leading blank, identical absolute layout across all sheets. 15 pieces/color: Wall,
> Corner, Pillar, Window, Door Frame, Wide Window L/C/R, Tall Window, Wide Tall Window
> L/C/R, Garage Door Frame L/C/R (garage at row7 = sprites 56-61). Routed to Complete tab.
> SUPERSEDES the old 30-buildable version (wall/window/doorframe only, which also had the
> mis-indexed base-0/base-1 drift). ALL newburbs now complete (interiors + walls).

> ## NEWBURBS INTERIORS COMPLETE (in-game verified) - 2026-08-28
> `27_tikitown_newburbs_interiors.json` fully REBUILT v2 from the user tile catalog
> (gen_newburbs_interiors_v2.py) and confirmed working in-game. 240 buildables =
> 15 per color x 4 colors x 4 sheets (tt_newburbs_interiors_01..04). Each color block
> is 4 rows x 8 cols = 28 populated tiles (local 22,23,30,31 empty); color stride 32,
> sprite = color*32 + (row*8 + col). 15 pieces/color: Wall, Window, Door Frame, Wide
> Window L/C/R, Tall Window, Wide Tall Window L/C/R, Garage Door Frame L/C/R (all W+N
> paired into one wall object), plus standalone Corner + Pillar. Routed to the Complete
> tab. SUPERSEDES the old flag-anchor build (which had the index-drift bug).
> STILL OPEN: Newburbs WALLS (`28`) - distinct layout, awaiting separate catalog + rework.
> Color NAMES are placeholder (C1-C4; C2 is actually salmon-red) - cosmetic, TBD.

> ## MATERIAL WALLS COMPLETE (in-game verified) - 2026-08-28
> All material walls (`21_tikitown_walls.json`, 919 buildables incl. the standalone
> corners + pillars across every wall sheet) confirmed working in-game and routed to
> the **"TikiTown TEST - Complete"** tab (build_test_bundle.py file-level route).
> EXCLUDED - still in the in-progress "TikiTown TEST" tab:
> - **Newburbs interiors (`27`) + Newburbs walls (`28`)** - extensive sprite-INDEX
>   issues (wrong atlas cells); need a full re-derivation pass before they can ship.
>   Everything else in the walls/glass/doors/bedroom/counters set is now Complete.

> ## GLASS COMPLETE (in-game verified) - 2026-08-28
> Glass walls (`26_tikitown_glass.json`) confirmed working in a full in-game test:
> all pillars and corners render, all 5 colors appear, and all rotations work as
> expected. The 110 glass buildables (95 Glass Walls + 15 Glass Half-Walls/Fences,
> incl. the standalone corners + pillars) are now routed to the **"TikiTown TEST -
> Complete"** tab in the test bundle (build_test_bundle.py: file-level route for
> `26_tikitown_glass.json`, same pattern as doors). No open glass defects remain.

> ## CORNERS + PILLARS as standalone buildables - 2026-10-11
> Both the glass (`26`) and material-wall (`21`) deliverables now ship standalone
> **Corner** and **Pillar** buildables, because the engine's auto-corner only fires for
> true structural walls - our window/glass pieces (and the material corner cells, flagged
> `WallNWTrans`) don't trigger it, so `cornerSprite`/`pillarSprite` alone rendered nothing.
>
> - **Walls `21_tikitown_walls.json`(+_accurate):** +134 each (67 Corner + 67 Pillar, one per
>   material sheet). Corner sprite = sheet corner (primW+2, e.g. brick `_2`), Pillar = SE (primW+3,
>   e.g. brick `_3`). Now 919 buildables/file. gen_wall_corners_pillars.py.
> - **Glass `26_tikitown_glass.json`(+_accurate):** +70 each (35 Corner + 35 Pillar across the 7
>   true style bases 0/16/24/32/48/56/72 x 5 colors). Corner = base+2, Pillar = base+3. Now 115
>   buildables/file. gen_glass_corners_pillars.py.
> - **Modeling:** kind:"wall", single corner/pillar sprite on W+N faces, plain thumpable. These are
>   MANUAL, non-auto-joining pieces (the sprite carries a `*Trans` overlay flag, not a structural
>   `WallNW`), which is acceptable for decorative storefront/wall corners. pieceClass="corner"/"pillar".
> - **Glass rename:** the 5 "Half-Height Glass Wall" buildables renamed to "<color> Glass Fence" to
>   match the live naming convention.
> - **Recipes/material** cloned from each sheet/style's primary wall (cheap vs accurate preserved per file).
> - **Translations** regenerated (B42 JSON: 42/media/lua/shared/Translate/EN/IG_UI.json + Tooltip.json)
>   so the new names resolve. Backups: wall_backups\*.PRE_WALLCP.json / *.PRE_CP.json.
> - Known upstream bug documented separately: DEV_BUG_REPORT_floating_counters.md (15 floating
>   counters stack; tilesheet BlocksPlacement omission, not fixable in the definition).

> ## FULL PIECE EXPANSION (Option B) - 2026-10-11
> `21_tikitown_walls.json` and `21_tikitown_walls_accurate.json` were expanded from **69 -> 2137
> buildables each** (id-identical, 0 dup ids, 0 diagnostics). Previously each sheet shipped ONLY
> its plain wall (W/N + corner); the window/door/half-wall pieces baked into every sheet were
> dropped. Now EVERY non-damage tile is its own buildable.
>
> - Per file: 67 primary walls + 731 windows + 100 door frames + 1237 half-wall segments + 2 kept-manual.
> - Each buildable carries a `pieceClass` tag: `"wall"` | `"window"` | `"door"` | `"segment"`.
>   A curated subset is therefore a simple filter on `pieceClass` (no re-derivation needed).
> - **Modeling:** windows = `kind:"wall"` + `dontNeedFrame` + `providesWindowFrame` (NO windowGlass
>   callback - solid material, not glass). Door frames = `object.isDoorFrame` + `canPassThrough`
>   + `cutSpritesW/N`. Segments = `kind:"wall"`. Damage states (`*Trans` flags, ~sprite _72+) skipped.
> - **Drift fix:** each primary wall now points at the classifier's TRUE wall W index, fixing the
>   pre-existing lead=1 +1 drift (e.g. `tikitown_vanilla_walls_add_01` id stays `_0` but sprites
>   are now `_1`/`_2`). ID suffixes for new pieces = true sprite index.
> - **Recipes/costs preserved per file** (cheap wood vs accurate per-material) by deep-cloning each
>   file's own existing per-sheet buildable.
> - **MANUAL sheets left untouched** (verified correct by atlas slice): `tikitown_tents_01` and
>   `tt_melos_tiles_overgrown_ruins_01` both ship the correct plain wall W=_0/N=_1/corner=_2;
>   their extra cells are tent-awnings / ruins fragments, not the canonical window/door layout.
> - **REVERT:** pre-expansion originals saved at
>   `pz_craft_loops/wall_backups/21_tikitown_walls.PRE_EXPANSION.json` (+ `_accurate`). Restore to
>   return to the 69-buildable curated state. Tooling: `classify_wall_pieces.py` -> `_wall_pieces.json`,
>   `gen_wall_full.py` (--write to apply).
> - Test bundle `99_tikitown_TEST_ALL.json` rebuilt (2477 buildables, 0 dup) + copied to Workshop.

> DOORS (separate deliverable 22_tikitown_doors.json): fixtures_doors_tterika_01 (33 doors) +
> fixtures_doors_tterika_02 (64 doors) = 97 openable doors, built on the live WE 03_doors.json
> functional-door schema (4-face geometry + sprites open-states + hinge/doorknob recipe).

> COST PROFILES (see WALL_COST_PROFILES_README.md): walls + glass ship as TWO mutually-exclusive
> pairs with IDENTICAL ids (load exactly one pair). CHEAP = 21_tikitown_walls.json +
> 26_tikitown_glass.json (uniform wood, Woodwork). ACCURATE = 21_tikitown_walls_accurate.json +
> 26_tikitown_glass_accurate.json (per-material vanilla B42 recipes: wood Woodwork2, brick/stone
> Masonry2, metal + glass MetalWelding3 welded). Commercial-add walls in the CHEAP file were
> downgraded from metal to uniform wood to match the cheap model.

---


Markers: [x] converted in 21_tikitown_walls.json | [ ] pending-clean (safe) | [!] irregular (manual/skip) | [X] excluded by decision
"Clean" = binary-framed .tiles parse confirms first three real tiles = WallW / WallN / corner(WallNW|WallSE).
See TILESHEET_INDEX.md for the full by-type index with [K] = already-in-Knox markers.

## Converted (70 buildables in 21_tikitown_walls.json - RE-AUDITED against raw .tiles flags)
Brick (15), Wallpaper (10), generic TikiTown Walls (15), Bathroom (6), Decorative (5),
Siding (4), Commercial-add (3), Stone (3), Industrial/Metal (2), Interior (2), Plaster (2),
Exterior (2), Wooden (1). Full per-sheet list in 21_tikitown_walls.json.

### Re-audit (post-glass-lessons) - audit_all_walls.py vs fresh raw-.tiles parse
- 70/70 remaining buildables VERIFIED CORRECT: every sheet maps W=idx0(WallW), N=idx1(WallN),
  corner=idx2(WallNW) against fresh single-flag parse. No gap mis-maps, no W/N swaps.
  (Wall sheets are dense/regular at the top, unlike the glass sheets - the gap-drift that hit
  glass does not occur here.)
- REMOVED 1 phantom: `tikitown_commercial_walls_add_04` ("Commercial Wall - Style 4") referenced
  a sheet with NO .png backing in the tilepack (only _01/_02/_03 exist). It was manufactured by
  a bug in the old parser cache. Would have rendered as a missing texture in-game.
- Tooling fixes (scratch): parse_tiles_v3.py rewritten to split on real 4-byte record prefixes
  (fixes FLAG-BLEED where each cell inherited the prior cell's flag, and the PHANTOM-SHEET
  over-count). gen_wall_defs.py now (a) guards: skip any sheet whose idx0!=WallW or idx1!=WallN,
  and (b) brick/stone use the WOOD recipe to match the committed brick-cost decision.
- Brick/stone cosmetic note: pillarSprite uses the NW-corner (idx2); the SE piece is idx3.

## Pending - CLEAN (safe to convert as complete sheets) - 17
- [ ] tikitown_courthouse_01
- [ ] tikitown_newburbs_interiors_add_01
- [ ] tikitown_walls_brick_burnt
- [ ] tikitown_walls_wall_burnt_01
- [ ] tikitown_whatthefun_01
- [ ] tikitown_whistlin_dixie_01
- [ ] tt_newburbs_interiors_01
- [ ] tt_newburbs_interiors_02
- [ ] tt_newburbs_interiors_03
- [ ] tt_newburbs_interiors_04
- [ ] tt_newburbs_walls_04_warmgray
- [ ] tt_newburbs_walls_05_red
- [ ] tt_newburbs_walls_06_orange
- [ ] tt_newburbs_walls_07_redbrown
- [ ] tt_newburbs_walls_11_yellow
- [ ] tt_newburbs_walls_14_blue
- [ ] tt_newburbs_walls_16_pink
- [ ] tt_newburbs_walls_17_coolgray
- [ ] tt_newburbs_walls_18_black

## Excluded by decision (will NOT convert)
- [X] industry_containers_tterika_01   (dropped; also already partly in Knox)
- [X] tikitown_towncenter_01 / _02 / _03 / _04 / _05  (all towncenter sheets are MIXED tile types)

## Pending - IRREGULAR (first 3 tiles are not W/N/corner; manual map or skip)
- [!] fixtures_doors_fences_tterika_01   (door frames)
- [!] tikitown_garage_01                 (garage-door segments, all WallW)
- [!] tikitown_railings_02               (t0=WallSE only)
- [!] tikitown_walls_commercial_01..05   (glass storefront, window-first layout)
- [!] tt_newburbs_doors_garages_01       (garage doors)
- [!] walls_commercial_tterika_01..08    (door-frame-first layout)  [note: no _06]
- [!] walls_exterior_roofs_tterika_02    (sloped roof-walls)
- [!] fencing_tterika_01                 (W/N swapped)
- [!] tikitown_power_plant_01            (W face far down the sheet)

## Method
Verdicts from pz_craft_loops/check_pending.py (binary-framed .tiles parser; records bounded by
the 4-byte count prefix, leading empty-flag header records stripped). Validated against raw bytes.
Confirm any sheet against its extracted PNG in zomboid/Tiles/ before converting.

### DEFECT FIX (in-game test): glass walls placed invisible - placement kind wrong
Found during live test: the commercial-glass buildables placed but rendered no sprite in-world
(icon showed fine in the Knox menu, proving the sprite loads). Root cause: all 30 glass WINDOW
buildables (block idx 0,16,32,47,55,67 x 5 colors) were authored as `placement.kind:"object"`
+ `requiresFloor:true`, but the raw .tiles data flags every one as a WALL-mounted window
(WindowW/WindowN + cutW/cutN + `wall` + WindowLocked, mat=Glass). A wall/window sprite rendered
at an object's floor anchor draws off the visible tile -> invisible. The half-height pieces
(idx24, WallWTrans/WallNTrans) were already correctly `kind:"wall"` and rendered fine, which is
why only the full-height windows vanished.
FIX (fix_glass_placement.py): converted all 30 object buildables -> `kind:"wall"`,
requiresFloor:false, added dontNeedFrame+providesWindowFrame (standalone window-wall), swapped
timedAction BuildWoodenStructureSmall->BuildWallHammer, dropped canBarricade. Kept ids,
displayNames, recipes, and windowGlass onCreate callback. Applied to BOTH 26_tikitown_glass.json
and 26_tikitown_glass_accurate.json. Verified: 35 buildables each, all kind:wall, W=blockIdx /
N=blockIdx+1 matches audited block structure, 0 diagnostics. (Audit: audit_glass_full.py ->
_glass_full_audit.txt; verify: verify_glass_fix.py.)

### DEFECT FIX (in-game test): glass sprite INDICES mismarked (wrong atlas cells)
After the object->wall placement fix, live testing showed the frameless pane / frameless+lower /
multi-pane grid pieces still rendered wrong (pane invisible, "+ lower panel" showed a bare PILLAR,
grid invisible). Root cause: the buildable sprite suffixes were off - parse-order index != true
atlas sprite number (the sheet has blank/gap cells that shift the row*cols+col numbering). The
earlier corner-reference derivation was also unreliable.
AUTHORITATIVE METHOD (now the standard for sprite verification): slice the atlas PNG into a
labeled contact sheet (slice_glass_sheet.py; sheet is 8 cols x 16 rows of 128x256 cells, sprite
number N = row*8 + col) and READ the art directly. Confirmed uniform across all 5 colors
(verify_glass_allcolors.py).
Correct W-sprite per role: Framed+Lower=0, FullWindow=16, HalfWall=24, FullTall=32,
FramelessPane=48 (was 47), Frameless+Lower=56 (was 55), MultiPaneGrid=72 (was 67). N face = W+1.
First four were already correct; only the last three roles were wrong.
FIX (fix_glass_indices.py): remapped W 47->48, 55->56, 67->72 (+iconSprite) in BOTH
26_tikitown_glass.json and _accurate - 15 buildables each (3 roles x 5 colors). Buildable IDS kept
at the OLD numeric suffix for stability (so id ..._47 now draws sprite _48 - intentional; changing
ids would break saved builds + the test bundle). Verified 0 diagnostics, 0 mismatches
(verify_glass_idx_fix.py), 35 unique ids per file.
LESSON: never trust parse-order index as the sprite number on a gappy sheet. Slice the atlas and
eyeball it. This likely affects other extracts too - re-verify any sheet with blank cells.


## 2026-10-30: solid corner pillar is back: Newburbs INTERIOR only (WE-shipped version)
**RESOLVED, not a bug:** the blocking pillar was an old copy built before the walk-through fix.
Newly built pillars are fine. Existing pre-fix pillars keep their old solid flags until they are
rebuilt (dismantle and build again). Notes below kept for history.
- Reported in game on the server (World Essentials - TikiTown Buildworks). Other wall sets are fine.
- Checked: the shipped `27_tikitown_newburbs_interiors.json` matches our source. All 16 interior
  `pieceClass:"pillar"` pieces still carry the walk-through fix (`blockAllSquare:false`,
  `canPassThrough:true`, no `isThumpable`). So the definition flags didn't regress.
- Suspects (unverified):
  1. What's being hit may be the interior **corner** pieces (`pieceClass:"corner"`), which block on
     purpose, not the pillars.
  2. The **Newburbs interior tile sheet's own properties** (`solid`/`solidtrans` on the pillar sprite),
     which a definition flag can't override.
  3. A KBW/WE build path ignoring `canPassThrough` for this sheet.
- To check in game: build one interior pillar on open floor (no walls) and try to walk through it.
  Then compare with an exterior Newburbs pillar. Note the sprite name of the blocking piece.


## 2026-11-01: OUR BUG, fixed by the WE dev: wall sprite references off by one (181 entries)
- WE patch note: "Corrected 181 wall, window, doorway, corner and pillar entries ... including
  Commercial Styles 1-3."
- Verified against Drazion's tile flags (tikitown_tiles.tiles):
  - **Our** `21_tikitown_walls` pointed every face/corner/pillar/cut sprite one tile too high on 11
    sheets: W face on the `WallN` tile, N face on `WallNW`, corner on `WallSE`, pillar on `WindowW`,
    doorways shifted the same way.
  - The `tterika_02` sheets had irregular wrong offsets (-2/+1/+14).
  - Two single pillars were also wrong: tents_01 pillar off by one, and overgrown_ruins had a
    pillar that doesn't exist on the sheet.
- Affected sheets: tikitown_commercial_walls_add_01-03, tikitown_vanilla_walls_add_01-07,
  tikitown_walls_wallpaper_10, walls_exterior_half_tterika_01, walls_exterior/interior_house_tterika_02.
- **WE's version scores 100% correct** on the same check; ours failed on every affected sheet.
- Fix on our side: adopted WE's corrected file as `21_tikitown_walls_accurate.json`. The old file is
  kept as `21_tikitown_walls_accurate.before_WEfix_20261101.json`. Only sprite fields changed; ids
  and costs are unchanged.
- **Where it came from (checked 2026-11-01):** these sheets started as the WE dev's original curated
  walls, which were CORRECT (W=_0, N=_1, corner=_2; our own re-audit above confirmed 70/70). Our
  2026-10-11 "Full piece expansion" applied a "drift fix" that moved them to _1/_2 ("fixing the
  pre-existing lead=1 +1 drift"). That drift was a phantom created by the old parser's flag-bleed bug
  (each cell inherited the previous cell's flag). So our expansion introduced the off-by-one, and
  WE's patch reverts it. Tooling responsible: `classify_wall_pieces.py` / `gen_wall_full.py`. DO NOT
  re-run them as-is. Pre-expansion originals: `pz_craft_loops/wall_backups/21_tikitown_walls.PRE_EXPANSION.json`.
- **Full audit of everything else we generated** (`pz_craft_loops/_audit_faces.py`, tile-flag check):
  - PASS: TikiTown 21 (after WE fix), 22, 24, 25, 27, 28, 33; Community 35, 42-48, 55.
  - Flagged but explained (not this bug):
    - 26 glass corners/pillars: Drazion's glass sheets have no WallNW tiles at all, so corners use
      unflagged art tiles. User-confirmed in game. Two unflagged pillars per glass sheet (_6, _27)
      are worth a visual check.
    - 59 fencing: fences use Hoppable flags, not wall corner flags. User-confirmed in game.
    - 40 military cases, 57 TK wall shelf, 31 roof gutter corners, 32 Newburbs flags: wall fixtures
      or floor objects whose `attachedN/W` flags don't follow wall-face rules. Shelf, cases and
      flags were confirmed in game.
- Players: pieces built before the fix keep the wrong tile until rebuilt.
