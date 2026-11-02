# TikiTown Walls + Glass — Cost Profile Pairs (choose ONE)

These deliverables ship in **two mutually exclusive pairs**. A server operator installs
**exactly one pair**. Both pairs cover the same buildables (same in-game items, same sprites,
same menu entries) — only the build **cost/skill** differs.

## ⚠️ Load exactly ONE pair. Never both.

Each buildable has the **same `id`** in both pairs (so a pair is a true drop-in swap). If both
pairs are loaded at once, every buildable id collides and Knox Buildworks will silently keep
only one definition per id (load-order dependent, unpredictable). Install one pair, delete/omit
the other.

| Pair | Files | Cost model |
|------|-------|------------|
| **CHEAP** (default / current) | `21_tikitown_walls.json` + `26_tikitown_glass.json` + `27_tikitown_newburbs_interiors.json` + `28_tikitown_newburbs_walls.json` | Uniform wood, Woodwork 4 |
| **ACCURATE** (match vanilla) | `21_tikitown_walls_accurate.json` + `26_tikitown_glass_accurate.json` + `27_tikitown_newburbs_interiors_accurate.json` + `28_tikitown_newburbs_walls_accurate.json` | Per-material vanilla B42 recipes; wood walls at Woodwork 2 |

> **27 / 28 (Newburbs interior + exterior walls)** are wood/plaster walls. Their ACCURATE
> variant differs from CHEAP ONLY by carpentry skill (Woodwork 4 → 2, the vanilla wall skill);
> materials, action, ids, and menu grouping are identical, so each is a clean drop-in swap.

### Files that are SINGLE-TIER (same in both pairs — install regardless of chosen pair)

These are not part of the material-honesty split and ship once:

- `22_tikitown_doors.json` — all doors use the vanilla **wood door** recipe
  (Hammer / Carpentry, Woodwork 4; 4 Plank + 4 Nails + **2 Hinge + 1 Doorknob**). Metal-vs-wood
  per-door costing is a planned later pass; everything is wood for now.
- `29_tikitown_garages.json` — garage doors use the vanilla WE garage recipe
  (Welding, MetalWelding 5): **per tile** 3 Small Sheet Metal + 1 metal bar/pipe + 2 Hinge,
  plus 1 Doorknob flat, Blow Torch + Welding Rods drained by use. Paint is a planned later pass.
- `23_tikitown_furniture.json`, `24_tikitown_bookshelves.json`, `25_tikitown_bedroom.json` —
  carpentry furniture, single cost.

## Cost difference by material

| Buildable group | CHEAP pair | ACCURATE pair (vanilla B42) |
|---|---|---|
| Wood-type walls (wallpaper, bathroom, decorative, siding, interior, plaster, exterior, wooden, generic, tents, vanilla-add) | Hammer + 2 Plank + 4 Nails, Woodwork 4 | Hammer + 2 Plank + 4 Nails, **Woodwork 2** (BuildWallHammer / Carpentry) |
| Brick + cement walls (16) | Hammer + 2 Plank + 4 Nails, Woodwork 4 | **Mason's Trowel + 2 Concrete (mortar) + 4 ClayBrick, Masonry 2** (BuildWallNoTool / Masonry; wall can be plastered) |
| Stone walls (2) | Hammer + 2 Plank + 4 Nails, Woodwork 4 | **Mason's Trowel + 2 Concrete + 6 StoneBlock, Masonry 2** (BuildWallNoTool / Masonry) |
| Metal/industrial + commercial-add walls (5) | Hammer + 2 Plank + 4 Nails, Woodwork 4 | **3 Small Sheet Metal + 4 Blow Torch + 4 Welding Rods, MetalWelding 3** (BuildWallMetal / Welding) |
| Glass windows + half-wall (35) | Hammer + 2 Plank + 4 Nails, Woodwork 4 | **3 Small Sheet Metal + 4 Blow Torch, MetalWelding 3** (BuildWallMetal / Welding; welded storefront window) |

Notes on the ACCURATE pair (these are literal vanilla B42 recipes, not invented numbers):
- Blow Torch and Welding Rods are **drained by use** (not consumed as whole items) and are not
  recorded as recipe inputs, exactly as vanilla metal walls/window frames behave.
- No welding mask is required — vanilla metal wall/window builds don't use one.
- Brick walls carry the vanilla `canBePlastered` on-create behavior.
- Glass windows become **welded metal window frames** in the accurate pair; they keep the
  `windowGlass` break behavior (intact → shattered → empty frame) via the on-create callback.

## Why cheap exists

The current Knox Buildworks tiles were given a quick uniform wood cost without per-material
balancing. The CHEAP pair preserves that (easy, carpentry-only). The ACCURATE pair restores the
material-honest costs the base game uses, so brick needs masonry, metal/glass needs welding, etc.

## Install

1. Pick a pair (CHEAP or ACCURATE).
2. Place its **four** wall/glass `.json` files (21 + 26 + 27 + 28, with or without the
   `_accurate` suffix depending on the pair) in the mod's KnoxBuildworks `definitions` folder.
3. Ensure the **other** pair's four files are NOT present (same ids would collide).
4. Install the single-tier files (22 doors, 23 furniture, 24 bookshelf, 25 bedroom, 29 garages)
   regardless of which pair you chose.
