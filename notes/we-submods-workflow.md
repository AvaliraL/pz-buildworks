---
inclusion: fileMatch
fileMatchPattern: ['pz_craft_loops/build_*.py', 'pz_craft_loops/kbw_tilepatch.py', 'pz_craft_loops/we_sync.py', 'zomboid/WE_submods/**', 'zomboid/communitytilepack/**', 'zomboid/tikitown/**']
---

# Community / TikiTown buildables now live in World Essentials

Since 2026-10-30 our standalone Workshop items are RETIRED:
- Knox Buildworks - Community Tilepack (3828080624, id `KnoxCommunityTilepack`)
- Knox Buildworks - Drazion's Tilepack (TikiTown) (3828081863, id `TikiTownKBW`)

World Essentials (Workshop 3733324672) ships the same content as bundled submods that KEEP those
mod ids: `World Essentials - Community Buildworks` and `World Essentials - TikiTown Buildworks`.

## Rules
- Never stage a mod with id `KnoxCommunityTilepack` or `TikiTownKBW` in `C:\Users\josep\Zomboid\Workshop`
  or `Zomboid\mods`. A local folder with the same id shadows WE's copy and the server rejects the join
  ("File doesn't match the one on the server"). Old staging folders are parked in
  `C:\Users\josep\Zomboid\_staging_parked\`.
- Never edit the Steam copy of WE. It breaks server checksums and Steam overwrites it on update.
- Builders write canonical builds into the project, then `we_sync.py` syncs them into
  `zomboid/WE_submods/work/<submod>/`. `zomboid/WE_submods/upstream/` is the untouched snapshot to diff
  against when handing changes to the WE dev.
- WE-owned files are never overwritten by the sync: `mod.info`, `bundled_source.txt`, and the runtime
  Lua WE moved into main World Essentials (`KBWCommunity_Destroyable/MultiStorey/TableTop/TVScreens/
  Viewscreens.lua`; WE rewrote them, e.g. MultiStorey is a stub and the load dispatcher is
  `WorldEssentialsCommunityGrid.lua`). Changes to those must be ported by hand into
  `zomboid/WE_submods/work/World Essentials (base, our files only)/` and flagged to the WE dev.
- When WE updates, refresh `upstream/` (and reconcile `work/`) before making new changes.
- `TikiTownCommunityTest` (test bundle in Zomboid\Workshop) has its own id but ships Lua with the same
  filenames as WE's runtime files. Never enable it together with World Essentials.

## Hand-offs go through git (since 2026-11-02), not zips
- Repo: `c:\Users\josep\Kiro\pz-buildworks` (private GitHub). `we/` = drop-in WE layout, `src/` = our
  builders + sources, `notes/`.
- Git = GitHub Desktop's bundled git (not on PATH; the folder changes when Desktop updates):
  `(Get-ChildItem "$env:LOCALAPPDATA\GitHubDesktop" -Directory -Filter 'app-*' | Sort-Object Name -Descending | Select-Object -First 1).FullName + '\resources\app\git\cmd\git.exe'`
- After WE updates: `_refresh_upstream.py`, then `python pz_craft_loops/export_repo.py --baseline`,
  commit `WE baseline: ...`, tag `we-baseline-<date>`.
- For a hand-off: build, then `python pz_craft_loops/export_repo.py`. It matches each JSON to WE's own
  formatting, so diffs show only real changes. Commit `we/` ALONE first, tag `handoff-<date>-<topic>`,
  then commit `src/` + `notes/` separately. Give the dev the compare link
  `https://github.com/<owner>/pz-buildworks/compare/we-baseline-<date>...handoff-<date>-<topic>`.
- The commit message says what changed and whether it was tested in game or only built and checked.
  Push only when the user asks.
