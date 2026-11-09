Everything below is the full delta from the LIVE World Essentials (identical to our `we-baseline-2026-11-01`)
to our tip. Sections 1-6 were in earlier hand-offs (names/tooltips, ice machines, RC1, multipart couches).
Sections 7-14 are NEW in `handoff-2026-11-08-full-sheets` (full TikiTown wall sheets, naming pass, generator
cabinet, KBW component recipes, Spray Paint loot). We re-checked WE's 11-08 update: it changed none of the files
we track, so the baseline did not need a refresh. Counts in sections 1-2 are generated; the rest is hand-written
from the git history.

**mod.info lines WE needs (mod.info is WE-owned, we do not touch it)**

Community submod, two new pack/tiledef pairs:

    pack=KBWCommunityIceShell
    tiledef=kbwcommunity_iceshell 8181
    pack=KBWCommunityLCouch
    tiledef=kbwcommunity_lcouch 8178

TikiTown submod, one new tiledef (tile-property patch for the tterika_02 lockers, loads after `tikitown_tiles`):

    tiledef=kbwtikitown_tterika.patch 8180

NEW in this hand-off, TikiTown submod: one pack + tiledef for the copied wall-overlay / soundproof / props tiles
(5 tilesets, each under the game's 512-tile limit):

    pack=KBWTikiTownWallOverlays
    tiledef=kbwtikitown_walloverlays 8179

**New folders in this hand-off** (nothing existed there before, so copy them over whole):

- TikiTown submod: `42/media/scripts/` (generator cabinet items), `42/media/textures/` (generator icons),
  and `42/media/lua/shared/Translate/EN/ItemName.json`.
- World Essentials (base): `42/media/scripts/WorldEssentials_SprayPaint_Items.txt` and
  `42/media/lua/server/Patches/WorldEssentialsSprayPaintDistribution_Server.lua`.
- Knox Buildworks Expansion: `42/media/scripts/WorldEssentials_KnoxComponentRecipes.txt`
  (recipe EN strings to merge into WE's Recipes.json: `notes/WorldEssentials_KnoxComponentRecipes_Recipes_EN.json`).

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
- tterika_02 needs a tile-property patch to stack and place correctly: `kbwtikitown_tterika.patch.tiles` (additive merge onto
  `furniture_storage_tterika_02`: IsStackable/IsTable on the footlocker and small cabinets; MoveType=Object and corrected
  Facing for the freestanding lockers, which the pack tags as wall objects) plus `KBWTikiTown_TileFixes.lua`, because a
  patch cannot remove a property: it unsets `IsTableTop` on the footlocker at runtime (vanilla never stacks onto a square with
  `IsTableTop`). Needs the tiledef line above.
- L couches use `KBWCommunityLCouch`: single-tile copies of the Comfy end pieces WITHOUT their 2-tile sprite grid (orange is
  a recolour of pink). With the originals the ends ghost as the full 2-tile couch and cannot be picked up.
- `common/media/depthmaps/DEPTH_d_location_sofaking.png`: sofaking depth map with the teal and orange corner cells cleared
  (only those colours carried depth data; purple and pink had none and looked right). Fixes the odd teal look, confirmed in game.

**5. Multi-part pick-up / sledgehammer (new this hand-off)**

- `KBWCommunity_MultiPart.lua` / `KBWTikiTown_MultiPart.lua`: KBW places each tile of a multi-tile build as its own object
  (`modData.KBW.groupId`/`partCount`). Vanilla only moves tiles together when sprites share a tile-property sprite grid, so
  picking up or smashing one tile of a bed left the rest. This wraps `ISMoveableSpriteProps:canPickUpMoveable/pickUpMoveable`
  and `ISDestroyStuffAction:complete` so all tiles of the group go together; part items drop on the floor with the generic
  `Moveables.Moveable` look (as vanilla mu lti-sprite pick-up does).

**6. Workbenches (Fears, file 56) become real workstations**

- `KBWCommunity_BenchTools.lua` (shared, NEW) registers the stage property `kbwcbBenchTools` and wraps
  `ISInventoryPaneContextMenu.getContainers` plus the B42 craft panels' `updateContainers`: while the player is adjacent to a
  configured bench, one detached (never saved, never shown) virtual container holding one of every member of the bench's core
  tool tags is added to the craft-panel query only. All recipe variants and tool alternates resolve.
- Same file wraps `ISHandcraftAction:getDuration`: crafting at a bench of the recipe's own category is 10% faster
  (`BT.SPEED_MULTIPLIER = 0.90`).
- Benches are recognised by their tile as well as by `modData.kbwcbBenchTools`, so a bench that was picked up and placed again
  (a plain moveable object; vanilla does not carry our modData across) keeps its tools. The sprite and category tables are
  generated into the Lua from the workbench definitions.
- Anti-duplication: the B42 craft flow moves tools from nearby containers into the player's inventory and only returns them
  when the craft completes, so cancelling a craft (walking away) left a bench tool in the inventory. Bench tools are marked
  (`modData.kbwcbBenchTool`); once the player has no craft or transfer queued, any marked item they hold (bags included) is
  removed and the bench's tool set rebuilt (on craft stop/perform, plus an EveryOneMinute backstop). Marked items cannot be
  transferred anywhere but the player's main inventory.
- `KBWCommunity_BenchMenu.lua` (client, NEW): right-click a bench to open the vanilla craft window on its category.
- Definitions: the six benches (tailoring, metalworking, electrical, carpentry, chemistry, gunsmithing) gain the
  `kbwcbBenchTools` stage property and a build cost of one of each core tool (any variant accepted). Chemistry has no B42 craft
  category, so it gives a mortar and pestle and opens Medical.
- New IG_UI labels `IGUI_KBWCB_Bench_<Category>`.
- Generated from `pz_craft_loops/bench_tools.py`.

---

## New in `handoff-2026-11-08-full-sheets`

**7. CALL-OUT: Knox Buildworks component recipes + lootable Spray Paint (tested in game)**

Full write-up with the recipe table and test plan: `notes/HANDOFF_KnoxComponentRecipes_WE.md`.

- `World Essentials - Knox Buildworks Expansion/42/media/scripts/WorldEssentials_KnoxComponentRecipes.txt` (NEW folder
  `scripts/`): six craft recipes turning vanilla-only inputs into KBW components:
  - **Asphalt mixture:** bucket + 2 uses gravel bag + 2 uses sand bag + 1.0 L petrol.
  - **Thin copper pipe:** Blacksmith 5, at a forge.
  - **Rubber seals:** from a tire piece.
  - **Plastic sheet:** tarp + epoxy + any lighter.
  - **Insulation foam:** sponge + glue or epoxy.
  - **Refrigerant bottle:** copper kettle + 1250 uses of a propane tank, MetalWelding 3.

  It goes in the Expansion because it names `KnoxBuildworks.*` items, and the Expansion requires KBW.
- Recipe names: merge `notes/WorldEssentials_KnoxComponentRecipes_Recipes_EN.json` (6 keys) into
  `World Essentials/42/media/lua/shared/Translate/EN/Recipes.json`. The keys are the **bare recipe name**, as in vanilla
  (`"Forge_Cup"`) and KBW (`"KBWCutPlasticSheet"`). Heads-up: WE's existing repair recipes use a `Recipe_` prefix
  (`Recipe_WERepair...`). The game adds that prefix itself, so those names most likely show as raw ids. Worth a look
  (not verified).
- **Spray Paint** (base folder): `WorldEssentialsSprayPaintDistribution_Server.lua` mirrors every vanilla `PaintCyan` loot entry
  with a same-weight `SprayPaint` entry (6 vanilla lists; other mods' lists are picked up too), on `OnPostDistributionMerge`,
  additive and idempotent. `WorldEssentials_SprayPaint_Items.txt` overrides the vanilla item (full block, only `Weight` 1.0 → 0.5).
  Vanilla has no Spray Paint loot at all, yet KBW's 12 graffiti buildables each use 1 of its 8 uses.
- Tested in game (single player): all 6 recipes craft; Spray Paint spawns (the patch logged 8 mirrored entries with our mod list).

**8. TikiTown wall sheets, full coverage (files 39-42, all NEW)**

- `40_tikitown_lower_walls.json` (945): 3/4, 2/3, 1/2, 1/3, 1/4 height walls built from the pack's own tiles 72-91, as real
  walls (panel, corner, pillar). One group card per sheet and piece type, with the heights inside it. A lower wall
  refuses an edge that already has a wall, window, door or fence: KBW otherwise swaps a player-built wall out
  (`KBWCommunityFreeEdge.OnIsValid` / `OnIsValidCorner`, in the OverlayGuard Lua).
- `39_tikitown_wall_overlays.json` (945): the same heights as decorative overlays on an existing wall. These use OUR OWN COPIES
  of the tiles (`KBWTikiTownWallOverlays1..3`, overlay-only properties). The pack's tiles are typed as walls, so KBW refused
  them as overlays ("the wall edge is already taken"), and re-tagging the pack's tiles would change every map-placed copy
  too. Needs the new mod.info lines above.
- `41_tikitown_roof_slope_walls.json` (1701): 27 roof-slope / gable walls per sheet (tiles 30-71, 96-117). They are modelled
  on the in-game-confirmed Newburbs roof slope walls: the sheet's own wall cost and health, kind wall, one card per sheet.
  W/N pairs are matched by shape and validated against the confirmed Newburbs pairs.
- `42_tikitown_garage_trim.json` (189): garage door frame Left / Center / Right per sheet (tiles 64-69). They are modelled on the
  confirmed Newburbs garage door frames, at the sheet's own door-frame cost.
- 63 sheets covered (the 60 used for lower walls + the 3 commercial cinder-block sheets). Deliberately NOT built:
  - wall fixtures (vents, meters): art only, no tile properties;
  - siding posts;
  - the tents / Melos ruins / four tterika sheets (own layouts). Their main wall pieces already exist.

  See `src/tikitown/TODO_wall_sheet_leftovers.md`.
- Window / door-frame walls no longer merge into the plain corner sprite. Two "(Window 2)" walls meeting at a corner used to
  become the solid corner tile, because every variant carried the plain wall's `cornerSprite`. Their `cornerSprite` is
  removed (716 pieces in file 21); they keep `pillarSprite` (the gap filler). Plain walls still join as before.

**9. Naming pass (TikiTown; names, group titles and subcategories only, no cost changes)**

- **69 wall styles** get descriptive names from their art instead of "Style N", e.g. "Pink Brick Wall", "Palm Leaf Wallpaper
  Wall (Door Frame)", "Dark Green Brick Lower Wall Corner (1/2)". Lower walls, overlays, roof slopes and garage trim follow the
  same style names.
- The 12 sheets under plain "Walls" moved into Brick / Stone, and cement became "Concrete Walls".
- **Doors (97):** descriptive names, regrouped from two per-sheet cards into 12 type cards (Panel, Six-Panel, Framed Glass,
  Kickplate, ...). The second door of each mirror pair is "(Mirrored)"; handedness is a TODO.
- **Beds and furniture cards:** beds are named by colour, and furniture group cards dropped the "TikiTown " prefix.
- **Spelling:** "Grey" became "Gray" everywhere (vanilla spelling).
- Translation tables regenerated: group card titles now always follow the definitions.

**10. TikiTown props-14 (NEW `38_tikitown_props14.json`) and soundproofing (NEW `37_tikitown_soundproof.json`)**

- props-14: desk microphone, small and large mixer boards, ATM, thermos coffee dispenser, styrofoam cups (1 plank), and the
  Electrical Cabinet Generator (section 11).
- Soundproofing (wall panel, pillar, corner, window, door frame) uses OUR OWN COPIES of the tiles (`KBWTikiTownSoundproof`):
  IsMoveAble removed, Facing fixed, door-trim types, the corner as an NW corner. The earlier approach patched the pack's tiles
  globally (map-placed copies changed too); that is gone, and the pack's soundproof tiles are untouched.
- `KBWTikiTown_TableTop.lua` (NEW, own guard): table-top pieces (mic, mixers, cups, coffee dispenser) sit on the floor when
  placed on the floor, not at counter height. It is the TikiTown counterpart of the Community TableTop fix; WE's copy only runs
  with the Community submod.

**11. Electrical Cabinet Generator (TikiTown, built and checked; not yet confirmed in game)**

- A real vanilla generator built by KBW (`nativeObject` generator).
  - Items `TikiTownKBW.ElectricalCabinetGenerator` / `...Mirrored`, one per facing: the game maps a placed generator's
    sprite to its item.
  - Stats: wear 1 in 40, sound radius 15, weight 40, own 32x32 icons.
  - Cost: the yellow generator as WE balances it, with every skill +1 (Electricity 9, MetalWelding 6; alternative 9 / 7).
- Second facing = our mirrored tile `KBWTikiTownProps_0`.
- `KBWTikiTown_GeneratorRotate.lua` (shared, NEW): vanilla can only drop a generator, so this adds a "Rotate" world option.
  It swaps the placed generator's sprite in place, keeping fuel, condition and on/off state. In MP the client asks, and the
  server swaps and calls `transmitUpdatedSpriteToClients`. Tested against mocks (single player, MP client and MP server
  paths), not in game.

**12. Community: L couch corners, multi-part pick-up**

- L couch corners use copied tiles (`KBWCommunityLCouch` 32-47) for the depth fix (pack + tiledef 8178, already listed above).
- `KBWCommunity_MultiPart.lua` / `KBWTikiTown_MultiPart.lua`: the dropped parts of a multi-tile build use the flat-pack box icon
  (`Item_Flatpack`), and a group places back as one piece. Parts drop like vanilla.

**13. OverlayGuard Lua (Community + TikiTown, NEW files)**

- `KBWCommunity_OverlayGuard.lua` / `KBWTikiTown_OverlayGuard.lua`:
  - KBW's overlay cursor must also pass WE's own wall-attachment check, so an invalid spot shows red instead of erroring
    mid-build.
  - `KBWCommunityCornerTrim.OnIsValid`: inside-corner trims and soundproof corners need a wall edge on both sides.
  - `KBWCommunityFreeEdge` (section 8).
- Same code in both submods, install-guarded.

**14. KBW load fix: definition order (affects anyone shipping large files)**

- KBW sorts every buildable with Kahlua's recursive quicksort (`Registry:list()`). With our ~2,000 new pieces in generation
  order, it hit Kahlua's stack limit ("Stack overflow" in `partition_comp`), and KBW never finished loading. Files 39-42 now
  list their buildables in a fixed md5(id) order, which brings the sort depth back to what KBW + VE alone produce. Confirmed in
  game. The root cause is reported for the KBW dev: `notes/DEV_BUG_REPORT_registry_sort_overflow.md`.

**Also for the WE dev**: `notes/DEV_BUG_REPORT_ZVirusVaccine_dependency.md`. WE's 2026-11-08 update crashes the game before the
menu if Zombie Virus Vaccine is not enabled: its lab recipes use that mod's timed actions, and it is only in `loadModAfter`,
not `require`. The PAW / MedievalZ repair recipes log missing-item errors the same way when those mods are absent.

**Untouched WE-owned files**: `mod.info`, `bundled_source.txt`, `KBWCommunity_Seating.lua`, and the runtime Lua WE moved into
main World Essentials (Destroyable, MultiStorey, TableTop, TVScreens, Viewscreens).

**Test status**

- Confirmed in game: stairs, bedroom, couches and all four L couches, tterika storage, reinforced counters, fridge tiers,
  two-stage ice machines and tiers, workbench pick-up, RC1 Lua (single player).
- Also confirmed in game: multi-part pick-up / sledgehammer on multi-tile builds, generic box look for dropped parts,
  tterika stacking, the teal depth-map fix, names/tooltips pass.
- This hand-off, confirmed in game (user, single player, test bundle; everything marked Completed):
  - the component recipes and Spray Paint loot;
  - the lower walls, including the replace-refusal;
  - wall overlays, soundproofing, props-14, the naming pass;
  - the roof slope walls and garage trim;
  - L couch corners;
  - the KBW load-order fix.
- Built and checked, NOT yet confirmed in game:
  - the Electrical Cabinet Generator, its "Rotate" option (mock-tested) and its pick-up / re-place;
  - the window / door-frame corner fix;
  - the W/N slope direction of each roof slope wall when rotated.
- Not tested: multiplayer.
