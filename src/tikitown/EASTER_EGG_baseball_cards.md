# TikiTown — Baseball Card Easter Egg (Signed Titanium Bat)

Mod: TikiTown (workshop 3037854728), B42 folder
Reward: `Tikitown.Titanium_Baseball_Bat` ("Signed Titanium Baseball Bat")
Fixed world location: **(7782, 7399, z0)**

This documents the full "collect all 35 cards" quest chain, the trigger, the
spawn mechanic, and the follow-on display crafts.

---

## 1. The collectible cards

35 distinct cards: `Tikitown.Baseball_Card_01` … `Baseball_Card_35`.

- `DisplayCategory = Memento`, `Weight = 0.01` each, icon `Tikitown_BaseballCard`.
- Each has a unique named player (e.g. `01 Diego Richmond`, `02 Aziel Noble`,
  `10 Russell Baker`). Cards 06 and 08 share the same static model (cosmetic
  quirk, not a functional issue).
- Defined in `42/media/scripts/Tikitown_CollectorCards.txt`.

You find these as loot around the map (they're in the memento distribution set).

---

## 2. Craft chain (how you claim the reward)

Category for all steps: `TTCollections`. Four sequential crafts:

**Step 1 — `Create_Baseball_Card_Box`**
- In: any box (`Base.Shoebox` / `Mov_CardboardBox` / any `ProduceBox_*`) + a
  sharp knife/scissors (kept) + a writing tool (kept).
- Out: `Tikitown.Empty_Baseball_Card_Box`.

**Step 2 — `Add_Cards_to_Box`**
- In: `Empty_Baseball_Card_Box` (destroyed) + all **35** cards `Baseball_Card_01`
  … `Baseball_Card_35`, each destroyed. This is the gate — you must have the
  complete set.
- Out: `Tikitown.Unsorted_Full_Baseball_Card_Box`.
- Uses timed action `Tikitown.AddCardsToBox`, Time 45.

**Step 3 — `Sort_Cards`**
- In: `Unsorted_Full_Baseball_Card_Box` (destroyed).
- Out: `Tikitown.Sorted_Full_Baseball_Card_Box`.
- Timed action `Tikitown.AddCardsToBox`, Time 120.

**Step 4 — `Trace_Cards_Picture`  ← THIS IS THE TRIGGER**
- In: `Sorted_Full_Baseball_Card_Box` (destroyed) + `Base.SheetPaper2` + writing
  tool (kept).
- Out: `Tikitown.Used_Sorted_Full_Baseball_Card_Box` + `Tikitown.Tikitown_quest1_map3`
  (a treasure/quest map item).
- **`OnCreate = CraftRecipeCode.GenerateTreasure.TraceCardsOnBox`** — this hook
  is what fires the bat spawn.

So the reward is not handed to you directly. Finishing the trace gives you a
**map** (`quest1_map3`) and quietly places the bat at a fixed spot in the world
for you to go collect.

---

## 3. The spawn mechanic (`TraceCardsOnBox`)

File: `42/media/lua/server/TikitownReturnsandXP.lua` (lines ~123–220).

Fixed target square is hard-coded:
```lua
TikitownTraceCards.x = 7782
TikitownTraceCards.y = 7399
TikitownTraceCards.z = 0
TikitownTraceCards.item = "Tikitown.Titanium_Baseball_Bat"
```

**On craft (`TraceCardsOnBox`):**
1. Reads `player:getModData()`.
2. If `md.TikitownTraceCardsBatSpawned` is already true → returns (one-time only,
   can't be farmed).
3. Sets `md.TikitownTraceCardsDone = true`.
4. Gets the target grid square via `getWorld():getCell():getGridSquare(7782,7399,0)`.
   - **If that square is currently loaded** → spawns immediately and sets
     `md.TikitownTraceCardsBatSpawned = true`.
   - **If NOT loaded** (you're far away, which is the normal case) → registers a
     `LoadGridsquare` event listener instead (`ensureEventRegistered`).

**Deferred spawn (`onLoadGridsquare`):**
- Fires as squares stream in. When the loaded square matches (7782, 7399, 0)
  exactly, it spawns the duffel, sets `TikitownTraceCardsBatSpawned = true`, and
  removes the listener.
- Guarded so it only arms when `TikitownTraceCardsDone` is set and the bat
  hasn't spawned yet.

**Persistence across reload (`OnGameStart`):**
- On game start, if `md.TikitownTraceCardsDone` is true but the bat hasn't spawned
  yet, it re-registers the `LoadGridsquare` listener — so if you log off before
  reaching the spot, the pending spawn survives a restart.

**The physical spawn (`Tikitown_SpawnDuffelWithBat`):**
```lua
local worldBag = square:AddWorldInventoryItem("Base.Bag_DuffelBag", 0.5, 0.5, 0)
-- resolve the bag's container...
bagContainer:AddItem("Tikitown.Titanium_Baseball_Bat")
```
So the reward appears as a **Duffel Bag on the ground at (7782, 7399, 0)** with
the signed bat inside it.

---

## 4. State tracking

Two `ModData` flags on the player drive the whole thing:

| Flag | Meaning |
|------|---------|
| `TikitownTraceCardsDone` | The trace craft was completed; bat is "owed". |
| `TikitownTraceCardsBatSpawned` | Bat has physically spawned; egg is finished. |

Because both live on **player** ModData, the reward is per-player and one-time.

---

## 5. MULTIPLAYER CAVEAT (same class of bug as the sealed boxes)

`TraceCardsOnBox` and its helpers use `getPlayer()` and `player:getModData()`,
and the world spawn (`AddWorldInventoryItem` / `AddItem`) runs from the
client-side craft `OnCreate` / client `LoadGridsquare`. On a dedicated server:

- `getPlayer()` / client `LoadGridsquare` are client-context, so the spawn is
  performed client-side and may not be authoritative — the same failure mode as
  the sealed-box loot (see `DEV_BUG_REPORT_sealed_boxes.md`). The duffel + bat
  could fail to persist on the server or fail to appear for other players.
- The one-time flags are on the local player's ModData, which does sync back, so
  the "already claimed" guard should hold, but the physical bat placement is the
  risky part.

Not independently confirmed in-game for this egg — flagging it as likely,
matching the confirmed sealed-box behavior. Worth the same fix pattern
(server-authoritative spawn) if it reproduces.

---

## 6. What the bat is (the reward itself)

`Tikitown.Titanium_Baseball_Bat` — "Signed Titanium Baseball Bat"
(`Tikitown_CollectorCards.txt` ~line 443):

- Two-handed blunt swinging weapon, `Categories = Blunt`, `SubCategory = Swinging`.
- Damage 1.5–2.5, MaxRange 1.25, `CriticalChance 50`, `critDmgMultiplier 2.5`,
  `KnockdownMod 3`, `MaxHitCount 3`, `DoorDamage 8`.
- Very durable feel: `ConditionMax 15`, `ConditionLowerChanceOneIn 90`.
- `AttachmentType = Shovel`, uses `SpecialTitanBaseballBat` sprite/icon.
- Tooltip: "You found this after collecting all 35 Baseball Cards. Nice!"

---

## 7. Display / trophy crafts (optional follow-on)

You can mount the bat as a trophy:

- `MakeWoodenBatDisplayMount` → `Bat_Mount_Wood` (Carpentry 5; plank, 4 nails,
  small sheet metal, wood glue + hammer/saw/screwdriver).
- `MakeGlassBatDisplayCover` → `Bat_Mount_Glass` (Glassmaking 4; 4 glass panels,
  2 small sheet metal, 4 screws, epoxy + scalpel/screwdriver).
- `MountSpecialBat` → consumes wood mount + glass cover + bat →
  `Special_Bat_Mounted` (`OnCreate = Recipe.OnCreate.MountSpecialBat`).
- `RemoveSpecialBat` → reverses it back into the three parts.
- Client script `Tikitown_BatDisplay.lua` handles the mounted-display world
  interaction (checks `getFullType() == "Tikitown.Titanium_Baseball_Bat"`).

---

## TL;DR

Collect all 35 unique baseball cards → craft an empty card box → stuff all 35 in
→ sort them → trace the picture. That final "Trace" craft gives you a treasure
map (`quest1_map3`) and permanently (one-time, per-player) drops a **Duffel Bag
containing the Signed Titanium Baseball Bat at world coords (7782, 7399, 0)**. If
that square isn't loaded when you finish, the spawn waits (via a LoadGridsquare
listener that survives restarts) until you walk there. Then you can optionally
build a wood mount + glass cover and mount the bat as a trophy.
