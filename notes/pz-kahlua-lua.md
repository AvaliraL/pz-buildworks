---
inclusion: fileMatch
fileMatchPattern: ['**/*.lua', 'pz_craft_loops/kbw_tilepatch.py']
---

# Project Zomboid Lua (Kahlua) rules

PZ runs Lua through Kahlua, a Lua 5.1-style runtime on the JVM. It is NOT standard Lua.
Testing with a standard Lua runtime (lupa, lua5.x) only proves syntax and logic. It does not
prove a function exists in game.

## Not available in Kahlua (do not use)
- `next()`: confirmed missing (WE dev report, 2026-08-28). To test "table not empty", loop with
  `pairs` and set a flag, or keep a count.
- `goto` / labels, integer division `//`, bitwise operators (`&`, `|`, `~`, `<<`, `>>`): 5.2+ syntax.
- `load(string)` style chunk loading at runtime, and the `debug` library, can't be relied on.

## Safe to use
- `pairs`, `ipairs`, `pcall`, `type`, `tostring`, `tonumber`, `rawget`, `setmetatable`,
  `string.find(s, p, 1, true)`, `string.format`, `table.sort`, `table.concat`, `math.*`.

## When writing or reviewing Lua for PZ
- Grep the file for the "not available" list before shipping.
- When mocking for tests, delete `next` (and other non-Kahlua globals) from the test runtime
  first (`next = nil`), so a missing-function bug fails the test instead of passing.
- Say "tested against mocks" vs "tested in game" explicitly in handoffs.
