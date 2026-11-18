# BC_TakePinned (prototype)

Adds a **Take Pinned** button to the loot window controls row (next to Take All / Take Same Type).
One click moves every item whose type is pinned in Better Containers into the container that is
open in the player's inventory window.

- Requires Better Containers (`EURY_CONTAINERS`, Workshop 3586216562), version folder 42.19 or newer
  (older versions have no pinned items; the button then never appears).
- Client-side only. No server changes. Transfers are normal `ISInventoryTransferAction`s.

## Behaviour
- Source: every container in the loot window (including the floor and the BC Proximity and zombie
  corpse views) plus bags nested inside any of them. Each item is moved once.
- Destination: `getPlayerInventory(n).inventoryPane.inventory`, the container currently selected in
  the inventory window (main inventory or a bag).
- Skips: items already carried, equipped items, human corpses, "unwanted" items, force-drop heavy items.
- A pinned bag moves with its contents; its contents are not listed separately.
- Weight check against the destination before queueing (same call BC smart deposit uses). Items that
  do not fit are skipped and a "No room for N pinned item(s)" text is shown.
- Walks to each source container nearest first, without clearing the player's action queue.
- Button shows whenever at least one type is pinned. It does not scan on refresh, only on click.

## Layout
`42/mod.info`, `42/media/lua/client/BC_TakePinned.lua`, `42/media/lua/shared/Translate/EN/IG_UI.json`.

## Testing
- Mock test (lupa, `next` deleted): `python tests/test_take_pinned.py`. Covers nested bags, floor,
  proximity duplicates, own/equipped items, capacity, walk ordering, missing BC module.
  **CONFIRMED in game (user, 2026-11-17, single player): a corpse pile's pinned items, worn ones included,
  all taken in one click.**
- To try in game: copy `42` into `%USERPROFILE%\Zomboid\mods\BC_TakePinned\42`, enable it after
  Better Containers, pin a type (right-click an item, "Pin Item Type"), open a container, click the button.

## In-game test log
- 2026-11-17, 1st click: `Object 1.0 did not have __call metatable` in vanilla `ISButton:onMouseDown`
  (ISButton.lua:63): the button's `onmousedown` slot held a number. No frame from this mod in the trace.
  No installed mod redefines `ISButton` or `getButtonControl`, so the source is not known. The button is now
  our own `ISButton` (explicit empty `onmousedown`, cleared on every layout), `getTextOrNull` is called with
  the key only. Errors inside the run are caught and logged as `[BC_TakePinned] error: ...` (the only
  console output left; the click/scan diagnostic lines used during testing were removed after the confirm).

- 2026-11-17, corpse pile: the diagnostic log showed 332 items in the BC corpse view, 34 of a pinned type, 32
  of them skipped as `equipped`. Items a zombie corpse wears report `isEquipped`; they are now taken (the
  player's own equipped items stay excluded, as carried). The "Taking pinned items: 1$s" text came from
  filling `%1` by hand in a Translator string; translated texts now go through `getText(key, n)`.

## Known gaps
- Button only appears in the loot window controls row. If CleanUI is active, Better Containers skips
  its own override of that row; the vanilla row is used, which should still show it (unverified).
- No hover highlight of the items that will move (Take Same Type has one).
- Vehicle trunks are handled like BC smart deposit does; untested.
