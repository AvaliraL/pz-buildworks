# -*- coding: utf-8 -*-
"""Moveable rotation for our buildables whose tile pack groups them badly (2026-11-02).

Rotating a held moveable (vanilla ISMoveableSpriteProps:getFaces) needs the tile's Facing plus
per-face sprite offsets Noffset / Eoffset / Soffset / Woffset. The engine generates those at load
(IsoWorld.LoadTileDefinitions, checked with javap): moveable tiles of ONE tileset are grouped by
GroupName + " " + CustomName, and offsets are only set when the group has <= 4 tiles, every tile
has a Facing and no facing appears twice. Several packs put far more tiles under one name
(Dirkies kitchen "Modern Corner / Counter" = 52 tiles, Block Trasher 8) or have no GroupName, so
those pieces can't be rotated when placed from the inventory.

Our KBW definitions already say which sprites are the facings of one piece, so we compute the
offsets ourselves and set them at runtime (OnLoadedTileDefinitions), the way
KBWCommunity_TileFixes.lua removes properties. Pieces are skipped (and reported) when:
  * the engine already rotates them,
  * a face sprite isn't moveable / has no Facing / two faces share a Facing,
  * faces sit in different tilesets (offsets are index steps within one sheet),
  * multi-tile faces (sprite grids rotate through a different engine path),
  * a sprite would get conflicting offsets from two buildables.
"""
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kbw_tilepatch as k

LUA_NAME = "KBWCommunity_Rotation.lua"
_WORKSHOP = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600"


def load_sheets():
    """sheet name -> per-tile property dicts (vanilla, Community pack, any installed .tiles)."""
    sheets = {}

    def add(tilesets, override=False):
        for n, t in tilesets.items():
            name = n.decode("utf-8", "replace")
            if override or name not in sheets:
                sheets[name] = [{a.decode("utf-8", "replace"): b.decode("utf-8", "replace") for a, b in raw}
                                for raw in t[6]]

    _v, vts, _o = k._parse(open(k._VANILLA_TILES, "rb").read())
    add(vts, True)
    _v, cts = k._load_community_tilesets()
    add(cts, True)
    for p in glob.glob(os.path.join(_WORKSHOP, "*", "mods", "**", "*.tiles"), recursive=True):
        if p.endswith(".patch.tiles"):
            continue
        try:
            _v, ts, _o = k._parse(open(p, "rb").read())
        except Exception:
            continue
        add(ts)
    return sheets


def engine_rotates(sheets, sheet, idx):
    """True if the engine's own grouping already gives this tile face offsets."""
    tiles = sheets.get(sheet) or []
    p = tiles[idx] if idx < len(tiles) else {}
    if "IsMoveAble" not in p or "GroupName" not in p:
        return False
    key = (p["GroupName"], p.get("CustomName"))
    members = [q for q in tiles if "IsMoveAble" in q and (q.get("GroupName"), q.get("CustomName")) == key]
    if any(q.get("SpriteGridPos", "None") != "None" for q in members) or len(members) > 4:
        return False
    facings = [q.get("Facing") for q in members]
    return None not in facings and len(set(facings)) == len(facings) and len(members) > 1


def _face_sprites(stage):
    faces = ((stage.get("geometry") or {}).get("faces")) or {}
    out = []
    for face in faces.values():
        cells = [c for L in face.get("layers", []) for r in L.get("rows", []) for c in r if isinstance(c, str)]
        if len(cells) != 1:
            return None          # multi-tile face
        out.append(cells[0])
    return out


def build_offsets(buildables, sheets):
    """(offsets {sprite: {Noffset: n, ...}}, report dict)."""
    offsets, owner = {}, {}
    report = {"fixed": 0, "already": 0, "skipped": {}}

    def skip(reason, bid):
        report["skipped"].setdefault(reason, []).append(bid)

    for b in buildables:
        for st in b.get("stages") or []:
            sprites = _face_sprites(st)
            if not sprites or len(set(sprites)) < 2:
                continue
            sprites = sorted(set(sprites))
            parsed = [s.rpartition("_") for s in sprites]
            if len({p[0] for p in parsed}) != 1 or not all(p[2].isdigit() for p in parsed):
                skip("faces in different tilesets", b["id"])
                continue
            sheet = parsed[0][0]
            tiles = sheets.get(sheet)
            if tiles is None:
                skip("tileset not found", b["id"])
                continue
            idxs = [int(p[2]) for p in parsed]
            if any(i >= len(tiles) for i in idxs):
                skip("tile index out of range", b["id"])
                continue
            props = [tiles[i] for i in idxs]
            if any("IsMoveAble" not in p for p in props):
                skip("not moveable", b["id"])
                continue
            facing = [p.get("Facing") for p in props]
            if None in facing or len(set(facing)) != len(facing):
                skip("missing / duplicate Facing in the pack", b["id"])
                continue
            if any(p.get("SpriteGridPos", "None") != "None" for p in props):
                skip("sprite grid", b["id"])
                continue
            if all(engine_rotates(sheets, sheet, i) for i in idxs):
                report["already"] += 1
                continue
            by_face = dict(zip(facing, idxs))
            conflict = False
            new = {}
            for s, i, f in zip(sprites, idxs, facing):
                want = {other + "offset": j - i for other, j in by_face.items() if other != f}
                if s in offsets and offsets[s] != want:
                    conflict = True
                new[s] = want
            if conflict:
                skip("conflicting offsets (sprite shared by two pieces)", b["id"])
                continue
            for s, want in new.items():
                offsets[s] = want
                owner.setdefault(s, b["id"])
            report["fixed"] += 1
    return offsets, report


_LUA_HEAD = r'''-- AUTO-GENERATED by pz_craft_loops/rotation_fix.py -- do not edit by hand.
-- Face offsets for moveable rotation. The engine only generates Noffset/Eoffset/Soffset/Woffset
-- when a tileset groups at most 4 tiles under one GroupName + CustomName; several packs group far
-- more (Dirkies kitchen counters: 52), so those pieces could not be rotated when placed from the
-- inventory. Offsets come from our Knox Buildworks definitions (which sprites are the faces of
-- one piece). Applied once tile definitions are loaded.
local OFFSETS = {
'''
_LUA_TAIL = r'''}

local applied = false
local function apply()
    if applied then return end
    applied = true
    local done, missing = 0, 0
    for spriteName, values in pairs(OFFSETS) do
        local sprite = getSprite(spriteName)
        local props = sprite and sprite:getProperties() or nil
        if props then
            for key, value in pairs(values) do
                pcall(function() props:set(key, tostring(value)) end)
            end
            pcall(function() props:CreateKeySet() end)
            done = done + 1
        else
            missing = missing + 1
        end
    end
    print("[KBWCommunity] Rotation: face offsets set on " .. tostring(done) .. " sprite(s), "
        .. tostring(missing) .. " not loaded")
end

if Events.OnLoadedTileDefinitions then Events.OnLoadedTileDefinitions.Add(apply) end
Events.OnGameStart.Add(apply)
if Events.OnServerStarted then Events.OnServerStarted.Add(apply) end
'''


def write_rotation_lua(path, offsets):
    lines = []
    for s in sorted(offsets):
        vals = ", ".join("%s = %d" % (kk, offsets[s][kk]) for kk in sorted(offsets[s]))
        lines.append('    ["%s"] = { %s },' % (s, vals))
    lua = _LUA_HEAD + "\n".join(lines) + "\n" + _LUA_TAIL
    for bad in ("next(", "goto ", "//", "debug."):
        if bad in lua.replace("-- AUTO-GENERATED", ""):
            raise RuntimeError("Kahlua-unsafe construct in %s: %s" % (LUA_NAME, bad))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8", newline="\n").write(lua)
    return len(offsets)
