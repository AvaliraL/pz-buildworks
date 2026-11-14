# -*- coding: utf-8 -*-
"""Shared KBW Community Tilepack tile-property PATCH generator.

Reverse-engineered + round-trip-verified .tiles binary format (see _tiles_roundtrip.py):
    b'tdef' + int32le version(1) + int32le numTilesets
    per tileset:  name\\n  image\\n  int32le cols  int32le rows  int32le firstId  int32le numTiles
      per tile:   int32le numProps ; numProps * (key\\n value\\n)   (value '' for flag props)

We copy the needed Community Tilepack tilesets verbatim and, for specific sprite indices, ADD and/or
REMOVE tile-properties, then emit a multi-tileset *.patch.tiles. Registered in mod.info via
`tiledef=<TILEPATCH_NAME> <TILEPATCH_ID>` with a FREE id (not the pack's own id space) and loaded
AFTER the Community Tilepack so the patch merges onto the pack's sheets.

This is the single reusable mechanism for all sprite-property edits (TV device data, walk-through
collision removal, vegetation behavior, future viewscreen toggles, etc.).
"""
import struct, os

_COMMUNITY_TILES = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600\3628736763\mods\CommunityTilePack\common\media\dylanstiles.tiles"

# Free tiledef id (8185: below UsefulBarrels' confirmed-working 8188/8189, under the 8190
# negative-sprite-id ceiling, not in the community tiledef registry). Name carries ".patch".
TILEPATCH_NAME = "kbwcommunity_tvpatch.patch"
TILEPATCH_ID = 8185

# Patch groups: (tileset_name, {sprite indices}, [(addKey, addVal), ...], {removeKey, ...})
# ADD only inserts a key if absent; REMOVE strips the key entirely.
_PATCH_GROUPS = [
    # --- CRT TVs: functional device + walk-through wall mount ---
    # signal=tv routes the TV UI; TV flag drives the on-screen graphic overlay; CustomItem/Surface
    # mirror the vanilla TV tile. Remove solidtrans (the pack wrongly made these block the square);
    # they stay wall-mounted via MoveType=WallObject + IsHigh.
    ("DylansRandomFurniture02", {36, 37, 38, 39},
     [(b"signal", b"tv"), (b"IsoType", b"IsoTelevision"), (b"CustomItem", b"Base.TvWideScreen"),
      (b"TV", b""), (b"Surface", b"15")],
     # BlocksPlacement: KBW Placement.lua checks the SQUARE's merged properties, so a wall TV with
     # it made the floor below unbuildable (counter-then-TV worked, TV-then-counter didn't).
     {b"solidtrans", b"solid", b"BlocksPlacement"}),

    # --- TV screen overlay: IsoTelevision.setupDefaultScreens/isFacing choose the screen sprite by
    # the tile's Facing. Vanilla TV tiles all carry Facing; the pack's TVs had none. Matched by art
    # (pixel-measured): 36/38 have the screen on the left face sloping down-right, like vanilla
    # appliances_television_01_1 (Facing=S); 37/39 screen on the right face like _0 (Facing=E).
    ("DylansRandomFurniture02", {36, 38}, [(b"Facing", b"S")], set()),
    ("DylansRandomFurniture02", {37, 39}, [(b"Facing", b"E")], set()),

    # --- Dirkies RUS upper cabinets (edit_ddd_RUS_fixtures_counters_03, 8 colours x 8 tiles): the
    # art hangs at head height but the pack copied the LOWER counter's properties (Surface 34,
    # ContainerPosition Low, no IsHigh), so KBW treated them as floor counters and refused to put
    # them over one. KBW lets a piece share a square with a counter only if it is a high wall
    # object (MoveType=WallObject + IsHigh), as the sheet-35 upper cabinets are.
    ("edit_ddd_RUS_fixtures_counters_03", set(range(0, 64)),
     [(b"MoveType", b"WallObject"), (b"IsHigh", b"")],
     {b"Surface", b"ContainerPosition"}),

    # --- Dirkies green military case (furniture_storage_ddd_01_4): stackable like vanilla/KBW crates
    # (IsStackable + IsTable + Surface). Vanilla allows a crate while stack height + Surface <= 96.
    # Surface 16 => 6 high (5*16 + 16 = 96) and pixel-flush with the art (measured by stacking it
    # at 14..20); 17 would cap at 5 with a ~1px gap. User chose 6 high.
    # White case (_9) is the same sprite in another colour: same stacking.
    ("furniture_storage_ddd_01", {4, 9},
     [(b"IsStackable", b""), (b"IsTable", b""), (b"Surface", b"16")], set()),

    # --- Dirkies broken louvered fence (fencing_ddd_02 24-29): per user a LOW wall you vault over,
    # not a tall climb. Its properties are copied from the intact fence (TallHoppable), so swap to the
    # low-fence flags: HoppableN on N pieces, HoppableW on W pieces, both on the corner.
    ("fencing_ddd_02", {24, 25}, [(b"HoppableN", b"")], {b"TallHoppableN", b"TallHoppableW"}),
    ("fencing_ddd_02", {26, 27}, [(b"HoppableW", b"")], {b"TallHoppableN", b"TallHoppableW"}),
    ("fencing_ddd_02", {28}, [(b"HoppableN", b""), (b"HoppableW", b"")], {b"TallHoppableN", b"TallHoppableW"}),

    # --- Future Room viewscreens (west wall): the pack gave them no properties, so KBW used its
    # generic against-wall check, which rejects a square holding any other thumpable (a corner
    # square holds two built walls). As wall fixtures (MoveType=WallObject + Facing) KBW uses
    # hasAttachedWallSupport instead, which allows different faces of a corner. Facing=E means
    # attached to the west wall (KBW/vanilla convention).
    ("DylansFutureRoom01", {24, 25, 26, 27, 28, 29, 32, 33, 34},
     [(b"MoveType", b"WallObject"), (b"Facing", b"E")], set()),

    # --- TK kitchen_misc_tk_01: ice machine (8-11) and deep fryer (16-19) ship with only
    # `solidtrans`. Give them a name, facing (read from the art: front panel on the lower-left
    # face = S, lower-right = E, back visible = N / W) and the placement block vanilla
    # appliances carry.
    # Ice machine = vanilla chest freezer (appliances_refrigeration_01_48): `Freezer` +
    # FreezerCapacity/ContainerCapacity 30 (no `container=`; the game creates the freezer from
    # these when the object is placed as a prop, and it cools on grid/generator power).
    ("kitchen_misc_tk_01", {8, 9, 10, 11},
     [(b"CustomName", b"Ice Machine"), (b"GroupName", b"Commercial"), (b"BlocksPlacement", b"")], set()),
    # Deep fryer = vanilla electric oven (appliances_cooking_01_0): IsoType=IsoStove,
    # container=stove; cooks only with power, like the vanilla oven.
    ("kitchen_misc_tk_01", {16, 17, 18, 19},
     [(b"CustomName", b"Deep Fryer"), (b"GroupName", b"Commercial"), (b"BlocksPlacement", b"")], set()),
    ("kitchen_misc_tk_01", {8, 16}, [(b"Facing", b"S")], set()),
    ("kitchen_misc_tk_01", {9, 17}, [(b"Facing", b"E")], set()),
    ("kitchen_misc_tk_01", {10, 18}, [(b"Facing", b"N")], set()),
    ("kitchen_misc_tk_01", {11, 19}, [(b"Facing", b"W")], set()),

    # --- Fears RP raccoon figure (61-63): pack props look copied from a tree (MoveWithWind,
    # HitByCar, StopCar, forceFade). Keep collision/fade, drop MoveWithWind so it doesn't sway.
    ("fears_rp_tiles", {61, 62, 63},
     [(b"CustomName", b"Figure"), (b"GroupName", b"Raccoon")],
     {b"MoveWithWind"}),

    # --- Exercise ball (5,6,7) + Punching bag (12,13): meant to be walk-through centre-of-tile
    # decor. The pack authored them solidtrans (full-tile block). Remove it so you can walk through.
    ("DylansRandomFurniture02", {5, 6, 7, 12, 13},
     [],
     {b"solidtrans", b"solid"}),

    # --- Obs_04 hedges (24-29): meant to block line-of-sight but be walk-through and slow you.
    # The pack authored them plain `solid` (hard wall). Replace with vanilla bush behavior:
    # remove solid, add Bush + Movement=HedgeHigh (blocks LOS, passable, slows) + vegitation flags.
    ("Obs_04", {24, 25, 26, 27, 28, 29},
     [(b"Bush", b""), (b"Movement", b"HedgeHigh"), (b"vegitation", b""),
      (b"canBeRemoved", b""), (b"MoveWithWind", b"")],
     {b"solid", b"solidtrans"}),
]


def _parse(data):
    class R:
        def __init__(s, b): s.b = b; s.p = 0
        def raw(s, n): v = s.b[s.p:s.p + n]; s.p += n; return v
        def i32(s): v = struct.unpack_from("<i", s.b, s.p)[0]; s.p += 4; return v
        def line(s):
            e = s.b.index(b"\n", s.p); v = s.b[s.p:e]; s.p = e + 1; return v
    r = R(data)
    assert r.raw(4) == b"tdef", "bad magic"
    ver = r.i32(); num = r.i32()
    tilesets = {}
    order = []
    for _ in range(num):
        name = r.line(); img = r.line()
        cols = r.i32(); rows = r.i32(); firstId = r.i32(); ntiles = r.i32()
        tiles = []
        for _t in range(ntiles):
            np = r.i32(); tiles.append([(r.line(), r.line()) for _p in range(np)])
        tilesets[name] = [name, img, cols, rows, firstId, ntiles, tiles]
        order.append(name)
    return ver, tilesets, order


def _ser_tileset(ts):
    name, img, cols, rows, firstId, ntiles, tiles = ts
    out = bytearray()
    out += name + b"\n" + img + b"\n" + struct.pack("<iiii", cols, rows, firstId, ntiles)
    for props in tiles:
        out += struct.pack("<i", len(props))
        for k, v in props:
            out += k + b"\n" + v + b"\n"
    return bytes(out)


def _load_community_tilesets():
    """All Community pack tilesets by name. dylanstiles first (its tilesets keep the firstIds the
    patch has always shipped with); other files' tilesets are added only if the name is new."""
    import glob
    ver, tilesets, _order = _parse(open(_COMMUNITY_TILES, "rb").read())
    for p in sorted(glob.glob(os.path.join(os.path.dirname(_COMMUNITY_TILES), "*.tiles"))):
        if os.path.normcase(p) == os.path.normcase(_COMMUNITY_TILES):
            continue
        _v, ts, _o = _parse(open(p, "rb").read())
        for n, t in ts.items():
            tilesets.setdefault(n, t)
    return ver, tilesets


# PZ build 26486631 (2026-11-09) moved the vanilla tile definitions into media/tile_definitions/.
_VANILLA_TILES = next((p for p in (
    r"C:\Program Files (x86)\Steam\steamapps\common\ProjectZomboid\media\tile_definitions\newtiledefinitions.tiles",
    r"C:\Program Files (x86)\Steam\steamapps\common\ProjectZomboid\media\newtiledefinitions.tiles")
    if os.path.isfile(p)), None) or \
    r"C:\Program Files (x86)\Steam\steamapps\common\ProjectZomboid\media\tile_definitions\newtiledefinitions.tiles"

# ---- TikiTown (Drazion's tilepack) patches: opt-in via tikitown=True (the patch then also copies
# TikiTown tilesets and must load after tikitown_tiles). Same group / override formats as above.
_TIKITOWN_TILES = (r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600\3046728955\mods"
                   r"\Drazions Tile Pack\common\media\tikitown_tiles.tiles")
_TT_PATCH_GROUPS = [
    # tterika_02 footlocker (4-7): stackable 6 high (user). Surface stays the tile's 15
    # (5*15 + 15 = 90 <= 96, a 7th would be 105). IsTableTop removed: vanilla never stacks onto a
    # square that has IsTableTop.
    ("furniture_storage_tterika_02", {4, 5, 6, 7},
     [(b"IsStackable", b""), (b"IsTable", b"")], {b"IsTableTop"}),
    # tterika_02 small cabinet / small military lockers (0-3, 12-15, 20-23): stack 2 high (user).
    # Their Surface is already 48: 48 + 48 = 96 allows a 2nd, a 3rd would be 144.
    ("furniture_storage_tterika_02", set(range(0, 4)) | set(range(12, 16)) | set(range(20, 24)),
     [(b"IsStackable", b""), (b"IsTable", b"")], set()),
    # tikitown-props-14 soundproofing: NO LONGER PATCHED (2026-08-28). The IsMoveAble removal, Facing
    # and door-trim overrides changed map-placed soundproofing too; they now live on our own copies
    # (tikitown_soundproof.copy_props, KBWTikiTownWallOverlays_1200..1206).
]
# tterika_02 freestanding lockers: idx 12-15, 20-47 are MoveType=WallObject in the pack and 24-47
# carry Facing E,S,W,N against the S,E,N,W art. {sprite: {key: value}} (also used by rotation_fix).
TT_LOCKER_OVERRIDES = {
    "furniture_storage_tterika_02_%d" % i: {"MoveType": "Object", "Facing": ("S", "E", "N", "W")[i % 4]}
    for i in list(range(12, 16)) + list(range(20, 48))
}


# tikitown-props-14 recording-studio soundproofing (WallOverlay panels). The pack's Facing values
# contradict the tiles' own attach flags (8: attachedW + Facing S, 9: attachedN + Facing E, 18/19
# the same) and 10/11/17 have none. KBW's against-wall check reads Facing, not the attach flags
# (same bug as the TK kitchen wall shelf), so the 2026-10 attempt never found its wall. Facing is
# set from the attach flag: attachedW -> E, attachedN -> S, attachedE -> W, attachedS -> N.
# The door-frame panels must be door TRIM for World Essentials to hang them on a door frame:
# WE's FindOverlaySupport only accepts a DoorWall edge for sprites of type doorFrW / doorFrN.
# These fixes are now baked into our copied tiles (tikitown_soundproof.copy_props), not patched
# onto the pack tiles, so this stays empty.
TT_SOUNDPROOF_OVERRIDES = {}
# everything the TikiTown patch overrides (also drives rotation_fix's moveable offsets)
TT_PROP_OVERRIDES = dict(TT_LOCKER_OVERRIDES, **TT_SOUNDPROOF_OVERRIDES)


def _tt_override_list():
    om = {}
    for spr, kv in TT_PROP_OVERRIDES.items():
        sh, _, i = spr.rpartition("_")
        om.setdefault(sh, {})[int(i)] = [(k.encode(), v.encode()) for k, v in kv.items()]
    return list(om.items())

# Value OVERRIDES: replace an existing property's value (the patch merge overrides values; it
# only can't remove keys). (tileset, {index: [(key, value), ...]})
_PATCH_OVERRIDES = [
    # TK metal kitchen wall shelf: the pack's attachedW/N/E/S FLAGS match the art, but its Facing
    # values are swapped (4/5 and 6/7). KBW's wall check reads attachment via
    # PropertyContainer.has("attachedW"), which only sees key/value properties, not sprite flags
    # (bytecode-checked), so it falls back to Facing and looked for the wrong wall; only corner
    # squares (both walls) passed. Set Facing to match each tile's attached wall
    # (attachedW -> E, attachedN -> S, attachedE -> W, attachedS -> N).
    ("kitchen_misc_tk_01", {4: [(b"Facing", b"E")], 5: [(b"Facing", b"S")],
                            6: [(b"Facing", b"W")], 7: [(b"Facing", b"N")]}),
]

# Functional properties copied from a vanilla tile onto pack tiles, so the object behaves exactly
# like the vanilla appliance (containers, power use, sounds, scrap/pick-up). Identity and layout
# keys stay the pack's own (name, facing, group, surface/height, grid, collision).
# (target tileset, {indices}, vanilla tileset, vanilla index)
_VANILLA_COPIES = [
    ("kitchen_misc_tk_01", {8, 9, 10, 11}, "appliances_refrigeration_01", 48),    # chest freezer
    ("kitchen_misc_tk_01", {16, 17, 18, 19}, "appliances_cooking_01", 0),         # electric oven
]
_VANILLA_COPY_SKIP = {b"CustomName", b"GroupName", b"Facing", b"Surface", b"IsLow", b"IsHigh",
                      b"SpriteGridPos", b"solid", b"solidtrans", b"BlocksPlacement"}


# Property copies WITHIN the Community pack: some art tiles ship with no properties at all (the
# artist set up one fence row and left its look-alikes blank). Copy the configured twin's
# properties (add-only) so the blank tiles become real walls.
# (target tileset, first target index, source tileset, first source index, count)
_SHEET_COPIES = [
    # Dirkies fencing_ddd_01 two-storey louvered fence (base 72-77, angled-cap top 80-85,
    # flat-cap top 88-93) <- the identical, configured louvered fence in fencing_ddd_02.
    ("fencing_ddd_01", 72, "fencing_ddd_02", 0, 6),
    ("fencing_ddd_01", 80, "fencing_ddd_02", 8, 6),
    ("fencing_ddd_01", 88, "fencing_ddd_02", 16, 6),
    # fencing_ddd_02 broken louvered fence (24-29) and double-post louvered fence (32-35, tops
    # 40-43 / 48-51) <- the configured louvered fence rows of the same sheet.
    ("fencing_ddd_02", 24, "fencing_ddd_02", 0, 6),
    ("fencing_ddd_02", 32, "fencing_ddd_02", 0, 4),
    ("fencing_ddd_02", 40, "fencing_ddd_02", 8, 4),
    ("fencing_ddd_02", 48, "fencing_ddd_02", 16, 4),
]


def _sheet_copy_groups():
    """Turn _SHEET_COPIES into ordinary patch groups (add-only), one group per target tile."""
    _ver, ts = _load_community_tilesets()
    # keys a _PATCH_GROUPS entry removes from a tile must not be copied back onto it
    removed = {}
    for tsname, idxs, _add, remove in _PATCH_GROUPS:
        for i in idxs:
            removed.setdefault((tsname, i), set()).update(remove)
    groups = []
    for tgt, t0, src, s0, n in _SHEET_COPIES:
        props = ts[src.encode()][6]
        for i in range(n):
            skip = removed.get((tgt, t0 + i), set())
            groups.append((tgt, {t0 + i}, [(a, b) for a, b in props[s0 + i] if a not in skip], set()))
    return groups


def _vanilla_copy_groups():
    """Turn _VANILLA_COPIES into ordinary patch groups (add-only)."""
    _v, van, _o = _parse(open(_VANILLA_TILES, "rb").read())
    groups = []
    for tsname, idxs, vsheet, vidx in _VANILLA_COPIES:
        props = [(k, v) for k, v in van[vsheet.encode()][6][vidx] if k not in _VANILLA_COPY_SKIP]
        groups.append((tsname, idxs, props, set()))
    return groups


# The TikiTown submod's OWN tile patch (tikitown_only=True): only the tterika_02 stacking + locker
# fixes, no Community sheets, so it never double-patches what the Community submod already does.
# Needs its own tiledef line in the TikiTown submod's mod.info (WE-owned; handed over in the notes).
TT_TILEPATCH_NAME = "kbwtikitown_tterika.patch"
TT_TILEPATCH_ID = 8180      # free (8180-8187 checked across installed mods; 8181-8187 are ours)


def write_community_tilepatch(dest_path, tikitown=False, tikitown_only=False):
    """Emit the multi-tileset .patch.tiles with all _PATCH_GROUPS applied. Returns a report dict.
    tikitown=True also patches TikiTown sheets (_TT_PATCH_GROUPS / TT_LOCKER_OVERRIDES); only for
    builds that load after tikitown_tiles. tikitown_only=True emits ONLY the TikiTown patches (for
    the TikiTown submod's own patch file)."""
    if tikitown_only:
        ver = 1
        _v, tilesets, _o = _parse(open(_TIKITOWN_TILES, "rb").read())
        overrides = _tt_override_list()
        groups_in = list(_TT_PATCH_GROUPS)
        tikitown = True
    else:
        ver, tilesets = _load_community_tilesets()
        overrides = list(_PATCH_OVERRIDES)
        groups_in = _PATCH_GROUPS + _vanilla_copy_groups() + _sheet_copy_groups()
        if tikitown:
            _v, tts, _o = _parse(open(_TIKITOWN_TILES, "rb").read())
            for n, t in tts.items():
                tilesets.setdefault(n, t)
            groups_in = groups_in + _TT_PATCH_GROUPS
            overrides += _tt_override_list()

    # group patches by tileset so each patched sheet is emitted once
    by_sheet = {}
    for tsname, idxs, add, remove in groups_in:
        by_sheet.setdefault(tsname, []).append((idxs, add, remove))
    if tikitown:                            # TikiTown override-only sheets still need emitting
        for otsname, _om in _tt_override_list():
            by_sheet.setdefault(otsname, [])

    report = {}
    emit = []
    for tsname, groups in by_sheet.items():
        key = tsname.encode() if isinstance(tsname, str) else tsname
        if key not in tilesets:
            raise RuntimeError("tileset %r not found in community .tiles" % tsname)
        ts = tilesets[key]
        name, img, cols, rows, firstId, ntiles, tiles = ts
        touched = []
        for idxs, add, remove in groups:
            for idx in idxs:
                if idx >= ntiles:
                    continue
                if remove:
                    tiles[idx] = [(k, v) for (k, v) in tiles[idx] if k not in remove]
                have = {k for k, _ in tiles[idx]}
                for k, v in add:
                    if k not in have:
                        tiles[idx].append((k, v))
                touched.append(idx)
        for otsname, omap in overrides:
            if otsname != tsname:
                continue
            for idx, kvs in omap.items():
                for k, v in kvs:
                    tiles[idx] = [(kk, v if kk == k else vv) for kk, vv in tiles[idx]]
                    if not any(kk == k for kk, _ in tiles[idx]):
                        tiles[idx].append((k, v))
                touched.append(idx)
        report[tsname] = sorted(set(touched))
        emit.append(ts)

    # Tilesets from different source files can share a firstId; keep them unique inside our patch
    # file (the merge onto the pack's sheets is by NAME, firstId only spans our own patch file).
    used = set()
    for ts in emit:
        if ts[4] in used:
            ts[4] = max(used | {ts[4]}) + 1
        used.add(ts[4])

    out = bytearray(b"tdef")
    out += struct.pack("<ii", 1, len(emit))
    for ts in emit:
        out += _ser_tileset(ts)
    blob = bytes(out)
    # self-verify it re-parses
    _parse(blob)
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    open(dest_path, "wb").write(blob)
    report["_bytes"] = len(blob)
    report["_tilesets"] = [ts[0].decode() for ts in emit]
    return report


# ---------------------------------------------------------------------------------------------
# PROPERTY REMOVAL (runtime Lua)
# A .patch.tiles MERGES onto the pack's tiles: it can add/override properties but CANNOT remove
# them (confirmed in-game 2026-10-28: TVs/ball/bag/hedges stayed solid although the patch file had
# solid/solidtrans stripped). The engine itself removes properties at runtime via
# PropertyContainer.unset(...) (IsoWorld fixes up tree tiles this way). Exact B42 method names, read
# from zombie/core/properties/PropertyContainer.class:
#     set(String) / set(String,String) / unset(String) / unset(IsoFlagType) / has(...) / get(String)
#     CreateKeySet()
# (The earlier failed Lua attempt used the B41 names Set/UnSet/Is/Val, which do not exist in B42.)
# So removals are applied by a small generated Lua script, driven by the same _PATCH_GROUPS table.

_REMOVAL_LUA_TEMPLATE = r'''-- AUTO-GENERATED by pz_craft_loops/kbw_tilepatch.py -- do not edit by hand.
-- Removes tile properties that a .patch.tiles merge cannot remove (merges are additive).
-- Uses the B42 PropertyContainer API: has/unset (lowercase). Every call is pcall-guarded and
-- logged, so a failure can never break loading.
local REMOVALS = {
%(rows)s
}

local function applyRemovals(source)
    local removed, missing, failed = 0, 0, 0
    for _, g in ipairs(REMOVALS) do
        local spr = getSprite(g[1])
        if not spr then
            missing = missing + 1
        else
            local props = spr:getProperties()
            for _, key in ipairs(g[2]) do
                local ok, err = pcall(function()
                    local flag = IsoFlagType[key]
                    if flag ~= nil and props:has(flag) then
                        props:unset(flag)
                        removed = removed + 1
                    end
                    if props:has(key) then
                        props:unset(key)
                    end
                end)
                if not ok then
                    failed = failed + 1
                    print("[KBWCommunityTileFixes] unset failed " .. g[1] .. " " .. key .. ": " .. tostring(err))
                end
            end
            pcall(function() props:CreateKeySet() end)
        end
    end
    print(string.format("[KBWCommunityTileFixes] %%s: removed=%%d missingSprites=%%d failed=%%d",
        tostring(source), removed, missing, failed))
end

if Events.OnLoadedTileDefinitions then
    Events.OnLoadedTileDefinitions.Add(function() applyRemovals("OnLoadedTileDefinitions") end)
end
if Events.OnGameStart then
    Events.OnGameStart.Add(function() applyRemovals("OnGameStart") end)
end
if Events.OnServerStarted then
    Events.OnServerStarted.Add(function() applyRemovals("OnServerStarted") end)
end
'''


# ---------------------------------------------------------------------------------------------
# TV SCREEN OVERLAYS (runtime Lua)
# IsoTelevision.setupDefaultScreens fills its screen list from the TV's own sheet at sprite index
# +16, +32, +48 (bytecode-verified), only when the list is empty. The Community pack has no screen
# art there, so our TVs get none. updateTvScreen/setScreen then pick from that 3-entry list for
# TESTSCREEN (on, no signal) / ALTERNATESCREEN (broadcast or media playing) / OFFSCREEN, so if we
# supply vanilla's three screens in vanilla's order, shows and tapes are handled by vanilla.
# Vanilla appliances_television_01: tile 0 Facing=E, tile 1 Facing=S; screens at +16/+32/+48.
#
# The vanilla screen art sits at floor/table height (y~131-185 in the 128x256 tile); the pack's
# wall TVs have their screens ~70px higher and a different size, so vanilla sprites can't be used
# as-is. We generate our own screen tiles: each vanilla screen (incl. its glow) is affine-warped
# onto the measured screen parallelogram of each pack TV, then shipped as a small texture pack +
# tiledef (tileset KBWCommunityTVScreens). Quads are (top-left, top-right, bottom-left) in tile
# pixels, measured from the extracted art (_tv_ascii.py).
SCREEN_TILESET = "KBWCommunityTVScreens"
SCREEN_TILEDEF_NAME = "kbwcommunity_tvscreens"
SCREEN_TILEDEF_ID = 8186          # free (8180-8187 checked across installed mods; 8188/8189 = UsefulBarrels)
_VANILLA_TILES2X = r"C:\Program Files (x86)\Steam\steamapps\common\ProjectZomboid\media\texturepacks\Tiles2x.pack"
_SCREEN_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_cache_tvscreens")

# vanilla screen series: facing -> ([tile indices for the 3 screens], source quad of the opaque core)
_VANILLA_SCREENS = {
    "S": ([17, 33, 49], ((36, 133), (80, 155), (36, 165))),
    "E": ([16, 32, 48], ((48, 153), (92, 131), (48, 184))),
}
# pack TV -> (facing, target quad)
_PACK_TVS = [
    ("DylansRandomFurniture02_36", "S", ((34, 65), (69, 82.5), (34, 96))),     # CRT, left face
    ("DylansRandomFurniture02_37", "E", ((51, 82), (88, 64.5), (51, 114))),    # CRT, right face
    ("DylansRandomFurniture02_38", "S", ((34, 52), (78, 73.5), (34, 85))),     # flat panel, inside bezel
    ("DylansRandomFurniture02_39", "E", ((47, 76), (91, 54), (47, 109))),      # flat panel, inside bezel
]

# TV sprite -> its 3 generated screen sprites, in vanilla order.
TV_SCREEN_MAP = {
    tv: ["%s_%d" % (SCREEN_TILESET, t * 3 + k) for k in range(3)]
    for t, (tv, _f, _q) in enumerate(_PACK_TVS)
}


def _extract_vanilla_screens():
    """Pull the needed appliances_television_01 screen textures out of Tiles2x.pack (cached)."""
    import io
    from PIL import Image
    want = {"appliances_television_01_%d" % i for f in _VANILLA_SCREENS.values() for i in f[0]}
    os.makedirs(_SCREEN_CACHE, exist_ok=True)
    if all(os.path.exists(os.path.join(_SCREEN_CACHE, n + ".png")) for n in want):
        return
    with open(_VANILLA_TILES2X, "rb") as f:
        def i32():
            return struct.unpack("<i", f.read(4))[0]

        def s():
            return f.read(i32()).decode("utf-8", "replace")
        assert f.read(4) == b"PZPK" and i32() == 1
        for _ in range(i32()):
            s(); nent = i32(); i32()
            ents = [(s(), struct.unpack("<8i", f.read(32))) for _ in range(nent)]
            png = f.read(i32())
            hits = [e for e in ents if e[0] in want]
            if not hits:
                continue
            page = Image.open(io.BytesIO(png)).convert("RGBA")
            for name, (x, y, w, h, ox, oy, tw, th) in hits:
                tile = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
                tile.paste(page.crop((x, y, x + w, y + h)), (ox, oy))
                tile.save(os.path.join(_SCREEN_CACHE, name + ".png"))
    missing = [n for n in want if not os.path.exists(os.path.join(_SCREEN_CACHE, n + ".png"))]
    if missing:
        raise RuntimeError("vanilla screen textures not found: %s" % missing)


def _affine_inverse(src, dst):
    """Coefficients (a,b,c,d,e,f) mapping OUTPUT (dst) pixel -> INPUT (src) pixel, for PIL AFFINE."""
    (sx0, sy0), (sx1, sy1), (sx2, sy2) = src
    (dx0, dy0), (dx1, dy1), (dx2, dy2) = dst
    # solve [dx dy 1] * M = [sx sy] using the three point pairs (Cramer's rule)
    det = dx0 * (dy1 - dy2) - dy0 * (dx1 - dx2) + (dx1 * dy2 - dx2 * dy1)

    def solve(v0, v1, v2):
        a = (v0 * (dy1 - dy2) - dy0 * (v1 - v2) + (v1 * dy2 - v2 * dy1)) / det
        b = (dx0 * (v1 - v2) - v0 * (dx1 - dx2) + (dx1 * v2 - dx2 * v1)) / det
        c = (dx0 * (dy1 * v2 - dy2 * v1) - dy0 * (dx1 * v2 - dx2 * v1) + v0 * (dx1 * dy2 - dx2 * dy1)) / det
        return a, b, c
    a, b, c = solve(sx0, sx1, sx2)
    d, e, f = solve(sy0, sy1, sy2)
    return (a, b, c, d, e, f)


def _write_pack(dest_path, page_name, tiles):
    """Write a single-page PZPK v1 texture pack. tiles: [(name, 128x256 RGBA Image)]."""
    import io
    from PIL import Image
    placed, x, y, rowh, W = [], 0, 0, 0, 1024
    crops = []
    for name, im in tiles:
        bbox = im.getbbox() or (0, 0, 1, 1)
        crops.append((name, im.crop(bbox), bbox, im.size))
    for name, c, bbox, full in crops:
        if x + c.width > W:
            x, y, rowh = 0, y + rowh + 1, 0
        placed.append((name, c, x, y, bbox, full))
        x += c.width + 1
        rowh = max(rowh, c.height)
    H = 1
    while H < y + rowh:
        H *= 2
    page = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for name, c, px, py, bbox, full in placed:
        page.paste(c, (px, py))
    buf = io.BytesIO()
    page.save(buf, "PNG")
    png = buf.getvalue()

    def s(v):
        b = v.encode("utf-8")
        return struct.pack("<i", len(b)) + b
    out = bytearray(b"PZPK") + struct.pack("<ii", 1, 1)
    out += s(page_name) + struct.pack("<ii", len(placed), 1)
    for name, c, px, py, bbox, full in placed:
        out += s(name) + struct.pack("<8i", px, py, c.width, c.height, bbox[0], bbox[1], full[0], full[1])
    out += struct.pack("<i", len(png)) + png
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    open(dest_path, "wb").write(bytes(out))
    return len(placed)


def write_tv_screen_assets(media_dir, preview_path=None):
    """Generate the wall-TV screen tiles: texture pack + tiledef in <media_dir>.
    Returns (pack basename, tiledef name, tiledef id) for mod.info."""
    from PIL import Image
    _extract_vanilla_screens()
    tiles = []
    for t, (tv, facing, dst) in enumerate(_PACK_TVS):
        idxs, src = _VANILLA_SCREENS[facing]
        coeffs = _affine_inverse(src, dst)
        for k, vi in enumerate(idxs):
            srcim = Image.open(os.path.join(_SCREEN_CACHE, "appliances_television_01_%d.png" % vi)).convert("RGBA")
            out = srcim.transform((128, 256), Image.AFFINE, coeffs, resample=Image.BILINEAR)
            tiles.append(("%s_%d" % (SCREEN_TILESET, t * 3 + k), out))
    n = _write_pack(os.path.join(media_dir, "texturepacks", SCREEN_TILESET + ".pack"), SCREEN_TILESET + "0", tiles)

    cols, rows = 8, (len(tiles) + 7) // 8
    ts = [SCREEN_TILESET.encode(), (SCREEN_TILESET + ".png").encode(), cols, rows, 1, cols * rows,
          [[] for _ in range(cols * rows)]]
    blob = b"tdef" + struct.pack("<ii", 1, 1) + _ser_tileset(ts)
    _parse(blob)
    open(os.path.join(media_dir, SCREEN_TILEDEF_NAME + ".tiles"), "wb").write(blob)

    if preview_path:
        # TV art with its generated screens composited on top, for eyeballing the fit
        tvdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_tvart")
        sheet = Image.new("RGBA", (128 * len(_PACK_TVS), 160), (60, 60, 60, 255))
        for t, (tv, _f, _q) in enumerate(_PACK_TVS):
            p = os.path.join(tvdir, tv + ".png")
            if os.path.exists(p):
                base = Image.open(p).convert("RGBA")
                base.alpha_composite(tiles[t * 3][1])
                sheet.alpha_composite(base.crop((0, 0, 128, 160)), (t * 128, 0))
        sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).save(preview_path)
    return SCREEN_TILESET, SCREEN_TILEDEF_NAME, SCREEN_TILEDEF_ID, n

# Shared LoadGridsquare dispatcher, emitted identically into every runtime file that needs square
# loads (TV screens, table-top height). Whichever file loads first creates it and registers ONE
# event handler; each file registers its sprite names + per-object fix. Per loaded square this is a
# single pass over the objects with one sprite-name table lookup each; only our sprites do any work.
# The handler is a published, named function so other mods (World Essentials' LoadGridsquare gate)
# can Remove it and call it from their own gate. Must not contain bare percent signs (the templates
# it goes into use Python %-formatting).
_LOADGRID_LUA = r'''-- Shared LoadGridsquare dispatcher for KBWCommunity runtime fixes (one handler for all files).
-- To gate it from another mod:  Events.LoadGridsquare.Remove(KBWCommunityLoadGrid.onSquare)
-- then call KBWCommunityLoadGrid.onSquare(square) from the gate. KBWCommunityLoadGrid.bySprite
-- lists the sprite names that need it (everything else is a no-op).
if not KBWCommunityLoadGrid then
    local G = { bySprite = {} }
    function G.register(names, fn)
        for name in pairs(names) do
            local list = G.bySprite[name]
            if not list then list = {}; G.bySprite[name] = list end
            list[#list + 1] = fn
        end
    end
    function G.onSquare(sq)
        if not sq then return end
        local objs = sq:getObjects()
        local n = objs and objs:size() or 0
        if n == 0 then return end
        local bySprite = G.bySprite
        for i = 0, n - 1 do
            local o = objs:get(i)
            local spr = o and o:getSprite()
            local name = spr and spr:getName()
            local list = name and bySprite[name]
            if list then
                for k = 1, #list do
                    local ok, err = pcall(list[k], o, "LoadGridsquare")
                    if not ok then print("[KBWCommunityLoadGrid] " .. tostring(name) .. ": " .. tostring(err)) end
                end
            end
        end
    end
    KBWCommunityLoadGrid = G
    if Events.LoadGridsquare then Events.LoadGridsquare.Add(G.onSquare) end
end
'''

_TV_SCREEN_LUA_TEMPLATE = r'''-- AUTO-GENERATED by pz_craft_loops/kbw_tilepatch.py -- do not edit by hand.
-- Gives Community Tilepack TVs vanilla's screen overlay sprites (the pack has no screen art).
-- Screen choice (test card / broadcast or tape / off) stays with vanilla IsoTelevision logic.
local SCREENS = {
%(rows)s
}

local warned = {}
local seen = setmetatable({}, { __mode = "k" })   -- objects already handled (weak keys)
local function applyScreens(obj, source)
    if not obj or not instanceof(obj, "IsoTelevision") then return end
    seen[obj] = true
    local spr = obj:getSprite()
    local name = spr and spr:getName() or nil
    local list = name and SCREENS[name] or nil
    if not list then return end
    local ok, err = pcall(function()
        obj:clearTvScreenSprites()
        local added = 0
        for _, sn in ipairs(list) do
            local s = getSprite(sn)
            if s then
                obj:addTvScreenSprite(s)
                added = added + 1
            elseif not warned[sn] then
                warned[sn] = true
                print("[KBWCommunityTVScreens] missing screen sprite " .. sn)
            end
        end
        print(string.format("[KBWCommunityTVScreens] %%s: %%s got %%d screens", tostring(source), name, added))
    end)
    -- Wall TVs must be walk-through. KBW's build path calls setMovedThumpable(true), and
    -- IsoGridSquare.getSpecialSolid() treats any movedThumpable object as solid, regardless of
    -- tile flags. Clear it and recalc the square so collision is rebuilt.
    local okT, errT = pcall(function()
        if obj.isMovedThumpable and obj:isMovedThumpable() then
            obj:setMovedThumpable(false)
            local sq = obj:getSquare()
            if sq then
                sq:RecalcAllWithNeighbours(true)
            end
            print("[KBWCommunityTVScreens] cleared movedThumpable on " .. tostring(name))
        end
    end)
    if not okT then
        print("[KBWCommunityTVScreens] movedThumpable clear failed on " .. tostring(name) .. ": " .. tostring(errT))
    end
    if not ok then
        print("[KBWCommunityTVScreens] failed on " .. tostring(name) .. ": " .. tostring(err))
    end
end

local function scanSquare(sq, source)
    if not sq then return end
    local objs = sq:getObjects()
    for i = 0, objs:size() - 1 do
        applyScreens(objs:get(i), source)
    end
end

-- Existing TVs as their squares load: through the shared dispatcher (only our 4 TV sprites).
%(loadgrid)s
KBWCommunityLoadGrid.register(SCREENS, applyScreens)
-- Newly built TVs (B42 event; argument shape guarded).
if Events.OnTileObjectAdded then
    Events.OnTileObjectAdded.Add(function(a, b)
        if a and instanceof(a, "IsoObject") then applyScreens(a, "OnTileObjectAdded")
        elseif a and instanceof(a, "IsoGridSquare") then scanSquare(a, "OnTileObjectAdded") end
        if b and instanceof(b, "IsoObject") then applyScreens(b, "OnTileObjectAdded") end
    end)
end
if Events.OnObjectAdded then
    Events.OnObjectAdded.Add(function(obj) applyScreens(obj, "OnObjectAdded") end)
end

-- Newly BUILT TVs: none of the events above fire for KBW builds (confirmed in console: only
-- LoadGridsquare ever logged). KBW builds TVs through NativeObjectFactory.create (which calls
-- setMovedThumpable(true)) and then calls NativeObjectFactory.finalize via the module table, so
-- wrapping finalize at runtime catches every new TV right after it enters the square. We do not
-- edit KBW's files; this only wraps the function in memory.
local function hookKBWFinalize(source)
    local okR, NOF = pcall(require, "KnoxBuildworks/BuildingObjects/NativeObjectFactory")
    if not okR or type(NOF) ~= "table" or type(NOF.finalize) ~= "function" then return end
    if NOF.__kbwCommunityTVHooked then return end
    local orig = NOF.finalize
    NOF.finalize = function(object, state, square)
        orig(object, state, square)
        if state and state.type == "television" then
            applyScreens(object, "KBWFinalize")
        end
    end
    NOF.__kbwCommunityTVHooked = true
    print("[KBWCommunityTVScreens] hooked KBW NativeObjectFactory.finalize (" .. tostring(source) .. ")")
end
if Events.OnGameStart then Events.OnGameStart.Add(function() hookKBWFinalize("OnGameStart") end) end
if Events.OnServerStarted then Events.OnServerStarted.Add(function() hookKBWFinalize("OnServerStarted") end) end

-- Multiplayer clients never run the server-side finalize, and a TV another player builds arrives
-- without a LoadGridsquare. A scan around each local player every in-game minute covers that
-- case. It runs ONLY on multiplayer clients (single player and servers are covered by the
-- finalize hook + LoadGridsquare). Each TV is handled once (weak-keyed so unloaded objects are
-- released).
local function scanNearPlayers()
    local cell = getCell()
    if not cell then return end
    for p = 0, getNumActivePlayers() - 1 do
        local pl = getSpecificPlayer(p)
        if pl then
            local px, py, pz = math.floor(pl:getX()), math.floor(pl:getY()), math.floor(pl:getZ())
            for z = pz - 1, pz + 1 do
                for x = px - 12, px + 12 do
                    for y = py - 12, py + 12 do
                        local sq = cell:getGridSquare(x, y, z)
                        if sq then
                            local objs = sq:getObjects()
                            for i = 0, objs:size() - 1 do
                                local o = objs:get(i)
                                if not seen[o] and instanceof(o, "IsoTelevision") then
                                    applyScreens(o, "NearbyScan")
                                end
                            end
                        end
                    end
                end
            end
        end
    end
end
if Events.EveryOneMinute then
    Events.EveryOneMinute.Add(function()
        if isClient() then pcall(scanNearPlayers) end
    end)
end
'''


def write_tv_screen_lua(dest_path):
    rows = ['    ["%s"] = { %s },' % (k, ", ".join('"%s"' % s for s in v)) for k, v in sorted(TV_SCREEN_MAP.items())]
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    open(dest_path, "w", encoding="utf-8").write(
        _TV_SCREEN_LUA_TEMPLATE % {"rows": "\n".join(rows), "loadgrid": _LOADGRID_LUA})
    return len(rows)


# ---------------------------------------------------------------------------------------------
# NORTH-WALL VIEWSCREENS (generated art)
# The pack only ships the Future Room viewscreens for the WEST wall. In the 2:1 iso projection a
# horizontal mirror of a west-wall sprite is the same object on the north wall, so we mirror each
# one into our own tileset. The originals carry no tile properties, so the copies need none.
_DTILES_PACK = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600\3628736763\mods\CommunityTilePack\common\media\texturepacks\DTilesPack.pack"
VIEWSCREEN_SOURCE = [24, 25, 26, 27, 28, 29, 32, 33, 34]      # DylansFutureRoom01_<i>, west wall
VIEWSCREEN_TILESET = "KBWCommunityViewscreensN"
VIEWSCREEN_PACK = "KBWCommunityViewscreens"
VIEWSCREEN_TILEDEF_NAME = "kbwcommunity_viewscreens"
VIEWSCREEN_TILEDEF_ID = 8187       # free (8180-8187 checked; 8185/8186 are ours)
# west sprite -> generated north sprite
VIEWSCREEN_NORTH = {"DylansFutureRoom01_%d" % s: "%s_%d" % (VIEWSCREEN_TILESET, j)
                    for j, s in enumerate(VIEWSCREEN_SOURCE)}


def _extract_from_pack(pack_path, names, cache_dir):
    """Extract named 128x256 tiles from a PZPK v1 pack into cache_dir (skips if cached)."""
    import io
    from PIL import Image
    os.makedirs(cache_dir, exist_ok=True)
    if all(os.path.exists(os.path.join(cache_dir, n + ".png")) for n in names):
        return
    with open(pack_path, "rb") as f:
        def i32():
            return struct.unpack("<i", f.read(4))[0]

        def s():
            return f.read(i32()).decode("utf-8", "replace")
        assert f.read(4) == b"PZPK" and i32() == 1
        for _ in range(i32()):
            s(); nent = i32(); i32()
            ents = [(s(), struct.unpack("<8i", f.read(32))) for _ in range(nent)]
            png = f.read(i32())
            hits = [e for e in ents if e[0] in names]
            if not hits:
                continue
            page = Image.open(io.BytesIO(png)).convert("RGBA")
            for name, (x, y, w, h, ox, oy, tw, th) in hits:
                tile = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
                tile.paste(page.crop((x, y, x + w, y + h)), (ox, oy))
                tile.save(os.path.join(cache_dir, name + ".png"))
    missing = [n for n in names if not os.path.exists(os.path.join(cache_dir, n + ".png"))]
    if missing:
        raise RuntimeError("textures not found in %s: %s" % (pack_path, missing))


def write_viewscreen_assets(media_dir):
    """Generate north-wall viewscreen tiles: texture pack + tiledef in <media_dir>."""
    from PIL import Image
    cache = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_cache_viewscreens")
    _extract_from_pack(_DTILES_PACK, set(VIEWSCREEN_NORTH), cache)
    tiles = []
    for west, north in sorted(VIEWSCREEN_NORTH.items(), key=lambda kv: int(kv[1].rsplit("_", 1)[1])):
        im = Image.open(os.path.join(cache, west + ".png")).convert("RGBA")
        tiles.append((north, im.transpose(Image.FLIP_LEFT_RIGHT)))
    n = _write_pack(os.path.join(media_dir, "texturepacks", VIEWSCREEN_PACK + ".pack"), VIEWSCREEN_PACK + "0", tiles)
    cols, rows = 8, (len(tiles) + 7) // 8
    # north-wall fixtures: Facing=S means attached to the north wall (see the west-wall patch group)
    props = [[(b"MoveType", b"WallObject"), (b"Facing", b"S")] if i < len(tiles) else []
             for i in range(cols * rows)]
    ts = [VIEWSCREEN_TILESET.encode(), (VIEWSCREEN_TILESET + ".png").encode(), cols, rows, 1, cols * rows, props]
    blob = b"tdef" + struct.pack("<ii", 1, 1) + _ser_tileset(ts)
    _parse(blob)
    open(os.path.join(media_dir, VIEWSCREEN_TILEDEF_NAME + ".tiles"), "wb").write(blob)
    return n


# Image cycle for a placed viewscreen: frosted -> Earth -> Mars -> frosted. The pack draws three
# framings (horizon heights) of each image; the k-th tile of each set shares a framing.
_VIEWSCREEN_SETS = {"frosted": [32, 33, 34], "earth": [24, 25, 26], "mars": [27, 28, 29]}
_VIEWSCREEN_ORDER = ["frosted", "earth", "mars"]


def _viewscreen_cycle():
    """sprite -> (next sprite, next state name), for west and generated north tiles."""
    cyc = {}
    for k in range(3):
        ring = [_VIEWSCREEN_SETS[s][k] for s in _VIEWSCREEN_ORDER]
        for i, idx in enumerate(ring):
            nxt = ring[(i + 1) % len(ring)]
            state = _VIEWSCREEN_ORDER[(i + 1) % len(ring)]
            w, wn = "DylansFutureRoom01_%d" % idx, "DylansFutureRoom01_%d" % nxt
            cyc[w] = (wn, state)
            cyc[VIEWSCREEN_NORTH[w]] = (VIEWSCREEN_NORTH[wn], state)
    return cyc


_VIEWSCREEN_LUA = r'''-- AUTO-GENERATED by pz_craft_loops/kbw_tilepatch.py -- do not edit by hand.
-- Right-click a Future Room viewscreen to cycle its image: frosted -> Earth -> Mars -> frosted.
-- Swaps the placed object's sprite (same pattern as vanilla ISWallpaperAction), so the choice is
-- saved with the object and synced to clients. No light source is involved.
require "TimedActions/ISBaseTimedAction"

local NEXT = {
%(rows)s
}
local LABEL = { frosted = "Viewscreen: Frost the Glass", earth = "Viewscreen: Show Earth", mars = "Viewscreen: Show Mars" }

KBWCycleViewscreenAction = ISBaseTimedAction:derive("KBWCycleViewscreenAction")

function KBWCycleViewscreenAction:isValid()
    return self.object ~= nil and self.object:getObjectIndex() ~= -1
end

function KBWCycleViewscreenAction:waitToStart()
    self.character:faceThisObject(self.object)
    return self.character:shouldBeTurning()
end

function KBWCycleViewscreenAction:update()
    self.character:faceThisObject(self.object)
end

function KBWCycleViewscreenAction:start()
    self:setActionAnim("Loot")
end

function KBWCycleViewscreenAction:perform()
    ISBaseTimedAction.perform(self)
end

function KBWCycleViewscreenAction:complete()
    local spr = self.object and self.object:getSprite()
    local entry = spr and NEXT[spr:getName()]
    if entry then
        self.object:setSpriteFromName(entry[1])
        self.object:transmitUpdatedSpriteToClients()
    end
    return true
end

function KBWCycleViewscreenAction:getDuration()
    return 20
end

function KBWCycleViewscreenAction:new(character, object)
    local o = ISBaseTimedAction.new(self, character)
    o.object = object
    o.maxTime = o:getDuration()
    o.stopOnWalk = true
    o.stopOnRun = true
    return o
end

local function onCycle(playerObj, object)
    if luautils.walkAdj(playerObj, object:getSquare(), true) then
        ISTimedActionQueue.add(KBWCycleViewscreenAction:new(playerObj, object))
    end
end

local function addMenu(player, context, worldobjects, test)
    if test then return end
    local playerObj = getSpecificPlayer(player)
    if not playerObj then return end
    local seen = {}
    for _, wo in ipairs(worldobjects) do
        local sq = wo and wo.getSquare and wo:getSquare()
        if sq then
            local objs = sq:getObjects()
            for i = 0, objs:size() - 1 do
                local o = objs:get(i)
                local spr = o and o:getSprite()
                local entry = spr and NEXT[spr:getName()]
                if entry and not seen[o] then
                    seen[o] = true
                    context:addOption(LABEL[entry[2]] or "Viewscreen: Change Image", playerObj, onCycle, o)
                end
            end
        end
    end
end

if Events.OnFillWorldObjectContextMenu then
    Events.OnFillWorldObjectContextMenu.Add(addMenu)
end
'''


def write_viewscreen_lua(dest_path):
    rows = ['    ["%s"] = { "%s", "%s" },' % (k, v[0], v[1]) for k, v in sorted(_viewscreen_cycle().items())]
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    open(dest_path, "w", encoding="utf-8").write(_VIEWSCREEN_LUA % {"rows": "\n".join(rows)})
    return len(rows)


def add_viewscreen_north_faces(buildable):
    """If a buildable is a west-only Future Room viewscreen, add the generated north face. In place."""
    changed = False
    for st in buildable.get("stages", []):
        faces = (st.get("geometry") or {}).get("faces") or {}
        w = faces.get("W")
        if not w or "N" in faces:
            continue
        try:
            sprite = w["layers"][0]["rows"][0][0]
        except (KeyError, IndexError, TypeError):
            continue
        north = VIEWSCREEN_NORTH.get(sprite)
        if north:
            faces["N"] = {"layers": [{"rows": [[north]]}]}
            changed = True
    return changed


# TIKITOWN SOUNDPROOF WINDOW PANEL, west wall: a generated mirror of tikitown-props-14_17
# (tiledef kbwtikitown_soundproof 8179) was tried 2026-08-28 and REMOVED (user): a plain flip does
# not match the pack's west panels; the west window panel needs redrawn art. 8179 is free again.


# ---------------------------------------------------------------------------------------------
# FEARS WORKBENCHES: generated second orientations (art + tile properties + depth maps)
# fears_workbenches (Community pack) ships S-facing pairs for six benches but E-facing pairs only
# for Tailoring (8/9) and Metalworking (10/11). In the 2:1 iso projection a horizontally mirrored
# S-facing pair IS the E-facing pair (the pack's own E pairs are drawn that way):
#   E grid (0,0) = mirror(S grid (0,0))      E grid (0,1) = mirror(S grid (1,0))
# Depth maps mirror the same way (the iso camera is symmetric under the X<->Y swap). B42 loads a
# mod's depth maps / tileGeometry ONLY from <mod>/common/media, and depth maps only when that mod
# also has a common/media/tileGeometry.txt, so those go in common/.
_FEARS_PACK = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600\3628736763\mods\CommunityTilePack\common\media\texturepacks\fearstiles.pack"
_FEARS_TILES = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600\3628736763\mods\CommunityTilePack\common\media\fearstiledefinitions01.tiles"
_FEARS_DEPTH = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600\3628736763\mods\CommunityTilePack\common\media\depthmaps\DEPTH_fears_workbenches.png"
FEARS_TILESET = "KBWCommunityFearsMirror"
FEARS_PACK = "KBWCommunityFears"
FEARS_TILEDEF_NAME = "kbwcommunity_fears"
FEARS_TILEDEF_ID = 8184            # free (8180-8187 checked; 8185-8187 are ours)
# generated index -> (source fears_workbenches index, new Facing or None, new SpriteGridPos or None)
_FEARS_MIRRORS = [
    (4, "E", "0,0"), (5, "E", "0,1"),     # Electrical
    (6, "E", "0,0"), (7, "E", "0,1"),     # Carpentry
    (20, "E", "0,0"), (21, "E", "0,1"),   # Chemistry
    (22, "E", "0,0"), (23, "E", "0,1"),   # Gunsmithing
    (17, "S", None),                      # Anvil (pack: Facing=E)
    (18, None, None),                     # Compressor (pack: no Facing)
]


def fears_mirror_name(src_index):
    for j, (s, _f, _g) in enumerate(_FEARS_MIRRORS):
        if s == src_index:
            return "%s_%d" % (FEARS_TILESET, j)
    raise KeyError(src_index)


def write_fears_assets(media_dir, common_media_dir):
    """Texture pack + tiledef in <media_dir>; depth map + tileGeometry.txt in <common_media_dir>."""
    from PIL import Image
    cache = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_cache_fears")
    names = {"fears_workbenches_%d" % s for s, _f, _g in _FEARS_MIRRORS}
    _extract_from_pack(_FEARS_PACK, names, cache)
    _ver, src_ts, _order = _parse(open(_FEARS_TILES, "rb").read())
    src = src_ts[b"fears_workbenches"]

    tiles, props = [], []
    for j, (s, facing, grid) in enumerate(_FEARS_MIRRORS):
        im = Image.open(os.path.join(cache, "fears_workbenches_%d.png" % s)).convert("RGBA")
        tiles.append(("%s_%d" % (FEARS_TILESET, j), im.transpose(Image.FLIP_LEFT_RIGHT)))
        p = []
        for k, v in src[6][s]:
            if k == b"Facing" and facing:
                v = facing.encode()
            elif k == b"SpriteGridPos" and grid:
                v = grid.encode()
            p.append((k, v))
        if facing and not any(k == b"Facing" for k, _ in p):
            p.append((b"Facing", facing.encode()))
        props.append(p)
    n = _write_pack(os.path.join(media_dir, "texturepacks", FEARS_PACK + ".pack"), FEARS_PACK + "0", tiles)

    cols = 8
    rows = (len(tiles) + cols - 1) // cols
    props += [[] for _ in range(cols * rows - len(props))]
    ts = [FEARS_TILESET.encode(), (FEARS_TILESET + ".png").encode(), cols, rows, 1, cols * rows, props]
    blob = b"tdef" + struct.pack("<ii", 1, 1) + _ser_tileset(ts)
    _parse(blob)
    open(os.path.join(media_dir, FEARS_TILEDEF_NAME + ".tiles"), "wb").write(blob)

    # depth map: same cell layout as the art sheet (128x256 cells, 8 per row)
    depth_src = Image.open(_FEARS_DEPTH).convert("RGBA")
    cw, ch = 128, 256
    depth = Image.new("RGBA", (cols * cw, rows * ch), (0, 0, 0, 0))
    for j, (s, _f, _g) in enumerate(_FEARS_MIRRORS):
        sx, sy = (s % 8) * cw, (s // 8) * ch
        cell = depth_src.crop((sx, sy, sx + cw, sy + ch)).transpose(Image.FLIP_LEFT_RIGHT)
        depth.paste(cell, ((j % cols) * cw, (j // cols) * ch))
    os.makedirs(os.path.join(common_media_dir, "depthmaps"), exist_ok=True)
    depth.save(os.path.join(common_media_dir, "depthmaps", "DEPTH_%s.png" % FEARS_TILESET))
    # The depth-map loader only runs for mods that ship a tileGeometry.txt. Ours carries no shapes
    # (the source geometry uses rotated boxes/cylinders/polygons that don't mirror trivially); the
    # rendered depth comes from the depth map above.
    open(os.path.join(common_media_dir, "tileGeometry.txt"), "w", encoding="utf-8").write(
        "tileGeometry\n{\n    VERSION = 2,\n}\n")
    return n


# ---------------------------------------------------------------------------------------------
# MILITARY CASES: second orientation (generated)
# The pack draws the green (furniture_storage_ddd_01_4) and white (_9) cases in ONE orientation
# only. Tiles 5/6 and 10/11 are NOT a rotated angle: shifted down 31/62 px they match 4/9 pixel
# for pixel apart from shading -- they are the same case pre-drawn at stack levels 2 and 3.
# The second orientation is a horizontal mirror of 4/9 (same method as the Fears benches), in our
# own tileset, with the source tile's properties plus our stacking patch (IsStackable/IsTable/
# Surface 16), the attached flag swapped N<->W, and mirrored depth-map cells.
_DTP_PACK = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600\3628736763\mods\CommunityTilePack\common\media\texturepacks\diederiks_tile_palooza.pack"
_DTP_DEPTH = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600\3628736763\mods\CommunityTilePack\common\media\depthmaps\DEPTH_furniture_storage_ddd_01.png"
CASES_TILESET = "KBWCommunityCasesMirror"
CASES_PACK = "KBWCommunityCases"
CASES_TILEDEF_NAME = "kbwcommunity_cases"
CASES_TILEDEF_ID = 8183            # free (8176-8183 checked across all installed mods; 8184-8187 ours)
_CASES_SRC_SHEET = "furniture_storage_ddd_01"
_CASES_MIRRORS = [4, 9]            # generated index j -> source index (green, white)
_ATTACH_SWAP = {b"attachedN": b"attachedW", b"attachedW": b"attachedN",
                b"attachedS": b"attachedE", b"attachedE": b"attachedS"}


def cases_mirror_name(src_index):
    return "%s_%d" % (CASES_TILESET, _CASES_MIRRORS.index(src_index))


def _patched_props(tileset, index, props):
    """Source tile props with our _PATCH_GROUPS adds/removes applied (what the game ends up with)."""
    p = list(props)
    for ts_name, idxs, adds, removes in _PATCH_GROUPS:
        if ts_name != tileset or index not in idxs:
            continue
        p = [(k, v) for k, v in p if k not in removes]
        have = {k for k, _ in p}
        p += [(k, v) for k, v in adds if k not in have]
    return p


def write_cases_assets(media_dir, common_media_dir):
    """Mirrored military-case tiles: texture pack + tiledef in <media_dir>, depth map in
    <common_media_dir>/depthmaps (common/media/tileGeometry.txt is written by write_fears_assets)."""
    from PIL import Image
    cache = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_cache_cases")
    names = {"%s_%d" % (_CASES_SRC_SHEET, s) for s in _CASES_MIRRORS}
    _extract_from_pack(_DTP_PACK, names, cache)
    _ver, tilesets = _load_community_tilesets()
    src = tilesets[_CASES_SRC_SHEET.encode()]

    tiles, props = [], []
    for j, s in enumerate(_CASES_MIRRORS):
        im = Image.open(os.path.join(cache, "%s_%d.png" % (_CASES_SRC_SHEET, s))).convert("RGBA")
        tiles.append(("%s_%d" % (CASES_TILESET, j), im.transpose(Image.FLIP_LEFT_RIGHT)))
        p = []
        for k, v in _patched_props(_CASES_SRC_SHEET, s, src[6][s]):
            p.append((_ATTACH_SWAP.get(k, k), v))
        props.append(p)
    n = _write_pack(os.path.join(media_dir, "texturepacks", CASES_PACK + ".pack"), CASES_PACK + "0", tiles)

    cols = 8
    rows = 1
    props += [[] for _ in range(cols * rows - len(props))]
    ts = [CASES_TILESET.encode(), (CASES_TILESET + ".png").encode(), cols, rows, 1, cols * rows, props]
    blob = b"tdef" + struct.pack("<ii", 1, 1) + _ser_tileset(ts)
    _parse(blob)
    open(os.path.join(media_dir, CASES_TILEDEF_NAME + ".tiles"), "wb").write(blob)

    if os.path.isfile(_DTP_DEPTH):
        depth_src = Image.open(_DTP_DEPTH).convert("RGBA")
        cw, ch = 128, 256
        depth = Image.new("RGBA", (cols * cw, rows * ch), (0, 0, 0, 0))
        for j, s in enumerate(_CASES_MIRRORS):
            sx, sy = (s % 8) * cw, (s // 8) * ch
            depth.paste(depth_src.crop((sx, sy, sx + cw, sy + ch)).transpose(Image.FLIP_LEFT_RIGHT),
                        (j * cw, 0))
        os.makedirs(os.path.join(common_media_dir, "depthmaps"), exist_ok=True)
        depth.save(os.path.join(common_media_dir, "depthmaps", "DEPTH_%s.png" % CASES_TILESET))
    return n


# ---------------------------------------------------------------------------------------------
# ICE MACHINE SHELL (generated, 2026-11-02): stage 1 of the two-stage Large / Industrial ice
# machines. Same art as kitchen_misc_tk_01_8..11 (TK ice machine) in our own tileset, carrying the
# tile's patch-group properties (name, facing, placement block) but NOT the vanilla chest-freezer
# copy, so the shell is not a freezer. KBW turns any tile with a container property into a
# container, which is why the shell can't simply reuse the patched ice machine tiles.
# No depth map / tileGeometry: the source sheet has none.
_TK_PACK = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600\3628736763\mods\CommunityTilePack\common\media\texturepacks\tkTiles_01.pack"
ICESHELL_TILESET = "KBWCommunityIceShell"
ICESHELL_PACK = "KBWCommunityIceShell"
ICESHELL_TILEDEF_NAME = "kbwcommunity_iceshell"
ICESHELL_TILEDEF_ID = 8181          # free (8170-8199 checked across installed mods; 8182-8187 ours)
_ICESHELL_SRC_SHEET = "kitchen_misc_tk_01"
_ICESHELL_SRC = [8, 9, 10, 11]     # generated index j -> source index (Facing S, E, N, W)


def iceshell_name(src_index):
    return "%s_%d" % (ICESHELL_TILESET, _ICESHELL_SRC.index(src_index))


# Fridge / freezer shell tiles (EXPERIMENT 2026-11-02, test bundle only until confirmed): inert
# single-tile copies of the vanilla 1-tile refrigerators and the chest freezer
# (appliances_refrigeration_01), stage 1 of the two-stage fridge / freezer tiers
# (align_appliance_costs.build_fridge_defs). Shell index = 4 + position in _FRIDGE_SRC.
# Container / pick-up / scrap properties are dropped so the shell is inert and can't be picked up
# or scrapped for free materials. (The 2-tile popsicle shells were dropped: WE's placement check
# only waives collisions on the anchor tile of a replacement, so 2-tile shells can't be finished.)
_VANILLA_TILES2X_PACK = r"C:\Program Files (x86)\Steam\steamapps\common\ProjectZomboid\media\texturepacks\Tiles2x.pack"
_VANILLA_DEPTH_REFRIG = r"C:\Program Files (x86)\Steam\steamapps\common\ProjectZomboid\media\depthmaps\DEPTH_appliances_refrigeration_01.png"
_FRIDGE_SHEET = "appliances_refrigeration_01"
# white 0-3, blue 4-7, steel 8-11, green 12-15, industrial 22/23/36/37, mini 24-27, plain 28-31,
# red 32-35, white industrial 40-43, chest freezer 48-51
_FRIDGE_SRC = (list(range(0, 16)) + [22, 23] + list(range(24, 38)) + list(range(40, 44))
               + list(range(48, 52)))
_FREEZER_SRC = set(range(48, 52))
_SHELL_DROP = {b"ContainerCapacity", b"ContainerCloseSound", b"ContainerOpenSound", b"ContainerPosition",
               b"ContainerPutSound", b"ContainerTakeSound", b"Freezer", b"FreezerCapacity", b"container",
               b"ForceSingleItem", b"IsMoveAble", b"PickUpLevel", b"PickUpWeight", b"CanScrap",
               b"Material", b"Material2", b"Material3", b"ScrapSize", b"SpriteGridPos"}


def fridge_shell_name(src_index):
    """Shell sprite for vanilla appliances_refrigeration_01_<src_index>."""
    return "%s_%d" % (ICESHELL_TILESET, 4 + _FRIDGE_SRC.index(src_index))


# Hand-pump sinks (user, 2026-11-09): copies of the five vanilla counter-top sinks
# (fixtures_sinks_01, IsTableTop: White 0-3, Industrial 4-7, Chrome 8-11, Dark Industrial 16-19,
# Beige 20-23) that draw water like WE's Large Water Tank / a map hand pump: waterAmount and
# waterMaxAmount 999999 and no waterPiped. Vanilla's own sinks keep their 20-unit plumbed reserve:
# the map's sinks are never touched. They live in the ice-shell tileset at FIXED indices 48..67
# (after the 44 fridge shells, padded to the row), so no new pack / tiledef / mod.info line.
PUMP_SINK_SHEET = "fixtures_sinks_01"
PUMP_SINK_SRC = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 16, 17, 18, 19, 20, 21, 22, 23]
PUMP_SINK_BASE = 48
_VANILLA_DEPTH_SINKS = r"C:\Program Files (x86)\Steam\steamapps\common\ProjectZomboid\media\depthmaps\DEPTH_fixtures_sinks_01.png"
_VANILLA_DEPTH_SEATING = r"C:\Program Files (x86)\Steam\steamapps\common\ProjectZomboid\media\depthmaps\DEPTH_furniture_seating_indoor_01.png"
_VANILLA_DEPTH_PRESET = r"C:\Program Files (x86)\Steam\steamapps\common\ProjectZomboid\media\depthmaps\DEPTH_preset_depthmaps_01.png"
_VANILLA_DEPTH_ASSIGN = r"C:\Program Files (x86)\Steam\steamapps\common\ProjectZomboid\media\tileDepthTextureAssignments.txt"
_PUMP_SINK_DROP = {b"waterPiped", b"waterAmount", b"waterMaxAmount"}   # re-added below (one copy)


def pump_sink_name(src_index):
    """Hand-pump copy of vanilla fixtures_sinks_01_<src_index>."""
    return "%s_%d" % (ICESHELL_TILESET, PUMP_SINK_BASE + PUMP_SINK_SRC.index(src_index))


def _pump_sink_props(src_props):
    out = [(k, v) for k, v in src_props if k not in _PUMP_SINK_DROP]
    # waterPiped is KEPT (user, 2026-11-13: the sinks gave tainted water). IsoObject.isWaterInfinite
    # returns true for waterAmount >= 9999 before any room / piping / water-shutoff check, so the
    # sinks stay infinite. getInfiniteWaterType returns clean Water only for an unmoved waterPiped
    # object (modData canBeWaterPiped not false; KBW's NativeObjectFactory sets it true) or the
    # hard-coded camping_01_16 / 64-67 sprites; anything else is TaintedWater. Only plumbing the
    # sink to a barrel (ISPlumbItem / plumbObject) sets canBeWaterPiped = false.
    out += [(b"waterAmount", b"999999"), (b"waterMaxAmount", b"999999"), (b"waterPiped", b"")]
    # moveable name = GroupName + CustomName ("White" + "Hand Pump Sink"): picked up it stays clear
    return [(k, b"Hand Pump Sink" if k == b"CustomName" else v) for k, v in out]


# Dirkies decor-house copies (user, 2026-08-28) at FIXED indices 72..83 of the ice-shell tileset
# (after the pump sinks 48..67, padded to the row). Source: edit_ddd_RUS_decor_house_01 (Community,
# diederiks_tile_palooza.pack). The pack tiles stay as they are on the map; only our copies change:
#   16-19 full-height iron ladder (pack: sheet-rope climbSheetW/N/S/E) -> B42 ladder flags
#         ladderW/N/S/E + attached/Facing, like vanilla's ladders (ladders.py builds it);
#   96-99 ladder top for the floor above (pack: climbSheetTop*; 99 says W but is drawn E) ->
#         decoration only: no climb flag, nothing solid;
#   100-103 red wall cabinet (pack: free-standing solidtrans block) -> MoveType WallObject on its
#         wall edge, not solid (a container comes from the definition; dirkies_decor_house.py).
# Edges from the art and the pack's own order (W, N, S, E). Depth: the pack's own depth cells.
#
# Caged crane ladder (user, 2026-08-28) at FIXED indices 84..89, right after: Dirkies
# edit_ddd_RUS_industry_crane_01 (same pack). Two wall edges only (W, N), three pieces each:
#   72 / 77 bottom (cage starts above an open lower part), 73 / 76 middle (full cage):
#         pack climbSheetW/N + solidtrans -> ladderW/N, not solid (a vanilla ladder is walk-through);
#   74 / 75 top ring for the open square above the last ladder (pack climbSheetTopW/N) ->
#         decoration only, like the iron ladder top.
DECOR_SHEET = "edit_ddd_RUS_decor_house_01"
CRANE_SHEET = "edit_ddd_RUS_industry_crane_01"
DECOR_BASE = 72
DECOR_LADDERS, DECOR_TOPS, DECOR_CABINET = (16, 17, 18, 19), (96, 97, 98, 99), (100, 101, 102, 103)
CRANE_BOTTOM, CRANE_MIDDLE, CRANE_TOP = (72, 77), (73, 76), (74, 75)   # (W, N)
# Exterior window trim (user, 2026-08-28) at FIXED indices 90..121: Dirkies fixtures_details_ddd_01
# 0-31 (4 colours x 4 styles x W/N). The pack tiles are MoveType WindowObject, which KBW / WE build as
# a native curtain. Our copies are plain wall overlays instead (WallOverlay + attachedW/N, no
# MoveType), like the tterika wall detailing, so KBW hangs them on the host (window) wall.
FDD_SHEET = "fixtures_details_ddd_01"
FDD_TRIM = tuple(range(0, 32))
# Dirkies medical sheet (user, 2026-08-28) at FIXED indices 122..129:
#   20-23 Large Industrial Sink (Facing E, S, W, N = KBW W, N, E, S) -> hand-pump copies, water
#         like the other pump sinks (999999, no waterPiped);
#   24-27 wheelchair (pack: CustomItem Wheelchair, IsMoveAble only; the pack's seating.txt already
#         has a seat per tile: 24 E, 25 W, 26 N, 27 S) -> a chair: bed + chair<dir> + BedType like
#         vanilla chairs, so "Rest" sits you in it. KBW face = opposite of the seat direction.
#         Our seating.txt (write_decor_seating) copies the pack's seat positions onto the copies.
MED_SHEET = "location_community_medical_ddd_01"
MED_SINK = (20, 21, 22, 23)
MED_WHEELCHAIR = (24, 25, 26, 27)
_FACE_SEAT = {"W": "E", "E": "W", "S": "N", "N": "S"}   # KBW face -> seat direction / Facing
# Height fixes (user, 2026-08-28) at FIXED indices 130..143:
#   medical 32-37 (centrifuge, analyzer, specimen cabinet): the art is drawn at counter height (art
#         bottom ~165 px, same as the desk mic) but the pack gives no table-top flags, so they float
#         on the floor. Copies get IsTableTop + IsSurfaceOffset + Surface=29 (the desk mic's values):
#         KBW / vanilla then drop them to the floor, or seat them on a counter, and our table-top
#         height Lua keeps it that way on load (TABLETOP_DECOR below).
#   decor house 0-3 / 8-11 (blue / green drawer cabinets): wall-mounted at mid height (see
#         _WALLBOX_EDGE; a floor / stacking version was tried and still floated).
# Window planters + pots (user, 2026-08-28) at FIXED indices 144..159, fixtures_details_ddd_01:
#   32-39 window planters: the pack tiles are movable WallObjects, which World Essentials builds
#         through its native wall-attachment path, and that path refuses window walls ("can't place
#         the planters"; they belong under a Window Frame-Tall window). Copies = plain wall overlays
#         like the window trim (WallOverlay + attached flag; no MoveType / IsMoveAble), which work.
#   40-47 potted plants / flower basket: drawn pushed against the west / north wall edge, so on an
#         open square they look raised. Copies have the art centred on the square (POT_BOTTOM) and
#         no wall attachment: free-standing floor pots.
FDD_PLANTERS = tuple(range(32, 40))
FDD_POTS = tuple(range(40, 48))
POT_BOTTOM = 228            # art bottom of a centred pot (floor diamond centre is y 224)
# Gun racks (user, 2026-08-28) at FIXED indices 160..175: Dylan's DarthGunStore (dylanstiles,
# DTilesPack). 8-15 = two 2-tile pegboard racks, each N (Facing S, 8+9 / 12+13) and W (Facing E,
# 11 over 10 / 15 over 14); 16-23 = their fill overlays (the pack's WorldFiller_dylan.lua maps
# DarthGunStore_8..15 -> _16.._23). The pack tiles are MoveType WallObject + WallOverlay, which vanilla
# types as a "WallOverlay" moveable, so World Essentials builds them as a sprite attached to the wall:
# no object, no storage (that was the old "placement bug"). Copies drop WallOverlay -> a plain wall
# object with its own metal_shelves container per tile. The overlays are copied too (our own names,
# safe from the dylanstiles tiledef clash) and registered for the copies by write_gunrack_overlay_lua.
GUN_SHEET = "DarthGunStore"
GUN_RACKS = tuple(range(8, 16))
GUN_OVERLAYS = tuple(range(16, 24))
_GUN_PACK = os.path.join(os.path.dirname(_COMMUNITY_TILES), "texturepacks", "DTilesPack.pack")
# Dylan's Future Room extras (user, 2026-08-28) at FIXED indices 176..198: DylansFutureRoom01
# (dylanstiles / DTilesPack). The pack gives these tiles NO properties at all, and World Essentials'
# isolated WECommunity_DylansFutureRoom01 covers only the viewscreens, so every piece is built on our
# own copies (also keeps them clear of the dylanstiles tiledef clash). MIRROR = source index + 1000:
# a whole-tile left-right flip of the source, which turns a south-facing piece into an east-facing
# one (and a north-wall fixture into a west-wall one); its depth cell is flipped with it.
#   22 / 23   wall screens -> working wall TVs (vanilla TV flags; screens warped by _PACK_TVS)
#   30 / 31   black / white fridge (Facing S) + mirrors (E): vanilla fridge flags (fridge + freezer)
#   35 / 36   black / white upper cabinet (north wall) + mirrors (west wall): like the Dirkie upper
#             cabinets (WallObject + IsHigh + attached + solidtrans + container): hang over counters
#   37 / 38   black / white low cabinet (Facing S) + mirrors: floor cabinet with counter storage
#   40-47     black 2-tile couch, 4 facings: vanilla Red Comfy couch flags + seat positions per tile
#   49        potted plant (floor decoration)
FR_SHEET = "DylansFutureRoom01"
FR_TV = (22, 23)
FR_FRIDGE = (30, 31, 1030, 1031)
# fridge copy -> (vanilla screen series, screen quad TL / TR / BL in tile px) for the door TV
_FRIDGE_TV_KEYS = {b"IsoType", b"signal", b"TV", b"CustomItem"}
FR_FRIDGE_TV_QUADS = (
    (30, "S", ((54, 99), (78, 111), (54, 123))),
    (31, "E", ((51, 108), (77, 95), (51, 135))),
    (1030, "E", ((50, 111), (74, 99), (50, 135))),
    (1031, "S", ((51, 95), (77, 108), (51, 122))),
)
FR_UPPER = (35, 36, 1035, 1036)
FR_LOWER = (37, 38, 1037, 1038)
FR_COUCH = (40, 41, 42, 43, 44, 45, 46, 47)
FR_PLANT = (49,)
MIRROR = 1000
SHELL = 2000                # index + SHELL = the inert shell copy of that (possibly mirrored) piece
# couch tile -> (vanilla furniture_seating_indoor_01 tile with the same facing + grid position, grid)
FR_COUCH_SRC = {40: (0, "0,0"), 41: (1, "1,0"), 43: (3, "0,0"), 42: (2, "0,1"),
                45: (5, "0,0"), 44: (4, "0,1"), 46: (6, "0,0"), 47: (7, "1,0")}
_FR_COLOUR = {30: b"Black", 31: b"White", 35: b"Black", 36: b"White", 37: b"Black", 38: b"White"}
MED_TABLETOP = (32, 33, 34, 35)
# 36/37 specimen cabinet: wall-mounted at mid height (user, in game 2026-08-28: as a table-top it
# floated and showed texture trouble at the base). Copy = pack art in place, hung on the wall edge
# its Facing names (wallbox, like the drawer cabinets).
# All 32-37 copies drop the pack's CustomItem (medical_01/02/03): that item does not exist, and the
# game logged "couldn't find item medical_03" over and over once one was built.
MED_WALL = (36, 37)
# MRI Scanner as a bed (user, 2026-08-28): the patient table runs N/S over medical 42 (south, the
# foot) and 43 (north, the head). Copies get the flags of the vanilla single bed tile with the same
# role (furniture_bedding_01: 0 = foot, Facing S, grid 0,1; 1 = head, grid 0,0), so Rest / Sleep
# lie the player N/S. Seating: the vanilla bed's W + E positions. (E only, for "seated facing east",
# failed in game 2026-08-28: Rest needs the stand square beside the seat free, and east of the table
# is the solid pedestal column, so the path failed and vanilla sat the player on the ground. A seat
# faces away from the bed, so the reachable W side faces west.)
MED_MRI_BED = {42: (0, "0,1"), 43: (1, "0,0")}
# MRI seats (user, in game 2026-08-28, 2nd round): the vanilla bed seats sat the player floating
# west of the table. The MRI table is NOT bed-sized: measured from the assembled art it is ~0.58
# tile wide, centred on the pedestal at x ~0.84 of the west column (spans x 0.55..1.13), its south
# end at the piece's south edge, top ~66 px up (vanilla mattress ~56 px at seat height 0.35-0.42).
# Seat = (id = the direction the seated player faces, x, height, y): tile units from the tile
# centre, +x east, +y south (seating.txt "translate = x height y" x 10000). Inset from the edge
# like vanilla's bed seats (~0.16). First id = what getFacingDirection reports.
#   foot 42: S only, on the south end (user: "facing south, on the south edge").
#   middle 43: W + E; Rest picks the reachable one nearest the player. E's stand square is the
#   pedestal column, which KBW blocks (blockAllTheSquare is per buildable, not per tile), so in
#   practice it is W; E is there for when that square is free.
MRI_SEATS = {
    42: [("S", 0.34, 0.41, 0.33)],
    43: [("W", 0.21, 0.42, 0.0), ("E", 0.47, 0.41, 0.0)],
}
# Copy kinds whose depth cell gets the art's uncovered pixels filled with the nearest depth
# (_fill_depth_holes; art with no depth is hidden once built). The couch always is (its own branch).
FILL_DEPTH_KINDS = ("bed",)
DRAWER_SRC = (0, 1, 2, 3, 8, 9, 10, 11)
# Blue / green drawer cabinets (decor house 0-3 / 8-11): moving the art 58 px to the floor still
# left them floating (user, 2026-08-28). They are wall-mounted mailbox banks (container postbox),
# drawn at mid height on purpose: the copies keep the pack art where it is and hang on the wall
# edge their facing names, like the Dirkie upper cabinets (WallObject + attached + solidtrans).
_WALLBOX_EDGE = {b"S": b"attachedN", b"E": b"attachedW", b"N": b"attachedS", b"W": b"attachedE"}
# (sheet, source index, wall edge, kind, group name) in copy order = index DECOR_BASE + position
DECOR_COPIES = (
    [(DECOR_SHEET, s, e, "ladder", b"Iron") for s, e in zip(DECOR_LADDERS, "WNSE")]
    + [(DECOR_SHEET, s, e, "top", b"Iron") for s, e in zip(DECOR_TOPS, "WNSE")]
    + [(DECOR_SHEET, s, e, "cabinet", b"Red") for s, e in zip(DECOR_CABINET, "WNSE")]
    + [(CRANE_SHEET, s, e, "ladder", b"Caged") for s, e in zip(CRANE_BOTTOM, "WN")]
    + [(CRANE_SHEET, s, e, "ladder", b"Caged") for s, e in zip(CRANE_MIDDLE, "WN")]
    + [(CRANE_SHEET, s, e, "top", b"Caged") for s, e in zip(CRANE_TOP, "WN")]
    + [(FDD_SHEET, s, "WN"[s % 2], "trim", b"Window Trim") for s in FDD_TRIM]
    + [(MED_SHEET, s, e, "pumpsink", b"Large Industrial") for s, e in zip(MED_SINK, "WNES")]
    + [(MED_SHEET, s, e, "seat", b"Wheelchair") for s, e in zip(MED_WHEELCHAIR, "WESN")]
    + [(MED_SHEET, s, "WN"[s % 2], "wallbox" if s in MED_WALL else "tabletop", b"Medical")
       for s in MED_TABLETOP + MED_WALL]
    + [(DECOR_SHEET, s, e, "wallbox", b"") for s, e in zip(DRAWER_SRC, "NWSE" * 2)]
    + [(FDD_SHEET, s, "WN"[s % 2], "overlaycopy", b"Window Planter") for s in FDD_PLANTERS]
    + [(FDD_SHEET, s, "WN"[s % 2], "centerpot", b"") for s in FDD_POTS]
    + [(GUN_SHEET, s, "NNWW"[(s - 8) % 4], "gunrack", b"") for s in GUN_RACKS]
    + [(GUN_SHEET, s, "", "overlaylayer", b"") for s in GUN_OVERLAYS]
    + [(FR_SHEET, s, "WN"[n], "tv", b"Future") for n, s in enumerate(FR_TV)]
    + [(FR_SHEET, s, "", "fridge", b"") for s in FR_FRIDGE]
    + [(FR_SHEET, s, "", "uppercab", b"") for s in FR_UPPER]
    + [(FR_SHEET, s, "", "lowcab", b"") for s in FR_LOWER]
    + [(FR_SHEET, s, "", "couch", b"Black Modern") for s in FR_COUCH]
    + [(FR_SHEET, s, "", "plant", b"") for s in FR_PLANT]
    # inert shells of the Future fridges (stage 1 of the 80/40 and 100/50 tiers, user 2026-08-28):
    # same art, the shell flags of the vanilla fridge shells (no fridge / freezer / container)
    # (index + SHELL keeps the key unique; the source tile stays index % 1000)
    + [(FR_SHEET, s + SHELL, "", "fridgeshell", b"") for s in FR_FRIDGE]
    + [(MED_SHEET, s, "", "bed", b"MRI") for s in sorted(MED_MRI_BED)]
)


def future_fridge_shells():
    """{our Future fridge sprite: its inert shell sprite} (DylansFutureRoom01 30/31 + mirrors)."""
    return {decor_copy_name(s, FR_SHEET): decor_copy_name(s + SHELL, FR_SHEET) for s in FR_FRIDGE}


def _mirrored(s):
    return (s // MIRROR) % 2 == 1        # 1030 / 3030 mirrored, 2030 (a shell of 30) not


def _src_index(s):
    return s % MIRROR


def gun_overlay_map():
    """{our rack copy: our overlay copy} (pack: DarthGunStore_<i> -> DarthGunStore_<i + 8>)."""
    return {decor_copy_name(s, GUN_SHEET): decor_copy_name(s + 8, GUN_SHEET) for s in GUN_RACKS}


GUNRACK_LUA_NAME = "KBWCommunity_GunRackOverlays.lua"


def write_gunrack_overlay_lua(dest_path):
    """Fill overlays (guns on the rack once it holds items) for our gun rack copies: the same
    vanilla ContainerOverlays registration the pack uses for its own DarthGunStore tiles."""
    rows = "\n".join('overlayMap["%s"] = {{ name = "other", tiles = {"%s", "%s"} }}' % (b, o, o)
                     for b, o in sorted(gun_overlay_map().items()))
    lua = ("-- AUTO-GENERATED by pz_craft_loops/kbw_tilepatch.py -- do not edit by hand.\n"
           "-- Fill overlays for our gun rack copies (DarthGunStore 8-15 -> overlays 16-23).\n"
           "local overlayMap = {}\noverlayMap.VERSION = 1\n%s\n"
           "if not TILEZED and getContainerOverlays then\n"
           "    getContainerOverlays():addOverlays(overlayMap)\nend\n" % rows)
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    open(dest_path, "w", encoding="utf-8", newline="\n").write(lua)
_DECOR_SHIFT = {}   # (sheet, index) -> (dx, dy) the copy's art was moved by (depth follows)
_DECOR_POS = {(sh, s): j for j, (sh, s, _e, _k, _g) in enumerate(DECOR_COPIES)}
DECOR_SRC = [s for sh, s, _e, _k, _g in DECOR_COPIES if sh == DECOR_SHEET]   # decor-house sources
_EDGE_FACING = {"W": b"E", "N": b"S", "S": b"N", "E": b"W"}   # vanilla ladders: attachedW + Facing=E
_COMMUNITY_MEDIA = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600\3628736763\mods\CommunityTilePack\common\media"
_DECOR_PACK = os.path.join(_COMMUNITY_MEDIA, "texturepacks", "diederiks_tile_palooza.pack")
_DECOR_DEPTH = os.path.join(_COMMUNITY_MEDIA, "depthmaps", "DEPTH_edit_ddd_RUS_decor_house_01.png")


def _decor_depth_png(sheet):
    return os.path.join(_COMMUNITY_MEDIA, "depthmaps", "DEPTH_%s.png" % sheet)


_DECOR_DROP = {b"climbSheetW", b"climbSheetN", b"climbSheetS", b"climbSheetE", b"climbSheetTopW",
               b"climbSheetTopN", b"climbSheetTopS", b"climbSheetTopE", b"solidtrans", b"solid",
               b"BlocksPlacement", b"Facing"}


def _shift(im, dx, dy):
    """The tile image moved by (dx, dy) pixels, same size (what moves off the edge is dropped)."""
    from PIL import Image
    out = Image.new(im.mode, im.size, (0, 0, 0, 0) if im.mode == "RGBA" else 0)
    out.paste(im, (dx, dy))
    return out


def _shift_down(im, px):
    return _shift(im, 0, px)


def _add_future_room_tvs():
    """Our Future Room wall-TV copies get generated screens like the Dylan TVs (APPENDED to
    _PACK_TVS so the existing KBWCommunityTVScreens_0..11 keep their names). Quads measured from the
    art (inner screen inside the bezel): 22 west wall (screen slopes up-right, vanilla E), 23 north
    wall (slopes down-right, vanilla S)."""
    names = [decor_copy_name(s, FR_SHEET) for s in FR_TV]
    if any(n == tv for n in names for tv, _f, _q in _PACK_TVS):
        return
    _PACK_TVS.append((names[0], "E", _WALLTV_QUAD[22]))
    _PACK_TVS.append((names[1], "S", _WALLTV_QUAD[23]))
    # Future fridges: their built-in door screen works as a TV (user, 2026-08-28). Quads measured
    # from the art (screen panel): black 30 on its left face (slopes down-right, vanilla S), white 31
    # on its right face (slopes up-right, vanilla E); the mirrors 1030 / 1031 flip x -> 128 - x.
    for s, facing, quad in FR_FRIDGE_TV_QUADS:
        _PACK_TVS.append((decor_copy_name(s, FR_SHEET), facing, quad))
    TV_SCREEN_MAP.clear()
    TV_SCREEN_MAP.update({tv: ["%s_%d" % (SCREEN_TILESET, t * 3 + k) for k in range(3)]
                          for t, (tv, _f, _q) in enumerate(_PACK_TVS)})
    # the 2nd Wall Screen TV copies use their own screen tiles (see WALLTV_BASE)
    TV_SCREEN_MAP.update({walltv_name(n): walltv_screen_names(n) for n in range(len(WALLTV))})


# Future Wall Screen TV, 2nd copies (user, 2026-11-13). The first copies (IceShell 176 / 177) came
# back from a reload with a black screen and half a Future couch on them: IsoTelevision.update()
# runs setupDefaultScreens while the screen list is empty, and that adds the sprites at the TV's
# own index +16 / +32 / +48 (vanilla's screen layout). For 176 that is IceShell_192, a couch tile;
# WE's TVScreens Lua replaces the list later, but the overlay already set stays until the next
# setScreen (switching off / on). So these copies sit at FIXED indices whose +16 / +32 / +48 hold
# their own warped screens, in vanilla's order: whichever code fills the list, it gets the right
# screens. 176 / 177 stay as they are (placed TVs keep their sprite); new builds use these.
# DECOR_COPIES must end before WALLTV_BASE; later fixed blocks go after the last screen (254).
WALLTV_BASE = 205
WALLTV = ((22, "W"), (23, "N"))                 # (DylansFutureRoom01 source, wall edge)
_WALLTV_SCREEN_FACING = {"W": "E", "N": "S"}    # vanilla screen series (W wall faces east)
# screen quads (top-left, top-right, bottom-left) measured from the art, inside the bezel
_WALLTV_QUAD = {22: ((12, 82), (65, 56), (12, 131)), 23: ((62, 56), (115, 82), (62, 106))}
_WALLTV_DEPTH_BIAS = 2      # TV + screens this much nearer than the bare wall plane (0..255)
# Future upper cabinets: the depth vanilla gives its floating wall cabinets (every facing of
# fixtures_counters_01 16-31 uses cell 16), so a cabinet hung over a Wall Screen TV draws over it
_UPPERCAB_DEPTH = ("fixtures_counters_01", 16)


def walltv_name(n):
    """Our 2nd Wall Screen TV copy n (0 = west wall, 1 = north wall)."""
    return "%s_%d" % (ICESHELL_TILESET, WALLTV_BASE + n)


def walltv_screen_names(n):
    return ["%s_%d" % (ICESHELL_TILESET, WALLTV_BASE + n + 16 * (k + 1)) for k in range(3)]


def walltv_face_sprites():
    """KBW face -> our 2nd Wall Screen TV sprite."""
    return {edge: walltv_name(n) for n, (_s, edge) in enumerate(WALLTV)}


def _walltv_tiles(cache):
    """{tile index: (name, image, props)} for the 2nd Wall Screen TV copies and their screens."""
    from PIL import Image
    _extract_vanilla_screens()
    out = {}
    for n, (s, edge) in enumerate(WALLTV):
        im = Image.open(os.path.join(cache, "%s_%d.png" % (FR_SHEET, s))).convert("RGBA")
        out[WALLTV_BASE + n] = (walltv_name(n), im, _future_room_props((FR_SHEET, s, edge, "tv", b"Future")))
        idxs, src = _VANILLA_SCREENS[_WALLTV_SCREEN_FACING[edge]]
        coeffs = _affine_inverse(src, _WALLTV_QUAD[s])
        for k, (vi, name) in enumerate(zip(idxs, walltv_screen_names(n))):
            sim = Image.open(os.path.join(_SCREEN_CACHE, "appliances_television_01_%d.png" % vi)).convert("RGBA")
            scr = sim.transform((128, 256), Image.AFFINE, coeffs, resample=Image.BILINEAR)
            out[WALLTV_BASE + n + 16 * (k + 1)] = (name, scr, [])    # vanilla screen tiles: no props
    return out


def _wall_plane_depth(edge, art, bias=0):
    """Vanilla's wall preset depth cell for a piece hung on the <edge> wall (W -> preset_depthmaps_01_4,
    N -> _5, as for walls_interior_detailing_01), extended along the wall plane (least-squares fit)
    under every art pixel outside the wall slab, then moved <bias> nearer the viewer."""
    import numpy as np
    from PIL import Image
    pre = Image.open(_VANILLA_DEPTH_PRESET).convert("RGBA")
    pcols = pre.size[0] // 128
    pi = {"W": 4, "N": 5}[edge]
    cell = np.array(pre.crop(((pi % pcols) * 128, (pi // pcols) * 256,
                              (pi % pcols) * 128 + 128, (pi // pcols) * 256 + 256)))
    ys, xs = np.nonzero(cell[:, :, 3] == 255)
    A = np.stack([xs, ys, np.ones_like(xs)], axis=1).astype(float)
    (ca, cb, cc), *_ = np.linalg.lstsq(A, cell[ys, xs, 0].astype(float), rcond=None)
    hole = (np.array(art.convert("RGBA"))[:, :, 3] > 0) & (cell[:, :, 3] == 0)
    hy, hx = np.nonzero(hole)
    v = np.clip(np.rint(ca * hx + cb * hy + cc), 0, 255).astype(np.uint8)
    for ch in range(3):
        cell[hy, hx, ch] = v
    cell[hy, hx, 3] = 255
    on = cell[:, :, 3] > 0
    for ch in range(3):
        c = cell[:, :, ch].astype(int)
        c[on] = np.clip(c[on] - bias, 0, 255)
        cell[:, :, ch] = c.astype(np.uint8)
    return Image.fromarray(cell, "RGBA")


def sync_we_tv_screens(we_base_lua):
    """Add our TV -> screen rows to the SCREENS table of World Essentials' own (WE-owned)
    KBWCommunity_TVScreens.lua, in our WORK copy. Returns the TVs added."""
    import re as _re
    raw = open(we_base_lua, "rb").read().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    txt = raw.replace("\r\n", "\n")
    m = _re.search(r"local SCREENS = \{\n(.*?)\n\}", txt, _re.S)
    if not m:
        raise RuntimeError("SCREENS table not found in %s" % we_base_lua)
    have = set(_re.findall(r'\["([^"]+)"\]\s*=', m.group(1)))
    add = [tv for tv in sorted(TV_SCREEN_MAP) if tv not in have]
    if add:
        rows = "\n".join('    ["%s"] = { %s },' % (tv, ", ".join('"%s"' % s for s in TV_SCREEN_MAP[tv])) for tv in add)
        txt = txt[:m.end(1)] + "\n" + rows + txt[m.end(1):]
        open(we_base_lua, "wb").write(txt.replace("\n", nl).encode("utf-8"))
    return add


_VANILLA_PROPS_CACHE = {}


def _vanilla_props(sheet, idx):
    if not _VANILLA_PROPS_CACHE:
        _v, ts, _o = _parse(open(_VANILLA_TILES, "rb").read())
        _VANILLA_PROPS_CACHE.update(ts)
    return list(_VANILLA_PROPS_CACHE[sheet.encode()][6][idx])


def _replace(props, **kv):
    """props with the given keys set (b"" for flags) and Python None meaning 'remove'."""
    d = dict(props)
    for k, v in kv.items():
        kb = k.encode()
        if v is None:
            d.pop(kb, None)
        else:
            d[kb] = v if isinstance(v, bytes) else v.encode()
    return sorted(d.items())


def _future_room_props(entry):
    """Tile properties for our DylansFutureRoom01 copies (the pack tiles have none)."""
    _sheet, s, edge, kind, group = entry
    base, m = _src_index(s), _mirrored(s)
    facing = "E" if m else "S"                      # source art faces south; the mirror east
    colour = _FR_COLOUR.get(base, b"")
    if kind == "fridge":                           # vanilla 1-tile fridge: fridge + freezer
        # + the door screen as a working TV (user, 2026-08-28): vanilla TV flags, so KBW builds an
        # IsoTelevision (NativeObjectTypes: IsoType) and creates the fridge / freezer containers from
        # these same flags (createContainersFromSpriteProperties, as for map fridges). CustomItem is
        # what IsoWaveSignal clones its TV device data from (none = a blank DeviceData). Not movable
        # (like our wall TVs): a vanilla pick-up would hand back the CustomItem TV, not the fridge.
        return _replace(_vanilla_props("appliances_refrigeration_01", 1 if m else 0), GroupName=colour,
                        IsoType=b"IsoTelevision", signal=b"tv", TV=b"", CustomItem=b"Base.TvWideScreen",
                        IsMoveAble=None, PickUpLevel=None, PickUpWeight=None)
    if kind == "uppercab":                         # a high wall cabinet, NOT solid (user 2026-08-28)
        # solidtrans made the square solid, and KBW refuses any solid / BlocksPlacement piece on a
        # solid square, so nothing could be built UNDER the cabinet (couch, low cabinet). Like the
        # vanilla overhead cabinets the copy is a movable high WallObject with its own container and
        # no solid flags: it still passes over counters / fridges (KBW's high-wall-object rule).
        wall = "attachedW" if m else "attachedN"
        return sorted({b"MoveType": b"WallObject", b"IsHigh": b"", wall.encode(): b"", b"IsMoveAble": b"",
                       b"container": b"counter", b"ContainerCapacity": b"20", b"ContainerPosition": b"High",
                       b"Facing": facing.encode(), b"CustomName": b"Upper Cabinet", b"GroupName": colour,
                       b"Material": b"MetalPlates", b"CanScrap": b""}.items())
    if kind == "lowcab":
        return sorted({b"BlocksPlacement": b"", b"solidtrans": b"", b"IsLow": b"", b"container": b"counter",
                       b"ContainerCapacity": b"20", b"ContainerPosition": b"Low", b"Facing": facing.encode(),
                       b"CustomName": b"Cabinet", b"GroupName": colour, b"Material": b"MetalPlates",
                       b"CanScrap": b""}.items())
    if kind == "tv":                               # same flags as the patched Dylan wall TVs
        face = "E" if edge == "W" else "S"
        # + vanilla's TV pick-up flags (user 2026-11-13: no Pick up option). The pick-up item is the
        # CustomItem TV (a Radio, which is a Moveable): ReadFromWorldSprite keeps OUR sprite on it, so
        # it places back as this Wall Screen. Rotation: W copy (Facing E) <-> N copy (Facing S) are
        # always adjacent indices (176/177, 205/206). No CanScrap (would scrap a built piece for free).
        off = {b"Soffset": b"1"} if face == "E" else {b"Eoffset": b"-1"}
        off.update({b"signal": b"tv", b"IsoType": b"IsoTelevision", b"CustomItem": b"Base.TvWideScreen",
                    b"TV": b"", b"Surface": b"15", b"MoveType": b"WallObject", b"IsHigh": b"",
                    ("attached" + edge).encode(): b"", b"Facing": face.encode(),
                    b"CustomName": b"Wall Screen", b"GroupName": group, b"IsMoveAble": b"",
                    b"PickUpWeight": b"100", b"Material": b"Electric", b"MaterialType": b"Glass_Light"})
        return sorted(off.items())
    if kind == "couch":
        vi, grid = FR_COUCH_SRC[s]
        return _replace(_vanilla_props("furniture_seating_indoor_01", vi), GroupName=group,
                        SpriteGridPos=grid, IsMoveAble=None, PickUpLevel=None, PickUpTool=None,
                        PickUpWeight=None, PlaceTool=None)
    return sorted({b"BlocksPlacement": b"", b"CustomName": b"Planter", b"GroupName": b"Future"}.items())


def decor_copy_name(src_index, sheet=DECOR_SHEET):
    """Our copy of <sheet>_<src_index> (decor house by default, or CRANE_SHEET)."""
    return "%s_%d" % (ICESHELL_TILESET, DECOR_BASE + _DECOR_POS[(sheet, src_index)])


def decor_edge(src_index, sheet=DECOR_SHEET):
    """KBW face (= the wall edge the piece hangs on) of a decor copy."""
    return DECOR_COPIES[_DECOR_POS[(sheet, src_index)]][2]


def _decor_props(entry, src_props):
    _sheet, _s, edge, kind, group = entry
    if kind == "pumpsink":     # same art and props, water like a map hand pump (see _pump_sink_props)
        return sorted(_pump_sink_props(src_props))
    if kind == "tabletop":     # counter-height art: the desk mic's table-top flags
        out = [(k, v) for k, v in src_props if k not in (b"IsTableTop", b"IsSurfaceOffset", b"Surface",
                                                         b"CustomItem")]
        out += [(b"IsTableTop", b""), (b"IsSurfaceOffset", b""), (b"Surface", b"29")]
        return sorted(out)
    if kind == "overlaycopy":  # plain wall overlay (not a movable WallObject): KBW hangs it on any wall
        out = [(k, v) for k, v in src_props if k not in (b"MoveType", b"IsMoveAble", b"PickUpWeight")]
        out += [(b"WallOverlay", b"")]
        return sorted(dict(out).items())
    if kind in ("fridge", "uppercab", "lowcab", "tv", "couch", "plant"):
        return _future_room_props(entry)
    if kind == "fridgeshell":  # inert casing: the vanilla fridge-shell rule (_SHELL_DROP + no fridge flags)
        fr = _future_room_props((entry[0], entry[1] % SHELL, entry[2], "fridge", entry[4]))
        # the shell is no TV either (unpowered casing): drop the door-screen TV flags too
        return sorted((k, b"Refrigerator Shell" if k == b"CustomName" else v) for k, v in fr
                      if k not in _SHELL_DROP and k not in _FRIDGE_TV_KEYS
                      and b"Fridge" not in k and b"Freezer" not in k)
    if kind == "bed":          # MRI table: the vanilla single bed tile with the same role
        vi, grid = MED_MRI_BED[_s]
        # the menu shows "<GroupName> <CustomName>": "MRI" + "Scanner" (was "MRI MRI Scanner")
        return _replace(_vanilla_props("furniture_bedding_01", vi), GroupName=b"MRI",
                        CustomName=b"Scanner", SpriteGridPos=grid.encode(), BedType=b"averageBed",
                        IsMoveAble=None, PickUpLevel=None, PickUpTool=None, PickUpWeight=None,
                        PlaceTool=None, CanScrap=None, Material=b"MetalPlates", Material2=None,
                        Material3=None)
    if kind == "gunrack":      # plain wall object with storage (not a "WallOverlay" moveable)
        return sorted((k, v) for k, v in src_props if k != b"WallOverlay")
    if kind == "overlaylayer":  # fill-overlay art only: no props
        return []
    if kind == "centerpot":    # centred floor pot: no wall attachment
        out = [(k, v) for k, v in src_props if not k.startswith(b"attached")]
        return sorted(out)
    if kind == "wallbox":      # mid-height wall-mounted cabinet on the edge its Facing names
        facing = dict(src_props).get(b"Facing", b"S")
        out = [(k, v) for k, v in src_props if k not in (b"Surface", b"IsLow", b"IsTableTop",
                                                         b"IsSurfaceOffset", b"CustomItem")]
        # solidtrans keeps it on KBW's thumpable path (container from the definition), like the
        # Dirkie upper cabinets; without it an attached sprite is placed as a bare moveable prop
        out += [(b"MoveType", b"WallObject"), (_WALLBOX_EDGE[facing], b""), (b"solidtrans", b"")]
        return sorted(dict(out).items())
    if kind == "seat":         # a chair: vanilla chair flags, no pick-up as the pack's CustomItem
        seat = _FACE_SEAT[edge]
        out = [(k, v) for k, v in src_props if k not in (b"CustomItem", b"IsMoveAble", b"Facing")]
        out += [(b"bed", b""), (("chair" + seat).encode(), b""), (b"BedType", b"averageBed"),
                (b"Facing", seat.encode()), (b"CustomName", b"Wheelchair"), (b"GroupName", b"Medical"),
                (b"BlocksPlacement", b""), (b"solidtrans", b""), (b"IsLow", b""), (b"Material", b"MetalBars")]
        return sorted(out)
    out = [(k, v) for k, v in src_props if k not in _DECOR_DROP]
    out += [(("attached" + edge).encode(), b""), (b"Facing", _EDGE_FACING[edge])]
    if kind == "ladder":
        out += [(("ladder" + edge).encode(), b""), (b"BlocksPlacement", b""), (b"forceFade", b""),
                (b"CanBreak", b""), (b"CustomName", b"Ladder"), (b"GroupName", group),
                (b"Material", b"Steel"), (b"MaterialType", b"Metal")]
    elif kind == "top":
        out += [(b"CustomName", b"Ladder Top"), (b"GroupName", group), (b"Material", b"Steel")]
    elif kind == "trim":
        out = [(k, v) for k, v in out if k != b"MoveType"]   # not a curtain / window moveable
        out += [(b"WallOverlay", b""), (b"CustomName", group)]
        return sorted(dict(out).items())   # the pack tile already has its attached flag
    else:
        # The container must be on the TILE (user 2026-08-28: "no storage"): an attached, non-solid
        # sprite is built by KBW through vanilla moveable placement, which only creates the
        # containers the sprite itself declares. The definition's capacity (20 / Reinforced 100) is
        # then applied to that container.
        out += [(b"MoveType", b"WallObject"), (b"CustomName", b"Wall Cabinet"), (b"GroupName", group),
                (b"Material", b"MetalPlates"), (b"CanBreak", b""), (b"IsMoveAble", b""),
                (b"container", b"counter"), (b"ContainerCapacity", b"20")]
    return sorted(dict(out).items())


_COMMUNITY_SEATING = os.path.join(_COMMUNITY_MEDIA, "seating.txt")


def _seating_tiles(path, tileset):
    """{(col, row): tile block text} for one tileset of a seating.txt (brace-matched)."""
    txt = open(path, encoding="utf-8", errors="replace").read()
    import re as _re
    m = _re.search(r"name\s*=\s*%s\s*," % _re.escape(tileset), txt)
    if not m:
        return {}
    # the tileset block ends at the brace that closes the one opened before "name ="
    depth, i = 1, m.end()
    while depth and i < len(txt):
        depth += {"{": 1, "}": -1}.get(txt[i], 0)
        i += 1
    body = txt[m.end():i - 1]
    out, pos = {}, 0
    for tm in _re.finditer(r"\btile\s*\{", body):
        if tm.start() < pos:
            continue
        depth, j = 1, tm.end()
        while depth and j < len(body):
            depth += {"{": 1, "}": -1}.get(body[j], 0)
            j += 1
        block = body[tm.start():j]
        xy = _re.search(r"xy\s*=\s*(\d+)\s+(\d+)", block)
        if xy:
            out[(int(xy.group(1)), int(xy.group(2)))] = block
        pos = j
    return out


def _seat_block(col, row, seats):
    """A seating.txt tile block. seats: [(id, x, height, y)] in tile units (x 10000 in the file);
    Front approach only (BlockLeft / BlockRight, like vanilla's bed seats)."""
    pos = []
    for pid, x, h, y in seats:
        pos.append("    position\n        {\n            id = %s,\n            translate = %d %d %d,\n"
                   "            properties\n            {\n                BlockLeft = true,\n"
                   "                BlockRight = true,\n            }\n        }"
                   % (pid, round(x * 10000), round(h * 10000), round(y * 10000)))
    return "tile\n        {\n            xy = %d %d,\n        %s\n        }" % (col, row, "\n        ".join(pos))


def _keep_seat_positions(block, ids):
    """A seating.txt tile block with only the `position` blocks whose id is in `ids`."""
    import re as _re
    out, pos = [], 0
    for pm in _re.finditer(r"\bposition\s*\{", block):
        if pm.start() < pos:
            continue
        depth, j = 1, pm.end()
        while depth and j < len(block):
            depth += {"{": 1, "}": -1}.get(block[j], 0)
            j += 1
        pid = _re.search(r"\bid\s*=\s*(\w+)", block[pm.start():j])
        out.append(block[pos:pm.start()])
        if pid and pid.group(1) in ids:
            out.append(block[pm.start():j])
        pos = j
    out.append(block[pos:])
    kept = "".join(out)
    if not _re.search(r"\bposition\s*\{", kept):
        raise RuntimeError("no seat position %s left in seating block" % (ids,))
    return kept


def write_decor_seating(common_media_dir, cols=8):
    """<common_media_dir>/seating.txt: the pack's seat positions for our seat copies (wheelchair),
    re-keyed to their cells in the ice-shell tileset. Returns the number of tiles written."""
    import re as _re
    src_cache, blocks = {}, []
    _VANILLA_SEATING = os.path.join(os.path.dirname(os.path.dirname(_VANILLA_TILES)), "seating.txt")
    if not os.path.isfile(_VANILLA_SEATING):
        _VANILLA_SEATING = r"C:\Program Files (x86)\Steam\steamapps\common\ProjectZomboid\media\seating.txt"
    for sh, s, _e, kind, _g in DECOR_COPIES:
        if kind == "seat":          # the pack's own seat for this tile
            src_file, src_set, src_i = _COMMUNITY_SEATING, sh, s
        elif kind == "couch":       # vanilla Red Comfy couch tile with the same facing + grid position
            src_file, src_set, src_i = _VANILLA_SEATING, "furniture_seating_indoor_01", FR_COUCH_SRC[s][0]
        elif kind == "bed":         # MRI table: our own seats on the measured table (MRI_SEATS)
            j = DECOR_BASE + _DECOR_POS[(sh, s)]
            blocks.append("        /* %s_%d (MRI table seats, medical %d) */\n        %s"
                          % (ICESHELL_TILESET, j, s, _seat_block(j % cols, j // cols, MRI_SEATS[s])))
            continue
        else:
            continue
        key = (src_file, src_set)
        if key not in src_cache:
            src_cache[key] = _seating_tiles(src_file, src_set)
        block = src_cache[key].get((src_i % 8, src_i // 8))
        if not block:
            raise RuntimeError("no seating data for %s_%d in %s" % (src_set, src_i, src_file))
        j = DECOR_BASE + _DECOR_POS[(sh, s)]
        block = _re.sub(r"xy\s*=\s*\d+\s+\d+", "xy = %d %d" % (j % cols, j // cols), block, count=1)
        blocks.append("        /* %s_%d (seat of %s_%d) */\n        %s" % (ICESHELL_TILESET, j, src_set, src_i, block.strip()))
    if not blocks:
        return 0
    os.makedirs(common_media_dir, exist_ok=True)
    out = os.path.join(common_media_dir, "seating.txt")
    open(out, "w", encoding="utf-8").write(
        "seating\n{\n    VERSION = 3,\n    tileset\n    {\n        name = %s,\n%s\n    }\n}\n"
        % (ICESHELL_TILESET, "\n".join(blocks)))
    return len(blocks)


_COUCH_RECUT = {}


def couch_recut_art(cache):
    """{Future couch tile: re-cut RGBA art} (user 2026-08-28: dithered seam once built, the ghost
    fine). The pack's two tiles of each couch OVERLAP (~1500-1700 px drawn by both) and split the
    art elsewhere than the square boundary; each tile is depth-sorted on its own square, so the
    shared pixels z-fought. Re-cut like vanilla: composite the pair as the ghost draws it (back tile
    first), then give every pixel to ONE tile: the one the vanilla Red Comfy couch draws there,
    else the nearest such tile. Same picture, no overlap, seam on vanilla's line."""
    if _COUCH_RECUT:
        return _COUCH_RECUT
    import numpy as np
    from PIL import Image as _Im
    pairs = {}
    for s in FR_COUCH:
        pairs.setdefault(FR_COUCH_SRC[s][0] // 2, []).append(s)
    need = {"furniture_seating_indoor_01_%d" % FR_COUCH_SRC[s][0] for s in FR_COUCH}
    if not all(os.path.isfile(os.path.join(cache, n + ".png")) for n in need):
        _extract_from_pack(_VANILLA_TILES2X_PACK, need, cache)
    W, H = 128 * 3, 256 + 64
    for ss in pairs.values():
        def frame(s):
            gx, gy = (int(v) for v in FR_COUCH_SRC[s][1].split(","))
            return 128 + (gx - gy) * 64, (gx + gy) * 32, gx + gy
        order = sorted(ss, key=lambda s: frame(s)[2])            # back tile first, like the ghost
        comp = _Im.new("RGBA", (W, H), (0, 0, 0, 0))
        van = {}
        for s in order:
            ox, oy, _d = frame(s)
            comp.alpha_composite(_Im.open(os.path.join(cache, "%s_%d.png" % (FR_SHEET, s))).convert("RGBA"), (ox, oy))
            v = np.zeros((H, W), bool)
            v[oy:oy + 256, ox:ox + 128] = np.array(_Im.open(os.path.join(
                cache, "furniture_seating_indoor_01_%d.png" % FR_COUCH_SRC[s][0])).convert("RGBA"))[:, :, 3] > 0
            van[s] = v
        # owner label per pixel: vanilla's tile there (front tile wins a shared pixel), then grow
        label = np.full((H, W), -1, int)
        for n, s in enumerate(order):
            label[van[s]] = n
        for _ in range(W + H):
            if (label >= 0).all():
                break
            grown = False
            for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                src = np.roll(label, (dy, dx), axis=(0, 1))
                if dy == 1: src[0, :] = -1
                if dy == -1: src[-1, :] = -1
                if dx == 1: src[:, 0] = -1
                if dx == -1: src[:, -1] = -1
                take = (label < 0) & (src >= 0)
                if take.any():
                    label[take] = src[take]
                    grown = True
            if not grown:
                break
        # a pixel can only go to a tile whose 128x256 frame contains it (else it would be cropped)
        inframe = []
        for s in order:
            ox, oy, _d = frame(s)
            f = np.zeros((H, W), bool)
            f[oy:oy + 256, ox:ox + 128] = True
            inframe.append(f)
        for n in range(len(order)):
            bad = (label == n) & ~inframe[n]
            label[bad] = 1 - n
        c = np.array(comp)
        lost = (c[:, :, 3] > 0) & ~np.logical_or.reduce([(label == n) & inframe[n] for n in range(len(order))])
        if lost.any():
            raise RuntimeError("couch re-cut would drop %d px" % int(lost.sum()))
        for n, s in enumerate(order):
            ox, oy, _d = frame(s)
            mine = c.copy()
            mine[label != n] = 0
            _COUCH_RECUT[s] = _Im.fromarray(mine[oy:oy + 256, ox:ox + 128].copy(), "RGBA")
    return _COUCH_RECUT


def _mask_depth(cell, art):
    """Depth cell with every pixel outside `art`'s drawn pixels (alpha 0) cleared."""
    import numpy as np
    from PIL import Image as _Im
    d = np.array(cell.convert("RGBA"))
    d[np.array(art.convert("RGBA"))[:, :, 3] == 0] = 0
    return _Im.fromarray(d, "RGBA")


def _fill_depth_holes(cell, art, max_steps=128):
    """Depth cell (RGBA) where every art pixel (alpha > 0) with no depth (alpha 0) gets the depth
    of the nearest pixel that has one (grown one pixel ring per step, 4-neighbour)."""
    import numpy as np
    from PIL import Image as _Im
    orig = np.array(cell.convert("RGBA"))
    d = orig.copy()
    want = np.array(art.convert("RGBA"))[:, :, 3] > 0
    have0 = d[:, :, 3] > 0
    have = have0.copy()
    # grow through the whole cell (art islands can sit apart from the shape), apply to art only
    for _ in range(max_steps):
        if not (want & ~have).any():
            break
        hole = ~have
        grown = False
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            src_have = np.roll(have, (dy, dx), axis=(0, 1))
            src_val = np.roll(d, (dy, dx), axis=(0, 1))
            # np.roll wraps: never take a value across the cell border
            if dy == 1: src_have[0, :] = False
            if dy == -1: src_have[-1, :] = False
            if dx == 1: src_have[:, 0] = False
            if dx == -1: src_have[:, -1] = False
            take = hole & src_have
            if take.any():
                d[take] = src_val[take]
                have = have | take
                hole = hole & ~take
                grown = True
        if not grown:
            break
    if (want & ~have).any():
        raise RuntimeError("depth cell has art pixels with no depth to grow from")
    keep = ~(want & ~have0)               # only the art holes take a grown value
    d[keep] = orig[keep]
    return _Im.fromarray(d, "RGBA")


def _vanilla_depth_cell_index(sheet, idx):
    """The depth cell vanilla draws <sheet>_<idx> with (tileDepthTextureAssignments, else its own)."""
    if os.path.isfile(_VANILLA_DEPTH_ASSIGN):
        key = "%s_%d" % (sheet, idx)
        for line in open(_VANILLA_DEPTH_ASSIGN, encoding="utf-8", errors="replace"):
            parts = line.strip().rstrip(",").split("=")
            if len(parts) == 2 and parts[0].strip() == key:
                target = parts[1].strip()
                if target.startswith(sheet + "_"):
                    return int(target.rsplit("_", 1)[1])
                return None
    return idx


def write_iceshell_assets(media_dir, common_media_dir=None, include_fridges=False):
    """Inert shell tiles (stage 1 of two-stage appliances): texture pack + tiledef in <media_dir>.
    0..3 = TK ice machine. With include_fridges: 4..43 = vanilla 1-tile fridges / chest freezer,
    plus a depth map for those cells in <common_media_dir>/depthmaps (needs
    common/media/tileGeometry.txt)."""
    from PIL import Image
    cache = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_cache_iceshell")
    names = {"%s_%d" % (_ICESHELL_SRC_SHEET, s) for s in _ICESHELL_SRC}
    _extract_from_pack(_TK_PACK, names, cache)
    _ver, tilesets = _load_community_tilesets()
    src = tilesets[_ICESHELL_SRC_SHEET.encode()]
    tiles, props = [], []
    for j, s in enumerate(_ICESHELL_SRC):
        im = Image.open(os.path.join(cache, "%s_%d.png" % (_ICESHELL_SRC_SHEET, s))).convert("RGBA")
        tiles.append(("%s_%d" % (ICESHELL_TILESET, j), im))
        p = []
        for k, v in _patched_props(_ICESHELL_SRC_SHEET, s, src[6][s]):
            if k == b"CustomName":
                v = b"Ice Machine Shell"
            p.append((k, v))
        props.append(p)
    if include_fridges:
        fnames = {"%s_%d" % (_FRIDGE_SHEET, s) for s in _FRIDGE_SRC}
        _extract_from_pack(_VANILLA_TILES2X_PACK, fnames, cache)
        _v, vts, _o = _parse(open(_VANILLA_TILES, "rb").read())
        vsrc = vts[_FRIDGE_SHEET.encode()]
        for s in _FRIDGE_SRC:
            im = Image.open(os.path.join(cache, "%s_%d.png" % (_FRIDGE_SHEET, s))).convert("RGBA")
            tiles.append(("%s_%d" % (ICESHELL_TILESET, len(tiles)), im))
            shell = b"Freezer Shell" if s in _FREEZER_SRC else b"Refrigerator Shell"
            # also drop every fridge/freezer marker (IsFridge, FreezerPosition, ...): an inert shell
            # must not count as a powered appliance
            p = [(k, shell if k == b"CustomName" else v) for k, v in vsrc[6][s]
                 if k not in _SHELL_DROP and b"Fridge" not in k and b"Freezer" not in k]
            props.append(p)
    for p in props:
        bad = {b"Freezer", b"FreezerCapacity", b"container", b"ContainerCapacity", b"IsFridge",
               b"IsMoveAble"} & {k for k, _ in p}
        if bad:
            raise RuntimeError("shell tile would be a container / appliance: %s" % bad)
    if include_fridges:
        # hand-pump sinks at fixed indices PUMP_SINK_BASE.. (see PUMP_SINK_SRC)
        if len(props) > PUMP_SINK_BASE:
            raise RuntimeError("ice-shell tiles reach %d; pump sinks start at %d" % (len(props), PUMP_SINK_BASE))
        props += [[] for _ in range(PUMP_SINK_BASE - len(props))]
        snames = {"%s_%d" % (PUMP_SINK_SHEET, s) for s in PUMP_SINK_SRC}
        _extract_from_pack(_VANILLA_TILES2X_PACK, snames, cache)
        ssrc = vts[PUMP_SINK_SHEET.encode()]
        for s in PUMP_SINK_SRC:
            src_props = ssrc[6][s]
            if not any(k == b"IsTableTop" for k, _v in src_props):
                raise RuntimeError("%s_%d is not a counter-top sink" % (PUMP_SINK_SHEET, s))
            im = Image.open(os.path.join(cache, "%s_%d.png" % (PUMP_SINK_SHEET, s))).convert("RGBA")
            tiles.append((pump_sink_name(s), im))
            props.append(_pump_sink_props(src_props))
        # Dirkies decor-house copies at fixed indices DECOR_BASE.. (ladders, ladder tops, red cabinet)
        if len(props) > DECOR_BASE:
            raise RuntimeError("ice-shell tiles reach %d; decor copies start at %d" % (len(props), DECOR_BASE))
        props += [[] for _ in range(DECOR_BASE - len(props))]
        _copy_pack = {GUN_SHEET: _GUN_PACK, FR_SHEET: _GUN_PACK}
        for pk in {_copy_pack.get(sh, _DECOR_PACK) for sh, _s, _e, _k, _g in DECOR_COPIES}:
            _extract_from_pack(pk, {"%s_%d" % (sh, _src_index(s)) for sh, s, _e, _k, _g in DECOR_COPIES
                                    if _copy_pack.get(sh, _DECOR_PACK) == pk}, cache)
        from PIL import ImageOps as _IO
        for entry in DECOR_COPIES:
            sh, s = entry[0], entry[1]
            im = Image.open(os.path.join(cache, "%s_%d.png" % (sh, _src_index(s)))).convert("RGBA")
            if _mirrored(s):
                im = _IO.mirror(im)
            if entry[3] == "centerpot":
                # the pack has a stray pixel at y 23 above every pot: clear rows above 64 first
                im.paste((0, 0, 0, 0), (0, 0, im.size[0], 64))
                bb = im.split()[3].point(lambda v: 255 if v > 40 else 0).getbbox()
                _DECOR_SHIFT[(sh, s)] = (64 - (bb[0] + bb[2]) // 2, POT_BOTTOM - bb[3])
            if (sh, s) in _DECOR_SHIFT:
                im = _shift(im, *_DECOR_SHIFT[(sh, s)])
            if entry[3] == "couch":     # re-cut on vanilla's seam, no overlap (couch_recut_art)
                im = couch_recut_art(cache)[s]
            tiles.append((decor_copy_name(s, sh), im))
            props.append(_decor_props(entry, tilesets[sh.encode()][6][_src_index(s)]))
        # 2nd Wall Screen TV copies + their screens at fixed indices (see WALLTV_BASE)
        if len(props) > WALLTV_BASE:
            raise RuntimeError("decor copies reach %d; the wall TVs start at %d" % (len(props), WALLTV_BASE))
        walltv = _walltv_tiles(cache)
        for j in sorted(walltv):
            props += [[] for _ in range(j - len(props))]
            name, im, p = walltv[j]
            tiles.append((name, im))
            props.append(p)
    n = _write_pack(os.path.join(media_dir, "texturepacks", ICESHELL_PACK + ".pack"), ICESHELL_PACK + "0", tiles)
    cols = 8
    # from the highest index used (props), not the tile count: the pump sinks sit at fixed indices
    # after padding, so there are fewer tiles than cells
    rows = (len(props) + cols - 1) // cols
    props += [[] for _ in range(cols * rows - len(props))]
    ts = [ICESHELL_TILESET.encode(), (ICESHELL_TILESET + ".png").encode(), cols, rows, 1, cols * rows, props]
    blob = b"tdef" + struct.pack("<ii", 1, 1) + _ser_tileset(ts)
    _parse(blob)
    open(os.path.join(media_dir, ICESHELL_TILEDEF_NAME + ".tiles"), "wb").write(blob)
    if include_fridges and common_media_dir and os.path.isfile(_VANILLA_DEPTH_REFRIG):
        depth_src = Image.open(_VANILLA_DEPTH_REFRIG).convert("RGBA")
        cw, ch = 128, 256
        depth = Image.new("RGBA", (cols * cw, rows * ch), (0, 0, 0, 0))
        for j, s in enumerate(_FRIDGE_SRC):
            sx, sy = (s % 8) * cw, (s // 8) * ch
            dj = 4 + j
            depth.paste(depth_src.crop((sx, sy, sx + cw, sy + ch)), ((dj % cols) * cw, (dj // cols) * ch))
        # pump sinks: the depth cell vanilla draws each source sink with
        if os.path.isfile(_VANILLA_DEPTH_SINKS):
            sink_depth = Image.open(_VANILLA_DEPTH_SINKS).convert("RGBA")
            scols = sink_depth.size[0] // cw
            for s in PUMP_SINK_SRC:
                c = _vanilla_depth_cell_index(PUMP_SINK_SHEET, s)
                if c is None:
                    continue
                sx, sy = (c % scols) * cw, (c // scols) * ch
                dj = PUMP_SINK_BASE + PUMP_SINK_SRC.index(s)
                depth.paste(sink_depth.crop((sx, sy, sx + cw, sy + ch)), ((dj % cols) * cw, (dj // cols) * ch))
        # decor-house copies: the Community pack's own depth cells for the source tiles
        _ddepth = {}
        _couch_depth = None
        for sh, s, _e, _k, _g in DECOR_COPIES:
            if _k == "couch":
                # Future couch (user, 2026-08-28: the pack's depth drew the backrest over a resting
                # player). Its seat positions are the vanilla Red Comfy couch's, so it uses that
                # couch's depth cells too (furniture_seating_indoor_01, same facing + grid position).
                if _couch_depth is None:
                    _couch_depth = Image.open(_VANILLA_DEPTH_SEATING).convert("RGBA")
                vi = _vanilla_depth_cell_index("furniture_seating_indoor_01", FR_COUCH_SRC[_src_index(s)][0])
                if vi is None:
                    raise RuntimeError("no vanilla depth cell for couch tile %d" % s)
                vcols = _couch_depth.size[0] // cw
                sx, sy = (vi % vcols) * cw, (vi // vcols) * ch
                dj = DECOR_BASE + _DECOR_POS[(sh, s)]
                cell = _couch_depth.crop((sx, sy, sx + cw, sy + ch))
                # The vanilla cell also holds the FLOOR / shadow under the vanilla couch (ground
                # depth). Future art pixels past the vanilla shape landed on it and z-fought the
                # ground (user 2026-08-28: dithered seam between the two tiles), or had no depth at
                # all (gaps). So: keep vanilla depth only where the vanilla couch art is drawn, then
                # give every other Future art pixel the depth of the nearest couch-body pixel.
                vn = "furniture_seating_indoor_01_%d" % vi
                if not os.path.isfile(os.path.join(cache, vn + ".png")):
                    _extract_from_pack(_VANILLA_TILES2X_PACK, {vn}, cache)
                van = Image.open(os.path.join(cache, vn + ".png")).convert("RGBA")
                cell = _mask_depth(cell, van)
                cell = _fill_depth_holes(cell, couch_recut_art(cache)[s])
                depth.paste(cell, ((dj % cols) * cw, (dj // cols) * ch))
                continue
            if sh not in _ddepth:
                p = _decor_depth_png(sh)
                _ddepth[sh] = Image.open(p).convert("RGBA") if os.path.isfile(p) else None
            ddepth = _ddepth[sh]
            if ddepth is None:
                continue
            dcols = ddepth.size[0] // cw
            si = _src_index(s)
            sx, sy = (si % dcols) * cw, (si // dcols) * ch
            if sy + ch > ddepth.size[1]:
                continue
            dj = DECOR_BASE + _DECOR_POS[(sh, s)]
            cell = ddepth.crop((sx, sy, sx + cw, sy + ch))
            if _mirrored(s):
                from PIL import ImageOps as _IO2
                cell = _IO2.mirror(cell)
            if (sh, s) in _DECOR_SHIFT:
                cell = _shift(cell, *_DECOR_SHIFT[(sh, s)])   # depth follows the moved art
            if _k in FILL_DEPTH_KINDS:      # art pixels outside the depth shape would be hidden
                art = Image.open(os.path.join(cache, "%s_%d.png" % (sh, si))).convert("RGBA")
                if _mirrored(s):
                    from PIL import ImageOps as _IO3
                    art = _IO3.mirror(art)
                if (sh, s) in _DECOR_SHIFT:
                    art = _shift(art, *_DECOR_SHIFT[(sh, s)])
                cell = _fill_depth_holes(cell, art)
            depth.paste(cell, ((dj % cols) * cw, (dj // cols) * ch))
        # Future upper cabinets: vanilla's floating-cabinet box, filled under the Future art
        # (user 2026-11-13: the Wall Screen TV drew over the cabinet hung above it; neither had depth)
        _ucab = Image.open(os.path.join(os.path.dirname(_VANILLA_DEPTH_REFRIG),
                                        "DEPTH_%s.png" % _UPPERCAB_DEPTH[0])).convert("RGBA")
        ui = _vanilla_depth_cell_index(*_UPPERCAB_DEPTH)
        ucols = _ucab.size[0] // cw
        ucell = _ucab.crop(((ui % ucols) * cw, (ui // ucols) * ch, (ui % ucols) * cw + cw, (ui // ucols) * ch + ch))
        for s in FR_UPPER:
            art = Image.open(os.path.join(cache, "%s_%d.png" % (FR_SHEET, _src_index(s)))).convert("RGBA")
            if _mirrored(s):
                art = _IO.mirror(art)
            dj = DECOR_BASE + _DECOR_POS[(FR_SHEET, s)]
            depth.paste(_fill_depth_holes(ucell, art), ((dj % cols) * cw, (dj // cols) * ch))
        # 2nd Wall Screen TVs: the wall preset (like vanilla wall detailing); each screen uses its
        # TV's cell, as vanilla's appliances_television_01 screens do
        for n, (s, edge) in enumerate(WALLTV):
            idx = [WALLTV_BASE + n] + [WALLTV_BASE + n + 16 * (k + 1) for k in range(3)]
            art = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
            for j in idx:
                art.alpha_composite(walltv[j][1])
            cell = _wall_plane_depth(edge, art, _WALLTV_DEPTH_BIAS)
            for j in idx:
                depth.paste(cell, ((j % cols) * cw, (j // cols) * ch))
        os.makedirs(os.path.join(common_media_dir, "depthmaps"), exist_ok=True)
        depth.save(os.path.join(common_media_dir, "depthmaps", "DEPTH_%s.png" % ICESHELL_TILESET))
        # seat positions for the wheelchair copies (Rest / sit animation)
        write_decor_seating(common_media_dir, cols)
    return n


def add_case_mirror_faces(buildable):
    """Give the green/white military cases (and their .crate versions) the generated second face.
    Their one pack face is 'W'; the mirror becomes 'N'. In place; returns True if changed."""
    changed = False
    src_names = {"%s_%d" % (_CASES_SRC_SHEET, s): cases_mirror_name(s) for s in _CASES_MIRRORS}
    stage_lists = [buildable.get("stages") or []]
    for v in buildable.get("variants") or []:
        stage_lists.append(v.get("stages") or [])
    for stages in stage_lists:
        for st in stages:
            faces = ((st.get("geometry") or {}).get("faces")) or {}
            w = faces.get("W")
            if not w or "N" in faces:
                continue
            sprites = [c for L in w.get("layers", []) for row in L.get("rows", []) for c in row]
            if len(sprites) != 1 or sprites[0] not in src_names:
                continue
            faces["N"] = {"layers": [{"rows": [[src_names[sprites[0]]]]}]}
            changed = True
    return changed


# ---------------------------------------------------------------------------------------------
# SEATING FIXES (runtime Lua)
# B42 Rest / Get on bed / sit animations read per-tile positions from each mod's seating.txt.
# Merging is FIRST-WINS per tile (SeatingFile$Tileset.merge skips a tile that already has
# positions), so a seating.txt of ours cannot override another pack's entry. Instead we edit that
# pack's in-memory seating data the way the vanilla TileGeometryEditor does
# (removeTilePosition / addTilePosition / getTilePositionTranslate():set / setTilePositionProperty),
# copying positions from a matching vanilla tile (modID "game"), then call mergeAfterEditing().
# Nothing is written to disk.
#
# (target modID, target tileset, source tileset, [(target index, source index), ...])
_SEATING_FIXES = [
    # Drazion's tterika double bed ships placeholder data: every tile has one S seat at 0,0,0,
    # so Rest sits you inside the bed facing south. All four facings (16-19 W, 20-23 N, 24-27 S,
    # 28-31 E) match vanilla "Large Modern" (furniture_bedding_01_16-31) tile for tile (same
    # Facing + SpriteGridPos). (First pass only covered 16-23; KBW's N/W faces use 24-31.)
    ("tikitown_tiles", "furniture_bedding_tterika_01", "furniture_bedding_01",
     [(i, i) for i in range(16, 32)]),
]

_SEATING_LUA = r'''-- AUTO-GENERATED by pz_craft_loops/kbw_tilepatch.py -- do not edit by hand.
-- Replaces broken seating positions (Rest / Get on bed) in other packs' in-memory seating data
-- with positions copied from matching vanilla tiles. Seating merge is first-wins per tile, so a
-- seating.txt of ours could not override these. Nothing is written to disk.
local FIXES = {
%(rows)s
}
local PROPS = { "BlockLeft", "BlockRight" }

local function colRow(i) return i %% 8, math.floor(i / 8) end

local function apply(source)
    local sm = SeatingManager and SeatingManager.getInstance and SeatingManager.getInstance()
    if not sm then return end
    local fixed, failed = 0, 0
    for _, f in ipairs(FIXES) do
        local mod, dst, src = f[1], f[2], f[3]
        for _, pair in ipairs(f[4]) do
            local ok, err = pcall(function()
                local dc, dr = colRow(pair[1])
                local sc, sr = colRow(pair[2])
                local n = sm:getTilePositionCount("game", src, sc, sr)
                if n <= 0 then error("vanilla tile has no positions") end
                for i = sm:getTilePositionCount(mod, dst, dc, dr) - 1, 0, -1 do
                    sm:removeTilePosition(mod, dst, dc, dr, i)
                end
                for i = 0, n - 1 do
                    local id = sm:getTilePositionID("game", src, sc, sr, i)
                    local idx = sm:addTilePosition(mod, dst, dc, dr, id)
                    sm:getTilePositionTranslate(mod, dst, dc, dr, idx):set(sm:getTilePositionTranslate("game", src, sc, sr, i))
                    for _, p in ipairs(PROPS) do
                        local v = sm:getTilePositionProperty("game", src, sc, sr, i, p)
                        if v then sm:setTilePositionProperty(mod, dst, dc, dr, idx, p, v) end
                    end
                end
            end)
            if ok then fixed = fixed + 1 else
                failed = failed + 1
                print("[KBWCommunitySeating] " .. dst .. "_" .. tostring(pair[1]) .. " failed: " .. tostring(err))
            end
        end
    end
    pcall(function() sm:mergeAfterEditing() end)
    print(string.format("[KBWCommunitySeating] %%s: fixed=%%d failed=%%d", tostring(source), fixed, failed))
end

local done = false
local function once(source)
    if done then return end
    done = true
    apply(source)
end
if Events.OnGameStart then Events.OnGameStart.Add(function() once("OnGameStart") end) end
if Events.OnServerStarted then Events.OnServerStarted.Add(function() once("OnServerStarted") end) end
'''


def write_seating_lua(dest_path):
    rows = []
    for mod, dst, src, pairs in _SEATING_FIXES:
        rows.append('    { "%s", "%s", "%s", { %s } },' % (mod, dst, src, ", ".join("{ %d, %d }" % p for p in pairs)))
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    open(dest_path, "w", encoding="utf-8").write(_SEATING_LUA % {"rows": "\n".join(rows)})
    return len(rows)


# ---------------------------------------------------------------------------------------------
# TABLE-TOP HEIGHT FIX (runtime Lua)
# Table-top tiles with IsSurfaceOffset are drawn already raised to counter height (Surface). Vanilla
# placement sets renderYOffset = (height of the table underneath) - Surface: 0 on a counter, -Surface
# on the floor. In game our coffee makers stayed at counter height on the floor (confirmed by
# screenshot). Root cause: they are IsoStove sprites, so KBW builds them with its native "stove"
# builder (checked before isProp), which never sets the offset. We recompute it after KBW's
# NativeObjectFactory.finalize, after vanilla placeMoveableInternal (pick up / place), and on load.
_TABLETOP_SPRITES = ["kitchen_misc_tk_01_%d" % i for i in list(range(0, 4)) + list(range(24, 32))]
# TikiTown props-14 table-top pieces (desk mic 0-3, small mixer 4-7, large mixer 12-15, cups 23/31,
# thermos coffee dispenser 27-30): same bug, floated at counter height on the floor (in game
# 2026-08-28). Shipped in the TikiTown submod as its OWN file (KBWTikiTown_TableTop.lua, own guard
# flags): KBWCommunity_TableTop.lua is WE-owned (WE's copy only runs with the Community submod).
TT_TABLETOP_SPRITES = ["tikitown-props-14_%d" % i
                       for i in list(range(0, 8)) + list(range(12, 16)) + [23] + list(range(27, 32))]
# 2026-08-28 (user: "a common bug we should just account for"): every table-top piece we add goes on
# these lists. props-14 terrarium 90-93 + Mahjong 104-105 (pack table-top flags); the Dirkies
# medical centrifuge / analyzer / specimen cabinet copies (flags added on the copies, MED_TABLETOP).
TT_TABLETOP_SPRITES += ["tikitown-props-14_%d" % i for i in (90, 91, 92, 93, 104, 105)]
# (the medical centrifuge / analyzer copies are no longer built, user 2026-08-28: off the list)
TABLETOP_DECOR = []
_add_future_room_tvs()      # Future Room wall-TV copies get generated screens (append-only)
_TABLETOP_SPRITES += TABLETOP_DECOR


def sync_we_tabletop_sprites(we_base_lua):
    """Add every sprite of our two table-top lists to the SPRITES table of World Essentials' own
    KBWCommunity_TableTop.lua (WE-owned; our WORK copy only). Returns the sprites added. Lines WE
    already has stay as they are; the hand-off notes must flag the change to the WE dev."""
    import re as _re
    raw = open(we_base_lua, "rb").read().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    txt = raw.replace("\r\n", "\n")
    m = _re.search(r"local SPRITES = \{\n(.*?)\n\}", txt, _re.S)
    if not m:
        raise RuntimeError("SPRITES table not found in %s" % we_base_lua)
    want = TT_TABLETOP_SPRITES + _TABLETOP_SPRITES
    have = set(_re.findall(r'\["([^"]+)"\]\s*=\s*true', m.group(1)))
    add = [s for s in want if s not in have]
    # our own copies that are no longer table-top pieces (e.g. the specimen cabinet) come off the list
    stale = [s for s in have if s.startswith(ICESHELL_TILESET + "_") and s not in want]
    if add or stale:
        lines = [l for l in m.group(1).split("\n")
                 if not any('["%s"]' % s in l for s in stale)]
        block = "\n".join(lines + ['    ["%s"] = true,' % s for s in add])
        txt = txt[:m.start(1)] + block + txt[m.end(1):]
        open(we_base_lua, "wb").write(txt.replace("\n", nl).encode("utf-8"))
    return add + ["-" + s for s in stale]

_TABLETOP_LUA = r'''-- AUTO-GENERATED by pz_craft_loops/kbw_tilepatch.py -- do not edit by hand.
-- Keeps our counter-top appliances (coffee makers, slicer) at the right height: on a counter
-- they sit on its top, on the floor they sit on the floor. Same formula as vanilla
-- ISMoveableSpriteProps:placeMoveableInternal (table height - Surface for IsSurfaceOffset tiles).
local SPRITES = {
%(rows)s
}

local function tableHeightUnder(obj)
    local sq = obj and obj:getSquare()
    if not sq then return 0 end
    local objs = sq:getObjects()
    for i = objs:size() - 1, 0, -1 do
        local o = objs:get(i)
        if o ~= obj then
            local spr = o:getSprite()
            local p = spr and spr:getProperties()
            if p and p:has("IsTable") and p:has("Surface") and tonumber(p:get("Surface")) then
                return o:getRenderYOffset() + tonumber(p:get("Surface"))
            end
        end
    end
    return 0
end

local function fixHeight(obj, source)
    local spr = obj and obj.getSprite and obj:getSprite()
    local name = spr and spr:getName()
    if not name or not SPRITES[name] then return end
    local p = spr:getProperties()
    if not p:has("IsTableTop") then return end
    local want = tableHeightUnder(obj)
    if p:has("IsSurfaceOffset") and p:has("Surface") and tonumber(p:get("Surface")) then
        want = want - tonumber(p:get("Surface"))
    end
    local have = obj:getRenderYOffset()
    if math.abs(have - want) > 0.5 then
        obj:setRenderYOffset(want)
        if isServer() and obj.transmitUpdatedSpriteToClients then obj:transmitUpdatedSpriteToClients() end
        print(string.format("[%(tag)s] %%s: %%s offset %%.1f -> %%.1f", tostring(source), name, have, want))
    end
end

local function install()
    if not ISMoveableSpriteProps or ISMoveableSpriteProps.%(flag)s then return end
    local orig = ISMoveableSpriteProps.placeMoveableInternal
    if type(orig) ~= "function" then return end
    ISMoveableSpriteProps.placeMoveableInternal = function(self, character, square, item, spriteName)
        local obj = orig(self, character, square, item, spriteName)
        if spriteName and SPRITES[spriteName] and square then
            pcall(function()
                local objs = square:getObjects()
                for i = objs:size() - 1, 0, -1 do
                    local o = objs:get(i)
                    if o:getSprite() and o:getSprite():getName() == spriteName then fixHeight(o, "placed"); break end
                end
            end)
        end
        return obj
    end
    ISMoveableSpriteProps.%(flag)s = true
    print("[%(tag)s] hooked placeMoveableInternal")
end

-- Coffee makers are IsoType=IsoStove, and KBW resolves any IsoStove sprite to its native "stove"
-- builder BEFORE it looks at object.isProp (KBWBuildingObject.lua: NativeObjectFactory.resolve is
-- checked first). That builder never applies the table-top offset, so the object is left at 0:
-- right on a counter (the art is drawn raised), floating on the floor. placeMoveableInternal is
-- never called on that path, so we also wrap KBW's NativeObjectFactory.finalize, which runs right
-- after the object enters the square. Wrapped in memory only; KBW's files are not edited.
local function hookFinalize(source)
    local okR, NOF = pcall(require, "KnoxBuildworks/BuildingObjects/NativeObjectFactory")
    if not okR or type(NOF) ~= "table" or type(NOF.finalize) ~= "function" then return end
    if NOF.%(flag)sHooked then return end
    local orig = NOF.finalize
    NOF.finalize = function(object, state, square, ...)
        local r = orig(object, state, square, ...)
        pcall(fixHeight, object, "built")
        return r
    end
    NOF.%(flag)sHooked = true
    print("[%(tag)s] hooked KBW NativeObjectFactory.finalize (" .. tostring(source) .. ")")
end

install()
if Events.OnGameStart then Events.OnGameStart.Add(install) end
if Events.OnGameStart then Events.OnGameStart.Add(function() hookFinalize("OnGameStart") end) end
if Events.OnServerStarted then Events.OnServerStarted.Add(function() hookFinalize("OnServerStarted") end) end
-- Placed appliances as their squares load: through the shared dispatcher (only our 12 sprites).
%(loadgrid)s
KBWCommunityLoadGrid.register(SPRITES, fixHeight)
'''


# ---------------------------------------------------------------------------------------------
# MULTI-STOREY WALL PIECES (runtime Lua)
# Two-storey fences (Dirkies louvered) put their top tile one level up (geometry layer 2, dz=1).
# KBW Placement.validate runs the wall-support test on EVERY wall tile of the footprint; the top
# square has no floor, so it needs an existing wall directly below it - the base we are building in
# the same action - and fails with "wall support missing". We wrap Placement.validate (in memory,
# KBW untouched): for our multi-level buildables, when that is the only problem, re-validate with the
# ground-level tiles only, then require each upper square's edge to be free of another wall.
_MULTISTOREY_LUA = r'''-- AUTO-GENERATED by pz_craft_loops/kbw_tilepatch.py -- do not edit by hand.
-- Lets our two-storey wall pieces (base + top one level up) pass KBW's wall-support check.
local PREFIXES = { "community." }

local function isOurs(id)
    if type(id) ~= "string" then return false end
    for _, p in ipairs(PREFIXES) do
        if id:sub(1, #p) == p then return true end
    end
    return false
end

local function edgeTaken(sq, north)
    if not sq then return false end
    local p = sq:getProperties()
    if north then
        return p:has(IsoFlagType.WallN) or p:has(IsoFlagType.WallNTrans) or p:has(IsoFlagType.WallNW)
    end
    return p:has(IsoFlagType.WallW) or p:has(IsoFlagType.WallWTrans) or p:has(IsoFlagType.WallNW)
end

local function install(source)
    local okR, Placement = pcall(require, "KnoxBuildworks/Validation/Placement")
    if not okR or type(Placement) ~= "table" or type(Placement.validate) ~= "function" then return end
    if Placement.__kbwCommunityMultiStorey then return end
    local orig = Placement.validate
    Placement.validate = function(cursor, square, ...)
        local ok, reason, previous = orig(cursor, square, ...)
        if ok or reason ~= "wall support missing" or not cursor or not cursor.definition
            or not isOurs(cursor.definition.id) or not cursor.getFootprint or not square then
            return ok, reason, previous
        end
        local full = cursor:getFootprint()
        if not full then return ok, reason, previous end
        local ground, upper = {}, {}
        for _, t in ipairs(full) do
            if (t.dz or 0) == 0 then ground[#ground + 1] = t else upper[#upper + 1] = t end
        end
        if #upper == 0 then return ok, reason, previous end
        rawset(cursor, "getFootprint", function() return ground end)
        local okG, ok2, reason2, previous2 = pcall(orig, cursor, square, ...)
        rawset(cursor, "getFootprint", nil)
        if not okG then return ok, reason, previous end
        if not ok2 then return ok2, reason2, previous2 end
        for _, t in ipairs(upper) do
            local sq = getCell():getGridSquare(square:getX() + (t.dx or 0), square:getY() + (t.dy or 0),
                square:getZ() + (t.dz or 0))
            if edgeTaken(sq, cursor.north == true) then return false, "wall already blocked" end
        end
        return true, nil, previous2
    end
    Placement.__kbwCommunityMultiStorey = true
    print("[KBWCommunityMultiStorey] wrapped KBW Placement.validate (" .. tostring(source) .. ")")
end

install("load")
if Events.OnGameStart then Events.OnGameStart.Add(function() install("OnGameStart") end) end
if Events.OnServerStarted then Events.OnServerStarted.Add(function() install("OnServerStarted") end) end
'''


# ---------------------------------------------------------------------------------------------
# WALL OVERLAY GUARD (runtime Lua)
# World Essentials builds every WallOverlay tile as a wall attachment and, right before the build,
# requires WorldEssentialsKnoxNative.ValidateWallOverlay (ConstructionPlan.lua). KBW's own overlay
# cursor accepts more hosts (window walls, door walls), so a ghost could go green and the build
# then threw "attachment support changed" -> error screen (soundproofing test, 2026-08-28).
# This wraps KBW Placement.validate: for our buildables, every WallOverlay tile of the footprint must
# also pass WE's check at the cursor, so an invalid spot simply shows red. No-op without WE.
_OVERLAY_GUARD_LUA = r'''-- AUTO-GENERATED by pz_craft_loops/kbw_tilepatch.py -- do not edit by hand.
-- Our wall-overlay pieces only show a valid ghost where World Essentials will accept the build.
local PREFIXES = { "community.", "tikitown.", "worldessentials.tikitown." }

local function isOurs(id)
    if type(id) ~= "string" then return false end
    for index = 1, #PREFIXES do
        if string.find(id, PREFIXES[index], 1, true) == 1 then return true end
    end
    return false
end

-- exactly World Essentials' own test (ConstructionPlan.lua): a vanilla "WallOverlay" moveable, i.e.
-- IsMoveAble + MoveType WallObject + the WallOverlay flag. Non-movable overlays (Newburbs trim) are
-- built by plain KBW and are not checked by WE, so they are not checked here either.
local function isWallOverlay(spriteName)
    if not spriteName or not ISMoveableSpriteProps or not ISMoveableSpriteProps.new then return false end
    local okM, moveable = pcall(ISMoveableSpriteProps.new, spriteName)
    return okM and type(moveable) == "table" and moveable.type == "WallOverlay"
end

local function install(source)
    local okR, Placement = pcall(require, "KnoxBuildworks/Validation/Placement")
    if not okR or type(Placement) ~= "table" or type(Placement.validate) ~= "function" then return false end
    if Placement.__kbwCommunityOverlayGuard then return true end
    local orig = Placement.validate
    Placement.validate = function(cursor, square, ...)
        local ok, reason, previous = orig(cursor, square, ...)
        if not ok or not square or not cursor or not cursor.definition or not isOurs(cursor.definition.id) then
            return ok, reason, previous
        end
        local native = WorldEssentialsKnoxNative
        if type(native) ~= "table" or type(native.ValidateWallOverlay) ~= "function" then
            return ok, reason, previous
        end
        local okF, footprint = pcall(function() return cursor.getFootprint and cursor:getFootprint() end)
        if not okF or type(footprint) ~= "table" then return ok, reason, previous end
        for index = 1, #footprint do
            local tile = footprint[index]
            if tile and tile.sprite and isWallOverlay(tile.sprite) then
                local target = getCell():getGridSquare(square:getX() + (tile.dx or 0),
                    square:getY() + (tile.dy or 0), square:getZ() + (tile.dz or 0))
                if not target then return false, "wall required" end
                local params = { square = target, spriteName = tile.sprite, north = cursor.north,
                                 character = cursor.character }
                local okV, valid = pcall(native.ValidateWallOverlay, params)
                if not okV or not valid then return false, "wall required" end
            end
        end
        return ok, reason, previous
    end
    Placement.__kbwCommunityOverlayGuard = true
    print("[KBWCommunity] OverlayGuard: wall overlays checked against World Essentials at the cursor ("
        .. tostring(source) .. ")")
    return true
end

if not install("load") then
    if Events.OnGameStart then Events.OnGameStart.Add(function() install("OnGameStart") end) end
    if Events.OnServerStarted then Events.OnServerStarted.Add(function() install("OnServerStarted") end) end
end

-- Inside-corner pieces (Newburbs base trim corner, soundproof corner panel) are free-standing props
-- whose stage callbacks.onIsValid points here. KBW's own corner overlays (isCorner) only accept a
-- WallNW corner tile or a WallSE pillar, so they were refused where two plain walls meet. This
-- accepts a square with a wall edge on BOTH its west and north sides (plain, window or door wall;
-- a WallNW corner counts as both). Global, defined once; both submods ship the same code.
KBWCommunityCornerTrim = KBWCommunityCornerTrim or {}
local EDGE_FLAGS = {
    north = { "WallN", "WindowN", "DoorWallN", "WallNW" },
    west = { "WallW", "WindowW", "DoorWallW", "WallNW" },
}

local function propsHaveEdge(props, flags)
    if not props then return false end
    for index = 1, #flags do
        if props:has(flags[index]) then return true end
    end
    return false
end

local function squareHasEdge(square, flags)
    if propsHaveEdge(square:getProperties(), flags) then return true end
    local objects = square:getObjects()
    for index = 0, objects:size() - 1 do
        local object = objects:get(index)
        if object and propsHaveEdge(object:getProperties(), flags) then return true end
    end
    return false
end

function KBWCommunityCornerTrim.OnIsValid(params)
    local square = params and params.square
    if not square then return false end
    local ok, valid = pcall(function()
        return squareHasEdge(square, EDGE_FLAGS.north) and squareHasEdge(square, EDGE_FLAGS.west)
    end)
    return ok and valid == true
end

-- TikiTown lower walls (real walls, 40_tikitown_lower_walls.json) must not REPLACE a wall. KBW's
-- placement treats a player-built (IsoThumpable) wall on the same edge as the piece being upgraded
-- and swaps it out. These callbacks refuse any edge that already has a wall, window wall, door wall
-- or fence. Panel: the cursor's edge only. Corner: its sprite covers both edges, so both must be free.
-- Map walls were already refused by KBW ("wall already blocked"); this adds player-built ones.
KBWCommunityFreeEdge = KBWCommunityFreeEdge or {}
local BLOCK_FLAGS = {
    north = { "WallN", "WindowN", "DoorWallN", "HoppableN", "collideN", "WallNW" },
    west = { "WallW", "WindowW", "DoorWallW", "HoppableW", "collideW", "WallNW" },
}

function KBWCommunityFreeEdge.OnIsValid(params)
    local square = params and params.square
    if not square then return false end
    local ok, blocked = pcall(function()
        return squareHasEdge(square, params.north == true and BLOCK_FLAGS.north or BLOCK_FLAGS.west)
    end)
    return ok and blocked == false
end

function KBWCommunityFreeEdge.OnIsValidCorner(params)
    local square = params and params.square
    if not square then return false end
    local ok, blocked = pcall(function()
        return squareHasEdge(square, BLOCK_FLAGS.north) or squareHasEdge(square, BLOCK_FLAGS.west)
    end)
    return ok and blocked == false
end
-- Known, accepted (user, 2026-08-28): an overlay panel appears about a second after it is built.
-- KBW / WE attach its sprite to the host wall without marking the render chunk dirty. Deliberately
-- not patched here (a redraw hook on AttachedSprites.attach was tried and removed).
'''


def write_overlay_guard_lua(dest_path):
    for bad in ("next(", "goto ", "//", "debug."):
        if bad in _OVERLAY_GUARD_LUA.replace("-- AUTO-GENERATED", ""):
            raise RuntimeError("Kahlua-unsafe construct in overlay guard: %s" % bad)
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    open(dest_path, "w", encoding="utf-8", newline="\n").write(_OVERLAY_GUARD_LUA)


def write_multistorey_lua(dest_path):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    open(dest_path, "w", encoding="utf-8").write(_MULTISTOREY_LUA)


def write_tabletop_lua(dest_path, sprites=None, tag="KBWCommunityTableTop", flag="__kbwCommunityTableTop"):
    """Table-top height fix. Defaults = the Community file (output unchanged). The TikiTown submod
    ships its own copy (TT_TABLETOP_SPRITES, own tag + guard flag) so both hook independently."""
    rows = ['    ["%s"] = true,' % s for s in (sprites or _TABLETOP_SPRITES)]
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    open(dest_path, "w", encoding="utf-8").write(
        _TABLETOP_LUA % {"rows": "\n".join(rows), "loadgrid": _LOADGRID_LUA, "tag": tag, "flag": flag})


def write_tt_tabletop_lua(dest_path):
    write_tabletop_lua(dest_path, TT_TABLETOP_SPRITES, "KBWTikiTownTableTop", "__kbwTikiTownTableTop")


# ---------------------------------------------------------------------------------------------
# SLEDGEHAMMER DESTROY (runtime Lua)
# Vanilla ISDestroyCursor:canDestroy hard-refuses any sprite named d_*, e_*, f_* (meant for vanilla
# vegetation sheets) and anything flagged vegitation. Every Dirkies tile is d_*, so those builds
# could be dismantled but never destroyed. This wraps canDestroy: if vanilla says no, objects built
# from OUR buildables are re-checked with vanilla's remaining safety rules only.
_DESTROY_LUA = r'''-- AUTO-GENERATED by pz_craft_loops/kbw_tilepatch.py -- do not edit by hand.
-- Makes every buildable from our packs destroyable with a sledgehammer. Vanilla blocks sprites
-- named d_* / e_* / f_* and vegitation tiles outright; for objects built from our KBW buildables
-- only vanilla's other safety checks still apply.
local OUR_ID_PREFIXES = { "community.", "tikitown.", "worldessentials.tikitown." }

local function isOurs(object)
    if not object or not object.hasModData or not object:hasModData() then return false end
    local kbw = object:getModData().KBW
    local id = kbw and kbw.buildableId
    if type(id) ~= "string" then return false end
    for _, p in ipairs(OUR_ID_PREFIXES) do
        if string.sub(id, 1, #p) == p then return true end
    end
    return false
end

local function oursCanDestroy(self, object)
    local square = object:getSquare()
    if not square or not object:getSprite() then return false end
    if instanceof(object, "IsoWorldInventoryObject") or instanceof(object, "IsoTree") then return false end
    if self:isBasementWallAdjacentToTheVoid(object) then return false end
    -- no destroying a door-wall that still holds a door
    if self:_isDoorWallN(object) or self:_isDoorWallW(object) then
        local isNorth = self:_isDoorWallN(object)
        local objects = square:getObjects()
        for i = 1, objects:size() do
            local other = objects:get(i - 1)
            if other ~= object and ((isNorth and self:_isDoorN(other)) or (not isNorth and self:_isDoorW(other))) then
                return false
            end
        end
    end
    if object:getZ() > 0 and self:isFloorAtTopOfStairs(object) then return false end
    if not square:isCouldSee(self.player) then
        return self:couldSeeOpposite(object, square) == true
    end
    if object:getProperties() and object:getProperties():has(IsoFlagType.solidfloor) then
        return object:getZ() > 0
    end
    return true
end

local function install(source)
    if not ISDestroyCursor or type(ISDestroyCursor.canDestroy) ~= "function" then return end
    if ISDestroyCursor.__kbwCommunityDestroy then return end
    local orig = ISDestroyCursor.canDestroy
    ISDestroyCursor.canDestroy = function(self, object)
        if orig(self, object) then return true end
        if self.dismantle or not isOurs(object) then return false end
        local ok, res = pcall(oursCanDestroy, self, object)
        return ok and res == true
    end
    ISDestroyCursor.__kbwCommunityDestroy = true
    print("[KBWCommunityDestroy] sledgehammer support installed (" .. tostring(source) .. ")")
end

install("load")
if Events.OnGameStart then Events.OnGameStart.Add(function() install("OnGameStart") end) end
'''


def write_destroy_lua(dest_path):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    open(dest_path, "w", encoding="utf-8").write(_DESTROY_LUA)


def write_removal_lua(dest_path, tikitown=False, tikitown_only=False):
    """Emit the runtime removal script for every sprite in _PATCH_GROUPS that has removals
    (plus _TT_PATCH_GROUPS when tikitown=True)."""
    rows = []
    base_groups = [] if tikitown_only else _PATCH_GROUPS
    for tsname, idxs, _add, remove in base_groups + (_TT_PATCH_GROUPS if (tikitown or tikitown_only) else []):
        if not remove:
            continue
        keys = ", ".join('"%s"' % (k.decode() if isinstance(k, bytes) else k) for k in sorted(remove))
        for idx in sorted(idxs):
            rows.append('    { "%s_%d", { %s } },' % (tsname, idx, keys))
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    open(dest_path, "w", encoding="utf-8").write(_REMOVAL_LUA_TEMPLATE % {"rows": "\n".join(rows)})
    return len(rows)


if __name__ == "__main__":
    rep = write_community_tilepatch(r"c:\Users\josep\Kiro\pz_craft_loops\_kbw_tilepatch_selftest.tiles")
    print(rep)
    print("removal rows:", write_removal_lua(r"c:\Users\josep\Kiro\pz_craft_loops\_kbw_tilefixes_selftest.lua"))


# ---------------------------------------------------------------------------------------------
# ORANGE COMFY COUCH (generated, 2026-08-28): the sofaking sheet has an ORANGE corner but the
# couches sheet has no orange straight couch, so the orange L-shaped couch had no end pieces.
# We recolour the Pink Comfy couch's 8 tiles (d_furniture_couches_01_48..55) to orange. The pink
# and orange corner tiles (sofaking 44..47 / 52..55) are the same shapes in two colours, so the
# pink->orange colour mapping is LEARNED from those pixel pairs (hue shift + per-channel S/V
# curves) and applied to the couch tiles. Generated tileset = same index order as the source
# (j = source index - 48), props copied from the pink tiles with GroupName "Orange Comfy".
ORANGE_COUCH_TILESET = "KBWCommunityLCouch"      # holds ALL four colours' L-couch end tiles
ORANGE_COUCH_PACK = "KBWCommunityLCouch"
ORANGE_COUCH_TILEDEF_NAME = "kbwcommunity_lcouch"
L_COUCH_END_SOURCES = [("Teal", 0), ("Purple", 16), ("Pink", 48), ("Orange", 48)]  # (colour, src base)
# corner tiles (d_location_sofaking base, S,N,E,W = +0..+3) copied to KBWCommunityLCouch_32 + colour*4
L_COUCH_CORNER_SOURCES = [("Teal", 28), ("Purple", 36), ("Pink", 44), ("Orange", 52)]


def lcouch_corner_name(colour_index, v):
    """Our copy of an L-couch corner tile (colour order as L_COUCH_CORNER_SOURCES)."""
    return "%s_%d" % (ORANGE_COUCH_TILESET, 32 + colour_index * 4 + v)
ORANGE_COUCH_TILEDEF_ID = 8178      # free (8170-8199 checked across installed mods; 8181-8187 ours)
_OC_SRC_COUCH = [48 + j for j in range(8)]          # Pink Comfy couch tiles
_OC_PINK_CORNER = [44 + j for j in range(4)]
_OC_ORANGE_CORNER = [52 + j for j in range(4)]
_OC_BINS = 64


def _oc_build_recolor(pink_imgs, orange_imgs):
    """Learn pink -> orange from aligned tile pairs. Returns f(rgb tuple) -> rgb tuple."""
    import colorsys, math
    dh_s = dh_c = 0.0
    sb = [[0.0, 0] for _ in range(_OC_BINS)]
    vb = [[0.0, 0] for _ in range(_OC_BINS)]
    pairs = 0
    for a, b in zip(pink_imgs, orange_imgs):
        pa, pb = a.load(), b.load()
        for y in range(a.height):
            for x in range(a.width):
                p, q = pa[x, y], pb[x, y]
                if p[3] < 200 or q[3] < 200:
                    continue
                hp, sp, vp = colorsys.rgb_to_hsv(p[0] / 255., p[1] / 255., p[2] / 255.)
                ho, so, vo = colorsys.rgb_to_hsv(q[0] / 255., q[1] / 255., q[2] / 255.)
                d = (ho - hp) * 2 * math.pi
                dh_s += math.sin(d); dh_c += math.cos(d)
                i = min(_OC_BINS - 1, int(sp * _OC_BINS)); sb[i][0] += so; sb[i][1] += 1
                i = min(_OC_BINS - 1, int(vp * _OC_BINS)); vb[i][0] += vo; vb[i][1] += 1
                pairs += 1
    if pairs < 1000:
        raise RuntimeError("orange recolor: only %d aligned pixel pairs" % pairs)
    dh = math.atan2(dh_s, dh_c) / (2 * math.pi)

    def table(bins):
        pts = [((i + 0.5) / _OC_BINS, s / n) for i, (s, n) in enumerate(bins) if n >= 20]
        def f(x):
            if x <= pts[0][0]:
                return pts[0][1] * (x / pts[0][0]) if pts[0][0] else pts[0][1]
            for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
                if x <= x1:
                    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
            return pts[-1][1]
        return f
    fs, fv = table(sb), table(vb)

    def recolor(rgb):
        h, s, v = colorsys.rgb_to_hsv(rgb[0] / 255., rgb[1] / 255., rgb[2] / 255.)
        r, g, bl = colorsys.hsv_to_rgb((h + dh) % 1.0, min(1., max(0., fs(s))), min(1., max(0., fv(v))))
        return (int(round(r * 255)), int(round(g * 255)), int(round(bl * 255)))
    return recolor


def _oc_apply(img, recolor):
    out = img.copy()
    px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            p = px[x, y]
            if p[3] > 0:
                r, g, b = recolor(p[:3])
                px[x, y] = (r, g, b, p[3])
    return out


def orange_couch_tile_name(j):
    return "%s_%d" % (ORANGE_COUCH_TILESET, j)


def write_orange_couch_assets(media_dir, check=None):
    """Recoloured Orange Comfy couch tiles: texture pack + tiledef in <media_dir>.
    check: optional dict filled with the fit error on the corner pairs (mean abs RGB diff)."""
    from PIL import Image
    cache = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_cache_orangecouch")
    names = {"d_furniture_couches_01_%d" % (b + j) for _c, b in L_COUCH_END_SOURCES for j in range(8)}
    names |= {"d_location_sofaking_%d" % (b + v) for _c, b in L_COUCH_CORNER_SOURCES for v in range(4)}
    _extract_from_pack(_DTP_PACK, names, cache)

    def load(n):
        return Image.open(os.path.join(cache, n + ".png")).convert("RGBA")
    pink_c = [load("d_location_sofaking_%d" % i) for i in _OC_PINK_CORNER]
    orng_c = [load("d_location_sofaking_%d" % i) for i in _OC_ORANGE_CORNER]
    recolor = _oc_build_recolor(pink_c, orng_c)

    if check is not None:       # how well does the learned mapping reproduce the real orange corner
        tot = n = 0
        for a, b in zip(pink_c, orng_c):
            ra = _oc_apply(a, recolor).load(); pb = b.load()
            for y in range(b.height):
                for x in range(b.width):
                    if pb[x, y][3] > 200 and ra[x, y][3] > 200:
                        tot += sum(abs(ra[x, y][c] - pb[x, y][c]) for c in range(3)) / 3.0
                        n += 1
        check["mean_abs_rgb_err"] = round(tot / max(1, n), 2)

    _ver, tilesets = _load_community_tilesets()
    src = tilesets[b"d_furniture_couches_01"]
    # 32 tiles = 4 colours x the 8 Comfy end tiles (index = colour*8 + j). Teal / purple / pink are
    # straight copies, orange is the recolour. SpriteGridPos is REMOVED and GroupName made unique
    # per tile: the originals belong to a 2-tile couch sprite grid, so as L-couch ends the engine
    # showed the full 2-tile ghost and refused to pick them up (the other half was never there).
    tiles, props = [], []
    for ci, (cname, cbase) in enumerate(L_COUCH_END_SOURCES):
        for j in range(8):
            i = cbase + j
            img = load("d_furniture_couches_01_%d" % i)
            if cname == "Orange":
                img = _oc_apply(img, recolor)
            tiles.append((orange_couch_tile_name(ci * 8 + j), img))
            p = []
            for k, v in src[6][i]:
                if k == b"SpriteGridPos":
                    continue
                p.append((k, ("%s L-Couch End %d" % (cname, j)).encode()) if k == b"GroupName" else (k, v))
            props.append(p)
    # 32..47 = the four colours' CORNER tiles (index 32 + colour*4 + v, v = S,N,E,W as in the pack).
    # Copies of d_location_sofaking so the corner lives in a tileset with no depth map: the pack's
    # DEPTH_d_location_sofaking.png carries depth only for the teal and orange cells, and teal L
    # couches rendered wrong while purple / pink (no depth data) were fine. Our depth-map override
    # of that file did not take in game (2026-08-28), so the corner no longer uses the pack tiles.
    # Props copied from the colour's own corner (orange has none; pink's are used), GroupName unique.
    soft = tilesets[b"d_location_sofaking"]
    for ci, (cname, cbase) in enumerate(L_COUCH_CORNER_SOURCES):
        for v in range(4):
            i = cbase + v
            tiles.append((orange_couch_tile_name(32 + ci * 4 + v), load("d_location_sofaking_%d" % i)))
            srcp = soft[6][i] or soft[6][_OC_PINK_CORNER[v]]
            props.append([(k, ("%s L-Couch Corner %d" % (cname, v)).encode()) if k == b"GroupName" else (k, val)
                          for k, val in srcp])
    n = _write_pack(os.path.join(media_dir, "texturepacks", ORANGE_COUCH_PACK + ".pack"),
                    ORANGE_COUCH_PACK + "0", tiles)
    cols, rows = 8, 6
    ts = [ORANGE_COUCH_TILESET.encode(), (ORANGE_COUCH_TILESET + ".png").encode(), cols, rows, 1,
          cols * rows, props]
    blob = b"tdef" + struct.pack("<ii", 1, 1) + _ser_tileset(ts)
    _parse(blob)
    open(os.path.join(media_dir, ORANGE_COUCH_TILEDEF_NAME + ".tiles"), "wb").write(blob)
    return n


# ---------------------------------------------------------------------------------------------
# SOFAKING DEPTH MAP OVERRIDE (2026-08-28): in DEPTH_d_location_sofaking.png only the TEAL (28-31)
# and ORANGE (52-55) corner cells carry depth data; purple (36-39) and pink (44-47) carry none, and
# the straight couches have none at all. Purple / pink L couches were fine in game, teal looked
# off, so we ship the same sheet with those two colours' cells cleared (consistent with the
# confirmed colours). Written to <common_media_dir>/depthmaps (same file name as the pack's).
SOFAKING_DEPTH_SRC = (r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600\3628736763\mods"
                      r"\CommunityTilePack\common\media\depthmaps\DEPTH_d_location_sofaking.png")
SOFAKING_CLEAR_DEPTH = list(range(28, 32)) + list(range(52, 56))


def write_sofaking_depth_override(common_media_dir):
    from PIL import Image
    im = Image.open(SOFAKING_DEPTH_SRC).convert("RGBA")
    cleared = 0
    for i in SOFAKING_CLEAR_DEPTH:
        x, y = (i % 8) * 128, (i // 8) * 256
        box = (x, y, x + 128, y + 256)
        if im.crop(box).getbbox():
            cleared += 1
        im.paste((0, 0, 0, 0), box)
    os.makedirs(os.path.join(common_media_dir, "depthmaps"), exist_ok=True)
    im.save(os.path.join(common_media_dir, "depthmaps", "DEPTH_d_location_sofaking.png"))
    return cleared
