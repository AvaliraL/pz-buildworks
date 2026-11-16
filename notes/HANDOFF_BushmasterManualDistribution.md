# Hand-off: Bushmaster Auto Manual loot spawns

Server Lua distribution patch, same style as the asphalt and spray paint patches.
File: `WorldEssentialsBushmasterManualDistribution_Server.lua`

## Problem
The '97 ADI Bushmaster's skill book, `Base.97BushmasterMagazine` ("Bushmaster Auto Manual"), teaches all
17 Bushmaster part recipes (hood, doors, front windshield, ...). The Bushmaster mod only places it in one
loot table: the glovebox of a Bushmaster (`BUSHGloveBox`, weight 80). Nobody can learn the recipes
without finding a Bushmaster first. (Checked across every Workshop mod: no other source.)

## Fix
On `OnPostDistributionMerge` the patch adds the manual to five `ProceduralDistributions` lists, with fixed
weights:

| List | Weight |
|---|--:|
| BookstoreMisc | 0.3 |
| CrateMagazines | 0.3 |
| MagazineRackMixed | 0.3 |
| MechanicShelfBooks | 0.5 |
| PostOfficeMagazines | 0.2 |

These are the same lists and weights the M998 mod uses for its own magazine
(`Base.92amgeneralM998Magazine`, 42.13 / 42.20). They are copied in as fixed values, so **the patch does
not depend on the M998 mod**. It only needs the Bushmaster mod.

## Where it goes
```
World Essentials/42/media/lua/server/Patches/WorldEssentialsBushmasterManualDistribution_Server.lua
```
Same folder as the existing `WorldEssentials*Distribution_Server.lua` patches. No registration needed.

## Deliberately NOT done
- **No vehicle tables.** The Bushmaster's own glovebox entry is left exactly as the mod ships it.
- **No walking of other tables.** Unlike the asphalt and spray paint patches, this one names its lists
  directly. It will not pick up extra lists if another mod later adds the M998 magazine somewhere new.

## Safety / behavior
- **Additive only**: never removes or rescales entries.
- **Idempotent**: skips any list that already has the manual.
- **Guarded**: does nothing unless mod id `97bushmaster` is active.
- **Missing list**: if one of the five lists doesn't exist, it logs that and still does the others.
- Existing worlds: loot tables are built at load, but containers that were already generated and looted keep
  their contents. New and respawned containers use the new tables.

## Testing status
- **Tested against mocks only** (lupa / Lua 5.4 with `next` removed, plus a static check for Kahlua-unsafe
  constructs and for any M998 reference in the code). **Not tested in game.**
- Mock cases: with only the Bushmaster mod active, all five lists get the entry at the right weight and
  other lists and vehicle tables are untouched; a second run adds nothing; Bushmaster inactive adds nothing;
  one missing list adds the other four; missing `getActivatedMods` or `ProceduralDistributions` is a safe no-op.

## Verify in game
1. Start the server on a fresh load with the Bushmaster mod active. The log should print:
   ```
   [WorldEssentials][BushmasterManualDistribution] added the Bushmaster Auto Manual to 5 loot lists (0 not found).
   ```
2. In debug mode, check one list:
   ```lua
   local it = ProceduralDistributions.list.MechanicShelfBooks.items
   for i = 1, #it - 1, 2 do print(it[i], it[i + 1]) end
   ```
   You should see `Base.97BushmasterMagazine 0.5`.
3. Spot check: mechanic-shop shelves (`MechanicShelfBooks`, the highest weight at 0.5) and bookstore shelves.
   These rates are low, so use the debug console rather than waiting on random loot.
