# Hand-off: crafting recipes for Knox Buildworks components + lootable Spray Paint

For the World Essentials dev. Item scripts and one server Lua patch, ready to drop in.
Written 2026-11-08.

## Problem
Knox Buildworks (KBW) buildables consume custom component items that either cannot be
crafted at all or only spawn at a very low rate. Players stall on them, especially in the
refrigeration / appliance cost ladders and the asphalt road tiles. Separately, KBW's 12
graffiti buildables each drain 1 use of vanilla **Spray Paint**, which has **no loot
entries in vanilla**, so the graffiti tiles are effectively unbuildable.

## Fix
1. Six craft recipes that turn **vanilla-only inputs** into KBW components.
2. Spray Paint gets the same loot spawns as one vanilla house-paint colour (`PaintCyan`),
   and its weight drops from 1.0 to 0.5.

Loot spawns for the KBW components themselves are unchanged (they still spawn at KBW's own
rates); these recipes are an extra source, not a replacement.

## Files and where they go

| File | Destination | Why there |
|---|---|---|
| `WorldEssentials_KnoxComponentRecipes.txt` | `World Essentials - Knox Buildworks Expansion/42/media/scripts/` (new folder) | Names `KnoxBuildworks.*` items. The Expansion's `mod.info` has `require=KnoxBuildworks,KnoxBuildworksVanillaExpanded,TableSaw`, so these items always exist when the file loads. A script file cannot guard itself, so it must not go in main WE. |
| `WorldEssentials_KnoxComponentRecipes_Recipes_EN.json` (6 keys) | Merge into `World Essentials/42/media/lua/shared/Translate/EN/Recipes.json` | Keys are global, so main WE is fine. Keys are the **bare recipe name** (`"WEMakePlasticSheet": ...`), like vanilla (`"Forge_Cup": "Forge Cup"`) and KBW (`"KBWCutPlasticSheet"`). Our first draft used a `Recipe_` prefix, copied from WE's repair recipes (`Recipe_WERepair...`). The game adds that prefix itself, so a prefixed key most likely never matches. Worth checking whether WE's repair recipe names show up in game (not verified). |
| `WorldEssentials_SprayPaint_Items.txt` | `World Essentials/42/media/scripts/` | Vanilla item override; same full-block style as `WorldEssentials_ConcreteBucketUses_Items.txt`. |
| `WorldEssentialsSprayPaintDistribution_Server.lua` | `World Essentials/42/media/lua/server/Patches/` | Same style as `WorldEssentialsAsphaltDistribution_Server.lua`. |

B42 auto-loads every `.txt` in `media/scripts` and runs server Lua in that path; no
registration needed. All recipe ids carry a `WE` prefix so they never clash with KBW's own.

## The recipes

All inputs are vanilla. Item ids, use counts and syntax were read from the installed B42
scripts.

| Recipe id | Inputs | Output | Gate / station |
|---|---|---|---|
| `WEMakeBucketOfAsphaltMixture` | 1 `Base.Bucket` or `Base.BucketEmpty` (destroyed), 2 uses `Base.Gravelbag`, 2 uses `Base.Sandbag`, 1.0 `Petrol` fluid | 1 `KnoxBuildworks.BucketAsphaltMixtureFull` (10 uses) | Hand craft, Masonry, 150 |
| `WEForgeThinCopperPipe` | 1 `Base.SmallCopperSheet`, 1 charcoal; smithing hammer + tongs/pliers kept | 2 `KnoxBuildworks.ThinCopperPipe` | Blacksmith 5, Forge, +25 Blacksmith xp |
| `WECutRubberSeal` | 1 `Base.TirePiece`; sharp knife kept | 2 `KnoxBuildworks.RubberSeal` | Hand craft, no skill |
| `WEMakePlasticSheet` | 1 `Base.Tarp`, 2 uses `Base.Epoxy`, 1 use of any lighter (`base:lighter`); scissors kept | 1 `KnoxBuildworks.PlasticSheet` | Hand craft, no skill |
| `WEMakeInsulationFoam` | 1 `Base.Sponge`, 2 uses `Base.Glue` or `Base.Epoxy` | 1 `KnoxBuildworks.InsulationFoam` | Hand craft, no skill |
| `WEChargeRefrigerantBottle` | 1 `Base.Kettle_Copper` (destroyed), 1250 uses `Base.PropaneTank` | 1 `KnoxBuildworks.RefrigerantBottle` (10 uses) | Metalworking 3, +10 Metalworking xp |

Design notes:
- **Asphalt**: vanilla sand and gravel bags are 4 uses (`UseDelta 0.25`), so 2 uses is half
  a bag of each. Vanilla has no tar or bitumen, so petrol is the binder. One bucket = 10 road
  tiles. No carved-bucket variant: KBW has no carved asphalt bucket.
  The petrol is its own input line, `item 1 [*]` then `-fluid 1.0 [Petrol]` (as in vanilla
  `recipes_lightsources.txt`). A `-fluid` line draws from the item line directly above it, which
  must be amount 1. Placed directly under `item 2 [Base.Sandbag]`, it made the recipe invalid and
  stopped every world from loading (fixed 2026-11-08, before shipping).
- **Copper pipe**: 1 copper sheet saws into 4 small sheets (vanilla), so 1 sheet = 8 pipes.
  No `NeedToBeLearn`; available as soon as Blacksmith 5 is reached.
- **Rubber seal**: 1 tire = 4 pieces (vanilla `CutUpTire`) = 8 seals.
- **Plastic sheet**: KBW's `KBWCutPlasticSheet` then cuts 1 sheet into 6 small sheets.
  Garbage bags are deliberately not an input (too easy to get).
- **Refrigerant**: propane is a real refrigerant (R-290). `PropaneTank` is a drainable with
  `UseDelta 0.0002` (5000 uses), so 1250 uses = 25% of a tank, 4 bottles per tank. The tank
  is kept when empty (vanilla `KeepOnDeplete`). The copper kettle is forged from a copper
  sheet at the advanced forge, so the bottle carries a real metalworking cost.
- Skill ids in script are the internal ones: `Blacksmith`, and `MetalWelding` (shown in game
  as Metalworking).

## Spray Paint loot map it mirrors (verified, Build 42)
The patch adds a `SprayPaint` entry next to every `PaintCyan` entry at the same weight. One
colour, not all 15, so a spray can is as common as a single paint colour.

| ProceduralDistributions list | Weight |
|---|---|
| `CratePaint` | 20 |
| `ToolStorePaint` | 20 |
| `PaintStudioTools` | 2 |
| `ArtSupplies` | 1 |
| `CrateWallFinish` | 1 |
| `CrateRandomJunk` | 0.4 |

`PaintCyan` has no entries in `Distributions.lua`. The patch is generic: any list another
mod adds with `PaintCyan` gets spray paint too.

Safety / behaviour (same as the asphalt patch): additive only, idempotent (skips a list that
already has `SprayPaint`), recurses into nested `.junk` lists, runs on
`OnPostDistributionMerge`, MP-safe. It does **not** guard on KBW, since Spray Paint is a
vanilla item. Kahlua-safe: no `next()`, `goto`, `//`, or bitwise ops.

---

## Verification / testing

### What has been checked so far
- **Spray Paint patch: tested against mocks, not in game.** Run under lupa with `next = nil`,
  against the real vanilla `ProceduralDistributions.lua`. Result: 6 lists each gained exactly
  one `SprayPaint` entry at the `PaintCyan` weight; a second run added nothing.
- **Recipe file: structure only.** Braces balance, 6 recipe ids present. Every item id, tag
  and use count was read from the installed scripts. **No recipe has been loaded in game.**
- **Spray Paint item override: not tested.** Full vanilla block, only `Weight` changed.
  Re-compared field by field with vanilla `drainable.txt` (2026-11-08): identical apart from Weight.
- **Recipe file: checked by script against the installed game + KBW (2026-11-08)**
  (`pz_craft_loops/recipe_check.py`). Every input/output item, tag, timed action and skill
  exists; drainable amounts fit their use counts; every `-fluid` line follows an amount-1 item.
  This pass found and fixed two bugs: the asphalt `-fluid` placement (no world could load), and
  the `Recipe_` translation prefix (the names would have shown as raw ids). Still not loaded in game.

### In-game test plan
Fresh save / server start with KBW, KBW Vanilla Expanded, TableSaw and the Expansion active.
Loot tables and scripts build at load, so restart after adding the files.

1. **Scripts load.** No script errors for `WorldEssentials_KnoxComponentRecipes.txt` in
   `console.txt`. All 6 recipes show in the crafting menu with their English names (e.g. "Make Plastic Sheet"), not raw ids.
2. **Asphalt.** With a bucket, a gravel bag, a sand bag and petrol (a can in inventory),
   craft once. Expect a full asphalt bucket, both bags at 2/4 uses left, petrol reduced by
   1.0. Then build one KBW asphalt road tile and confirm the bucket drops to 9 uses.
3. **Copper pipe.** At a forge with Blacksmith 5: 1 small copper sheet + 1 charcoal gives 2 pipes,
   hammer and tongs kept. Confirm the recipe is hidden or greyed out at Blacksmith 4.
4. **Rubber seal.** 1 tire piece + sharp knife gives 2 seals; knife kept. A dull knife should
   not qualify (`IsNotDull`).
5. **Plastic sheet.** Tarp + epoxy + any lighter + scissors gives 1 sheet. Try a disposable, Zippo,
   BBQ and battery lighter. Confirm the lighter loses one use and is not consumed.
6. **Insulation foam.** Sponge + glue works; sponge + epoxy works; 2 uses taken.
7. **Refrigerant bottle.** With Metalworking 3, a copper kettle and a full propane tank:
   craft once, expect 1 bottle and the tank at 75%. Craft 4 times total: the tank should be
   empty but **kept**. Check two open points:
   - Does `item 1250` drain 1250 tank uses as intended? (Vanilla drains drainables this way,
     e.g. 2 blowtorch uses in `CutCircularSawblade`, but not at this scale.)
   - Does a tank on the floor next to the player count, or must it be in inventory? (It weighs 10.)
8. **Spray Paint loot.** Console should print
   `[WorldEssentials][SprayPaintDistribution] mirrored PaintCyan -> SprayPaint on N loot entries.`
   Expect **N = 6** with base game only; higher is fine if other mods carry `PaintCyan`.
   In the debug Lua console:
   ```lua
   local it = ProceduralDistributions.list.CratePaint.items
   for i=1,#it-1,2 do if it[i]=="SprayPaint" or it[i]=="PaintCyan" then print(it[i], it[i+1]) end end
   ```
   Expect `PaintCyan 20` and `SprayPaint 20`.
9. **Spray Paint weight.** `additem "yourname" Base.SprayPaint`; the item tooltip should show 0.5,
   with 8 uses. Build one KBW graffiti tile; the can drops to 7 uses.

### Test result (2026-11-08, single player, local test mod `WEKnoxComponentRecipesTest`)
**Tested in game and working.** All 6 recipes craft as described, and Spray Paint spawns as loot.
The console printed `[WorldEssentials][SprayPaintDistribution] mirrored PaintCyan -> SprayPaint on
8 loot entries`: 6 vanilla lists, plus 2 more from other loaded mods carrying `PaintCyan`, as
expected. No script errors at world load.

### Expected result
All six KBW components are craftable from vanilla materials. Graffiti tiles become buildable
from looted spray paint. Existing KBW loot for the components is untouched.

Attached files: `WorldEssentials_KnoxComponentRecipes.txt`,
`WorldEssentials_KnoxComponentRecipes_Recipes_EN.json`, `WorldEssentials_SprayPaint_Items.txt`,
`WorldEssentialsSprayPaintDistribution_Server.lua`
