# HANDOFF — Staging a NEW Knox Buildworks (KBW) add-on mod for deployment (PZ B42)

Audience: a fresh session that needs to package the TikiTown deliverables (or any new KBW
definitions) as a **standalone mod** and deploy it so the game loads it. This explains the exact
folder layout, the required files, and the deploy mechanics, using the existing test-bundle mod as
the proven reference.

> Context you must respect: we are an **independent investigator**, NOT the KBW/Drazion mod owner.
> NEVER edit the live KBW, WorldEssentials, or Drazion mod files. Our deliverables live in
> `c:\Users\josep\Kiro\zomboid\tikitown\` (source JSON) and we deploy a *separate* mod folder.
> Scratch/scripts live in `c:\Users\josep\Kiro\pz_craft_loops\`.

---

## 0. How KBW add-on content actually loads (the mental model)

KBW is a data-driven build-menu framework. A mod adds buildables by shipping **definition JSON
files** that KBW discovers through a **manifest**. The buildables reference **tile sprites** that
must exist in some loaded tilepack (for us: Drazion `tikitown_tiles`, which supplies all
`tt_newburbs_*` / `tikitown_*` sprites). So a working add-on mod = three things:

1. A standard PZ B42 mod skeleton (`mod.info` + `media/`).
2. A KBW **manifest.json** that lists our definition files.
3. The **definition JSON** files themselves (the buildables), plus **translation JSON** for the
   display-name / tooltip keys.

KBW reads the manifest at game load and registers every buildable. Sprites are resolved by name
against whatever tilepacks are loaded — we do NOT ship tiles; we `require` the tilepack mod.

---

## 1. Exact folder layout (copy this skeleton)

Reference: the live test bundle at
`...\steamapps\workshop\content\108600\3818232509\mods\TikiTownTestBundle\42\`.
A new mod `<ModId>` must replicate this under the mod's `42/` (B42) version folder:

```
<ModRoot>/
  42/
    mod.info
    poster.png                         (optional workshop thumbnail)
    media/
      KnoxBuildworks/
        manifest.json                  <-- KBW discovers definitions via this
        definitions/
          01_<name>.json               <-- one or more definition files (buildables)
          02_<name>.json
          ...
      lua/
        shared/
          Translate/
            EN/
              IG_UI.json               <-- displayName + group-name keys (IGUI_*)
              Tooltip.json             <-- tooltip keys (Tooltip_*)
```

Notes:
- The `42/` folder is the Build-42 content root (PZ B42 mods nest versioned content under `42/`).
- `media/KnoxBuildworks/...` is the fixed path KBW scans. Keep that casing exactly.
- Definition filenames are prefixed with a number (`01_`, `02_`, ...) only for load-order/readability;
  KBW loads whatever the manifest lists, in manifest order.

---

## 2. mod.info (required)

Plain `key=value` text, one per line. Reference (test bundle):

```
name=<Human Readable Mod Name>
id=<ModId>                          # unique; this is the folder/workshop id used everywhere
description=<one-line description>
require=KnoxBuildworks,WorldEssentialsKnoxBuildworksExpansion,tikitown_tiles
loadModAfter=KnoxBuildworks,WorldEssentialsKnoxBuildworksExpansion,tikitown_tiles
versionMin=42.0
tags=Build 42,Misc
```

Critical:
- `require=` lists the mod IDs that MUST be present. For our buildables that's KBW (framework),
  the WorldEssentials KBW Expansion (adds the categories like Roofing / Walls and Wall Finishes),
  and `tikitown_tiles` (Drazion's tilepack — supplies every sprite our JSON references). Without
  the tilepack, buildables load but render as missing/blank sprites.
- `loadModAfter=` the same three, so KBW + categories + tiles are all registered before us.
- `id=` must be unique and stable — placed-object persistence and workshop identity key off it.

---

## 3. manifest.json (required — this is what KBW reads)

Path: `media/KnoxBuildworks/manifest.json`. It lists every definition file, relative to the mod's
media root. Reference (test bundle had one merged file):

```json
{"schemaVersion":1,"definitions":["media/KnoxBuildworks/definitions/99_tikitown_TEST_ALL.json"]}
```

For a real multi-file mod, list each definition file:

```json
{
  "schemaVersion": 1,
  "definitions": [
    "media/KnoxBuildworks/definitions/21_tikitown_walls.json",
    "media/KnoxBuildworks/definitions/27_tikitown_newburbs_interiors.json",
    "media/KnoxBuildworks/definitions/28_tikitown_newburbs_walls.json",
    "media/KnoxBuildworks/definitions/31_tikitown_newburbs_roofs.json",
    "media/KnoxBuildworks/definitions/32_tikitown_newburbs_flags.json",
    "media/KnoxBuildworks/definitions/33_tikitown_newburbs_doors.json"
  ]
}
```

Rules:
- Paths are the full `media/KnoxBuildworks/definitions/<file>.json`, forward slashes.
- Ship the CHEAP tier of any cheap/accurate pair OR the accurate tier — never BOTH, they share
  buildable ids and would be duplicate-id collisions. (Pick one per pair.)
- Do NOT also ship the merged `99_..._TEST_ALL.json` alongside the individual files — same dup-id
  problem. The test bundle is a single merged file precisely so it is used ALONE.

---

## 4. Definition JSON files (the buildables)

These are our existing deliverables in `c:\Users\josep\Kiro\zomboid\tikitown\` (21..33 + _accurate).
Each file is `{"schemaVersion":1,"category":"<fallback>","source":"<note>","buildables":[ ... ]}`.
Just COPY the chosen files into `media/KnoxBuildworks/definitions/`. Key facts that matter when
packaging:

- **category / subcategory** on each buildable are what the in-game menu groups by. Confirmed live
  KBW top-level categories we target: `Walls and Wall Finishes`, `Doors`, `Roofing`,
  `Decorations`, `Furniture and Appliances`. Use the real strings (see the deliverables).
- **ids** must be globally unique across everything loaded. Ours are `tikitown.<family>.<sprite>`
  or `worldessentials.tikitown.<...>`. Do not renumber ids casually — placed objects persist by id
  (see TODO_standalone_id_overhaul.md: when this becomes a standalone mod, ids SHOULD be reworked,
  but only with a server wipe / migration plan).
- **sprites** referenced must exist in the loaded tilepack. Everything we ship resolves against
  Drazion `tikitown_tiles` (require it in mod.info). If a sprite sheet is absent from Drazion (e.g.
  `tt_newburbs_windows_01` was dropped in the merge), those buildables will not render — do not ship
  them. (See NEWBURBS_COVERAGE notes / the Windows+ BLOCKED finding.)

---

## 5. Translation JSON (display names + tooltips)

Path: `media/lua/shared/Translate/EN/`. Two files:
- `IG_UI.json` — maps every `translationKey` and `group.translationKey` (the `IGUI_*` keys) to the
  shown text. Format is a flat JSON object: `{ "IGUI_...": "Shown Name", ... }`.
- `Tooltip.json` — maps every `tooltipKey` (`Tooltip_*`) to tooltip text, same flat-object format.

Important: a buildable's `displayName` field in the definition is a fallback; the game prefers the
translation-key lookup. If you ship new buildables, you MUST add their `translationKey` /
`tooltipKey` entries to these files or the menu shows raw `IGUI_...` keys. The current test bundle's
`IG_UI.json` already contains all keys for 21..29 + roofs etc.; regenerate/extend it from the
definition files when adding new ones.

(How these were generated originally: scan every buildable's `translationKey`, `group.translationKey`,
and `tooltipKey`, and emit `{key: displayName}` / `{key: tooltip}`. A small Python pass over the
definition JSON produces both files.)

---

## 6. Deploy mechanics (where the files must physically land)

THE GAME LOADS THE STEAM-SUBSCRIBED COPY, not a staging folder. During dev we write to BOTH so the
loaded copy is always current. The test-bundle deploy script (`pz_craft_loops/build_test_bundle.py`)
writes the built file to two absolute paths — replicate this pattern for the new mod:

1. Local Zomboid Workshop staging copy:
   `C:\Users\josep\Zomboid\Workshop\<ModId>\Contents\mods\<ModId>\42\media\KnoxBuildworks\definitions\<file>.json`
2. Steam-subscribed workshop copy (THE ONE THE GAME LOADS):
   `C:\Program Files (x86)\Steam\steamapps\workshop\content\108600\<WORKSHOP_NUMERIC_ID>\mods\<ModId>\42\media\KnoxBuildworks\definitions\<file>.json`

For the test bundle: `<ModId>` = `TikiTownTestBundle`, `<WORKSHOP_NUMERIC_ID>` = `3818232509`.
A NEW mod needs its OWN workshop numeric id — that only exists AFTER the mod is first uploaded to
the Steam Workshop (or created as a local mod). For a brand-new, not-yet-uploaded mod, you deploy to
the LOCAL mods folder instead:
   `C:\Users\josep\Zomboid\mods\<ModId>\...`  (local mods load without Workshop)
Then enable it in the in-game Mods menu.

Deploy = copy the whole `42/` skeleton (mod.info, manifest.json, definitions/, lua translate) into
the target. On every content change, rewrite the changed definition JSON into the deployed copy.
The game only re-reads definitions on a full reload (main menu -> reload save, or restart) — a live
in-world refresh will NOT pick up changes.

---

## 7. Minimal step-by-step to stage a NEW mod

1. Pick `<ModId>` (unique, no spaces) and a human name.
2. Create the skeleton under `C:\Users\josep\Zomboid\mods\<ModId>\42\` (local mod) following §1.
3. Write `mod.info` (§2) with `require`/`loadModAfter` = KBW, WE KBW Expansion, tikitown_tiles.
4. Copy the chosen definition JSON files into `42/media/KnoxBuildworks/definitions/`.
   - Choose cheap XOR accurate per pair; never both.
5. Write `42/media/KnoxBuildworks/manifest.json` listing exactly those files (§3).
6. Generate `42/media/lua/shared/Translate/EN/IG_UI.json` + `Tooltip.json` from those definitions (§5).
7. (Optional) add `poster.png`.
8. Launch PZ, enable `<ModId>` in Mods, start/reload a save, verify categories/sprites in the build menu.
9. For iteration, use a deploy script that rewrites definitions into the enabled mod copy, then
   reload the save to re-read.

## 8. Gotchas (learned the hard way)
- **Dup ids** if you ship both tiers or ship individual files + the merged bundle. Pick one source set.
- **Blank sprites** = the referenced tile sheet isn't in a loaded tilepack (missing `require`, or the
  sheet was dropped in the Drazion merge). Verify sheet presence in the tiledef before shipping.
- **Raw IGUI_ keys showing** = missing translation entries; regenerate IG_UI.json/Tooltip.json.
- **Category shows under the wrong header / merges with KBW's** = the category/subcategory STRING
  collides with a live KBW one (e.g. our roofs had to be prefixed `Newburbs <Color> Roofs` so they
  would not merge into KBW's `Grey Roofs`/`Black Roofs`). Use distinct subcategory strings.
- **Changes not appearing** = game didn't reload definitions; exit to menu and reload the save.
- **Never edit live KBW/WE/Drazion files** — only our own mod folder.

## 9. Reference files to copy structure from
- mod.info:        `...\3818232509\mods\TikiTownTestBundle\42\mod.info`
- manifest.json:   `...\3818232509\mods\TikiTownTestBundle\42\media\KnoxBuildworks\manifest.json`
- translations:    `...\42\media\lua\shared\Translate\EN\IG_UI.json` + `Tooltip.json`
- deploy script:   `c:\Users\josep\Kiro\pz_craft_loops\build_test_bundle.py` (DEPLOY_PATHS pattern)
- source defs:     `c:\Users\josep\Kiro\zomboid\tikitown\2*_*.json`, `3*_*.json`
