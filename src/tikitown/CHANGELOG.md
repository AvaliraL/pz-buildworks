# TikiTown → Knox Buildworks — Changelog

Changes in this handoff vs. the original quick-fix TikiTown implementation currently in the live
mod (`3733324672`, namespace `worldessentials.tikitown.handoff.tikitown.*`).

Tier shipped: **ACCURATE** (per-material B42 recipes). Bundle total (all files merged):
**2391 buildables, 0 duplicate ids.**

---

## Added (net-new — no predecessor in the live mod)

- **Roofs** — `31_tikitown_newburbs_roofs_accurate.json` — 348 buildables.
  53 roof tiles + 5 garage-style multi-tile "roof runs", ×6 Drazion colors (Light Gray, Warm Gray,
  Red Brown, Slate Green, Slate Blue, Black). Category `Roofing`; subcategories
  `Newburbs <Color> Roofs`. Uses the native KBW roof schema (`roof` block with
  `family`/`pitch`/`role`, and identity `faceByEdge` on 4-face slopes).
- **Flags** — `32_tikitown_newburbs_flags.json` — 8 buildables. Category `Decorations`,
  subcategory `Newburbs Flags`.
- **Newburbs doors** — `33_tikitown_newburbs_doors_accurate.json` — 21 buildables
  (18 wooden + 3 sliding glass). Category `Doors`, subcategory `Newburbs Doors`.
- **Newburbs windows** — `34_tikitown_newburbs_windows_accurate.json` — 13 buildables.
  Category `Windows`, subcategory `Newburbs Windows`.
- **Shelving** — `30_tikitown_shelving.json`.

## Changed

- **Newburbs interiors** (`27_..._accurate`): **240** buildables.
  Subcategory renamed from the old **"Newburbs Interior Walls"** → **"Newburbs Interior"**.
  Category standardized to **"Walls and Wall Finishes"** (was `Walls`).
  Namespace `tikitown.newburbs.*` (was `handoff.tikitown.*`). Grouped by piece type
  (Window Frames / Door Frames / etc.) instead of one giant per-color group.
- **Newburbs exterior walls** (`28_..._accurate`): grew from **150 → 460** buildables (full set).
  Subcategory **"Newburbs Walls"** → **"Newburbs Exterior"**. Category → "Walls and Wall Finishes".
  Namespace `tikitown.newburbs_walls.*`. Grouped per (color, piece type); roof-trim slope walls
  split N/W vs S/E.
- **Glass** (`26_..._accurate`): re-grouped/renamed; namespace `handoff.tikitown.*` → `tikitown.*`.
- **Garages** (`29`): namespace `handoff.tikitown.*` → `tikitown.garages.*`.
- **Bedroom** (`25`): reworked, 52 → 58 buildables.
- **Category string**: all wall/glass/interior/exterior files standardized on
  **"Walls and Wall Finishes"**.

## Fixed

- **Pillar collision (gameplay bug).** All corner-completing `pieceClass:"pillar"` pieces were
  solid (`isThumpable:true`), placing an invisible blocking barrier on the connector tile. They are
  now **walk-through**, matching the painted-wall-pillar standard:
  `{dismantable, blockAllSquare:false, canPassThrough:true, canBarricade:false, isCorner:true}`.
  Applied to `21`, `26` (commercial corner pillars), `27`, `28`. Verified in-game (walk-through,
  still renders, dismantles). `pieceClass:"corner"` pieces still block (intended); glass-pane
  pillars with no `pieceClass` left untouched.
- **Roof build-action resolution.** Roof slopes now carry the native `roof` block; the required
  `faceByEdge` uses the IDENTITY map `{W:W,N:N,E:E,S:S}` for the Drazion sheet (the KBW 30° roofs'
  `{S:E,E:S,N:W,W:N}` is sheet-specific and mis-maps these tiles / drops slopes from the menu).
- **Duplicate subcategories eliminated** by replacing the old `handoff.tikitown.*` files rather
  than loading alongside them (old build showed both "Newburbs Interior" + "Newburbs Interior
  Walls", etc., plus `Sprite reused` warnings).

## Notes / not a defect

- `[WorldEssentialsKnox][BuildAttempt] ... build action not created direction=N` is WE's own
  placement-feedback logging (`WorldEssentialsKnoxPlacementFeedback.lua`); it fires for every
  buildable, vanilla included, on rejected cursor directions. Not a TikiTown issue.

## Kept (do not remove)

- `20_tikitown.json` (original KBW_VE TikiTown set — our files are additive).
- `99_catalogue_finish.json` (catalog terminator).

---

See `HANDOFF_tikitown_deliverables.md` (STEP 0 removal + full replacement map) and
`PUSH_NOTE_for_WE_author.md` (short cover note).
