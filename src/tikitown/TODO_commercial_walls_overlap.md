# TODO — Commercial wall sprite overlap (walls_commercial_tterika* vs tikitown_*_commercial)

**Status:** OPEN — confirm before/while working on commercial wall sheets.

## The issue
The `walls_commercial_tterika*` sheet(s) overlap with the TikiTown commercial wall sprites
(`tikitown_walls_commercial_0X` used in `26_tikitown_glass.json`, and the
`tikitown_commercial_walls_add_0X` used in `21_tikitown_walls.json` under "Commercial Walls").
Some sprites appear in BOTH sources, so there's a risk of shipping the same wall twice (duplicate
in-game entries) or picking the wrong atlas.

## What to do
Before implementing / editing any commercial wall set, confirm **which exact sprites** overlap:
- Compare the `walls_commercial_tterika*` sprite indices against those already used in
  `21_tikitown_walls.json` (`tikitown_commercial_walls_add_*`) and `26_tikitown_glass.json`
  (`tikitown_walls_commercial_*`).
- Decide the canonical source for each overlapping sprite; do NOT ship the same wall from two
  files (would create duplicate catalogue entries / possible id or sprite collisions).
- Record the resolved mapping here once confirmed.
