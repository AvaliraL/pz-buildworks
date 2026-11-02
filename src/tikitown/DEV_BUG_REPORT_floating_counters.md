# TikiTown / WE Knox Buildworks — Bug Report: Floating Counters stack on the same tile

Mod: World Essentials - Knox Buildworks Expansion (TikiTown counters)
File: `media/KnoxBuildworks/definitions/23_tikitown_furniture.json`
Affected buildables: the 15 **"Floating Counter"** variants from sheet
`fixtures_counters_tterika_02` (ids ending `_floating`, e.g.
`worldessentials.tikitown.fixtures_counters_tterika_02.modern_floating`).

> Status: LEFT AS-IS (not fixed) pending WE-dev decision. All OTHER counters
> (`fixtures_counters_tterika_01.*` and non-floating `_02`) are unaffected and are
> verified working. The floating variants are shipped as-is (functional storage; they
> just allow stacking). All counters sit under **Furniture and Appliances / Counters**.

---

## Symptom (confirmed in-game)

A Floating Counter can be built on a tile that already holds another Floating
Counter (or another object). Multiple counters occupy the exact same square,
overlapping. Normal counters correctly reject a second placement on an occupied
tile.

---

## Root cause

KnoxBuildworks' placement validator decides "square already occupied / solid
placement blocked" from the **sprite's own tile properties**, not from anything
the buildable definition can set.

In `media/lua/shared/KnoxBuildworks/Validation/Placement.lua`
(`Placement.validate`, the per-footprint-tile collision block):

```lua
local occupiedBlocks = target:getProperties():has(IsoPropertyType.BLOCKS_PLACEMENT)
    and placement.allowSharedSquare ~= true
if props and not isHighWallObject(props)
    and (occupiedBlocks or target:isSolid() or target:isSolidTrans())
    and (props:has(IsoFlagType.solidtrans) or props:has("BlocksPlacement")) then
    ... return "solid placement blocked"
end
```

The final gate `props:has(IsoFlagType.solidtrans) or props:has("BlocksPlacement")`
reads `props` from the **placed sprite** (`spriteProps(tile.sprite)`). The
`fixtures_counters_tterika_02` floating-counter sprites carry **neither**
`solidtrans` nor a `BlocksPlacement` property in the tilesheet, so this gate is
never satisfied — the engine never considers the tile occupied by one, and a
second one places freely.

Confirmed the schema cannot patch this from the definition JSON:
- `media/lua/shared/KnoxBuildworks/Definitions/StageConfig.lua` maps the full
  supported `object` block: `isThumpable`, `isProp`, `canBePadlocked`,
  `breakSound`, `cornerSprite`→corner, `pillarSprite`→pillar. There is **no**
  occupancy / blocks-placement / solid key.
- `media/lua/shared/KnoxBuildworks/Geometry/Matrix.lua` (`cellFromToken`) does
  support a per-cell `blocks` flag and a `properties` table, but the collision
  gate above reads the SPRITE's properties, not the cell's — so a definition
  `properties:{BlocksPlacement:true}` is not consulted by that check.
- The one definition-reachable blocker path, `if tile.blocks and not tile.sprite`
  (the `isFree` test), only fires for **spriteless** blocker cells, not for the
  counter's own sprite tile.

Net: this is a **tilesheet property omission** on the `fixtures_counters_tterika_02`
floating-counter sprites, not something fixable in the buildable definition.

---

## Potential fixes (for the WE / tilesheet author)

Pick ONE:

1. **Tilesheet fix (preferred, root cause).** Add the `BlocksPlacement` property
   (or `solidtrans`) to the floating-counter sprites in
   `fixtures_counters_tterika_02` via the tile definitions
   (`.tiles` / tiledef). Once the sprite reports `BlocksPlacement`, the existing
   Placement.lua gate rejects stacking automatically — no definition change
   needed. This matches how vanilla/normal counters already behave.

2. **KnoxBuildworks schema enhancement.** Add an `object.blocksPlacement` (or
   `placement.occupiesTile`) key that `StageConfig.sprite` maps through and that
   `KBWBuildingObject:create` writes onto the built part's properties as
   `IsoPropertyType.BLOCKS_PLACEMENT`. Then the definition could opt-in per
   buildable. (Note `KBWBuildingObject.lua` already reads
   `IsoPropertyType.BLOCKS_PLACEMENT` into `self.blockAllTheSquare` at ~line 1121,
   so the write side is the only missing half.)

3. **Definition workaround (hacky, not recommended).** Add a second, spriteless
   footprint cell `{dx:0,dy:0,blocks:true}` on the counter's tile so the
   `tile.blocks and not tile.sprite` → `isFree` path rejects stacking. Risk: may
   also reject the counter's own first placement on tiles with minor floor
   clutter, and changes multi-tile footprint semantics. Needs in-game testing.

---

## Notes

- Scope: 15 buildables, all `fixtures_counters_tterika_02 *_floating`. They ship in the
  deliverable under Furniture and Appliances / Counters alongside the working counters.
- No change was made to the deliverable for this issue; the floating counters
  remain stackable until the tilesheet (fix #1) or KBW schema (fix #2) is updated.
- Investigation references (KnoxBuildworks workshop build): `Validation/Placement.lua`,
  `Definitions/StageConfig.lua`, `Definitions/Properties.lua`, `Geometry/Matrix.lua`,
  `server/.../KBWBuildingObject.lua`.
