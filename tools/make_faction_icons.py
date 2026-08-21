"""
Generate placeholder faction icons for the Archinity suite.

RimWorld faction icons are white silhouettes with alpha; the game tints them
with the faction's colour at draw time. Anything non-white here will fight the
tint, so keep fills pure white and carry all shape information in the alpha
channel.

Run:  python tools/make_faction_icons.py
Output lands in each mod's Textures/World/WorldObjects/Expanding/ folder.

These are placeholders. Replace the PNGs with real art whenever you like -
keep the filenames and nothing else needs to change.
"""

import math
import os

from PIL import Image, ImageDraw

SIZE = 256          # generous; RimWorld downsamples cleanly
SS = 4              # supersample factor for smooth edges
W = SIZE * SS

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def chevron(cx, cy, span, thick, droop=1.35):
    """A V pointing up, with thickness. Returns a polygon point list."""
    return [
        (cx, cy - span),
        (cx + span, cy),
        (cx + span - thick, cy),
        (cx, cy - span + thick * droop),
        (cx - span + thick, cy),
        (cx - span, cy),
    ]


def free_companies():
    """Three chevrons in loose formation - a fleet that flies together but
    answers to nobody. Decreasing size implies depth and motion."""
    img = Image.new("RGBA", (W, W), (255, 255, 255, 0))
    d = ImageDraw.Draw(img)

    cx = W * 0.5
    specs = [
        (W * 0.66, W * 0.30, W * 0.085),   # cy, span, thickness
        (W * 0.50, W * 0.22, W * 0.070),
        (W * 0.37, W * 0.14, W * 0.055),
    ]
    for cy, span, thick in specs:
        d.polygon(chevron(cx, cy, span, thick), fill=(255, 255, 255, 255))

    # A single point above the formation: the star they are steering by.
    r = W * 0.030
    d.ellipse([cx - r, W * 0.20 - r, cx + r, W * 0.20 + r],
              fill=(255, 255, 255, 255))
    return img


def glitterites():
    """A closed ring with radial spokes - a gate, a watcher, something that
    encircles and does not let you past. Deliberately cold and symmetrical,
    the opposite of the Free Companies' open formation."""
    img = Image.new("RGBA", (W, W), (255, 255, 255, 0))
    d = ImageDraw.Draw(img)

    cx = cy = W * 0.5
    outer, inner = W * 0.36, W * 0.28

    d.ellipse([cx - outer, cy - outer, cx + outer, cy + outer],
              fill=(255, 255, 255, 255))
    d.ellipse([cx - inner, cy - inner, cx + inner, cy + inner],
              fill=(255, 255, 255, 0))

    # Eight spokes bridging the gap inward.
    spoke_w = W * 0.035
    for i in range(8):
        a = math.radians(i * 45.0)
        x, y = cx + math.cos(a) * inner * 0.55, cy + math.sin(a) * inner * 0.55
        d.regular_polygon((x, y, spoke_w), 4, rotation=i * 45,
                          fill=(255, 255, 255, 255))

    # Solid core.
    core = W * 0.10
    d.ellipse([cx - core, cy - core, cx + core, cy + core],
              fill=(255, 255, 255, 255))
    return img


TARGETS = [
    ("Archinity.Drifters", "Archinity_FreeCompanies", free_companies),
    ("Archinity.Glitterites", "Archinity_Glitterites", glitterites),
]


def main():
    for mod, name, fn in TARGETS:
        if not os.path.isdir(os.path.join(REPO, mod)):
            print("skip (mod not created yet):", mod)
            continue
        out_dir = os.path.join(REPO, mod, "Textures", "World",
                               "WorldObjects", "Expanding")
        os.makedirs(out_dir, exist_ok=True)
        img = fn().resize((SIZE, SIZE), Image.LANCZOS)
        path = os.path.join(out_dir, name + ".png")
        img.save(path, "PNG", optimize=True)
        print("wrote", os.path.relpath(path, REPO),
              "(%d bytes)" % os.path.getsize(path))


if __name__ == "__main__":
    main()
