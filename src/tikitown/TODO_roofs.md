# TODO — Roof sheets (shared layout; some have +4 skylight tiles)

**Status:** OPEN — reference for when roofs are implemented.

## Sheet layout (what the tiles mean)
Each sheet has **14 rows** (the reference image shows only the first 2). Rows 0–1 are described
below; the remaining rows presumably continue the same height-stepped slope pattern (other
facings / slope directions / pitches — confirm per sheet when implementing).

Each roof sprite is the **same roof-slope angle but at a different vertical HEIGHT/level**.
Stacking them lets the player build a **multi-level / tiered roof** (step the slope up or down
level by level). From the first two rows (ref image, tikitown_roofs_05):
- Row 0: a run of the slope tile descending (height offset increasing) across the leading
  columns, then the **skylight** tiles in the last 2 columns.
- Row 1: the slope tile ascending across the leading columns, then **skylight** tiles again in
  the last 2 columns.
- The skylights are the +4 "extra" tiles (2 per row across rows 0–1) that are blank on the
  non-skylight sheets.

## Sheets (all share the SAME roof sheet layout)
tt_newburbs set (color-named):
- `tt_newburbs_roofs_01a_lightgray.png`
- `tt_newburbs_roofs_02a_warmgray.png`
- `tt_newburbs_roofs_03a_redbrown.png`
- `tt_newburbs_roofs_05a_slategreen.png`
- `tt_newburbs_roofs_06a_slateblue.png`
- `tt_newburbs_roofs_07a_black.png`

tikitown set:
- `tikitown_roofs_01.png`
- `tikitown_roofs_02.png`
- `tikitown_roofs_05.png`
- `tikitown_roofs_06.png`

> All of the above use the identical roof sheet layout, so one geometry template can drive every
> color/sheet (map by sheet name, same per-sprite offsets).

## Skylight variants (+4 skylight tiles present; blank in the others)
These sheets have an ADDITIONAL 4 skylight tiles where the others are blank:
- `tt_newburbs_roofs_01a_lightgray.png`
- `tt_newburbs_roofs_02a_warmgray.png`
- `tt_newburbs_roofs_03a_redbrown.png`
- `tt_newburbs_roofs_05a_slategreen.png`
- `tt_newburbs_roofs_06a_slateblue.png`
- `tt_newburbs_roofs_07a_black.png`
- `tikitown_roofs_02.png`
- `tikitown_roofs_05.png`
- `tikitown_roofs_06.png`

So: emit the 4 skylight buildables ONLY for the skylight-bearing sheets; skip those 4 slots
(blank) on `tikitown_roofs_01.png` and any other non-skylight sheet.

All in `c:\Users\josep\Kiro\zomboid\Tiles\`.

---

## TODO — Automatic multi-height roof building (garage-door-style sizing)

**Status:** OPEN — design/feature idea for the roof implementation.

Build roofs the same way the garage doors do multi-tile sizing: the player picks an **angle**
(roof slope / sheet-style), uses the catalogue **arrows to select a HEIGHT** (number of levels),
and on build it places that many roof tiles automatically — a true multi-level roof in one action.

Mechanics:
- Each height N buildable uses the **first N roof tiles for that angle, starting at the lowest
  height** (sprite indices for levels 1..N on that sheet).
- Group per angle (one catalogue entry, arrow through heights 1..max), exactly like the garage
  per-color groups cycle through tile widths.
- **Cost scales with N** (per-tile cost × number of tiles), same approach as the garage per-tile
  recipe scaling.
- Max height = however many stepped-height tiles the sheet provides for that angle (14 rows total;
  confirm the usable per-angle height count when mapping the sheet).

Reference implementation to mirror: `29_tikitown_garages.json` (per-tile geometry + per-tile
recipe scaling) and WE `17_garage_door_sizes.json`.

---

## "B" sheets — end pieces / gutters (match the associated "A" style)

The `tt_newburbs_roofs_*b_*` sheets are the companion **end pieces / gutters** for each matching
`*a_*` roof color/style. Their sheet layout roughly follows the same order as the A sheets but is
**NOT identical** — do not assume the A offsets map 1:1 onto B. Map the B sheet separately when
implementing, and pair each B end-piece/gutter set with its associated A style (same color).

---

## Authoritative roof geometry (extracted from ExtraNoise addon Lua, 2026-10-22)

Source: `addRoofingToMenu()` in `BuildingMenu_ExtraNoisesNewburbs.lua` (approx L1461-1631).
Extracted to `pz_craft_loops/_addon_structure.txt`; full Lua table captured in session.

**Build model (IMPORTANT, differs from walls):** roofs use `BuildingMenu.onBuildSimpleFurniture`
(floor-helper placement: `renderFloorHelper=true`, `needToBeAgainstWall=false`,
`blockAllTheSquare=false`, `canPassThrough=true`, `isCorner=true`, `canBarricade=false`,
`dismantable=true`), NOT the wall-build model. So in our JSON these are furniture-style
buildables (placement kind likely "floor"/furniture), with up to 4 facings (sprite=W, northSprite,
eastSprite, southSprite). This is the same floor-helper technique worth revisiting for our
furniture deliverables (see note at bottom).

**Recipes:** `BuildingMenu.RoofTileRecipe` default; the two glass/skylight pitched pieces use
`BuildingMenu.GlassRoofTileRecipe`.

**Colors (7):** Light_Gray, Warm_Gray, Red_Brown, Light_Brown, Slate_Green, Slate_Blue, Black.
NOTE this color set differs from the clapboard walls' 9/our 10. Each color uses TWO sheets:
  - `en_newburbs_roofs_0Xa_<color>` (A = main roof tiles)  -> Drazion `tt_newburbs_roofs_0Xa_<color>`
  - `en_newburbs_roofs_0Xb_<color>` (B = fascia/gutter)    -> Drazion `tt_newburbs_roofs_0Xb_<color>`
(Confirm which of the 7 Drazion kept via the tiledef, same as we did for walls. The TODO sheet
list above shows lightgray/warmgray/redbrown/slategreen/slateblue/black present as tt_ ; verify
light_brown.)

**A-sheet pieces (26 per color)** — name / sprite / northSprite [/ eastSprite / southSprite]:
  Roof_Pitched_1..6:  (5,16,8,29)(4,17,9,28)(3,18,10,27)(2,19,11,26)(1,20,12,25)(0,21,13,24)
  Roof_Pitched_2_wGlass (7,14) + Roof_Pitched_3_wGlass (6,15)   <-- these are the SKYLIGHTS, GlassRoofTileRecipe
  Roof_Valley_1..6:   (32,48,61,45)(33,49,60,44)(34,50,59,43)(35,51,58,42)(36,52,57,41)(37,53,56,40)
  Roof_Inner_1..6:    (69,72,80,93)(68,73,81,92)(67,74,82,91)(66,75,83,90)(65,76,84,89)(64,77,85,88)
  Roof_Ridge_Cap_1..6:(101,104)(100,105)(99,106)(98,107)(97,108)(96,109)

**B-sheet pieces (fascia/gutter, ~31 per color)** — same (sprite,N[,E,S]) tuple format:
  Roof_Fascia_1..6: (0,45,29,48)(1,44,28,49)(2,43,27,50)(3,42,26,51)(4,41,25,52)(5,40,24,53)
  Roof_Fascia_Extension_Top_1/2: (6,46,30,54)(14,38,22,62)
  Roof_Fascia_Extension_Middle_1/2: (7,47,31,55)(15,39,23,63)
  Roof_Gutter_Top: (78,94,70,86) ; Roof_Gutter_Top_Inner_Corner: (96,98,104,106) ;
    Roof_Gutter_Top_Outer_Corner: (102,110,118,126)
  Roof_Gutter_Middle: (79,95,71,87) ; Roof_Gutter_Middle_Outer_Corner: (103,111,119,127)
  Roof_Apex_Fascia_Back_1..6: (69,80)(68,81)(67,82)(66,83)(65,84)(64,85)
  Roof_Apex_Fascia_Front_1..6: (77,88)(76,89)(75,90)(74,91)(73,92)(72,93)

Total ~57 pieces/color x 7 colors ~= 400 buildables if emitted 1:1. The multi-height-builder
idea above would instead group the stepped pitched tiles into height-selectable entries.

## Status of related work (2026-10-22)
- **Roof-TRIM WALLS: DONE.** The clapboard-walls section also defined 31 roof-trim wall pieces
  per color (Roof Slope Wall 1-6, Roof End Small/Medium/Big, Roof Steep Slope Wall 1-12, Roof
  Steep End x6, plus 3 extra plain walls + 2nd pillar). These were ADDED to `28_tikitown_
  newburbs_walls.json` (+ `_accurate`) on 2026-10-22 (10 colors x 46 pieces = 460 each; names use
  "<Color> Clapboard <Type>"). These are the gable-end filler WALLS that match roof pitches; they
  are NOT the roofs themselves. The actual Roofing category above is still OPEN.

## Other untouched Newburbs sheets (not yet implemented)
Beyond roofs, the Newburbs tilepack has sheets we have not converted at all, e.g.:
- `tt_newburbs_trim*` (trim pieces) -- NEEDS its own extraction + conversion pass.
- Possibly others (flags `addExtraNoisesNewburbsFlagsToMenu`, standalone windows
  `addWindowsPlusToMenu`). Audit the full `tt_newburbs_*` sheet list in the Drazion tiledef vs
  what we've shipped (21/22/26/27/28/29) and the addon's menu sections to enumerate remaining gaps.

---

## Technique note: floor-helper placement for FURNITURE (revisit)
The roofs' `onBuildSimpleFurniture` + `renderFloorHelper=true` placement (free-placement on a
tile with a ghost helper, 4 facings, not wall-locked) is a cleaner placement model than some of
our current furniture. Worth revisiting for our furniture deliverables (23/24/25) where a piece
should sit on the floor and rotate through facings rather than snap to a wall edge.
