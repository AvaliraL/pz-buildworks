# KnoxBuildworks (KBW) JSON Buildable — Property Catalog

Reference for every property assignable to a KBW JSON buildable tile, traced from the B42
KnoxBuildworks engine Lua (not guessed). Use this when authoring/converting tiles.

**Engine source** (read-only):
`...\steamapps\workshop\content\108600\3772269882\mods\KnoxBuildworks\42\media\lua\`
- `shared\KnoxBuildworks\Definitions\Schema.lua` — authoritative schema + defaults
- `server\KnoxBuildworks\BuildingObjects\KBWBuildingObject.lua` — placement/rendering, flags, capacity, deconstruct
- `shared\KnoxBuildworks\Definitions\Properties.lua` — container / nativeObject / fluidContainer / well
- `shared\KnoxBuildworks\Geometry\Matrix.lua` — faces → dx/dy/dz expansion, fallbackFaces
- `shared\KnoxBuildworks\Definitions\StageConfig.lua` — JSON→native mapping, default callbacks

---

## TL;DR — the three questions that started this

- **Storage capacity:** `stage.object.container = { "type": <label-string>, "capacity": <number> }`.
  `capacity` is applied **directly** (`container:setCapacity(capacity)`). `type` is just a
  free-form **label/tag** — it is NOT a preset that looks up a capacity. Omit `capacity` to keep
  the sprite's native default. (Properties.lua ~110-140)
- **Deconstruct / breakdown yield:** there is **no** explicit refund/salvage/breakdown JSON key.
  Yield is **implicit**: `object.dismantable` (default `true`) controls whether dismantle is
  offered; the returned items come from the sprite's native tile props (CanScrap/ScrapSize/Material)
  — EXCEPT a **single-tile `kind:wall`** object auto-records what it consumed
  (`modData["need:<fullType>"]`) and gives a portion back. You cannot author a custom refund list.
  (KBWBuildingObject.lua ~986-1010)
- **Hue / tint / color shift:** **NO.** There is no hue/tint/rgb/color key. The only recolor in the
  engine is the translucent *ghost preview* tint for wall-finish recipes (not the placed object).
  Color variants require **distinct sprite ids** via the `variants` block. (confirmed full-tree)

---

## 1. "Clear space / see-through" — how tiles show what's behind them

**There is no `seeThrough` / `transparency` / `alpha` / `cutaway` JSON key.** Whether the ground
(or object behind) shows through is **entirely a consequence of `placement.kind`** plus the
sprite's own texture alpha:

| `placement.kind` | How it renders | Transparency result |
|---|---|---|
| `floor`  | `square:addFloor(sprite)` creates a native floor AND **removes/clears** the existing floor + grass/overlays/rugs under it (`Floor.OnCreate`). It REPLACES the tile surface. | **Opaque.** Any clear/diamond edges in the sprite become a **black border** — nothing shows underneath. **This was the bathmat bug.** |
| `object` | `IsoThumpable.new(...)` + `AddSpecialObject(part)` **lays a sprite on top** of the existing tile. Does not clear the floor or objects below. | **Preserves the sprite's own alpha** — the floor/tile underneath shows through transparent pixels. **This is the fix for rugs/mats.** |
| `overlay` | sprite-on-top, `canBeAlwaysPlaced=true`, `canPassThrough` defaults true (wall-deco / attached sprites). | Preserves alpha; attaches to a wall host when `needToBeAgainstWall`. |
| `wall` / `wallCovering` | wall-edge `IsoThumpable` (N/W anchored). Native wall-cutaway transparency (WallNTrans etc.) applies when the player is behind it. | Engine-driven wall transparency, not a JSON flag. |
| `stairs` | native stairs build path. | n/a |

**Rule of thumb:** anything that lies flat and has transparent pixels (rugs, mats, floor decals,
decals, puddles) must be **`kind:object`**, never `kind:floor`. Floor is only for solid,
edge-to-edge floor surfaces (tile, carpet-wall-to-wall, concrete) where opacity is correct.

`placement.kind` enum (Schema.lua ~17): `object`, `wall`, `floor`, `stairs`, `overlay`, `wallCovering`.

Placement sub-flags:
- `needToBeAgainstWall` (bool) — must border a wall; for overlay deco attaches to the wall host.
- `maxDistance` (number > 0), `requiresOutside` (bool).
- `needWindowFrame` (bool) — treat as wall-like, auto window-glass onCreate.
- `dontNeedFrame`, `isPole` (bool).
- `providesWindowFrame` / `providesDoorFrame` (bool) — recorded in part modData.
- `windowSupportSprites` (string[]).

---

## 2. Top-level buildable keys  (Schema.lua ~262-355)

Bundle/file root: `schemaVersion` (must == engine SCHEMA_VERSION), `buildables` (array),
optional `patches`, `templates`, `materialGroups`.

Per buildable:

| Key | Type | Req | Default / notes |
|---|---|---|---|
| `id` | string | **yes** | must match `^[%w_.%-]+$` |
| `category` | string | **yes** | also drives durability class |
| `stages` | array | **yes** | ≥1 stage |
| `translationKey` | string | no | default `IGUI_KBW_Buildable_<id>` |
| `tooltipKey` | string | no | default `Tooltip_KBW_Buildable_<id>` |
| `displayName` | string | no | used by menu grouping; falls back to translationKey |
| `subcategory` | string | no | default `"General"`; affects durability |
| `material` | string | no | enum keys: Wood, "Wood and Metal", Natural, Fabric, Glass, Electronics, Other, Brick, Stone, Concrete, Metal (Durability multiplier) |
| `materialTags` | string[] | no | default `[material]` |
| `styleTags` / `tags` / `aliases` | string[] | no | default `[]` |
| `materialRequired` | bool | no | if true needs ≥1 `materialOptions` |
| `materialOptions` | array | no | each option has its own `stages` (like variants) |
| `variants` | array | no | color/material picker — see §8 |
| `group` | `{id,name,level,translationKey}` | no | collapse multiple buildables into one catalog entry |
| `placement` | object | no | see §1 |
| `construction` | object | no | see §6 |
| `tools` | array | no | definition-level tools, merged into every stage |
| `finishes` | object | no | wall finishes / plasterable |
| icons | — | no | `icon`, `iconTexture`, `iconName`, `iconSprite`, `iconItem` |
| sprite helpers | — | no | `directionalSprites`, `spritePattern {prefix,suffix,directions,start,step}`, `spritePrefix`, `spriteSuffix`, `rotations` |

---

## 3. Stage keys  (Schema.lua ~168-215, 357-412)

| Key | Type | Notes |
|---|---|---|
| `id` | string | default = 1-based index |
| `level` | number | default = index |
| `object` | object | collision/role flags + property handlers — see §4 |
| `geometry` | `{faces}` | sprite layout — see §5 |
| `footprints` | per-dir `{sprite?,dx,dy,dz?}[]` | alternative to geometry.faces |
| `sprites` | per-dir map | keys `W/N/E/S` and `W_open/N_open/E_open/S_open` |
| `requirements` | object | inputs/skills/knowledge — see §6 |
| `construction` | object | stage overrides definition — see §6 |
| `callbacks` | object | `onAddToMenu`,`onCreate`,`onIsValid`,`timedActionOnIsValid` — see §9 |
| `lightSource` | `{radius≥1 req, item?, tags?, fuel?, debugItem?, offsets?}` | |
| `roof` | object | see §7 |
| `entityCompat` | `{module?, entity}` | inherit a vanilla entity's defaults |
| `health` / `skillBaseHealth` / `bonusHealth` | number | explicit durability override (else auto-derived) |
| `xp` | perk→number | stage XP (fallback to construction.xp) |
| `hoppable` | bool | |
| `container` / `nativeObject` / `fluidContainer` / `well` | object | property handlers — see §4 |

---

## 4. stage.object flags + property handlers

Collision / behavior flags (KBWBuildingObject:new ~515-560). All optional pass-throughs:

| Flag | Type | Default |
|---|---|---|
| `isThumpable` | bool | true (unless kind=overlay) |
| `isProp` | bool | false (forced true when canPassThrough and kind not overlay/floor) |
| `blockAllSquare` | bool | true when kind=object, else false (then recomputed from sprite, explicit wins) |
| `canPassThrough` | bool | true for overlay / passable openings; else false |
| `canBarricade` | bool | false (auto-derived for doors/windows) |
| `dismantable` | bool | **true** — gates deconstruction (§ deconstruct) |
| `isDoorFrame` | bool | false (also sprite-derived) |
| `isCorner` | bool | false |
| `hoppable` | bool | false unless sprite hoppable |
| `buildLow` | bool | false |
| `drawFloorGrid` | bool | true |
| `thumpDamage` | number | from base (doors forced 5) |
| `canBePadlocked` | bool | sprite-derived |
| `breakSound` | string | — |
| `cornerSprite` / `pillarSprite` | string | wall corner/pillar auto-draw (pillar forced walk-through) |

**Walk-over object (rug/mat/low decor) preset:**
`{ "isThumpable": true, "blockAllSquare": false, "canPassThrough": true, "canBarricade": false }`
with `placement:{kind:"object", needToBeAgainstWall:false}`. (matches KBW_VE `rugs.json`)

### container  (Properties.lua ~110-140)
```json
"container": { "type": "crate", "capacity": 40 }
```
- `capacity` (number) applied directly via `setCapacity`. Omit → native sprite default.
- `type` (string) = label/tag only. NO capacity preset table.
- If the sprite declares a native container type, the part becomes a container even without this key.

### nativeObject  (Properties.lua ~142-150, NativeObjectTypes.lua)
```json
"nativeObject": { "type": "television" }
```
Functional object. `type` enum: `barbecue, clothingDryer, clothingWasher, combinationWasherDryer,
curtain, fireplace, generator, lightSwitch, mannequin, radio, stove, television`.
- `item` (item fulltype) required ONLY for `generator`.
- `script` valid ONLY for `mannequin`.
- Engine can also auto-detect from sprite props if type omitted.
- Routed through NativeObjectFactory → real Iso class (e.g. IsoTelevision = functional TV).

### fluidContainer  (Properties.lua ~152-200)
`{ capacity≥1, initialPercent 0-100, rainFactor≥0, containerName, emptySprite, filledSprite, fireSprite, filledPercent }`
(emptySprite+filledSprite paired; fireSprite needs both). Applied to tileIndex 1 only.

### well  (Properties.lua ~202-240)
`true` OR `{ capacity≥1, initialPercent 0-100, refillPerHour≥0, rainFactor≥0 }`.
Backed by Base.Well. In finite-water sandbox, defaults: capacity 1500, initial 25%, refill 3/hr.

---

## 5. geometry.faces  (Matrix.lua)

`geometry.faces` = map keyed `W`/`N`/`E`/`S` (or 1=W,2=N,3=E,4=S). Each face:
```
{ "layers": [ { "z"?, "x"?, "y"?, "rows": [ [token, token, ...], ... ] } ] }
```
Expansion (Matrix.expandFace ~57-78):
- **column index → dx** (+ `layer.x`)
- **row index → dy** (+ `layer.y`)
- **layer → dz** (`layer.z` or layerIndex-1)

Token types: `false`=skip (gap); `true`=empty blocking cell; `"sprite"`=sprite cell;
`{dx,dy,dz,sprite,empty,blocks,kind,properties}`=explicit cell.

**fallbackFaces** (Matrix ~9-14) when a face is missing: `W→W,E,S,N`; `E→E,W,S,N`;
`N→N,S,W,E`; `S→S,N,W,E`. i.e. **E falls back to W, S falls back to N** (mirroring).

**Two-tile layout convention** (verified vs TikiTown bed): W/E = two **columns** `[[a, b]]`;
N/S = two **rows** `[[a],[b]]`. For the swapped-position bug we hit repeatedly, order the
second-half sprite correctly per the owner's described half (west/east, north/south).

`cornerSprite`/`pillarSprite` (under stage.object) → auto corner/pillar pieces via connectWallParts.
Render applies: `setNorthSprite(N or S)`, `setEastSprite(E or W)`, `setSouthSprite(S or N)`,
base = W or S or N or E.

---

## 6. requirements + construction

### requirements  (Schema ~57-101, Requirements.lua ~360-430)
- `inputs[]`: `{ id, role(material|tool), mode(consume|keep|drain), resourceType(Item),
  items[], tags[], amount, uses, flags[], label/labelKey/icon, matchTag, amountMax, materialTags }`.
  Need ≥1 item or tag when resourceType=Item.
  Flags: NoBrokenItems, AllowDestroyedItem, IsEmptyContainer, IsFull/NotFull, IsEmpty/NotEmpty,
  HasOneUse/HasNoUses, AllowFavorite, Prop1/Prop2, MayDegrade[Heavy|Light|VeryLight].
- `materials`: array OR string naming a bundle `materialGroup`.
- `tools[]`: role=tool, mode=keep default.
- `skills`: `{ perk: level }` (perks must exist).
- `recipes[]`: known-recipe gate.
- `knowledge`: `{ recipes[], sources[] (display), hideUntilLearned(bool), needToBeLearned(bool),
  skillAlternatives[] { mode:"any"|"all", skills:{perk:level} } }`.
- `debugOnly` (bool).

Consumption: `keep`=record/degrade tool; `drain`/`uses`=UseAndSync per use; `consume`=remove item.

### construction  (Schema ~168-199)
`{ time(≥0, default max 200), timedAction(real action script), completionSound, sound,
actionAnim, animVariable{key,value}, xp{perk:n}, category, tags(e.g. "CanBeDoneInDark"),
canWalk(bool) }`. Stage-level overrides definition-level.

---

## 7. Roof / window / door specifics

**Roof** (Schema ~361-399): `stage.roof = { family(req), role(flat|slope|detail|gable|accent),
pitch(shallow|custom|0|30|45), step(int, slope), stepsPerLevel(int, slope), faceByEdge(edge→face,
req for slope), hiddenEdges[], partsByFace(face→sprite) }`. (We currently defer roofs per user.)

**Window**: `placement.needWindowFrame` (wall-like + auto window-glass onCreate);
`placement.windowSupportSprites[]`. Glass panes auto-create native IsoWindow.

**Door**: behavior is sprite-driven (sprite type doorN/doorW → isDoor, thumpDmg=5).
Open-state sprites via `sprites` keys `W_open/N_open/E_open/S_open`. `object.isDoorFrame` marks
frames. Callback `KnoxBuildworks.JsonCallbacks.DoorFrame.OnIsValid` rejects frames next to stairs.
(Our door schema: faces W=E=sprite / N=S=northSprite closed + `sprites` open block + DoorFrame
OnIsValid + Hammer/Plank/Nails/Hinge/Doorknob cost.)

---

## 8. variants  (Schema ~340-355) — the ONLY color mechanism

`variants: [ { id, labelKey, iconSprite, stages } ]`. Each variant's `stages` is a full stage list,
merged over the parent definition. Produces ONE menu entry with a style/color picker. Because there
is no hue/tint key, **this is how you do "3 colors / N styles": one variant per distinct sprite set.**
`materialOptions` has the identical shape (material picker). Resolved at build via
`Resolver.resolveStage(buildableId, variantId, materialId, stageId)`.

Example (exercise ball, 3 colors): three variants, each a stage with its own `iconSprite` + geometry
pointing at that color's sprite id.

---

## 9. Callbacks  (Schema ~192-205, Callbacks/JsonBuildable.lua, Util/LuaCallback.lua)

`stage.callbacks`: `onAddToMenu`, `onCreate`, `onIsValid`, `timedActionOnIsValid` — each a dotted Lua
path (≥2 identifier tokens). `KnoxBuildworks.JsonCallbacks.*` and `BuildRecipeCode.*` auto-resolve.

Built-in `KnoxBuildworks.JsonCallbacks.*`:
- `Floor.OnIsValid` / `Floor.OnCreate` — auto-wired for `kind:floor` (the clear/replace logic).
- `DoorFrame.OnIsValid` — no door frame beside stairs.
- `Surface.EnablePlaster` — setCanBePlastered.
- `Visibility.BrickWallLvl2` — Masonry≥5 cutaway gate.

`onCreate` receives `{thumpable, square, character, facing, north, definition, stage, buildObject,
tile, x, y, z}` and may return `{ replaceObject = ... }` to swap the built object.

---

## 10. Durability (auto, unless overridden)

Health auto-derives from placement kind + category + material + required skill (Durability.lua).
Override with stage `health` / `skillBaseHealth` / `bonusHealth` (explicit wins).

---

## Gotchas (keep these in mind when converting)

1. **Transparency = `kind` only.** Rugs/mats/decals → `kind:object`. Floor is opaque and will
   black-border any clear pixels. (This was the bathmat fix.)
2. **container `type` is a label, not a capacity preset.** Set `capacity` explicitly.
3. **No color/hue/tint key.** Use `variants` with distinct sprite ids.
4. **Deconstruct yield is implicit** — `dismantable` + native tile props; single-tile walls auto-record
   consumed inputs. No custom refund list in JSON.
5. **fallbackFaces: E←W, S←N.** Only author W and N if E/S mirror; otherwise set all four.
