# Hand-off `handoff-2026-11-10-detailing-sinks`

Compare: `we-baseline-2026-11-10...handoff-2026-11-10-detailing-sinks`. The baseline is your merged
WE (installed 2026-11-10, Steam manifest 8104864525325359112), so the diff only shows what's new
since your merge. The previous notes are archived in `notes/HANDOFF_NOTES_2026-11-08.md`.

**Not in this hand-off (held for your MP review, as you asked):** the Electrical Cabinet Generator and
the workbench built-in tools. We stopped building them for WE: no definition, items, icons, Rotate
Lua, bench Lua or labels. Your merged file 38 / file 56 are unchanged apart from the md5 reorder.

**Your consolidation is respected.** Our builds no longer produce the per-submod OverlayGuard,
MultiPart, Pickup, StageInfo or TikiTown TableTop Lua. Your `WorldEssentialsBuildworks*.lua` and
`KBWCommunity_TableTop.lua` are untouched, and so are your `mod.info` files. The translation keys you
added (`Tooltip_KBWCB_WallCorner`, `Tooltip_KBWCB_WallWindow` in TikiTown) are kept.

**mod.info:** no new lines needed.

**Spray Paint matches your merge.** Loot distribution only; we dropped our item weight override
(follow-up tag `handoff-2026-11-10-spraypaint-match`).

## 1. TikiTown: wall paint, cladding and trim (NEW files 43 / 44)

- `43_tikitown_wall_paint_cladding.json` (860): the four tterika detailing sheets (interior paint /
  wallpaper, exterior brick / stone / wood / siding). Each colour row has 10 pieces in one card:
  - lower panel, its corner and end cap
  - top band, its corner and end cap
  - window and door-frame panels
  - the two door-frame edge halves

  Category "Wall Paint & Cladding". Names come from the art ("Teal Paint Lower Panel",
  "Red Brick Cladding ...").
- `44_tikitown_wall_trim.json` (231): the two tterika trim sheets (baseboards, chair rails, crown,
  wainscot panels, corner trim). Category "Wall Trim".
- Costs:
  - paint: paintbrush + the nearest vanilla paint
  - wallpaper: a wallpaper roll
  - cladding: the matching TikiTown wall recipe, scaled to the piece
  - trim: 1/4 of the wood wall recipe
- Tiles:
  - The paint/cladding sheets carry `WallOverlay` but mostly no `attached*` facing, so KBW would
    place them as loose objects. They use OUR copies with the facing added by position, in new
    tilesets `KBWTikiTownDetail1..3`.
  - Those tilesets go into the existing `kbwtikitown_walloverlays` tiles file and pack; existing
    sprite names are unchanged.
  - The trim sheets already carry facings, so the pack's own tiles are used.
- Confirmed in game (single player).

## 2. TikiTown: overlay corners are dismantlable thumpables (file 39, also used by 43 / 44)

- Corner pieces now build with `canPassThrough: false` (`isThumpable` stays false), so KBW makes
  them an IsoThumpable instead of a prop.
- Why: inside a PhunInteriors room the sledgehammer is blocked, and vanilla Dismantle only works on a
  thumpable, so corners couldn't be removed there.
- A corner only builds where both walls exist, so it blocks nothing new. End caps and pillars stay props.

## 3. TikiTown: depth for our copied tiles (NEW `common/media/` folder)

- `common/media/tileDepthTextureAssignments.txt` gives each copied tile vanilla's own wall preset
  for its role (W face `preset_depthmaps_01_4`, N `_5`, corner `_6`, end cap `_7`), the same
  presets vanilla uses for `walls_interior_detailing_01`. Without it the copies had no depth at all:
  Drazion's pack doesn't assign the lower-wall block we copy, and the copies have new names.
- `common/media/tileGeometry.txt` is the minimal VERSION 2 stub the engine needs before it reads a
  mod's `common/media`.

## 4. Community: hand-pump sinks (NEW file 71)

- The five Knox VE counter-top sinks (Beige, White, Industrial, Dark Industrial, Chrome) as
  "<Sink> (Hand Pump)". They give water like your Large Water Tank: no plumbing or mains.
  One card, "Hand Pump Sinks", under Appliances / Bathroom Fixtures.
- Stage `"well": true` (Knox's well system), so the server's Knox well settings apply. In the
  default mode the water is endless.
- Cost: your Large Water Tank recipe (`worldessentials.kbw.camping_01_64`).
- Tiles: our copies of `fixtures_sinks_01` 0-11 / 16-23 in the ice-shell tileset at fixed slots
  48-67 (water 999999, no `waterPiped`, vanilla's own depth). Vanilla sinks and map sinks are
  untouched.
- Confirmed in game (single player).

## 5. Reinforced bookshelves (capacity 100, military-crate cost; same rule as the counters)

- TikiTown (5): In-Wall Bookshelf, Tall Bookshelf (Walnut, Oak, Charcoal, White).
- Community (14):
  - In-Wall Bookshelf, two Bookstore Shelves, Store Bookshelf
  - five Bookcases and their five in-wall Wall Shelves

  The secret-entrance bookshelves are doors, so they're excluded.

## 6. Community: "Grey" -> "Gray" (vanilla spelling, names only)

## 7. All definition files are written in md5(id) order (big but data-neutral diff)

- KBW's `Registry:list()` uses Kahlua's recursive quicksort. With 43/44 added, the files as written
  would have reached depth 472 in the WE layout. That is the same "Stack overflow" in
  `partition_comp` that stopped KBW loading at 482 on 2026-11-08.
- With every file md5-ordered the depth is 20-85, about what KBW + VE produce alone (83). It stays low
  if any file is dropped (26), in random load orders (37) and at twice the content (27).
- Menu order is unchanged.

## For the KBW dev (FYI)

- `notes/DEV_BUG_REPORT_attached_sprite_redraw.md`:
  - Wall-overlay sprites attached by KBW don't appear, or draw in the wrong order, until the area
    reloads. `AttachedSprites.attach` / `remove` never call `invalidateRenderChunkLevel`.
  - This affects file 39 panels and 43/44. The pieces are built and saved; leaving the area and
    coming back shows them.

## Test status

- Confirmed in game (single player, test bundle):
  - files 43/44
  - corner thumpables
  - hand-pump sinks
  - Gray names
- Built and checked only:
  - the reinforced bookshelves, apart from the shared counter rule
  - the md5 reorder (simulated)
- Not tested: multiplayer.
- Known: the KBW redraw issue above.

---

# Hand-off 2026-11-12 (tag handoff-2026-11-12-ladders-tvs)

Compare: https://github.com/AvaliraL/pz-buildworks/compare/we-baseline-2026-11-10...handoff-2026-11-12-ladders-tvs

## 8. Climbable ladders (B42 ladder mechanic). NEW TikiTown file 45, NEW Community file 72

- **How the game does it:** everything runs off the tile flags `ladderN/S/E/W`. The Java code handles the menu option ("Climb Ladder" / "Climb Down Ladder"), the animation and the sounds, so there is no Lua.
- **TikiTown `45_tikitown_ladders.json`:** "Rusted Iron Ladder", faces W/N.
  - Drazion's tterika sewer ladder (`location_sewer_tterika_01_0/1`) uses the old sheet-rope flags (`climbSheetW/N`).
  - It is built from our copies `KBWTikiTownLadders_0/1`. These are in the existing `KBWTikiTownWallOverlays` pack and in `kbwtikitown_walloverlays.tiles`, appended last.
  - The copies swap the sheet-rope flags for `ladderW/ladderN` + `BlocksPlacement` + `forceFade`, and drop the moveable keys.
  - Depth = vanilla's sewer ladder (`location_sewer_01_32/33`) in `common/media/tileDepthTextureAssignments.txt`.
  - The pack tiles are unchanged.
- **Community `72_kbwcb_ladders.json`:** one "Ladders" card with Wooden Ladder, Rusted Metal Ladder and Steel Ladder.
  - Sprites: the vanilla `carpentry_02_84-87` and `industry_railroad_05_20/21/56/57` and `_36/37/58/59`. Nothing built these before.
  - These are vanilla tiles, so no tile work was needed.
- **Placement and cost:**
  - Stairs / Ladders. Object block = WE's Sewer Ladders.
  - `requiresFloor: false`, so a second ladder can stand over the open square above the first.
  - Metal cost = WE Sewer Ladders - Style 2 (read from WE). Wood = hammer + saw, 3 planks, 6 nails, Woodwork 3.
  - WE's landing-floor callback is not used.
- **New tooltip key:** `Tooltip_KBWCB_Ladder`.
- **Test status:** climbing CONFIRMED in game (single player, test bundle, 2026-11-12). All ladders work: TikiTown Rusted Iron Ladder plus the Wooden, Rusted Metal and Steel Ladders.
- **Wall requirement (added after that test; tested against mocks only, NOT yet in game):**
  - Every ladder in files 45 and 72 now needs a wall. Its stage `callbacks.onIsValid` is `KBWLadderGuard.OnIsValid`.
  - The check reads the ladder's wall edge from its tile (`ladderW/N/E/S`, `attached*` as fallback). That edge needs a wall, window wall or door wall. E/S edges = the next square's W/N wall.
  - Ladder tops use `KBWLadderGuard.OnIsValidTop`: a ladder must be on the square directly below.
  - KBW's own `needToBeAgainstWall` wasn't usable: for these non-WallObject tiles it only looks at the square's own W/N wall, so every E/S ladder would be refused.
- **NEW Lua, one per submod:** `media/lua/shared/KBWCommunity_LadderGuard.lua` and `KBWTikiTown_LadderGuard.lua`. They have the same code and define the global once. They are generated by `ladders.py` and are not WE-owned files.

## 9. Community: Dirkies decor-house pieces. NEW file 63, more in file 72

All tiles come from `edit_ddd_RUS_decor_house_01`.

- **Iron Ladder (file 72, "Ladders" card, level 4):** tiles 16-19 are one ladder shown in its 4 wall orientations.
  - The pack tiles use the sheet-rope flags (`climbSheet*`). Our copies use the ladder flags `ladderW/N/S/E`, plus attached, Facing and Steel.
- **Iron Ladder Top (file 72, level 5):** tiles 96-99, a decoration for the open square above a ladder.
  - The copies drop the pack's `climbSheetTop*` flags and `BlocksPlacement`. The piece is walk-through and not climbable.
  - Pack tile 99 is flagged W but drawn E, so the copy uses E.
- **Blue / Green Metal Drawer Cabinet (file 63):** pack tiles 0-3 / 8-11, used as they are.
  - KBW keeps the tile's container type, which is the pack's `postbox` (capacity 20).
- **Red Wall Cabinet (file 63):** tiles 100-103.
  - On the pack these are a free-standing solid block with no container.
  - Our copies are `MoveType=WallObject` on their wall edge and not solid, so the cabinet can hang over counters or fridges. Storage comes from the definition: counter, 20.
  - Placement uses `needToBeAgainstWall`.
- **Where the copies live:** `KBWCommunityIceShell_72..83`, after the pump sinks. That means no new pack, tiledef or mod.info line. Depth uses the Community pack's own depth cells for the source tiles.
- **Cost:** metal pieces cost the same as the Dirkies Blue Rolling Tool Cabinet. The ladder top is cheap (1 metal bar, MetalWelding 2).
- **Tooltip key:** new `Tooltip_KBWCB_LadderTop`.
- **Test status:** Iron Ladder + Iron Ladder Top CONFIRMED in game (2026-11-12). Drawer cabinets and Red Wall Cabinet: built and checked only.

## 10. Community: Caged Ladder (file 72, own "Caged Ladder" card)

- **Source:** Dirkies `edit_ddd_RUS_industry_crane_01` tiles 72-77. There are three pieces, each on the W and N walls (the pack has no S/E art):
  - bottom 72/77
  - middle 73/76
  - top 74/75
- **Bottom and Middle** are climbable.
  - The pack uses `climbSheetW/N` + `solidtrans`. Our copies use `ladderW/N` and are not solid, like vanilla ladders.
  - Stack Middle pieces for more floors.
- **Top** is the cage ring for the open square above the last ladder. It is a decoration: walk-through, not climbable.
- **Copies:** `KBWCommunityIceShell_84..89`, with depth from the pack's own `DEPTH_edit_ddd_RUS_industry_crane_01.png`.
  - `kbw_tilepatch.DECOR_COPIES` now lists every decor copy (decor house + crane) in index order.
- **Cost:** Bottom and Middle = WE Sewer Ladders cost. Top = ladder-top cost.
- **Test status:** CONFIRMED in game (single player, test bundle, 2026-11-12). Tested over several floors: climbing up and down, stacked Middles, and the Top ring.

## 11. Community: Dirkies window decor (NEW file 64, 26 pieces)

All pieces come from `fixtures_details_ddd_01`, tiles 0-47.

- **Exterior window trim (tiles 0-31):** 4 cards (Arched, Round-Top, Corniced, Ornate Header and Sill), each in White / Gray / Charcoal / Terracotta. W and N facings.
  - The pack tiles are `MoveType=WindowObject`, which KBW's native-type detection builds as a curtain.
  - Our copies `KBWCommunityIceShell_90..121` are plain wall overlays: `WallOverlay` + `attachedW/N`, no MoveType. They are placed with `kind: overlay` + `needToBeAgainstWall`, like files 43/44.
  - Which window each style matches is unknown, so check the fit in game.
- **Window Planters (tiles 32-39):** one card with Empty, Shrubs, Ivy and Potted Plants. These are pack tiles (`WallObject` + attached) placed against a wall. They are not solid.
  - `requiresFloor: false` so they can hang on upper floors.
- **Potted Plants (tiles 40-47):** one card.
  - Marigold Pot and Pink Flower Basket have W/N facings.
  - Tiles 42-45 are four different plants with one facing each. The pack pairs them as two items, but the art differs.
  - All are walk-through floor decorations.
- **Costs:**
  - Trim: hammer, 2 planks, 2 nails, Woodwork 2.
  - Planters: hammer, 2 planks, 4 nails (+2 dirt-bag uses when planted).
  - Pots: 1 clay pot + 1 dirt-bag use.
- **New tooltip keys:** `Tooltip_KBWCB_WindowTrim`, `_WindowPlanter`, `_PottedPlant`.
- **Known:** overlays are subject to the KBW attached-sprite redraw bug.
- **Duplicate sheet:** Drazion's `tikitown_walls_details_04` is the same art as `fixtures_details_ddd_01` (tiles 0-55 pixel-identical). Only the Community copy is built. The TikiTown twin is deliberately skipped to avoid duplicate menu entries.
- **Test status:** built and checked only.

## 12. Community: rest of the Dirkies medical sheet (NEW file 65) + reinforced default

**Source:** `location_community_medical_ddd_01`. File 40 already covered 8-13, 16-19 and 28-31.

**Pieces:**
- **Teal / Red Medical Locker (0-3 / 4-7):** one locker storage, 40 (Reinforced 100). The 4-slot idea was dropped by the user: it would need a new multi-container mechanism.
- **Hospital Push Cart (14-15):** shelves 20.
- **Lab Specimen Cabinet (36-37):** medicine 20.
- **Large Industrial Sinks card (20-23)**, four versions, all with counter storage underneath:
  - Plumbed: KBW VE Industrial Sink recipe, 20.
  - Reinforced: crate cost, 100.
  - Hand Pump: our water copies `KBWCommunityIceShell_122..125`, `well: true`, WE Large Water Tank cost, 20.
  - Hand Pump, Reinforced: crate + tank cost added together, 100.
- **Wheelchair (24-27):** our chair copies `KBWCommunityIceShell_126..129` (`bed` + `chair<dir>` + `BedType`, like vanilla chairs) so Rest sits you in it.
  - NEW `common/media/seating.txt` in the Community submod, with the pack's own seat positions re-keyed to the copies.
- **Lab Equipment card:**
  - Lab Centrifuge (32-33) and Lab Analyzer (34-35): walk-through decorations.
  - MRI Scanner (42-47): one 2x3 piece, single orientation. Layout read from the art: rows `[43,45] [42,46] [44,47]`.

**Reinforced by default (new rule):** every new container is tagged `reinforce`, so it also gets a "(Reinforced)" version (crate cost, 100).
- Applied here and to file 63 (both drawer cabinets, the red wall cabinet).

**New tooltip keys:** `Tooltip_KBWCB_StorageSink*`, `_PumpStorageSink*`, `_Chair`, `_MedicalEquipment`.

**Test status:** built and checked only.

## 13. TikiTown: rest of tikitown-props-14 (file 38, +4 pieces)

These tiles sit at the bottom of the sheet, past a large empty gap, and were missed the first time.

- **Floor Bird Cage (85/86 + 88/89):** 2 tiles, 2 facings.
  - E = 86 over 85 (runs N-S).
  - S = 88 beside 89 (runs E-W).
  - The pack has no SpriteGridPos, so the joins were composited from the art.
- **Reptile Terrarium (90-93):** 4 facings, table-top. The pack tile's `lightswitch` + `LightRadius` make it a switchable light.
- **Wire Pet Cage (pack "Possum Cage"):** 2 tiles, 1 facing (95 over 94).
- **Mahjong Game (104/105):** 2 facings, table-top.
- **Costs:** first pass.
- **Test bundle:** today's pieces are forced In Progress (`INPROGRESS_ID_PREFIXES`). This includes their reinforced variants, which the `.reinforced` = Completed rule would otherwise have marked done.
- **Test status:** built and checked only.

## 14. TikiTown: Barrel Planters (NEW file 46)

- **Source:** `vegetation_ornamental_tterika_01`, the whole sheet: 8 plants in small wooden barrels, all in one "Barrel Planters" card.
- **Pieces:** White / Pink / Red / Yellow Rose, plus four bushes named from the art: Purple, Yellow Flowering, Light Green, Dark Green.
- **Tiles:** pack tiles as they are. One sprite each, since the barrels are round and need no rotation. They are walk-through, matching the tile (no solid flags).
- **Cost:** hammer, 3 planks, 4 nails, 2 dirt-bag uses, Woodwork 2.
- **New tooltip key:** `Tooltip_KBWCB_BarrelPlanter`.
- **Test status:** built and checked only.

## 15. Fixes after the first in-game pass (2026-11-12)

- **Table-top height ("floats at counter height on the floor"):** the fix is the sprite list in WE's own `KBWCommunity_TableTop.lua`.
  - **WE-OWNED FILE CHANGED** in our work copy: `World Essentials (base, our files only)/42/media/lua/shared/KBWCommunity_TableTop.lua`. 12 new `SPRITES` lines; nothing else touched.
  - Added sprites:
    - `tikitown-props-14_90..93` (terrarium) and `_104/105` (Mahjong): these have the pack's table-top flags.
    - `KBWCommunityIceShell_130..135`: new copies of the medical centrifuge / analyzer / specimen cabinet (32-37). Their art is drawn at counter height but the pack gives no table-top flags, so the copies get the desk mic's `IsTableTop` + `IsSurfaceOffset` + `Surface=29`.
  - From now on, every new table-top piece goes on that list (`kbw_tilepatch.sync_we_tabletop_sprites`, run by the Community builder).
- **Blue / Green Metal Drawer Cabinets:** the pack draws them raised. They are now built on copies `KBWCommunityIceShell_136..143`:
  - art moved down 58 px to the floor (depth cells moved with it);
  - crate-style stacking: `IsStackable` + `IsTable` + `Surface=32`, so exactly 3 high under vanilla's 96 limit.
- **MRI Scanner:** rows corrected from the user's in-game screenshot (first and last rows swapped). North to south: `44 47 / 43 45 / 42 46`.
- **Test status:** built and checked only. To be re-checked in game.

## 16. File 64 fixes after the in-game check (2026-11-12)

- **Fit:** the window trim and the window planters both belong to the **Window Frame-Tall** window shape, in any colour. User-confirmed in game; the tooltips say so.
- **Window trim:** works in game.
- **Window Planters could not be placed.**
  - Cause: the pack tiles are movable `WallObject`s, which WE builds through its native wall-attachment path, and that path refuses window walls.
  - Fix: now built on overlay copies `KBWCommunityIceShell_144..151` (`WallOverlay` + attached flag; no MoveType / IsMoveAble), placed like the trim.
- **Potted Plants + Flower Basket looked raised.**
  - Cause: the pack draws them against the west / north wall edge.
  - Fix: now built on copies `KBWCommunityIceShell_152..159` with the art centred on the square, art bottom at y 228 (depth cells moved with it). They have no wall attachment, and the pack's stray pixel above every pot is removed.
- **Test bundle:** files 63-65 keep their KBW cards (`COMM_KEEP_GROUPS`), so "Potted Plants" reviews as the single card it ships as. In the WE build it always was one card.
- **TikiTown:** everything that was In Progress is confirmed by the user: props-14 bird cage / terrarium / pet cage / Mahjong, and the barrel planters (file 46).
- **Test status:** the planter and pot copies are built and checked only.

## 17. Community: Dylan pegboard gun racks (NEW file 66, second attempt)

- **Source:** `DarthGunStore` 8-15. Two racks, each 2 tiles wide, with N and W facings:
  - rack 1: N = 8+9, W = 11 over 10.
  - rack 2: N = 12+13, W = 15 over 14.
  - The joins were composited from the art.
- **Why the first attempt failed:** the pack tiles are `MoveType=WallObject` + `WallOverlay`. Vanilla types those as a "WallOverlay" moveable, so WE's ConstructionPlan builds them as a bare sprite attached to the wall, with no object and no storage.
- **Fix:** copies `KBWCommunityIceShell_160..167` without `WallOverlay`. They become plain wall objects with the pack's own `metal_shelves` container (10) on each tile.
- **Fill overlays:**
  - The pack's overlays (16-23) are copied as `KBWCommunityIceShell_168..175`. Using our own names keeps them clear of the dylanstiles tiledef clash.
  - They are registered for the copies in a NEW Lua, `media/lua/server/Items/KBWCommunity_GunRackOverlays.lua` (the vanilla `getContainerOverlays():addOverlays`, the same call the pack's `WorldFiller_dylan.lua` uses).
- **Card and cost:** one "Gun Racks" card, plus Reinforced versions by the default rule (100 per tile). Cost = the Dirkies Metal Wall Shelves.
- **Test status:** built and checked only.

## 18. Community: Dylan Future Room extras (NEW file 67)

**Source:** `DylansFutureRoom01`. The pack gives these tiles no properties at all, and WE's isolated `WECommunity_DylansFutureRoom01` only covers the viewscreens. So every piece is built on our copies `KBWCommunityIceShell_176..198`. The south-facing-only pieces also get a mirrored east-facing copy (whole-tile flip, depth cell flipped with it).

**Pieces:**
- **Wall Screen TV (22 west wall / 23 north wall):** vanilla TV flags (`IsoType=IsoTelevision`, `signal=tv`) like the Dylan wall TVs.
  - Generated screens `KBWCommunityTVScreens_12..17`, appended.
  - **WE-OWNED FILE CHANGED:** two new rows in our work copy of `KBWCommunity_TVScreens.lua` (`SCREENS` table), via `kbw_tilepatch.sync_we_tv_screens`.
- **Black / White Future Fridge (30 / 31 + mirrors):** vanilla 1-tile fridge flags (fridge + freezer). Built as the normal fridge TIER ladder in **file 70** (not 67), one card per colour:
  - tiers 60/30, 80/40, 100/50: shell + unit for the upper two, KBW VE White Refrigerator recipe ladder (`align_appliance_costs.FUTURE_FRIDGES`).
  - Shells are our inert copies `KBWCommunityIceShell_199..202`.
  - No Reinforced version: a reinforced version takes the crate cost and would drop the compressor.
- **Black / White Metal Cabinet (37 / 38 + mirrors):** counter storage 20.
- **Black / White Metal Upper Cabinet (35 / 36 + mirrors):** same flags as the Dirkie upper cabinets (`WallObject` + `IsHigh` + attached + `solidtrans` + container), so they can hang over counters and fridges.
- **Black Modern Couch (40-47):** 2 tiles, 4 facings (joins composited from the art). It uses the vanilla Red Comfy couch flags and seat positions per tile, and the seats are added to our `common/media/seating.txt`.
- **Future Planter (49).**

**Reinforced:** all cabinets get Reinforced versions by the default rule.

**Test status:** built and checked only.

## 19. Wall-mounted cabinets + log-spam fix (2026-11-12, after the in-game check)

- **Blue / Green Metal Drawer Cabinets (file 63):** they are wall-mounted mailbox banks at mid height. Moving them to the floor (section 15) still floated.
  - Copies `KBWCommunityIceShell_136..143` keep the pack art in place.
  - They are now `MoveType=WallObject` + `attached<edge>` (from the tile's Facing: S->N, E->W, N->S, W->E) + `solidtrans`, like the confirmed Dirkie upper cabinets.
  - Placement: `needToBeAgainstWall`. The stacking flags are gone.
- **Lab Specimen Cabinet (file 65):** also wall-mounted at mid height.
  - It was floating and showed texture trouble at the base as a table-top piece.
  - Same wall-mount treatment on its copies `_134/_135`.
  - Removed from WE's `KBWCommunity_TableTop.lua` list again (the sync now also drops our own stale entries).
- **Log spam ("couldn't find item medical_03"):** the pack's `CustomItem=medical_01/02/03` on 32-37 points at items that don't exist. All our 32-37 copies drop `CustomItem`.
- **Test status:** built and checked only.

## 20. TikiTown: entertainment pieces (NEW file 47)

- **Source:** `tikitown_entertainment_01`. Joins come from the pack's SpriteGridPos; composites were checked.
- **Stripper Poles (0 / 1):** one card, pack tiles.
- **Neon signs:** built on our copies, new tileset `KBWTikiTownEntertainment_0..10`, APPENDED to `kbwtikitown_walloverlays.tiles` / the `KBWTikiTownWallOverlays` pack (no new mod.info lines).
  - Why copies: the pack tiles are WallOverlay moveables, which WE builds as bare sprites attached to the wall, so their light could never work. The copies drop `WallOverlay` and keep the pack's `lightswitch` + light colour/radius, so they build as real light switches (on/off, need power).
  - The signs:
    - "Cheeky" (18+19, north wall)
    - "18+ XXX" (22, west wall)
    - Red Legs (23, north wall + mirrored west-wall copy)
    - Ladies Legs (29 over 28, west wall + mirrored north-wall pair)
    - "GIRLS" (31 over 30, west wall; no mirror because of the text)
  - Depth for the mirrors: the wall preset of their attach flag.
- **Hanging Bead Curtain (45 / 46):** pack tiles. The pack calls it a "Door" but gives it no door flags and no open art, so it stays the walk-through hanging decoration the pack defines. It does not block movement or sight.
- **New tooltip keys:** `Tooltip_KBWCB_NeonSign`, `_BeadCurtain`, `_StripperPole`.
- **Test status:** built and checked only.

## 21. File 65: Lab Centrifuge + Lab Analyzer removed (user, 2026-11-12)

- **Removed:** both pieces, because of texture issues in game. The "Lab Equipment" card now holds only the MRI Scanner.
- **Copies:** their copies `KBWCommunityIceShell_130..133` stay in the tileset unused, so that the fixed indices of every later copy don't shift.
- **Table-top list:** both are off WE's `KBWCommunity_TableTop.lua` list again.

## 22. File 67: Future upper cabinets no longer block the square below (2026-11-12)

- **Symptom (user, in game):** nothing could be built under a Future Metal Upper Cabinet. The couch and the low cabinets were refused.
- **Cause:** the copies carried `solidtrans`. KBW refuses any solid / BlocksPlacement piece on a square that is already solid (`Placement.lua`, solid-on-solid check).
- **Fix:** copies `KBWCommunityIceShell_182..185` are now like the vanilla overhead cabinets: movable high `WallObject` + attached + container, with no solid flags. They still go over counters and fridges (KBW's high-wall-object rule).
- **Known:** the Dirkie Upper Cabinets (file 35, pack tiles) carry `solidtrans` and have the same limit. Build the piece below first.
- **Test status:** tested in game (user, 2026-11-12). The Future floor cabinets now place against a wall, and the earlier "can't be placed against a wall" report was this blocking upper cabinet.

## 23. File 63: Red Wall Cabinet had no storage (2026-11-12)

- **Symptom (user, in game):** neither the cabinet nor its Reinforced version had storage.
- **Cause:** the copies `KBWCommunityIceShell_80..83` are attached, non-solid wall objects. KBW builds those through vanilla moveable placement, which only creates the containers the tile itself declares. The definition's `container` block alone does nothing on that path.
- **Fix:** the copies now carry `container=counter` + `ContainerCapacity=20` (+ `IsMoveAble`). The definition still sets the capacity: 20, Reinforced 100.
- **Audit:** no other copy with a definition container has this gap.
- **Test status:** built and checked only.

## 24. Cost rule: a metal base costs half its reinforced version (user, 2026-11-12)
Many metal base pieces cost more than their "(Reinforced)" sibling (e.g. kbwve.extended.metal =
3 sheet metal + 2 pipes + 4 screws vs the crate's 2 small sheets + 2 sheets + 1 scrap).
`counter_variants.halve_metal_bases` (run by `add_variants`) now gives every base whose cost is metal
and that has a `<id>.reinforced` sibling the sibling's actual cost at half: amounts and drainable uses
halved, rounded up, at least 1; tools unchanged. The base keeps its own skills and knowledge gate.
Result: SmallSheetMetal 1, SheetMetal 1, ScrapMetal 1, BlowTorch 2 uses, WeldingRods 2 uses + mask.
Wood bases are unchanged. 29 bases changed: Community 40 (1), 41 (2), 42 (1), 63 (3), 65 (4),
66 (2), 67 (4); TikiTown 36 (12). The Large Industrial Sink (Hand Pump) is set in dirkies_medical.py
to half of its reinforced version (crate + tank). The plain sink keeps its plumbing cost (no metal).
Built and checked: 159 pairs in the test bundle, no base costs more metal than its sibling.
NOT tested in game.

## 25. Future Room couch: depth fixed (2026-11-12)
In game the couch drew over a resting player (backrest hid the body). The copies (iceshell
190-197) used the pack's `DEPTH_DylansFutureRoom01` cells, but their seat positions are the vanilla
Red Comfy couch's (`furniture_seating_indoor_01` 0-7). Their depth cells are now the vanilla couch's
too (same tiles as `FR_COUCH_SRC`, from `DEPTH_furniture_seating_indoor_01.png`). Built and checked:
8/8 cells identical to vanilla. NOT tested in game.

## 26. Future Room fridge tiers: Completed in the test bundle (user confirmed in game, 2026-11-12)

## 27. File 47: Stripper Pole is one piece with two orientations (user, 2026-11-12)
Before, the two pack tiles were two styles: `entertainment_pole_1` / `_2`, grouped as "Stripper Poles".
Now they are one buildable `worldessentials.tikitown.entertainment_pole`, with faces W =
`tikitown_entertainment_01_0` and N = `_1`. The pack gives the tiles no `Facing`, so this mapping is
our choice. The group is removed. Built and checked. NOT tested in game.

## 28. File 65: MRI Scanner works as a bed; tiles 45 and 46 swapped (user, 2026-11-12)
- **Layout (3rd in-game correction):** rows north to south are now `44 47 / 43 46 / 42 45`.
- **Bed:** the patient table is the west column of the two south rows, medical 42 (foot, south) and
  43 (head, north). Those tiles are now our copies `KBWCommunityIceShell_203` / `_204`, appended to
  `DECOR_COPIES` as kind "bed" (`kbw_tilepatch.MED_MRI_BED`).
- **Copy flags:** the vanilla single bed tile with the same role (`furniture_bedding_01_0` foot /
  `_1` head): `bed`, `BedType=averageBed`, `Facing=S`, `SpriteGridPos` 0,1 / 0,0, GroupName "MRI",
  CustomName "MRI Scanner". The moveable / pick-up keys are removed. So Rest / Sleep should lie the
  player N/S.
- **Seating:** our seating.txt copies the vanilla bed's seat positions for these two tiles, keeping
  only the `E` position, so a seated player should face east.
- **Unchecked:** the vanilla seat heights are for a normal bed, and the MRI table may sit higher.
- **Test status:** built and checked. NOT tested in game.

## 29. File 47: gaps in the built "Cheeky" and "GIRLS" neon signs (user, in game 2026-11-12)
- **Symptom:** once built, part of the lettering was missing at the tile join (Cheeky: "Ch eeky").
  The placement ghost was fine, because it draws without depth.
- **Cause:** every neon copy used a vanilla wall depth preset (`preset_depthmaps_01_4` / `_5`), but
  the art overhangs the preset's wall slab. Cheeky tile 19 reaches 16 px into the x0 square, and
  GIRLS tile 30 reaches past its edge. Art pixels with no depth are hidden. The pack never hit this
  because a WallOverlay draws with its host wall's depth.
- **Fix:** tileset `KBWTikiTownEntertainment` now has its own
  `common/media/depthmaps/DEPTH_KBWTikiTownEntertainment.png`, written by
  `tikitown_wall_overlays.write_own_depth`. Each cell is the tile's wall preset (picked from its
  attach flag), with the preset's wall plane extended under every overhanging art pixel. The plane is
  a least-squares fit, about 0.5/255 mean error. The 11 tiles no longer appear in
  `tileDepthTextureAssignments.txt`.
- **Check:** 586 pixels filled, 0 art pixels left without depth.
- **Test status:** built and checked. NOT tested in game.

## 30. Future couch: gaps after the depth fix (user, in game 2026-11-12)
- **Symptom:** after note 25 the couch showed small texture gaps, like the neon signs (note 29).
- **Cause:** the Future art pokes 4-48 px per tile past the vanilla couch's depth shape (cushion and
  arm edges, some detached from the shape). Art pixels with no depth are hidden.
- **Fix:** `kbw_tilepatch._fill_depth_holes` gives each such pixel the depth of the nearest covered
  pixel. It grows through the whole cell, and only the art holes take the grown value. It runs on
  the couch cells (190-197) and on kinds in `FILL_DEPTH_KINDS` (now "bed": MRI 203/204, 7 px).
  Check: 0 art pixels without depth on those tiles. Built and checked, NOT tested in game.
- **Found, not changed (pieces already confirmed or pack-identical):** other iceshell copies whose
  depth (the pack's own cells) leaves art uncovered:
  - ladder tops 76-79: 530-1023 px
  - centred pots 152-159: about 1300-1800 px
  - drawer cabinets 136-139: 109-161 px
  - crane ladders 84-87: 9-184 px
  - pump sinks, wheelchair, trim, planters, gun racks: 1-94 px
  Most of these holes are the same on the pack's own map tiles. If any of them shows gaps in game,
  add its kind to `FILL_DEPTH_KINDS`.

## 31. MRI bed: Rest sat the player on the ground; menu said "MRI MRI Scanner" (user, in game 2026-11-12)
- **Rest:** vanilla `ISWorldObjectContextMenu.onRest` paths to a seat position. If none is reachable,
  `onRestPathFailed` sits the player on the ground beside the object. We kept only the vanilla bed's
  `E` position (for "seated facing east"), but its stand square is the solid pedestal column east of
  the table, so it could never be reached. Now both vanilla positions `W` + `E` are kept
  (`MRI_SEAT_SIDES`). The reachable W side seats the player facing west, since a seat faces away from
  the bed. Facing east would need the east squares walkable.
- **Name:** the menu shows "<GroupName> <CustomName>". CustomName is now "Scanner" (GroupName "MRI").
- **Test status:** built and checked. NOT tested in game.

## 32. Test bundle: all TikiTown is Completed (user, 2026-11-12)
`TT_COMPLETED` now includes 47 (entertainment). The bundle has no "TikiTown - In Progress" entries left.

## 33. File 65: Lab Specimen Cabinet removed for now (user, 2026-11-12)
Neither the table-top version nor the wall-mounted version looked right. The card and its reinforced
sibling are gone. Copies `KBWCommunityIceShell_134/135` stay in the tileset (fixed indices), unused.

## 34. Future fridges: the door screen is a working TV (user, 2026-11-12)
- **Copies:** fridge copies `KBWCommunityIceShell_178-181` (black / white + mirrors) also carry the
  vanilla TV flags: `IsoType=IsoTelevision`, `signal=tv`, `TV`, `CustomItem=Base.TvWideScreen`.
  `IsMoveAble` and the pick-up keys are removed.
- **How it builds:** KBW `NativeObjectTypes` maps the IsoType to "television", so the build makes an
  IsoTelevision. KBW's `initializeSpriteContainers` then calls
  `createContainersFromSpriteProperties`, so the fridge + freezer come from the same tile flags, as
  for map fridges.
- **Why CustomItem:** `IsoWaveSignal.init` clones its TV device data from `CustomItem` (checked in
  the bytecode). Without it the device is a blank `DeviceData`.
- **Why not movable:** a vanilla pick-up would return that TV item instead of the fridge, so the
  fridge is not movable, like our wall TVs.
- **Shells:** the shells (199-202) drop the TV keys (`_FRIDGE_TV_KEYS`).
- **Screens:** generated like the wall TVs, appended to `_PACK_TVS` (`FR_FRIDGE_TV_QUADS`): screen
  tiles `KBWCommunityTVScreens_18..29`. Black 30 uses the left face (vanilla S series), white 31 the
  right face (E). The mirrors flip.
- **WE-owned Lua:** `sync_we_tv_screens` added the 4 rows to WE's `KBWCommunity_TVScreens.lua` in
  our work copy. The WE dev must take those rows.
- **Collision:** that Lua clears `movedThumpable` (for the walk-through wall TVs). The fridge keeps
  `solidtrans`, so it stays solid.
- **Test bundle:** the Future fridges are back under "Community - In Progress".
- **Test status:** built and checked; the screen fit was checked on a composite. NOT tested in game.
  To check: the fridge/freezer still cool on power, the TV turns on and shows broadcasts, the tier
  capacities, and dismantling.

## 35. MRI seats placed on the table (user, in game 2026-11-12, round 2)
- **Symptom:** with the vanilla bed seats copied (note 31), the player sat floating west of the
  table, facing west, on both tiles.
- **Cause:** the MRI table is not bed-sized. Measured from the assembled art (pedestal base,
  table-top edges, with the vanilla mattress as height reference), it is about 0.58 tile wide,
  centred at x ≈ 0.84 of the west column (spans x 0.55-1.13). Its south end is at the piece's south
  edge, and its top is about 1.2x the mattress height.
- **New seats:** `kbw_tilepatch.MRI_SEATS`, written by `_seat_block`. seating.txt
  `translate = x height y` (x 10000), tile units from the tile centre, +x east, +y south;
  id = the direction the seated player faces. Front approach only, like vanilla's bed seats.
  - foot (203, medical 42): `S` 0.34 / 0.41 / 0.33, sits on the south end facing south.
  - middle (204, medical 43): `W` 0.21 / 0.42 / 0 and `E` 0.47 / 0.41 / 0. Rest picks the reachable
    seat nearest the player.
- **Why E never triggers:** E's stand square is the pedestal column. KBW sets
  `blockAllTheSquare` / `canPassThrough` per buildable, not per tile, so that square stays blocked
  and in practice the middle tile seats you facing west.
- **First seat id:** `SeatingManager.getFacingDirection` returns the first seat's id, so S is first on
  the foot tile and W first on the middle tile (as vanilla's head tile).
- **Fine-tuning:** heights and insets are estimates from the art. B42's debug Tile Geometry Editor
  can adjust seats live if needed.
- **Test status:** built and checked; the seats were projected on the art. NOT tested in game.

## 36. Future couch: dithered seam between the two tiles (user, in game 2026-11-12, after note 30)
- **Symptom:** a dithered strip, with the ground showing through, along the join of the two couch
  tiles.
- **Cause:** the vanilla couch depth cells also hold the floor and shadow under the vanilla couch,
  at ground depth. 141-317 px per tile of the Future art lie past the vanilla couch shape, on that
  floor-only depth, so they z-fought the ground.
- **Fix:** `_mask_depth` keeps vanilla depth only where the vanilla couch art
  (`furniture_seating_indoor_01_<n>`, extracted from Tiles2x.pack) is drawn. `_fill_depth_holes`
  then gives every other Future art pixel the depth of the nearest couch-body pixel.
- **Check:** 0 art px without depth. The few px that still equal the floor value are within 1-2 px
  of the couch body, at the base where body and floor meet.
- **Test status:** built and checked. NOT tested in game.

## 37. Future couch: the real seam cause; art re-cut like vanilla (user, in game 2026-11-12, after note 36)
- **Symptom:** a dithered strip at the join persisted after note 36. The ghost, drawn without depth,
  was fine.
- **Cause:** the pack's two tiles of each couch OVERLAP: about 1,480-1,740 px are drawn by BOTH tiles.
  They also split the art away from the square boundary (60-260 px of each tile lie on the other
  tile's vanilla area). Each tile is depth-sorted on its own square, so the shared pixels z-fought
  each other.
- **Fix:** `kbw_tilepatch.couch_recut_art`.
  1. Composite each pair as the ghost draws it (back tile first).
  2. Give every pixel to ONE tile: the one the vanilla Red Comfy couch
     (`furniture_seating_indoor_01_<n>`) draws there, else the nearest such tile, and always a tile
     whose frame contains it.
  The copies 190-197 ship that art. Their depth is the vanilla cell masked to the vanilla art
  (note 36), filled from the couch body.
- **Check (shipped pack):** 0 overlap px per pair. Each pair composites to exactly the original
  picture (max diff 0). 0 art px without depth. Test bundle and WE work pack + depth are identical.
- **Test status:** NOT tested in game.

## 38. Future TV fridges: confirmed in game; their cost now includes a TV's parts (user, 2026-11-12)
- **Status:** the door-screen TV works in game (note 34). The Future fridges are back under
  "Community - Completed" in the test bundle.
- **Cost:** every Future fridge working unit (black / white, 60 / 80 / 100) also costs the Wall
  Screen TV's parts: 6 Electronics Scrap, 1 Small Sheet Metal, 2 Electric Wire. These come from
  `align_appliance_costs._add_tv_cost`, read from `community.dylan.rf02.tv_crt_premium` so the two
  stay in sync, and are added as stage inputs next to the tier's material group.
- **Not repeated:** the TV's screwdriver, which the material group already lists. The TV's
  Electricity 2 is below every tier's Electricity (4-6).
- **Unchanged:** the shells, and all other fridges.
- **Test status:** built and checked. The cost change is NOT tested in game.

---

# Hand-off 2026-11-13: rugs, Ranger Station signs, neon light fix, clean pump-sink water
Tag `handoff-2026-11-13-rugs-signs-sinks`. Minor update. Everything was tested in game by the user:
- **39** TikiTown rugs (new file 48), **40** Ranger Station signs (new file 49).
- **41c** Hand-pump sinks give clean water (`waterPiped` restored on the 24 pump-sink tiles; still
  infinite).
- **43** Neon signs 18+, GIRLS and Ladies Legs now build as real lights (below).
- Card title `IGUI_WETiki_barrel_planters_group` added (it was missing for the barrel planters
  shipped on 2026-11-12).
NOT included: 41 / 41b furnace experiments (test bundle only), 42 StageInfo fix (user: not this
time), the Dirkies drawer-cabinet rotation offsets the rotation pass now finds (not tested).

## 39. TikiTown rugs (NEW file 48, tikitown_rugs_01) (user, 2026-11-12)
- **Floral rugs** (Light Green / Dark Red / Yellow and Black): each colour's 12 tiles are two 2x3
  rugs, one laid N/S and one laid E/W (read from the art, checked by compositing). They are built as
  a **Straight** and a **Corner** piece with 4 orientations each, one card per colour, so players
  lay out any shape.
  - Offsets inside a colour block (start tile 4 / 6 / 10, row step 8):
    - Straight: N +33, E +9, S +32, W +8 (the border side).
    - Corner, clockwise: N = NW +16, E = NE +17, S = SE +1, W = SW +0 (the N/S rug's corner set;
      its south corners carry the pineapple end motif).
  - All corner tiles share the same border, so they join straights on both axes. Checked: 2x4 N/S
    and 4x2 E/W rugs built from the pieces are seamless in all 3 colours.
  - **Corner (Alt)** (user, 2026-11-12): the E/W rug's own corners, clockwise N = NW +25,
    E = NE +41, S = SE +40, W = SW +24. Its pineapple motif sits on the west / east ends. Checked:
    the 2x4 and 4x2 rugs built with the alt corners are seamless in all 3 colours. Each colour card
    now has 3 pieces: Straight, Corner, Corner (Alt). Every rug tile of the sheet is used (10
    buildables).
- **Street Play Rug** (tiles 0-3): one 2x2 piece. North row `3 2`, south row `0 1`, west to east.
  This is the only one of the 24 arrangements whose pieces meet with no gap or overlap (the art
  covers less than each floor diamond). It matches the user's sketch, rotated.
- **Pack tiles:** used directly (FloorRug + solidfloor, no grid / facing).
- **Setup / cost:** like the confirmed Dylan floor mats (file 52): Decorations / Rugs, the same
  object flags, Tailoring 2, the Rugs & Carpets magazine. The cost is scaled per tile from the
  2-tile mat: a 1-tile piece = fabric 3 + thread 2 uses (100 time); the 2x2 = fabric 12 + thread 8
  (400).
- **Test bundle:** TikiTown - In Progress, keeps its cards (`TT_KEEP_GROUPS` 48).
- **Test status:** built and checked. NOT tested in game.

## 40. TikiTown Ranger Station signs (NEW file 49, tikitown_signs_02 46-48) (user, 2026-11-12)
- **Card:** one card, "Ranger Station Signs", category Decorations and Landscaping / Signs.
- **Ranger Station Sign:** 2 tiles, single orientation, built on the pack tiles. The board runs N/S:
  rows north to south = `47`, `46`. Checked by compositing: one continuous "RANGER STATION" board on
  two posts; the other order splits it. The pack tiles are BlocksPlacement + solidtrans, so it
  builds as a solid sign. Cost: hammer, 4 planks, 6 nails, Woodwork 2 (time 200).
- **Ranger Station Wall Sign:** tile `48`, a small green metal plate (pack: WallObject + WallOverlay
  + attachedW). Built like the confirmed TikiTown posters (23_tikitown_furniture: placement object +
  requiresFloor, not thumpable, dismantable), so WE hangs it on a west wall as an attached sprite.
  Single orientation, since the pack has no north-wall version. Cost: hammer, 1 small sheet metal,
  2 nails.
- **Test bundle:** TikiTown - In Progress, keeps its card (`TT_KEEP_GROUPS` 49).
- **Test status:** built and checked. NOT tested in game.

## 41c. Hand-pump sinks gave TAINTED water: `waterPiped` restored (2026-11-13)
- Cause (ours, not WE's): the pump-sink tiles had `waterPiped` removed. For infinite water, the
  engine's `IsoObject.getInfiniteWaterType` returns clean Water only for an unmoved `waterPiped` object
  or the hard-coded sprites `camping_01_16` and `camping_01_64`-`67` (map pump, Large Water Tank).
  Every other infinite source is TaintedWater. The list is a Java string match, so mods can't extend it.
- Fix: `kbw_tilepatch._pump_sink_props` adds `waterPiped` back, on all 20 counter-top pump sinks
  (KBWCommunityIceShell_48-67) and the medical Large Industrial Sink copies. They stay infinite:
  `isWaterInfinite` returns true for `waterAmount >= 9999` BEFORE the room, piping and shutoff
  checks.
- Side effect: vanilla's plumb option appears on them. Plumbing one to a barrel sets
  `canBeWaterPiped = false`, so it then draws from that barrel, the same as a vanilla sink.
- Built and synced to `work/`; NOT yet confirmed in game (clean water with the water shutoff active).

## 43. Neon signs 18+, GIRLS, Ladies Legs build as real lights (2026-11-13)
- Symptom (user): these three weren't lights, unlike Cheeky and Red Legs.
- Cause: the pack defines these three as hammer `MoveType = WallObject` moveables (Pick/PlaceTool,
  no `IsMoveAble`). The working signs are plain `IsMoveAble` tiles, and KBW only creates an
  IsoLightSwitch for those.
- Fix (`tikitown_entertainment.copy_props`, our KBWTikiTownEntertainment copies only):
  - the three get the working signs' layout (`MoveType` / tools dropped, `IsMoveAble` added)
  - 18+ and GIRLS: pink (255/20/147, vanilla LightBulbPink)
  - Ladies Legs: orange (255/128/0, vanilla LightBulbOrange) on ONE tile only (29); 28 is plain
    decoration (user)
- Signs placed before the fix stay plain objects; they must be rebuilt.

---

# Hand-off 2026-11-13 (2): Future Wall Screen TV fixes
Tag `handoff-2026-11-13-wall-screen-tv`. Minor update, on top of
`handoff-2026-11-13-rugs-signs-sinks` (not merged yet; this tag includes it). Tested in game by
the user.
- **44** Future Wall Screen TV: right screens after a reload, draws under the upper cabinet above it,
  walk-through, Pick up option. Needs the 2 SCREENS rows in WE's `KBWCommunity_TVScreens.lua`.
NOT included: 41 / 41b furnace experiments (test bundle only), 42 StageInfo fix, the Dirkies
drawer-cabinet rotation offsets (not tested).

## 44. Future Wall Screen TV: screens after a reload, draw order, walk-through (2026-11-13)
Buildable `community.dylan.future_room.wall_screen_tv` (file 67). The user reported three bugs.
- **Black screen and half a couch after leaving and coming back.**
  - Cause: `IsoTelevision.update()` runs `setupDefaultScreens` while the screen list is empty. It adds
    the sprites at the TV's own index +16 / +32 / +48 (vanilla's screen layout). For our TV
    `KBWCommunityIceShell_176` that is `_192`, a Black Modern Couch tile, and `_208` / `_224` don't
    exist. WE's `applyScreens` replaces the list later, but the overlay already shown stays until the
    next `setScreen` (turning the TV off and on).
  - Fix (tiles, no Lua): new TV copies at FIXED indices `KBWCommunityIceShell_205` (west wall) and
    `_206` (north wall). Their +16 / +32 / +48 slots (`_221`/`_222`, `_237`/`_238`, `_253`/`_254`)
    hold their own warped screens in vanilla order. Whichever code fills the list, it gets the right
    screens. The tileset grows to 32 rows (256 cells).
  - `_176` / `_177` stay as they were. TVs already placed keep them (and the bug) until rebuilt.
- **The TV drew over the upper cabinet hung above it.** Neither tile had a depth cell.
  - The new TVs and their screens use vanilla's wall preset (`preset_depthmaps_01_4` W / `_5` N, as
    for wall detailing), extended along the wall plane under the art, 2 steps nearer than the wall.
    Each screen uses its TV's cell, as vanilla's TV screens do.
  - Future upper cabinets (`_182`-`_185`) use vanilla's floating-cabinet box
    (`fixtures_counters_01` cell 16), filled under the Future art.
- **Solid.** The placement is now `{"kind":"object","needToBeAgainstWall":true}`, and the object gets
  `isThumpable:false, canPassThrough:true`, like the viewscreens (file 50).
- **No Pick up option.** The TV tiles had no `IsMoveAble`. All four (`_176`/`_177`, `_205`/`_206`) now
  get vanilla's TV pick-up flags (`IsMoveAble`, `PickUpWeight 100`, `Material Electric`,
  `MaterialType Glass_Light`) plus face offsets for rotation (W copy `Soffset 1`, N copy `Eoffset -1`).
  The pick-up item is the `CustomItem` (`Base.TvWideScreen`). `Radio` extends `Moveable` (checked in
  the jar), and `ReadFromWorldSprite` keeps our sprite on the item, so it places back as the Wall
  Screen. No `CanScrap`, so a built TV can't be scrapped for free parts. Tile properties apply to
  TVs already placed, so the old ones get the option too.
- **WE-owned Lua (flag to the dev):** `KBWCommunity_TVScreens.lua` SCREENS gets 2 rows (work copy of
  `World Essentials (base, our files only)`): `_205` -> `_221, _237, _253`, `_206` -> `_222, _238, _254`.
  - Optional dev note, not done: calling `setScreen` once right after `applyScreens` would also fix
    TVs that are already placed. That is WE's code, so it is only a suggestion.
- Built and synced to `work/` (collision check total 0).
- **Confirmed in game (user, 2026-11-13), all of it:** the new TV keeps the right screen after leaving
  and coming back (no couch), the upper cabinet draws over the TV, the TV square is walk-through,
  and Pick up / place / rotate work.

---

# Pending for the next hand-off (not pushed yet)
(41, 41b experiments; 42 StageInfo fix)

## 41. EXPERIMENT: fuel-fired furnace on B42's unused machine path (TEST BUNDLE ONLY, not for WE) (2026-11-12)
- **Vanilla furnaces:** `Blast_Furnace` (the Advanced Furnace) is a plain CraftBench. Every smelting
  recipe lists its charcoal as an ordinary input. Recipe counts: PrimitiveFurnace 7, Furnace 12,
  AdvancedFurnace 17; 29 of the 36 use charcoal.
- **Dead end: a tank on a bench.**
  - `CraftBench` `fluidInputChannels` / `energyInputChannels` are parsed but referenced nowhere else
    in the jar.
  - `CraftBench.getResources()` is a stub (`return new ArrayList()`).
  - Handcrafting only takes fluid from fluid-container items.
- **The implemented path: an automated machine.**
  - Component `CraftLogic` (also `FurnaceLogic`, `MashingLogic`) plus a `Resources` component.
  - These are registered ComponentTypes, and their systems are registered in `GameEntityManager`.
  - `CraftLogicSystem.start` -> `CraftRecipeData.consumeInputs(resources)` -> `consumeInputFromResources`,
    which switches on Item / Fluid / Energy.
  - UI: `ISCraftLogicPanel` + widgets, and `ISFluidSlot` -> `ISFluidTransferUI`, so players can pour
    into a fluid slot.
  - Vanilla only uses `DryingCraftLogic`.
- **Prototype:** `pz_craft_loops/fuel_furnace_proto.py`, wired into `build_merged_test_mod.py`.
  - Script `media/scripts/KBWCommunity_FuelFurnace.txt`: module KBWCommunity, entity `Fuel_Furnace` on
    the vanilla Blast Furnace art and cost, with its own xuiSkin style.
  - Resources: `craft_inputs` = `Item@Input@4` + `Fluid@Input@20`; `craft_outputs` = `Item@Output@4@StackAny`.
  - `CraftLogic`: Manual start.
  - One recipe: vanilla ExtractSteelFromSmallItem with `fluid 0.5 [Petrol]` instead of 2 charcoal.
  - Buildable `kbwcb.experimental.fuel_furnace`: one `entityCompat` stage, under "Community - In
    Progress / Experimental".
- **Unverified until in game:**
  - the standalone `fluid` input line (vanilla only uses the item-attached `-fluid`)
  - the unfiltered fluid slot
  - machine time units
  - multiplayer sync
- **Test status:** built and checked statically (script braces balanced, buildable present, nothing in
  WE work). NOT tested in game.
- **First in-game load crashed** (console.txt):
  - `Sprite 'crafted_02_11' is duplicate. entity script: Fuel_Furnace` (SpriteConfigManager). A sprite
    can belong to one entity only. That was a script load error, so the world refused to load.
  - Also `XuiSkin 'KBWCommunity.default' ignored, skin needs to be module Base`.
- **Fix:**
  - The entity now uses its own copies, test-bundle-only tileset `KBWFuelFurnaceProto`
    (tiledef `kbwfuelfurnaceproto` 8177, free across installed mods): copy j = crafted_02_(8+j) with
    vanilla props, depth from the crafted_02_8 cell as vanilla assigns it.
  - The xuiSkin block moved into its own `module Base` section of the script file.
  - Lesson for any entity work: never put a pack or vanilla sprite in an entity SpriteConfig. Use
    copies (it would also claim every map tile of that sprite).
- **Second run: the world loaded, but clicking the furnace threw an error.** The machine window opened
  (so CraftLogic is live), then vanilla `ISWidgetCraftLogicInputControl.lua:64` threw
  IndexOutOfBounds. That widget makes one item slot per recipe input, fluid inputs included.
  - Fix: one `Item@Input` per recipe input (2).
  - Also found: vanilla never shows a Resources fluid slot in the machine window
    (`ISCraftLogicPanel:createFluidSlotPanel` is defined but uncalled). The panel itself is complete:
    `ISFluidSlotPanel` -> `ISFluidSlot` -> Transfer -> `ISFluidTransferUI` on the resource.
  - New test-bundle Lua `KBWCommunity_FuelFurnaceUI.lua` (client) wraps
    `ISWidgetCraftLogicInputControl.createDynamicChildren`. It adds that panel in the input column's
    unused tools spot (`inputTools`, laid out by vanilla's own calculateLayout), only when the input
    group has Fluid@Input resources (no vanilla machine does).
  - Checked: Kahlua-safe grep, Lua syntax with `next = nil`. NOT tested in game.
- **Third run (a newly built furnace): still "Index 1 out of bounds for length 1".** Two identical
  `Item@Input@4` lines in a Resources group collapse into one slot (the script parser keeps one of
  duplicate value lines).
  - Fix: every slot line must differ (`Item@Input@4` + `Item@Input@2`).
  - Fourth run: **the machine window works** (2 item slots, the fuel bar, Craft / Cancel, timer,
    In Progress / Done). Two errors repeated every frame:
    - `ISItemSlot.lua:157`: vanilla gives the fluid input an item slot, and its preview asks for a
      possible item. Our hook now sets `showPreviewItem = false` on slots whose input is a fluid.
    - `ISLabel.lua:89`: ISGroupBox's default title label uses textColor `{1,1,1,1}`, but ISLabel
      reads `.r/.g/.b`. The panel now gets title "Fuel" and an r/g/b/a colour. The label error
      aborted drawing the panel, which is likely why Transfer / Clear were missing (their xui
      styles exist).
  - Fifth run: the window was clean (no errors) and the "Fuel" panel drew, but it had no Transfer /
    Clear buttons. The default skin's base `ISFluidSlot` style (xs_ISFluidSlot.txt) sets
    `enableTransfer = false` and `enableClear = false`, making a read-only gauge. Fix: the slots use
    vanilla's `S_FluidSlot_Editable` style, and the panel uses `S_FluidSlotPanel_Inputs`.
  - **Sixth run: crafting works end to end** (user confirmed): pour petrol in with Transfer, load
    the item, press Craft, and it drains the fuel and makes the output. The engine route is proven.
  - Recipes reworked (user: "require a crucible to output the liquid into"):
    - B42 has no molten-metal fluids. Molten metal is a filled crucible item (CeramicCrucible_Steel /
      _Iron, drainable, uses = units), which every casting recipe consumes. So there is no internal
      molten tank.
    - Generated from vanilla's own 11 charcoal Smelt* recipes (copper ore + iron / steel, smaller to
      large): crucible in, filled crucible out via their itemMapper and Java
      `RecipeCodeOnCreate.smeltIronOrSteel*` (it adds the units; the character is unused).
    - Charcoal becomes Petrol at 0.25 L per charcoal, as the last input. The tongs (mode:keep) are
      dropped.
    - Slots: `Item@Input@1` (crucible), `@10` (metal), `@2` (the fuel input's placeholder slot) +
      `Fluid@Input@20`.
    - Not ported yet: Extract* (keep a crucible as a tool) and Cast* (keep a mold), because kept tools
      don't work in machine slots.
  - Also: a placed machine keeps the resources it was built with. Changing the script does not
    update built ones. Before shipping, the slot layout must be final (or old ones need a Lua
    fix-up).
  - **v2: integrated molten tanks** (user: one built-in tank per crucible material = iron, steel,
    glass; 100 per type; player picks the pour amount, with a fill-all option). Built and checked
    only, NOT yet tested in game:
    - New fluids `KBWMoltenIron` / `KBWMoltenSteel` / `KBWMoltenGlass` (module Base, Industrial,
      Fluids.json names). Each has a `fluidFilter <Fluid>Filter { filterType = whitelist, fluid = X }`.
      The syntax was read from `FluidFilterScript.readBlock`: a filter name without a module resolves
      in Base, and a modded fluid's id is its bare name.
    - Tanks: `Fluid@Output@100@KBWMolten*Filter@null@null` in the output group. Inputs:
      `Item@Input@10`, `Item@Input@1`, `Fluid@Input@20` (petrol).
    - 13 recipes generated from vanilla's crucible recipes: 11 Smelt*, ExtractIronFromIronOre (12),
      MeltSand / MeltGlass (4). Charcoal becomes petrol. The crucible, tongs and startfire are dropped.
      The output is `fluid N [KBWMolten*]`, where N is the units vanilla's OnCreate adds. Copper ore
      is left out: it does not use a crucible.
    - A full tank blocks a recipe on its own (`CraftUtil.findResourceOrEmpty` skips full tanks, or
      tanks with too little free space). But a tank can't feed a recipe input: that function accepts
      only IO == Output for outputs, and CraftLogic passes the input and output groups separately.
      So the pour is Lua. The molten tank's vanilla Transfer button (`ISFluidSlot.onTransferFluids`
      hook) opens a menu of the player's crucibles: "Fill (+N)", then +1/2/4/8/12. A timed action
      sets the crucible's uses to litres poured, and empty crucibles turn into the filled type.
      Clear (vanilla `ISFluidEmptyAction`) dumps a tank.
    - Single player only: the pour changes the tank and the inventory locally, with no MP sync.
    - Old furnaces must be rebuilt: the resources changed.
  - In-game fixes, 2026-11-13:
    - Recipe OUTPUT lines take the bare fluid name (`fluid 4 KBWMoltenIron`). The bracketed form
      stopped world load with "Fluid not found: [KBWMoltenIron]".
    - Vanilla machines only load or start as many items as they have free ITEM output space. That
      comes from `ISCraftLogicPanel.ItemSlotAddItems` and `CraftLogic.willOutputsAccommodate`,
      built for drying racks. With only fluid outputs nothing could be loaded and Craft did
      nothing. Fix: an `Item@Output@20@StackAny` slot (headroom; it also receives the empty sacks).
    - The engine never applies a Resources line's fluid filter, so molten fluids went to the first
      empty tank. Recipe output does respect the tank container's whitelist, so the Lua sets
      `FluidContainer:setWhitelist(FluidFilterScript:getFilter())` per tank when the window opens.
    - The whitelist alone does not route. `CraftUtil.findResourceOrEmpty` records the first EMPTY
      tank before checking `canAddFluid`, and returns it unless a tank already holds the fluid. With
      iron in the Iron tank and Steel empty, glass was always aimed at Steel, refused, and the craft
      couldn't start. So each molten tank keeps a 0.01 L seed of its own fluid, and the engine then
      picks the tank already holding it. Pours ignore the seed, and Clear dumps everything above it.
      Tested against mocks only.
    - Melt Sand: a machine slot burns the whole sack (vanilla handcraft takes 1 of its 4 uses). Now
      it takes one FULL sack = 4 vanilla melts: 16 L glass, 2 L petrol, and the empty sack back.
    - StartMode Automatic was tried and reverted. In a machine window the Craft button also
      transfers the picked ingredients (`ISWidgetCraftLogicControl.startCraft` ->
      `GenericCraftTransferAndStart`), and Automatic hides it, so nothing could be loaded or started.
      Vanilla's quantity box is never used either: `startCraft` caches it in `self.craftTimes`, and
      nothing reads that. A Lua batch on Manual was tried next, but Manual start is gated on the
      player using the machine (`CraftLogic.isInvalidStartMode` -> `GameEntity.isUsingPlayer`), so
      it stopped once the window closed.
    - Automatic is NOT usable in this build. `CraftLogicSystem.start` calls
      `player.getPlayerCraftHistory()` unconditionally, after consuming the inputs. The system
      starts Automatic machines with player = nil, so the first auto-start threw an NPE
      (`CraftLogicSystem.java:173`) and froze the game. No vanilla machine uses Automatic.
      **Report to the WE dev / TIS.** StartMode is saved with the placed machine, so a furnace built
      while the script said Automatic stays Automatic. The Lua refuses to load items into one.
    - **Confirmed in game (user, 2026-11-13):** Melt Sand (with the empty sack back), steel smelting,
      per-metal tank routing (seed), and the crucible pour (Transfer button) for all 3 tanks.
    - Tuning (user, 2026-11-13): fuel 0.125 L per vanilla charcoal (half of before), fuel tank
      100 L, metal tanks 400 L each, material slot 99 (item output headroom 100). Loading an item
      takes 5 ticks instead of vanilla's 30 + 3 x weight. Cancel also clears the queued batch. The
      molten tank's Transfer button (the crucible pour) now has a "Pour into crucible" tooltip.
    - Final: Manual. Before each batch restart, the Lua marks the furnace as used by the player
      (`GameEntity:setUsingPlayer`), so the batch keeps going after the window closes. Quantity
      1-99, MAX = until it runs out. Single player only. Tested against mocks only.
    - Fluid bars use minimumBarSize 50 so the panel fits the window's grey area.
    - A Resources line's filter name (`Resource.filterName`) is only set from the script when the
      machine is built, and it isn't saved. After a reload `getFilterName()` is nil, so an old
      furnace showed only the fuel tank. The Lua now identifies tanks by position in the output
      group (script order Iron, Steel, Glass) and the furnace by entity name.
    - Vanilla lays out the quantity box only for Automatic machines (`allowBatchCraft`). The Lua
      hides it on the furnace, because the value is never used.

## 41b. EXPERIMENT: furnace suite on Dirkies' Production Furnace art (TEST BUNDLE ONLY) (2026-11-13)
- Generator: `pz_craft_loops/furnace_suite.py`. It reuses `fuel_furnace_proto.py` for the fluids, tank
  filters, machine UI, batching and crucible pour. Tileset `KBWFurnaceSuite`, tiledef `kbwfurnacesuite`
  8176 (free), from `edit_ddd_RUS_Production_Furnace`, with the pack's own depth cells. It is
  planned as its own WE submod later.
- Brick Fuel Furnace (72-75, 2x2, rows N->S `75 73` / `72 74`): the prototype machine on brick art,
  petrol and molten tanks. **Confirmed in game (user, 2026-11-13):** it builds and crafts, and a
  batch keeps going after the player steps away. So far only Smelt Large Iron Item (axe head) has
  been tested.
- Electric Furnace (32/35/38/39, faces S E N W): a machine with the same molten tanks, and the fuel
  recipes minus the fuel input (`KBWElectricFurnace*`). It needs power and its switch on.
  **Confirmed working in game (user, 2026-11-13).**
- Electric Smelter (48 / 50) and Electric Kiln (56/59/62/63): CraftBench workbenches, ground or table
  top (toaster-style props `IsTableTop`, `IsMoveAble`, `attachedSurface`). The smelter runs vanilla
  MeltSand/MeltGlass and Smelt(Small|Smaller)(Iron|Steel)Item; the kiln runs MakeCoke and
  MakeWoodCharcoal*. Charcoal and fire starter inputs are removed, and each recipe has
  `OnTest = KBWFurnaceSuite.smelterPowered / kilnPowered`. OnTest runs per input item as
  `OnTestItem(item, character)`, so the check is "a powered, switched-on bench of that kind within 2
  tiles of the crafter". **Confirmed in game (user, 2026-11-13):** the smelter's recipes show as
  missing every input until it's switched on, then appear.
- Smelter "on but idle" overlay (user, 2026-11-13): the pack has only one lit tile per
  orientation, so the idle state is the working overlay recoloured dimmer and redder (`DIM_RGB`,
  KBWFurnaceSuite_28/29).
- States are OVERLAYS, never sprite swaps (user). The pack only has full on/running tiles, so each
  overlay is the on-tile's pixels that differ from the off-tile. Three noise filters apply: blobs
  under 6 px, long 1-px lines (re-drawn outlines), and faint blobs with average alpha under 160
  (anti-aliased edges). The Lua attaches them as attached anim sprites: powered = power + switch
  on; running = CraftLogic running, or someone handcrafting at that bench.
- Power: `square:haveElectricity() or hasGridPower()`, plus an on/off switch (modData `KBWPowerOn`,
  context menu "Turn On/Off <name>", default off).
- Redraw: B42 caches each chunk's drawing, so a changed attached sprite only showed after leaving
  and coming back (user, 2026-11-13: "same display bug from wall panels"). The fix is to call
  `obj:invalidateRenderChunkLevel(256 + 1024)` (FBORenderChunk DIRTY_OBJECT_MODIFY + DIRTY_REDRAW)
  after each change. The overlay itself is confirmed (the kiln shows its "on" state after leaving
  and coming back); the live redraw is not yet confirmed. **The wall panels likely need the same call;
  flag it to the WE dev** (their runtime Lua is WE-owned).
- Status (2026-11-13):
  - Confirmed in game: Brick Fuel Furnace, Electric Furnace, the smelter's power gate, the kiln's
    "on" overlay.
  - Not yet tested in game: the smelter and kiln recipes end to end, entity table-top placement
    through KBW, 4-facing rotation, overlay depth and offset (especially on table tops), the live
    redraw, and the latest furnace tuning (99 slot, fast loading, Cancel clearing the queue).
  - Not handled: multiplayer sync.

## 42. Storage tooltip: `hasModData` called on recipe script items (found 2026-11-12 with the fuel furnace)
- **Symptom:** with the furnace's machine window open, the console logged
  `Object tried to call nil in pcall` at `KBWCommunity_StageInfo.lua:84`, under the Tikitown Power Plant
  tooltip render, 32 times in one session.
- **Cause:** the ISToolTipInv storage-line hook calls `item:hasModData()`. Machine and craft windows show
  tooltips for recipe SCRIPT items, which have no such method. The pcall catches it, but debug mode
  logs every catch.
- **Fix (ours, `container_caps.py`):** return early unless `instanceof(item, "InventoryItem")`.
- **For the WE dev:** WE's consolidated `WorldEssentialsBuildworksStageInfo.lua` (line 85) has the same
  unguarded call. Suggested one-line guard as above. We have not edited that WE-owned file.
