"""Stage BC_TakePinned as a Steam Workshop item (run again after any change to the mod).

Writes  %USERPROFILE%\\Zomboid\\Workshop\\BC_TakePinned\\
          workshop.txt, preview.png (256x256, the Workshop thumbnail)
          Contents\\mods\\BC_TakePinned\\42\\...  (mod.info, poster.png, media)
          Contents\\mods\\BC_TakePinned\\common\\ (empty; B42 expects the folder)
and the poster into this source folder (42/poster.png, which mod.info names).

The game's Workshop menu (main menu > Workshop > Create and update items) uploads the folder. After the
first upload Steam gives the item an id: put it in WORKSHOP_ID below so later runs keep it. Better Containers
must be added on the Steam page as a Required Item (workshop.txt has no field for it).
"""
import os
import shutil
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
MOD_ID = "BC_TakePinned"
WORKSHOP_ID = "3842073243"  # https://steamcommunity.com/sharedfiles/filedetails/?id=3842073243 (2026-11-18)
DEST = os.path.join(os.environ["USERPROFILE"], "Zomboid", "Workshop", MOD_ID)
TITLE = "Better Containers: Take Pinned"
DESCRIPTION = """Adds a [b]Take Pinned[/b] button to the loot window, next to Take All.

Pin an item type in Better Containers (right-click an item > Pin Item Type). Then one click on Take Pinned moves every item of a pinned type into the container that is open in your inventory window (your main inventory or a bag).

[b]Where it takes from[/b]
[list]
[*]every container shown in the loot window
[*]the floor
[*]Better Containers' Proximity and zombie corpse views (worn items on corpses included)
[*]bags inside any of these
[/list]

[b]Details[/b]
[list]
[*]Walks to each container nearest first and queues normal transfers, so it adds to your action queue without clearing it.
[*]Checks your destination's room first; items that don't fit are skipped with a "No room for N pinned item(s)" message.
[*]Leaves alone what you already carry or wear, unwanted items, and heavy force-drop items.
[*]A pinned bag moves with its contents.
[*]The button only shows when at least one type is pinned, and it scans only when you click.
[/list]

[b]Requirements[/b]
Better Containers (Build 42.19 or newer: the version with pinned items). Older versions have no pins, so the button never appears.

Client-side only: it uses the game's own transfer actions and changes nothing on the server. Tested in single player; not yet tested in multiplayer.
"""
TAGS = "Build 42;Interface"
VISIBILITY = "public"


def _font(size, bold=True):
    for name in (("arialbd.ttf", "segoeuib.ttf") if bold else ("arial.ttf", "segoeui.ttf")):
        p = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", name)
        if os.path.isfile(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def _pin(d, cx, cy, s, colour):
    """A push pin: round head, collar, needle (s = head radius)."""
    d.ellipse((cx - s, cy - s, cx + s, cy + s), fill=colour)
    d.ellipse((cx - s * 0.45, cy - s * 0.6, cx - s * 0.05, cy - s * 0.2), fill=(255, 255, 255, 110))
    d.polygon([(cx - s * 0.55, cy + s * 0.75), (cx + s * 0.55, cy + s * 0.75),
               (cx + s * 0.3, cy + s * 1.35), (cx - s * 0.3, cy + s * 1.35)], fill=colour)
    d.line((cx, cy + s * 1.35, cx, cy + s * 2.6), fill=(205, 205, 210, 255), width=max(2, int(s * 0.16)))


def art(size):
    im = Image.new("RGBA", (size, size), (30, 34, 40, 255))
    d = ImageDraw.Draw(im)
    u = size / 256.0
    # the loot window row: three item slots, the middle one pinned
    for i, x in enumerate((38, 104, 170)):
        box = (x * u, 70 * u, (x + 48) * u, 118 * u)
        d.rounded_rectangle(box, radius=6 * u, fill=(52, 58, 66, 255),
                            outline=(214, 170, 60, 255) if i == 1 else (80, 88, 98, 255), width=max(1, int(3 * u)))
    _pin(d, 128 * u, 52 * u, 16 * u, (214, 64, 52, 255))
    # the button
    bx = (40 * u, 150 * u, 216 * u, 196 * u)
    d.rounded_rectangle(bx, radius=8 * u, fill=(214, 170, 60, 255))
    f = _font(int(22 * u))
    t = "TAKE PINNED"
    w = d.textlength(t, font=f)
    d.text(((256 * u - w) / 2, 160 * u), t, font=f, fill=(30, 34, 40, 255))
    f2 = _font(int(15 * u), bold=False)
    t2 = "for Better Containers"
    w2 = d.textlength(t2, font=f2)
    d.text(((256 * u - w2) / 2, 210 * u), t2, font=f2, fill=(190, 196, 204, 255))
    return im.convert("RGB")


def main():
    art(512).save(os.path.join(HERE, "42", "poster.png"))
    contents = os.path.join(DEST, "Contents", "mods", MOD_ID)
    if os.path.isdir(contents):
        shutil.rmtree(contents)
    shutil.copytree(os.path.join(HERE, "42"), os.path.join(contents, "42"))
    os.makedirs(os.path.join(contents, "common"), exist_ok=True)
    art(256).save(os.path.join(DEST, "preview.png"))
    lines = ["version=1", "id=" + WORKSHOP_ID, "title=" + TITLE]
    lines += ["description=" + l for l in DESCRIPTION.strip("\n").split("\n")]
    lines += ["tags=" + TAGS, "visibility=" + VISIBILITY]
    open(os.path.join(DEST, "workshop.txt"), "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    for dp, _dn, fn in os.walk(DEST):
        for f in fn:
            p = os.path.join(dp, f)
            print("%-90s %7d" % (os.path.relpath(p, DEST), os.path.getsize(p)))


if __name__ == "__main__":
    main()
