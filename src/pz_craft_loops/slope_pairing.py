"""Pair W-facing and N-facing wall tiles by mirrored shape (alpha mask of W flipped left-right
vs alpha mask of N). Used for the gable / roof-slope pieces, whose index order differs by sheet."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageOps
import kbw_tilepatch as k
import tikitown_wall_overlays as two

CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_cache_names")


def _mask(sheet, i):
    im = Image.open(os.path.join(CACHE, "%s_%d.png" % (sheet, i))).convert("RGBA")
    return im.getchannel("A").point(lambda a: 255 if a > 40 else 0)


def _iou(a, b):
    import numpy as np
    x, y = np.asarray(a) > 0, np.asarray(b) > 0
    u = (x | y).sum()
    return float((x & y).sum()) / u if u else 0.0


def _profile(sheet, i, bins=32):
    """Visible wall height per column, left to right across the tile's opaque columns."""
    import numpy as np
    a = np.asarray(_mask(sheet, i)) > 0
    cols = np.where(a.any(axis=0))[0]
    if not len(cols):
        return np.zeros(bins)
    h = a[:, cols[0]:cols[-1] + 1].sum(axis=0).astype(float)
    xs = np.linspace(0, len(h) - 1, bins)
    return np.interp(xs, np.arange(len(h)), h) / 256.0


def _rot_score(pw, pn):
    """Rotation pairing (what KBW W->N rotation shows): same height profile, same left-right order.
    (A plain mirror would flip the order; that pairs the wrong slope direction, see validation.)"""
    import numpy as np
    return 1.0 - float(np.abs(pw - pn).mean()) * 4.0


def pair(sheet, w_idx, n_idx, min_score=0.80):
    """Greedy best-first one-to-one pairing. Returns ([(w, n, score)], unpaired_w, unpaired_n)."""
    k._extract_from_pack(two._TIKITOWN_PACK, {"%s_%d" % (sheet, i) for i in list(w_idx) + list(n_idx)}, CACHE)
    wp = {i: _profile(sheet, i) for i in w_idx}
    np_ = {i: _profile(sheet, i) for i in n_idx}
    cand = sorted(((_rot_score(wp[w], np_[n]), w, n) for w in w_idx for n in n_idx), reverse=True)
    used_w, used_n, out = set(), set(), []
    for s, w, n in cand:
        if s < min_score:
            break
        if w in used_w or n in used_n:
            continue
        used_w.add(w); used_n.add(n); out.append((w, n, round(s, 3)))
    return sorted(out), sorted(set(w_idx) - used_w), sorted(set(n_idx) - used_n)


if __name__ == "__main__":
    # validation against the in-game-confirmed Newburbs roof slope pairs
    sh = "tt_newburbs_walls_01_white"
    known = {(88, 99), (89, 100), (90, 101), (98, 93), (97, 92), (96, 91)}
    got, uw, un = pair(sh, [88, 89, 90, 96, 97, 98], [91, 92, 93, 99, 100, 101])
    print("newburbs:", got, "| matches known:", {(w, n) for w, n, _s in got} == known, uw, un)
    for s in sys.argv[1:]:
        print(s, pair(s, list(range(30, 48)), list(range(48, 64)) + [70, 71]))
