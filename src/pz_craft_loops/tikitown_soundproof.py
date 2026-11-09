# -*- coding: utf-8 -*-
"""Generate 37_tikitown_soundproof.json: the recording-studio soundproofing panels on Drazion's
tikitown-props-14 (8 cols; GroupName Proof Wall / Proof Window / Proof Door Frame, Material Fabric).

MODEL (rev 4, 2026-08-28): copied piece-for-piece from the in-game-confirmed Newburbs trim
(35_tikitown_newburbs_trim.json), whose tiles carry the SAME flags (WallOverlay + attachedW/N):
  * wall + corner panels  -> like the trim runs:   placement overlay + needToBeAgainstWall
  * window panel          -> like the window trim: placement wall + dontNeedFrame + providesWindowFrame
  * door frame panel      -> like the door trim:   placement wall (tiles typed doorFrW / doorFrN)
The one tile difference: the soundproof tiles are IsMoveAble. A movable WallObject + WallOverlay tile
is a vanilla "WallOverlay" moveable, and World Essentials builds those through its native
wall-attachment path, which refuses window and door walls (that refusal was the error screen).
Rev 5 (2026-08-28): the buildables use OUR OWN COPIES of the tiles (copy_sprite / copy_props below)
with IsMoveAble removed, Facing fixed, door-trim types added and the corner retagged attachedNW, so
they take the same plain-KBW path as the Newburbs trim. The pack tiles are no longer patched
(that changed map-placed soundproofing too).

History: rev 1 plain objects (error screen on window / door walls), rev 2 WE "wallCovering"
(KBW's paint / wallpaper path: no cursor at all), rev 3 overlay for every piece.

Faces, from each tile's attach flag: wall W 8 / N 9, pillar 11 (one post on the NW vertex: single
face, free-standing prop), corner N 10, window N 17 (no west art;
a mirrored tile was dropped, needs a redraw), door frame W 18 / N 19. No south-wall art in the pack. Cosmetic; nothing reduces sound.
"""
import json

SHEET = "tikitown-props-14"
OUT = r"c:\Users\josep\Kiro\zomboid\tikitown\37_tikitown_soundproof.json"

OVERLAY = {"kind": "overlay", "needToBeAgainstWall": True}
WINDOW = {"kind": "wall", "requiresFloor": False, "dontNeedFrame": True, "providesWindowFrame": True}
DOOR = {"kind": "wall", "requiresFloor": False}
POST = {"kind": "object", "requiresFloor": False}   # free-standing post (no host wall, no rotation)
TRIM_OBJECT = {"isThumpable": True, "dismantable": True}   # Newburbs window / door trim object block
CORNER_ISVALID = "KBWCommunityCornerTrim.OnIsValid"       # shared OverlayGuard Lua (kbw_tilepatch)

# (slug, display name, {KBW face: tile index}, placement, object, pieceClass)
PIECES = [
    ("wall", "Soundproof Wall Panel", {"W": 8, "N": 9}, OVERLAY,
     {"isThumpable": False, "canPassThrough": True, "dismantable": True}, None),
    # 11 is a thin post on the square's top (NW) vertex, where its W and N walls meet: one sprite,
    # nothing to rotate. As an overlay it had to pick a host wall per face (W -> west wall,
    # N -> north wall), which is why rotating it mattered. Built as a single-face walk-through prop
    # instead: no wall needed, so it also caps a run's end on a square with no wall of its own.
    ("pillar", "Soundproof Pillar", {"W": 11}, POST,
     {"isThumpable": False, "canPassThrough": True, "blockAllSquare": False, "dismantable": True}, None),
    # Corner (rev 3, 2026-08-28): free-standing walk-through prop + our corner onIsValid (wall
    # edge on BOTH the west and north sides; see newburbs_trim.CORNER_ISVALID). As an overlay it
    # was drawn onto one host wall only, so the half over the other edge did not render where that
    # wall was missing, and isCorner refused two plain walls meeting.
    ("corner", "Soundproof Corner Panel", {"N": 10}, POST,
     {"isThumpable": False, "canPassThrough": True, "blockAllSquare": False, "dismantable": True}, None),
    # North only: the pack has no west art. A plain mirror of 17 was tried (2026-08-28) and dropped;
    # the west window panel needs redrawn art to match the pack's west panels.
    ("window", "Soundproof Window Panel", {"N": 17}, WINDOW, TRIM_OBJECT, "window"),
    ("doorframe", "Soundproof Door Frame Panel", {"W": 18, "N": 19}, DOOR, TRIM_OBJECT, "door"),
]


# ---- our own copies of the soundproof tiles (2026-08-28) ---------------------------------------
# The fixes these tiles need (IsMoveAble removed, Facing from the attach flag, door-trim types, the
# corner as an NW corner overlay) used to be applied to the PACK tiles at load. Tile patches change
# every map-placed copy too, so they now live on our own copies instead, written by
# tikitown_wall_overlays.write_overlay_assets as a tileset of their own in the same pack +
# tiledef file (no new mod.info lines). Map-placed tikitown-props-14 tiles are left exactly as Drazion ships them.
# Own tileset inside the wall overlay .tiles file: a tileset may hold at most 512 tiles, so the
# copies could not simply be appended to the 1200 overlay tiles (world load refused, 2026-11-08).
COPY_TILESET = "KBWTikiTownSoundproof"
COPY_BASE = 0
SOUNDPROOF_SRC = (8, 9, 10, 11, 17, 18, 19)
_FACING = {8: b"E", 9: b"S", 10: b"S", 11: b"W", 17: b"S", 18: b"E", 19: b"S"}
_DOOR_TRIM = {18: b"doorFrW", 19: b"doorFrN"}   # WE's FindOverlaySupport needs these on a DoorWall
_CORNER = 10


def copy_sprite(i):
    """Our copy of tikitown-props-14_<i>."""
    return "%s_%d" % (COPY_TILESET, COPY_BASE + SOUNDPROOF_SRC.index(i))


def copy_props(i, src_props):
    """Tile props for our copy of tikitown-props-14_<i>, from the pack tile's props."""
    out = []
    for k, v in src_props:
        if k in (b"IsMoveAble", b"Facing"):
            continue          # not a vanilla "WallOverlay" moveable -> plain KBW path (like the trims)
        if i == _CORNER and k in (b"CornerNorthWall", b"CornerWestWall"):
            continue          # wall-split sprites only matter for a movable corner overlay
        if i == _CORNER and k == b"attachedN":
            k = b"attachedNW"  # drawn as an NW corner, not on the north wall only (west half hidden)
        out.append((k, v))
    out.append((b"Facing", _FACING[i]))
    if i in _DOOR_TRIM:
        out.append((_DOOR_TRIM[i], b""))
    return sorted(out)


def _spr(i):
    return copy_sprite(i)


def _recipe():
    # Newburbs trim cost: hammer + 2 planks + 4 nails, Woodwork 2
    return {
        "inputs": [
            {"id": "tool_hammer", "role": "tool", "mode": "keep",
             "resourceType": "Item", "tags": ["base:hammer"], "amount": 1},
            {"id": "source_material_1", "role": "material", "mode": "consume",
             "resourceType": "Item", "items": ["Base.Plank"], "amount": 2},
            {"id": "source_material_2", "role": "material", "mode": "consume",
             "resourceType": "Item", "items": ["Base.Nails"], "amount": 4},
        ],
        "skills": {"Woodwork": 2},
    }


def _buildable(slug, name, faces, placement, obj, piece_class):
    bid = "worldessentials.tikitown.soundproof_%s" % slug
    first = next(iter(faces.values()))
    b = {
        "id": bid,
        "allowSpriteReuse": True,
        "translationKey": "IGUI_WETiki_soundproof_%s" % slug,
        "displayName": name,
        "tooltipKey": "Tooltip_KBW_DecorativeWallFixture",
        "category": "Walls and Wall Finishes",
        "subcategory": "Soundproofing",
        "material": "Wood",
        "materialTags": ["Wood", "Fabric"],
        "iconSprite": _spr(first),
        "placement": dict(placement),
        "tags": ["tikitown", "drazion", "world-essentials", "soundproofing"],
        "stages": [{
            "id": "built",
            "geometry": {"faces": {f: {"layers": [{"rows": [[_spr(i)]]}]} for f, i in faces.items()}},
            "requirements": _recipe(),
            "construction": {"time": 200, "timedAction": "BuildWallHammer",
                             "completionSound": "BuildWoodenStructureLarge",
                             "xp": {"Woodwork": 40}, "category": "Carpentry"},
            "object": dict(obj),
            "health": 150,
        }],
    }
    if slug == "corner":
        b["stages"][0]["callbacks"] = {"onIsValid": CORNER_ISVALID}
    if piece_class:
        b["pieceClass"] = piece_class
    return b


def main():
    doc = {
        "schemaVersion": 1,
        "category": "Walls and Wall Finishes",
        "source": ("TikiTown tikitown-props-14 recording-studio soundproofing (Drazion's Tilepack), modeled "
                   "on the Newburbs trim (wall/corner overlay, window trim, door trim). Uses our own "
                   "copies of the tiles (KBWTikiTownSoundproof_0..6; pack tiles unchanged)."),
        "buildables": [_buildable(*p) for p in PIECES],
    }
    json.dump(doc, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    ids = [b["id"] for b in doc["buildables"]]
    assert len(ids) == len(set(ids))
    print("wrote %s (%d buildables)" % (OUT, len(ids)))


if __name__ == "__main__":
    main()
