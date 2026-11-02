# TikiTown Container Fill-State Overlays - How They Work & What Our Buildables Need

## Mechanism (confirmed from game + mod files)

The partial/full "contents" overlay on TikiTown containers (bookshelves showing books as
they fill up) is a **vanilla B42 ContainerOverlays system**, driven entirely by the base
container sprite name. It is NOT per-buildable and needs no special buildable JSON.

Chain:
1. Drazions Tile Pack ships `common/media/lua/server/Items/WorldFiller_Tikitown.lua`.
   It builds `overlayMap` and calls `getContainerOverlays():addOverlays(overlayMap)`
   (same vanilla API as `media/lua/server/Items/StorageOverlays.lua`, `WorldFiller.lua`, etc.).
2. Each entry maps a BASE container sprite -> {partial, full} overlay sprites:
   ```lua
   overlayMap["tikitown_furniture_03_0"] = {{ name="other", tiles={"tikitown_book_overlay_01_0","tikitown_book_overlay_01_0"} }}
   -- tiles = { PARTIAL (low weight), FULL (high weight) }
   ```
3. Vanilla `ItemPicker.updateOverlaySprite(container:getParent())` runs on inventory
   transfer (ISInventoryTransferAction / ClientCommands), reads the container's used weight,
   and calls object:setOverlaySprite(partial-or-full). Engine renders it over the base.

The `tikitown_book_overlay_01` / `overlay_furniture_tterika_01` sheets have NO .tiles tile
records (3 and 2 header records only) BECAUSE they are overlay LAYERS consumed by the registry,
never placed as standalone objects. That is why they looked "empty" earlier - correct and expected.

## What this means for our buildables (the key requirement)

A built container keeps the fill-overlay behavior IF AND ONLY IF the sprite it places is a
BASE sprite that WorldFiller_Tikitown.lua registered in the overlay map. The engine then does
partial/full automatically - zero extra JSON.

### Registered base sprites (these DO get fill overlays) - correct conversion targets:
- `tikitown_furniture_01`         indices 0,1,2,3            (overlays tikitown_furniture_01_8..11)
- `tikitown_furniture_03`         0,1,2,3, 40-43, 48,49, 53-55, 58,59, 61,62,63  (book + wardrobe overlays)
- `tikitown_furniture_shelving_02` 2,3,4,5,6
- `tikitown_whistlin_dixie_01`    many (shop shelves)
- `tikitown_whatthefun_01`        40,41 (+ shelving_02 2-4 cross-ref)
- `tikitown_am_legends_01`        52,56,57,59,61,62

### CAVEAT on what we already generated (23_tikitown_furniture.json)
- Our shelving buildables use `furniture_shelving_tterika_01_*`. That sheet is **NOT in the
  overlay registry** -> those shelves will work as containers but will NOT show fill overlays.
- Our counters (`fixtures_counters_tterika_01/02`) and desks (`furniture_tables_high_tterika_02`)
  are also NOT in the registry. Counters/desks don't have a books-style fill overlay anyway,
  so that's fine for them; but the shelving choice is the wrong sheet IF fill behavior is wanted.

## Recommendation
To deliver bookshelves that fill up like the live/Knox ones, generate buildables from the
REGISTERED sheets above (esp. tikitown_furniture_01 / _03 / _shelving_02), placing the base
sprite index that the overlay map keys on. No overlay sprite goes in the buildable; the vanilla
ContainerOverlays registry + ItemPicker.updateOverlaySprite handle it at runtime.

Do NOT build tikitown_book_overlay_01 or overlay_furniture_tterika_01 as objects - they are
engine-applied overlay layers, not placeable furniture.

## 2026-08-28: overlay catalog for un-registered TikiTown shelves (user maps by eye)
- User: the Community containers fill correctly. The TikiTown shelves don't fill because no overlay was ever assigned to them. They are reskins of vanilla shelves, so vanilla overlays fit, and Drazion's TikiTown overlays can be used as well.
- Tool: `pz_craft_loops/overlay_catalog.py [sheet ...]` (default `furniture_shelving_tterika_01`). Output goes to `zomboid/tikitown/overlay_catalog/`:
  - `target_<sheet>.png`: every tile, labelled with index, name, facing and container
  - `catalog_shelves_NN.png`: every registered shelf-type base (vanilla WorldFiller.lua + Drazion WorldFiller_Tikitown.lua), shown plain, with the partial overlay and with the full overlay
  - `suggest_<sheet>_NN.png`: each target tile followed by the 3 registered bases with the closest outline and the same facing, each drawing ITS full overlay on the target art
  - `mapping_<sheet>.csv`: fill-in sheet with a YOUR PICK column and the top 3 suggestions
- First results: the tall open-front shelves (S/E) match vanilla `furniture_shelving_01` exactly (score 1.00). The backs (W/N) have no good match, because vanilla has no overlay for a shelf back. Wall shelves only match partially, so they need picking by eye.
- Next: the user fills the CSV. We then generate a `getContainerOverlays():addOverlays(...)` registration Lua in our mod from it, and restore the furniture_shelving_tterika_01 buildables that were reverted from sheet 23.
- User preference: use `overlay_furniture_tterika_01` (92 tiles with art) and `tikitown_book_overlay_01` (16 tiles) wherever they fit. The catalog groups the target tiles into SHAPES (colour variants share an outline; the backs of free-standing shelves are skipped). furniture_shelving_tterika_01 comes out as 28 shapes. Outputs:
  - `shape_<sheet>_NN.png`: one shape drawn with every tile from both preferred sheets on top. The labels show which Drazion furniture already uses each overlay ("used:").
  - `overlays_<sheet>.png`: an index sheet for each preferred overlay sheet.
  - `shapes_<sheet>.csv`: one row per shape, listing every sprite that shares it and a YOUR PICK column. A pick applies to every colour variant of that shape.
