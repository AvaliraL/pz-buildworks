# World Essentials hand-off inventory

Generated 2026-11-06 by `pz_craft_loops/we_inventory.py`.
Compares our `work/` copy against the LIVE Steam World Essentials (Workshop 3733324672).

## 1. Has live WE changed since our baseline (`upstream/`)?

- **World Essentials - Community Buildworks**: 0 of 41 baseline files differ in live (baseline is current)
- **World Essentials - TikiTown Buildworks**: 0 of 20 baseline files differ in live (baseline is current)
- **World Essentials (base, our files only)**: 0 of 11 baseline files differ in live (baseline is current)

## 2. Our work vs LIVE

| Submod | New files | Changed files | Identical |
|---|---:|---:|---:|
| World Essentials - Community Buildworks | 15 | 23 | 17 |
| World Essentials - TikiTown Buildworks | 6 | 17 | 2 |
| World Essentials (base, our files only) | 0 | 0 | 11 |

### World Essentials - Community Buildworks

**Buildables: 209 new, 343 changed, 0 removed.**

New buildables, by definitions file:

- `60_community_dirkies_stairs.json` (new file): **7**
    - `community.dirkies.stairs`: 7
- `61_community_dirkies_bedroom.json` (new file): **60**
    - `community.dirkies.bedroom`: 60
- `62_community_dirkies_couches.json` (new file): **22**
    - `community.dirkies.couches`: 22
- `70_kbwcb_refrigeration_tiers.json` (new file): **59**
    - `kbwcb.appliances`: 59
- `35_community_dirkie_counters.json` (existing file): **31**
    - `community.dirkie.counters`: 31
- `40_community_dirkies_containers.json` (existing file): **19**
    - `community.dirkies.containers`: 19
- `41_community_dylan_containers.json` (existing file): **6**
    - `community.dylan.containers`: 6
- `42_community_tk_containers.json` (existing file): **1**
    - `community.tk.containers`: 1
- `57_community_tk_kitchen_misc.json` (existing file): **4**
    - `community.tk.kitchen_misc`: 4

Changed buildables (same id, different definition):

- `35_community_dirkie_counters.json`: **31** changed; what differs: tooltipKey x31, stage.allowSpriteReuse x31
    - e.g. `community.dirkie.counters.d_furniture_kitchen_01_10`
    - e.g. `community.dirkie.counters.d_furniture_kitchen_01_11`
    - e.g. `community.dirkie.counters.d_furniture_kitchen_01_18`
- `40_community_dirkies_containers.json`: **62** changed; what differs: tooltipKey x62, stage.allowSpriteReuse x19, displayName x16
    - e.g. `community.dirkies.containers.edit_ddd_RUS_furniture_storage_03_3`
    - e.g. `community.dirkies.containers.edit_ddd_RUS_furniture_storage_03_11`
    - e.g. `community.dirkies.containers.edit_ddd_RUS_furniture_storage_03_28`
- `41_community_dylan_containers.json`: **19** changed; what differs: tooltipKey x19, displayName x13, stage.allowSpriteReuse x6
    - e.g. `community.dylan.containers.DylansGardenStuff01_18`
    - e.g. `community.dylan.containers.DylansGardenStuff01_8`
    - e.g. `community.dylan.containers.DylansGardenStuff01_11`
- `42_community_tk_containers.json`: **11** changed; what differs: tooltipKey x11, stage.allowSpriteReuse x1, displayName x1
    - e.g. `community.tk.containers.fixtures_counters_tk_01_0`
    - e.g. `community.tk.containers.industry_tk_02_25`
    - e.g. `community.tk.containers.kitchen_misc_tk_01_12`
- `43_community_dirkies_walls.json`: **20** changed; what differs: tooltipKey x20, displayName x8
    - e.g. `community.dirkies.walls.industry_dirkea_ddd_01_8`
    - e.g. `community.dirkies.walls.industry_dirkea_ddd_01_16`
    - e.g. `community.dirkies.walls.industry_dirkea_ddd_01_10_corner`
- `44_community_dylan_walls.json`: **4** changed; what differs: tooltipKey x4, displayName x4
    - e.g. `community.dylan.walls.DylansGardenStuff02_8`
    - e.g. `community.dylan.walls.DylansGardenStuff02_10`
    - e.g. `community.dylan.walls.DylansGardenStuff02_11`
- `45_community_tk_walls.json`: **20** changed; what differs: tooltipKey x20, displayName x11
    - e.g. `community.tk.walls.industry_tk_01_0`
    - e.g. `community.tk.walls.industry_tk_01_8`
    - e.g. `community.tk.walls.industry_tk_01_2_corner`
- `46_community_dirkies_doors.json`: **56** changed; what differs: tooltipKey x56
    - e.g. `community.dirkies.doorframes.industry_dirkea_ddd_01_18`
    - e.g. `community.dirkies.doorframes.more_walls_ddd_01_86`
    - e.g. `community.dirkies.doorframes.more_walls_ddd_01_82`
- `48_community_tk_doors.json`: **4** changed; what differs: tooltipKey x4, displayName x4
    - e.g. `community.tk.doorframes.industry_tk_01_10`
    - e.g. `community.tk.doorframes.industry_tk_01_14`
    - e.g. `community.tk.doorframes.industry_tk_01_34`
- `49_community_tk_dumpsters.json`: **2** changed; what differs: tooltipKey x2
    - e.g. `community.tk.containers.dumpster_green`
    - e.g. `community.tk.containers.dumpster_brown`
- `50_community_dylan_futureroom.json`: **13** changed; what differs: tooltipKey x13
    - e.g. `community.dylan.futureroom.bed`
    - e.g. `community.dylan.futureroom.dresser`
    - e.g. `community.dylan.futureroom.ctable`
- `51_community_dylan_obs04_hedges.json`: **2** changed; what differs: tooltipKey x2
    - e.g. `community.dylan.obs04.hedge_straight`
    - e.g. `community.dylan.obs04.hedge_corner`
- `52_community_dylan_pitstop2_carpets.json`: **6** changed; what differs: tooltipKey x6
    - e.g. `community.dylan.pitstop2.carpet_pink`
    - e.g. `community.dylan.pitstop2.carpet_blue`
    - e.g. `community.dylan.pitstop2.carpet_black`
- `53_community_dylan_rf02_misc.json`: **4** changed; what differs: tooltipKey x4
    - e.g. `community.dylan.rf02.exercise_ball`
    - e.g. `community.dylan.rf02.punching_bag`
    - e.g. `community.dylan.rf02.tv_crt_small`
- `54_community_dylan_blocktrasher_shelf.json`: **1** changed; what differs: tooltipKey x1
    - e.g. `community.dylan.containers.blocktrasher_bookshelf`
- `55_community_dirkies_secret_shelf.json`: **2** changed; what differs: tooltipKey x2, displayName x1
    - e.g. `community.dirkies.secret_shelf.d_doors_02_64`
    - e.g. `community.dirkies.secret_shelf.d_doors_02_68`
- `56_community_fears_workbenches.json`: **9** changed; what differs: tooltipKey x9
    - e.g. `community.fears.workbench.tailoring`
    - e.g. `community.fears.workbench.metalworking`
    - e.g. `community.fears.workbench.electrical`
- `57_community_tk_kitchen_misc.json`: **6** changed; what differs: tooltipKey x6, stage.requirements x2, construction x2, group x1
    - e.g. `community.tk.kitchen_misc.deli_slicer`
    - e.g. `community.tk.kitchen_misc.wall_shelf`
    - e.g. `community.tk.kitchen_misc.ice_machine`
- `58_community_fears_rp.json`: **1** changed; what differs: tooltipKey x1
    - e.g. `community.fears.rp.raccoon_figure`
- `59_community_dirkies_fencing.json`: **70** changed; what differs: tooltipKey x70
    - e.g. `community.dirkies.fencing.picket`
    - e.g. `community.dirkies.fencing.picket_corner`
    - e.g. `community.dirkies.fencing.picket_post`

New non-definition files:

- `42/media/kbwcommunity_iceshell.tiles` (5548 bytes)
- `42/media/kbwcommunity_lcouch.tiles` (8454 bytes)
- `42/media/lua/client/KBWCommunity_StageInfo.lua` (5264 bytes)
- `42/media/lua/shared/KBWCommunity_MultiPart.lua` (8404 bytes)
- `42/media/lua/shared/KBWCommunity_Pickup.lua` (6453 bytes)
- `42/media/lua/shared/KBWCommunity_Rotation.lua` (32460 bytes)
- `42/media/lua/shared/KBWCommunity_StageProperties.lua` (4828 bytes)
- `42/media/texturepacks/KBWCommunityIceShell.pack` (796962 bytes)
- `42/media/texturepacks/KBWCommunityLCouch.pack` (370018 bytes)
- `common/media/depthmaps/DEPTH_KBWCommunityIceShell.png` (59717 bytes)
- `common/media/depthmaps/DEPTH_d_location_sofaking.png` (38456 bytes)

Changed non-definition files:

- `42/media/KnoxBuildworks/manifest.json` - 4 definition files added, 0 removed
- `42/media/lua/shared/Translate/EN/IG_UI.json` - 248 keys added, 58 changed
- `42/media/lua/shared/Translate/EN/Tooltip.json` - 50 keys added, 0 changed

### World Essentials - TikiTown Buildworks

**Buildables: 332 new, 2391 changed, 0 removed.**

New buildables, by definitions file:

- `35_tikitown_newburbs_trim.json` (new file): **250**
    - `tikitown.newburbs_trim`: 250
- `36_tikitown_tterika_storage.json` (new file): **24**
    - `worldessentials.tikitown.furniture_storage_tterika_02_0`: 2
    - `worldessentials.tikitown.furniture_storage_tterika_02_12`: 2
    - `worldessentials.tikitown.furniture_storage_tterika_02_16`: 2
    - `worldessentials.tikitown.furniture_storage_tterika_02_20`: 2
    - `worldessentials.tikitown.furniture_storage_tterika_02_24`: 2
    - `worldessentials.tikitown.furniture_storage_tterika_02_28`: 2
    - `worldessentials.tikitown.furniture_storage_tterika_02_32`: 2
    - `worldessentials.tikitown.furniture_storage_tterika_02_36`: 2
    - `worldessentials.tikitown.furniture_storage_tterika_02_4`: 2
    - `worldessentials.tikitown.furniture_storage_tterika_02_40`: 2
    - `worldessentials.tikitown.furniture_storage_tterika_02_44`: 2
    - `worldessentials.tikitown.furniture_storage_tterika_02_8`: 2
- `23_tikitown_furniture.json` (existing file): **58**
    - `worldessentials.tikitown.fixtures_counters_tterika_01`: 42
    - `worldessentials.tikitown.fixtures_counters_tterika_02`: 16

Changed buildables (same id, different definition):

- `21_tikitown_walls.json`: **919** changed; what differs: tooltipKey x919, displayName x7
    - e.g. `worldessentials.tikitown.tikitown_commercial_walls_add_01_0`
    - e.g. `worldessentials.tikitown.tikitown_commercial_walls_add_01_5`
    - e.g. `worldessentials.tikitown.tikitown_commercial_walls_add_01_7`
- `22_tikitown_doors.json`: **97** changed; what differs: tooltipKey x97
    - e.g. `worldessentials.tikitown.fixtures_doors_tterika_01_0`
    - e.g. `worldessentials.tikitown.fixtures_doors_tterika_01_4`
    - e.g. `worldessentials.tikitown.fixtures_doors_tterika_01_8`
- `23_tikitown_furniture.json`: **72** changed; what differs: tooltipKey x72, stage.allowSpriteReuse x58, displayName x21
    - e.g. `worldessentials.tikitown.fixtures_counters_tterika_01.brown_countertop_modern_corner`
    - e.g. `worldessentials.tikitown.fixtures_counters_tterika_01.brown_countertop_modern`
    - e.g. `worldessentials.tikitown.fixtures_counters_tterika_01.light_countertop_modern_corner`
- `24_tikitown_bookshelves.json`: **1** changed; what differs: tooltipKey x1
    - e.g. `worldessentials.tikitown.tikitown_furniture_03_41`
- `25_tikitown_bedroom.json`: **58** changed; what differs: tooltipKey x58
    - e.g. `worldessentials.tikitown.tikitown_furniture_bedroom_01_1`
    - e.g. `worldessentials.tikitown.tikitown_furniture_bedroom_01_17`
    - e.g. `worldessentials.tikitown.tikitown_furniture_bedroom_01_24`
- `26_tikitown_glass.json`: **110** changed; what differs: tooltipKey x110
    - e.g. `tikitown.glass.tikitown_walls_commercial_01_0`
    - e.g. `tikitown.glass.tikitown_walls_commercial_01_16`
    - e.g. `tikitown.glass.tikitown_walls_commercial_01_32`
- `27_tikitown_newburbs_interiors.json`: **240** changed; what differs: tooltipKey x240
    - e.g. `tikitown.newburbs.tt_newburbs_interiors_01_c1_wall`
    - e.g. `tikitown.newburbs.tt_newburbs_interiors_01_c1_window`
    - e.g. `tikitown.newburbs.tt_newburbs_interiors_01_c1_doorframe`
- `28_tikitown_newburbs_walls.json`: **460** changed; what differs: tooltipKey x460, displayName x40
    - e.g. `tikitown.newburbs_walls.tt_newburbs_walls_01_white_wall`
    - e.g. `tikitown.newburbs_walls.tt_newburbs_walls_01_white_window`
    - e.g. `tikitown.newburbs_walls.tt_newburbs_walls_01_white_doorframe`
- `29_tikitown_garages.json`: **40** changed; what differs: translationKey x40, tooltipKey x40
    - e.g. `tikitown.garages.tt_newburbs_doors_garages_01_white_w2`
    - e.g. `tikitown.garages.tt_newburbs_doors_garages_01_white_w3`
    - e.g. `tikitown.garages.tt_newburbs_doors_garages_01_white_w4`
- `30_tikitown_shelving.json`: **4** changed; what differs: tooltipKey x4
    - e.g. `worldessentials.tikitown.furniture_shelving_tterika_01_0`
    - e.g. `worldessentials.tikitown.furniture_shelving_tterika_01_4`
    - e.g. `worldessentials.tikitown.furniture_shelving_tterika_01_8`
- `31_tikitown_newburbs_roofs.json`: **348** changed; what differs: tooltipKey x348
    - e.g. `tikitown.newburbs_roofs.tt_newburbs_roofs_01a_lightgray_slope_1`
    - e.g. `tikitown.newburbs_roofs.tt_newburbs_roofs_01a_lightgray_slope_2`
    - e.g. `tikitown.newburbs_roofs.tt_newburbs_roofs_01a_lightgray_slope_3`
- `32_tikitown_newburbs_flags.json`: **8** changed; what differs: tooltipKey x8
    - e.g. `tikitown.newburbs_flags.tt_newburbs_details_01_16`
    - e.g. `tikitown.newburbs_flags.tt_newburbs_details_01_20`
    - e.g. `tikitown.newburbs_flags.tt_newburbs_details_01_24`
- `33_tikitown_newburbs_doors.json`: **21** changed; what differs: tooltipKey x21, displayName x1
    - e.g. `tikitown.newburbs_doors.tt_newburbs_doors_01_0`
    - e.g. `tikitown.newburbs_doors.tt_newburbs_doors_01_4`
    - e.g. `tikitown.newburbs_doors.tt_newburbs_doors_01_8`
- `34_tikitown_newburbs_windows.json`: **13** changed; what differs: tooltipKey x13
    - e.g. `tikitown.newburbs_windows.tikitown_newburbs_windows_01_0`
    - e.g. `tikitown.newburbs_windows.tikitown_newburbs_windows_01_8`
    - e.g. `tikitown.newburbs_windows.tikitown_newburbs_windows_01_16`

New non-definition files:

- `42/media/lua/client/KBWTikiTown_StageInfo.lua` (5264 bytes)
- `42/media/lua/shared/KBWTikiTown_MultiPart.lua` (8404 bytes)
- `42/media/lua/shared/KBWTikiTown_Pickup.lua` (6453 bytes)
- `42/media/lua/shared/KBWTikiTown_Rotation.lua` (8124 bytes)

Changed non-definition files:

- `42/media/KnoxBuildworks/manifest.json` - 2 definition files added, 0 removed
- `42/media/lua/shared/Translate/EN/IG_UI.json` - 372 keys added, 69 changed
- `42/media/lua/shared/Translate/EN/Tooltip.json` - 81 keys added, 0 changed

### World Essentials (base, our files only)

**Buildables: 0 new, 0 changed, 0 removed.**

## 3. Notes for the WE dev

Everything below is the full delta from the LIVE World Essentials (identical to our `we-baseline-2026-11-01`)
to our tip. It spans four earlier commits' worth of work (names/tooltips, ice machines, RC1) plus the latest
sheet work. Counts in sections 1-2 are generated; this section is hand-written from the git history.

**mod.info lines WE needs (mod.info is WE-owned, we do not touch it)**

Community submod, two new pack/tiledef pairs:

    pack=KBWCommunityIceShell
    tiledef=kbwcommunity_iceshell 8181
    pack=KBWCommunityLCouch
    tiledef=kbwcommunity_lcouch 8178

**1. Names + tooltips pass (Community + TikiTown; definitions and EN translations only)**

- 127 name fixes (raw sheet names, doubled words, duplicates split by art; `industry_tk_02_25` is a Fire Extinguisher Cabinet).
- Unique translationKey per width for the TikiTown garage doors (all showed "(2 Wide)"); 40 keys split.
- One-line type tooltip on every piece (`tooltipKey`). This is why nearly every existing buildable shows as "changed".
- KBW-owned tooltip keys are never shipped (includes the 2026-11-01 tooltip fix). WE's `WECommunity_*` Dylan isolation untouched.

**2. Ice machines and deep fryer (`57_community_tk_kitchen_misc.json`)**

- Commercial Ice Machine and Deep Fryer now cost the same as KBW's matching appliance (chest freezer / green oven recipe,
  magazine-gated like KBW's own).
- Ice machine tiers: Commercial (30), Large (65) and Industrial (100), grouped with the base machine; capacity set via the
  stage `container` capacity.
- 65 and 100 are built in two steps (inert shell, then the finished unit built ON the shell via `previousStage`) so each build
  stays under ~75 carry weight. New asset: `KBWCommunityIceShell` pack + tiledef 8181.
- Confirmed in game (two-stage build and tiers).

**3. RC1: fridge/freezer tiers, reinforced storage, pick-up / rotation fixes**

- 59 tiered 1-tile fridges/freezers (`70_kbwcb_refrigeration_tiers.json`, Appliances > Refrigeration); shell sheet extended
  to 44 tiles + depth map; "Build first" shell names. KBW part amounts (insulation foam, plastic sheet, rubber seal,
  refrigerant, copper pipe) are halved, rounded down, min 1, for fridges and ice machines.
- Reinforced counters/cabinets/crates (files 35/40/41/42) at military-crate capacity; TikiTown: 58 reinforced counters.
- New Lua: `KBWCommunity_StageProperties` (container capacity per type, freezer retype), `KBWCommunity_StageInfo`
  (build-menu capacities, picked-up tooltip), `KBWCommunity_Pickup` (pick up / place keeps storage and name),
  `KBWCommunity_Rotation` (moveable face offsets for badly grouped pack tiles). TikiTown gets its own copies
  (`KBWTikiTown_*`), all install-guarded so both can load together.
- Confirmed in game, single player, test bundle. Multiplayer not tested.

**4. New Dirkies / TikiTown sheets**

- Community: stairs (7, pillars removed), bedroom (60: floor beds, large beds, wardrobe, dressers, nightstand, bookcases),
  couches (22: 9 couches, 9 armchairs, 4 L-shaped couches in teal/purple/pink/orange).
- TikiTown: Newburbs trim (250), tterika_02 storage (12 lockers/chests + 12 reinforced; footlocker stacks 6, small cabinets 2),
  tterika counter and shelving additions in file 23.
- L couches use `KBWCommunityLCouch`: single-tile copies of the Comfy end pieces WITHOUT their 2-tile sprite grid (orange is
  a recolour of pink). With the originals the ends ghost as the full 2-tile couch and cannot be picked up.
- `common/media/depthmaps/DEPTH_d_location_sofaking.png`: sofaking depth map with the teal and orange corner cells cleared
  (only those colours carried depth data; purple and pink had none and looked right). Fixes the odd teal look, confirmed in game.

**5. Multi-part pick-up / sledgehammer (new this hand-off)**

- `KBWCommunity_MultiPart.lua` / `KBWTikiTown_MultiPart.lua`: KBW places each tile of a multi-tile build as its own object
  (`modData.KBW.groupId`/`partCount`). Vanilla only moves tiles together when sprites share a tile-property sprite grid, so
  picking up or smashing one tile of a bed left the rest. This wraps `ISMoveableSpriteProps:canPickUpMoveable/pickUpMoveable`
  and `ISDestroyStuffAction:complete` so all tiles of the group go together; part items drop on the floor with the generic
  `Moveables.Moveable` look (as vanilla multi-sprite pick-up does).

**Untouched WE-owned files**: `mod.info`, `bundled_source.txt`, `KBWCommunity_Seating.lua`, and the runtime Lua WE moved into
main World Essentials (Destroyable, MultiStorey, TableTop, TVScreens, Viewscreens).

**Test status**

- Confirmed in game: stairs, bedroom, couches and all four L couches, tterika storage, reinforced counters, fridge tiers,
  two-stage ice machines and tiers, workbench pick-up, RC1 Lua (single player).
- Also confirmed in game: multi-part pick-up / sledgehammer on multi-tile builds, generic box look for dropped parts,
  tterika stacking, the teal depth-map fix, names/tooltips pass.
- Not tested: multiplayer.

