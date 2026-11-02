# TODO — Redo poster build cost

**Status:** OPEN (next cost pass).

## Current state
All 6 posters are set to a placeholder recipe of **1 Nail only** (no plank/tool skill):
`BuildWoodenStructureSmall`, `tool_hammer` + `source_material_1 = 1 Base.Nails`, no skill.

Affected buildables:
- `23_tikitown_furniture.json`
  - `tikitown_walls_decoration_08_60` — U.S. Parks Ranger Special Forces Emblem
  - `tikitown_walls_decoration_08_62` — U.S. Park Ranger Rapid Force Poster
- `25_tikitown_bedroom.json`
  - `tikitown_furniture_bedroom_0{1..4}_61` — {Light Wood / Pink Wood / Blue Wood / White Wood} Bedroom Poster

All are category **Decorations and Landscaping / Posters**.

## What to do
Pick the real poster recipe (match a vanilla / KBW prod poster or wall-decoration recipe) and
apply it to all 6. Likely something small (e.g. a sheet of paper / glue / a nail), but confirm
against a live prod example rather than guessing. Keep it identical across both cost tiers
(posters are single-tier).
