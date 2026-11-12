# TODO: Dirkies radiators as electric heaters (user, 2026-08-28)

**Sheet:** `edit_ddd_RUS_decor_house_01` (Community pack, `diederiks_tile_palooza.pack`).
**Radiator tiles:** 4-7 and 12-15, in two styles. Each tile carries only `Material=Mechanical`, `Material2=MetalScrap` and pick-up/place tools. They have no container and no heat.

## Goal

Make the radiators work like fireplaces, but heat with electricity instead of burning wood.

## Starting points found so far

- KBW already turns a tile whose `container` is `fireplace` into a native fireplace. See `KnoxBuildworks/World/NativeObjectTypes.lua`, `detectFromSprite`.
  - The radiators would need their own copied tiles, the same way as the other copies.
  - The heat should come from the grid or a generator instead of from fuel. This needs research: check how vanilla handles heat sources (`IsoFireplace`, `IsoHeatSource`) and powered appliances.
- Not started.
