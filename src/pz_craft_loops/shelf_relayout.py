# -*- coding: utf-8 -*-
"""Re-lay vanilla shelf fill overlays (books) onto our Simon MD in-wall shelves (user, 2026-11-17: the
vanilla stand-ins drew in front of the shelves and between the boards; vanilla's shelf stands out from the
wall and has 3 boards, ours are recessed with 4).

For a wall shelf the boards run along the wall: on a W-wall piece a board's front lip drops half a row per
column to the left, on an N-wall piece to the right. With u = y + s * (x - X_REF) (s = +0.5 for W, -0.5
for N) every board is a constant u. We
  1. find our boards: runs of lighter board top surface along a reference column (their lips, in u),
  2. cut a vanilla overlay into rows of books the same way (gaps in u),
  3. move each row back toward the wall (along the wall normal) until it fits the shelf's depth, then up or
     down so its lowest pixel sits LIP_MARGIN rows above our board's lip,
  4. clip the result to our shelf's own outline.
Corners: the left half is laid as a W-wall shelf, the right half as an N-wall shelf.
"""
import numpy as np
from PIL import Image

LIP_MARGIN = 3
BOARD_MIN_RUN = 8        # rows of lighter wood that make a board top
BOARD_CONTRAST = 12      # luminance over the darker back panel


def _lum(a):
    return (a[:, :, 0] * 3 + a[:, :, 1] * 6 + a[:, :, 2]) // 10


def board_lips(art, side, x_ref):
    """Board lip rows at column x_ref (top to bottom), from runs of lighter wood in that column."""
    a = np.array(art.convert("RGBA")).astype(int)
    lum = _lum(a)[:, x_ref]
    on = a[:, x_ref, 3] > 200
    ys = np.nonzero(on)[0]
    if not len(ys):
        return []
    back = np.percentile(lum[on], 25)
    light = on & (lum > back + BOARD_CONTRAST)
    lips, y = [], 0
    while y < len(light):
        if light[y]:
            s = y
            while y < len(light) and light[y]:
                y += 1
            if y - s >= BOARD_MIN_RUN:
                lips.append(y - 1)
        y += 1
    return lips


def _rows_of_books(mask, side, x_ref):
    """Split overlay pixels into rows of books: [(boolean mask, (u_min, u_max))], top first."""
    ys, xs = np.nonzero(mask)
    if not len(ys):
        return []
    s = 0.5 if side == "W" else -0.5
    u = np.rint(ys + s * (xs - x_ref)).astype(int)
    order = np.unique(u)
    groups, cur = [], [order[0]]
    for v in order[1:]:
        if v - cur[-1] > 2:
            groups.append(cur)
            cur = [v]
        else:
            cur.append(v)
    groups.append(cur)
    out = []
    for g in groups:
        sel = (u >= g[0]) & (u <= g[-1])
        m = np.zeros_like(mask)
        m[ys[sel], xs[sel]] = True
        if m.sum() >= 30:                     # specks are not a row of books
            out.append((m, (g[0], g[-1])))
    return out


def _shift(a, dx, dy):
    out = np.zeros_like(a)
    h, w = a.shape[:2]
    ys0, ys1 = max(0, dy), min(h, h + dy)
    xs0, xs1 = max(0, dx), min(w, w + dx)
    out[ys0:ys1, xs0:xs1] = a[ys0 - dy:ys1 - dy, xs0 - dx:xs1 - dx]
    return out


# Board lips (row at the reference column) per shelf design, read from the art (2026-11-17): the open oak
# shelves give clean runs at 57 / 93 / 144 / 195 (W, column 45; N mirrored, column 83); the glass-door and
# corner pieces share that frame. The sloped shelves: tall 87 / 140 / 190, short 140 / 190.
INWALL_LIPS = [57, 93, 144, 195]
SLOPED_LIPS = {"tall": [87, 140, 190], "short": [140, 190]}
X_REF = {"W": 45, "N": 83}
FRONT_X = {"W": 60, "N": 68}     # the shelf's front post: books stay behind it


def relayout(overlay, shelf, side, x_ref, front_x, half=None, lips=None):
    """`overlay` (vanilla books) re-laid onto `shelf` (our art). side W / N; x_ref = column used to find
    boards; front_x = the shelf's front edge column (W: books must stay left of it, N: right of it);
    half = None, "L" or "R" (only that half of both images). Returns an RGBA image."""
    ov = np.array(overlay.convert("RGBA"))
    sh = np.array(shelf.convert("RGBA"))
    keep = np.ones(ov.shape[:2], bool)
    if half == "L":
        keep[:, 64:] = False
    elif half == "R":
        keep[:, :64] = False
    mask = (ov[:, :, 3] > 0) & keep
    s = 0.5 if side == "W" else -0.5
    lips = list(lips) if lips is not None else board_lips(shelf, side, x_ref)
    rows = _rows_of_books(mask, side, x_ref)
    out = np.zeros_like(ov)
    if not lips or not rows:
        return Image.fromarray(out, "RGBA"), lips, 0
    # our rows of books, top first: one per board (vanilla has 3, a 4-board shelf reuses the middle one)
    pick = [rows[min(i, len(rows) - 1)] if i < len(rows) else rows[len(rows) // 2] for i in range(len(lips))]
    for (m, _u), lip in zip(pick, lips):
        piece = np.where(m[:, :, None], ov, 0).astype(ov.dtype)
        ys, xs = np.nonzero(m)
        # back toward the wall along its normal: W wall -> screen (-2, -1) per step, N wall -> (+2, -1)
        if side == "W":
            t = max(0, int(np.ceil((xs.max() - front_x) / 2.0)))
            dx, dy0 = -2 * t, -t
        else:
            t = max(0, int(np.ceil((front_x - xs.min()) / 2.0)))
            dx, dy0 = 2 * t, -t
        xs2, ys2 = xs + dx, ys + dy0
        # lowest pixel in u (along the board) onto the lip
        u_bottom = (ys2 + s * (xs2 - x_ref)).max()
        dy = int(round(lip - LIP_MARGIN - u_bottom))
        out = np.maximum(out, _shift(piece, dx, dy0 + dy))
    out[sh[:, :, 3] == 0] = 0                 # never outside the shelf
    if half == "L":
        out[:, 64:] = 0
    elif half == "R":
        out[:, :64] = 0
    return Image.fromarray(out, "RGBA"), lips, len(rows)


def glassed(im, alpha=0.6):
    """Books seen through a glass door: fainter, so the glass shows over them."""
    a = np.array(im.convert("RGBA")).astype(float)
    a[:, :, 3] *= alpha
    return Image.fromarray(a.astype(np.uint8), "RGBA")
