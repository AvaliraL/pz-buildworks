# TODO — Overhaul buildable IDs when going fully standalone

**Status:** OPEN — deferred until the deliverables become a standalone mod (not a live in-place patch).

## Why ids are frozen right now
These deliverables are being applied to a LIVE server without a wipe. It is NOT known how Knox
Buildworks persists player-built objects (possibly keyed by the buildable `id`). To be safe,
**do not change any existing buildable `id`** while patching in place — a changed id could
orphan already-built objects on the live map/save.

What is safe to change WITHOUT a wipe (confirmed reasoning):
- **Sprite references** (`tt_newburbs_*` etc.) — we don't author sprite gids; those belong to
  Drazion's tilepack. Unchanged by us.
- **Display names / tooltips** — resolve via `translationKey` -> EN translation files; pure UI
  text. Changing "C1" -> "White" is cosmetic, affects nothing structural. SAFE mid-server.
- **category / subcategory / group** — menu organization; does not affect built objects.
- **geometry / recipe** — affects how NEW builds place/cost; does not rewrite existing objects.

## What to do when standalone
Once this is a clean standalone mod (fresh install / acceptable wipe), overhaul the buildable
`id` scheme to something consistent and human-readable (e.g. encode color + piece-type instead of
raw sprite index), aligned with the final naming. Until then, keep ids byte-stable.
