# TikiTown / WE Knox Buildworks — Bug Report: player-built shelves don't update book/item overlay

Mod: World Essentials - Knox Buildworks Expansion (TikiTown shelving)
File: `media/KnoxBuildworks/definitions/24_tikitown_bookshelves.json`
Shipped buildable: only **"Bookshelf - In-Wall"** (`tikitown_furniture_03_41`), under
Furniture and Appliances / Storage. The original 10 overlay-shelf candidates
(`tikitown_furniture_01_2`, `tikitown_furniture_03_0/41/53/58/61`,
`tikitown_furniture_shelving_02_2/3/4`) were dropped to one when the fill-overlay could
not be made to work (below). Bedroom storage shelves in `25_tikitown_bedroom.json` also
function as containers without the fill overlay.

> Status: **ABANDONED / UNRESOLVED (2026-08-28).** Not fixable from the KBW buildable
> definition, and the Lua-side workarounds below were deployed and tested in-game but the
> overlay STILL never appeared on a player-built shelf. Decision: ship only "Bookshelf - In-Wall"
> (`tikitown_furniture_03_41`) as a functional storage buildable (no fill-overlay); drop the
> other 9 shelving entries. The remaining in-wall bookshelf works as storage; it simply does
> not show the cosmetic book fill-overlay.
>
> ### Final test outcome (what was tried and failed)
> 1. **Direct container-overlay registration** for the bedroom shelf sprites via a server
>    `getContainerOverlays():addOverlays(map)` call (`TikiTownBedroomShelfOverlays.lua`), keyed
>    per facing sprite, pointing at vanilla `books&misc_01` art — same mechanism the base mods
>    use. Overlay did NOT appear on built shelves.
> 2. **Trigger-refresh wrap** of the inventory transfer path to call
>    `ItemPicker.updateOverlaySprite(object)` on item add (`TikiTownShelfOverlay.lua`). No effect.
> Both Lua files were REMOVED from the deployed test bundle after the test. Source copies remain
> under `zomboid/tikitown/lua/` for reference only. Root cause is most likely a KBW dev-side gap:
> the built IsoObject's runtime sprite/parent linkage is not what `updateOverlaySprite` keys on,
> so neither registration nor an external refresh trigger takes effect. This needs a fix inside
> KBW's build/placement finalize path (see "Potential fixes" below).

---

## Symptom (confirmed in-game)

A **pre-placed / map** shelf using these sprites shows the book/item overlay that grows as
the container fills (vanilla behavior). The **player-BUILT** version of the exact same shelf
does NOT update its overlay as items are added — it stays bare regardless of contents.

## What was verified OK (so these are NOT the cause)

1. **Sprite is a registered overlay key.** All 10 placed sprites appear in the overlay map
   registered by the base Tikitown + Drazions Tile Pack mods
   (`getContainerOverlays():addOverlays(overlayMap)` in their `server/Items/WorldFiller_Tikitown.lua`).
   Verified key list includes `tikitown_furniture_01_[0-3]`, `tikitown_furniture_03_[...58,61,...]`,
   `tikitown_furniture_shelving_02_[2-6]`.
2. **The buildable defines a container.** Each has `container:{type:"shelves", capacity:40}`,
   so items can be stored and a transfer event does occur.

## ROOT CAUSE FOUND — entityCompat vs raw geometry

KBW's OWN vanilla bookcases/shelves (which DO populate the overlay) are defined via
**`entityCompat`**, not raw geometry + inline container. Example from KBW `definitions/vanilla/furniture.json`:
```json
{ "id":"kbw.vanilla.wood_bookcase_lvl2",
  "placement":{"kind":"object"},
  "stages":[{"id":"built","level":1,
             "entityCompat":{"module":"Base","entity":"Wood_Bookcase_Lvl2"}}],
  "group":{"id":"vanilla.wood_bookcase","level":2} }
```
By referencing the vanilla B42 **entity script** `Base.Wood_Bookcase_Lvl2`, the built object IS a
real vanilla bookcase entity — so it inherits the vanilla container AND the engine-wired fill-overlay
behavior automatically. No definition-side overlay call is needed.

Our TikiTown shelves (`24_tikitown_bookshelves.json`) instead use raw `geometry.faces` + an inline
`container:{type:"shelves"}`. KBW places that as a generic sprite object with NO entity-script
backing, so the engine never attaches the overlay system -> overlay never updates on fill.

### ROOT CAUSE (corrected) — the overlay DATA is registered; the built object just doesn't trigger a refresh

CORRECTION to earlier notes: the TikiTown shelf sprites ARE registered in the LIVE container-overlay
system, not only the world-gen one. Confirmed:
- Drazions `server/Items/WorldFiller_Tikitown.lua:79` -> `getContainerOverlays():addOverlays(overlayMap)`
- Tikitown  `server/Items/WorldFiller_Tikitown.lua:58` -> `getContainerOverlays():addOverlays(overlayMap)`
  Both include `tikitown_furniture_01`, `tikitown_furniture_03`, `tikitown_furniture_shelving_02`.
(`getContainerOverlays()` = fill-level overlay updated on item transfer; distinct from
`getTileOverlays()` = static world-gen decoration. Our sprites are in the CONTAINER map.)

So WHY map shelves fill but built ones don't:
The vanilla refresh in `ISInventoryTransferAction.lua` is GUARDED:
```lua
if self.srcContainer:getParent() and self.srcContainer:getParent():getOverlaySprite() then
    ItemPicker.updateOverlaySprite(self.srcContainer:getParent())   -- only refreshes an EXISTING overlay
end
if self.destContainer:getParent() then
    ItemPicker.updateOverlaySprite(self.destContainer:getParent())  -- dest path (no guard)
end
```
`ItemPicker.updateOverlaySprite(obj)` (engine) reads obj's sprite NAME, looks it up in the container
overlay map, and sets the overlay by weight. For MAP shelves this fires. For KBW-built shelves it
does not take effect -> most likely the built IsoObject's runtime sprite name / parent linkage isn't
what `updateOverlaySprite` keys on, OR the built container's `getParent()` isn't returning the object
whose sprite matches the registered key. (The overlay DATA is present either way.)

### Fix — SHIPPABLE from our deliverable (small server Lua, no entity script needed)
Add a tiny Lua that, on inventory change for a KBW-built container object whose sprite IS a registered
container-overlay key, calls `ItemPicker.updateOverlaySprite(object)` directly (bypassing the
`getOverlaySprite()` first-item guard). Hook options:
- `Events.OnContainerUpdate` / an inventory transfer post-hook, filtered to objects tagged by KBW
  (`object:getModData().KBW`), OR
- a KBW `onCreate`/finalize callback that seeds the overlay once built.
This is a real fix we can ship as `media/lua/.../TikiTownShelfOverlay.lua` IF the deliverable is
allowed to include Lua (so far it has been pure KBW definition JSON).

### Alternative (cleanest, upstream): entityCompat
If the tilepack author later adds B42 entity scripts for these shelf sprites, switch the buildables to
`entityCompat:{module,entity}` (how KBW's own vanilla bookcases get the overlay for free). No entity
script currently exists for these sprites (searched all three mods' `media/scripts/**`).

## (original analysis) Overlay refresh mechanism

The vanilla overlay refresh is driven by **`ItemPicker.updateOverlaySprite(object)`**, called
from Lua inventory events, e.g.:
- `ISInventoryTransferAction.lua` -> `ItemPicker.updateOverlaySprite(container:getParent())`
- `ISInventoryPage.lua` -> `ItemPicker.fillContainer(...)` + `ItemPicker.updateOverlaySprite(...)`
- `ClientCommands.lua` `Commands.object.updateOverlaySprite`

`updateOverlaySprite(object)` reads the sprite's overlay entry from the registered map and sets
the overlay by container weight. For MAP objects this fires correctly. For a **KBW player-built**
object, the built part does not appear to route through this same `updateOverlaySprite` refresh on
item add — so the overlay is never (re)computed. This is a KBW build/placement integration gap,
not something the buildable JSON can set (the KBW `object`/`container` schema has no overlay hook).

## Potential fixes (for the WE / KBW dev)

Pick ONE:

1. **KBW build hook (preferred).** After a KBW object with a container is built AND whenever its
   container changes, call `ItemPicker.updateOverlaySprite(builtObject)` (same call the vanilla
   inventory actions use). Simplest place: in the server/placement finalize path for container
   objects, and/or add an `OnContainerUpdate`-style trigger so it tracks fill level like vanilla.
2. **Overlay opt-in on the definition.** Add an `object.containerOverlay` (or reuse the sprite's
   registered overlay automatically) that KBW wires to `updateOverlaySprite` on the built part.
3. **Event listener.** Register a global `OnObjectAdded` / inventory-transfer listener in KBW that,
   for any built object whose sprite has a registered overlay, calls `updateOverlaySprite`.

## Notes

- Scope: the fill-overlay (books appearing as the shelf is stocked). Shelves function as
  storage regardless; only the cosmetic overlay is missing. Shipped: 1 in-wall bookshelf +
  the bedroom storage shelves (all functional containers, no fill overlay).
- No deliverable change for this; it needs a KBW-side fix (see fixes above).
- Investigation refs: vanilla `ItemPicker`/`ItemPickerJava`, `ISInventoryTransferAction.lua`,
  `ISInventoryPage.lua`, `ClientCommands.lua` (`Commands.object.updateOverlaySprite`),
  base-mod `WorldFiller_Tikitown.lua` (`getContainerOverlays():addOverlays`).
