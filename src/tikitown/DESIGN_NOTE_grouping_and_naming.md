# TikiTown — Design Note: Final Knox grouping + naming for multi-piece sets

Status: DESIGN TARGET for final implementation (not yet applied to the dev deliverables).
The dev test deliverables currently ship each piece (wall/window/fence, corner, pillar,
door frame) as a SEPARATE flat buildable so each can be tested in isolation. For the
shipped mod they should be consolidated per the scheme below.

---

## Goal

Each "wall family" (one material/color/style) should appear as ONE grouped entry in the
Knox build menu, with the straight edge, corner, pillar (and door frame / window variants
where applicable) selectable within that single entry — the way vanilla groups a set.

Reference: vanilla **Refrigerators** (and KBW's own grouped entities, e.g.
`kbw.vanilla.metal_countercorner_lvl1/_lvl2` which share
`group.id = "vanilla.metal_countercorner"`). One catalogue tile, cycle through members.

Example target: **"Blue Glass Fence"** group contains:
- Blue Glass Fence (straight edge)
- Blue Glass Fence Corner
- Blue Glass Fence Pillar

...instead of 3 (or 8+) separately-named flat entries per color.

---

## Mechanism (KnoxBuildworks `group` field)

KBW buildables support a `group` block (seen on vanilla-compat defs):

```json
"group": {
  "id": "tikitown.glass.commercial_01.fence",   // shared id = members grouped together
  "name": "Blue Glass Fence",
  "translationKey": "IGUI_KBW_Group_tikitown_glass_commercial_01_fence",
  "level": 1                                      // order within the group
}
```

All members that share `group.id` collapse into one catalogue entry; `level` (or an
ordering key) controls the in-group cycle order. Confirm exact semantics against the KBW
Registry/Catalogue code before shipping — this note records intent, not a verified impl.

---

## Proposed grouping

### Glass commercial (per color sheet `tikitown_walls_commercial_0X`)
One group PER STYLE (7 styles x 5 colors = 35 groups). Each group = the window/edge piece
+ its corner + its pillar (+ door frame for the styles that have one).

| Style base | Group name (color = Blue e.g.) | Members |
|---|---|---|
| _0  | Blue Glass Framed Window        | edge _0, corner _2, pillar _3, door frame _8 |
| _16 | Blue Glass Full Window          | edge _16, corner _18, pillar _19 |
| _24 | Blue Glass Fence                | edge _24, corner _26, pillar _27 |
| _32 | Blue Glass Full Window (Tall)   | edge _32, corner _34, pillar _35 |
| _48 | Blue Glass Frameless Pane       | edge _48, corner _50, pillar _51 |
| _56 | Blue Glass Frameless + Lower    | edge _56, corner _58, pillar _59 |
| _72 | Blue Glass Multi-Pane Grid      | edge _72, corner _74, pillar _75 |

### Material walls (`21_tikitown_walls.json`, per sheet)
One group PER SHEET: straight wall + its corner (_2) + pillar (_3) + the windows/door
frame variants that belong to that sheet. Group name = the sheet's wall style name
("Brick Wall - Style 1", etc.).

### Bedroom / furniture
Not affected by this note (each furniture object is already its own 4-facing buildable).

---

## Interim naming (until grouping lands)

Because grouping is not yet applied, corners/pillars currently share a generic name per
color (e.g. every pillar = "Blue Glass Pillar"), which makes them hard to match to their
parent wall. INTERIM FIX (applied to the dev deliverable): tag each corner/pillar with its
style so it reads e.g. "Blue Glass Fence Corner", "Blue Glass Multi-Pane Pillar". Style
tags: Framed / Full / Fence / Full Tall / Frameless / Frameless Lower / Multi-Pane.

Once the `group` consolidation is implemented, these per-piece display names become the
in-group member labels and the generic group name ("Blue Glass Fence") is what shows in the
catalogue.

---

## TODO for final implementation
- [ ] Verify KBW `group` field semantics (Registry/Catalogue) + the correct ordering key.
- [ ] Add `group` blocks to glass corner/pillar/edge/doorframe members (35 groups).
- [ ] Add `group` blocks to material-wall members per sheet.
- [ ] Add `IGUI_KBW_Group_*` translation entries for each group name.
- [ ] Collapse the flat per-piece entries into their groups; keep ids stable for saved builds.
- [ ] Re-test the build menu shows one entry per family with corner/pillar selectable within.
