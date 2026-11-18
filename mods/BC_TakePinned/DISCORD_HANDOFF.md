**BC_TakePinned: "Take Pinned" button for Better Containers** (separate mod, not part of WE)
https://github.com/AvaliraL/pz-buildworks/tree/main/mods/BC_TakePinned (commit a0dde02)

**What it does**
Adds a **Take Pinned** button to the loot window controls row, next to Take All / Take Same Type. One click moves every item whose type you pinned in Better Containers (right-click an item > Pin Item Type) into the container open in your inventory window (main inventory or a bag).
- Pulls from every container in the loot window: the floor, the BC Proximity and zombie corpse views, and bags nested inside them.
- Walks to each source nearest first. It adds to the action queue and does not clear it.
- Checks the destination's weight first. Items that don't fit are skipped with a "No room for N pinned item(s)" message.
- Skips items you carry or wear, human corpses, unwanted items, and force-drop heavy items. Items worn by a zombie corpse are taken.
- The button only shows when at least one type is pinned. It scans on click, not on every refresh.

**Requirements**
Better Containers (`EURY_CONTAINERS`, Workshop 3586216562), version 42.19 or newer. Older versions have no pinned items, so the button never appears. Client-side only, no server changes. Transfers are normal `ISInventoryTransferAction`s.

**Install**
Copy `mods/BC_TakePinned` into `%USERPROFILE%\Zomboid\mods\` and enable it after Better Containers.

**Fixes made during testing**
- Clicking threw `Object 1.0 did not have __call metatable` in vanilla `ISButton.lua:63`, because the button's `onmousedown` held a number. The mod now builds its own button and clears `onmousedown` on every layout.
- The message showed "1$s". It now uses `getText(key, n)` for counts.
- Only 1 of 34 pinned items was taken from a corpse pile, because worn items report as equipped. Corpse-worn items are now taken. The player's own equipped items are still left alone.
- Test logging is removed. The only console output left is `[BC_TakePinned] error: ...` if something fails.

**Test status**
- Tested in game, single player (2026-11-17): a corpse pile's pinned items, worn ones included, all taken in one click.
- Mock tests (lupa, Kahlua-safe): 18/18 pass (`tests/test_take_pinned.py`).
- **Not tested**: multiplayer, vehicle trunks, and CleanUI (with CleanUI, BC skips its own row override and the vanilla row should still show the button).

**Known gaps**
- `mod.info` points to `poster.png`, which isn't made yet.
- No hover highlight of the items that will move (Take Same Type has one).
