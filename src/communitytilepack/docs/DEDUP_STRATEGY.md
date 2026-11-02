# Dedup strategy — Community Tilepack vs TikiTown

Goal: fully implement BOTH tile packs (TikiTown + Community), but when the same art appears in
both, show only ONE build-menu entry.

## Decisions
- **Community wins.** When a duplicate is confirmed, the **Community** entry is the one that
  displays; the **TikiTown** entry for that art is **suppressed** (not emitted / dropped from its
  bundle).
- **Duplicates are identified MANUALLY** by the owner (no auto image-hash matching). Names do NOT
  match across packs (verified: 0 exact sheet-name overlaps), so dedup is by human-confirmed art
  equivalence, recorded in the registry below.

## Why sprite-name, not menu-name
Two buildables collide when they reference the **same sprite name** (engine logs "Sprite reused" +
doubles the menu entry). TikiTown and Community use DIFFERENT sheet/sprite names even for identical
art, so the engine will NOT auto-detect them — we must suppress explicitly.

## Mechanism (build-time suppression, no runtime Lua)
1. Maintain `DUPLICATE_REGISTRY.csv` (one row per confirmed duplicate):
   `tikitown_buildable_id , community_buildable_id , note`
2. When building the **TikiTown** deliverables/bundle, DROP any buildable whose id appears in the
   `tikitown_buildable_id` column (Community wins).
3. The **Community** build emits everything (never suppressed).
4. Registry is the single source of truth — every dedup decision is one auditable row. Nothing is
   guessed; rows are added only when the owner confirms the art is the same.

## Registry
See `DUPLICATE_REGISTRY.csv` (created when the first duplicate is confirmed). Format:
```
tikitown_id,community_id,note
```

Until a row exists, nothing is suppressed — both entries show. The initial counter test
(`d_furniture_kitchen_01`) is NEW art with no TikiTown equivalent, so no suppression applies yet.
