# Discord post: hand-off 2026-11-18 (major release)

Two parts: the dev message (post in the dev channel) and the player announcement.

---

## Part 1: for the World Essentials dev

**Buildworks hand-off 2026-11-18: major release**
Compare: https://github.com/AvaliraL/pz-buildworks/compare/we-baseline-2026-11-17...handoff-2026-11-18-ravencreek
Full notes: `notes/HANDOFF_NOTES.md` in the repo (top section, notes 56-66).

The new baseline is your 2026-11-17 update. In the files we track it matches 11-16, so the 11-16 hand-off (reinforced capacity sync on servers, Bushmaster manual loot) isn't merged yet. It's included again in this compare.

**1. NEW submod: `World Essentials - Raven Creek Buildworks`** (mod id `RavenCreekKBW`, `require=...,RavenCreek_B42`)
239 buildables on Simon MD's tiles as Raven Creek ships them. It has its own small tileset `KBWRavenCreek` (+ `KBWRavenCreek_on` for lit art) with depth maps, `tiledef=kbwravencreek 8174` (free across every installed mod).

**Why it's a submod that requires Raven Creek:**
- Raven Creek (`RavenCreek_B42`, Workshop 3821823518) bundles its own cut-down copy of Simon MD's tiles: `LCB42_SimonMDsTiles`, 36 sheets. Every buildable here points at those sheets, or at our copies made from that pack's art and tile properties.
- Without Raven Creek these items **won't work**. The sprites don't exist, so Knox logs `Missing sprite`, the build menu shows blank previews, and the server refuses each build. We saw exactly this with the 12 fences that are now in Knox Buildworks Expansion with no gate.
- With `require=RavenCreek_B42` the submod can't be enabled without Raven Creek, so nothing broken shows up. That's why the fences belong here, not in the Expansion.
- **Please remove `35_simonmd_fencing.json` from Knox Buildworks Expansion**, with its manifest line, its 14 `IGUI_WESimon_*` keys and the 3 `Tooltip_KBWCB_Fence*` keys (those 3 are also in Community Buildworks). The same 12 fences, with the same ids, are in this submod, so fences already built keep their link.

**The standalone Simon MD tile pack is not covered:**
- Simon MD's own B42 tile pack, **Simon MDs Tiles** (Workshop 2852704777, id `simonMDsTiles`), has 205 sheets. Raven Creek's copy has 36 of them, with the same sheet names, and both declare tiledef file number 3333.
- This submod is built for Raven Creek's copy only. It doesn't require or support the standalone pack: we haven't tested it with the standalone pack instead of Raven Creek, and the other 169 sheets aren't touched. A separate submod for the full pack could come later.
- A few of our copies use art that Raven Creek's pack lacks (the glass display cabinet's fill overlays and Simon's container fill overlays). That art is copied into `KBWRavenCreek.pack` from the standalone pack, so there's no runtime dependency on it. Credit for that art goes to Simon MD.

**2. Knox Buildworks Expansion: Vegetation.** 188 BuildingCraft trees and shrubs, all on vanilla tiles, fill your empty `10_vegetation.json`, plus a NEW `WorldEssentialsKnoxVegetation.lua` (shrub callback).

**3. Community:** Make Ice at our ice machines with Sapph's Cooking (2 NEW Lua, inert without Sapph's). The Wall Screen TV is no longer drawn over by a light switch (depth sheet only). The reinforced capacity sync to clients is included again from 11-16.

**4. Base, WE-owned file edited by hand, please merge:** `WorldEssentialsBuildworksPickup.lua`. Reinforced pieces (and our `.crate` pieces) never break on pick-up. Before, there was a 52% chance at Carpentry 3 and the item vanished with nothing returned. The Bushmaster manual loot patch is included again from 11-16.

**Test status**
- Tested in game (single player, test bundle): every Raven Creek buildable, the vegetation, and the TV fix.
- Tested against mocks only (lupa, `next` removed): the ice machines and the no-break pick-up.
- Not tested: the Raven Creek gate with Raven Creek turned off, and multiplayer for all of it.
- Held back for later: the raised / ground planter beds and their indoor plants.

---

## Part 2: player announcement

**Buildworks update: Raven Creek furniture, trees, ice and sturdier crates**

**New: Raven Creek Buildworks** (needs the **Raven Creek** map mod enabled. Without it, none of these pieces show up or work.)
Build Simon MD's furniture and decor from Raven Creek with Knox Buildworks, 239 pieces:
- **Defences:** scrap fences, heavy barrier fences (including a 3-wide section) and low barriers.
- **Doors:** scrap metal-plank doors, a secret entrance hidden in a metal cabinet, and shipping-container garage doors.
- **Storage:** military lockers, glass display counters and cabinets, a military wall gun rack, in-wall and wine shelves, bar corner shelves, sloped-wall shelves, glass-front wardrobes and clothes racks. Most also come in a sturdier Reinforced version with more room.
- **Furniture:** glass low tables, a barrel table, marble counter tops you build onto your counters, and wall benches you can sit on.
- **Neon:** neon strips in 10 colours at two heights (they light up, and joined strips switch on and off together), plus "The Italian Bowl" sign and a dancer sign.
- **Decor:** speakers, a disco ball, posters and pictures, statues, table-top figures, a chalkboard, floor wedges in wood and carpet, planter boxes, a potted rose and flower buckets (on a table they sit on the table top).

**New: trees and shrubs** (Knox Buildworks Expansion, Vegetation)
Plant small, medium, large and giant trees of 11 species, plus shrubs. You need saplings and a shovel or spade.

**New: make ice**
With Sapph's Cooking on, right-click a powered ice machine you built and choose **Make Ice** to get 2 ice cubes per use.

**Fixes**
- Reinforced containers no longer break or vanish when you pick them up, whatever your Carpentry level.
- On servers, reinforced containers now show their real capacity straight away.
- The Wall Screen TV no longer has a light switch drawn on top of it.
- The Bushmaster Auto Manual can now be found in bookstores, magazine racks, mechanic shelves and post offices, not just in Bushmaster gloveboxes.
