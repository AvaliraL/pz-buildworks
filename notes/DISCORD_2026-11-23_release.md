# 2026-11-23 release: Discord text

Each part is under Discord's 2000-character limit. Post the dev note parts in order, then the player text.

---

## Part 1 of 2 (dev note)

**Buildworks hand-off, 2026-11-23**

Compare (your 2026-11-23 update as the base, so it shows only our changes):
https://github.com/AvaliraL/pz-buildworks/compare/we-baseline-2026-11-23...handoff-2026-11-23b-no-neon

Use the **23b** tag. An earlier tag from today (`handoff-2026-11-23-overlays-repack`) still had a neon card patch for your Expansion, which we've withdrawn. 23b removes it, and your Expansion `manifest.json` is exactly yours again.

Your 11-19 and 11-23 updates each changed one file we track, both your own (`WorldEssentialsReadIcons.lua`, `WorldEssentialsCommunityGrid.lua`). We had no edits there, so the compare keeps your versions.

Everything below is **confirmed in game** (test bundle, single player):

**TikiTown (file 39)**
- A **Top (1/4)** band for all 63 wall overlay sheets. It's the full wall minus the 3/4 overlay, so the two meet with no gap. It sits in each sheet's existing card.
- The **26 Newburbs colours** (10 clapboard, 16 interior paint) as overlays at 3/4, 2/3, 1/2, 1/3, 1/4 and Top, cut to the same shapes. New subcategories "Newburbs Exterior / Interior Wall Overlays".
- Three new tilesets appended to `kbwtikitown_walloverlays.tiles`. The existing 12 keep their names and firstIds. No new mod.info lines.

**Texture packs repacked (all our packs)**
Our packer left 1 px between sprites, vanilla leaves 2. Zoomed out, the game samples the half-size page, so edges blended with the next sprite: dashed seam lines. Now 2 px. Sprite names are unchanged, so placed pieces aren't affected. Needs a full restart.

---

## Part 2 of 2 (dev note)

**Repack, continued**
- Packs: TikiTown `KBWTikiTownWallOverlays`; Community `IceShell`, `LCouch`, `TVScreens`, `Viewscreens`, `Fears`, `Cases`; Raven Creek `KBWRavenCreek`.
- Fears pack: sprite edges also copied 2 px into the padding, which fixes a seam where the 2-tile workbenches meet.
- Dylan pegboard gun racks: depth is now the wall plane 12 nearer (their guns 14), because they drew behind wall trim.

**Community**
- NEW file 74: Dirkies foundation trim (plain + capped brick), brick columns, diamond-plate / concrete / plank floors, hall tree bench, wooden crate.
- NEW file 75: TK hammock, couch, lawn chair, shell chair, lawn lounger, plank garage door (3 and 4 wide).
- NEW `KBWCommunity_WallScreenPlacement.lua` (shared): the Wall Screen TV can be placed (moveable Place) on wall squares that have counters or upper cabinets, and they can be placed next to it. Vanilla's own rule otherwise.

**Still open from earlier hand-offs** (they show again as new files): the ice machine menu + Make Ice action (Community) and the Bushmaster manual distribution (base).

Full details are in `notes/HANDOFF_NOTES.md`, notes 70-73 and 75. Note 70 is an FYI about your snow Lua errors.

---

## Player text

**Building update**

- **Wall overlays, top band:** every wall overlay set now has a **Top (1/4)** piece that fills the strip above the 3/4 overlay. Mix colours freely: any top fits on any 3/4.
- **Newburbs wall overlays:** all 26 Newburbs colours, clapboard and interior paint, at five heights plus the top band. Look under *Decorations and Landscaping > Newburbs Exterior / Interior Wall Overlays*.
- **New Dirkies pieces:** brick foundation trim, brick columns, diamond-plate, concrete and plank floors, a hall tree bench and a wooden crate.
- **New TK pieces:** a hammock, an outdoor couch, lawn chairs and a lounger, and a plank garage door (3 and 4 wide).
- **Fixes:**
  - No more dashed seam lines on wall overlays and other pieces.
  - No seam in the middle of the Fears workbenches.
  - Pegboard gun racks no longer hide behind wall trim.
  - The Wall Screen TV can now be placed next to counters and upper cabinets.
- **Tip:** to remove a flat wall overlay, right-click the wall and choose **Remove <name>**. The sledgehammer only hits the wall.

After the update, restart the game completely so the new art loads.
