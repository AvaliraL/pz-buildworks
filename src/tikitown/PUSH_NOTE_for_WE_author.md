# Push note — TikiTown update for the WE / Knox Buildworks author

Three things in this update. Full detail is in `HANDOFF_tikitown_deliverables.md`; this is the
short version.

## 1. Roofs (NEW — `31_tikitown_newburbs_roofs.json` + `_accurate`)
- 348 buildables / tier: 53 roof tiles + 5 garage-style "roof runs", ×6 Drazion colors
  (Light Gray / Warm Gray / Red Brown / Slate Green / Slate Blue / Black).
- Category `Roofing`; subcategories `Newburbs <Color> Roofs`. Grouped by piece type
  (Slopes / Valleys / Inners / Ridge Caps / Fascias / Apex / Gutters / Run), small cycles.
- Uses your native roof schema: per-piece `roof` block (`family`/`pitch`/`role`, and for the
  4-face directional slopes `step`/`stepsPerLevel`/`faceByEdge`). **faceByEdge is the IDENTITY
  map** `{"W":"W","N":"N","E":"E","S":"S"}` for the Drazion sheet (its slope sprites face their
  own compass direction) — NOT the `{S:E,E:S,N:W,W:N}` from the 30° roofs, which is sheet-specific
  and would mis-map our tiles. Without faceByEdge, role:slope pieces drop out of the menu, so it
  must stay.
- No old counterpart in the live mod — safe to just add.

## 2. Catalog rebuild / replace the old partial handoff
The live mod (`3733324672`) already carries an **earlier partial** handoff under the
`worldessentials.tikitown.handoff.tikitown.*` namespace. Loading it alongside the new files makes
**duplicate subcategories** + `Sprite reused` warnings. Replace the old files with the new ones —
exact file-by-file map + rules in the handoff doc under "CRITICAL: replace the old handed-off
files". Headline deltas:
- `27` interiors: old "Newburbs Interior Walls" (240) → new **"Newburbs Interior"** (240)
- `28` exterior: old "Newburbs Walls" (**150**) → new **"Newburbs Exterior"** (**460**)
- Category string standardized to **"Walls and Wall Finishes"**.
- KEEP `20_tikitown.json` and `99_catalogue_finish.json`.

## 3. Pillar collision fix (gameplay bug — verified in-game)
Corner-completing `pieceClass:"pillar"` pieces were solid (`isThumpable:true`), leaving an
invisible blocking barrier on the connector tile. Now walk-through, matching your painted-wall
pillar standard:
```json
"object": { "dismantable": true, "blockAllSquare": false, "canPassThrough": true, "canBarricade": false, "isCorner": true }
```
Applied to `pieceClass:"pillar"` in `21`, `26` (the commercial corner pillars), `27`, `28`
(base + `_accurate`). `pieceClass:"corner"` pieces still block (intended). Glass-pane pillars with
no `pieceClass` left untouched. Don't let a template rebuild reintroduce `isThumpable` on pillars.

## Try it
Test bundle on the Workshop (merged, test-only — ship the individual files, not the bundle):
**Knox Buildcraft and Drazion's Tilepack Integration — id 3818232509.**
Current bundle: 2391 buildables, 0 duplicate ids.
