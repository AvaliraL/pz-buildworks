# Knox Buildworks: `Registry:list()` stack overflow with large definition sets

Mod: Knox Buildworks (Workshop 3772269882), file
`42/media/lua/shared/KnoxBuildworks/Definitions/Registry.lua`, line 128.
Severity: KBW never finishes loading its definitions (no build menu content). In our case the
game then showed "Sorry, an unexpected error occurred" when starting a world.

## Symptom

```
ERROR: General f:0> Lua(BuiltIn).partition_comp> Exception thrown
    java.lang.RuntimeException: Stack overflow at Coroutine.ensureStacksize(Coroutine.java:135).
    ...
    Lua((MOD:Knox Buildworks)).list(Registry.lua:128)
    Lua((MOD:Knox Buildworks)).finalize(Registry.lua:133)
    Lua((MOD:Knox Buildworks)).finishState(Loader.lua:127)
    Lua((MOD:Knox Buildworks)).stepAsync(Loader.lua:244)
```

It repeats on every loader step. It started once our add-on content reached about 5,000
buildables. Total registry was about 8,500 (KBW + VE about 3,500).

## Cause

```lua
function Registry:list()
    local list = {}
    for _, entry in pairs(self.entries) do list[#list + 1] = entry end
    table.sort(list, function (a, b) return a.id < b.id end)
    return list
end
```

The comparator is correct. The problem is Kahlua's `table.sort` (game `stdlib.lua`):
- It's a recursive quicksort that always takes the first element as the pivot.
- Only the right-hand recursion is a tail call; the left-hand one stacks.
- Kahlua tables keep insertion order (`J2SEPlatform` uses `LinkedHashMap`), so `pairs()` hands
  the sort the definitions in registration order.
- A definition file with long runs of related ids, such as families of variants, makes the left
  recursion very deep.
- Kahlua's `Coroutine` limits are `MAX_STACK_SIZE = 3000` slots and `MAX_CALL_FRAME_STACK_SIZE = 1000`.

We reproduced it by simulating Kahlua's exact algorithm on the real registration order. The
recursion depth was 482 with our content in generation order, and 83 for KBW + VE alone. At about
6 slots per level, 482 levels reaches the 3000-slot limit, which matches the crash.

`client/KnoxBuildworks/Debug/BuildTestRunner.lua` already notes this: "Stable iterative merge sort;
Kahlua's recursive table.sort overflows on large tied lists".

## Suggested fix

Use the same iterative merge sort in `Registry:list()`, and in any other sort that can receive the
full definition list, such as the name sort in `Groups.lua:134`. That makes load independent of how
add-on authors order their files.

## Our workaround (shipped on our side)

We now write our two large generated files (`39_tikitown_wall_overlays.json`,
`40_tikitown_lower_walls.json`, 900 buildables each) in a fixed pseudo-random order: md5 of the id.
Simulated depth is back to 82, and stays at 108 even at double the content. Menu order is unchanged,
because groups sort members by level, then id.

## What was verified

- Read in the game install: the crash trace in `console.txt`; KBW `Registry.lua`; Kahlua's sort in
  `ProjectZomboid/stdlib.lua`; `LinkedHashMap` in `J2SEPlatform`; the stack constants in
  `Coroutine.class`.
- Simulated depths come from `pz_craft_loops/kbw_sort_depth_check.py`. That script runs the same
  algorithm on the ids, in manifest order.
- Confirmed in game (2026-11-08 17:39 session): with the reordered files, KBW loads with no
  `Stack overflow` / `partition_comp` errors and a new world starts. The earlier sessions showed
  8+ overflows per launch.
