# Discord post: hand-off 2026-11-18 (major release, incl. the 18b follow-up)
Each part below is one Discord message (checked under 2000 characters). Post them in order.

=== PART 1 ===
**New hand-off: Raven Creek Buildworks (NEW submod), Knox Expansion vegetation, ice machines, no-break reinforced pick-up 📦 (1/5)**

New baseline = your 2026-11-17 Workshop update. In the files we track it's the same as 11-16, so the 11-16 hand-off (reinforced capacity sync on servers, Bushmaster manual loot) isn't merged yet. It's in this diff again.
One compare for everything (direct comparison, so your Expansion `IG_UI.json` shows only our added lines):
https://github.com/AvaliraL/pz-buildworks/compare/we-baseline-2026-11-17-full..handoff-2026-11-18b-veg-keys-ice
Notes (top section, 56–68): https://github.com/AvaliraL/pz-buildworks/blob/main/notes/HANDOFF_NOTES.md

Not included: the raised / ground planter beds and their indoor plants (held back for another round).
Your consolidation is respected: no per-submod OverlayGuard/MultiPart/Pickup/StageInfo Lua, and your mod.info and tooltip keys are kept.
mod.info: Community / TikiTown / Expansion need no new lines. The new submod ships its own `mod.info` (id `RavenCreekKBW`, `pack=KBWRavenCreek`, `tiledef=kbwravencreek 8174`, free across every installed mod; collision check clean).

Please port (your files):
• `WorldEssentialsBuildworksPickup.lua` (base): `isUnbreakable()` plus a one-time wrap of `doBreakTest`, so our `.reinforced` / `.crate` pieces never break on pick-up.
• Knox Buildworks Expansion: please **remove `35_simonmd_fencing.json`**, its manifest line, its 14 `IGUI_WESimon_*` keys and the 3 `Tooltip_KBWCB_Fence*` keys (those 3 are also in Community). The same 12 fences, same ids, are in the new submod, so fences already built keep their link.
• Expansion `10_vegetation.json`: your empty placeholder, now filled (drop-in), plus NEW `WorldEssentialsKnoxVegetation.lua`, and 233 vegetation keys appended to the end of your `Translate/EN/IG_UI.json`.

=== PART 2 ===
**Why Raven Creek Buildworks is a submod that requires Raven Creek 🏚️ (2/5)**
• Raven Creek (`RavenCreek_B42`, Workshop 3821823518) bundles its own cut-down copy of Simon MD's tiles (`LCB42_SimonMDsTiles`, 36 sheets). Every piece here points at those sheets, or at our copies made from that pack's art and properties.
• **Without Raven Creek these items don't work.** The sprites don't exist, so Knox logs `Missing sprite`, the menu shows blank previews, and the server refuses the build. That's what the 12 fences do today in the ungated Expansion. `require=RavenCreek_B42` stops the submod from enabling instead.
• **Not covered: Simon MD's own B42 tile pack**, "Simon MDs Tiles" (Workshop 2852704777, `simonMDsTiles`, 205 sheets). Raven Creek's 36 sheets use the same names, and both packs declare tiledef file number 3333. This submod doesn't require or support the standalone pack, isn't tested with it in place of Raven Creek, and doesn't touch its other 169 sheets. That could be its own submod later.
• The few textures Raven Creek's copy lacks (glass cabinet and container fill overlays) are copied into `KBWRavenCreek.pack` with credit to Simon MD, so there's no runtime dependency on the standalone pack.

=== PART 3 ===
**New: Raven Creek Buildworks, 239 pieces on Simon MD's tiles (files 01–09) (3/5)**
• Defences: scrap fences (12), heavy barrier fences including the 3-wide section, low barriers.
• Doors: scrap metal-plank doors, a secret entrance in a metal cabinet, shipping-container garage doors (3 and 4 wide).
• Storage (26 with a Reinforced version): military locker, glass display counter and cabinet, military wall gun rack, in-wall and wine shelves, bar corner shelves, sloped-wall shelves, honeywood glass-front wardrobes, wall benches with shoe storage (you can sit on them, via seating.txt), clothes racks. Simon's own fill overlays (bottles, books) are registered for our copies only.
• Furniture: glass low tables, a barrel table, marble counter tops built onto any counter (KBWRavenCreek_CounterTops.lua).
• 💡 Neon: strips in 10 colours (Simon's cyan and pink, plus 8 recoloured, one per vanilla bulb; each takes its own bulb), two heights, run / end / inside corner / corner cap. Real light switches. Joined strips of the same colour and height toggle together (KBWRavenCreek_NeonLink.lua). Plus "The Italian Bowl" and the dancer sign.
• Decor: speakers, a disco ball, Retro Wave pictures and movie posters, statues, table-top figures (they sit on tables via the vanilla table-top flags plus KBWRavenCreek_TableTop.lua), chalkboard, wood and carpet floor wedges, planter boxes, a potted rose, flower buckets (table-top).

=== PART 4 ===
**New: vegetation, ice machines; fixes (4/5)**
• 🌳 **Vegetation (Knox Buildworks Expansion):** 188 BuildingCraft trees and shrubs on vanilla tiles. Small / medium / large / giant trees of 11 species (one card per size and species) and shrubs, with BuildingCraft's sapling and digging-tool costs. Every piece and group has a `translationKey` in your scheme (`IGUI_WEKBW_veg_…`); the 233 texts are appended to your Expansion `IG_UI.json` (CRLF, 2-space indent, no collisions). Before, Knox logged 564 "Missing translation" warnings. The key list alone is `src/knox_expansion/IG_UI_vegetation_EN.json` if you'd rather merge by hand.
• 🧊 **Ice machines make ice (Community):** right-click a powered Knox-built ice machine, choose Make Ice, get 2 of Sapph's ice cubes, with Sapph's IceBreaking sound. The character's emitter returns 0 for that sound, so the machine's square plays it. Inert without Sapph's Cooking (no option, no item). 2 NEW Lua: KBWCommunityMakeIceAction (B42 timed action; `complete()` runs on the server) and KBWCommunity_IceMachineMenu.
**Fixes**
• Reinforced pieces never break on pick-up. Before, vanilla's roll ((10 − Carpentry) × 7.5%, 52% at Carpentry 3) deleted them and gave nothing back (player report).
• Wall Screen TV: a light switch on the same wall no longer draws over it (depth sheet only).
• Again from 11-16: reinforced capacities reach clients on servers (`sendObjectChange(CONTAINERS)` after KBW applies the stage), and the Bushmaster Auto Manual spawns in 5 loot lists.

=== PART 5 ===
**Under the hood 🔧 (5/5)**
• The new submod has its own tileset `KBWRavenCreek` plus `KBWRavenCreek_on` (lit art), with depth maps `DEPTH_KBWRavenCreek(_on).png`, the minimal `tileGeometry.txt` the depth loader needs, and `seating.txt` for the benches. Raven Creek ships no depth maps, so every copy gets its own: a matched vanilla cell, wall planes for wall pieces, or a computed box for the bar corner post.
• All copies are our own tiles (fixed indices), so Raven Creek's map tiles are untouched.
• `KBWRavenCreek` is now exactly at the game's 512-tiles-per-tileset limit. Over that, the game refuses the whole tiledef ("invalid number of tiles"). The builder now stops before that happens; the next batch goes into a new tileset in the same file.
• Neon: Simon's strip runs end one row short and rely on the next piece's overhang. Our copies carry the full line in their own square, so the joins stay solid.

FYI, Knox: a tileset over 512 tiles fails the entire `.tiles` file, not just the extra tiles. Worth knowing if anything else grows that far.

Tested in single player: every Raven Creek piece, the vegetation, the TV fix, and the ice machines with their sound (with Sapph's Cooking). Tested against mocks only: the no-break pick-up. Built and checked only: the vegetation keys (the warnings aren't re-checked in game yet). Not tested: the Raven Creek gate with Raven Creek turned off. MP not tested.


# Player announcement (separate channel; one message)

=== PLAYERS ===
**Buildworks update: Raven Creek furniture, trees, ice and sturdier crates**

**New: Raven Creek Buildworks** (needs the **Raven Creek** map mod. Without it, none of these pieces show up or work.)
Build Simon MD's furniture and decor from Raven Creek with Knox Buildworks, 239 pieces:
- **Defences:** scrap fences, heavy barrier fences (including a 3-wide section) and low barriers.
- **Doors:** scrap metal-plank doors, a secret entrance hidden in a metal cabinet, and shipping-container garage doors.
- **Storage:** military lockers, glass display counters and cabinets, a military wall gun rack, in-wall and wine shelves, bar corner shelves, sloped-wall shelves, glass-front wardrobes and clothes racks. Most also come in a sturdier Reinforced version with more room.
- **Furniture:** glass low tables, a barrel table, marble counter tops you build onto your counters, and wall benches you can sit on.
- **Neon:** strips in 10 colours at two heights (they light up, and joined strips switch on and off together), plus "The Italian Bowl" sign and a dancer sign.
- **Decor:** speakers, a disco ball, posters and pictures, statues, table-top figures, a chalkboard, floor wedges in wood and carpet, planter boxes, a potted rose and flower buckets (on a table they sit on the table top).

**New: trees and shrubs** (Knox Buildworks Expansion, Vegetation)
Plant small, medium, large and giant trees of 11 species, plus shrubs. You need saplings and a shovel or spade.

**New: make ice**
With Sapph's Cooking on, right-click a powered ice machine you built and choose **Make Ice** for 2 ice cubes per use.

**Fixes**
- Reinforced containers no longer break or vanish when you pick them up, whatever your Carpentry level.
- On servers, reinforced containers show their real capacity straight away.
- The Wall Screen TV no longer has a light switch drawn on top of it.
- The Bushmaster Auto Manual can now be found in bookstores, magazine racks, mechanic shelves and post offices, not just in Bushmaster gloveboxes.
