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

## NEXT: two-stage builds for the 65 / 100 ice machines (decided 2026-11-02)
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
