# Buildworks for World Essentials (Community + TikiTown)

Knox Buildworks buildables for the Community Tilepack and Drazion's Tilepack (TikiTown), as
shipped inside **World Essentials** (Workshop 3733324672) as the bundled submods
`World Essentials - Community Buildworks` and `World Essentials - TikiTown Buildworks`.

## For the World Essentials dev

`we/` is in World Essentials' own folder layout. Files there drop in place over the same paths
in WE's `mods/` folder.

- Commits tagged `we-baseline-<date>` are WE's shipped files, untouched.
- Each later commit is a change from us. A hand-off is a **compare link** from the baseline tag
  to that commit: it shows exactly which files and lines changed.
- `we/World Essentials (base, our files only)/` holds only the base-mod files we have touched
  or track. It is not the whole base mod.
- Lua is Kahlua-safe (no `next()`, `goto`, `//`, `debug`). Each commit message says whether a
  change was tested in game or only built and checked.

## Layout

| Path | What it is |
|---|---|
| `we/` | Drop-in WE submod files (the deliverable) |
| `src/pz_craft_loops/` | Our builders and helpers (Python). Paths are absolute to the author's machine |
| `src/communitytilepack/deliverables/` | Community source definitions |
| `src/communitytilepack/vendor_we/` | WE's isolated Dylan assets, copied verbatim (WE's work) |
| `src/tikitown/` | TikiTown source definitions + notes |
| `notes/` | Bug pass, workflow notes, upstream version |

The tilepacks themselves (Community Tilepack, Drazion's Tilepack) are not in this repo; the
buildables use them from the installed Workshop items.
