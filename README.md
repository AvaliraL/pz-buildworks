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

## Not included

The tilepacks' own art and packs (other authors' work), rulebook PDFs, build output and caches.
Those come from the installed Workshop items. The only packs here are the ones the WE submods
already ship (our generated mirror/screen sheets and WE's isolated Dylan sheet).

Private repository: contains World Essentials files and files derived from the tilepacks.
Review licensing before making anything public.
