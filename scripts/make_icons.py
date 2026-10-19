#!/usr/bin/env python3
"""Write icons/: a 3×3 grid of checked days as SVG plus PNG sizes for browsers, iOS and Android."""
import os

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "icons")
BLUE = "#2a78d6"
SURFACE = "#fcfcfb"

# Cells on a 16-unit grid: 4 wide with a 2-unit gap, corner radius 1. 1 = done, 0 = missed (faint).
GRID = [[1, 1, 0], [0, 1, 1], [1, 1, 1]]
FAINT = 0.28
CELLS = [(1 + c * 5, 1 + r * 5, on) for r, row in enumerate(GRID) for c, on in enumerate(row)]

SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">
{}
</svg>
""".format("\n".join(f'  <rect x="{x}" y="{y}" width="4" height="4" rx="1" fill="{BLUE}"{"" if on else f' fill-opacity="{FAINT}"'}/>'
                     for x, y, on in CELLS))


def png(size, background, pad):
    """Draw at 4x and downsample for smooth edges. pad = share of the canvas left empty on each side."""
    s = size * 4
    img = Image.new("RGBA", (s, s), background or (0, 0, 0, 0))
    unit = s * (1 - 2 * pad) / 16
    off = s * pad
    blue = tuple(int(BLUE[i:i + 2], 16) for i in (1, 3, 5))
    for x, y, on in CELLS:
        layer = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        ImageDraw.Draw(layer).rounded_rectangle([off + x * unit, off + y * unit, off + (x + 4) * unit, off + (y + 4) * unit],
                                                radius=unit, fill=blue + (255 if on else round(255 * FAINT),))
        img = Image.alpha_composite(img, layer)
    return img.resize((size, size), Image.LANCZOS)


def main():
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, "favicon.svg"), "w").write(SVG)
    png(32, None, 0).save(os.path.join(OUT, "favicon-32.png"))
    # Home-screen icons need an opaque background and room around the mark (iOS/Android crop the corners).
    png(180, SURFACE, 0.2).save(os.path.join(OUT, "apple-touch-icon.png"))
    png(192, SURFACE, 0.2).save(os.path.join(OUT, "icon-192.png"))
    png(512, SURFACE, 0.2).save(os.path.join(OUT, "icon-512.png"))
    print("icons:", ", ".join(sorted(os.listdir(OUT))))


if __name__ == "__main__":
    main()
