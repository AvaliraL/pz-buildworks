# TikiTown → Knox Buildworks Expansion — Deliverable Handoff

**From:** independent contributor (investigation artifacts, not a live mod edit)
**For:** World Essentials — Knox Buildworks Expansion (KBW) dev
**Scope:** new KBW buildable definitions wrapping Drazions Tile Pack TikiTown sprites that
`20_tikitown.json` does not already cover, structured to match your existing conventions.

> None of this touches any installed mod file. These are standalone candidate `definitions/`
> files plus their EN translation entries. Drop-in if adopted.

---

## Test it in-game right now

A ready-to-run test mod is published on the Workshop:

- **Knox Buildcraft and Drazion's Tilepack Integration — https://steamcommunity.com/sharedfiles/filedetails/?id=3818232509**

Subscribe + enable it alongside KBW (and the Drazions Tile Pack dependency). It merges all
deliverables below into a single file (`99_tikitown_TEST_ALL.json`) so everything is buildable
in one load. The bundle is **test-only** — do not ship it alongside the individual files (the
ids would collide). Ship the individual numbered files instead.

---

## ⚠️ CRITICAL: replace the old handed-off files (avoid duplicate menu entries)

An **earlier, partial** handoff is already integrated in the live mod
**World Essentials — Knox Buildworks Expansion** (Workshop id `3733324672`, under
`.../42/media/KnoxBuildworks/definitions/`). Those older files must be **replaced** by the
files in this handoff, not loaded alongside them. If both load, the build menu shows **duplicate
subcategories** (e.g. both `Newburbs Interior` *and* the old `Newburbs Interior Walls`, and both
`Newburbs Exterior` *and* the old `Newburbs Walls`) and KBW logs `[WARNING] Sprite ... reused`
because the old `worldessentials.tikitown.handoff.tikitown.*` buildables claim the same sprites
as the new `tikitown.*` ones.

### Exact replacement map (live file → replace with)

| Live file in `3733324672` (OLD) | Old content | REPLACE WITH (this handoff) | New content |
|---|---|---|---|
| `27_tikitown_newburbs_interiors_accurate.json` | 240 buildables, subcat **"Newburbs Interior Walls"**, ns `handoff.tikitown.*`, category `Walls` | `27_tikitown_newburbs_interiors.json` **or** `_accurate` | 240, subcat **"Newburbs Interior"**, ns `tikitown.newburbs.*`, category `Walls and Wall Finishes` |
| `28_tikitown_newburbs_walls_accurate.json` | **150** buildables, subcat **"Newburbs Walls"**, ns `handoff.tikitown.*`, category `Walls` | `28_tikitown_newburbs_walls.json` **or** `_accurate` | **460**, subcat **"Newburbs Exterior"**, ns `tikitown.newburbs_walls.*`, category `Walls and Wall Finishes` |
| `26_tikitown_glass_accurate.json` | 110 buildables, ns `handoff.tikitown.*` | `26_tikitown_glass.json` **or** `_accurate` | 110, ns `tikitown.*` (re-grouped/renamed) |
| `29_tikitown_garages.json` | 40 buildables, ns `handoff.tikitown.*` | `29_tikitown_garages.json` | 40, ns `tikitown.garages.*` |
| `21_tikitown_walls_accurate.json` | 919 buildables, ns `worldessentials.tikitown.*` | `21_tikitown_walls.json` **or** `_accurate` | 919, same ids — safe to overwrite in place |
| `22_tikitown_doors.json` | 97 | `22_tikitown_doors.json` | 97 |
| `23_tikitown_furniture.json` | 68 | `23_tikitown_furniture.json` | 68 |
| `24_tikitown_bookshelves.json` | 1 | `24_tikitown_bookshelves.json` | 1 |
| `25_tikitown_bedroom.json` | 52 | `25_tikitown_bedroom.json` | 58 (reworked) |
| `20_tikitown.json` | 379 (original KBW_VE tikitown set) | **KEEP — do not replace** | our files are additive to this |
| `99_catalogue_finish.json` | 0 buildables (catalog terminator) | **KEEP as-is** | — |

### Net-new files (no old counterpart — just add)

These have **no** predecessor in the live mod; adding them cannot duplicate anything:

| New file | Buildables | Category / subcategory |
|---|---:|---|
| `31_tikitown_newburbs_roofs.json` (or `_accurate`) | 348 | Roofing / `Newburbs <Color> Roofs` ×6 |
| `32_tikitown_newburbs_flags.json` | 8 | Decorations / `Newburbs Flags` |
| `33_tikitown_newburbs_doors.json` (or `_accurate`) | 21 | Doors / `Newburbs Doors` |
| `34_tikitown_newburbs_windows.json` (or `_accurate`) | 13 | Windows / `Newburbs Windows` |

### Replacement rules

1. **Delete the OLD file first, then drop in the new one.** Overwriting by filename is enough for
   `21–25` (same filenames), but for the newburbs/glass/garage files the old ones use the
   `handoff.tikitown.*` id namespace while the new ones use `tikitown.*` — so simply overwriting by
   filename IS sufficient *as long as the filename matches*. The live `27/28` names match ours, so a
   straight file overwrite removes the old buildables. Confirm no second `.json` in the folder still
   defines `handoff.tikitown.*` newburbs/glass ids after the swap.
2. **Category string = `"Walls and Wall Finishes"` (standardized).** The old live files use the
   bare `"Walls"` bucket; all our wall/glass/interior/exterior files use **"Walls and Wall
   Finishes"**, which is the agreed standard. Replacing the old files with ours automatically
   migrates them to the correct bucket — no action needed. Any remaining tikitown wall buildable
   still showing under a bare `Walls` category is an old file that wasn't replaced.
3. **Translations:** replace the newburbs/glass/garage keys in the live
   `media/lua/shared/Translate/EN/IG_UI.json` + `Tooltip.json` with the regenerated ones in this
   handoff (old `handoff.*`-keyed entries become orphaned otherwise).
4. **Pick ONE cost tier** for the wall/glass/interior/exterior files (cheap vs `_accurate`) — see
   the cost-tier section below. Never load both tiers (id collision).

---

## What's in the box (ship these)

JSON definitions (place in `media/KnoxBuildworks/definitions/`):

| File | Buildables | Category | Notes |
|---|---:|---|---|
| `21_tikitown_walls.json` | 919 | Walls | 67 wall styles; each style = base + windows + door frame + corner + pillar, grouped |
| `22_tikitown_doors.json` | 97 | Doors | 2 door style sets, grouped by family |
| `23_tikitown_furniture.json` | 68 | Furniture and Appliances / Decorations | Counters, Desks; posters → Decorations and Landscaping |
| `24_tikitown_bookshelves.json` | 1 | Furniture and Appliances | "Bookshelf - In-Wall" only (see overlay note) |
| `25_tikitown_bedroom.json` | 58 | Furniture and Appliances / Decorations | Beds, Storage, Small Tables; posters → Decorations and Landscaping |
| `26_tikitown_glass.json` | 110 | Walls | 5 colors × glass panes/half-walls, grouped per color |
| `27_tikitown_newburbs_interiors.json` | 240 | Walls and Wall Finishes | 4 interior wall sheets (C1–C4); subcat **Newburbs Interior** |
| `28_tikitown_newburbs_walls.json` | 460 | Walls and Wall Finishes | 10 exterior color families; subcat **Newburbs Exterior** |
| `29_tikitown_garages.json` | 40 | Doors | 8 colors × widths 2–6; per-color groups |
| `31_tikitown_newburbs_roofs.json` | 348 | Roofing | 53 tiles + 5 roof-runs (garage-style multi-tile), ×6 colors; subcats `Newburbs <Color> Roofs` |
| `32_tikitown_newburbs_flags.json` | 8 | Decorations | floor-helper flags; subcat **Newburbs Flags** |
| `33_tikitown_newburbs_doors.json` | 21 | Doors | 18 wooden + 3 sliding glass; subcat **Newburbs Doors** |
| `34_tikitown_newburbs_windows.json` | 13 | Windows | standalone Newburbs windows; subcat **Newburbs Windows** |

**Total: 2,363 buildables, 0 duplicate ids** (per installed cost pair — see below).

> Counts reflect the CURRENT deliverables. Files `31`/`33`/`34` also have `_accurate` variants
> (same count, different recipe) — pick one tier, see below. `27`/`28` counts (240/460) SUPERSEDE
> the older live-mod counts (240 "Interior Walls" / 150 "Walls").

Translations (merge into `media/lua/shared/Translate/EN/`):

- `IG_UI.json` — buildable name keys + 114 group name keys
- `Tooltip.json` — tooltip keys

---

## Two cost tiers (install exactly ONE pair of the wall/glass files)

Walls + glass ship in two mutually-exclusive cost profiles. **Same ids, same items, same menu
entries — only the build cost/skill differs.** Load exactly one set; never both (ids collide).
See `WALL_COST_PROFILES_README.md` for the full material-by-material breakdown.

| Tier | Files | Cost model |
|---|---|---|
| **CHEAP** (default) | `21` + `26` + `27` + `28` + `31` + `33` + `34` | Uniform wood, Woodwork 4 |
| **ACCURATE** (vanilla-honest) | `21_accurate` + `26_accurate` + `27_accurate` + `28_accurate` + `31_accurate` + `33_accurate` + `34_accurate` | Per-material B42 recipes (brick→masonry, metal/glass→welding); wood Woodwork 2 |

**Single-tier files** (install regardless of chosen pair): `22` doors, `23` furniture,
`24` bookshelf, `25` bedroom, `29` garages, `32` flags. These are the same in both tiers.

Door and garage costs come straight from live KBW/WE prod recipes and are identical in both tiers:
- **Doors (22):** wood recipe — Hammer / Carpentry, Woodwork 4; 4 Plank + 4 Nails + **2 Hinge +
  1 Doorknob**. (Metal-vs-wood per-door costing is a planned later pass; all wood for now.)
- **Garages (29):** WE garage recipe — Welding, MetalWelding 5; **per tile** 3 Small Sheet Metal +
  1 metal bar/pipe + 2 Hinge, plus 1 Doorknob flat, Blow Torch + Welding Rods drained by use.
  (Paint is a planned later pass.)

---

## Conventions used (mirrors your `20_tikitown.json` / KBW_VE)

- **category** = standard KBW build-menu bucket: `Walls`, `Doors`, `Furniture and Appliances`,
  and `Decorations and Landscaping` (posters).
- **subcategory** = type family (e.g. `Brick Walls`, `Glass Walls`, `Counters`, `Beds`,
  `Storage`, `Garage Doors`). The "TikiTown " prefix was dropped to match your native naming.
- **group** = `{ "id": "worldessentials.tikitown.family_<hash>", "name": "<label>",
  "translationKey": "IGUI_WETiki_family_<hash>", "level": <int> }`.
  Members sharing `group.id` collapse into one catalogue tile with arrow-through variants
  (`level` orders them), exactly like your Refrigerators / garage-door-size groups.
  - **Walls:** one group per style = base + its windows + door frame + corner + pillar.
  - **Glass / Newburbs walls:** one group per color.
  - **Bedroom:** grouped by object type across the 4 wood colors
    (e.g. "TikiTown Fancy Floor Bed" spans Light/Pink/Blue/White Wood; "TikiTown Shelves";
    "TikiTown Drawers"; …).
  - **Doors:** grouped by style family. **Garages:** per-color (2–6 tile widths cycle within).

### Bedroom color naming
Source art colors were relabeled for clarity and de-duplicated:
`Oak → Pink Wood`, `Dark Wood → Blue Wood`, `White → White Wood`, `Light Wood` kept.
Redundant material words were stripped (e.g. "Oak Light Wood Shelves" → "Pink Wood Shelves").
Bunk-bed fabric colors (Green/Yellow/Blue/Oak Bunk Bed) are literal and were left as-is.

---

## STEP 0 — Remove the original quick-fix TikiTown implementation first

Before dropping in this package, **delete the old quick-fix TikiTown definition files** from the
live mod so the new files fully replace them (otherwise you get duplicate menu entries + the
`Sprite reused` warnings). In
`.../3733324672/mods/World Essentials - Knox Buildworks Expansion/42/media/KnoxBuildworks/definitions/`
the old quick-fix ships these TikiTown files:

| Live file (OLD quick-fix) | Action |
|---|---|
| `21_tikitown_walls_accurate.json` | **replace** (overwrite with this package's copy) |
| `22_tikitown_doors.json` | replace |
| `23_tikitown_furniture.json` | replace |
| `24_tikitown_bookshelves.json` | replace |
| `25_tikitown_bedroom.json` | replace |
| `26_tikitown_glass_accurate.json` | replace |
| `27_tikitown_newburbs_interiors_accurate.json` | replace |
| `28_tikitown_newburbs_walls_accurate.json` | replace |
| `29_tikitown_garages.json` | replace |
| `20_tikitown.json` | **KEEP** (original KBW_VE set; our files are additive) |
| `99_catalogue_finish.json` | **KEEP** (catalog terminator) |

Because every filename in this package matches the old one, a straight overwrite is enough — but
the old `27/28/26/29` buildables use the `worldessentials.tikitown.handoff.tikitown.*` id
namespace while the new ones use `tikitown.*`. Overwriting by filename removes the old buildables
(they only existed in those files). After copying, **search the definitions folder for
`handoff.tikitown` and confirm zero matches remain** — if any other `.json` still defines
`handoff.tikitown.*` tikitown buildables, delete those stragglers too.

Also replace the old translation entries: overwrite / merge this package's
`media/lua/shared/Translate/EN/IG_UI.json` + `Tooltip.json` so the old `handoff.*`-keyed strings
don't linger as orphans.

New files with no old counterpart (`30` shelving, `31` roofs, `32` flags, `33` doors, `34`
windows) are pure adds — nothing to remove for those.

## Pillar collision fix (corner-completing pillars are now walk-through)

All `pieceClass: "pillar"` buildables (the corner-completing connector pillars) were set up as
solid walls (`isThumpable: true`, no pass-through), which placed an **invisible blocking barrier**
on the connector tile. They are now **walk-through**, matching Knox's painted-wall-pillar standard
(`wall_panels` / Architecture Plus). Per stage, the pillar `object` block is now:

```json
"object": {
  "dismantable": true,
  "blockAllSquare": false,
  "canPassThrough": true,
  "canBarricade": false,
  "isCorner": true
}
```
`isThumpable` removed; `placement` and the `["W","N"]` geometry are unchanged so the corner still
renders. **Verified in-game** (walk-through + still renders + dismantles).

Applied to every `pieceClass: "pillar"` buildable across (base + `_accurate`):
- `21_tikitown_walls.json` — 67 each
- `27_tikitown_newburbs_interiors.json` — 16 each
- `28_tikitown_newburbs_walls.json` — 20 each
- `26_tikitown_glass.json` — 30 each (the `tikitown_walls_commercial_01_*_pillar` corner pillars)

**Left unchanged on purpose:**
- `pieceClass: "corner"` pieces keep `isThumpable: true` (corners should block).
- Glass-pane pillars in `26` that have **no** `pieceClass` (4-face, `cornerSprite`/`pillarSprite`)
  are untouched by design.

When regenerating any of these files, preserve the new pillar `object` block — don't let a rebuild
from an older template reintroduce `isThumpable` on `pieceClass: "pillar"` pieces.

## Log note: "build action not created direction=N" is NOT a TikiTown defect

While testing you will see lines like:
`[WorldEssentialsKnox][BuildAttempt] <id> at x,y,z direction=N not queued: build action not created`

This is **WE's own placement-feedback instrumentation**, not a problem with these deliverables.
Source: `World Essentials - Knox Buildworks Expansion/42/media/lua/client/WorldEssentialsKnoxPlacementFeedback.lua`,
which wraps `KBWBuildingObject:tryBuild` and prints this line whenever vanilla
`ISBuildingObject.tryBuild` returns falsy for a probed direction/square. It fires for **every**
buildable — vanilla tiles and other mods included (verified in-game) — on the directions/squares
that aren't the one being placed. The piece still builds normally on the valid direction.
There is no JSON change in these deliverables that suppresses it; it is cosmetic WE log noise.

Roof pieces (31) now carry the KBW-native roof schema (`roof` block: family/pitch/role, and for
4-face slopes `step`/`stepsPerLevel`/`faceByEdge`). NOTE: `faceByEdge` is **required** for
`role:"slope"` pieces — without it KBW drops them from the build menu entirely. Our Drazion sheet
authors each slope sprite to face its own compass direction, so the correct map is the IDENTITY
`{"W":"W","N":"N","E":"E","S":"S"}` (NOT KBW's `{S:E,E:S,N:W,W:N}`, which is for their differently
arranged sheet).

## Known issues / deferred (dev-side decisions)

1. **Shelf fill-overlay (books don't populate on built shelves)** — see
   `DEV_BUG_REPORT_shelf_overlays.md`. The container-overlay sprites are registered, but a
   player-BUILT shelf never triggers the overlay refresh that map-placed shelves get. Direct
   `getContainerOverlays():addOverlays()` registration AND an `updateOverlaySprite()` refresh
   trigger were both tried in-game — neither made the overlay appear. Looks like a KBW
   build/placement finalize-path gap. **Resolution:** only "Bookshelf - In-Wall" shipped in
   `24`; the other 9 overlay shelves were dropped. Bedroom storage shelves still ship as
   functional containers (no fill overlay).

2. **Floating counters** — see `DEV_BUG_REPORT_floating_counters.md`. Minor stacking/overlap
   on the floating variants; functional, shipped per owner call. Upstream tilesheet/engine.

3. **Desk L-shapes** — see `HANDOFF_desks_Lshapes.md`. Only the 2×1 and 3×1 desks are
   shipped/verified. L-shaped desk assemblies were deferred (improvised-corner tile issues).

---

## Verification state

- All 9 files parse; 0 duplicate ids across the merged bundle.
- 114 groups, every group's `level` sequence is contiguous 1..N.
- No leftover "TikiTown " subcategory prefixes; no double-word "Wall Wall" names.
- Walls / Doors / Garages / Counters / Bedroom beds / Posters / Newburbs walls+interiors / Glass
  verified buildable + rotating correctly in-game across colors.
- Translation files regenerated to match the final display names and group labels.

## Build/merge tooling (reference, not shipped)

The test bundle is produced by a merge script that reads the cheap-tier wall/glass files plus the
single-tier files and writes `99_tikitown_TEST_ALL.json`. Finalized files keep their real
category/subcategory/group (a true preview of what ships); a TEST/Complete routing path remains in
the tooling for any future not-yet-signed-off sheet. The bundle is a test convenience only — ship
the individual numbered files, not this merged file (ids would collide).
