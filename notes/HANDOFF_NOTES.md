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

## 8. One question

- `World Essentials/42/media/scripts/WorldEssentials_SprayPaint_Items.txt` (Spray Paint weight
  1.0 -> 0.5) was left out of your merge, with no note. The loot distribution went in. It's still
  in this hand-off. Drop it again if that was intentional.

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
