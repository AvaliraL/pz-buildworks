# World Essentials (2026-11-08 update): crashes / errors when optional mods are not enabled

Two problems, both arrived with the update. Summary:
1. Startup crash before the main menu if `ZVirusVaccine42BETA` is not enabled (lab recipes).
2. "Item not found" errors if `Post Apocalyptic Weapons` / MedievalZ are not enabled (repair recipes).

Mod: World Essentials (Workshop 3733324672, mod id `WorldEssentials`)
File: `42/media/scripts/generated/entities/lab/craftRecipes/recipes_LabChemistrySet.txt`
(file date in the Steam copy: 2026-11-08 17:07, arrived with the latest WE update)
Severity: hard crash before the main menu. The player cannot reach the mod screen to fix it.

## Symptom

With World Essentials enabled and Zombie Virus Vaccine (`ZVirusVaccine42BETA`, Workshop
3615135168) NOT enabled, Project Zomboid closes during startup, before the main menu.
`Zomboid\console.txt`:

```
ERROR: General f:0> ScriptManager.loadScripts> Exception thrown
    java.lang.Exception: TimedActionScript 'MixingB' could not be found in recipe ChmSynthesizeCure
    at CraftRecipe.OnScriptsLoaded(CraftRecipe.java:804).
    ...
ERROR: General f:0 at GameWindow.uncaughtException > Unhandled java.lang.RuntimeException thrown by thread MainThread.
    java.lang.RuntimeException: java.io.IOException: Script load errors.
```

Mods enabled in the main-menu list load at startup, so the bad script stops the game before
the menu appears.

## Cause

WE ships its own (edited) copy of ZVirusVaccine's chemistry-set recipes. Its hash differs from
ZVirusVaccine's 42.20 file at the same path. All 13 recipes in it depend on ZVirusVaccine
content that neither vanilla nor WE defines:

| Timed action used | Recipes | Defined in vanilla | Defined in ZVirusVaccine | Defined in WE |
|---|---|---|---|---|
| `MixingB` | ChmSynthesizePlainVaccine, ChmSynthesizeQualityVaccine, ChmSynthesizeAdvancedVaccine, ChmDuplicateAdvancedVaccine, ChmSynthesizeCure, ChmDuplicateCure | no | yes (`LabActions.txt`) | no |
| `MixingChm` | ChmMixFlaskOfSodiumHypochlorite, ChmMixFlaskOfAmmoniumSulfate, ChmMixFlaskOfHydrogenPeroxide | no | yes | no |
| `MakingPills` | ChmMakeAlbumin, ChmMakeChlorineTablets | no | yes | no |
| `MakingChm2` | ChmMakeBottleOfBleach | no | yes | no |
| `MakingChm3` | ChmMakeBottleOfDisinfectant | no | yes | no |

The recipes also use `LabItems.*` items and the `ZVirusVaccine42BETA:ChemistrySet` tag, which
also come from ZVirusVaccine.

`mod.info` lists `ZVirusVaccine42BETA` only under `loadModAfter=`, not under `require=`.
`loadModAfter` only orders the mods when both are enabled. It does not make the game load
ZVirusVaccine, so the mod list accepts WE on its own and the scripts then fail to load.

When ZVirusVaccine IS enabled, WE's file overrides ZVirusVaccine's (same relative path) and
everything loads. That is probably why this was not seen on the server, which runs both.

## Reproduce

1. Enable World Essentials (with its required mods) in the main-menu mod list, with
   Zombie Virus Vaccine disabled.
2. Restart the game. It crashes before the main menu with the log above.

Confirmed on our side: adding `mod = ZVirusVaccine42BETA,` to `Zomboid\mods\default.txt` is the
workaround. That's the only way out, because the in-game mod screen is unreachable.

## Suggested fixes (either one)

1. **Make the dependency explicit:** add `ZVirusVaccine42BETA` to `require=` in
   `World Essentials/42/mod.info`. The mod list then enables or blocks it properly, and nobody
   can get into the crash state.
2. **Keep WE usable without it:** move the ZVirusVaccine overrides
   (`media/scripts/generated/entities/lab/...` and anything else that needs ZVirusVaccine) into
   a small bundled submod, e.g. "World Essentials - ZVirus Vaccine Patch", with
   `require=WorldEssentials,ZVirusVaccine42BETA`. B42 has no conditional script loading, so a
   separate mod is the way to make these scripts load only when ZVirusVaccine is present.

**Second instance, seen once the ZVirusVaccine workaround got us to the menu (new single-player
world, 2026-11-08 17:15):** `WorldEssentials_PostApocalypticWeapons_Repair.txt` (recipes
"Reinforce Light Post Apocalyptic Weapon" / "Reinforce Post Apocalyptic Weapon") references
`Base.Post_Apocalyptic_Axe` and the other items from `[B42] Post Apocalyptic Weapons` (Workshop
3472334215, mod id `Post Apocalyptic Weapons`), which is also only under `loadModAfter=`:

```
ERROR: General f:0 at InputScript.OnPostWorldDictionaryInit> Reinforce Post Apocalyptic Weapon item not found: Base.Post_Apocalyptic_Axe.
```

(In our runs the world load also failed, but a broken recipe of our own, still in local testing,
was present too. So we can't yet say whether these missing-item errors block a world on their own.
We'll update this once we've retested without it.)

The same happens with `WorldEssentials_MedievalZ_Repair.txt` (`WERepairLongSword` /
`WERepairMesserSword`: "item not found: MZ.LongSword1..4, MZ.MesserSword" and "Invalid input")
when MedievalZ isn't enabled. These "item not found" lines are logged as errors. Other WE script files
that look tied to optional mods and should get the same check: `WorldEssentials_MedievalZ_Repair.txt`,
`recipes/recipes_AuthenticZCurrent_fixing.txt` (module `AuthenticZRecipes`),
`WorldEssentials_MonsterMovementSounds.txt`, `WorldEssentialsCompanionCertificates.txt`,
`vehicles/OneLifeSignatureFleet_Vehicles.txt`.

The same check is worth running for the other mods in `loadModAfter=` that WE ships script
overrides for. Any WE script that references a timed action, item or tag from a mod listed only
under `loadModAfter` will crash startup the same way when that mod is missing.

## What was verified

- Read the crash in `Zomboid\console.txt` (launch on 2026-11-08 17:08). The load list contains
  `WorldEssentials` and not `ZVirusVaccine42BETA`.
- Searched the scripts of vanilla, ZVirusVaccine 42.20 and WE for `timedAction <name>`
  definitions (the results are in the table above).
- Compared WE's file with ZVirusVaccine's: WE's is a modified copy, not identical.
- Confirmed: with ZVirusVaccine added to the mod list, the game reaches the main menu.
