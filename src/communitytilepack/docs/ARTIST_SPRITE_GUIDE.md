# Sprite Art Guide: Project Zomboid B42 Tiles for Knox Buildworks

This guide is for an artist drawing new tile art (or missing orientations) for our Knox Buildworks (KBW) packs. It covers what the game expects so the art can be dropped in without rework. Everything here comes from the tiles we've already shipped (Fears workbenches, wall TVs, viewscreens). Points we haven't confirmed are marked *unverified*.

---

## 1. Canvas and tile size

| Item | Value |
|---|---|
| Tile cell | **128 × 256 px** (the game's "2x" size; every tile in the vanilla `Tiles2x` and community packs is this size) |
| Format | PNG, RGBA, **transparent background** |
| Floor footprint | A 2:1 diamond **128 px wide × 64 px tall at the bottom of the cell**: left point (0, 224), top (64, 192), right (128, 224), bottom (64, 256) |
| Height above floor | Everything above the diamond is height. A full-height wall uses nearly the whole 256 px. |

- Draw at 2x. Don't draw at 1x and upscale.
- Keep edges clean. Avoid soft or semi-transparent halos against a coloured background. The game composites on top of everything, so a dark fringe shows as a dark outline.
- Use the empty space freely. The packer crops each tile to its visible pixels and stores the offset, so unused space costs nothing.

## 2. Sheet layout and naming

- Sheets are **8 tiles wide**: 1024 px wide, and 256 px per row.
- A tile's index is `row * 8 + column`, counting from 0 at the top left.
- A tile's name in game is `<tilesetName>_<index>`, e.g. `fears_workbenches_20`.
- **Don't reorder existing tiles.** Saves and definitions refer to tiles by index. Put new tiles in empty slots or on a new sheet.
- Hand in one PNG per sheet, named after the tileset (`fears_workbenches.png`). We build the game files (`.pack` texture pack + `.tiles` definitions) from it.

## 3. Orientations (facings)

Most furniture needs **4 facings**: N, E, S, W. Some packs ship only 2 (S and E) and reuse them for the other two. The tile's `Facing` is the direction the front points:

| Facing | Front faces | Typical look |
|---|---|---|
| S | toward the bottom-left of the screen | the front/working side is the lower-left face |
| E | toward the bottom-right of the screen | the front/working side is the lower-right face |
| N | away from the viewer, toward the top-right | back side visible |
| W | away from the viewer, toward the top-left | back side visible |

### Mirror shortcut (S ↔ E, W-wall ↔ N-wall)

In this projection, **flipping a tile horizontally swaps the two world axes**:
- An S-facing object flipped left-to-right becomes the E-facing version.
- A west-wall object flipped becomes the north-wall version.

We've used this in game for the Fears workbenches, the north-wall viewscreens and the anvil/compressor. Vanilla's own E-facing tailoring and metalworking benches are drawn the same way.

When **not** to rely on the mirror:
- **Text, logos, screens with readable content:** they come out backwards.
- **Asymmetric details** that must stay on a specific side (a vice on the left-hand end, a door handle).
- **Shading:** a flip also moves highlights and shadows to the other face. It has been acceptable so far. If an object looks wrong next to vanilla furniture, draw that facing by hand and match the shading of the vanilla reference (section 9).

## 4. Multi-tile objects (beds, workbenches, big counters)

A 2-tile or 2×2 object is drawn as **one picture, then cut into one tile per floor square**.

- **Grid position (`SpriteGridPos x,y`):** x grows to the east (screen lower-right), y grows to the south (screen lower-left). Tile (0,0) is the north/west-most square.
- **Neighbouring squares on screen:** the east neighbour (x+1) sits **+64 px right, +32 px down**. The south neighbour (y+1) sits **-64 px left, +32 px down**.
- **Cutting:** each tile holds the part of the object above its own square. Parts may run right up to the cell edge where they meet the next tile. That's normal, as long as the pieces line up when reassembled with the offsets above.
- **How the halves map between facings:** S-facing benches run along x (`(0,0)` + `(1,0)`). E-facing benches run along y (`(0,0)` + `(0,1)`). For a mirrored E version, `E(0,0) = flip(S(0,0))` and `E(0,1) = flip(S(1,0))`.
- **Check:** before handing in, reassemble the pieces at the offsets above on a dark background. The seams should be invisible.

Reference layout (Fears workbench sheet):

| Bench | S tiles (grid 0,0 / 1,0) | E tiles (grid 0,0 / 0,1) |
|---|---|---|
| Tailoring | 0 / 1 | 9 / 8 |
| Metalworking | 2 / 3 | 11 / 10 |

## 5. Wall-mounted objects (TVs, screens, signs, cabinets)

- **West-wall objects** sit on the **left half** of the cell, along the edge from the left point to the top point of the floor diamond. Their `Facing` is **E**, because they hang on the west wall and face east.
- **North-wall objects** sit on the **right half**, along the edge from the top point to the right point. `Facing` is **S**.
- Keep both halves free. A corner square can hold one west-wall and one north-wall object, and they mustn't overlap.
- Mark height: wall objects mounted high up (TVs, cabinets) are flagged `IsHigh`, so counters and tables can go underneath. Draw high mounts high enough that a counter (top at roughly the `Surface` height of a vanilla counter) doesn't clip into them.

## 6. Overlay and state tiles

Some objects swap or layer sprites at runtime. Draw these as **separate tiles at exactly the same position** as the base tile, so they register perfectly.

- **TV screens:** vanilla looks for three screen overlays on the same sheet at **index +16, +32 and +48** from the TV tile: test card, broadcast/tape and off. Each is drawn only on the screen area. Our wall TVs needed generated screens because the pack had none. If you draw a TV, draw its three screens in those slots.
- **State swaps** (frosted/Earth/Mars viewscreen, open/closed doors, on/off): one full tile per state, same framing and outline, so swapping doesn't make the object jump. Give us the list of states and their order.
- **Doors and openables:** a closed and an open tile per facing. The open tile keeps the hinge in the same place.

## 7. Depth maps (B42)

B42 sorts sprites against characters and each other using a **per-tile depth map**:

- File: `DEPTH_<tilesetName>.png`, with **the same size and cell layout as the art sheet**, so cell `i` holds the depth for tile `i`.
- It's a grey-value image of the object's surfaces (lighter = closer to the camera, judging by the vanilla maps). Pixels with no art should be transparent.
- You don't have to paint these by hand. They can be generated from simple 3D boxes in the game's debug **Tile Geometry Editor**, which writes `tileGeometry.txt` and the depth map. If you can, block out each object there. Otherwise tell us and we'll do it.
- Mirrored tiles can use the mirrored depth cell. That's what we ship for the generated Fears tiles.

## 8. Things that live outside the art (we set these, but the drawing must allow for them)

| Property | What the drawing must respect |
|---|---|
| `Surface` (table/counter height, in px) | Items placed on top are drawn at this height above the floor point. Keep the top flat and at a consistent height across facings. Vanilla counters are about 30–34, beds about 23–29. |
| `IsTableTop` / `IsStackable` | The object sits on top of a table or another crate. Draw it from the floor point. The game lifts it by the surface height. |
| Collision (`solid`, `solidtrans`, `BlocksPlacement`) | Not drawn, but tell us which objects should be **walk-through** (rugs, low clutter, wall TVs) vs **blocking** (benches, beds). |
| Bed / seat positions (`seating.txt`) | Where a character sits or lies for each facing. Leave the sleeping surface clear (no props on the mattress) so characters don't clip. |
| Containers | No drawing impact. Note on the sheet whether an object should hold items. |

## 9. Matching vanilla

Put your sprite next to the closest vanilla tile in game, or on a mock-up using the vanilla `Tiles2x` art:

| Our object | Vanilla reference |
|---|---|
| Double bed | `furniture_bedding_01_16–31` ("Large Modern") |
| Single bed | `furniture_bedding_01_32–39` |
| Wall TV | `appliances_television_01_0–11`, screens at +16/+32/+48 |
| Counters | `fixtures_counters_01_*` |
| Tables / desks | `furniture_tables_high_01_*`, `furniture_tables_low_01_*` |

Check scale, line weight, top-surface height and shading direction. Compare which face is lit against a vanilla object with the same facing. We haven't measured an exact light angle *(unverified)*, so match the reference rather than a number.

## 10. Hand-in checklist

- [ ] PNG sheet(s), 1024 px wide, 128 × 256 cells, transparent background, named after the tileset.
- [ ] Every object in all required facings (or S and E, with a note saying the mirror is fine for N and W).
- [ ] Multi-tile objects split per square and checked reassembled at the offsets in section 4.
- [ ] Wall objects on the correct half of the cell (west = left, north = right).
- [ ] Overlay and state tiles registered exactly over their base tile, with the state order listed.
- [ ] Depth maps (or Tile Geometry Editor blocks), or a note asking us to generate them.
- [ ] A short list per object: name, tile indices per facing, walk-through or blocking, holds items y/n, table/seat/bed y/n.
