# Community Tilepack — Inventory

Workshop `3628736763` (id `UnofficialMappersCommunityTilePack`).
Path: `C:\Program Files (x86)\Steam\steamapps\workshop\content\108600\3628736763\mods\CommunityTilePack`

A bundle of older/abandoned community tilepacks, organized under `Resources/<pack>/`.

## Addon-source status (geometry/recipe source for mapping)

To convert a pack's sheets into KBW buildables quickly we need an original Building Menu /
BuildingCraft addon for that pack (so we can lift geometry instead of authoring from scratch).

| Pack | Sheets | B41 Building-Menu addon (geometry source) | Orig B41 tile pack (ref only) | Status |
|---|---:|---|---|---|
| Blackwood | 7 | none | — | author-from-scratch only |
| Dirkies | 90 | Daddy Dirkie Addon (`3137091536`) | Diederiks Tile Palooza (`2337452747`) | **have** |
| Dylans Tiles | 40 | Dylan Tiles Addon (`3137091698`) | Dylan's tiles (`2599752664`) | **have** |
| Ekron | 2 | none | — | author-from-scratch only |
| Fears | 17 | none | — | author-from-scratch only |
| TK (ThrottleKitty's) | 18 | Throttlekitty's Addon (`3246568083`) | throttlekitty's tiles (`2384329562`) | **have** |
| Workshop | 14 | unknown | — | TBD |

All addons + orig packs are **B41** (geometry reference only; sprites come from the B42 Community
Tilepack — see note below).

Next: cross-reference every sheet below against TikiTown's `TILESHEET_INDEX.md` so we skip
anything already re-implemented into the TikiTown pack (avoid duplicating prior work). Priority
targets = packs WITH an addon source (Dirkies, Dylans, TK).

### IMPORTANT — everything upstream here is BUILD 41 (work required)

Both the original standalone tile sheets AND the Building Menu addons for these packs were made
for **B41**, the previous build. They are NOT drop-in for our B42 KBW work:

- **Sprites:** the original B41 sheets are out of date. The **Community Tilepack (B42)** is the
  current replacement for the actual tile art. Use Community Tilepack sheet names as the sprite
  source; do NOT reference the old B41 sheet names.
- **Addons:** the B41 Building Menu addons use the older BuildingMenu tile-def/recipe API, which
  does not map 1:1 to the KBW B42 JSON buildable schema. We treat them as a **geometry/recipe
  REFERENCE** (which sprites form each wall/window/door, their facings, piece grouping, material
  costs) and re-express that in our KBW B42 JSON schema — same lift pattern used for the TikiTown
  walls/roofs.
- **Net effect:** each conversion needs a B41→B42 sheet-name remap (old addon sprite name →
  Community Tilepack B42 sheet) PLUS re-authoring the buildable in the B42 schema. The addon saves
  us the geometry/recipe design work, not the implementation.

### CONVENTION — copy the recipe/cost straight from the addon

For each converted buildable, **use the addon's own build cost** (materials, tool, skill level,
time/xp where given). Do NOT invent a new recipe or reuse an unrelated KBW recipe. Translate the
addon's BuildingMenu recipe fields into the KBW JSON `requirements`/`construction` as closely as
the schema allows. (Sheet-name alignment is largely 1:1 already — see section (B) of
`B41_B42_MAP.md` — so the main work is schema re-expression + carrying the cost across verbatim.)



## Component packs (7)

| Pack | PNG sheets |
|---|---:|
| Blackwood | 7 |
| Dirkies | 90 |
| Dylans Tiles | 40 |
| Ekron | 2 |
| Fears | 17 |
| TK | 18 |
| Workshop | 14 |

### Blackwood (7 sheets)
- `blackwood1`
- `blackwood2`
- `blackwood3`
- `blackwood5`
- `blackwood6`
- `blackwood7`
- `blackwood8`

### Dirkies (90 sheets)
- `blends_natural_ddd_01`
- `blends_street_dirkerdam_ddd_01`
- `container_overlays_ddd_01`
- `d_doors_01`
- `d_doors_02`
- `d_furniture_bedroom_01`
- `d_furniture_bedroom_02`
- `d_furniture_bedroom_03`
- `d_furniture_bedroom_04`
- `d_furniture_bedroom_05`
- `d_furniture_couches_01`
- `d_furniture_kitchen_01`
- `d_location_arcadian_01`
- `d_location_sofaking`
- `d_rocks_ddd_01`
- `d_wall_decorations_01`
- `d_walls_interior_bathroom_01`
- `details_ddd_01`
- `details_ddd_02`
- `edit_ddd_RUS_Doors_house_01`
- `edit_ddd_RUS_Forest Survival_01`
- `edit_ddd_RUS_House_Furnace`
- `edit_ddd_RUS_Machine_01`
- `edit_ddd_RUS_Production_Furnace`
- `edit_ddd_RUS_RoaStop_01`
- `edit_ddd_RUS_Street_01`
- `edit_ddd_RUS_Street_LEP_01`
- `edit_ddd_RUS_Street_LEP_02`
- `edit_ddd_RUS_Walls_house`
- `edit_ddd_RUS_decor_house_01`
- `edit_ddd_RUS_fixtures_counters_03`
- `edit_ddd_RUS_fixtures_kitchenware_01`
- `edit_ddd_RUS_furniture_storage_03`
- `edit_ddd_RUS_industry_crane_01`
- `edit_ddd_RUS_location_business_machinery_02`
- `edit_ddd_RUS_power_station_01`
- `f_bridge_ddd_01`
- `f_bridge_tiles_ddd_01`
- `f_flooring_raised_03_ddd`
- `f_railroad_tracks_01_ddd`
- `fencing_ddd_01`
- `fencing_ddd_02`
- `fixtures_details_ddd_01`
- `fixtures_stairs_ddd_01`
- `fixtures_windows_curtains_ddd_01`
- `fixtures_windows_ddd_01`
- `fixtures_windows_ddd_02`
- `flooring_raised_02_ddd`
- `flooring_raised_ddd`
- `furniture_more_ddd_01`
- `furniture_seating_outdoor_ddd_01`
- `furniture_storage_ddd_01`
- `furniture_tables_high_ddd_01`
- `grime_ddd_01`
- `industry_ddd_01`
- `industry_ddd_02`
- `industry_ddd_03`
- `industry_dirkea_ddd_01`
- `industry_railroad_ddd_01`
- `industry_railroad_ddd_02`
- `junkyard_singles_ddd_tk_01`
- `junkyard_singles_ddd_tk_02`
- `junkyard_singles_ddd_tk_03`
- `location_business_office_ddd_01`
- `location_community_medical_ddd_01`
- `location_farm_accesories_spyjack_01`
- `location_shop_generic_ddd_01`
- `location_shop_generic_ddd_02`
- `misc_ddd_01`
- `more_walls_ddd_01`
- `more_walls_ddd_02`
- `ornamental_ddd_01`
- `railings_ddd_01`
- `ramps_ddd`
- `roofs_ddd_01`
- `roofs_ddd_02`
- `roofs_ddd_03`
- `roofs_ddd_04`
- `rus_industry_crane_ddd_01`
- `shanty_ddd_01`
- `signs_ddd_01`
- `walls_detailing_ddd_01`
- `walls_details_ddd_01`
- `walls_double_window_ddd_01`
- `walls_exterior_roofs_ddd_01`
- `walls_interior_house_ddd_01`
- `walls_long_window_ddd_01`
- `walls_tents_ddd_01`
- `walls_trim_ddd_01`
- `walls_trim_ddd_02`

### Dylans Tiles (40 sheets)
- `AuthenticZ_Store`
- `BlackCoffeeCo01`
- `Block_Trasher`
- `Bookies_Store`
- `DarthGunStore`
- `DylanPitstopExpItems`
- `DylanPitstopExpSigns`
- `DylansBar01`
- `DylansBigItems01`
- `DylansClutter01`
- `DylansDiorama01`
- `DylansElectronics01`
- `DylansFutureRoom01`
- `DylansGardenStuff01`
- `DylansGardenStuff02`
- `DylansJunkstacks01`
- `DylansJunkstacks02`
- `DylansMotorcycles01`
- `DylansMusicStore`
- `DylansOvergrown01`
- `DylansPolice01`
- `DylansRandomFurniture01`
- `DylansRandomFurniture02`
- `DylansRandomFurniture03`
- `DylansRandomFurniture04`
- `DylansRoofs01`
- `DylansToppledFurniture01`
- `DylansWallDeco01`
- `DylansWallPieces01`
- `DylansWalls01`
- `DylansWalls02`
- `Obs_01`
- `Obs_02`
- `Obs_03`
- `Obs_04`
- `PitStop1`
- `PitStop2`
- `PitStop3`
- `ZombieMapTiles`
- `aza_apartment_number_overlays`

### Ekron (2 sheets)
- `Ekron01`
- `Ekron02`

### Fears (17 sheets)
- `fears_bullet_holes`
- `fears_corpses`
- `fears_crouchable_foliage`
- `fears_dead_animals`
- `fears_fallen_trees`
- `fears_footprints`
- `fears_mass_grave`
- `fears_mass_grave_small`
- `fears_nemford`
- `fears_overlays`
- `fears_rat_tiles`
- `fears_road_blockades`
- `fears_rp_tiles`
- `fears_storage_tiles`
- `fears_tire_marks`
- `fears_workbenches`
- `roman_flag`

### TK (18 sheets)
- `city_deco_tk_01`
- `city_works_tk_01`
- `container_overlays_tk_01`
- `fixtures_counters_tk_01`
- `industry_tk_01`
- `industry_tk_02`
- `invisibles_tk_01`
- `junkyard_tk_01`
- `junkyard_tk_02`
- `kitchen_misc_tk_01`
- `lighting_outdoor_tk_01`
- `seating_outdoor_tk_01`
- `tk_porch_01`
- `trash_containers_tk_01`
- `walls_exterior_roofs_tk_01`
- `walls_exterior_roofs_tk_02`
- `walls_garage_tk_01`
- `yard_deco_tk_01`

### Workshop (14 sheets)
- `Screenshot_1`
- `Screenshot_10`
- `Screenshot_14`
- `Screenshot_15`
- `Screenshot_16`
- `Screenshot_2`
- `Screenshot_3`
- `Screenshot_4`
- `Screenshot_5`
- `Screenshot_6`
- `Screenshot_7`
- `Screenshot_8`
- `Screenshot_9`
- `Screenshot_Fears`

## .tiles definition files
- `common\media\Blackwood.tiles`
- `common\media\diederikv_tile_def.tiles`
- `common\media\dylanstiles.tiles`
- `common\media\ekron.tiles`
- `common\media\fearstiledefinitions01.tiles`
- `common\media\tkTiles_01.tiles`

## lua files in pack
- `common\media\lua\server\items\CTP_Definitions.lua`
- `common\media\lua\server\items\fearsworldfiller01.lua`
- `common\media\lua\server\items\worldfiller_ddd.lua`
- `common\media\lua\server\items\WorldFiller_dylan.lua`
- `common\media\lua\server\items\WorldFiller_ekron.lua`
- `common\media\lua\server\items\WorldFiller_tk.lua`
- `common\media\lua\shared\Definitions\ContainerButtonIconsCTP.lua`

## PNGs outside Resources/ (packed atlases etc.)
- `poster.png`
- `42\poster.png`
- `common\media\depthmaps\DEPTH_AuthenticZ_Store.png`
- `common\media\depthmaps\DEPTH_BlackCoffeeCo01.png`
- `common\media\depthmaps\DEPTH_Block_Trasher.png`
- `common\media\depthmaps\DEPTH_city_deco_tk_01.png`
- `common\media\depthmaps\DEPTH_city_works_tk_01.png`
- `common\media\depthmaps\DEPTH_container_overlays_ddd_01.png`
- `common\media\depthmaps\DEPTH_DarthGunStore.png`
- `common\media\depthmaps\DEPTH_details_ddd_01.png`
- `common\media\depthmaps\DEPTH_details_ddd_02.png`
- `common\media\depthmaps\DEPTH_DylanPitstopExpItems.png`
- `common\media\depthmaps\DEPTH_DylanPitstopExpSigns.png`
- `common\media\depthmaps\DEPTH_DylansBar01.png`
- `common\media\depthmaps\DEPTH_DylansBigItems01.png`
- `common\media\depthmaps\DEPTH_DylansClutter01.png`
- `common\media\depthmaps\DEPTH_DylansDiorama01.png`
- `common\media\depthmaps\DEPTH_DylansElectronics01.png`
- `common\media\depthmaps\DEPTH_DylansFutureRoom01.png`
- `common\media\depthmaps\DEPTH_DylansGardenStuff01.png`
- `common\media\depthmaps\DEPTH_DylansGardenStuff02.png`
- `common\media\depthmaps\DEPTH_DylansMusicStore.png`
- `common\media\depthmaps\DEPTH_DylansOvergrown01.png`
- `common\media\depthmaps\DEPTH_DylansPolice01.png`
- `common\media\depthmaps\DEPTH_DylansRandomFurniture01.png`
- `common\media\depthmaps\DEPTH_DylansRandomFurniture02.png`
- `common\media\depthmaps\DEPTH_d_doors_02.png`
- `common\media\depthmaps\DEPTH_d_furniture_bedroom_01.png`
- `common\media\depthmaps\DEPTH_d_furniture_bedroom_02.png`
- `common\media\depthmaps\DEPTH_d_furniture_bedroom_03.png`
- `common\media\depthmaps\DEPTH_d_furniture_bedroom_04.png`
- `common\media\depthmaps\DEPTH_d_furniture_bedroom_05.png`
- `common\media\depthmaps\DEPTH_d_furniture_couches_01.png`
- `common\media\depthmaps\DEPTH_d_furniture_kitchen_01.png`
- `common\media\depthmaps\DEPTH_d_location_arcadian_01.png`
- `common\media\depthmaps\DEPTH_d_location_sofaking.png`
- `common\media\depthmaps\DEPTH_d_rocks_ddd_01.png`
- `common\media\depthmaps\DEPTH_d_wall_decorations_01.png`
- `common\media\depthmaps\DEPTH_edit_ddd_RUS_decor_house_01.png`
- `common\media\depthmaps\DEPTH_edit_ddd_RUS_fixtures_counters_03.png`
- `common\media\depthmaps\DEPTH_edit_ddd_RUS_fixtures_kitchenware_01.png`
- `common\media\depthmaps\DEPTH_edit_ddd_RUS_Forest Survival_01.png`
- `common\media\depthmaps\DEPTH_edit_ddd_RUS_furniture_storage_03.png`
- `common\media\depthmaps\DEPTH_edit_ddd_RUS_House_Furnace.png`
- `common\media\depthmaps\DEPTH_edit_ddd_RUS_industry_crane_01.png`
- `common\media\depthmaps\DEPTH_edit_ddd_RUS_location_business_machinery_02.png`
- `common\media\depthmaps\DEPTH_edit_ddd_RUS_Machine_01.png`
- `common\media\depthmaps\DEPTH_edit_ddd_RUS_power_station_01.png`
- `common\media\depthmaps\DEPTH_edit_ddd_RUS_Production_Furnace.png`
- `common\media\depthmaps\DEPTH_edit_ddd_RUS_RoaStop_01.png`
- `common\media\depthmaps\DEPTH_edit_ddd_RUS_Street_01.png`
- `common\media\depthmaps\DEPTH_edit_ddd_RUS_Street_LEP_01.png`
- `common\media\depthmaps\DEPTH_Ekron01.png`
- `common\media\depthmaps\DEPTH_Ekron02.png`
- `common\media\depthmaps\DEPTH_fears_corpses.png`
- `common\media\depthmaps\DEPTH_fears_crouchable_foliage.png`
- `common\media\depthmaps\DEPTH_fears_dead_animals.png`
- `common\media\depthmaps\DEPTH_fears_fallen_trees.png`
- `common\media\depthmaps\DEPTH_fears_nemford.png`
- `common\media\depthmaps\DEPTH_fears_rat_tiles.png`
- `common\media\depthmaps\DEPTH_fears_road_blockades.png`
- `common\media\depthmaps\DEPTH_fears_rp_tiles.png`
- `common\media\depthmaps\DEPTH_fears_storage_tiles.png`
- `common\media\depthmaps\DEPTH_fears_workbenches.png`
- `common\media\depthmaps\DEPTH_fencing_ddd_01.png`
- `common\media\depthmaps\DEPTH_fencing_ddd_02.png`
- `common\media\depthmaps\DEPTH_fixtures_details_ddd_01.png`
- `common\media\depthmaps\DEPTH_fixtures_windows_curtains_ddd_01.png`
- `common\media\depthmaps\DEPTH_flooring_raised_02_ddd.png`
- `common\media\depthmaps\DEPTH_flooring_raised_ddd.png`
- `common\media\depthmaps\DEPTH_furniture_more_ddd_01.png`
- `common\media\depthmaps\DEPTH_furniture_seating_outdoor_ddd_01.png`
- `common\media\depthmaps\DEPTH_furniture_storage_ddd_01.png`
- `common\media\depthmaps\DEPTH_furniture_tables_high_ddd_01.png`
- `common\media\depthmaps\DEPTH_f_bridge_ddd_01.png`
- `common\media\depthmaps\DEPTH_f_bridge_tiles_ddd_01.png`
- `common\media\depthmaps\DEPTH_f_flooring_raised_03_ddd.png`
- `common\media\depthmaps\DEPTH_f_railroad_tracks_01_ddd.png`
- `common\media\depthmaps\DEPTH_industry_ddd_01.png`
- `common\media\depthmaps\DEPTH_industry_ddd_02.png`
- `common\media\depthmaps\DEPTH_industry_ddd_03.png`
- `common\media\depthmaps\DEPTH_industry_dirkea_ddd_01.png`
- `common\media\depthmaps\DEPTH_industry_railroad_ddd_01.png`
- `common\media\depthmaps\DEPTH_industry_railroad_ddd_02.png`
- `common\media\depthmaps\DEPTH_industry_tk_02.png`
- `common\media\depthmaps\DEPTH_junkyard_singles_ddd_tk_01.png`
- `common\media\depthmaps\DEPTH_junkyard_singles_ddd_tk_02.png`
- `common\media\depthmaps\DEPTH_junkyard_singles_ddd_tk_03.png`
- `common\media\depthmaps\DEPTH_location_business_office_ddd_01.png`
- `common\media\depthmaps\DEPTH_location_community_medical_ddd_01.png`
- `common\media\depthmaps\DEPTH_location_farm_accesories_spyjack_01.png`
- `common\media\depthmaps\DEPTH_location_shop_generic_ddd_01.png`
- `common\media\depthmaps\DEPTH_misc_ddd_01.png`
- `common\media\depthmaps\DEPTH_more_walls_ddd_02.png`
- `common\media\depthmaps\DEPTH_railings_ddd_01.png`
- `common\media\depthmaps\DEPTH_ramps_ddd.png`
- `common\media\depthmaps\DEPTH_roman_flag.png`
- `common\media\depthmaps\DEPTH_roofs_ddd_01.png`
- `common\media\depthmaps\DEPTH_roofs_ddd_03.png`
- `common\media\depthmaps\DEPTH_roofs_ddd_04.png`
- `common\media\depthmaps\DEPTH_rus_industry_crane_ddd_01.png`
- `common\media\depthmaps\DEPTH_signs_ddd_01.png`
- `common\media\depthmaps\DEPTH_trash_containers_tk_01.png`
- `common\media\depthmaps\DEPTH_walls_trim_ddd_02.png`
- `common\media\ui\Container_Bulletinboard.png`
- `common\media\ui\Container_ExoticPot.png`
- `common\media\ui\Container_extinguisher_box.png`
- `common\media\ui\Container_FoodPallet.png`
- `common\media\ui\Container_Rusty.png`
- `common\media\ui\Container_Safe.png`
- `common\media\ui\Container_SpoonRack.png`
- `common\media\ui\Container_StackedAmmoPallet.png`
- `common\media\ui\Container_StandingToolbox.png`
- `common\media\ui\Container_SuppliesPallet.png`
- `common\media\ui\Container_ToolPallet.png`
- `common\media\ui\Container_ToolTray.png`
- `common\media\ui\Container_WeaponPallet.png`
- `common\media\ui\Container_WireShelves.png`
