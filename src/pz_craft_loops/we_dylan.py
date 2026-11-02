# -*- coding: utf-8 -*-
"""Adopt World Essentials' isolated Dylan sprites (WECommunity_*) in our Community build.

Background (2026-10-30/31): Fort Waterfront B42 registers a different `dylanstiles` under the same
tiledef 6985, so on servers with both mods the Dylan tile numbers shift and our pieces placed the
wrong tiles. The WE dev fixed it (not us) by shipping private copies of the 139 Dylan sprites we
use as WECommunity_<Set>_<n> (same index), tiledef `wecommunity_dylan 8182`, and rewriting the
definitions to use them. These helpers make our builder emit exactly that, so the WE sync works.

Assets are vendored verbatim in zomboid/communitytilepack/vendor_we/ (see _vendor_we_dylan.py).
Rename runs AFTER add_viewscreen_north_faces / add_case_mirror_faces (they match original names).
Only whole string leaves that are sprite names are renamed; ids, translationKeys and IG_UI keys
keep the original text (WE did not rename them).
"""
import os, re, json, shutil

VENDOR = r"c:\Users\josep\Kiro\zomboid\communitytilepack\vendor_we"
TILES = "wecommunity_dylan.tiles"
PACK = "WECommunityDylan.pack"
TILEDEF_NAME = "wecommunity_dylan"
TILEDEF_ID = 8182
MODINFO_LINES = ["pack=WECommunityDylan", "tiledef=%s %d" % (TILEDEF_NAME, TILEDEF_ID)]
_COMMUNITY_DYLAN_TILES = (r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600\3628736763"
                          r"\mods\CommunityTilePack\common\media\dylanstiles.tiles")

_MAP = None
_SPRITE_RE = None


def sprite_map():
    """Original Dylan sprite -> WECommunity sprite (WE's authoritative 139-entry table)."""
    global _MAP
    if _MAP is None:
        txt = open(os.path.join(VENDOR, "WorldEssentialsCommunitySprites.lua"), encoding="utf-8").read()
        _MAP = dict(re.findall(r'\["([^"]+)"\]="([^"]+)"', txt))
        if len(_MAP) < 100:
            raise RuntimeError("WE sprite map looks wrong (%d entries)" % len(_MAP))
    return _MAP


def _dylan_sprite_re():
    """Regex matching ANY sprite of the 40 dylanstiles tilesets (to catch unmapped indices)."""
    global _SPRITE_RE
    if _SPRITE_RE is None:
        from kbw_tilepatch import _parse
        sets = sorted((n.decode() for n in _parse(open(_COMMUNITY_DYLAN_TILES, "rb").read())[1]),
                      key=len, reverse=True)
        _SPRITE_RE = re.compile(r"^(%s)_\d+$" % "|".join(re.escape(s) for s in sets))
    return _SPRITE_RE


def rename_buildable(b):
    """Rewrite Dylan sprite leaves in place. Returns (renamed_count, unmapped_sprites)."""
    m, rx = sprite_map(), _dylan_sprite_re()
    count = [0]
    unmapped = []

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str):
                    o[k] = conv(v)
                else:
                    walk(v)
        elif isinstance(o, list):
            for i, v in enumerate(o):
                if isinstance(v, str):
                    o[i] = conv(v)
                else:
                    walk(v)

    def conv(s):
        if s in m:
            count[0] += 1
            return m[s]
        if rx.match(s):
            unmapped.append(s)
        return s

    for key in ("iconSprite", "stages", "variants"):
        if key in b:
            if isinstance(b[key], str):
                b[key] = conv(b[key])
            else:
                walk(b[key])
    return count[0], unmapped


def install_assets(media_dir, common_media_dir):
    """Copy WE's tiledef + pack into the build and merge its tileGeometry blocks into ours."""
    shutil.copy2(os.path.join(VENDOR, TILES), os.path.join(media_dir, TILES))
    os.makedirs(os.path.join(media_dir, "texturepacks"), exist_ok=True)
    shutil.copy2(os.path.join(VENDOR, PACK), os.path.join(media_dir, "texturepacks", PACK))
    tg_path = os.path.join(common_media_dir, "tileGeometry.txt")
    blocks = open(os.path.join(VENDOR, "tileGeometry_WECommunity.txt"), encoding="utf-8").read()
    if os.path.isfile(tg_path):
        ours = open(tg_path, encoding="utf-8").read().rstrip()
        if not ours.endswith("}"):
            raise RuntimeError("unexpected tileGeometry.txt layout: %s" % tg_path)
        body = ours[:-1].rstrip() + "\n"
    else:
        os.makedirs(common_media_dir, exist_ok=True)
        body = "tileGeometry\n{\n    VERSION = 2,\n"
    # CRLF: matches WE's shipped file byte for byte (keeps the hand-off diff clean)
    open(tg_path, "w", encoding="utf-8", newline="\r\n").write(body + blocks + "}\n")
