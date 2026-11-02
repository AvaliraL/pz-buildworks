# TODO — Subcategorize color-variant wall sets BY COLOR (not by sheet)

**Status:** PARTIAL. Newburbs interiors (27) + walls (28) DONE by-color; glass (26) still OPEN.

**Done (2026-10-22):** 27 + 28 (and their `_accurate` mirrors) re-subcategorized so `subcategory`
= color name only (27 = 16 colors, 28 = 10 colors; 15 buildables each). displayNames/ids/groups/
recipes untouched. Rule encoded durably in `apply_catpass.py` (COLOR_SUBCAT dict). Verified in the
deployed bundle. Transformer: `pz_craft_loops/apply_color_subcat.py`; backups `*.PRE_COLORSUBCAT_*`.
**Still open:** `26_tikitown_glass.json` (+ `_accurate`) — decide whether to keep the Glass Walls /
Glass Half-Walls structural split or collapse to color-only.

## The issue
Several wall/glass sets pack **multiple colors into a single subcategory** (organized by atlas
sheet or by a generic bucket), so the build menu groups by sheet rather than by color. These
should be re-subcategorized **by color**, one subcategory per color, matching the dev's
color-first convention.

## Affected files (confirmed)
| File | Buildables | Current subcategories | Colors packed inside |
|---|---:|---|---|
| `26_tikitown_glass.json` | 110 | `Glass Walls` (95), `Glass Half-Walls` (15) | 5 colors (White / Black / Red / Blue / Grey) mixed in each |
| `27_tikitown_newburbs_interiors.json` | 240 | `Newburbs Interior Walls` (1 subcat) | 4 colors (C1–C4) across 4 sheets |
| `28_tikitown_newburbs_walls.json` | 150 | `Newburbs Walls` (1 subcat) | 10 colors |

> `21_tikitown_walls.json` is intentionally NOT in scope — its subcategories are material/style
> buckets (Brick / Stone / Siding / …), which is the correct organization for that set.

## What to do
- Re-subcategorize each affected file so **subcategory = color** (e.g. "Newburbs Interior Walls -
  White", or a top-level color subcat — settle the exact label format once).
- Settle real color names for the C1–C4 interior colors (confirm with art / owner).
- Keep/adjust `group{}` within each color subcategory per our standard grouping convention.
- Mirror every cosmetic change onto the matching `_accurate` files (`26_accurate`, `27_accurate`,
  `28_accurate`) — same ids, same category/subcategory/group; recipes untouched.
- The transformer `pz_craft_loops/apply_catpass.py` is the place to encode the color-subcat rule
  so it is durable on future re-runs.
