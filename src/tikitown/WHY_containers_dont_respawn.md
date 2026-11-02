# Why some containers never respawn loot (TikiTown & other custom maps)

Symptom: in a room, one container reliably respawns loot on the server's respawn
interval, but the other containers in the same room never do — and it's always the
same one that works.

This is not random. It's the interaction of two Build 42 systems.

## 1. How loot respawn actually works in B42

Loot respawn is controlled by two sandbox settings:
- **`HoursForLootRespawn`** — how long before a container is eligible again.
- **`MaxItemsForLootRespawn`** — a container only respawns if it currently holds
  **fewer than this many items** (default is quite low).

Respawn is **per-container**, gated on the square being **unseen** for the interval,
AND the container being at/under the item threshold. Critically, respawn re-rolls the
**same distribution list** that container was originally filled from — keyed by the
container's **type/sprite** within the room's distribution.

## 2. How custom maps key their distributions (the cause)

Custom maps and mods (TikiTown included) define room loot as
`SuburbsDistributions.<roomName> = { <containerType> = { ... } }`, keyed by the
container **sprite/type name**: `shelves`, `counter`, `metal_shelves`, `crate`,
`fridge`, `freezer`, `locker`, `cardboardbox`, `desk`, etc. (TikiTown uses all of
these.)

For a container in that room to receive loot — on initial spawn **and** on respawn —
its in-map sprite must map to a container type that the room distribution defines a
list for. The match is by the container's **loot sprite/container name**, resolved
through the game's container-name mapping.

## 3. Why only one container respawns

When a room has several visually-similar containers but they were **placed with
different underlying container sprites/types**, only the type(s) that the distribution
explicitly lists get loot. The rest get **nothing** — not on first spawn and not on
respawn.

But the reason it *looks* like "one respawns, the rest are permanently empty" (rather
than "one has loot, rest never did") usually comes down to one of these:

1. **Mismatched container type on the tile.** The map cell was placed with a container
   sprite whose container name the room distribution doesn't have a key for
   (e.g. the room defines `shelves` and `counter`, but a shelf was stamped as a
   generic `shelvesmetal`/`wallshelf`/`displaycabinet` variant that isn't keyed).
   That container is never in the distribution, so it never fills — the one that DOES
   match its keyed type is the only one that spawns and respawns.

2. **The other containers already hold >= MaxItemsForLootRespawn items.** If players
   left items (or the container spawned with junk that never gets removed), respawn is
   suppressed for those containers forever, while the one that gets emptied to zero
   keeps qualifying. This is the most common non-mod cause and matches "always the
   same container" exactly.

3. **The container isn't a lootable container at all.** Some decorative map objects
   look like containers but aren't registered as loot containers; they can never
   respawn.

4. **`isShop = true` / one-shot lists.** A distribution list flagged for a special
   spawn (shop crates, some procedural lists) can be excluded from the normal respawn
   pass, so it fills once and never again while a sibling normal container keeps
   respawning.

## 4. Which one it is here — how to tell

For the TikiTown case (and the general pattern), diagnose in this order:

1. **Check the working vs dead container's TYPE.** In debug mode, hover/inspect each
   container and note its container name. If the dead ones report a type that is NOT a
   key in the room's `SuburbsDistributions` entry (shelves/counter/metal_shelves/etc.),
   that's cause #1 — a placement/keying mismatch. This is the likely culprit for a
   *modded custom map*, because the mapper stamped a container variant the
   distribution author didn't add a list for.

2. **Empty a dead container completely and wait one respawn interval unseen.** If it
   now fills, it was cause #2 (item-count threshold), not a keying bug.

3. **Check for `isShop`/procedural-only lists** on the container's list (cause #4).

## 5. Most likely explanation for TikiTown specifically

TikiTown keys its rooms by container type (21x `shelves`, 29x `counter`, 21x
`metal_shelves`, 14x `crate`, 12x `fridge`, etc.). When a room visually has, say, four
shelving units but only the ones stamped as the exact `shelves`/`metal_shelves` type
in the distribution get a list, the others are **unkeyed** and will never spawn or
respawn — while the single keyed one spawns initially and keeps respawning. That
matches your report precisely: **one specific container works, the identical-looking
neighbors never do.**

The fix (map/distribution side, for the map author):
- Either restamp the dead containers to a keyed container type, OR
- add the missing container-type keys to that room's `SuburbsDistributions` entry so
  every container present in the room has a matching list.

Neither is a player-side/server-config fix; it requires the mod's distribution or map
cells to be corrected. If it turns out the dead containers ARE keyed correctly, then
it's the `MaxItemsForLootRespawn` threshold (cause #2) and is fixable purely via
sandbox settings (raise the threshold / ensure containers get emptied).
