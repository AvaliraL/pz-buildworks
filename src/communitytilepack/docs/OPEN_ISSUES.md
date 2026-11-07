# Community Tilepack — Open Issues (carry to next session)

Last verified: 2026-10-28, from console.txt (13:52 session) + on-disk build of TikiTownCommunityTest.

## Test setup facts
- The mod actually enabled/loaded is **TikiTownCommunityTest** (loads from
  `C:\Users\josep\Zomboid\Workshop\TikiTownCommunityTest`). KnoxCommunityTilepack is NOT enabled.
  The stale subscribed Steam copy (3828080624) was not the cause for this setup.
- The tile patch `media/kbwcommunity_tvpatch.patch.tiles` (tiledef 8185) is on disk, correct, and
  loads with no tiledef errors.
- WorldEssentialsKnoxBuildworksExpansion is also loaded (1145 duplicate TikiTown buildable-id errors).

## Status by item
| Item | Status | Cause / note |
|---|---|---|
| TV works as a TV (TV UI) | WORKING | Patch ADDED signal/IsoType/CustomItem — adds take effect. |
| TV screen image when on | BROKEN | `TV` flag is in the patch but no screen renders. Unverified guess: vanilla TVs also carry `Facing`; IsoTelevision may need it to place the screen. |
| Walk through TVs | BROKEN | Patch merging is ADDITIVE: it can add properties but cannot remove the pack's `solidtrans`. |
| Exercise ball / punching bag walk-through | BROKEN | Same: `solidtrans` removal doesn't take. |
| Hedges | BROKEN (confirmed in-game: still solid) | `solid` removal didn't take (additive merge). |
| Secret bookshelves have no inventory | BROKEN (cause unknown) | Built JSON still has `container {shelves, 20}`. Suspect shelves built during the broken-tiledef (v1, id 6991) session lost their container; a freshly built one may work. Unverified. |
| Viewscreens can't be clicked | EXPECTED | Never made interactive — the frosted/planet toggle is a planned feature, not built. |

## Findings (2026-10-28, from the game jar)
- `.patch.tiles` merges are additive. Removal is done at runtime with
  `PropertyContainer.unset(String|IsoFlagType)` (the engine does this itself for tree tiles in IsoWorld).
- Exact B42 PropertyContainer API (read from the .class): `set`, `unset`, `has`, `get`,
  `CreateKeySet`, `Clear`, `AddProperties`. The earlier failed Lua used B41 names `Set/UnSet/Is/Val`.
- `OnLoadedTileDefinitions` IS fired by the engine (seen in console), though no Lua uses it.
- BUILT + DEPLOYED (2026-10-28, not yet tested in-game): kbw_tilepatch.write_removal_lua() generates
  `media/lua/shared/KBWCommunity_TileFixes.lua` (15 sprite removals) in both the test bundle and the
  subscribed community copy. Logs `[KBWCommunityTileFixes] <event>: removed=N missingSprites=N failed=N`.
- TV screen: IsoTelevision picks the screen via setupDefaultScreens/isFacing; pack TVs had no Facing.
  Patch now adds Facing=E (36/38, west-wall face) and Facing=S (37/39, north-wall face), following
  the wall-lamp convention (attachedW->Facing=E). If the screen draws on the wrong side, swap them.

## In-game results 2026-10-28 (after TileFixes.lua)
- Console: `OnLoadedTileDefinitions: removed=15 failed=0`, then `OnGameStart: removed=0` (already gone) -> removal works.
- FIXED: secret bookshelves (inventory), punching bag, exercise ball (walk-through).
- TV screen: ROOT CAUSE FOUND (bytecode of IsoTelevision.setupDefaultScreens): screen sprites =
  same sheet at sprite index +16, +32, +48. Pack TVs are idx 36-39 in a 48-tile sheet -> no screen
  art exists. Pack has NO TV screen art anywhere. Options: A dark screen / B inject vanilla
  appliances_television_01 screen sprites via tv:addTvScreenSprite on load (likely misaligned) /
  C author matching overlay art + texture pack. Awaiting user choice (recommended: test B).
- TV still SOLID: separate cause, on KBW nativeObject (IsoTelevision) build path. Not yet found.
- Hedges: walk-through but no hedge behaviour. Vanilla tall hedge = vegetation_ornamental_01
  (Bush, CanBreak, MoveType=Vegitation, Movement=HedgeHigh, vegitation, MaterialType=Grass).
  Slow/rustle is IsoGameCharacter via IsoGridSquare.hasBush/isBush -> KBW build path may matter too.

- TV screen option B BUILT (not yet tested): `KBWCommunity_TVScreens.lua` gives each pack TV
  vanilla's 3 screen sprites (36/38 <- appliances_television_01_16/32/48; 37/39 <- _17/33/49) via
  clearTvScreenSprites + addTvScreenSprite, on LoadGridsquare / OnTileObjectAdded / OnObjectAdded.
  Logs `[KBWCommunityTVScreens] <event>: <sprite> got N screens`. Shows/tapes = vanilla logic.
  Accept small offset; if large, do option C (generated overlay art + texture pack).

## Next steps
1. Find how a removal is done: inspect mods that "fix" tiles (e.g. TileFixes tiledef 3373/3374,
   kwrr_fixes_tiles 2630) — does a non-`.patch` tiledef REPLACE properties, or is there an unset token?
2. Test the TV screen with `Facing` added per sprite (36/38 = one facing, 37/39 = the other).
3. Build a FRESH secret bookshelf and check inventory before changing anything.
4. TikiTown bookshelf books (overlay): try KBW isProp/moveable path on In-Wall shelf
   (tikitown_furniture_03_41); fallback = ship our own entity script modelled on Base.Wood_Bookcase_Lvl2.

## Wall TVs (DylansRandomFurniture02_36-39) - 2026-08-28 fix, awaiting in-game test
- Solid: root cause was KBW NativeObjectFactory `setMovedThumpable(true)`; `IsoGridSquare.getSpecialSolid()` treats any movedThumpable object as solid. `KBWCommunity_TVScreens.lua` now calls `setMovedThumpable(false)` + `RecalcAllWithNeighbours(true)`.
- Orientation: Facing was backwards. Art measured: 36/38 = Facing S, 37/39 = Facing E.
- Height/size: vanilla screen art sits at table height (~y131-185). Generated screen tiles (tileset `KBWCommunityTVScreens`, tiledef `kbwcommunity_tvscreens 8186`, `pack=KBWCommunityTVScreens`) affine-warp vanilla screens 16/32/48 and 17/33/49 onto each TV's measured screen. Generator: `kbw_tilepatch.write_tv_screen_assets`.
- Known edge: a TV that was ON when saved can show the old screen until toggled once.

## TODO: balance passes (specifics to be decided with user)
- [ ] **Cost pass.** Use the KBW military crate as the baseline: its build cost per unit of
  storage becomes the standard. Re-cost Community/TikiTown containers to scale from it.
  (User believes the crate holds 100; check the actual capacity and recipe in KBW first.)
- [ ] **Storage capacity pass.** Align container capacities to the same baseline.
- [ ] **Tooltip text pass: wrong name / "counter" on containers (ALL tiles, both mods). HIGH PRIORITY.**
  Seen in game 2026-08-28: the military crate cases' tooltip shows another piece's name and calls
  it a counter. Root cause FOUND (builder bug, not tile data):
  - `build_community_mod.py` fills each SHARED tooltip key with the displayName of the FIRST
    buildable that uses it (`if tt and tt not in tooltip: tooltip[tt]=displayName`). So
    `Tooltip_KBW_Shared_StorageFixture` = "White Counter, Charcoal Top (Corner)" for all 140
    Community containers. The same applies to Wall (44), Door (60), DecorativeWallFixture (9),
    Vegetation, Floor, Decoration and Television.
  - TikiTownKBW ships the same problem from the copied test-bundle tables:
    `Tooltip_KBW_Shared_StorageFixture` = "Counter - Brown Countertop Modern Corner."
  - **Worse: two of those are KBW CORE keys.** KBW's own Tooltip.json defines
    `Tooltip_KBW_Shared_StorageFixture` ("Storage fixture for organizing supplies.") and
    `Tooltip_KBW_DecorativeWallFixture` ("Decorative wall fixture. Does not store items.").
    Our mods overwrite them, so KBW / Vanilla Expanded / WE pieces using those keys also show our
    counter name whenever our mods are loaded.
  - Fix plan: never write KBW-owned keys (use KBW's text); give our shared keys proper generic
    text (or per-piece tooltip keys); then a full pass over every buildable's name + tooltip in
    Community and TikiTown, compared in game.
  - 78 Community buildables have no tooltipKey at all; include them in the pass.
  - **2026-11-01 PART FIXED** (bug pass items 1+2): `pz_craft_loops/tooltip_fix.py`, called by all
    3 builders. KBW-owned keys are no longer shipped (list read from KBW's Translate files), and our
    6 shared keys have generic text. Sent to WE as `WE_handoff_zips/WE_Buildworks_TooltipFix_20261101.zip`.
    Still open: the full per-piece name/tooltip pass above.
  - `we_sync.py` now treats `KBWCommunity_Seating.lua` as WE-owned (the WE dev hardened it in place:
    registration guard, reads before removing) and skips JSON files whose data is unchanged.
    Our `kbw_tilepatch.py` still generates the older Seating version; port WE's if we change it.
- [ ] **Shown capacity must match actual capacity (all storage containers).** Seen in game
  2026-08-28: the Green/White Military Crate Case (`furniture_storage_ddd_01_4.crate` / `_9.crate`,
  definition `container.capacity` 100) still shows **30** in the tooltip. 30 is the pack tile's
  `ContainerCapacity` (tiles 4/9, and our mirrored copies `KBWCommunityCasesMirror_0/1` copy it).
  Unverified guess: the tooltip reads the tile property, while KBW's `Properties.lua` only calls
  `setCapacity` on the built object. To check:
  - what the build-menu tooltip actually reads;
  - what a built crate's container really holds (100 vs 30); **ANSWERED 2026-11-02: holds 100**
    (user, in game). KBW Properties.lua `container` handler calls
    `part:getContainer():setCapacity(stage.container.capacity)` on the built object, so the
    definition sets the real capacity; the tile's ContainerCapacity only feeds the tooltip.
  - whether the plain cases show 30 but have 25.
  Likely fixes: set `ContainerCapacity` in the tile patch to match the definition, or point
  the same-sprite variants at a capacity both agree on. Then audit every container buildable,
  shown vs actual (Community + TikiTown).
- [ ] **Higher-capacity storage tiers.** The military crate stacks 3 high. Add larger containers
  that take the full 3-high footprint, with the combined capacity and cost of 3 crates
  (e.g. ~300 capacity at 3x crate cost). Decide which tiles/models, exact numbers, and whether
  2-high tiers are wanted.

### 2026-08-28 follow-up
- In game: TVs that were already placed now work (screens + walk-through). Newly built TVs had no screen and were still solid, because no add-event fires for KBW builds (only LoadGridsquare ever logged).
- Fix (awaiting test): wrap KBW `NativeObjectFactory.finalize` in memory on OnGameStart/OnServerStarted (state.type=="television") and add an every-in-game-minute scan within 12 tiles of each local player (for MP clients). Logs `hooked KBW NativeObjectFactory.finalize` and `KBWFinalize:` / `NearbyScan:` lines.
- Secret bookshelves: old builds lacked storage; new builds are fine. Resolved.

### 2026-08-28: build under wall TV + sledgehammer (awaiting test)
- Build under TV: KBW `Placement.lua:709` checks the SQUARE's merged properties for BlocksPlacement; the TV tile carried it, so TV-then-counter failed (counter-then-TV worked because high wall objects are exempt). Now unset at runtime with solid/solidtrans. Note: this allows anything below, including tall items; no 2-slot height cap is enforced.
- Sledgehammer: vanilla `ISDestroyCursor:canDestroy` refuses sprites named `d_*`/`e_*`/`f_*` and vegitation tiles (all 61 Dirkies `d_` buildables affected). New `media/lua/client/KBWCommunity_Destroyable.lua` wraps canDestroy for objects whose KBW buildableId starts `community.` / `tikitown.` / `worldessentials.tikitown.`, keeping vanilla's other safety checks. Log: `[KBWCommunityDestroy] sledgehammer support installed`.

### 2026-08-28: north-wall viewscreens (awaiting test)
- The pack only has west-wall Future Room viewscreens (DylansFutureRoom01_24-29, 32-34; tiles carry no properties). `kbw_tilepatch.write_viewscreen_assets` mirrors each one horizontally into tileset `KBWCommunityViewscreensN_0..8` (`pack=KBWCommunityViewscreens`, `tiledef=kbwcommunity_viewscreens 8187`). `add_viewscreen_north_faces` adds the `N` face to all 9 buildables at build time; the source deliverable is unchanged.
- Mirroring also flips the artwork (the planet horizon slopes the other way).

### 2026-08-28: viewscreen corners + Dylan status
- Corner placement: KBW's generic against-wall check (`Placement.lua` ~553-566) rejects a square holding any other non-floor IsoThumpable, and a corner square holds two built walls. Viewscreens now carry `MoveType=WallObject` + `Facing` (west tiles via the tile patch: Facing=E; generated north tiles in their own tiledef: Facing=S), so KBW uses `hasAttachedWallSupport`, which allows different faces of a corner and still blocks two screens on the same face. Awaiting in-game test.
- All Dylan sheets (41, 44, 47, 50-54) moved to Completed in the test bundle (user confirmed). Dylan In Progress is now empty.
- Furniture audit kept in `pz_craft_loops/_furn_audit.py` (+ `_furn_audit.txt`): only Future Room tiles lack tile properties; most beds (tikitown_furniture_bedroom_01-04, tterika bunks, Sci-Fi bed) and the Sofaking couches have no seating.txt data. Awaiting the user's answer on scope.

### 2026-08-28: viewscreen image cycle (awaiting test)
- `media/lua/shared/KBWCommunity_Viewscreens.lua` (generator `kbw_tilepatch.write_viewscreen_lua`): right-click option cycles frosted -> Earth -> Mars -> frosted. Rings keep framing: 32->24->27, 33->25->28, 34->26->29, with the same rings on the generated north tiles. A timed action (`KBWCycleViewscreenAction`, modelled on vanilla ISWallpaperAction) does setSpriteFromName + transmitUpdatedSpriteToClients. No light source.
- The 9 viewscreen buildables are unchanged; any one of them can be cycled after placing.

### 2026-08-28: tterika double bed Rest / facing (awaiting test)
- Cause: Drazion's `seating.txt` has placeholder data for `furniture_bedding_tterika_01_16-23`: one `S` position at `0 0 0`, with no BlockLeft/Right. You sit inside the bed facing south in every orientation. The single beds (32-39) have proper data and work.
- Seating merge is FIRST-WINS per tile (`SeatingFile$Tileset.merge` skips tiles that already have positions), so a seating.txt of ours can't override it.
- Fix: `media/lua/shared/KBWCommunity_Seating.lua` (generator `kbw_tilepatch.write_seating_lua`, table `_SEATING_FIXES`). On OnGameStart/OnServerStarted it edits mod `tikitown_tiles`' in-memory seating data the way vanilla TileGeometryEditor does: remove positions, add the vanilla positions with the same IDs, copy translate via `getTilePositionTranslate():set(...)`, copy BlockLeft/Right, then `mergeAfterEditing()`. Source is vanilla `furniture_bedding_01_16-23` ("Large Modern", same Facing and SpriteGridPos per tile). Nothing is written to disk. Log: `[KBWCommunitySeating] OnGameStart: fixed=8 failed=0`.
- Shipped in TikiTownCommunityTest and the standalone TikiTown mod. The same table can carry fixes for other beds (Fancy floor beds, bunks, Sci-Fi bed, Sofaking couches) once their vanilla equivalents are picked. Those have NO seating data at all, so they need a target mod that has seating data.

### 2026-08-28: tterika double bed, N/W orientations
- My first fix covered only tiles 16-23, which KBW uses for the E and S faces (these work in game). The N face uses 24-27 and the W face uses 28-31, and those still had Drazion's placeholder data. `_SEATING_FIXES` now covers 16-31; they map tile for tile to vanilla `furniture_bedding_01_16-31`. Awaiting test: the log should say `fixed=16`.

### 2026-08-28: Fears workbenches (sheet 56, In Progress; user confirmed all working in game)
- Source: Community pack `fears_workbenches`. Benches (S pair / E pair): Tailoring 0,1 / 9,8; Metalworking 2,3 / 11,10 (pack); Electrical 4,5, Carpentry 6,7, Chemistry 20,21, Gunsmithing 22,23 (E generated). Singles: Wood Gas Stove 16, Anvil 17, Air Compressor 18.
- Generated tileset `KBWCommunityFearsMirror_0..9` (`pack=KBWCommunityFears`, `tiledef=kbwcommunity_fears 8184`). Each tile is a horizontal mirror of its source and copies the source's properties with Facing and SpriteGridPos swapped (E grid 0,0 = mirror of S grid 0,0; E grid 0,1 = mirror of S grid 1,0). The anvil and compressor also get a mirrored second orientation.
- Depth: B42 loads depth maps and tileGeometry ONLY from `<mod>/common/media`, and loads depth maps only if that mod also has a `tileGeometry.txt`. The builders now emit `common/media/depthmaps/DEPTH_KBWCommunityFearsMirror.png` (mirrored cells of the pack's depth map) and a shape-less `tileGeometry.txt`. The community builder syncs and wraps `common/` too.
- Definitions are generated by `pz_craft_loops/make_fears_workbenches.py` into `deliverables/56_community_fears_workbenches.json`. Category Furniture and Appliances / Workbenches. KBW faces: "N" = S-facing row, "W" = E-facing column.
- TODO before Completed:
  - [ ] COST: placeholder KBWVE material presets. Match each bench's cost to the other-mod workbench it gets synced with.
  - [ ] STORAGE: keeps the pack's 80 capacity. Revisit (crate baseline) before marking Completed.
  - [ ] Hook the benches up as alternatives to other mods' workbench objects (e.g. the cure mod).
    Reference list of the workbench mods we have: `zomboid/WORKBENCH_TOOL_MODS.md` (Machinery,
    Zombie Virus Vaccine lab benches, Tikitown Scrap Works, TableSaw, Lifestyle: Hobbies). Use it to
    pick which bench each Fears bench pairs with, and copy that bench's cost.

## Reference files
- `zomboid/WORKBENCH_TOOL_MODS.md`: survey of mods with working workbenches, placed tools, or tool behaviour on existing sprites. This is the source list for matching our Fears benches (function + cost) later. Machinery's context-menu adoption of existing sprites (`WorldMachines.lua`) is the reference pattern for the hookup.
- `zomboid/communitytilepack/ARTIST_SPRITE_GUIDE.md`: art spec for new or missing tile art.

### 2026-08-28: TK kitchen_misc_tk_01 finished (sheet 57, In Progress, awaiting test)
- Generator: `pz_craft_loops/make_tk_kitchen_misc.py` writes `deliverables/57_community_tk_kitchen_misc.json`. The wire rack (12-15) stays in sheet 42 and has been renamed "Wire Shelf Rack" (it was labelled "Stainless Prep Counter").
- Deli Slicer (0-3): table-top decoration. Wall Shelf (4-7): high wall fixture, SpoonRack 30. Ice Machine (8-11): freezer 40 (my choice; the pack has no container). Deep Fryer (16-19): decorative only. Drip Coffee Maker (24-27) and Commercial Coffee Machine (28-31): KBW native `stove` (IsoStove, per the pack).
- Tile patch now reads ALL Community .tiles files, not just dylanstiles, and keeps firstIds unique inside the patch. It adds name, facing and BlocksPlacement to the ice machine and fryer (the pack gave only solidtrans).
- KBW's native path skips the table-top offset for stoves, so `KBWCommunity_TVScreens.lua`'s finalize hook now applies the vanilla table-top offset for `state.type == "stove"` objects with IsTableTop (coffee makers on counters).
- To check: coffee makers sit on the counter top and brew; the wall shelf mounts on both walls and in corners with a counter underneath; the ice machine keeps items cold with power; the facings look right for all four orientations.
- Note: the rack's definition says container type "counter", but the tile's `container=WireShelves` wins at build time (KBW reads the tile's container type first). Left as is because it's confirmed working.
- 2026-08-28 revision (per user): the ice machine is single-tile; it now copies the vanilla Chest Freezer (`appliances_refrigeration_01_48`): Freezer, FreezerCapacity 30, ContainerCapacity 30, fridge sounds and materials. The deep fryer copies the vanilla electric oven (`appliances_cooking_01_0`): IsoType=IsoStove, container=stove, so it cooks only with power. The copies are made at build time by `kbw_tilepatch._VANILLA_COPIES` (identity, facing, height and collision keys stay the pack's own). The ice machine, fryer and both coffee makers are built with `object.isProp` (KBW Vanilla Expanded's pattern for its Chest Freezer and Green Oven), which places them through vanilla `placeMoveableInternal`. So the containers, power use and on-counter height are vanilla's. The earlier stove-height hook in the TVScreens Lua is removed.

### 2026-08-28: TK wall shelf placeable only in corners (fix, awaiting test)
- Cause: the pack tiles 4-7 carry correct `attachedW/N/E/S` sprite FLAGS but swapped `Facing` values (4=S, 5=E, 6=W, 7=N). KBW `Placement.lua` `attachmentName()` checks `props:has("attachedW")`. `PropertyContainer.has(String)` only looks up key/value properties via TilePropertyAliasMap, never sprite flags (bytecode-checked), so KBW falls back to `Facing` and checked the wrong wall. Corner squares have both walls, so only they passed.
- Fix: new `kbw_tilepatch._PATCH_OVERRIDES` (replaces existing values in our patch copy; the merge overrides values). It sets Facing 4=E, 5=S, 6=W, 7=N to match the attached flags.
- General note: any pack wall fixture whose Facing disagrees with its attached flag will have this problem in KBW. Worth reporting to the KBW author (attachmentName should check `IsoFlagType.attachedW` etc.).

### 2026-08-28: coffee makers float on the floor (fix, awaiting test)
- Seen in game: on a counter they sit right, but on the floor they stay at counter height. Their art is drawn raised (IsTableTop + IsSurfaceOffset, Surface=34), so the floor case needs renderYOffset -34. Vanilla `placeMoveableInternal` should compute that (table height - Surface). `setRenderYOffset` accepts negatives (bytecode-checked). I couldn't confirm whether the offset is saved: the disassembler fails on IsoObject.save.
- Fix: `media/lua/shared/KBWCommunity_TableTop.lua` (generator `kbw_tilepatch.write_tabletop_lua`, sprite list `_TABLETOP_SPRITES` = TK kitchen_misc 0-3, 24-31). It wraps `ISMoveableSpriteProps.placeMoveableInternal` and also runs on LoadGridsquare, recomputing the offset with vanilla's formula (ignoring the object itself). Console line `[KBWCommunityTableTop] <placed|load>: <sprite> offset X -> Y` appears whenever it corrects one. The before value tells us what went wrong.
- Retest result (user): the shelf works; the coffee makers on the floor were still at counter height. Root cause, found in KBW's `KBWBuildingObject.lua`: `NativeObjectFactory.resolve` maps any `IsoType=IsoStove` sprite to KBW's native "stove" builder, and it is checked before `object.isProp`. So `isProp` never applied to the coffee makers (or the fryer), and vanilla `placeMoveableInternal` never ran for them. KBW's stove builder sets no table-top offset, so it stays 0. That looks right on a counter (the art is drawn raised) and floats on the floor. My earlier note that isProp sends them through vanilla placement was wrong for IsoStove tiles.
- Fix 2: the TableTop Lua now also wraps KBW `NativeObjectFactory.finalize` (in memory) and corrects the offset right after the build. New console lines: `[KBWCommunityTableTop] hooked KBW NativeObjectFactory.finalize (OnGameStart)` and `... built: <sprite> offset 0.0 -> -34.0`. Coffee makers already placed on the floor should be corrected on the next load by the LoadGridsquare pass.
- Possible KBW report: the native stove builder should call its own `applyTableTopOffset`, the way its other handlers do.

### 2026-08-28: Fears RP raccoon figure (sheet 58, In Progress, awaiting test)
- Generator: `pz_craft_loops/make_fears_rp.py` writes `deliverables/58_community_fears_rp.json`. The buildable is `community.fears.rp.raccoon_figure` with faces W=`fears_rp_tiles_61`, N=`_62`, E=`_63` (the pack has no S art).
- Tile patch: tile 62 now has CustomName "Figure" and GroupName "Raccoon" (the pack left them off it). The removal Lua strips `MoveWithWind` from 61-63; it was a pack error, with properties apparently copied from a tree.
- Build verified: patch entries, removal rows and faces are all present in the community mod and in TikiTownCommunityTest.
- To check: it places in all 3 orientations, doesn't sway, is solid like a low prop, and can be picked up and destroyed.

### 2026-08-28: Dirkies fencing_ddd_01 + _02 (sheet 59, In Progress, awaiting test)
- Generator: `pz_craft_loops/make_dirkies_fencing.py` writes `deliverables/59_community_dirkies_fencing.json` (76 buildables, category Fencing). The labelled contact sheets are in `pz_craft_loops/_cache_fencing_ddd/`.
- The DaddyDirkie BuildingMenu addon only covers 01 rows 8-39 (double fences built with onBuildHighDoubleFence, plus a corner and a post). It never uses the two-storey louvered fences or anything in fencing_ddd_02.
- Layout matches KBW Vanilla Expanded's high fences. Each family has:
  - a double piece (W `[[b+3],[b+2]]`, N `[[b, b+1]]`)
  - Half A and Half B pieces
  - a corner and a post
  - object.cornerSprite/pillarSprite, so KBW auto-draws corners and end posts
- Families:
  - picket (low)
  - concrete pillar + wire
  - cinderblock
  - cinderblock + planks
  - cinderblock with vines (plus a heavy-vines variant, 38/39)
  - old wood
  - plank
  - plank with vines (plus a heavy-vines variant, 62/63)
  - low concrete (hoppable)
  - broken louvered (02 24-29)
- Two-storey louvered fences (01 72-77 with tops 80-85/88-93; 02 0-5 with tops 8-13/16-21; 02 double-post 32-35 with tops 40-43/48-51, no corner or post): each piece is one buildable with a second geometry layer (z+1), the same way KBW VE does its stair railings. Per the user, the angled-cap and flat-cap tops are levels of one group, as are the halves and corners/posts.
- Tile patch: the new `kbw_tilepatch._SHEET_COPIES` gives the blank art tiles the properties of their configured twin (add-only): 01 72-93 from 02 0-21; 02 24-29, 32-35, 40-43 and 48-51 from 02 rows 0/8/16.
- Skipped per user: 01 tiles 14, 15, 30; 02 tiles 6, 7, 14, 15, 22, 23, 30, 31, 46, 47, 54, 55.
- COST TODO: costs are copied from the matching KBW VE piece (metal = Tall Wrought Iron Fence, cinderblock/concrete = Brick Fence, wood = Tall Wooden Fence, picket = White Picket Fence). VE's magazine knowledge gate is dropped to match the rest of our pack. Two-storey pieces currently cost the same as a one-storey piece.
- To check in game:
  - the z+1 top renders on an empty upper square and stays with the base
  - picking up or destroying removes both levels
  - W/N facings are correct
  - auto corner/post pieces appear
  - fences block movement; the picket fence and low concrete wall are hoppable
  - the patched blank tiles act as walls (the patch can add wall flags; I haven't confirmed in game that it does)
- Builder fixes made alongside: the official mod now writes group card titles to IG_UI. The test mod adds any missing names from the merged definitions to its old copied translation table (353 earlier names were missing).

### 2026-08-28: test results, Fears complete, two-storey fence fix
- Fears sheets 56 (workbenches + singles) and 58 (raccoon figure) were confirmed in game and are now in COMPLETED_SHEETS (10 buildables, "Fears - Completed").
- Overlay mapping for TikiTown shelves is ON HOLD (per user). The catalog tool and outputs stay in place (see tikitown/OVERLAY_CONTAINER_FILL_ANALYSIS.md).
- Dirkies fencing (sheet 59): the one-storey fences work in game. The two-storey louvered ones failed with "wall support missing".
  - Cause: KBW `Placement.validate` runs `hasWallSupport` on every wall tile in the footprint. The top tile's square (z+1) has no floor, so KBW wants an existing wall directly below it. That wall is the base being built in the same action.
  - Fix: `media/lua/shared/KBWCommunity_MultiStorey.lua` (generator `kbw_tilepatch.write_multistorey_lua`, in both mods) wraps `Placement.validate` in memory. It only applies to `community.*` buildables when the result is "wall support missing". It re-validates with the ground-level tiles only, then requires each upper square's edge to be free of another wall. Console line on load: `[KBWCommunityMultiStorey] wrapped KBW Placement.validate (...)`.
  - To check: the two-storey fences place, the top piece appears one level up, and picking up or destroying removes both levels.
- 2026-08-28: the two-storey fences now place with the multi-storey fix (the other louvered fences look right in game).
- TODO LATER: the Double-Post Louvered Fence (fencing_ddd_02 base 32-35, tops 40-43 / 48-51) has been REMOVED from sheet 59 for now (6 buildables; 70 left). In game its caps didn't line up with the base. I tried tops 40/48, then 8/16 (which misread the user), then the two cap rows swapped (48/40). The call is commented out in `make_dirkies_fencing.py` with this note; re-enable it once the correct top tiles are worked out. Its tile properties (the `_SHEET_COPIES` rows for 02 32-35, 40-43, 48-51) are still in the patch, which does no harm.
- 2026-08-28: zombie destructibility of fences. Our fences are KBW IsoThumpable walls with isThumpable on, so zombies can thump them. Because they are JSON-only buildables, their health comes from KBW `Durability.lua`, the same model KBW VE's fences use. Fence class is 250 base x material x (1 + 0.08 x skill req). Ours: metal 480 (+20/level), cinderblock/concrete 362 (+50/level), wood 310 (+20/level). The low picket fence and low concrete wall are hoppable, so zombies climb over them as they do vanilla low fences. BUG FIXED: the test bundle renamed the subcategory to "Fencing", and KBW only recognises a fence by category Fencing or a subcategory containing "fence". So test-mod fences got full wall health (865/652/558). `generic_type` now returns "Fences" for the Fencing category, and both mods give identical values. Not yet watched in game.

### 2026-08-28: Dirkies doors (sheet 46) name pass + invisible door
- The invisible "D Doors 01" was `community.dirkies.doors.d_doors_01_68`: tiles 68-71 have no art in the pack and no tile properties. Removed (58 -> 57 buildables).
- Name pass: `pz_craft_loops/rename_dirkies_doors.py` (an id -> name table, idempotent; edit and re-run to correct any name). Names were picked by eye from `zomboid/communitytilepack/dirkies_doors_index.png` (numbered in file order). Also fixed the doubled "... Door Frame Frame".
- Test-mod builder: the copied old name table now gets OVERWRITTEN by each definition's displayName, not just filled in where keys are missing. Before this, renames never showed in the test mod (32 stale names were updated).
- To check: the names read right in game (a few hinge-side twins were guessed: Light Grey/White Flush, Khaki/Olive Flush, Grey/Silver Aluminium Glass, Z-/Cross-Brace gates).

### 2026-08-28: name passes (doors + counters), TK complete
- Dirkies doors (46): mirrored pairs are renamed as halves of two-wide doors (each half built as its own tile): White Double Door, Khaki Double Door, Aluminium Glass Double Door, Wooden Double Gate and White Wooden Double Gate, each as (Left)/(Right). I assigned Left/Right by sheet order; swap them in `rename_dirkies_doors.py` if they read backwards in game.
- Dirkies counters (35): `pz_craft_loops/rename_dirkies_counters.py` gives 13 colourways as "<Body> Counter, <Top> Top" plus a "(Corner)" variant (single-colour ones are e.g. "Navy Counter"), and 5 upper cabinets (White/Grey/Walnut/Charcoal/Black Upper Cabinet). The index sheet is `zomboid/communitytilepack/dirkies_counters_index.png`.
- TK sheet 57 (kitchen misc) confirmed in game and moved to COMPLETED_SHEETS. Every TK sheet is now Completed.
- IDEA / TODO (user): let table-top tools such as the Deli Slicer satisfy a recipe's KNIFE requirement when the player is within 1 tile of one, like a crafting-station tool. Needs research first:
  - where B42 checks recipe tools (CraftRecipe input "tags[...]", e.g. SharpKnife, and the craft logic's nearby-entity / CraftBench hooks)
  - whether KBW or vanilla already supports a "world object provides a tool tag" pattern, or whether we'd wrap the tool check in Lua
  - which recipes it should apply to (food slicing only, or every knife recipe)
- 2026-08-28: Dirkies containers (sheet 40) name + subcategory pass, done with `pz_craft_loops/rename_dirkies_containers.py` (id -> (name, subcategory), idempotent). The index sheet is `zomboid/communitytilepack/dirkies_containers_index.png`. New subcategories: Wardrobes, Dressers, Cabinets, Counters, Tool Cabinets, Shelving, Medical, Crates, Pallets, Upper Counters. Notable renames: the tile-sheet names ("Industry Ddd 01", "Location Community Medical Ddd 01", "Edit Ddd Rus Fixtures Counters 03") are now real names. The "lockers" that are military cases are now Green/White Military Case and Pallet of ... Military Cases. The RUS fixtures counters are now "<Colour> Upper Cabinet" with a (Corner) variant.
- Test-mod builder: `generic_type` no longer puts every "Containers" item under "Counters". It keeps the item's own subcategory (counter pieces still go to Counters). This also changes the test-menu grouping for the Dylan/TK containers (Lockers, Crates, Shelves, etc.).
- NOTE: if sheet 40 is ever re-transpiled from the BuildingMenu addon, run `rename_dirkies_containers.py` afterwards.
- 2026-08-28 review of Dirkies containers (sheet 40, now 60 buildables):
  - CONFIRMED (marked Completed via exact ids in `build_merged_test_mod.COMPLETED_IDS`): Medical (4), Dressers (2), Crates (4), Pallets (15), Shelving (5), Tool Cabinets (1). Dirkies walls (sheet 43) added to COMPLETED_SHEETS.
  - REMOVED: Wooden Crate (industry_ddd_01_9), because vanilla already has it.
  - The "(Side)" wardrobes were the rear-facing tiles of the same wardrobe. They are now merged into the front buildable as E/S faces (white double, white glass, light wood double, light wood glass), each 4-way and 2 tiles.
  - Oak Glass Display Cabinet: added its missing rear tiles 48 (Facing W) and 49 (Facing N), the oak twins of the dark set's 96/97.
  - The "Dark Wardrobe" (RUS 80/85/86/87, Finnish wall A) is the NON-glass display cabinet: renamed "Dark Display Cabinet" and moved to Cabinets. Added the missing oak twin "Oak Display Cabinet" (32/37/38/39), copied from the dark one.
  - Still In Progress for retest: Wardrobes (4 merged), Cabinets (7), Counters (18), plus Doors and Fences.
  - All of this lives in `rename_dirkies_containers.py` (idempotent).
- 2026-08-28 Dirkies doors follow-up (56 buildables): d_doors_02_16 / _20 are now "Steel Blue Utility Double Door (Left/Right)" (per user). Removed "Grey Door (Bloodied)" (d_doors_01_56): the blood texture never shows. The 4 wooden gates required a door frame. They now place like KBW's vanilla gates (`placement.dontNeedFrame`, no `DoorFrame.OnIsValid` check), can't be barricaded, take no doorknob, and sit in subcategory "Gates". All of this is in `rename_dirkies_doors.py`.
- 2026-08-28: Dirkies Cabinets (7) and Wardrobes (4) confirmed and added to COMPLETED_IDS. The Dirkies doors + gates sheet (46) is complete.
- Dirkies RUS upper cabinets (edit_ddd_RUS_fixtures_counters_03, 0-63) couldn't be built over lower counters. The art hangs at head height, but the pack gave them the lower counter's properties (Surface 34, ContainerPosition Low, no IsHigh). KBW lets a piece share a square with a counter only if `MoveType=WallObject` and `IsHigh` (Placement.lua `isHighWallObject`), which is how the sheet-35 upper cabinets work. Fix in `kbw_tilepatch._PATCH_GROUPS`: add MoveType=WallObject + IsHigh, and strip Surface + ContainerPosition with the runtime removal Lua (64 rows). To check: they place over a counter, sit on the right wall in all 4 facings, and still open as a container.
- 2026-08-28: Dirkies fencing (59) confirmed. The broken louvered fence is the exception: it's back In Progress (INPROGRESS_ID_PREFIXES) after a rework.
  - Broken louvered fence (02 24-29): per user, a LOW wall you vault over. Its tiles had the intact fence's TallHoppable flags. They now have HoppableN (N), HoppableW (W) or both (corner 28), and TallHoppable is removed at runtime. The buildables are subcategory "Low" with object.hoppable=true.
  - `_sheet_copy_groups` now skips any key a `_PATCH_GROUPS` entry removes from that tile, so the patch file no longer re-adds it.
- Green Military Case (furniture_storage_ddd_01_4) is now stackable like vanilla/KBW crates: IsStackable + IsTable + Surface 17. Vanilla allows another crate while stack height + Surface <= 96, so Surface 17 gives exactly 5 high. I measured it by stacking the art at 14-20: 16 is pixel-flush but would allow a 6th; 17 leaves about a 1px gap. Back to In Progress for retest. The White Military Case and the pallets are unchanged.
- 2026-08-28: Green Military Case changed to Surface 16 per user, giving 6 high (5 x 16 + 16 = 96) and pixel-flush with the art.
- 2026-08-28: Dirkies Counters (Sofaking pair + 16 RUS upper cabinets) and the broken louvered fence confirmed. Every Dirkies group is now Completed except 3 crates.
- NEW: "Green Military Crate Case" and "White Military Crate Case" (ids `...furniture_storage_ddd_01_4.crate` / `_9.crate`) use the same art as the cases but take everything else from KBW's Military Crate (copied at build time from `military_crates.json` by `rename_dirkies_containers.py`):
  - container militarycrate 100, padlockable, blocks the square
  - cost: welding mask, BlowTorch 4 uses, SheetMetal x2, SmallSheetMetal x2, ScrapMetal x1, WeldingRods 4 uses, MetalWelding 7
  - construction: 50 time, BuildMetalStructureMedium, 70 MetalWelding xp
  Notes: the green crate version shares tile _4, so it is also stackable 6 high; the white one isn't stackable. The tile's own container type (locker) may still show as the container name; KBW sets the capacity to 100 after building. In Progress for test, together with the original green case's stacking.
- 2026-08-28: The White Military Case (furniture_storage_ddd_01_9) is now stackable too: same sprite in another colour, same IsStackable + IsTable + Surface 16, so 6 high. This covers both the original white case and the White Military Crate Case. Back to In Progress for retest.

### 2026-08-28: military cases, second orientation (awaiting test)
- The pack has only one orientation for the green (furniture_storage_ddd_01_4) and white (_9) cases. Tiles 5/6 and 10/11 look like a second angle but are the same case drawn 31/62 px higher (pre-stacked levels 2 and 3); shifted down they match 4/9 apart from shading.
- Fix: `kbw_tilepatch.write_cases_assets` mirrors 4 and 9 into tileset `KBWCommunityCasesMirror_0/1` (`pack=KBWCommunityCases`, `tiledef=kbwcommunity_cases 8183`; 8176-8183 checked free across all installed mods). Props = the source tile's + our stacking patch (IsStackable/IsTable/Surface 16), attachedN swapped to attachedW. The depth-map cells from `DEPTH_furniture_storage_ddd_01.png` are mirrored into `common/media/depthmaps`.
- `add_case_mirror_faces` adds face N (mirror) to the 4 buildables (_4, _9 and their .crate versions) at build time in both builders; the deliverable is unchanged.
- To check: rotate while placing; the mirrored case stacks on itself and on the original (Surface 16, 6 high).

### 2026-08-28: LoadGridsquare cost (WE dev feedback)
- WE dev (Foxrayne): the TV fallbacks are expensive on LoadGridsquare; WE has a "load grid gate", but it is a Java-side byte-replacement optimisation, so it can't be merged into our Lua.
- Change: `kbw_tilepatch._LOADGRID_LUA` is a shared dispatcher emitted into TVScreens + TableTop. ONE LoadGridsquare handler for both files (was two, each walking every object and calling instanceof/pcall per object). Per square: one pass, one sprite-name table lookup per object; work only for our 16 sprites (`KBWCommunityLoadGrid.bySprite`).
- Gate contract for WE: `Events.LoadGridsquare.Remove(KBWCommunityLoadGrid.onSquare)`, then call `KBWCommunityLoadGrid.onSquare(square)` from the gate (optionally prefilter on `bySprite`). Stable Lua names, no byte offsets.
- The EveryOneMinute 25x25x3 nearby-TV scan now runs only when `isClient()` (MP clients). SP/servers rely on the finalize hook + load dispatcher.
- Verified with a real Lua runtime on mocks (1 handler registered, TV gets 3 screens, coffee maker on floor -> -34). Not yet tested in game.

### 2026-10-30: Dylan-sheet icons look wrong on the server (TO CHECK; lead below)
- Same symptom on **every Dylan-sheet buildable** seen so far, all in the WE build menu and none built yet:
  exercise ball + punching bag (above/below), **viewscreens** (`DylansFutureRoom01`, "like the index
  is wrong") and **wall TVs** (`DylansRandomFurniture02_36-39`).
- Lead (checked on disk, not in game):
  - **Fort Waterfront B42** (3486814612, on the server mod list) ships its own `dylanstiles` under
    the SAME tiledef 6985 as the Community Tilepack (also `tkTiles_01` 830 and
    `diederikv_tile_def` 7001). The log shows `tiledef fileNumber 6985 used by more than one mod`.
    Only one copy is kept.
  - The two `dylanstiles.tiles` differ: Community Tilepack `DylansRandomFurniture02` = 8x6, 48 tiles;
    Fort Waterfront = 8x8, 64 tiles (sha e9f079e4 vs 18403515; FW's matches standalone DylansTiles
    2599752664).
  - **Load order flips:** single player loaded Fort Waterfront then Community Tilepack; the server join
    (18:13) loaded Community Tilepack then **Fort Waterfront** (so FW's copy is the later one there).
  - **Art is NOT the difference:** the textures for all 16 of our sprite names (ball 5-7, bag 12-13,
    TVs 36-39, viewscreens 24-27/32-34) are pixel-identical in both `DTilesPack.pack` copies
    (`_dyl_compare.png` check, 2026-10-30).
  - So the suspect is the tile-definition layer: which `dylanstiles` wins, and how our
    `kbwcommunity_tvpatch.patch.tiles` (generated from the Community Tilepack's 48-tile layout)
    merges onto Fort Waterfront's 64-tile one.
- **2026-10-30 LIKELY CAUSE (supersedes the "can't explain it" note below):** a tile-number shift between
  the two `dylanstiles` copies sharing tiledef 6985.
  - The Community Tilepack trims several Dylan sheets: DRF01 32, DRF02 48, Bar01 48, DRF04 32,
    Police01 32, BlackCoffee 24 tiles. Fort Waterfront (= original DylansTiles 2599752664) has all of
    them at 64 and adds 3 tilesets.
  - If the game numbers tiles through the file and one copy's numbers are read against the other
    copy's layout, everything after DRF01 slides. That explains why the viewscreens break even though
    their own sheet is identical.
  - Screenshot evidence: the premium CRT TV (iconSprite DRF02_38) shows a DylansRandomFurniture03
    cabinet (red/black front, ~03_20-21); the CRT TV (02_36) shows the grey one next to it
    (~03_18-19). That is a shift of about 16-18 tiles; DRF02 itself is 48 vs 64 = 16. The exact
    numbering rule isn't confirmed (no access to the game jar here).
  - Load order fits: SP worked with **Fort Waterfront -> Community Tilepack** (CTP last). The server
    loads **Community Tilepack -> Fort Waterfront** (FW last), and that is where it breaks.
  - This is a conflict between those two mods (both ship dylanstiles 6985, also 830 tkTiles and
    7001 diederik). It isn't in our definitions, so any mod using these sprites is affected.
  - **Test to confirm:** in single player, enable both in the server's order (CTP before FW) and check
    the TV/viewscreen icons; then swap the order.
  - **Likely fix (server admin):** load `Fort Waterfront B42` BEFORE `UnofficialMappersCommunityTilePack`.
    - Caveat: if CTP wins, FW map squares that use Dylan tiles CTP trimmed (e.g. DRF02_48-63) may
      show wrong or missing. Check the Fort Waterfront map after reordering.
    - Other option: one shared dylanstiles (the full 64-tile one) in both packs. That's for those
      mods' authors.
- 2026-10-30 update: **placed objects are wrong too** (not just icons).
  - Tile firstIds match in both dylanstiles files (DylansRandomFurniture02 = 7, DylansFutureRoom01 = 26)
    and in our patch.
  - **DylansFutureRoom01 is identical in both** (8x8, no property diffs, same art), yet viewscreens
    are wrong too. So the Fort Waterfront 6985 clash alone can't explain it (it's still a real
    conflict, but not the cause).
  - DylansRandomFurniture02 differs in size (CTP 8x6 vs FW 8x8) and in properties on indices 0-15,
    22-31, 34-43.
  - Remaining suspects (unverified):
    - the server's Java-side optimisations (byte replacements; its LoadGridGate is scoped to our 16
      TV/table-top sprites);
    - other WE code that touches sprites;
    - client-side mods.
  - Next: a screenshot of WHICH tile appears (the offset tells a lot), and a single-player repro
    with the server's exact mod list/order.
- To check in game on the server:
  - which `dylanstiles` is active (console `loading` order and the 6985 error);
  - whether the icons are also wrong in single player with the same load order;
  - build one TV, viewscreen, ball and bag and see what actually gets placed;
  - check TK (830) and Dirkies/diederik (7001) pieces too, since those tiledefs are duplicated by
    Fort Waterfront as well.

### 2026-10-30: exercise ball + punching bag icons look wrong (WE submod, TO CHECK)
- Seen in the build menu of the WE-bundled version (World Essentials - Community Buildworks): the
  Exercise Ball and Punching Bag show messed-up icons. Neither has been built yet.
- Buildables: `community.dylan.rf02.exercise_ball` (iconSprite `DylansRandomFurniture02_5`; variants
  pink 5 / blue 6 / yellow 7) and `community.dylan.rf02.punching_bag` (iconSprite `_12`; variants
  red 12 / black 13), in `53_community_dylan_rf02_misc.json`. Both use `variants`, which most of our
  other buildables don't.
- To check:
  - How do the icons look in our own build vs WE's? The definition files are byte-identical, so a
    difference would point at WE's runtime/catalogue side.
  - Is it every variant or only the default?
  - Build one of each: does the placed object look right (sprite, height, walk-through)?
  - Do the icons render the right tile for each variant's `iconSprite`?
- Not yet investigated; no cause assumed.

### LONG-TERM GOAL (decided 2026-10-30): support both tile sources
| Installed | Dylan layout to use |
|---|---|
| Community Tilepack only | Community Tilepack's `dylanstiles` (trimmed sheets, e.g. DRF02 = 48) |
| Fort Waterfront B42 only | Fort Waterfront's `dylanstiles` (full 64-tile sheets, = DylansTiles 2599752664). Enable the Dylan buildables for it too |
| Both | **Fort Waterfront is primary** |
- Requirements to work out:
  - "Primary" must hold at the TILE layer, not just in our Lua. Both register tiledef 6985 and only one
    file survives (load order decides), so "both installed" needs FW's file to actually win. Either
    require/recommend FW to load after the Community Tilepack (the current server order already does
    this), or confirm with an in-game test which one wins in each order.
  - Build two variants of everything that depends on the layout:
    - the Dylan part of `kbwcommunity_tvpatch.patch.tiles` (generated from the 48-tile CTP file today);
    - the Dylan buildables' sprite indices, if any differ between the two layouts. Check index by index:
      DylansFutureRoom01 is identical, DRF02 differs in properties;
    - the generated TV-screen and viewscreen tiles (sprite names unchanged; check offsets).
  - Select at runtime with `getActivatedMods():contains("Fort Waterfront B42")` (Kahlua-safe).
    Note that `.tiles` patches are picked by mod.info, not Lua. The layout-dependent patch may need to
    live in its own optional submod that requires Fort Waterfront, or both property sets may need to
    merge safely.
  - Fort Waterfront also duplicates TK (830) and diederik (7001). Apply the same rule to those sheets
    once checked.
- Until then, `EXCLUDE_DYLANSTILES = True` in build_community_mod.py drops all 49 Dylan buildables.
- Also check TK (830) and Dirkies/diederik (7001), which Fort Waterfront duplicates too.

### 2026-10-30: WE dev fixed the Dylan texture/tile issue on his end (TO INVESTIGATE)
- The WE dev implemented his own fix for the wrong Dylan tiles (Fort Waterfront / Community Tilepack
  `dylanstiles` 6985 clash). We haven't looked at how yet.
- When WE next updates:
  - refresh `zomboid/WE_submods/upstream/` and diff against `work/` to find his change;
  - check whether he shipped our Dylan hotfix zip or something else;
  - see if his approach covers our "support both, Fort Waterfront primary" goal;
  - then decide whether `EXCLUDE_DYLANSTILES` in build_community_mod.py can go back to False.

## 2026-11-02: WECommunity names adopted + name/tooltip pass DONE (build-verified, not in game)
- `build_community_mod.py` now emits WE's isolated Dylan sprites (`we_dylan.py`): EXCLUDE_DYLANSTILES
  off, 231 sprite refs renamed to `WECommunity_*` (1:1, same index), WE's `wecommunity_dylan.tiles`,
  `WECommunityDylan.pack` and tileGeometry blocks vendored verbatim in
  `zomboid/communitytilepack/vendor_we/` (re-run `pz_craft_loops/_vendor_we_dylan.py` after an
  upstream refresh). Build fails if a Dylan sprite has no WE copy. The we_sync guard now passes and
  the Dylan files are byte-identical to WE's.
  - The TEST bundle still uses the original Dylan names (it requires the Community Tilepack
    directly), so on a server with Fort Waterfront its Dylan pieces can still shift.
- `pz_craft_loops/name_tooltip_pass.py`, called by all 3 builders:
  - 127 name fixes (raw sheet names, doubled words, duplicates split by art, mislabelled
    extinguisher box). 0 duplicate names left in either pack.
  - translationKeys shared by differently named pieces are split (TikiTown garage doors all
    showed "(2 Wide)"). 40 keys.
  - Every piece has a one-line type tooltip: our `Tooltip_KBWCB_*` keys + KBW's own where they fit.
    Old `Tooltip_WETiki_*` / `Tooltip_KBW_Shared_*` keys are no longer used (WE's Expansion
    defines 379 Tooltip_WETiki keys itself).
- Hand-off: `WE_handoff_zips/WE_Buildworks_NamesTooltips_20261102.zip` (38 files, defs + EN
  translations; supersedes the 2026-11-01 tooltip zip).
- Still open: in-game look at the new names/tooltips; the storage-capacity line shows the tile's
  container name and capacity (separate capacity pass).

## CONFIRMED IN GAME 2026-11-02: ice machine tiers 30 / 65 / 100 all work (user)
- Stage `container.capacity` resizes the ice machine's freezer (its only container), same as the
  military crate. The build-menu tooltip still shows the tile's 30 (expected).
- Test-bundle bug found and fixed: build_merged_test_mod.py dropped per-file `materialGroups`,
  so KBW rejected the 65 / 100 ("references unknown material group"). It now merges them.

## CONFIRMED IN GAME 2026-11-02: two-stage ice machines work (user)
- Shells place and are not freezers; the finished 65 / 100 only place on their own shell (same
  tile + facing), replace it, freeze, and hold 65 / 100. KBW `previousStage` + an inert generated
  tile copy is the proven pattern for future multi-stage appliances (e.g. the 100 fridge).
- Still open: build sounds (see TODO below).

## DONE: two-stage builds for the 65 / 100 ice machines (decided 2026-11-02)
- The 30 Commercial Ice Machine stays a single build (it fits the ~75 carry weight).
- 65 and 100 become two builds, like vanilla frame -> wall: stage 1 "Ice Machine Shell"
  (art only, not a freezer, heavy materials), stage 2 built ON the shell (fridge parts and
  electronics, sets capacity 65 / 100). Each build gets its own ~75 weight budget.
- KBW mechanism (checked in code): stage 2's stage sets `"previousStage": "<shell buildable id>"`.
  Placement.findPrevious finds the shell on the same tile and facing; KBWBuildingObject.create
  removes it and places stage 2 in its slot. Each stage has its own requirements, XP and time.
  The build menu shows "Build first: X, on the same tile and facing the same direction."
- Two catches:
  1. The shell needs art WITHOUT the freezer properties (our kitchen_misc_tk_01_8..11 tiles are
     patched with Freezer / FreezerCapacity, and KBW makes any tile with a container property a
     container). Generate an inert copy in our own sheet, like KBWCommunityCasesMirror.
  2. The shell must be an IsoThumpable (object.isThumpable, NO isProp): findPrevious only matches
     IsoThumpables. Stage 2 can stay isProp.
  - Use a distinct shell id (e.g. `..._shell`): previousStage matching is a suffix match, so
    `ice_machine` alone would also match the existing working 30 ice machine.
- Blowtorch stays at 5 uses on every build; rods / refrigerant within one pack / bottle.
- Waiting on: in-game test of the current 65 / 100 tiers, and the push (tags need pushing from
  here after the first GitHub Desktop push).

## TODO (come back later): build sounds missing on the ice machine shell (seen 2026-11-02)
- In game (test bundle): building the Ice Machine Shell plays no welder loop and no completion
  sound. Only the shell was tested so far; unknown whether the 30 ice machine, the finished
  65 / 100, or KBW VE's own Chest Freezer are also silent.
- Checked in code, all look correct: our construction block is KBW's chest-freezer template
  (timedAction BuildWallMetal -> sound BlowTorch; completionSound BuildMetalStructureMedium, both
  exist in the game scripts). KBW copies them onto the build (KBWBuildingObject.lua 550-557:
  craftingBank / completionSound) and vanilla ISBuildAction plays both unconditionally
  (ISBuildAction.lua 93-96 loop, 216-217 completion).
- Next steps: compare with the 30 ice machine and KBW VE Chest Freezer (if silent too -> KBW-side
  or mod-mix issue, report to the KBW dev); ask whether the build was started from the build menu
  or KBW's planner/queue; check console.txt for sound errors during a build.
- Unrelated log line seen at the same time: "[WorldEssentialsKnox][BuildAttempt]
  ice_machine_100_shell ... not queued: build action not created" (WE Knox Expansion hook), yet the
  shell DID build. Probably a duplicate/rejected click; harmless. Note WE - Knox Buildworks
  Expansion stays enabled even with WE off (separate submod).

### 2026-11-02: popsicle freezer dropped; fridge / freezer tiers (test bundle only, awaiting test)
- 2-tile two-stage builds are dropped. WE's own `WorldEssentialsKnox/Placement.lua` replaces KBW's
  check and only waives collisions on the ANCHOR tile of a replacement ("Replacing the anchor does
  not waive checks on other parts"). The freezer's second tile hit the solid 2nd shell tile
  ("Something solid is in the way"); offsetting by one tile built it shifted. Single-tile shells
  are unaffected. The `kbwcbReplacePrevious` Lua property and the popsicle shell tiles are removed.
- New (test bundle, "Community - In Progress > Test - Fridges"), generator
  `align_appliance_costs.build_fridge_defs`, 59 buildables (35 units + 24 shells):
  - 8 standard KBW VE fridges: 60/30 (single), 80/40 and 100/50 (two-stage). MW6+E4 / MW7+E5 / MW8+E6.
  - Mini Refrigerator: 30/8 (single), 40/12, 50/15. MW4+E4 / MW5+E5 / MW6+E6.
  - Industrial + White Industrial freezer-only: 30/30 (single), 65/65, 100/100, ice-machine cost,
    skills on the fridge ladder (MW6+E4 / MW7+E5 / MW8+E6; user: line them up with the fridges).
  - Chest Freezer 65 / 100, ice-machine cost and skills (KBW's own Chest Freezer is the 30).
  - Trailer Built-In Fridge untouched. Alternatives without the magazine: E8 / E9 / E10.
- Shell art: `KBWCommunityIceShell_4..43` (vanilla appliances_refrigeration_01 copies, all
  container / moveable / fridge / freezer properties stripped) + depth map. Test bundle only; the
  WE build still has only the 4 ice-machine shells.
- Freezer-only uses new Lua property `kbwcbContainerTypes {"fridge": "freezer"}`
  (ItemContainer:setType), tested against lupa mocks only (both property orders).
- To verify in game: each tier's capacities (loot window), freezer-only shows two freezers that
  actually freeze, shells take no power, both survive save + reload (also still pending for the
  100/100 test fridge). Picking up a tiered fridge returns a vanilla fridge item and re-placing it
  probably gives the vanilla 40/20 (capacity is set on the built object, not the tile). Not checked.
- 2026-11-02 description fixes (user: container values correct in game, build-menu text wrong):
  - "Build first: <raw id>": KBW BuildableInfo.placementHint looks up
    `IGUI_KBW_Vanilla_<previousStage id>`. Builders now add those keys with the shell names
    (`container_caps.previous_stage_names`), test bundle AND Community build (ice machine shells).
  - Capacity line showed the tile's numbers (tile ContainerCapacity / FreezerCapacity win over
    stage container.capacity in KBW). New client file `KBWCommunity_StageInfo.lua` wraps
    BuildableInfo.containerTiles to show kbwcbContainerCapacity / kbwcbContainerTypes /
    container.capacity. Test bundle only, tested against lupa mocks. The WE ice machines (65/100)
    still show 30 in the menu until this Lua ships to WE.
  - CONFIRMED in game (user, 2026-11-02): container values correct; build-menu text correct
    ("Build first: Green Refrigerator 80/40 Shell", "Tile 1 - Fridge: 80 + Freezer: 40").

### 2026-11-02: pick-up reverted our customs to the base tile (user bug; fix awaiting test)
- Cause: vanilla pick-up makes a plain moveable item that remembers only the sprite; placing it
  rebuilds the containers from the tile, so build-time capacities / freezer types were lost
  (fridge / freezer tiers, ice machines, reinforced counters and cabinets).
- Fix (test bundle only, tested against lupa mocks): shared `KBWCommunity_Pickup.lua`
  (`container_caps.write_pickup_lua`) wraps ISMoveableSpriteProps pickUpMoveableInternal /
  instanceItem / placeMoveableInternal. The picked-up item gets `modData.kbwcbStorage`
  (build id, name, each container's type + capacity) and is renamed to our build's name (KBW
  Registry + I18n); placing it re-applies types + capacities and keeps the record on the object.
  "Ours" = KBW buildableId starting community. / tikitown. / worldessentials.tikitown. / kbwcb.
- Not covered: multi-tile ForceSingleItem pieces (one item for the whole grid). The re-placed
  object is a plain moveable, not a KBW build any more (KBW dismantle refund not restored).
- Check in game: name in inventory; capacities after placing; freezer-only stays two freezers;
  rotate keeps capacities; a picked-up + re-placed fridge picked up again keeps the name.
- CONFIRMED in game (user, 2026-11-02): picked-up + re-placed builds keep their capacities.
- Item rename didn't show: `zombie.inventory.types.Moveable.getName` (javap) builds the name from
  the tile's movableFullName / customNameFull and ignores the item name (no Lua setter). Dropped
  setName. Instead `KBWCommunity_StageInfo.lua` (client) wraps ISToolTipInv.render and draws a box
  under the inventory tooltip: our build's name + "Fridge: 80 + Freezer: 40" (lupa mocks only).
  Items picked up with the previous build already carry the name in their record, so they should
  show the box too.
- CONFIRMED in game (user, 2026-11-02): inventory tooltip box shows our name + storage.

### 2026-11-02: counters can't be rotated when placed from inventory (fix awaiting test)
- Cause (javap, IsoWorld.LoadTileDefinitions): the engine only generates the moveable face
  offsets (Noffset/Eoffset/Soffset/Woffset) when a tileset groups <= 4 moveable tiles under one
  GroupName + CustomName, all with Facing, no facing twice. Dirkies groups far more
  (d_furniture_kitchen_01 "Modern Corner / Counter" = 52 tiles, edit_ddd_RUS counters 32,
  Block_Trasher 8); DylansRandomFurniture03 has no GroupName. TikiTown tterika / TK / Dylan bar
  counters were fine. Not specific to our reinforced versions.
- Fix (test bundle only): `rotation_fix.py` -> shared `KBWCommunity_Rotation.lua`. Offsets come
  from our KBW definitions (which sprites are one piece's facings) and are set with
  PropertyContainer:set at OnLoadedTileDefinitions / OnGameStart. 120 pieces (254 sprites)
  fixed, 214 already rotate. Skipped: walls / non-moveables, shells, 15 pieces whose 2nd facing
  is in our generated mirror sheet (offsets only work inside one sheet), 12 with broken pack
  Facing (e.g. location_community_medical_ddd_01: every tile Facing=E).
- Check in game: console "[KBWCommunity] Rotation: face offsets set on 254 sprite(s)"; a Dirkies
  kitchen counter rotates (R) when placed from inventory and lands with the right art.

## 2026-11-02: RELEASE CANDIDATE -- everything above CONFIRMED in game (user)
All of this session's work was tested in the TikiTownCommunityTest bundle and confirmed working:
- name / tooltip pass, WECommunity Dylan swap
- appliance costs (ice machine = KBW Chest Freezer, deep fryer = KBW Green Oven)
- ice machine 30 / 65 / 100 (65 + 100 two-stage on inert shells)
- reinforced counters / upper cabinets / wall cupboards (crate cost, 100)
- fridge / freezer tiers: 8 fridges 60/30-80/40-100/50, mini 30/8-40/12-50/15, Industrial +
  White Industrial freezer-only 30/30-65/65-100/100, Chest Freezer 65 / 100 (59 buildables)
- container capacity + freezer retype (KBWCommunity_StageProperties.lua), survives save / reload
- build-menu text: "Build first: <shell name>", real capacities (KBWCommunity_StageInfo.lua)
- pick up / place keeps storage + inventory tooltip box (KBWCommunity_Pickup.lua / StageInfo)
- moveable rotation for badly grouped pack tiles (KBWCommunity_Rotation.lua)
Dropped: 2-tile two-stage builds (popsicle freezer) -- WE's placement check only waives the
anchor tile. Still open (not in this RC): build sounds on shells; TK / Dirkies tiledef isolation;
container balance pass; desk allowSpriteReuse; Fort Waterfront-aware Dylan.

RC moves the test-bundle-only pieces into the WE submod builds:
- Community: 70_kbwcb_refrigeration_tiers.json (Appliances > Refrigeration, 12 catalog cards),
  KBWCommunityIceShell sheet 4 -> 44 tiles (same pack / tiledef 8181, no mod.info change) +
  common/media/depthmaps/DEPTH_KBWCommunityIceShell.png, Lua StageProperties / Pickup / Rotation
  (shared) + StageInfo (client).
- TikiTown: KBWTikiTown_Pickup.lua, KBWTikiTown_Rotation.lua (shared), KBWTikiTown_StageInfo.lua
  (client) -- own file names so the submods never shadow each other; install guards make loading
  both harmless.

### Tailoring Workbench built-in needle + "Tailoring" menu (test bundle only)

#### rev 2 (2026-08-28) — Direction A (virtual container). REPLACES rev 1. Mock-tested, NOT game-tested.
rev 1 (real needle in the bench's own container) was confirmed broken in game: players could fill
the container, only one of the bench's two tiles held the needle, and every craft popped a "part of
the workbench" message (the transfer-block halo firing on the craft's internal tool handling).

**Direction A fix — no real item the player can reach, no lootable container:**
- A single DETACHED virtual `ItemContainer.new()` (no parent object/square) holds one transient
  needle. It is never rendered in a loot window and never saved → nothing to fill/drop/transfer.
- B42 craft panels build their tool/ingredient pool via `ISInventoryPaneContextMenu.getContainers`
  then `HandcraftLogic:setContainers` (both `ISHandCraftPanel:updateContainers` and
  `ISCraftLogicPanel:updateContainers`). We wrap `getContainers` to APPEND the virtual needle
  container ONLY while a module flag `BT._inCraftQuery` is set AND the player is adjacent to a
  configured bench. The two craft `updateContainers` methods are wrapped to set/clear that flag, so
  the loot window and every other `getContainers` caller never see the needle (no UI leak).
- Bench adjacency (`BT.adjacentBenchConfig`) scans the player's square + the 8 neighbours for any
  object carrying the `kbwcbBenchTools` config, so it covers BOTH tiles of the 2-tile bench.
- NO transfer/drop/pickup/stray-sweep hooks anymore (the needle is unreachable). Much less code.
- Kept: stage property `kbwcbBenchTools` {tools, category, labelKey} on
  `community.fears.workbench.tailoring` (tags the bench); item `KBWCommunity.WorkbenchNeedle`
  (Tags base:sewingneedle, flagged never-spawns); right-click "Tailoring" → vanilla craft window.
- Generator `pz_craft_loops/bench_tools.py` (rewritten). Verified: mock test `_test_bench.py`
  (lupa, `next` deleted) — 9/9 PASS incl. inject only in craft query + only when bench adjacent,
  flag clears, no loot-pane leak, virtual container cached. Shipped in the test bundle (rc=0).
- Only benches built AFTER this build get the config (stage property applies at build time).
- **TODO (game test):** stand by the Tailoring Workbench, craft a needle-tool recipe → should work
  with no needle in inventory and NO message; confirm the needle never appears in any loot window;
  confirm it works from either of the bench's two tiles; MP (server rebuilds containers each query,
  but our wrap runs client-side on every craft refresh, so it should still apply).
- Not covered: clothing patching (Inspect > Patch) reads the player's own inventory only — out of
  scope for this craft-panel injection.

---

## TikiTown Newburbs TRIM (`35_tikitown_newburbs_trim.json`)

### rev 2 (2026-08-28) — REBUILT on the wall model after in-game bugs. NOT yet re-game-tested.
First in-game test of rev 1 found two bugs; both are fixed in rev 2:
1. **Door trim demanded a wall, refused to place over a door frame** (placed fine over a wall).
   Cause: the object model's `needToBeAgainstWall` check wants a solid wall, not a door frame.
2. **Duplicate pieces** — e.g. "Door Trim Head" and "Door Trim Jamb" were the SAME sprite in two
   orientations. rev 1 emitted the West-wall sprite and the North-wall sprite of one piece as two
   separate buildables. User confirmed this happened across many pieces.

**Fix — model trim exactly like the proven Newburbs walls/interiors (27/28_*_accurate.json):**
- `placement {kind:"wall", requiresFloor:false}`; the engine auto-orients to the wall edge.
- Each logical piece is ONE buildable with BOTH a `W` face and an `N` face (+ an `E` face where the
  sheet has an east variant). No more W/N duplicates. Verified: 0 single-sprite pieces share art.
- `pieceClass`: door casing = `door` (places over door frames → fixes bug 1); window casing +
  surrounds = `window` with `dontNeedFrame:true` + `providesWindowFrame:true`; base trim = `wall`.
- Within each sheet row: LEFT half = West sprite, RIGHT half = matching North sprite, trailing col =
  East variant (user-confirmed). W↔N pairs fold into one buildable.
- Recipe unchanged: hammer (keep) + 2 Plank + 4 Nails, Woodwork 2, 40xp, BuildWallHammer, Carpentry.
  category "Decorations and Landscaping", subcategory "Newburbs Trim", `allowSpriteReuse:true`.
- **Count: 28 pieces/color × 6 colors = 168 buildables** (was 240 in rev 1; the W/N merge removed 72).
  Colors: 01_white, 02_red, 05_darkgreen, 06_darkblue, 08_black, add_01_brightred. (orange NOT done.)
- Generator: `pz_craft_loops/newburbs_trim.py` (rewritten). Tile→face map verified vs `.tiles` art.
- Build verified: `_run_all.py build_merged_test_mod.py` rc=0, **3081 total buildables, 0 duplicate
  ids**, 168 trim pieces all `kind:wall` (window 144 / door 6 / wall 18). See `_trimverify.txt`.
- Wiring unchanged (build_tikitown_mod SRC_FILES; build_merged_test_mod TT_FILES + TT_PACK_OF/
  TT_COMPLETED so "35" = TikiTown Newburbs, not Dirkies; status "In Progress").
- rev 2 game test confirmed: **door frame works**. Two bugs found and fixed in rev 3 (below).

### rev 3 (2026-08-28) — base-trim overlay fix + garage-door-trim merge. NOT yet re-game-tested.
rev-2 in-game test findings:
1. **Base trim destroyed the wall it was placed on** (corner and straight). Cause: base trim was
   modelled as a real wall (`pieceClass:"wall"` + `object {isThumpable:true}`), so it replaced the
   wall-edge object. FIX: model base trim on KBW VE **"Black Vinyl Trim"**
   (`KnoxBuildworks_Vanilla_Expanded/.../architecture_plus/crown_molding.json`): an OVERLAY drawn on
   top of the wall. `placement {kind:"overlay", needToBeAgainstWall:true}`,
   `object {blockAllSquare:false, canPassThrough:true, canBarricade:false, dismantable:true}`; the
   corner adds `isCorner:true` (W-only). No `isThumpable`, no health. pieceClass emitted as
   "decoration". (Knox keeps the matching floor-level trims in a sibling `floor_molding.json` under
   subcategory "Floor Molding" — same overlay model, if we ever want to match that subcategory.)
2. **"Window Jamb (Medium)" (idx 37/38/39) are GARAGE-DOOR trim, and "Window Jamb (Short)"
   (idx 29/30/31) is the same piece in the other orientation.** FIX: merge each pair into ONE
   buildable (W=29.. / N=37..), a new "Garage Door Trim" family (3 pieces), plain wall-edge casing
   (`kind:"wall"`, `pieceClass:"wall"`, no window-frame flags). Removed the 6 old `surround_*_edge`
   jamb entries. (idx 45/46 remain as the tall-surround "Window Jamb" edge pieces — those are
   genuine window-surround edges, not garage.)

**Count after rev 3: 25 pieces/color × 6 = 150 buildables.** Build verified:
`_run_all.py build_merged_test_mod.py` rc=0, 3063 total buildables, 0 duplicate ids, 0 cross-piece
sprite collisions. Generator `pz_craft_loops/newburbs_trim.py`.
- **TODO (game test rev 3):** base trim overlays the wall WITHOUT destroying it (corner + straight +
  end); Garage Door Trim places correctly around a garage door and the two orientations show right;
  earlier rev-2 items (door frame ✓, window casing/surround alignment, no dupes) still good.
- **Left for a later pass:** orange sheet; unmapped lower-sheet tiles (idx 47/68 empty, 48-63,
  69/70, 72-77 on the white sheet).

### rev 3 (2026-08-28) — needle CONFIRMED in game; expanded to all 6 benches + build cost
The Direction-A needle works in game. Generalised to every workbench with a clean craft category:
each bench now provides ALL core tools for its crafting type, and building it COSTS one of each of
those tool types (any variant accepted) on top of its normal materials.

- Benches + core tool tags (core = tag used by >=25% of the category's recipes in the B42 recipe
  scripts; Metalworking had obvious tailoring bleed removed):
  - tailoring (Tailoring): scissors, sewingneedle, awl, sharpknife
  - metalworking (Metalworking): weldingmask, metalsaw, sheetmetalsnips, metalworkingpunch,
    drillmetal, hammer, wrench
  - electrical (Electrical): screwdriver, pliers
  - carpentry (Carpentry): saw, crudesaw, smallsaw, hammer
  - gunsmithing (Weaponry): drillmetal, wrench
  - chemistry (Medical — no dedicated Chemistry category in B42): mortarpestle
  - NOT done: wood_gas_stove / air_compressor (utility stations, no tool reqs); anvil (blacksmith —
    its tools need the forge/furnace STATIONS, a different gated-surface problem, out of scope).
- Alternates: each tool tag expands to ALL its member items (from the B42 item scripts, e.g.
  scissors = Scissors/ScissorsBlunt/ScissorsBluntMedical/ScissorsForged/Multitool). Runtime holds
  one of every member (so every recipe variant resolves); the build-cost input lists all members as
  `items[...]` alternates (pay with whatever you have).
- Runtime unchanged in mechanism (detached virtual container injected into the craft getContainers
  query only when adjacent to a bench). No custom item anymore — holds REAL vanilla tool items, so
  the old `KBWCommunity.WorkbenchNeedle` item + its scripts file are dropped.
- Build cost: `apply_to_buildables` appends one consumed input per core tag ALONGSIDE the bench's
  existing materialGroup. Verified KBW VE does exactly this (102 buildables have both `materials`
  group ref + inline `inputs`, e.g. appliances/bathroom.json) so the base cost is preserved.
- Generator `pz_craft_loops/bench_tools.py` (rewritten). Verified: config well-formed, Lua
  Kahlua-safe, apply_to_buildables adds correct stage property + per-tag cost inputs to all 6
  benches, materialGroup kept, idempotent. Test bundle built rc=0; "bench tools on" lists all 6.
- **TODO (game test):** at each bench, craft a recipe of its type with NO tools in inventory →
  works; building each bench now also requires one of each core tool (any variant). Right-click
  menu opens the bench's craft category.

### rev 4 (2026-08-28) — workstation craft-speed bonus (+10%)
Second bench goal: crafting at a workstation of the recipe's type is 10% faster.
- Hook: wrap `ISHandcraftAction:getDuration()` (the one place craft time is decided; vanilla returns
  `craftRecipe:getTime(character) * 5`). When the player is adjacent to a configured bench whose
  `category` equals `self.craftRecipe:getCategory()` (confirmed Java accessor on CraftRecipe), the
  duration is scaled by `BT.SPEED_MULTIPLIER = 0.90`. Guarded with pcall so a bad category read can
  never break crafting; instant actions (return 1) and no-recipe (return -1) are left untouched.
- Reuses `BT.adjacentBenchConfig(player, wantCategory)` (added a category filter param) so only a
  MATCHING-type bench gives the bonus (a tailoring bench won't speed up carpentry).
- In bench_tools.py `_SHARED`, installed in `install()` on OnGameBoot/OnGameStart/OnServerStarted.
- Verified: mock test (lupa, `next` deleted) 6/6 PASS — base time unchanged with no bench; 10%
  faster with a matching adjacent bench; no bonus for mismatched-category or distant bench; instant
  actions unaffected. Shipped in test bundle (rc=0; wrap present in built Lua).
- **TODO (game test):** craft at e.g. the Carpentry bench and confirm the action bar is ~10% shorter
  than crafting the same recipe away from any bench; confirm a non-matching bench gives no speedup.

### rev 5 (2026-08-28) — trim naming/structure pass (wall trim, not window surround)
In-game review findings:
1. The "Window Surround (Short/Medium/Tall)" pieces are just straight decorative WALL TRIM at three
   heights, not window surrounds.
2. Those tiles should have ONE menu entry PER TILE, not W/N auto-orienting pairs (and the "Window
   Jamb (Tall)" entries were part of the same set).
Fix (rows 3/4/5, idx 24-28, 32-36, 40-46):
- Renamed to "Wall Trim (Short/Medium/Tall)" under a new "Wall Trim" build-menu family (dropped the
  "Window Surrounds" family and all "Window Surround"/"Window Jamb" names).
- One buildable PER TILE (single face: W/W/N/N/E per height; tall adds 45/46 W) -- no more pairing.
- OVERLAY model (kind:"overlay", needToBeAgainstWall, vinyl-trim object block) since they are
  WallOverlay tiles in the art, same as base trim -- so they sit on the wall without destroying it
  (same bug class as the earlier base-trim fix).
- Count now 34 pieces/color x 6 = 204. Regenerated clean (0 dup ids, 0 cross-piece sprite
  collisions); test bundle rc=0.
- **TODO (game test):** Wall Trim short/med/tall place as overlays without destroying the wall, in
  all orientations (W/N/E tiles); names read sensibly; no leftover "Window Surround/Jamb" entries.

### rev 6 (2026-08-28) — 4 more trim sheets (same layout)
Added four more trim sheets that share the exact 34-piece layout:
- `tt_newburbs_trim_add_01_orange` ("Orange") — the Newburbs orange. NOTE: earlier parked as
  "truncated/duplicated" — that was WRONG. The parity script read the `.tiles` PROPERTY defs (only
  32 cells tagged) but the PNG (1024x4096, 8x32) has art in all our used cells; sprites resolve by
  index regardless of whether the def tagged them, and our buildables set faces explicitly. Full
  34-piece conversion works.
- `tikitown_trim_02_yellow` ("Yellow"), `tikitown_trim_03_orange` ("Bright Orange" — brighter than
  the Newburbs orange), `tikitown_trim_04_gray` ("Gray") — all verified full parity with our layout.
- Generator change: `COLORS` -> `SHEETS` list of (full_sheet_base, color_word); `_sprite` and the
  id/translation/group tails now use the full sheet base name, so both `tt_newburbs_trim_*` and
  `tikitown_trim_*` prefixes work.
- Count now 34 pieces/sheet x 10 sheets = 340. Regenerated clean (0 dup ids, 0 cross-piece sprite
  collisions). Test bundle rc=0, 3253 total buildables.
- **TODO (game test):** the 4 new colors (Orange, Yellow, Bright Orange, Gray) show up and place
  correctly; "Bright Orange" vs "Orange" are visually distinct and both named sensibly.
- Still left for a later pass: lower-sheet tiles (idx 48-63, 69/70, 72-77, 80-82) on all sheets.

### rev 7 (2026-08-28) — wall-trim W/N merge (fix over-correction from rev 5)
rev 5 split wall trim into one-entry-per-tile, which was wrong for the W/N tiles: the "one entry
per tile" note applied to the jambs, not the plain wall trim. The W and N tiles of each wall-trim
board are the SAME piece in two orientations and must MERGE into one buildable with both faces
(engine auto-orients), like the window casing.
- Per height row (cols W,W,N,N,E): merged W[0]+N[0](+E) and W[1]+N[1] into paired buildables; the
  tall row's extra 45/46 are W-only tiles with no N partner on the sheet, so they stay single-face.
- Still OVERLAY model (sits on wall, no destroy). Wall Trim now = 2 (short) + 2 (med) + 4 (tall) = 8
  entries per sheet instead of 17.
- Count now 25 pieces/sheet x 10 = 250. Regenerated clean (0 dup ids, 0 collisions); test bundle
  rc=0.
- **TODO (game test):** Wall Trim short/med/tall each show ONE menu entry per board and auto-orient
  to the wall (W/N) correctly; overlay still doesn't destroy the wall.

### 2026-08-28: Dirkies stairs (`60_community_dirkies_stairs.json`) — NEW, not game-tested
Converted fixtures_stairs_ddd_01 (Daddy Dirkie / Melos tiles): 7 stairs, each E/W + N/S orientation
(3 step sprites each, low->high). KBW stair model: placement kind:"stairs", object isThumpable:false;
W face = vertical 3-row stack (high->low, y:-2); N face = horizontal 3-sprite row. Pillars added as a
2nd face layer (KBW stair-railing pattern).
- Layout (user walked the sheet set-by-set; E/W = left cols, N/S = right):
  1 Dark Metal:  E/W 0,1,2  / N/S 8,9,10    -- NO pillar
  2 Teal Metal:  E/W 3,4,5  / N/S 11,12,13  -- ONE post idx 30, shared by both faces
  3 Grey:        E/W 16,17,18/ N/S 24,25,26 -- TWO posts: W=38, N=46
  4 White:       E/W 19,20,21/ N/S 27,28,29 -- TWO posts: W=54, N=62
  5 Wood Blue:   E/W 32,33,34/ N/S 35,36,37 -- no pillar
  6 Wood Olive:  E/W 40,41,42/ N/S 43,44,45 -- no pillar
  7 Wood Tan:    E/W 48,49,50/ N/S 51,52,53 -- no pillar
- IMPORTANT: the BuildingMenu Daddy Dirkie addon's pillar indices are WRONG vs the art (it hardcodes
  pillar=14, but idx 14/15 are EMPTY; its wood `+6/+7` offsets point at other stairs' step tiles).
  The addon DID confirm the pillar *scheme*: metal = one post both orientations; wood helper =
  pillar + pillarNorth (two posts). Real post sprites verified by pixel inspection (tall+narrow art):
  idx 30 (slate), 38/46 (grey), 54/62 (white).
- Wired: build_community_mod.py SRC_DEFS (60_*); build_merged_test_mod.py PACK_OF "60"=Dirkies +
  generic_type Stairs branch. Generator: pz_craft_loops/dirkies_stairs.py.
- Build verified: test bundle rc=0, 3170 total, all 7 present, 0 dup ids.
- **TODO (game test):** all 7 place and climb z-levels correctly in both orientations; the 3 pillared
  ones show their post(s) correctly (teal one post both ways; grey/white a post per orientation).

### 2026-08-28: Dirkies addon gap pass — container tails + full bedroom
Audited the Daddy Dirkie BuildingMenu addon (3137091536) vs our Dirkies deliverables. Findings:
- **industry_ddd_01 idx 9 + 10**: real crate containers (.tiles: container=crate, capacity 60) we
  hadn't shipped. ADDED to `40_community_dirkies_containers.json` as "Pallet Crate Stack" / "Pallet
  Crate" (kind:object, container crate 60, crates knowledge gate).
- **furniture_storage_ddd_01 idx 32/33** ("Secret Entrance Shelf" in the addon): the tiles are
  EMPTY on the sheet (verified by crop) and there's no entrance mechanic — a dead addon reference.
  NOT shipped. (The real in-wall bookshelf at 34/35 is already shipped.)
- The industry "gap" indices 12/13/14/15/61/62/63 are paired-sprite property patches
  (BM_Utils.setOrUnsetSpriteProperties), not buildables. Nothing to add.
- NOTE: an earlier worry that our shipped industry barrels (idx 4-7) point at empty tiles was a
  FALSE ALARM — my pixel crop used a wrong grid; the .tiles def has valid props for all 64 indices
  and the game indexes by that. No bug; disregard.

### Dirkies BEDROOM (`61_community_dirkies_bedroom.json`) — NEW, not game-tested
Converted all 5 d_furniture_bedroom_0{1..5} sheets (the addon's addBedroomFurnitureToMenu). 15
pieces/sheet x 5 = **75 buildables**: 2 two-tile beds, 2 four-tile beds, nightstand, 6 dressers
(4-facing), 2 wide dressers (2-tile), bookcase, wall bookcase.
- Modelled on our TikiTown bedroom (`25_tikitown_bedroom.json`): beds kind:object multi-tile, NO
  container; dressers/bookcases object{isProp,canBePadlocked} + container{dresser 20 / shelves 40};
  nightstand simple furniture. 4-tile beds use a 2x2 face grid (matches the TikiTown "Large Fancy
  Floor Bed"). Wall bookcase = needToBeAgainstWall.
- Sheet 4's bed sprite indices differ from the others (addon i==4 conditional); encoded in
  `dirkies_bedroom.py` bed_indices().
- Generator: pz_craft_loops/dirkies_bedroom.py. Wired: build_community_mod SRC_DEFS (61_*);
  build_merged_test_mod PACK_OF "61"=Dirkies. Build verified: rc=0, 3247 total, 0 dup ids, 75
  bedroom pieces present (4-tile beds have 2x2 grids, dressers 4-facing + container, wall bookcase
  against-wall).
- **TODO (game test):** beds place with correct multi-tile footprint + orientation (esp. the 4-tile
  beds and the sheet-4 variants); dressers/bookcases store items and show right facing; wall
  bookcase sits against a wall. If a 4-tile bed's 2x2 corners look scrambled, the TL/TR/BL/BR order
  in dirkies_bedroom._bed4 is the knob to adjust.
- **REV 2 (user game test 2026-08-28): all multi-tile pieces had wrong tile placement** (floor bed
  only right in its first orientation; large beds all wrong; single-tile pieces fine). Cause: same
  addon split as the couches. Floor Bed + Floor Bed 2 are ONE 2-tile bed (idx 0-7), the two large
  beds are ONE 4-tile bed (idx 8-23), Wide Dresser 1 + 2 are ONE 2-tile wardrobe (idx 40-47; 2 was
  its rear facings). Merged: 12 pieces/sheet, **60 total**. Layouts copied verbatim from the
  in-game-confirmed TikiTown bedroom (same tile layout; rule SpriteGridPos (x,y) -> row y, col x;
  bed face = opposite of tile Facing). Sheet 4 (Weathered) is a different bed design with its own
  order -> derived from its .tiles (idx 19 typo taken as 1,0); least certain. Wardrobe gets
  container wardrobe 25. Names now by color: Cream (01), Grey (02), Oak (03), Weathered (04),
  Birch (05). Build rc=0, 3254 total. **TODO (game test):** all 4 facings of floor bed, large bed,
  wardrobe on each sheet, especially Weathered.
- **Still unimplemented from the addon (bigger jobs):** d_furniture_couches_01 (108), ramps_ddd
  (101), roofs_ddd_04 + building_menu_walls_exterior_roofs_ddd_01 (80), walls_trim_ddd_02 (24),
  furniture_more_ddd_01 (16), grime_ddd_01 (16).

### Dirkies COUCHES (`62_community_dirkies_couches.json`) — NEW, not game-tested
Converted `d_furniture_couches_01` + the corner couches on `d_location_sofaking` (the addon's
addCouchesToMenu). **22 buildables**: 9 two-tile couches + 9 armchairs + 4 corner couches.
- **Sheet geometry correction:** both sheets are **8 columns wide**, not 16. `d_furniture_couches_01`
  = 8x16 (firstId 9, 128 tiles); `d_location_sofaking` = 8x8 (firstId 10, 64 tiles). An early pass
  used a 16-wide grid and produced bogus indices (120/152/... for corners) that tripped the build's
  "tile index out of range" rotation check. Fixed — all indices now read from the pack `.tiles`.
- **Couches are ONE piece each, not two.** The addon registered 27 "objects" because its build fn
  takes only 2 facings at a time, so it split each 2-tile couch into an S/E entry and an N/W entry.
  The `.tiles` metadata (GroupName/CustomName=Couch, Facing, SpriteGridPos) shows they're one couch
  with 4 facings. We merge them: 9 couches (not 18) + 9 armchairs.
- **Facings taken from the pack, not guessed.** Armchair facing layout is NOT uniform — the Comfy +
  *_Lazy groups start at S (S,E,W,N) but the Dirk* Lazy groups start at E (E,S,W,N). Explicit S/E/W/N
  indices per armchair in `ARMCHAIR_VARIANTS`. Two-tile couch pairs derived from Facing+SpriteGridPos:
  S/N = horizontal row `[a,b]`, E/W = vertical column `[a],[b]` (see `_couch_all_pairs` derivation).
- **Corner couches (net-new).** The addon never built these (it mis-used other sofaking cells as
  kitchen counters). 4 colors: Teal 36-39, Purple 44-47, Pink 52-55, Orange 60-63; facing order
  (user-annotated art) base+0=S, +1=N, +2=E, +3=W. They let players build L- and C-shapes with the
  straight couches. Pack tags teal/purple/pink IsMoveAble + GroupName="Couch Corner" but all with
  Facing=S; orange 60-63 carry NO props. Harmless — we set all 4 faces explicitly, so the sprites
  render and the piece places without relying on the pack's (broken/absent) facing metadata. These
  show in the rotation report as "missing/duplicate Facing" (teal/purple/pink) and "not moveable"
  (orange); that's the engine auto-rotate shortcut being skipped, NOT a build failure.
- Props mirror the addon couch: object {isThumpable, canPassThrough, isCorner, dismantable}; no
  container; subcategory "Seating". Recipe: hammer + planks/nails/thread, Woodwork.
- Generator: `pz_craft_loops/dirkies_couches.py`. Wired: `build_merged_test_mod.py` PACK_OF "62"=
  Dirkies + a Couches branch in `generic_type` (Furniture sub containing couch/seat/sofa -> "Couches").
  (Not yet wired into `build_community_mod.py` SRC_DEFS — do that before a WE hand-off.)
- Build verified: merged test bundle rc=0, **3269 total** (3247 + 22), 0 dup ids; no out-of-range.
- **TODO (game test):**
  - 2-tile couches place with the right footprint and each facing's sprite pair lands correctly
    (if a facing's two tiles are swapped or the row/column is wrong, flip the pair order or the
    `_row2`/`_col2` choice in `dirkies_couches.py`).
  - armchairs rotate through all 4 facings with correct art (watch the Dirk* E-first groups).
  - corner couches: all 4 colors place and rotate S/N/E/W to the right corner; confirm they line up
    flush with the straight couches for L/C-shapes. If a corner faces the wrong way, the S/N/E/W
    index map in `CORNER_COLORS` / `_corner_couch` is the knob.

### 2026-08-28: game-test fixes (Dirkies stairs / couches / bedroom / containers)
- **Stairs: orientations were swapped** (user). The sheet's "E/W" art is the N-face stair and its
  "N/S" art the W-face stair. `dirkies_stairs.py` now puts `ns` on W and `ew` on N; each pillar
  travels with its own art. User noted this was "the main" stair issue -> others may remain.
- **Corner couches were one color late** (teal showed purple, purple pink, pink orange, orange
  nothing). Cause: `d_location_sofaking` cells are 128x256 (1792px = 7 rows), not 128x224. Fixed
  bases: Teal 28, Purple 36, Pink 44, Orange 52 (+0 S, +1 N, +2 E, +3 W). Other couches confirmed good.
- **Pallet Crate / Pallet Crate Stack** (industry_ddd_01_10 / _9) REMOVED from `40_*` (redundant tiles).
- **Reinforced counters CONFIRMED** (incl. Steel Medical Counter with Shelves (Reinforced)):
  `piece_status` marks every `*.reinforced` id Completed.
- **Bedroom single-tile renames to match the art** (ids unchanged): Small Table (58/59), Low Cabinet
  (62/63), Dresser with Mirror (24-27), Wide Dresser (28-31), Small Chest of Drawers (32-35), Bedside
  Table (36-39), Low Shelf (52-55), Wall Shelf (56/57); Bookcase unchanged. Containers unchanged.
- **Newburbs trim (TikiTown 35) marked Completed** (user tested, no issues).
- Build: rc=0, 3252 total.

### 2026-08-28: TikiTown furniture_storage_tterika_02 (`zomboid/tikitown/36_tikitown_tterika_storage.json`) — NEW, not game-tested
- 12 single-tile metal containers, 2 per row, each 4 sprites in **S,E,N,W** order (user; checked
  against art extracted from `tikitown_tiles.pack` into `_cache_tt02`). The pack's Facing metadata
  for idx 24-47 (colored lockers) says E,S,W,N — wrong vs the art; we follow the art.
- Pieces: Small Grey Metal Cabinet (0, metal_shelves 40), Small Black Footlocker (4, locker 10),
  Green Military Locker (8), Small Olive Metal Cabinet (12), Grey Military Locker (16), Small Steel
  Metal Cabinet (20), Pink/Red/Grey/Green/Orange/Purple Locker (24-44). Capacity from the tile where
  set, else 40 (our locker convention). Metal recipe = our Dirkies metal lockers.
- Freestanding (`kind:object`), even though the pack tags idx 12-47 `MoveType=WallObject`.
- Possible side effect: because the pack's own Facing is wrong for 24-47, picking one of those
  lockers up and re-placing it from inventory may rotate to the wrong art (engine rotation uses
  the tile metadata). KBW building is unaffected.
- Generator `pz_craft_loops/tikitown_tterika_storage.py`; wired in `build_merged_test_mod.py`
  (TT_FILES + TT_PACK_OF "36") and `build_tikitown_mod.py` SRC_FILES. Build rc=0, 3264 total.
- Same session: Dirkies Bedside Table -> sidetable 10, Low Shelf -> shelves 20 (Shelving).
- **Reinforced versions added for all 12 tterika_02 containers** (user): `counter_variants.py` now
  also accepts any container tagged `"reinforce"` (opt-in; tterika generator sets it). Same as
  the counters: `<id>.reinforced`, military-crate cost, capacity 100, same container type, name
  "<name> (Reinforced)", tooltip "Reinforced metal storage with a large capacity." Base tterika
  pieces now get Locker / Chest tooltips (were "laboratory furniture" / "decoration"). The tterika
  prefix is in `INPROGRESS_ID_PREFIXES` so the blanket "*.reinforced = Completed" rule doesn't
  mark these untested variants done. Build rc=0, 3276 total (24 tterika pieces, In Progress).

### 2026-08-28: game test — Dirkies beds, couches, furniture, storage CONFIRMED
- Sheets 61 (bedroom) and 62 (couches) added to COMPLETED_SHEETS.
- **Exception — the 4 sofaking corner couches are NOT shipping as-is.** Forced In Progress via
  INPROGRESS_ID_PREFIXES (`community.dirkies.couches.corner_`). Keep them out of any shipping
  build (62 isn't in build_community_mod SRC_DEFS yet; when wiring it, drop corner_*).
- **TODO (design + build): custom L-shaped corner couches**, one per corner color. Each = 3 tiles:
  the 2 tiles of the same-color Comfy couch as the two ends + the sofaking corner tile at the
  bend. No straight middle-couch tile exists, so 3 tiles is the max per L. Open points before
  building: which Comfy couch matches each corner color (Teal/Purple/Pink/Orange vs Blue/Purple/
  Pink Comfy + the Dirk* variants — orange has no obvious Comfy match), and which of the couch's
  two tiles sits at each end per facing (multi-tile face with an L footprint; KBW grid needs an
  empty cell in the 2x2 — check KBW supports null cells, else a 2-layer/2-piece approach).

### 2026-08-28: fridge / freezer tiers CONFIRMED; TEST fridge dropped
- The 59 fridge/freezer tier pieces (align_appliance_costs.build_fridge_defs) moved from
  "Community - In Progress / Test - Fridges" to "Community - Completed / Fridges" (user).
- The `kbwcb.test.fridge_100` TEST Refrigerator experiment is removed from the test bundle
  (`_test_fridge_100()` deleted). container_caps / kbwcbContainerCapacity Lua left in place.
- Build rc=0, 3275 total.
- **tterika_02 base cost lowered to HALF the reinforced (military crate) cost** (user): base was
  kbwve.extended.metal (3 sheet metal, 2 pipe, 4 screws + screwdriver) = more metal than the
  100-capacity reinforced version. Base now: welding mask, 1 small sheet metal, 1 sheet metal,
  1 scrap metal, torch 2 uses, rods 2 uses (crate halved, rounded up, min 1; scrap stays 1).
  Computed from the crate definition (`_half_crate_inputs`) so it tracks the crate. Skill
  Welding 4 + Projects in Metal knowledge unchanged; reinforced stays crate cost, Welding 7.

### 2026-08-28: fridge / freezer KBW parts halved
- KBW-only parts spawn too rarely for our tiers (user). In `align_appliance_costs.build_fridge_defs`
  (the 59 fridge / freezer pieces only) these are halved, **round down, min 1**:
  InsulationFoam, PlasticSheet, RubberSeal, RefrigerantBottle (uses). Metal costs, ThinCopperPipe
  (metal) and the compressor (already 1) unchanged. Ice machines (`build_freezer_tiers`, shipped
  in WE) NOT changed. Examples: single 60-tier foam/plastic/seal 3->1, refrigerant 3->1;
  100-tier unit refrigerant 9->4; 100 shell foam/plastic/seal 8/6/6->4/3/3.
- Rounding rule for both halvings (this + the tterika base cost) = round down, min 1. Tterika base
  unchanged by that (crate amounts 2/2/1/4/4 -> 1/1/1/2/2).

### 2026-08-28: picked-up tterika locker can't be re-placed (red shadow) — fix awaiting test
- Cause (vanilla ISMoveableSpriteProps.canPlaceMoveableInternal): a picked-up piece is placed with
  the TILE's data, not our KBW def. Drazion tags tterika_02 idx 12-15 + 20-47 `MoveType=WallObject`
  -> vanilla requires a wall on the Facing side; and idx 24-47 Facing is E,S,W,N vs the S,E,N,W art,
  so even next to a wall the side is wrong. Console showed the user's test piece = Green Locker (36).
- Fix (`rotation_fix.PROP_OVERRIDES`, set at runtime by the existing rotation Lua via props:set):
  those tiles get `MoveType=Object` (freestanding, like our build) and Facing = art order; their
  rotation offsets are recomputed from the corrected Facing (engine's were built from the wrong
  one). Only emitted into a build's rotation Lua when that build uses the sprites (test bundle +
  TikiTown builder; not the Community build). 32 sprites.
- Side effect: map-placed copies of these lockers become freestanding moveables too (they were
  wall objects in Drazion's data). Check in game: pick up + place each kind, rotate with R.

### 2026-08-28: ice machines + copper pipe halved too
- `ThinCopperPipe` added to HALVE_KBW_PARTS (KBW item, not vanilla metal — user).
- Ice machines (`build_freezer_tiers`, 57_community_tk_kitchen_misc.json — a WE-shipped file)
  now halve the same KBW parts: 65/100 shells + units, and the base 30 gets its own group
  `kbwcb.appliance.freezer30` (KBW chest-freezer recipe, KBW parts halved) instead of KBW VE's
  `kbwve.appliance.refrigerator`. Round down, min 1. Needs the WE hand-off when shipped.
- **Retest result (user): still needed a wall on place + snapped to the wrong side.** Console showed
  the rotation Lua DID run (416 sprites). Cause: B42 `props:set(key, value)` does not replace a
  key the tile already has, so MoveType / Facing (and the engine-generated offsets on 24-47) kept
  Drazion's values; only NEW keys (our counters' offsets) ever took. Vanilla re-reads props on
  every `ISMoveableSpriteProps.new` (no cache).
- Fix v2 (rotation Lua, both test bundle + TikiTown builder): (1) unset the key before set;
  (2) wrap `ISMoveableSpriteProps.new` (OnGameStart / OnServerStarted) so sprites in our table
  with a MoveType get type / facing / N,S,E,W offsets forced from the table — placement no longer
  depends on the property edit. Tested against lupa mocks (next=nil, set-doesn't-replace mock):
  36 -> Object/S/N2 E1 W3, 39 -> Object/W, other sprites untouched. NOT yet tested in game.
  Console should now also print "[KBWCommunity] Rotation: moveable placement overrides active".

### 2026-08-28: tterika stacking + renames; stair pillars fixed (awaiting test)
- Renames (user): idx 12 "Small Olive Military Locker", 20 "Small Steel Military Locker", 16 "Steel
  Military Locker" (was Grey). idx 0 "Small Grey Metal Cabinet" stays.
- Stacking: vanilla/KBW/WE stacking all reads the TILE (IsStackable + IsTable + Surface; WE
  Placement hands stack checks to ISMoveableSpriteProps:canPlaceMoveable). `kbw_tilepatch` now has
  an opt-in TikiTown section (`tikitown=True` on write_community_tilepatch / write_removal_lua;
  test bundle only, it loads after tikitown_tiles):
  - footlocker 4-7: +IsStackable +IsTable, IsTableTop removed at runtime (vanilla never stacks
    onto an IsTableTop square), Surface stays 15 -> 6 high (5*15+15=90; 7th = 105 > 96).
  - small cabinet / small military lockers 0-3, 12-15, 20-23: +IsStackable +IsTable, Surface 48 -> 2
    high (48+48=96; 3rd = 144).
  - The locker MoveType=Object / Facing fix is now ALSO in the .patch.tiles (patch merges DO
    override existing values — the proven path); the runtime wrapper stays as a fallback.
    Single source: kbw_tilepatch.TT_LOCKER_OVERRIDES (rotation_fix.PROP_OVERRIDES points at it).
  - Not yet in the TikiTown / WE shipping build (build_tikitown_mod writes no tile patch) —
    needs a patch + tiledef there before these ship.
- Stair pillars: KBW Matrix.expandFace defaults a layer's z to (layerIndex - 1), so our pillar
  (layer 2) was one floor UP (and on the W face over the LOW step). Now z=0 on the highest step's
  square (W: y -2; N: x 0, y 0). Stair step tiles confirmed correct; the pillar is the only open
  stair issue.
- **Retest (user, 2026-08-28): locker pick-up/place FIXED.** Newly built + picked-up lockers place
  freestanding and rotate through all 4 facings. An OLD inventory copy (picked up before the fix)
  only offered E/W — leftover from the earlier test, not a current bug. Watch for it only if old
  saves carry pre-fix picked-up lockers.

### 2026-08-28: all TikiTown In Progress -> Completed (user)
- TT_COMPLETED += "30" (shelving), "36" (tterika storage, incl. its 12 reinforced variants);
  tterika prefix removed from INPROGRESS_ID_PREFIXES. TikiTown now 1383 Completed, 0 In Progress.
  Only Dirkies stairs (7) + corner couches (4) remain In Progress. Build rc=0, 3275.

### 2026-08-28: stairs game test — wood stairs CONFIRMED; post indices fixed (awaiting test)
- Wooden stairs (blue / olive / tan trim) confirmed -> COMPLETED_ID_PREFIXES `community.dirkies.stairs.wood_`.
- Grey + white had no pillar, teal showed white's: the first post pass read the sheet on a
  128x128 grid; it is 8x8 tiles of 128x256 (same mistake as the sofaking corners). Real posts:
  teal 14 (both orientations — the addon's pillar=14 was right), grey 22 / 23, white 30 / 31
  (pillar / pillarNorth, the addon's +6/+7). 38/46/54/62 were empty cells.
- Position: KBW builds every stair cell where our geometry puts it (BuildRecipeCode.stairs
  OnCreate works per cell), and vanilla AddStairs (javap) puts the pillar under the TOP step's
  x,y (on the floors below, only over open air). Our pillar layer is on the top step's square for
  both faces (z 0). Teal N/S showing the post on the middle step is most likely the wrong post
  art (30 is white's E/W post, drawn offset for another stair) — re-check with post 14.
- Dark metal / teal / grey / white stairs stay In Progress (8 Dirkies In Progress incl. 4 corners).
- **Pillar top poking out through the top step (user screenshot vs vanilla).** Not an opacity
  flag: objects on one square draw in the order they were added, and our pillar was the 2nd layer
  (added after the step, so drawn over it). Vanilla adds the post first and the top step covers its
  top. `dirkies_stairs.py` now lists the pillar layer BEFORE the stair layer, both z 0. Unverified:
  that KBW adds cells in layer order (could not confirm from its Lua). If the post still shows over
  the step, the next lever is a sprite-level change (crop the post top) or a runtime reorder.

### 2026-08-28: stairs round 3 (user) — dark metal CONFIRMED; teal post position + grey/white clipping open
- Dark metal stairs confirmed (COMPLETED_ID_PREFIXES). Still open: teal post sits under the MIDDLE
  step (should be the top tile); grey + white posts still clip into the top step.
- How the original addon / vanilla does it (javap of IsoGridSquare.AddStairs + ISWoodenStairs):
  the addon only calls vanilla `ISWoodenStairs:new(..., pillar, pillarNorth)`; there is no custom
  pillar logic. Vanilla builds the 3 steps as 3 stair objects (level 0/1/2) and the pillar sprite
  (arg 4) is used in exactly ONE place: on level 2 (the top step), a post object is added on the
  square(s) BELOW it (z-1, z-2 ... until a solid floor), and only when that step's square has no
  solid floor of its own. It is drawn as a lower-floor object, so the engine renders it BEHIND the
  top step — that is why vanilla posts never poke through. Pillar art is therefore drawn for a
  tile one floor down. Metal stairs in the addon pass the same post for both orientations
  (teal: pillar = pillarNorth = 14).
- Ours puts the post on the same floor and square as the top step (z 0), so the art is not offset
  like vanilla's and nothing orders it behind the step. We cannot use z -1 at ground level (no
  square below). Options noted for the user: (1) cropped post variants in our own tileset so the
  top ends under the step (same method as the Fears / case mirrors); (2) mirrored copy of post 14
  for the teal N/S face (single post art is drawn for one orientation).
- **Decision (user): pillars removed from all stairs.** teal / grey / white now have no post, like
  the confirmed dark metal and wood stairs. Step tiles were already confirmed for all 7, so all 7
  stairs are Completed. Post art (teal 14, grey 22/23, white 30/31) is not used; revisit only if the
  cropped / mirrored post idea is wanted later.

### 2026-08-28: custom L-shaped corner couches (`dirkies_couches.py`) — NEW, not game-tested
- Per user: corner + right piece + left piece = L with equal sides, 3 tiles. Built for the colors
  that have a matching straight couch: **Teal** (Blue Comfy), **Purple** (Purple Comfy), **Pink**
  (Pink Comfy). **Orange has no matching straight couch** (no orange couch tiles), so no orange L.
- Shape (default, world grid, corner at the NW cell): corner, right piece to its east, left piece
  to its south. "Right"/"left" = the on-screen right/left end tiles of the straight couch.
- All 4 rotations designed from an iso composite render (`_lcomp`, not kept): each rotation has
  exactly one sofaking corner variant that forms a clean L: rot0 (corner NW) S(+0), rot1 (NE) W(+3),
  rot2 (SE) N(+1), rot3 (SW) E(+2). Game rotate order W,N,E,S = rot0..rot3 (clockwise).
  Arm tiles: always the end tile pointing away from the corner (see the table in the generator).
- The corner is the anchor cell (dx 0, dy 0) in every face via layer x/y offsets; the empty 2x2 cell
  is KBW's `false` token (Matrix.cellFromToken). Cost 11 planks / 11 nails / 8 thread (corner 5 +
  two ends 3+3), Woodwork 4. Subcategory Seating -> "Couches". Forced In Progress.
- The 4 standalone sofaking corners are still in the file and still In Progress: remove them once
  the L couches are confirmed (they were never meant to ship).
- **TODO (game test):** each L places in all 4 rotations with the corner at the cursor and the
  arms in the right directions; check there is no tile from the empty cell blocking placement;
  check armrest/back sides line up on every rotation (swap corner variants in `_l_faces` if one is
  off); decide about orange (e.g. derive ends from another color, or skip).

## 2026-08-28 - Orange L couch + teal depth-map guess
- Teal oddity: the only difference found vs purple/pink is DEPTH_d_location_sofaking.png. Cells 28-31 (teal) and 52-55 (orange) carry depth data; 36-39 (purple) and 44-47 (pink) carry none. HYPOTHESIS, unconfirmed in game. Fix: test bundle ships an override depth map (common/media/depthmaps) with those cells cleared (`kbw_tilepatch.write_sofaking_depth_override`).
- Orange L couch (`community.dirkies.couches.lcouch_orange`): no orange straight couch exists, so Pink Comfy tiles (couches_01_48..55) are recoloured to orange. Mapping learned from pink vs orange corner pixel pairs (mean abs RGB error 0.54 on the corner pair). New pack/tiledef `KBWCommunityOrangeCouch` / `kbwcommunity_orangecouch` id 8178 (test bundle only; needs WE hand-off if shipped).
- L couches stay In Progress. After confirmation, remove the 4 standalone `corner_*` buildables.

## 2026-08-28 - Multi-part pieces pick up / smash as one (built, NOT game-tested)
- Bug: L-couch end pieces could not be picked up and ghosted as the full 2-tile couch (their tiles belong to the Comfy couch's 2-tile sprite grid, but only one half is built). Beds: picking up one tile left the others.
- Cause: KBW places each tile as its own object (modData.KBW.groupId/partIndex/partCount). Vanilla only moves tiles together when the sprites share a tile-property sprite grid.
- Fix 1: L-couch ends now come from a generated single-tile tileset `KBWCommunityLCouch` (tiledef `kbwcommunity_lcouch` id 8178, replaces the short-lived KBWCommunityOrangeCouch). 32 tiles = Teal 0-7, Purple 8-15, Pink 16-23, Orange 24-31 (recoloured pink). SpriteGridPos removed, unique GroupName per tile. Corner tiles unchanged.
- Fix 2: new shared Lua `KBWCommunity_MultiPart.lua` (container_caps.py): wraps ISMoveableSpriteProps:canPickUpMoveable/pickUpMoveable (when the clicked tile has no working sprite grid, all tiles of the KBW group are picked up; part items drop on the floor like vanilla multi-sprite) and ISDestroyStuffAction:complete (sledgehammer removes the whole group). Written to the test bundle and build_community_mod.py; NOT yet in the TikiTown builder (KBWTikiTown_* files) - add before shipping TikiTown beds etc.
- WE hand-off: new file KBWCommunity_MultiPart.lua + new pack/tiledef.
