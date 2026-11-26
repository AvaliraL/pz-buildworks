# 2026-11-24 hand-off: Discord text

Under Discord's 2000-character limit.

---

## Dev note

**Buildworks hand-off, 2026-11-24: two small Lua fixes**

Compare (your 11-24 update as the base):
https://github.com/AvaliraL/pz-buildworks/compare/we-baseline-2026-11-24..handoff-2026-11-24-takepinned-mp

Thanks for the merge, it took everything we had open. Your edits to our files (Make Ice water, Wall Screen checks, stage sync, Pickup) are our working copy now too, and our builds won't overwrite them.

**1. Take Pinned grabs only 1-2 items per click on the server** (`WorldEssentialsTakePinned.lua`)
A player reported it on zombie corpses. Your loop stops when the queue is empty and the last item isn't in the destination. In MP the client's transfer doesn't move the item: the server does, and its sync arrives after the action has left the queue (sometimes as a new item object). So a good transfer looks like a cancel. The fix counts the item as moved when it's in the destination *or* gone from its source, and waits up to 3 s for the sync before treating it as cancelled.
Tested against mocks only: your file moves 1 of 8 with MP timing, the fix moves 8 of 8, and a cancel still stops. Not tested on a server yet.

**2. Reinforced pieces can break on pick-up again** (`WorldEssentialsBuildworksPickup.lua`)
The new `self._kbwNoBreak=priorNoBreak` inside the `instanceItem` wrapper reads a nil global (`priorNoBreak` is local to `pickUpMoveableInternal`), so it clears the flag. Vanilla calls `instanceItem` before `doBreakTest`, so the break roll is back for pieces with a storage record. The fix removes that one line. Checked only, not tested in game.

**Question:** Raven Creek now ships inside the Knox Expansion, not as its own submod. Is that the layout to keep? If so, we'll build Raven Creek changes into the Expansion.

Details: `notes/HANDOFF_NOTES.md`, notes 76 and 77.
