# KBW buildable schema reference — per object type

Canonical schema for each buildable TYPE, pulled from the live Knox Buildworks defs. Mirror the
matching type when converting ANY new tile (TikiTown or Community). The self-contained templates
live in the **KnoxBuildworks_Vanilla_Expanded** mod (workshop 3772269882,
`.../KnoxBuildworks_Vanilla_Expanded/42/media/KnoxBuildworks/definitions/`). Base-mod `vanilla/*`
files are thin entity-script wrappers — use only for category taxonomy.

## Common top-level shape
```
{ "id":"kbw.vanillaexpanded.<area>.<group>.<name>",
  "allowSpriteReuse": true,                      // when sprite already registered elsewhere
  "translationKey":"IGUI_KBWVE_Buildable_...", "displayName":"...",
  "tooltipKey":"Tooltip_KBW_Shared_<Type>",      // shared per-type key
  "category":"...", "subcategory":"...",
  "material":"Wood|Metal|Glass|Stone|Fabric|Electronics", "materialTags":["Wood"],
  "iconSprite":"<W-facing sprite>",
  "placement":{ "kind":"...", ...flags },
  "construction":{ time, timedAction, completionSound, category, xp{} },
  "stages":[ { "id":"built", "geometry":{faces{W,N,E,S}}, "requirements":{...}, "object":{...}, <type-block> } ] }
```
Requirements are EITHER inline `requirements.inputs:[...]` OR a named group
`requirements.materials:"kbwve.extended.wood"` (groups declared in a file-top `materialGroups` map).

## placement.kind (the type-defining field)
- `wall` — walls, fences, door frames, door-wall sections
- `object` — counters, containers, furniture, windows, door leaves, rugs, lamps
  (flags: requiresFloor, againstWall, needToBeAgainstWall, needWindowFrame, windowSupportSprites[], dontNeedFrame)
- `floor` — floors AND roofs (roofs add needToBeAgainstWall:false)
- `stairs` — stairs
- `wallCovering` — paint/plaster/wallpaper trim (+ wallCoveringType, sign)
- `overlay` — posters/signs/wall decorations (+ needToBeAgainstWall:true)

## type-specific blocks
- `container:{type,capacity?}` — counters(`counter`/`overhead`), dressers(`sidetable`), lockers/shelves
- `roof:{family,pitch,role}` — roofing
- `lightSource:{radius,item,fuel}` — lighting
- doors/windows: NO block — behavior from `object.canBarricade` + placement `needWindowFrame`/`dontNeedFrame`
- plain furniture (bed/chair/couch/table): often NO type block and NO object block

## knowledge (magazine gate) — identical pattern across learnable types
```
"knowledge":{ "recipes":["KBWKnowledge_<X>"], "hideUntilLearned":true, "needToBeLearned":true,
  "sources":[{"type":"magazine","item":"KnoxBuildworks.<X>"}],
  "skillAlternatives":[{"mode":"all","skills":{"<Skill>":<n>}}] }
```
recipe id ↔ magazine id mirror each other. Basic structural pieces (log wall) OMIT knowledge.
Pairs: FineWoodWorking_Furniture_Counters, _Furniture_Dressers, _Furniture_ChairsBenches,
_Furniture_BedsCouchesArmchairs, FineWoodWorking_DoorsWindows, FlooringGuide_Ceramic,
TheFamilyHandyman_StairsFences (stairs/fences/roofing), PopularMechanics_Lighting.

## named material groups (from extended_storage.json + lighting/indoor.json)
- `kbwve.extended.wood` = hammer + 4 Plank + 4 Nails
- `kbwve.extended.wood_large` = hammer + 8 Plank + 8 Nails
- `kbwve.extended.wood_glass` = wood + 2 GlassPanel ; `_glass_large` = wood_large + 4 GlassPanel
- `kbwve.extended.metal` = weldmask+screwdriver + BlowTorch(x4)+WeldingRods(x2) + 3 SheetMetal + 2 MetalPipe + 4 Screws
- `kbwve.extended.metal_light` = weldmask + BlowTorch(x2)+Rods(x1) + 2 SmallSheetMetal + 2 ScrapMetal
- `kbwve.extended.metal_large` = weldmask+screwdriver + BlowTorch(x8)+Rods(x4) + 6 SheetMetal + 4 MetalPipe + 8 Screws
- `kbwve.extended.log_stack` = hammer + 9 Log + 10 Nails
- `kbwve.light.basic` = 10 ElectronicsScrap + 4 ElectricWire + 5 ScrapMetal + 1 LightBulb + 5 Screws
(doors/windows/walls/floors/roofing/fencing inline their inputs instead of using a group)

## timedActions / completionSounds / construction.category (valid values)
timedAction: BuildWallMetal, BuildWallHammer, BuildWallNoTool, BuildWoodenStructureMedium, BuildLowNoTool
completionSound: BuildMetalStructure{Medium,Small}, BuildWoodenStructure{Large,Medium,Small}, DropSoilFromGravelBag
construction.category: Welding, Carpentry, Furniture, Masonry, Electrical, Tailoring  (+ optional canWalk:false)
object flags: isThumpable, dismantable, blockAllSquare, canPassThrough, canBarricade, canBePadlocked, drawFloorGrid
  (NO isCorner — corners are separate buildables)

---

## Per-type templates (mirror these)

### 1. Wall (structural) — `walls/log_cabin.json`
category "Walls" / subcat "<Style> Walls" / material Wood. placement `{kind:"wall"}`.
construction time200 BuildWallNoTool / BuildWoodenStructureLarge / Carpentry. inputs inline (logs+bindings).
object `{isThumpable:true, canBarricade:false}`. Corners = separate buildables, often W-face only, costlier.

### 2. Wall covering / trim / baseboard — `vanilla/wall_finishes.json`
category "Wall Finishes" / subcat "Paint, Plaster & Wallpaper". placement
`{kind:"wallCovering", requiresFloor:false, wallCoveringType:"paintSign", sign:N}`. stage id "finish",
`sprites:{N,E,S,W}` flat map (NOT geometry), entityCompat. (NOTE: the earlier TikiTown trim used the
native `wallAttachment` pattern — `placement.kind:"wallCovering"`+`OnCreateWallAttachment` callback —
which is the KBW-VE-equivalent for custom trim pieces.)

### 3. Door (openable) — `doors.json`
category "Doors" / subcat "Doors"/"Sliding Doors"/"Door Frames". Door leaf placement
`{kind:"object", dontNeedFrame:true}`; door-wall section `{kind:"wall"}` + `previousStage:["WoodenWallFrame","MetalWallFrame"]`.
inputs add `door_hinges`(Base.Hinge x2) + `door_hardware`(Base.Doorknob x1); magazine FineWoodWorking_DoorsWindows.
construction time200 BuildWallHammer / BuildWoodenStructureLarge / Carpentry. object `{isThumpable:true, canBarricade:true}`.
No open/closed sprite arrays — engine-driven.

### 4. Window — `windows.json`
category "Windows" / subcat "Wooden" / Wood. placement `{kind:"object", needWindowFrame:true, windowSupportSprites:[...]}`.
inputs planks+nails+`glass_panels`(Base.GlassPanel); Woodwork 5; magazine FineWoodWorking_DoorsWindows.
construction time50 BuildWoodenStructureMedium / Furniture. object `{canBarricade:true}`.

### 5. Counter (container) — `containers/extended_storage.json` (GOLD TEMPLATE)
category "Containers" / subcat "Counters" (upper="Upper Counters"). placement `{kind:"object", requiresFloor:true}`
(upper: `requiresFloor:false, againstWall:true`). materials group `kbwve.extended.wood`|`.metal`.
Wood construction time75 BuildWoodenStructureMedium / Furniture / xp Woodwork40 (metal: BuildWallMetal / Welding / MetalWelding50).
object `{isThumpable:true}`. block `container:{type:"counter"}`. magazine FineWoodWorking_Furniture_Counters.

### 6. Container furniture (dresser/locker/shelf/crate) — `furniture/dressers.json`, `furniture/bookshelves.json`
category "Furniture" / subcat "Dressers"/"Bookshelves" / Wood. placement `{kind:"object"}`.
inputs inline hammer+Plank+Nails; magazine FineWoodWorking_Furniture_Dressers. object `{canBePadlocked:true}`.
block `container:{type:"sidetable", capacity:10}` (type per furniture class).

### 7. Plain furniture (bed/chair/couch/table) — `furniture/{simple_beds,chairs,couches,large_tables}.json`
category "Furniture" / subcat "Chairs"/"Couches"/"Large Tables"/"Simple Beds". material Fabric (upholstered) or Wood.
placement `{kind:"object"}`. Upholstered inputs use tailoring set (FabricRoll_Cotton drain + scissors + sewingneedle + thread)
+ wood frame, dual skills {Tailoring,Woodwork}, construction.category Tailoring. Beds add `mattress`(Base.Mattress).
NO type block; often NO object block.

### 8. Roof — `roofing/<color>_roofs.json`
category "Roofing" / subcat "<Color> Roofs" / Wood / tooltip Tooltip_KBW_Shared_RoofSection.
placement `{kind:"floor", needToBeAgainstWall:false}` (flat) or `{kind:"object", needToBeAgainstWall:false}` (pitched).
inputs hammer+Plank+Nails+`roof_shingles`(Base.ClayShingle); magazine TheFamilyHandyman_StairsFences.
construction time200 BuildWallHammer / BuildWoodenStructureSmall / Carpentry. object `{blockAllSquare:false, canPassThrough:true, canBarricade:false}`.
block `roof:{family, pitch, role}`. (OUR newburbs roofs additionally carry faceByEdge on 4-face slopes — required for them to appear.)

### 9. Floor / rug — `floors.json`, `decorations/rugs.json`
FLOOR: category "Floors" / Stone / placement `{kind:"floor"}` (W only). masonry inputs; magazine FlooringGuide_Ceramic.
construction BuildLowNoTool / Masonry. no object block.
RUG: category "Decorations" / subcat "Rugs" / Fabric / placement `{kind:"object", needToBeAgainstWall:false}` 4-face; tailoring inputs.

### 10. Fence / railing / gate — `fencing.json`
category "Fencing" / subcat "High" / Metal. placement `{kind:"wall"}`. metal inputs; magazine TheFamilyHandyman_StairsFences.
construction time200 BuildWallMetal / BuildMetalStructureMedium. Multi-tile (multiple sprites per row/layer).
Vanilla gates = base mod `vanilla/fences_gates.json`, entityCompat wrappers, openability inherited.

### 11. Lighting — `lighting/indoor.json`
Uses `templates:{kbwve.light.electrical}` + `extends`. category "Lighting" / Electronics.
placement `{kind:"object", requiresFloor:true}` (switches: `needToBeAgainstWall:true, requiresFloor:false`).
materials `kbwve.light.basic`; Electricity 4; magazine PopularMechanics_Lighting. construction time150 BuildWallMetal / Electrical / canWalk:false.
block `lightSource:{radius:8, item:"Base.LightBulb", fuel:"Base.LightBulb"}`. object full flag set incl drawFloorGrid:false.

### 12. Decoration / sign / poster — `decorations/posters.json`
category "Decorations" / subcat "Posters" / Fabric / tooltip Tooltip_KBW_Shared_Poster.
placement `{kind:"overlay", needToBeAgainstWall:true}`. tailoring inputs; Tailoring 2; simple posters may omit knowledge.

### 13. Stairs — `stairs.json`
category "Stairs" / subcat "Metal Stairs". placement `{kind:"stairs"}`. Multi-tile geometry (W face y:-2 with 3 stacked rows; N face 1 row x 3 sprites).
inputs hammer + 13 Plank + 8 Nails; Woodwork 6; magazine TheFamilyHandyman_StairsFences. construction time200 BuildWallHammer / BuildMetalStructureMedium / Carpentry / xp Woodwork60. object `{isThumpable:false}`.
