"""Photo -> animated ASCII portrait SVG (run locally, once per photo).

    python scripts/make_portrait.py [assets/source/portrait.png] [assets/portrait.svg]

Steps: flood-fill the plain studio background away from the image border,
stretch contrast on the subject only, sample the photo onto a character grid,
map darkness to glyph density, then emit one <text> row per grid line that is
revealed by an animated clip-path wipe with a block cursor riding the edge.
Strongly coloured areas (the turban) keep a tint; everything else is grey.
"""

import colorsys
import sys
from collections import deque

import numpy as np
from PIL import Image, ImageFilter, ImageOps

from theme import HOST, MAROON, SOFT, esc, window, write

SRC = sys.argv[1] if len(sys.argv) > 1 else "assets/source/portrait.png"
OUT = sys.argv[2] if len(sys.argv) > 2 else "assets/portrait.svg"

W, H = 840, 880
COLS = 100
CHAR_W = 8.0
LINE_H = 14.6
FONT = 13.2
TOP = 52
ROW_DUR = 0.055
GAMMA = 0.8  # < 1 lifts mid-tones (skin) toward sparse glyphs

# light -> dark. Bright areas become blank so the background disappears.
RAMP = " .`',:;-~=+*cxo%#&@"


def remove_background(rgb, tol=7.0, min_lum=110):
    """Region-grow from the border across smooth, light, unsaturated pixels."""
    lum = rgb.mean(axis=2)
    sat = rgb.max(axis=2) - rgb.min(axis=2)
    h, w = lum.shape
    bg = np.zeros((h, w), bool)
    q = deque()
    for x in range(w):
        q.append((0, x))
        q.append((h - 1, x))
    for y in range(h):
        q.append((y, 0))
        q.append((y, w - 1))
    for y, x in q:
        bg[y, x] = lum[y, x] > min_lum and sat[y, x] < 40
    q = deque((y, x) for y, x in q if bg[y, x])
    while q:
        y, x = q.popleft()
        for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= ny < h and 0 <= nx < w and not bg[ny, nx]:
                if (
                    lum[ny, nx] > min_lum
                    and sat[ny, nx] < 40
                    and abs(lum[ny, nx] - lum[y, x]) < tol
                ):
                    bg[ny, nx] = True
                    q.append((ny, nx))
    # close pin-holes so stray glyphs don't speckle the background
    m = Image.fromarray((bg * 255).astype(np.uint8))
    m = m.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))
    return np.array(m) > 127


def to_grid(path):
    img = Image.open(path).convert("RGB")
    rgb = np.asarray(img).astype(float)
    bg = remove_background(rgb)

    gray = np.asarray(ImageOps.grayscale(img)).astype(float)
    # local-contrast boost (unsharp mask) so eyes, brows and nose survive
    # the trip down to ~100 columns
    blur = np.asarray(Image.fromarray(gray.astype(np.uint8)).filter(ImageFilter.GaussianBlur(4))).astype(float)
    gray = gray + 1.6 * (gray - blur)
    subject = gray[~bg]
    lo, hi = np.percentile(subject, 2), np.percentile(subject, 99)
    gray = np.clip((gray - lo) / max(hi - lo, 1), 0, 1) ** GAMMA
    gray[bg] = 1.0

    rows = round(COLS * (CHAR_W / LINE_H) * img.height / img.width)
    size = (COLS, rows)
    g = np.asarray(Image.fromarray((gray * 255).astype(np.uint8)).resize(size, Image.BOX)) / 255
    c = np.asarray(img.resize(size, Image.BOX)).astype(float) / 255
    m = np.asarray(Image.fromarray((bg * 255).astype(np.uint8)).resize(size, Image.BOX)) / 255

    lines = []
    for y in range(rows):
        cells = []
        for x in range(COLS):
            if m[y, x] > 0.5:
                cells.append((" ", None))
                continue
            ch = RAMP[min(int((1 - g[y, x]) * len(RAMP)), len(RAMP) - 1)]
            hue, sat, val = colorsys.rgb_to_hsv(*c[y, x])
            tinted = sat > 0.5 and val > 0.15 and (hue < 0.015 or hue > 0.9)
            cells.append((ch, MAROON if tinted else None))
        lines.append(cells)
    return lines


def row_markup(cells):
    """Collapse runs of the same colour into <tspan>s."""
    out, run, colour = [], [], None
    for ch, col in cells + [("", "__end__")]:
        if col != colour and run:
            text = esc("".join(run))
            out.append(f'<tspan fill="{colour}">{text}</tspan>' if colour else text)
            run = []
        colour = col
        run.append(ch)
    return "".join(out)


def build(lines):
    left = (W - COLS * CHAR_W) / 2
    width = COLS * CHAR_W
    parts = []
    for i, cells in enumerate(lines):
        if all(ch == " " for ch, _ in cells):
            continue
        y = TOP + i * LINE_H
        t0 = i * ROW_DUR
        parts.append(
            f'<clipPath id="r{i}"><rect x="{left}" y="{y}" height="{LINE_H + 1:.1f}" width="0">'
            f'<animate attributeName="width" from="0" to="{width}" begin="{t0:.3f}s" '
            f'dur="{ROW_DUR}s" fill="freeze"/></rect></clipPath>'
            f'<text clip-path="url(#r{i})" xml:space="preserve" x="{left}" y="{y + LINE_H * 0.78:.1f}" '
            f'font-size="{FONT}" fill="{SOFT}" textLength="{width}" lengthAdjust="spacing">'
            f"{row_markup(cells)}</text>"
        )
    end = len(lines) * ROW_DUR
    # cursor rides down the right edge of each freshly typed row, then blinks
    parts.append(
        f'<rect x="{left}" width="{CHAR_W:.0f}" height="{LINE_H - 3:.1f}" fill="{SOFT}" opacity="0.85">'
        f'<animate attributeName="x" values="{left};{left + width}" dur="{ROW_DUR}s" '
        f'repeatCount="{len(lines)}" fill="freeze"/>'
        f'<animate attributeName="y" values="{";".join(f"{TOP + 1.5 + i * LINE_H:.1f}" for i in range(len(lines)))}" '
        f'dur="{end:.3f}s" calcMode="discrete" fill="freeze"/>'
        f'<animate attributeName="opacity" values="0.85;0;0.85" dur="1s" begin="{end:.3f}s" '
        f'repeatCount="indefinite"/></rect>'
    )
    return window(W, H, f"{HOST}: ~$ ./portrait.sh", "".join(parts))


if __name__ == "__main__":
    write(OUT, build(to_grid(SRC)))
