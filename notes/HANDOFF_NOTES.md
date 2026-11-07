Everything below is the full delta from the LIVE World Essentials (identical to our `we-baseline-2026-11-01`)
to our tip. It spans four earlier commits' worth of work (names/tooltips, ice machines, RC1) plus the latest
sheet work. Counts in sections 1-2 are generated; this section is hand-written from the git history.

**mod.info lines WE needs (mod.info is WE-owned, we do not touch it)**

Community submod, two new pack/tiledef pairs:

    pack=KBWCommunityIceShell
    tiledef=kbwcommunity_iceshell 8181
    pack=KBWCommunityLCouch
    tiledef=kbwcommunity_lcouch 8178

TikiTown submod, one new tiledef (tile-property patch for the tterika_02 lockers, loads after `tikitown_tiles`):

    tiledef=kbwtikitown_tterika.patch 8180

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
  `Moveables.Moveable` look (as vanilla multi-sprite pick-up does).

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

**Untouched WE-owned files**: `mod.info`, `bundled_source.txt`, `KBWCommunity_Seating.lua`, and the runtime Lua WE moved into
main World Essentials (Destroyable, MultiStorey, TableTop, TVScreens, Viewscreens).

**Test status**

- Confirmed in game: stairs, bedroom, couches and all four L couches, tterika storage, reinforced counters, fridge tiers,
  two-stage ice machines and tiers, workbench pick-up, RC1 Lua (single player).
- Also confirmed in game: multi-part pick-up / sledgehammer on multi-tile builds, generic box look for dropped parts,
  tterika stacking, the teal depth-map fix, names/tooltips pass.
- Not tested: multiplayer.
