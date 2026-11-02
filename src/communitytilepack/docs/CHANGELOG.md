# Knox Buildworks - Community Tilepack — Changelog

Workshop: https://steamcommunity.com/sharedfiles/filedetails/?id=3828080624
Mod id: `KnoxCommunityTilepack`
Requires: Knox Buildworks, Knox Buildworks Vanilla Expanded, Unofficial Mappers Community Tile Pack
(`UnofficialMappersCommunityTilePack`). No World Essentials required.

---

## 2026-08-28 — New build (first full release)

This is a new mod. It turns the Community Tilepack's tiles into Knox Buildworks buildables, so
you can build them from the Knox build menu like vanilla furniture and walls. Every piece in this
build has been checked in game for collision, function, orientation and naming.

**343 buildables** across five tile packs (Dirkies, Dylan, TK, Fears, RUS edits).

### What's buildable

| Area | Count | Highlights |
|---|---:|---|
| Counters and upper cabinets | 31 + 16 | Kitchen counters, plus upper cabinets that mount over existing counters |
| Containers | 46 + 19 + 11 + 2 | Cabinets, wardrobes, dressers, crates, pallets, shelving, medical, tool cabinets, lockers, trash cans, dumpsters |
| Walls | 44 | Dirkies, Dylan and TK wall sets |
| Doors and gates | 60 | Wooden, glass and metal doors, double-door left/right halves, door frames, 4 wooden gates |
| Fencing | 70 | High, two-storey and low fences |
| Future Room (Dylan) | 13 | Sci-Fi floor bed, laptop and coffee tables, 9 space viewscreens |
| Workbenches (Fears) | 9 | Tailoring, metalworking, electrical, carpentry, chemistry and gunsmithing benches, plus a wood gas stove, anvil and air compressor |
| Kitchen (TK) | 6 | Deli slicer, wall shelf, ice machine, deep fryer, drip coffee maker, commercial coffee machine |
| Misc | 16 | Hedges, rugs, 2 CRT TVs, exercise ball, punching bag, secret-entrance bookshelves, raccoon statue |

### Works like vanilla

- **Wall TVs** work as TVs. They show a picture when on and you can walk past them.
- **Space viewscreens:** right-click to cycle frosted → Earth → Mars. They now have north-wall
  versions too, and fit into corners.
- **Workbenches:** every bench can face both ways. The pack only drew one direction, so the
  other orientation is generated. Mirrored pieces have their lighting flipped too, so the shaded
  side swaps.
- **Kitchen appliances:**
  - The ice machine works as a powered freezer.
  - The deep fryer cooks like an electric oven (needs power).
  - The coffee makers brew, and sit correctly on counters or on the floor.
- **Wall shelf** mounts on either wall or in a corner, with a counter underneath.
- **Upper cabinets** can be built over existing lower counters.
- **Military cases:**
  - The green and white cases stack up to 6 high.
  - New Green/White Military Crate Case versions hold 100 and cost the same as the Knox military crate.
  - All four cases can be rotated. The pack only drew one orientation, so the second is
    generated (mirrored, and stacks the same way).
- **Gates** no longer need a door frame.
- **Fences** can be destroyed by zombies, like vanilla fences.
  - Broken louvered fences are low and can be vaulted.
  - Two-storey fence pieces no longer fail with "wall support missing".
- **Walk-through:** hedges, punching bag and exercise ball no longer block movement.
- **Secret bookshelves** have storage and open like a door.
- **Sledgehammer** can destroy everything in this mod. Vanilla normally refuses these tiles.

### Performance

- The TV and counter-top fixes share one square-load handler that only does work for this mod's
  own sprites (16 tile names). It's published as `KBWCommunityLoadGrid.onSquare`, so server
  optimisation mods can gate it.
- The nearby-TV scan only runs on multiplayer clients.

### Known limitations

- Hedges don't slow or rustle like vanilla hedges yet.
- North-wall viewscreens are mirrored copies, so the planet horizon slopes the other way.
- A wall TV that was on when you saved may show its old screen until you switch it off and on.
- Not included yet: double-post louvered fence, shelf overlays (books and items on shelves),
  Dirkies/TikiTown overlay decorations.
- Build costs on the Fears workbenches are placeholders until the workbench balance pass.

---

### Steam change note (paste into the upload dialog)

```
New build: 343 Knox Buildworks buildables for the Community Tilepack (Dirkies, Dylan, TK, Fears, RUS).
Counters + upper cabinets, containers, walls, doors + gates, fencing, Future Room, Fears workbenches, TK kitchen.
Working TVs, cycling viewscreens, powered ice machine / fryer / coffee makers, stackable military cases,
vaultable broken fences, zombie-destructible fences, gates without frames, sledgehammer support.
Requires Knox Buildworks, Knox Buildworks Vanilla Expanded and the Community Tilepack. No World Essentials needed.
```
