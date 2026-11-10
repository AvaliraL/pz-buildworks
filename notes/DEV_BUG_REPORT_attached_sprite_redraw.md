# Bug report: wall-overlay sprites built with `kind: "overlay"` don't appear until the area is reloaded

**Mod:** Knox Buildworks (Workshop 3772269882), B42 (PZ build 26486631)
**Severity:** cosmetic, but players think the build failed and rebuild it, paying the cost twice
**Status:** reproduced in single player (2026-11-10); cause found in code, fix not applied

## What happens

- Build any wall-overlay piece (`placement.kind = "overlay"`, `needToBeAgainstWall: true`) whose sprite
  goes down the attached-sprite path (`AttachedSprites.isWallDecorationSprite` = true).
- The timed action finishes and the materials are used, but nothing appears on the wall.
- Some pieces appear after a moment, some don't appear at all.
- Leaving the area (out of sight, so the chunk is dropped) and coming back makes them all appear.
  The data is there and saved; only the first draw is missing.
- Pieces that build as their own object (props, thumpables) show at once, but can be drawn in the
  wrong order until the same reload. For example, a corner overlay showed in front of a fridge built
  on the same square, and leaving the area and coming back corrected it.

## Cause

`shared/KnoxBuildworks/World/AttachedSprites.lua`:

- `AttachedSprites.attach` adds the sprite instance to `object:getAttachedAnimSprite()` and transmits
  it. But it never tells the renderer that the host object changed.
- B42 caches each chunk level's render (`FBORenderChunk`). An object whose sprite list changes keeps
  its cached image until something else marks the chunk dirty: a nearby object add, lighting, or a
  chunk reload. That is why the delay looks random.
- `AttachedSprites.remove` has the same gap (a removed overlay stays visible until a redraw).

Vanilla marks the render dirty itself after changing an object's sprites, e.g.
`server/BuildingObjects/ISMoveableCursor.lua:827` and `:841`:

```lua
object:invalidateRenderChunkLevel(FBORenderChunk.DIRTY_REDRAW)
```

## Suggested fix

After the sprite list changes in both `attach` and `remove`:

```lua
if object.invalidateRenderChunkLevel and FBORenderChunk then
    object:invalidateRenderChunkLevel(FBORenderChunk.DIRTY_REDRAW)
end
```

In MP the render cache lives on each client, so the same call is needed where a client applies the
transmitted sprite update (server -> client), not only on the side that ran the build.

## Not verified

- I haven't tested whether `DIRTY_REDRAW` alone is enough. The other flag vanilla uses for added objects is
  `DIRTY_OBJECT_ADD` (`buildRecipeCode.lua:436`).
- The MP client path is not tested.
