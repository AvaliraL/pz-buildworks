# TikiTown — Easter Eggs & Secrets Catalogue

Mod: TikiTown (Workshop 3037854728). Compiled from the mod's Lua/scripts/map
data. Coordinates are TikiTown map cells (x, y, z).

---

## 1. Baseball Card quest → Signed Titanium Baseball Bat
The headline egg. Collect all **35 Baseball Cards**, craft them into a box, sort,
then "Trace" the picture. The trace craft (`TraceCardsOnBox`) drops a **Duffel
Bag containing the "Signed Titanium Baseball Bat"** at a fixed spot.

- Reward location: **(7782, 7399, z0)** (`TikitownTraceCards.x/y/z`).
- One-time, per-player (ModData flags `TikitownTraceCardsDone` /
  `TikitownTraceCardsBatSpawned`); if you're not at the spot when you finish, a
  LoadGridsquare listener spawns it when you arrive (survives relog).
- The trace craft also gives **`Tikitown_quest1_map3`** (a treasure map — see #2).
- The bat can be repaired (`RepairTitaniumBat`) and mounted as a trophy
  (`MakeWoodenBatDisplayMount` + `MakeGlassBatDisplayCover` + `MountSpecialBat`).
- Full detail in `EASTER_EGG_baseball_cards.md`.

## 2. Quest treasure maps (1–4)
Four lootable map items `Tikitown_quest1_map1..4` (defined in
`Tikitown_CollectorCards.txt`), each overlaying a treasure PNG on the world map
UI centered at world **(10524, 9222)** (`TikitownLootableMap.lua` /
`TT_ISMapDefinitions.lua`). map3 is the one handed out by the card-trace craft;
the legacy server file (`TreasureLocations` / `AddWorldInventoryItem` at lines
~524–569) grants maps 1–4 and spawns the bat — this is the older B41 path that
the B42 folder's `TikitownTraceCards` supersedes.

## 3. Hidden "Jenntacles Plush" spawn
A secret plushie hardcoded to appear at two exact tiles
(`TikitownItemSpawner.lua`):
- **(6760, 7356, z0)** and **(6760, 7358, z0)**
- Spawns `Tikitown.Jenntacles_Plush` once per tile (tracked in `JennPlushieData`
  ModData so it won't respawn). Server-side, fires on LoadGridsquare.
- These two tiles are a deliberate hidden drop — go to that spot to grab it.

## 4. The Secret Lab (underground, multi-level)
The map tags a **`SecretLab`** zombie zone spanning **five basement levels**
(`objects.lua`):
- **(6856, 7556, z-1)** 26×33, and (6863/6861, 7559) at **z-2, z-3, z-4, z-5**
  (~19–21 × 20 each).
- A 5-floor-deep underground complex under TikiTown — the "Proxima" research
  facility (ties to the medicine/cure storyline: ImmunoStasis, the medical
  dummy, VHS_Proxima). Marked as a heavy zombie-density area.
- This is where the Proxima medical content lives thematically.

## 5. Plush Can "gachapon" (PlushCanSurprise)
A random-plushie loot can (`PocketPaws_PlushCan.lua`):
- Right-click a **`Tikitown.PlushCanSurprise`** → "Open Plush Can" → 80-tick
  action → yields **one random plushie** from a pool of 11 (Whale, Penguin,
  Rhino, Sheep, Cat, Dolphin, Pig, Raccoon, Possum, Beaver, Elephant) + an empty
  tin can. Consumes the can.

## 6. Proxima VHS tape
`Tikitown.VHS_Proxima` — a recorded-media tape (RecordedMedia/`proxima_media.lua`)
that spawns alongside the Medical Dummy in the `TikiMedicalDumy` loot list
(weight 50). Watching it presumably delivers Proxima lore.

## 7. GoKart (drivable novelty vehicle)
`vehicles/GoKart.txt` — a full custom vehicle with lock/unlock animations,
tuning, and a spawn list (`GoKartSpawnList.lua`). A fun-vehicle egg rather than a
hidden one.

## 8. Hidden recipes
Many TikiTown recipes are flagged `IsHidden : true` (the box-open recipes, trace
craft, etc. in `Tikitown_Recipes.txt`) — they don't show in the normal craft
menu and are triggered contextually (e.g. opening a sealed box). Not "eggs" per
se, but hidden content worth noting.

---

## Coordinate summary (go-here list)
| Egg | Coordinates | Notes |
|-----|-------------|-------|
| Signed Titanium Bat (card quest reward) | **7782, 7399, 0** | duffel spawns after 35-card trace |
| Jenntacles Plush (hidden) | **6760, 7356, 0** and **6760, 7358, 0** | one-time each |
| Secret Lab (Proxima) | **~6856–6863, 7556–7559, z-1 to z-5** | 5-level underground complex |
| Quest map PNGs center | world 10524, 9222 | UI overlay anchor for maps 1–4 |

## Caveats
- Coordinates are read from the mod's Lua/map object data and are TikiTown map
  cells; they're correct relative to the TikiTown map's placement in the world.
- The card-quest reward and Jenntacles spawns are confirmed from server Lua. The
  Secret Lab is a map-tagged zone (its exact contents/loot are set by the map
  tiles + distributions, not a single script).
- The legacy `media/lua/server/TikitownReturnsandXP.lua` (non-42 folder) holds an
  older version of the treasure logic; the active B42 code is in
  `42/media/lua/server/TikitownReturnsandXP.lua`.
