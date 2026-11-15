# -*- coding: utf-8 -*-
"""Generate 52_tikitown_lighting.json (user, 2026-11-14): Drazion's lighting_indoor_tterika_01 and
lighting_outdoor_tterika_01 as working lights. No Building Menu / BuildingCraft addon covers these
sheets (all installed addons checked), so pieces come from the tiles themselves (their light, facing,
attach and table-top flags) and their art; nothing built any of these tiles before.

Setup copies KBW Vanilla Expanded's confirmed lamps (definitions/lighting/indoor.json): native light
switch, VE's basic light materials (kbwve.light.basic: 10 electronics scrap, 4 electric wire, 5 scrap
metal, 1 light bulb, 5 screws), a screwdriver, Electricity 4, gated by the Popular Mechanics: Lighting
magazine (or Electricity 5). Floor lamps add a metal pipe (as VE's floor lamps); the two-storey
outdoor lights add 2 metal pipes.

Indoor (lighting_indoor_tterika_01):
  floor lamps 0, 8-13 (one tile, no facing)                      7 pieces, one card
  table lamps, 8 colours x 4 facings (Facing E 16-23, S 24-31, W 32-39, N 40-47), table-top
  wall lamps Gold 48-51 / Gold Beige 52-55 (attachedW/N/E/S)       + fluorescent wall lamps:
  long 2-tile (W face 57 over 56, N face 58 59) and short (W 61, N 60)
  exit sign, 2 tiles (W face 5 over 4, N face 6 7)
Outdoor (lighting_outdoor_tterika_01):
  Victorian lamp post 0 (one tile)
  "OPEN" neon sign 6 (north wall) / 7 (west wall), on the PACK tiles first (user: try the existing
    version; the 18+ / GIRLS neon needed our own copies, so this may too)
  two-storey poles: the lower half is never a piece of its own (user). Pole 16 (dark) under the
    single-arm street light 8-11 and the two traffic lights 12-15 / 20-23; pole 17 (grey, white
    base) under the double street light 18 / 19. Built like World Essentials' own pole lights
    (06_furniture.json searchlights): two layers (pole on the square, head one storey up) and
    nativeObject.poleSprite, so only the head becomes the light switch. The pole tiles carry no
    solid / car-stopping flags and the piece is not thumpable, so players and cars pass through
    the lower half (user).
  traffic lights: the pack gives their heads no light; our TikiTown tile patch makes them yellow
    street lights (255/255/0 = vanilla LightBulbYellow), and their recipe takes a yellow bulb.
  Lit sprites: the tile patch also adds HasLightOnSprite to every tile that has art on the pack's
  *_on sheet, so the game shows the lit version when a light is on (kbw_tilepatch._TT_PATCH_GROUPS).
  Not built yet: the pole-top lamp heads 24-31 (they sit above the pole tops; how they mount is unclear).
NOT yet tested in game.
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kbw_tilepatch as k   # noqa: E402

IN = "lighting_indoor_tterika_01"
OUT_SHEET = "lighting_outdoor_tterika_01"
OUT = r"c:\Users\josep\Kiro\zomboid\tikitown\52_tikitown_lighting.json"
PREFIX = "worldessentials.tikitown.light_"
KNOWLEDGE = {
    "recipes": ["KBWKnowledge_PopularMechanics_Lighting"], "hideUntilLearned": True, "needToBeLearned": True,
    "sources": [{"type": "magazine", "item": "KnoxBuildworks.PopularMechanics_Lighting"}],
    "skillAlternatives": [{"mode": "all", "skills": {"Electricity": 5}}],
}
SCREWDRIVER = {"id": "screwdriver", "role": "tool", "mode": "keep", "tags": ["base:screwdriver"],
               "flags": ["Prop1", "MayDegradeVeryLight"], "amount": 1}
CONSTRUCTION = {"time": 150, "timedAction": "BuildWallMetal", "completionSound": "BuildMetalStructureSmall",
                "canWalk": False, "category": "Electrical", "xp": {"Electricity": 20}}
# VE's kbwve.light.basic spelled out, so the yellow-bulb version can swap the bulb
BASIC = [
    {"id": "electronics", "role": "material", "mode": "consume", "items": ["Base.ElectronicsScrap"], "amount": 10},
    {"id": "electric_wire", "role": "material", "mode": "consume", "items": ["Base.ElectricWire"], "amount": 4},
    {"id": "scrap_metal", "role": "material", "mode": "consume", "items": ["Base.ScrapMetal"], "amount": 5},
    {"id": "light_bulb", "role": "material", "mode": "consume", "items": ["Base.LightBulb"], "amount": 1},
    {"id": "screws", "role": "material", "mode": "consume", "items": ["Base.Screws"], "amount": 5},
]
OBJ_FLOOR = {"isProp": True, "dismantable": True, "blockAllSquare": True}
OBJ_WALL = {"isProp": True, "dismantable": True, "blockAllSquare": False, "canPassThrough": True, "drawFloorGrid": False}
# two-storey poles: not a prop, not thumpable, nothing blocks the square (pole tiles have no solid flags)
OBJ_POLE = {"isThumpable": False, "dismantable": True, "blockAllSquare": False, "canPassThrough": True}

FLOOR_LAMPS = [(0, "Mauve"), (8, "Gold"), (9, "Black"), (10, "Pink"), (11, "Plum"), (12, "Red"), (13, "Beige")]
TABLE_COLOURS = ["Gold", "Black", "Pink", "Plum", "Red", "Beige", "Orange", "Green"]


# ---------------------------------------------------------------------------------------------
# OUR COPIES (user, in game 2026-11-14), tileset KBWTikiTownLights in the TikiTown copy tiledef
# kbwtikitown_walloverlays 8179 (tikitown_wall_overlays.write_overlay_assets appends them), with the
# lit art in KBWTikiTownLights_on at the same index (the game shows <tileset>_on_<index> for a lit
# HasLightOnSprite tile). Map-placed pack tiles are untouched (user: "i dont want to affect any map
# placed copies").
#  * street / traffic lights + lamp post: NO `streetlight` flag. Vanilla lights a streetlight tile
#    only at night and only on grid power (LightingJNI.checkLights), never on a generator, and skips
#    the switch click (ISToggleLightAction); without it they work like player-built lamps (user).
#    Traffic heads get their yellow light (vanilla LightBulbYellow 255/255/0, radius 6) here instead
#    of in the tile patch. Every outdoor copy (poles too) gets BlocksPlacement: KBW refuses a build on
#    a square that already holds a BlocksPlacement sprite (Placement.lua), so pole lights cannot
#    overlap (user). BlocksPlacement does not block movement.
#  * exit sign + long fluorescent lamp: the game links a multi-tile light (one toggle switches both
#    halves) only when every tile of its GroupName + CustomName + Facing group has SpriteGridPos
#    (IsoWorld.LoadTileDefinitions). The pack's long fluorescent lamp shares its group with the short
#    one (60 / 61, no SpriteGridPos), so its halves never linked; the exit sign's group is complete
#    and links. In our tileset each group is complete. No depth (like the pack's long lamp, which
#    draws fine): the pack's exit-sign depth cells put one half behind its wall.
LIGHT_TILESET = "KBWTikiTownLights"
LIGHT_ON_TILESET = LIGHT_TILESET + "_on"
TRAFFIC_HEADS = set(range(12, 16)) | set(range(20, 24))
_TRAFFIC_LIGHT = [(b"lightswitch", b""), (b"lightR", b"255"), (b"lightG", b"255"), (b"lightB", b"0"),
                  (b"LightRadius", b"6")]
# (sheet, source index, copy index): outdoor at the same index, indoor after them
LIGHT_COPIES = ([(OUT_SHEET, i, i) for i in [0] + list(range(8, 24))]
                + [(IN, i, 32 + i - 4) for i in range(4, 8)]          # exit sign      -> 32..35
                + [(IN, i, 40 + i - 56) for i in range(56, 60)])      # long fluorescent -> 40..43
_COPY_INDEX = {(sh, s): j for sh, s, j in LIGHT_COPIES}
# Two-storey lights, second pass (user, in game 2026-11-14: "i cant interact with any of the 2 high
# streetlamps"; the lamp post clicked but never lit):
#  * Outdoors (no map room) vanilla IsoLightSwitch.setActive returns at once unless the light is
#    "modifiable", and the constructor sets canBeModified only for a tile with a light colour AND
#    IsMoveAble. Every outdoor light copy now has IsMoveAble (the pack's lamps that work outdoors
#    have it too).
#  * The head hangs one storey up, out of reach of the ground context menu (BuildingCraft builds it
#    the same way and has no toggle path either). Each head gets its OWN pole copy, and the two form
#    one 2-level sprite grid (SpriteGridPos 0,0 + SpriteGridLevel 0 / 1, a group of their own): the
#    pole is a light switch too (same colour, LightRadius 1, so it is not a "room switch"), and the
#    vanilla toggle switches every light of the grid (IsoLightSwitch.switchLight ->
#    getSpriteGridObjects, which walks the grid's levels). The definitions drop nativeObject.poleSprite.
# (head source index, pole source index, style label, KBW face)
POLE_HEADS = ([(h, 16, "Street", f) for h, f in zip((8, 9, 10, 11), "WNES")]
              + [(h, 17, "Double Street", f) for h, f in zip((18, 19), "WN")]
              + [(h, 16, "Traffic 1", f) for h, f in zip((12, 13, 14, 15), "WNES")]
              + [(h, 16, "Traffic 2", f) for h, f in zip((22, 23, 20, 21), "WNES")])
POLE_BASE = 48
_FACE_WORD = {"W": "West", "N": "North", "E": "East", "S": "South"}
_FACE_FACING = {"W": b"E", "N": b"S", "E": b"W", "S": b"N"}   # KBW face -> tile Facing (opposite)


def pole_sprite(head):
    """Our pole copy paired with head copy <head> (lighting_outdoor_tterika_01 index)."""
    j = [h for h, _p, _l, _f in POLE_HEADS].index(head)
    return "%s_%d" % (LIGHT_TILESET, POLE_BASE + j)
# copied tiles that have lit art on the pack's *_on sheet (the rest have none: lamp post 0, poles,
# double street light 18 / 19, traffic heads 14 / 15 / 20 / 21)
LIT_SOURCES = ({(OUT_SHEET, i) for i in list(range(8, 14)) + [22, 23]}
               | {(IN, i) for i in list(range(4, 8)) + list(range(56, 60))})


def light_sprite(sheet, i):
    """Our copy of <sheet>_<i>."""
    return "%s_%d" % (LIGHT_TILESET, _COPY_INDEX[(sheet, i)])


def copy_tiles(tts, has_on_art):
    """[(source sprite, copy sprite, props, source lit sprite or None, copy lit sprite or None)].
    tts: parsed tikitown_tiles tilesets; has_on_art(source lit sprite) -> bool."""
    out = []
    for sh, s, j in LIGHT_COPIES:
        props = [(a, b) for a, b in tts[sh.encode()][6][s] if a not in (b"streetlight", b"HasLightOnSprite")]
        have = {a for a, _b in props}
        if sh == OUT_SHEET and s in TRAFFIC_HEADS:
            props += [kv for kv in _TRAFFIC_LIGHT if kv[0] not in have]
        on_src = "%s_on_%d" % (sh, s)
        lit = (sh, s) in LIT_SOURCES and has_on_art(on_src)
        if lit:
            props.append((b"HasLightOnSprite", b""))
        if sh == OUT_SHEET:
            props.append((b"BlocksPlacement", b""))
            if any(a == b"lightR" for a, _b in props):
                props.append((b"IsMoveAble", b""))     # outdoors a light must be modifiable to switch
        out.append(("%s_%d" % (sh, s), "%s_%d" % (LIGHT_TILESET, j), props,
                    on_src if lit else None, "%s_%d" % (LIGHT_ON_TILESET, j) if lit else None))
    # 2-level grids: head copy (level 1) + its own pole copy (level 0)
    by_copy = {c: p for _s, c, p, _o, _oc in out}
    for k, (head, pole, style, face) in enumerate(POLE_HEADS):
        grid = [(b"CustomName", b"Light"), (b"GroupName", ("%s %s" % (style, _FACE_WORD[face])).encode()),
                (b"Facing", _FACE_FACING[face]), (b"SpriteGridPos", b"0,0")]
        hp = by_copy[light_sprite(OUT_SHEET, head)]
        hp[:] = [kv for kv in hp if kv[0] not in (b"CustomName", b"GroupName", b"Facing", b"SpriteGridPos")]
        hp += grid + [(b"SpriteGridLevel", b"1")]
        colour = [kv for kv in hp if kv[0] in (b"lightR", b"lightG", b"lightB")]
        pp = [(a, b) for a, b in tts[OUT_SHEET.encode()][6][pole] if a not in (b"streetlight",)]
        pp += [(b"lightswitch", b"")] + colour + [(b"LightRadius", b"1"), (b"IsMoveAble", b""),
                                                   (b"BlocksPlacement", b"")]
        pp += grid + [(b"SpriteGridLevel", b"0")]
        out.append(("%s_%d" % (OUT_SHEET, pole), "%s_%d" % (LIGHT_TILESET, POLE_BASE + k), pp, None, None))
    return out


def _one(s):
    return {"layers": [{"rows": [[s]]}]}


def _req(pipes=0, bulb="Base.LightBulb"):
    inputs = [SCREWDRIVER] + [dict(i) for i in BASIC]
    for i in inputs:
        if i["id"] == "light_bulb":
            i["items"] = [bulb]
    if pipes:
        inputs.append({"id": "metal_pipe", "role": "material", "mode": "consume", "items": ["Base.MetalPipe"],
                       "amount": pipes})
    return {"inputs": inputs, "skills": {"Electricity": 4}, "knowledge": copy.deepcopy(KNOWLEDGE)}


def _piece(slug, name, sub, faces, obj, req, placement, group=None, level=None, native=None, icon=None):
    b = {
        "id": PREFIX + slug,
        "allowSpriteReuse": True,
        "translationKey": "IGUI_WETiki_light_" + slug,
        "displayName": name,
        "tooltipKey": "Tooltip_KBW_Shared_TableLamp",
        "category": "Lighting",
        "subcategory": sub,
        "material": "Electronics",
        "materialTags": ["Electronics", "Metal"],
        "iconSprite": icon or faces[next(iter(faces))]["layers"][-1]["rows"][0][0],
        "placement": placement,
        "tags": ["tikitown", "drazion", "world-essentials", "lighting", "electrical"],
        "stages": [{"id": "built", "geometry": {"faces": faces}, "requirements": req,
                    "construction": copy.deepcopy(CONSTRUCTION), "object": dict(obj),
                    "nativeObject": native or {"type": "lightSwitch"}}],
    }
    if group:
        b["group"] = dict(group, level=level)
    return b


def _group(slug, name):
    return {"id": PREFIX + slug, "name": name, "translationKey": "IGUI_WETiki_light_%s_group" % slug}


def _check(ts):
    """The tiles are what the pieces assume."""
    ind = ts[IN.encode()][6]
    out = ts[OUT_SHEET.encode()][6]
    f = lambda t, i: {a.decode(): b.decode() for a, b in t[i]}
    for i, _c in FLOOR_LAMPS:
        assert f(ind, i).get("CustomName") == "Floor Lamp", i
    for c in range(8):
        for base, facing in ((16, "E"), (24, "S"), (32, "W"), (40, "N")):
            p = f(ind, base + c)
            assert p.get("CustomName") == "Table Lamp" and p.get("Facing") == facing and p.get("GroupName") == TABLE_COLOURS[c].replace("Plum", "Dark"), (base + c, p)
    for i, att in zip(range(48, 56), "WNESWNES"):
        assert "attached" + att in f(ind, i), i
    assert f(ind, 5).get("SpriteGridPos") == "0,0" and f(ind, 4).get("SpriteGridPos") == "0,1"
    assert f(ind, 6).get("SpriteGridPos") == "0,0" and f(ind, 7).get("SpriteGridPos") == "1,0"
    assert f(ind, 57).get("SpriteGridPos") == "0,0" and f(ind, 56).get("SpriteGridPos") == "0,1"
    assert f(ind, 58).get("SpriteGridPos") == "0,0" and f(ind, 59).get("SpriteGridPos") == "1,0"
    for i in (16, 17):            # the poles must not block anything
        p = f(out, i)
        assert not ({"solid", "solidtrans", "StopCar", "HitByCar", "BlocksPlacement"} & set(p)), (i, p)
    for i in (0, 8, 9, 10, 11, 18, 19):
        assert "lightswitch" in f(out, i), i
    assert "attachedN" in f(out, 6) and "attachedW" in f(out, 7)


def build():
    _v, ts, _o = k._parse(open(k._TIKITOWN_TILES, "rb").read())
    _check(ts)
    si = lambda i: "%s_%d" % (IN, i)
    so = lambda i: "%s_%d" % (OUT_SHEET, i)
    floor = {"kind": "object", "requiresFloor": True}
    wall = {"kind": "object", "needToBeAgainstWall": True, "requiresFloor": False}
    out = []
    # ---- indoor
    g = _group("floor_lamps", "TikiTown Floor Lamps")
    for lvl, (i, colour) in enumerate(FLOOR_LAMPS, 1):
        out.append(_piece("floor_%d" % i, "%s Floor Lamp" % colour, "Floor Lamps", {"W": _one(si(i))},
                          OBJ_FLOOR, _req(pipes=1), floor, g, lvl))
    g = _group("table_lamps", "TikiTown Table Lamps")
    for c, colour in enumerate(TABLE_COLOURS):
        faces = {"E": _one(si(16 + c)), "S": _one(si(24 + c)), "W": _one(si(32 + c)), "N": _one(si(40 + c))}
        out.append(_piece("table_%d" % c, "%s Table Lamp" % colour, "Table Lamps", faces, OBJ_FLOOR, _req(), floor,
                          g, c + 1, icon=si(24 + c)))
    g = _group("wall_lamps", "TikiTown Wall Lamps")
    for lvl, (base, colour) in enumerate(((48, "Gold"), (52, "Gold Beige")), 1):
        faces = {"W": _one(si(base)), "N": _one(si(base + 1)), "E": _one(si(base + 2)), "S": _one(si(base + 3))}
        out.append(_piece("wall_%d" % base, "%s Wall Lamp" % colour, "Wall Lights", faces, OBJ_WALL, _req(), wall, g, lvl))
    ci = lambda i: light_sprite(IN, i)        # our copies (see LIGHT_COPIES)
    co = lambda i: light_sprite(OUT_SHEET, i)
    out.append(_piece("fluorescent_long", "Fluorescent Wall Lamp (Long)", "Wall Lights",
                      {"W": {"layers": [{"rows": [[ci(57)], [ci(56)]]}]}, "N": {"layers": [{"rows": [[ci(58), ci(59)]]}]}},
                      OBJ_WALL, _req(), wall, g, 3))
    out.append(_piece("fluorescent_short", "Fluorescent Wall Lamp (Short)", "Wall Lights",
                      {"W": _one(si(61)), "N": _one(si(60))}, OBJ_WALL, _req(), wall, g, 4))
    out.append(_piece("exit_sign", "Exit Sign", "Exit Signs",
                      {"W": {"layers": [{"rows": [[ci(5)], [ci(4)]]}]}, "N": {"layers": [{"rows": [[ci(6), ci(7)]]}]}},
                      OBJ_WALL, _req(), wall))
    # ---- outdoor (our copies: no streetlight flag, BlocksPlacement so they cannot overlap)
    out.append(_piece("lamp_post", "Victorian Lamp Post", "Street Lights", {"W": _one(co(0))}, OBJ_POLE,
                      _req(pipes=2), floor))
    out.append(_piece("neon_open", "OPEN Neon Sign", "Wall Lights", {"W": _one(so(7)), "N": _one(so(6))},
                      OBJ_WALL, _req(), wall))

    def pole(slug, name, sub, pole_i, heads, group, lvl, bulb="Base.LightBulb"):
        # each head on its OWN pole copy (one 2-level sprite grid, see POLE_HEADS); the pole is a
        # light switch too, so no nativeObject.poleSprite
        for f, h in heads.items():
            assert (h, pole_i) in [(hh, pp) for hh, pp, _l, _f in POLE_HEADS], (h, pole_i)
        faces = {f: {"layers": [{"rows": [[pole_sprite(h)]]}, {"rows": [[co(h)]]}]} for f, h in heads.items()}
        return _piece(slug, name, sub, faces, OBJ_POLE, _req(pipes=2, bulb=bulb), floor, group, lvl,
                      native={"type": "lightSwitch"}, icon=co(next(iter(heads.values()))))
    g = _group("street_lights", "TikiTown Street Lights")
    out.append(pole("street_single", "Street Light", "Street Lights", 16, {"W": 8, "N": 9, "E": 10, "S": 11}, g, 1))
    out.append(pole("street_double", "Double Street Light", "Street Lights", 17, {"W": 18, "N": 19}, g, 2))
    g = _group("traffic_lights", "TikiTown Traffic Lights")
    out.append(pole("traffic_1", "Traffic Light 1", "Traffic Lights", 16, {"W": 12, "N": 13, "E": 14, "S": 15}, g, 1,
                    bulb="Base.LightBulbYellow"))
    out.append(pole("traffic_2", "Traffic Light 2", "Traffic Lights", 16, {"W": 22, "N": 23, "E": 20, "S": 21}, g, 2,
                    bulb="Base.LightBulbYellow"))
    return out


# TEST BUNDLE ONLY (user, in game 2026-11-14: toggling a street / traffic light switched every lamp
# nearby). World Essentials' Knox Expansion (WorldEssentialsKnoxConstructionSafety.lua) makes
# NativeObjectFactory.resolve return nil for a definition's nativeObject.poleSprite, so only the lit
# head becomes a light. The test bundle runs WITHOUT World Essentials, so plain KBW made the pole an
# IsoLightSwitch too. A KBW-built switch with no lightR on a square with no map room is a "detached
# room switch" to KBW's World/LightSwitches.lua, which toggles every wired lamp in the open area
# around it. This file applies the same pole guard in the test bundle. Not for WE (WE has its own).
TEST_POLE_GUARD_LUA_NAME = "KBWTest_PoleLightGuard.lua"
TEST_POLE_GUARD_LUA = r'''-- AUTO-GENERATED by pz_craft_loops/tikitown_lighting.py -- TEST BUNDLE ONLY, never shipped.
-- Same rule as World Essentials' Knox Expansion: the pole tile of a two-storey light
-- (nativeObject.poleSprite) is not a light switch; only the lit head is.
local ok, Factory = pcall(require, "KnoxBuildworks/BuildingObjects/NativeObjectFactory")
if not ok or type(Factory) ~= "table" or type(Factory.resolve) ~= "function" then
    print("[KBWTest_PoleLightGuard] NativeObjectFactory unavailable; guard not installed")
    return
end
if Factory._kbwTestPoleGuard then return end
Factory._kbwTestPoleGuard = true
local originalResolve = Factory.resolve
function Factory.resolve(config, sprite)
    if type(config) == "table" and config.poleSprite ~= nil and config.poleSprite == sprite then return nil end
    return originalResolve(config, sprite)
end
'''


def write_test_pole_guard_lua(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8", newline="\n").write(TEST_POLE_GUARD_LUA)
    return path


def main():
    out = build()
    ids = [b["id"] for b in out]
    assert len(ids) == len(set(ids))
    doc = {"schemaVersion": 1, "category": "Lighting",
           "source": ("TikiTown lighting_indoor_tterika_01 / lighting_outdoor_tterika_01 (Drazion's Tilepack): working "
                      "lamps on KBW VE's lamp setup, two-storey street and traffic lights on WE's pole-light setup. "
                      "Generated by pz_craft_loops/tikitown_lighting.py."),
           "buildables": out}
    json.dump(doc, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("wrote %s (%d buildables)" % (OUT, len(ids)))


if __name__ == "__main__":
    main()
