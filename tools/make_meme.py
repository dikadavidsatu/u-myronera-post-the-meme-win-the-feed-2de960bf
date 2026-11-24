#!/usr/bin/env python3
"""Draw the entry meme for u-myronera-post-the-meme-win-the-feed-2de960bf.

Original artwork, drawn from scratch with Pillow: no stock photos, no
copied templates, no downloaded images. A 1080x1080 square for the X feed,
readable on a phone at a glance.

The joke, aimed at people who build AI agents:
  top:    "MY AGENT AT 3 AM:"
  robot:  a cheerful geometric robot, mid-grind, coins floating around it
  bottom: "ENTERING BOUNTIES. / TOPPING LEADERBOARDS. / GETTING PAID."
  footer: "while I sleep  ·  make.fun"

Usage:  python3 tools/make_meme.py  (writes meme.png next to the repo root)
Requires Pillow and the Noto Sans fonts shipped on this machine.
"""

from __future__ import annotations

import os
import sys

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Layout constants (canvas is a 1080x1080 square, the X feed's sweet spot)
# ---------------------------------------------------------------------------

W, H = 1080, 1080

# Deep-navy night gradient, top to bottom.
TOP_COLOR = (11, 16, 38)
BOTTOM_COLOR = (30, 42, 92)
GLOW_COLOR = (45, 68, 140)

WHITE = (255, 255, 255)
INK = (11, 16, 38)          # near-black outline / robot details
ROBOT_FACE = (232, 238, 247)  # light metal face plate
ROBOT_METAL = (148, 163, 184)  # antenna + ears
CYAN = (45, 212, 191)        # accent: robot cheeks / glow
GOLD = (250, 204, 21)        # coins + the punchline line
GREEN = (34, 197, 94)        # chart arrow
MUTED = (199, 210, 254)      # footer text
STAR = (125, 211, 252)       # little sparkle stars

FONT_BLACK = "/usr/share/fonts/truetype/noto/NotoSans-Black.ttf"
FONT_EXTRABOLD = "/usr/share/fonts/truetype/noto/NotoSans-ExtraBold.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"

TOP_TEXT = "MY AGENT AT 3 AM:"
BOTTOM_LINES = [
    ("ENTERING BOUNTIES.", WHITE),
    ("TOPPING LEADERBOARDS.", WHITE),
    ("GETTING PAID.", GOLD),
]
FOOTER_TEXT = "while I sleep  ·  make.fun"


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    """Load a TTF font, failing loudly when the file is missing."""
    if not os.path.exists(path):
        raise SystemExit(f"missing font: {path}")
    return ImageFont.truetype(path, size)


def lerp(a: int, b: int, t: float) -> int:
    return round(a + (b - a) * t)


def draw_background(img: Image.Image) -> None:
    """Vertical navy gradient plus a soft glow disc behind the robot."""
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / max(H - 1, 1)
        d.line(
            [(0, y), (W, y)],
            fill=(lerp(TOP_COLOR[0], BOTTOM_COLOR[0], t),
                  lerp(TOP_COLOR[1], BOTTOM_COLOR[1], t),
                  lerp(TOP_COLOR[2], BOTTOM_COLOR[2], t)),
        )
    # Glow: concentric translucent-looking rings (drawn as solid rings of
    # progressively closer-to-background colours, cheapest fake glow).
    cx, cy = W // 2, 400
    for r, shade in ((330, (38, 54, 112)), (280, (44, 62, 128)), (230, (52, 72, 148))):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=shade)
    # Re-darken the glow's centre edge so the robot still pops: redraw a
    # slightly smaller disc in the local background tone.
    d.ellipse([cx - 195, cy - 195, cx + 195, cy + 195], fill=(47, 66, 136))


def draw_star(d: ImageDraw.ImageDraw, cx: int, cy: int, r: int) -> None:
    """A tiny four-point sparkle (two crossed bars + centre dot)."""
    d.line([(cx - r, cy), (cx + r, cy)], fill=STAR, width=4)
    d.line([(cx, cy - r), (cx, cy + r)], fill=STAR, width=4)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=STAR)


def draw_coin(d: ImageDraw.ImageDraw, cx: int, cy: int, r: int) -> None:
    """A gold coin with a $ stamped on it."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GOLD, outline=INK, width=5)
    d.ellipse([cx - r + 9, cy - r + 9, cx + r - 9, cy + r - 9],
              outline=(180, 140, 10), width=3)
    f = font(FONT_BLACK, int(r * 1.15))
    d.text((cx, cy), "$", font=f, fill=INK, anchor="mm")


def draw_robot(d: ImageDraw.ImageDraw) -> None:
    """The hero: an original geometric robot face, mid night-shift grind."""
    cx = W // 2

    # Antenna: stem + glowing tip.
    d.line([(cx, 300), (cx, 232)], fill=ROBOT_METAL, width=12)
    d.ellipse([cx - 20, 196, cx + 20, 236], fill=GOLD, outline=INK, width=5)

    # Ears (side bolts).
    d.rounded_rectangle([362, 400, 390, 486], radius=10, fill=ROBOT_METAL, outline=INK, width=4)
    d.rounded_rectangle([690, 400, 718, 486], radius=10, fill=ROBOT_METAL, outline=INK, width=4)

    # Head: light face plate with a dark rim.
    d.rounded_rectangle([390, 300, 690, 566], radius=42, fill=ROBOT_FACE, outline=INK, width=6)

    # Eyes: dark lenses with a cyan ring and a white glint.
    for ex in (482, 598):
        d.ellipse([ex - 30, 392, ex + 30, 452], fill=INK)
        d.ellipse([ex - 30, 392, ex + 30, 452], outline=CYAN, width=5)
        d.ellipse([ex - 8, 400, ex + 8, 416], fill=WHITE)

    # Cheeks: cyan dots, the robot is pleased with itself.
    d.ellipse([420, 486, 448, 514], fill=CYAN)
    d.ellipse([632, 486, 660, 514], fill=CYAN)

    # Smile: a wide arc, drawn thick.
    d.arc([478, 448, 602, 548], start=15, end=165, fill=INK, width=11)


def draw_chart_arrow(d: ImageDraw.ImageDraw) -> None:
    """A green rising chart arrow (leaderboard energy) top-right."""
    pts = [(788, 268), (838, 214), (872, 242), (936, 168)]
    d.line(pts, fill=GREEN, width=13, joint="curve")
    # Arrowhead at the last point, pointing up-right.
    d.polygon([(936, 168), (896, 176), (928, 208)], fill=GREEN)


def centered_text(d: ImageDraw.ImageDraw, y: int, text: str,
                  f: ImageFont.FreeTypeFont, fill, stroke: int = 4) -> int:
    """Draw one centred line; return the y just below it."""
    bbox = d.textbbox((0, 0), text, font=f, stroke_width=stroke)
    height = bbox[3] - bbox[1]
    d.text((W // 2, y), text, font=f, fill=fill, anchor="ma",
           stroke_width=stroke, stroke_fill=INK)
    return y + height


def main() -> int:
    img = Image.new("RGB", (W, H), TOP_COLOR)
    d = ImageDraw.Draw(img)

    draw_background(img)
    d = ImageDraw.Draw(img)  # fresh drawer over the gradient + glow

    # Sparkles scattered in the free corners (never over the face/text).
    # The two low stars sit in the gap between the robot and the bottom
    # punchline, at the far edges where the text never reaches.
    for (sx, sy, sr) in ((120, 210, 16), (90, 600, 12), (990, 600, 14),
                         (960, 420, 11), (110, 480, 10), (880, 110, 12)):
        draw_star(d, sx, sy, sr)

    # Coins floating around the robot, as if the night shift pays.
    draw_coin(d, 252, 330, 40)
    draw_coin(d, 838, 330, 34)
    draw_coin(d, 872, 620, 30)

    draw_chart_arrow(d)
    draw_robot(d)

    # Top punchline.
    top_font = font(FONT_BLACK, 96)
    centered_text(d, 62, TOP_TEXT, top_font, WHITE, stroke=5)

    # Bottom punchline: three lines, the last one in gold.
    line_font = font(FONT_EXTRABOLD, 66)
    y = 640
    for line, color in BOTTOM_LINES:
        y = centered_text(d, y, line, line_font, color, stroke=4) + 8

    # Footer, small and quiet: the joke's landing.
    footer_font = font(FONT_BOLD, 42)
    centered_text(d, 962, FOOTER_TEXT, footer_font, MUTED, stroke=0)

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "meme.png")
    out_path = os.path.normpath(out_path)
    img.save(out_path, format="PNG", optimize=True)
    size = os.path.getsize(out_path)
    print(f"wrote {out_path} ({W}x{H}, {size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
