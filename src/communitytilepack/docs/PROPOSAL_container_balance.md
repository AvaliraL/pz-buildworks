vfc n# Proposal: Container Storage and Cost Based on Space Used

**Status:** draft for review
**Scope:** containers in our KBW packs (Community Tilepack, TikiTown, Fears, TK). Appliances whose storage is set by vanilla (freezers, ovens, the coffee makers) are excluded.

## 1. Problem

Our container capacities and build costs come from wherever each pack or transpile left them (pack tile values, KBW Vanilla Expanded presets, guesses). Two containers taking the same space can differ a lot in storage and cost. Some are cheap for what they hold, so there's no consistent rule a player can learn.

## 2. Baseline: the KBW Military Crate

Source: `KnoxBuildworks/42/media/KnoxBuildworks/definitions/military_crates.json` (`kbw.military_crate.green` / `.gray` / `.paintable`, all identical apart from colour). The in-game tile report (`kbw_location_military_generic_01_0`) confirms the values below.

| | Value |
|---|---|
| Storage | **100** (`container = militarycrate`, `ContainerCapacity = 100`) |
| Footprint | 1 floor square, low (`IsLow`) |
| Stacking | `IsStackable`, up to **3 high** on one square |
| Skill | MetalWelding 7 |
| Tools (kept) | Welding mask |
| Consumables | Blowtorch 4 uses, Welding rods 4 uses |
| Materials | Sheet Metal ×2, Small Sheet Metal ×2, Scrap Metal ×1 |
| Other | Can be padlocked, blocks the whole square |

One crate fills one **slot**: one floor square, one third of the room height. A square holds at most 3 slots.

*Not yet checked: the shared base entry `kbw.military_crate` (build time, XP, placement rules). These values come from the colour variants.*

## 3. Rule

**Crate-equivalents (CE) = floor squares used × height slots used**

| Shape | Example | CE |
|---|---|---|
| 1 square, low (crate height) | crate, low drawer, counter | 1 |
| 1 square, 2/3 height | tall cabinet, shelf unit | 2 |
| 1 square, full height | wardrobe, wire rack, tall shelving | 3 |
| 2 squares, low | 2-tile workbench, long counter | 2 |
| 2 squares, full height | double wardrobe | 6 |

- **Storage = 100 × CE.** If a single container can't exceed 100 (see 5.1), the object gets CE separate 100-capacity compartments instead. Vanilla fridges already have two (fridge + freezer).
- **Cost = crate recipe × CE**, rounded up per material. Tools and skill stay the same as the crate (they set the tier, not the size).
- **Wall-mounted or table-top storage** (wall shelves, spice racks) counts as **1/3 CE per wall face**: storage 33, cost one third of a crate (rounded up). That keeps small fixtures cheap and useful without matching a crate.
- **Partial fills:** if an object visibly uses less than its full slots (open shelving, a mostly empty frame), apply a **0.5–0.75 factor** to storage only. Cost stays at full CE, so open designs are a trade-off rather than a free upgrade.

## 4. Worked examples (current → proposed)

| Object | Shape | CE | Storage now | Proposed storage | Proposed cost (metal) |
|---|---|---|---|---|---|
| Wire Shelf Rack (TK) | 1 sq, full height, open | 3 (×0.75) | 50 | 225 | 3× crate |
| Fears workbench (any) | 2 sq, low | 2 | 80 | 200 | 2× crate |
| Metal Kitchen Wall Shelf (TK) | wall, 1 face | 1/3 | 30 | 33 | 1/3 crate |
| TikiTown wardrobe | 1 sq, full height | 3 | 25 | 300 | 3× crate (wood, see 5.2) |
| TikiTown drawers | 1 sq, low | 1 | 20 | 100 | 1× crate (wood) |

*"Storage now" comes from the current definitions. Proposed numbers apply the rule as written, with no rebalancing yet.*

## 5. Open questions

1. **Capacity cap:** confirm whether B42 limits a single world container's capacity (the crate sitting at exactly 100 suggests a limit, but this isn't verified). If there's a cap, CE above 1 becomes multiple compartments.
2. **Wood-equivalent recipe:** the crate is metal (MetalWelding 7). Wooden containers need a wood "crate slot" recipe (for example Planks/Nails sized to match, at Carpentry ~7) so wood and metal storage cost about the same per CE.
3. **Is 100 per slot too generous for furniture?** Vanilla furniture sits much lower (wardrobe 25, drawers 20, shelves 40). Option: keep the crate as the top end and use a **furniture rate of 50 per CE** for non-industrial furniture, still with crate-scaled cost.
4. **Bigger-than-crate tiers (from the todo list):** a container that fills all 3 slots of a square, at 3 crates' storage and 3 crates' cost. This rule covers that directly (CE 3).
5. **Workbench pairing:** the Fears benches are due to copy the cost of the other-mod workbench they're synced with. Decide whether that cost or this rule wins for their **storage**.

## 6. Plan

1. Answer the open questions, especially 5.1 (cap) and 5.3 (furniture rate).
2. Add a CE field per container definition in the generators (`make_*.py` and the deliverable JSONs). It's computed from the tile footprint (`SpriteGridPos`) and height (`IsLow`/`IsHigh`/`Surface`), with manual overrides.
3. Generate storage and cost from CE at build time, so the rule stays in one place.
4. Produce a before/after table for every affected container and review it before rebuilding.
5. Test in game: capacities shown, recipes, stacking/padlocks unchanged.
