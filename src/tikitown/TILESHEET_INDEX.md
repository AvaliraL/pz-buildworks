# TikiTown Tile Pack - Sheet Index by Type

Source: Drazions Tile Pack `tikitown_tiles.tiles` (extracted PNGs in `zomboid/Tiles/`).
Total sheets: 318.  Classification is heuristic (from tile flags + sheet name); verify visually before converting.

> WALLS FULL-EXPANSION (2026-10-11): 21_tikitown_walls.json(+_accurate) now ship EVERY non-damage
> tile per wall sheet as its own buildable (69 -> 2137), not just the plain wall. Each buildable has
> a `pieceClass` tag (wall/window/door/segment). See WALL_CONVERSION_STATUS.md. A `[x]` wall sheet
> below now contributes its full wall+window+door+segment set.
> NOTE: a crash from that full set led to a CURATED rebuild (sprites _0.._29 per sheet, 785 buildables)
> plus standalone Corner/Pillar pieces per sheet. Glass (26) likewise got Corner/Pillar pieces + a
> Half-Height->"Glass Fence" rename. See WALL_CONVERSION_STATUS.md (Corners+Pillars section) and
> DEV_BUG_REPORT_floating_counters.md.

Status markers:
- `[x]` converted in our candidate file 21_tikitown_walls.json
- `[K]` already included in LIVE Knox base + WE defs (sprite from this sheet referenced in-game)
- `[ ]` not referenced anywhere yet (pending / untouched)
- `[X]` EXCLUDED by decision (mixed-type sheet or chosen not to convert)
- `(no png)` = PNG not present in extracted zomboid/Tiles/ folder

Note: `[x]` and `[K]` can overlap when a sheet is partly in Knox and also in our file; our file was built to AVOID duplicating live sprites, so overlap means different sprites from the same sheet.

## container/appliance  (30 sheets | 0 converted | 9 in Knox)
- [ ] appliances_refrigeration_tterika_01
- [ ] appliances_refrigeration_tterika_01_on
- [x] fixtures_counters_tterika_01  (converted -> 23_tikitown_furniture.json)
- [x] fixtures_counters_tterika_02  (converted -> 23_tikitown_furniture.json)
- [ ] furniture_shelving_tterika_01  (REVERTED: removed from 23 - NOT in container-overlay registry, shelves wouldn't fill; use registered sheets below instead)
- [K] furniture_storage_tterika_01
- [ ] furniture_storage_tterika_02
- [ ] furniture_storage_tterika_03
- [ ] furniture_storage_tterika_04
- [x] furniture_tables_high_tterika_02  (converted -> 23_tikitown_furniture.json, multi-tile desks)
- [K] furniture_tables_low_tterika_01
- [K] location_shop_accessories_tterika_01
- [ ] location_shop_storage_tterika_01
- [K] tikitown_am_legends_01
- [ ] tikitown_appliances_01
- [ ] tikitown_bank_01
- [ ] tikitown_bowlingguns_01
- [ ] tikitown_bowlingguns_02
- [x] tikitown_furniture_01  (converted -> 24_tikitown_bookshelves.json, registered fill-overlay shelves idx 0-3)
- [ ] tikitown_furniture_02
- [x] tikitown_furniture_03  (converted -> 24_tikitown_bookshelves.json, registered fill-overlay bookshelves; [K] also partly in live Knox)
- [x] tikitown_furniture_bedroom_01  (converted -> 25_tikitown_bedroom.json; beds+dresser/sidetable/wardrobe/shelves storage. [K] = Light Low Modern Table already live, left as-is)
- [x] tikitown_furniture_bedroom_02  (converted -> 25_tikitown_bedroom.json)
- [x] tikitown_furniture_bedroom_03  (converted -> 25_tikitown_bedroom.json)
- [x] tikitown_furniture_bedroom_04  (converted -> 25_tikitown_bedroom.json)
- [x] tikitown_furniture_shelving_02  (converted -> 24_tikitown_bookshelves.json, registered fill-overlay shelves idx 2-4)
- [ ] tikitown_hospital_05
- [ ] tikitown_museum_02
- [ ] trashcontainers_tterika_01
- [ ] tt_melos_tiles_kitchen_props_01

## decoration  (52 sheets | 0 converted | 9 in Knox)
- [ ] overlay_grime_wall_tterika_01
- [ ] signs_tterika_01
- [ ] signs_tterika_02
- [ ] tikitown_book_overlay_01
- [ ] tikitown_decoration_vanilla_add_01
- [ ] tikitown_office_decoration_01
- [ ] tikitown_overlays_01
- [ ] tikitown_overlays_02
- [ ] tikitown_overlays_03
- [ ] tikitown_overlays_04
- [ ] tikitown_signs_01
- [ ] tikitown_signs_02
- [ ] tikitown_signs_03
- [ ] tikitown_signs_04
- [ ] tikitown_signs_05
- [ ] tikitown_signs_06
- [ ] tikitown_signs_07
- [ ] tikitown_signs_08
- [ ] tikitown_signs_09
- [ ] tikitown_signs_10
- [ ] tikitown_signs_11
- [ ] tikitown_signs_12
- [ ] tikitown_signs_13
- [K] tikitown_wall_decoration_02
- [K] tikitown_wall_decoration_03
- [K] tikitown_wall_decoration_04
- [K] tikitown_wall_decoration_05
- [K] tikitown_wall_decoration_06
- [ ] tikitown_wall_murals_01
- [ ] tikitown_wall_murals_02
- [K] tikitown_walls_decoration_01
- [K] tikitown_walls_decoration_07
- [ ] tikitown_walls_decoration_08
- [ ] tikitown_walls_decoration_09
- [ ] tikitown_walls_details_01
- [ ] tikitown_walls_details_02
- [ ] tikitown_walls_details_03
- [ ] tikitown_walls_details_04
- [ ] tikitown_walls_overlay_01
- [ ] tt_newburbs_details_01
- [ ] vegetation_ornamental_tterika_01
- [ ] walls_decoration_mirrors_tterika_01
- [ ] walls_decoration_paintings_tterika_01
- [K] walls_decoration_posters_tterika_01
- [K] walls_decoration_tterika_01
- [ ] walls_detailing_tterika_01
- [ ] walls_detailing_tterika_02
- [ ] walls_exterior_detailing_tterika_01
- [ ] walls_exterior_detailing_tterika_02
- [ ] walls_interior_bathroom_detailing_tterika_01
- [ ] walls_interior_detailing_tterika_01
- [ ] walls_interior_detailing_tterika_02

## door  (15 sheets | 0 converted | 2 in Knox)
- [ ] fixtures_doors_frames_tterika_01
- [ ] fixtures_doors_frames_tterika_02
- [x] fixtures_doors_tterika_01  (converted -> 22_tikitown_doors.json, 33 openable doors)
- [x] fixtures_doors_tterika_02  (converted -> 22_tikitown_doors.json, 64 openable doors)
- [K] furniture_seating_indoor_tterika_01
- [K] furniture_seating_indoor_tterika_02
- [ ] furniture_seating_indoor_tterika_03
- [ ] furniture_seating_outdoor_tterika_01
- [ ] lighting_indoor_tterika_01
- [ ] lighting_indoor_tterika_01_on
- [ ] lighting_outdoor_tterika_01
- [ ] lighting_outdoor_tterika_01_on
- [ ] tikitown_doors_01
- [ ] tt_newburbs_doors_01
- [ ] vegetation_indoor_tterika_01

## fence/railing  (3 sheets | 0 converted | 0 in Knox)
- [ ] fixtures_railings_tterika_01
- [ ] tikitown_fencing_01
- [ ] tikitown_railings_01

## floor  (24 sheets | 0 converted | 3 in Knox)
- [ ] floors_exterior_detailing_tterika_01
- [K] floors_exterior_tilesandstone_tterika_01
- [K] floors_interior_carpet_tterika_01
- [K] floors_interior_tilesandwood_tterika_01
- [ ] floors_rugs_tterika_01
- [ ] floors_rugs_tterika_02
- [ ] floors_rugs_tterika_03
- [ ] overlay_grime_floor_tterika_01
- [ ] street_curbs_01_blend_road_tterika_01
- [ ] street_curbs_tterika_01
- [ ] street_decoration_tterika_01
- [ ] street_roadsigns_tterika_01
- [ ] street_trafficlines_tterika_01
- [ ] tikitown_brown_curbs_01
- [ ] tikitown_brown_curbs_02
- [ ] tikitown_brown_curbs_03
- [ ] tikitown_floor_leaves_01
- [ ] tikitown_rugs_01
- [ ] tikitown_street_roadsigns_01
- [ ] tikitown_streetcracks_01
- [ ] tikitown_trafficlines_01
- [ ] tt_flooring_raised_02_ddd_add
- [ ] tt_flooring_raised_03_ddd_add
- [ ] tt_flooring_raised_ddd_add

## furniture  (22 sheets | 0 converted | 6 in Knox)
- [K] furniture_bedding_tterika_01
- [ ] furniture_decoration_tterika_01
- [K] furniture_tables_high_tterika_01
- [K] industry_tterika_01
- [ ] overlay_furniture_tterika_01
- [K] tikitown_courthouse_02
- [K] tikitown_entertainment_01
- [ ] tikitown_firedept_01
- [K] tikitown_furniture_04
- [ ] tikitown_hospital_01
- [ ] tikitown_hospital_02
- [ ] tikitown_hospital_03
- [ ] tikitown_hospital_04
- [ ] tikitown_metalworks_01
- [ ] tikitown_museum_01
- [ ] tikitown_newspaper_01
- [X] tikitown_towncenter_01  (EXCLUDED: mixed tile types)
- [X] tikitown_towncenter_02  (EXCLUDED: mixed tile types)
- [X] tikitown_towncenter_04  (EXCLUDED: mixed tile types)
- [X] tikitown_towncenter_05  (EXCLUDED: mixed tile types)
- [ ] tikitown_trash_01
- [ ] trash_tterika_01

## opening(window/door)  (4 sheets | 0 converted | 1 in Knox)
- [K] location_sewer_tterika_01
- [ ] tikitown_walls_exterior_01
- [ ] walls_exterior_house_tterika_01
- [ ] walls_interior_house_tterika_01

## other  (21 sheets | 0 converted | 1 in Knox)
- [ ] preset_depthmaps_01  (no png)
- [ ] tikitown_coal_pile
- [ ] tikitown_coal_pile_02
- [ ] tikitown_industry_01
- [ ] tikitown_invisible
- [ ] tikitown_pillar_carolina
- [K] tikitown_power_plant_02
- [ ] tikitown_skal_factory_01
- [ ] tikitown_skal_factory_02
- [ ] tikitown_trim_01
- [ ] tikitown_trim_02_yellow
- [ ] tikitown_trim_03_orange
- [ ] tikitown_trim_04_gray
- [ ] tikitown_walls_exterior_cabin_01  (no png)
- [ ] tt_newburbs_trim_01_white
- [ ] tt_newburbs_trim_02_red
- [ ] tt_newburbs_trim_05_darkgreen
- [ ] tt_newburbs_trim_06_darkblue
- [ ] tt_newburbs_trim_08_black
- [ ] tt_newburbs_trim_add_01_brightred
- [ ] tt_newburbs_trim_add_01_orange

## roof  (20 sheets | 0 converted | 1 in Knox)
- [K] roofs_tterika_01
- [ ] tikitown_roofs_01
- [ ] tikitown_roofs_02
- [ ] tikitown_roofs_03
- [ ] tikitown_roofs_04
- [ ] tikitown_roofs_05
- [ ] tikitown_roofs_06
- [ ] tikitown_roofs_snow_01
- [ ] tt_newburbs_roofs_01a_lightgray
- [ ] tt_newburbs_roofs_01b_lightgray
- [ ] tt_newburbs_roofs_02a_warmgray
- [ ] tt_newburbs_roofs_02b_warmgray
- [ ] tt_newburbs_roofs_03a_redbrown
- [ ] tt_newburbs_roofs_03b_redbrown
- [ ] tt_newburbs_roofs_05a_slategreen
- [ ] tt_newburbs_roofs_05b_slategreen
- [ ] tt_newburbs_roofs_06a_slateblue
- [ ] tt_newburbs_roofs_06b_slateblue
- [ ] tt_newburbs_roofs_07a_black
- [ ] tt_newburbs_roofs_07b_black

## stairs  (1 sheets | 0 converted | 0 in Knox)
- [ ] fixtures_stairs_tterika_01

## vehicle/misc  (8 sheets | 0 converted | 1 in Knox)
- [ ] barges_empty
- [ ] barges_empty_south
- [ ] barges_metal
- [ ] barges_rocks
- [ ] barges_rocks_south
- [ ] barges_trash
- [ ] tikitown_railroad_01
- [K] tikitown_train_station_01

## wall  (110 sheets | 70 converted | 2 in Knox)
- [ ] fencing_tterika_01
- [ ] fixtures_doors_fences_tterika_01
- [K] industry_containers_tterika_01  (EXCLUDED from our conversion: will not add)
- [x] tikitown_commercial_walls_add_01
- [x] tikitown_commercial_walls_add_02
- [x] tikitown_commercial_walls_add_03
- [K] tikitown_courthouse_01
- [ ] tikitown_garage_01
- [ ] tikitown_newburbs_interiors_add_01
- [ ] tikitown_power_plant_01
- [ ] tikitown_railings_02
- [x] tikitown_tents_01
- [X] tikitown_towncenter_03  (EXCLUDED: mixed tile types)
- [x] tikitown_vanilla_walls_add_01
- [x] tikitown_vanilla_walls_add_02
- [x] tikitown_vanilla_walls_add_03
- [x] tikitown_vanilla_walls_add_04
- [x] tikitown_vanilla_walls_add_05
- [x] tikitown_vanilla_walls_add_06
- [x] tikitown_vanilla_walls_add_07
- [x] tikitown_vanilla_walls_add_08
- [x] tikitown_vanilla_walls_add_09
- [x] tikitown_vanilla_walls_add_10
- [x] tikitown_vanilla_walls_add_11
- [x] tikitown_vanilla_walls_add_12
- [x] tikitown_vanilla_walls_add_bathroom_01
- [x] tikitown_walls_bathroom_01
- [x] tikitown_walls_bathroom_02
- [x] tikitown_walls_bathroom_03
- [x] tikitown_walls_bathroom_04
- [x] tikitown_walls_brick_01
- [x] tikitown_walls_brick_02
- [x] tikitown_walls_brick_03
- [x] tikitown_walls_brick_04
- [x] tikitown_walls_brick_05
- [x] tikitown_walls_brick_06
- [x] tikitown_walls_brick_07
- [x] tikitown_walls_brick_08
- [x] tikitown_walls_brick_09
- [x] tikitown_walls_brick_10
- [x] tikitown_walls_brick_11
- [x] tikitown_walls_brick_12
- [ ] tikitown_walls_brick_burnt
- [x] tikitown_walls_brick_purewhite
- [x] tikitown_walls_brick_standard
- [x] tikitown_walls_bricks_dirtywhite
- [x] tikitown_walls_cement_01
- [x] tikitown_walls_commercial_01  (converted -> 26_tikitown_glass.json, color White; 6 glass windows w/ windowGlass callback + 1 half-height glass wall; broken/empty/corner/pole/center-fill sprites skipped as runtime damage states)
  > DEFECT FIX 1 (live test): the 6 glass WINDOW buildables were authored as kind:object/requiresFloor and placed INVISIBLE in-world (icon ok). Raw .tiles flags them WindowW/WindowN + wall. Converted all 30 (6 x 5 colors) to kind:wall + dontNeedFrame/providesWindowFrame in both 26_tikitown_glass.json and _accurate. Half-height (idx24) was already kind:wall.
  > DEFECT FIX 2 (live test): sprite INDICES were mismarked (parse-order idx != true atlas sprite number due to gap cells). FramelessPane 47->48, Frameless+Lower 55->56 (was showing a bare pillar), MultiPaneGrid 67->72. N=W+1. Verified by slicing the atlas into a labeled contact sheet (slice_glass_sheet.py). IDs kept at old suffix. See WALL_CONVERSION_STATUS.md.
- [x] tikitown_walls_commercial_02  (converted -> 26_tikitown_glass.json, color Black; re-implements some vanilla+)
- [x] tikitown_walls_commercial_03  (converted -> 26_tikitown_glass.json, color Red)
- [x] tikitown_walls_commercial_04  (converted -> 26_tikitown_glass.json, color Blue)
- [x] tikitown_walls_commercial_05  (converted -> 26_tikitown_glass.json, color Grey)
- [x] tikitown_walls_decorative_01
- [x] tikitown_walls_decorative_02
- [x] tikitown_walls_decorative_03
- [x] tikitown_walls_decorative_04
- [x] tikitown_walls_decorative_05
- [x] tikitown_walls_interior_01
- [x] tikitown_walls_metal_01
- [x] tikitown_walls_metal_02
- [x] tikitown_walls_plaster_01
- [x] tikitown_walls_plaster_02
- [x] tikitown_walls_siding_01
- [x] tikitown_walls_siding_02
- [x] tikitown_walls_siding_03
- [x] tikitown_walls_siding_04
- [x] tikitown_walls_stone_01
- [x] tikitown_walls_stone_02
- [ ] tikitown_walls_wall_burnt_01
- [x] tikitown_walls_wallpaper_01
- [x] tikitown_walls_wallpaper_02
- [x] tikitown_walls_wallpaper_03
- [x] tikitown_walls_wallpaper_04
- [x] tikitown_walls_wallpaper_05
- [x] tikitown_walls_wallpaper_06
- [x] tikitown_walls_wallpaper_07
- [x] tikitown_walls_wallpaper_08
- [x] tikitown_walls_wallpaper_09
- [x] tikitown_walls_wallpaper_10
- [x] tikitown_walls_wood_01
- [ ] tikitown_whatthefun_01
- [ ] tikitown_whistlin_dixie_01
- [x] tt_melos_tiles_overgrown_ruins_01
- [ ] tt_newburbs_doors_garages_01
- [x] tt_newburbs_interiors_01  (converted -> 27_tikitown_newburbs_interiors.json; 10-col sheet, 4 color blocks [Light Grey/Red/Tan/Dusty Rose], each block = Wall(W/N/NW-corner) + Window frame(W/N) + Door frame(W/N, vanilla door-frame flags). 12 buildables. NOTE: 01 has fewer padding cells than 02-04 (blocks at idx 0/30/53/76 vs 0/30/60/90) but identical buildable set.)
- [x] tt_newburbs_interiors_02  (converted -> 27_tikitown_newburbs_interiors.json; colors Slate Blue/Grey/Mint/Purple; blocks at idx 0/30/60/90)
- [x] tt_newburbs_interiors_03  (converted -> 27_tikitown_newburbs_interiors.json; colors Tan/Dark Grey/Brown Tan/Green)
- [x] tt_newburbs_interiors_04  (converted -> 27_tikitown_newburbs_interiors.json; colors Taupe/Light Grey/Olive/Grey)
- [x] tt_newburbs_walls_01_white  (converted -> 28_tikitown_newburbs_walls.json as FULL set Wall+Window+DoorFrame; MOVED out of 21_tikitown_walls.json where it was only a lone plain wall)
- [x] tt_newburbs_walls_04_warmgray  (converted -> 28_tikitown_newburbs_walls.json)
- [x] tt_newburbs_walls_05_red  (converted -> 28_tikitown_newburbs_walls.json)
- [x] tt_newburbs_walls_06_orange  (converted -> 28_tikitown_newburbs_walls.json)
- [x] tt_newburbs_walls_07_redbrown  (converted -> 28_tikitown_newburbs_walls.json)
- [x] tt_newburbs_walls_11_yellow  (converted -> 28_tikitown_newburbs_walls.json)
- [x] tt_newburbs_walls_14_blue  (converted -> 28_tikitown_newburbs_walls.json)
- [x] tt_newburbs_walls_16_pink  (converted -> 28_tikitown_newburbs_walls.json)
- [x] tt_newburbs_walls_17_coolgray  (converted -> 28_tikitown_newburbs_walls.json)
- [x] tt_newburbs_walls_18_black  (converted -> 28_tikitown_newburbs_walls.json)
> NOTE: 28_tikitown_newburbs_walls.json = 10 colors x 3 types (Wall/Window/DoorFrame) = 30 buildables, cheap wood recipe. All 10 sheets are single-color, identical layout (W0/N1/corner2, Window 4/5, DoorFrame 6/7), MaterialType Plaster.
- [ ] walls_commercial_tterika_01
- [ ] walls_commercial_tterika_02
- [ ] walls_commercial_tterika_03
- [ ] walls_commercial_tterika_04
- [ ] walls_commercial_tterika_05
- [ ] walls_commercial_tterika_07
- [ ] walls_commercial_tterika_08
- [x] walls_exterior_half_tterika_01
- [x] walls_exterior_house_tterika_02
- [ ] walls_exterior_roofs_tterika_02
- [x] walls_interior_bathroom_tterika_01
- [x] walls_interior_house_tterika_02

## window  (8 sheets | 0 converted | 2 in Knox)
- [K] fixtures_windows_curtains_tterika_01
- [K] fixtures_windows_curtains_tterika_02
- [ ] fixtures_windows_curtains_tterika_03
- [ ] fixtures_windows_frames_tterika_01
- [ ] fixtures_windows_tterika_01
- [ ] tikitown_newburbs_windows_01
- [ ] tikitown_windows_01
- [ ] tikitown_windows_02

## partial extracts (prop sheets - selected cells only)

These are MIXED prop sheets (not pure wall sheets) where only a few cells were extracted. The rest of each sheet is decorative props (left untouched).

- [X] tikitown-props-14  (REMOVED - was 29_tikitown_soundproof.json, DELETED)
  > REMOVED per user: soundproofing was buggy in-game both as wallCovering (build silently failed) AND as structural wall (build error + would not change orientation). Deliverable 29_tikitown_soundproof.json deleted and dropped from the test bundle. The props-14 soundproof set may be revisited later with a different model.
  > [superseded notes below]
- [~] tikitown-props-14  (was PARTIAL -> 29_tikitown_soundproof.json)
  - 8-column sheet (hyphenated name; sprite refs = `tikitown-props-14_<idx>`). Column count NOT from PNG width (1024px = atlas padding, same as 10-col newburbs); confirmed cols=8 from user observation that the wall set starts at (1,0) = idx8.
  - Extracted ONLY the soundproofing set (GroupName Proof Wall / Proof Window / Proof Door Frame), modeled as Knox **wallCovering** wall-attachments (overlays applied over existing walls, like WE Baseboard/Crown Molding panels) - NOT structural walls. Confirmed against WE 01_building_decor.json: coverings carry corners via `isCorner:true` + 4 face sprites, not `cornerSprite`/`pillarSprite`.
  - 3 buildables:
    - Soundproof Wall Covering: W=idx9(Facing E), N=idx8(Facing S), E=idx11, S=idx10 (all 4 facing sprites used; Option A), isCorner:true
    - Soundproof Window Covering: idx17 (single sprite, all faces)
    - Soundproof Door Frame Covering: W/E=idx19(Facing E), N/S=idx18(Facing S), isCorner:true
  - Cheap-tier wood recipe (hammer + 1 Plank + 2 Nails, Woodwork 4, BuildWallHammer, Carpentry). onCreate=WorldEssentialsKnoxNative.OnCreateWallAttachment; worldEssentialsNative.kind=wallAttachment; blockAllSquare:false, canPassThrough:true.
  - SKIPPED (props, not extracted): Professional Microphone, Blue/Teal Mixer Boards, Styrofoam Cups/Cup Stack, Coffee Dispenser-Thermos, Floor Bird Cage, Terrarium. idx24 (3,0) blank - user-confirmed NOT part of the wall set.
