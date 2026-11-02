# Knox Buildworks - Drazion's Tilepack (TikiTown) — Changelog

Workshop: https://steamcommunity.com/sharedfiles/filedetails/?id=3828081863
Mod id: `TikiTownKBW`
Requires: Knox Buildworks, Knox Buildworks Vanilla Expanded, Drazion's Tilepack (`tikitown_tiles`).
No World Essentials required. Works on any map; the TikiTown map is not needed.

(For the earlier handoff history to World Essentials, see `CHANGELOG.md` in this folder.)

---

## 2026-08-28 — Standalone update

TikiTown buildables now live only in this mod. They are moving out of World Essentials (the WE
author has the removal guide). This update makes the switch safe for existing worlds.

**2391 buildables** in 14 definition files, accurate (per-material) build costs.

### Changed

- **Existing builds stay linked.** Each of the 1240 glass, Newburbs, garage, roof, flag, door and
  window pieces carries an alias for the id World Essentials used for it
  (`worldessentials.tikitown.handoff.*`). Anything built from WE's copy keeps resolving after WE drops it.
  The other 1151 pieces (walls, doors, furniture, bookshelf, bedroom, shelving) already use the
  same ids as WE's copy.
- Workshop item id set, so updates go to this page.

### Included vs World Essentials' copy

- **Everything WE's TikiTown handoff had** (2385 buildables), plus **6 bedroom pieces** WE's
  import left out: the tterika double bed (A) and single beds R4-R8.
- **Fixed: tterika double bed rest/sit position.** Drazion's seating data put you inside the bed
  facing south in every direction. All four orientations now use vanilla's matching double-bed
  positions.

### While World Essentials still has its copy

If you run this mod alongside a World Essentials version that hasn't removed the TikiTown files
yet, the console shows `Duplicate buildable id`, `Sprite ... reused` and `Duplicate alias` lines.
They're harmless: one copy of each piece loads, and everything stays buildable. They go away
once WE updates.

One thing to know: current WE hides `worldessentials.tikitown.*` buildables unless the
**TikiTown map** mod is also enabled. On a server with WE but without the map, some walls, doors
and furniture from this mod won't show until WE ships its update. Enable the TikiTown map, or
run without WE, in the meantime.

### Contents

| File | Buildables | What |
|---|---:|---|
| 21 walls | 919 | 67 wall styles: base, windows, door frame, corner, walk-through pillar |
| 22 doors | 97 | 2 door style sets |
| 23 furniture | 72 | Counters, desks, posters |
| 24 bookshelves | 1 | In-wall bookshelf |
| 25 bedroom | 58 | Beds, storage, small tables, posters |
| 26 glass | 110 | 5 colours of glass panes and half-walls |
| 27 Newburbs interiors | 240 | 4 interior wall sheets |
| 28 Newburbs exterior | 460 | 10 exterior colour families |
| 29 garages | 40 | 8 colours, 2-6 tiles wide |
| 30 shelving | 4 | Shelving |
| 31 Newburbs roofs | 348 | 6 colours: slopes, valleys, ridges, fascias, gutters, roof runs |
| 32 Newburbs flags | 8 | Floor helper flags |
| 33 Newburbs doors | 21 | 18 wooden, 3 sliding glass |
| 34 Newburbs windows | 13 | Standalone windows |

---

### Steam change note (paste into the upload dialog)

```
Standalone update: TikiTown buildables now live only in this mod (moving out of World Essentials).
Existing builds made from World Essentials' copy stay linked (legacy id aliases).
Includes 6 bedroom pieces WE never had, and fixes the tterika double bed sit/rest position.
Harmless duplicate-id log lines appear until WE ships its update. If you run WE without the TikiTown map,
enable the map until then so all pieces show.
```
