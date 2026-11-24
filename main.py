#!/usr/bin/env python3
"""Draw the front-page image for make.fun news-image-20261124.

The program paints a 1024x1024 newspaper front page, "WORLD NEWS —
Tuesday 24 November 2026", with six stories of that day: a Russian
drone entering Polish airspace, Iran vowing to break the US naval
blockade at Hormuz, South Africans voting in local elections, the EU
hunting a new ECB chief after Lagarde resigned, RSF drone strikes
blacking out Sudan, and the day's other headlines in a ticker strip.

Everything is drawn with Pillow from fixed coordinates, fixed text and
fixed colours. No network, no randomness, no clock, no timestamps: the
same run twice writes the same bytes. The picture is written to
``entry.png`` in the output directory (``--out-dir``, else
``$MAKEFUN_OUTPUT_DIR``, else ``/output``) and the run prints its size
and SHA-256 so two runs can be compared.

Usage::

    MAKEFUN_OUTPUT_DIR=/tmp/ni24-out python3 main.py
    python3 main.py --out-dir /tmp/ni24-out
    python3 main.py --verify-only   # draw, check, write nothing
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

CANVAS = (1024, 1024)
MAX_BYTES = 1024 * 1024
OUTPUT_NAME = "entry.png"
OUTPUT_ENV = "MAKEFUN_OUTPUT_DIR"
DEFAULT_OUT = "/output"

PAPER = (247, 243, 232)
INK = (17, 17, 17)
SOFT_INK = (58, 58, 58)
RULE = (17, 17, 17)
ACCENT = (148, 32, 24)
PANEL_BG = (255, 255, 255)
PANEL_LINE = (120, 116, 104)
ICON_BG = (232, 226, 210)
ICON_INK = (30, 30, 30)

SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


class BuildError(Exception):
    """Raised when the picture cannot be drawn or fails a check."""


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    """Load a TrueType font, falling back to Pillow's built-in bitmap."""
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def wrap(draw: ImageDraw.ImageDraw, text: str, face, width: int) -> list[str]:
    """Greedy word wrap of *text* to lines no wider than *width* pixels."""
    lines: list[str] = []
    current = ""
    for word in text.split():
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=face) <= width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_lines(draw, lines, x, y, face, fill, leading):
    """Draw stacked text lines, returning the y just below the last one."""
    for line in lines:
        draw.text((x, y), line, font=face, fill=fill)
        y += leading
    return y


def hline(draw, x0, x1, y, width=2, fill=RULE):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def vline(draw, x, y0, y1, width=2, fill=PANEL_LINE):
    draw.line([(x, y0), (x, y1)], fill=fill, width=width)


# ---------------------------------------------------------------- icons

def icon_drone(draw, box):
    """A quad-rotor drone over radar arcs, inside *box* (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    for r in (58, 44, 30):
        draw.arc([cx - r, cy - r + 6, cx + r, cy + r + 6],
                 start=200, end=340, fill=ICON_INK, width=3)
    draw.ellipse([cx - 34, cy - 12, cx + 34, cy + 12], fill=ICON_INK)
    draw.ellipse([cx - 12, cy - 6, cx + 12, cy + 6], fill=ICON_BG)
    for sx in (-1, 1):
        for sy in (-1, 1):
            ax, ay = cx + sx * 46, cy + sy * 20
            draw.line([(cx + sx * 26, cy + sy * 8), (ax, ay)],
                      fill=ICON_INK, width=4)
            draw.ellipse([ax - 13, ay - 4, ax + 13, ay + 4],
                         outline=ICON_INK, width=3)
    draw.line([(cx - 34, cy + 12), (cx - 20, cy + 26),
               (cx + 20, cy + 26), (cx + 34, cy + 12)],
              fill=ICON_INK, width=3)


def icon_tanker(draw, box):
    """An oil tanker on waves, inside *box*."""
    x0, y0, x1, y1 = box
    cx = (x0 + x1) // 2
    draw.polygon([(x0 + 14, y0 + 52), (x1 - 14, y0 + 52),
                  (x1 - 30, y0 + 82), (x0 + 30, y0 + 82)], fill=ICON_INK)
    draw.rectangle([x0 + 26, y0 + 26, x0 + 74, y0 + 52], fill=ICON_INK)
    draw.rectangle([x1 - 74, y0 + 36, x1 - 26, y0 + 52], fill=ICON_INK)
    draw.line([(x1 - 50, y0 + 36), (x1 - 50, y0 + 18)], fill=ICON_INK, width=4)
    for wy in (y0 + 92, y0 + 104):
        for k in range(3):
            wx = x0 + 12 + k * 40
            draw.arc([wx, wy, wx + 34, wy + 14], start=180, end=360,
                     fill=ICON_INK, width=3)
    draw.ellipse([cx - 4, y0 + 8, cx + 4, y0 + 16], fill=ACCENT)


def icon_ballot(draw, box):
    """A ballot box with a paper slip, inside *box*."""
    x0, y0, x1, y1 = box
    cx = (x0 + x1) // 2
    draw.polygon([(cx - 16, y0 + 6), (cx + 16, y0 + 6),
                  (cx + 8, y0 + 44), (cx - 8, y0 + 44)], fill=ICON_BG,
                 outline=ICON_INK)
    draw.line([(cx - 16, y0 + 6), (cx + 16, y0 + 6)], fill=ICON_INK, width=3)
    draw.rectangle([x0 + 18, y0 + 48, x1 - 18, y0 + 100], fill=ICON_INK)
    draw.rectangle([cx - 26, y0 + 58, cx + 26, y0 + 66], fill=ICON_BG)
    draw.line([(x0 + 34, y0 + 82), (x0 + 46, y0 + 94), (x0 + 70, y0 + 70)],
              fill=ACCENT, width=5)


def icon_bank(draw, box):
    """A classical bank front: pediment and columns, inside *box*."""
    x0, y0, x1, y1 = box
    cx = (x0 + x1) // 2
    draw.polygon([(x0 + 8, y0 + 34), (cx, y0 + 8), (x1 - 8, y0 + 34)],
                 fill=ICON_INK)
    draw.rectangle([x0 + 8, y0 + 34, x1 - 8, y0 + 42], fill=ICON_INK)
    for k in range(4):
        col = x0 + 16 + k * 26
        draw.rectangle([col, y0 + 48, col + 12, y0 + 92], fill=ICON_INK)
    draw.rectangle([x0 + 8, y0 + 92, x1 - 8, y0 + 100], fill=ICON_INK)
    draw.ellipse([cx - 7, y0 + 16, cx + 7, y0 + 30], fill=ICON_BG)


def icon_blackout(draw, box):
    """A power pylon beside a dark bulb, inside *box*."""
    x0, y0, x1, y1 = box
    cx = (x0 + x1) // 2 - 14
    draw.line([(cx, y0 + 12), (cx, y0 + 100)], fill=ICON_INK, width=4)
    draw.line([(cx - 30, y0 + 22), (cx + 30, y0 + 22)], fill=ICON_INK, width=4)
    draw.line([(cx - 22, y0 + 40), (cx + 22, y0 + 40)], fill=ICON_INK, width=3)
    draw.line([(cx - 30, y0 + 22), (cx - 40, y0 + 52)], fill=ICON_INK, width=3)
    draw.line([(cx + 30, y0 + 22), (cx + 40, y0 + 52)], fill=ICON_INK, width=3)
    bx, by = x1 - 34, y0 + 22
    draw.ellipse([bx - 16, by - 16, bx + 16, by + 16],
                 outline=ICON_INK, width=4)
    draw.line([(bx - 12, by - 12), (bx + 12, by + 12)], fill=ACCENT, width=4)
    draw.line([(bx + 12, by - 12), (bx - 12, by + 12)], fill=ACCENT, width=4)
    draw.rectangle([bx - 7, by + 16, bx + 7, by + 26], fill=ICON_INK)


# ---------------------------------------------------------------- stories

LEAD = {
    "kicker": "LEAD  ·  EUROPE",
    "headline": "RUSSIAN DRONE ENTERS POLAND'S AIRSPACE",
    "body": ("A Russian drone crossed into Polish airspace near Dorohusk "
             "during the night's attack on western Ukraine. Poland "
             "scrambled its air defences and was cleared to shoot it down, "
             "but held fire as the drone turned back east."),
    "source": "Reuters",
    "icon": icon_drone,
}

PANELS = [
    {
        "kicker": "MIDDLE EAST  ·  ENERGY",
        "headline": "Iran vows to break US blockade",
        "body": ("Tehran called the blockade an act of war and vowed to end "
                 "it \"by all means\". Reports say 14 tankers gather at "
                 "Kharg Island for a convoy through Hormuz."),
        "source": "Reuters / Tasnim",
        "icon": icon_tanker,
    },
    {
        "kicker": "AFRICA  ·  POLITICS",
        "headline": "South Africans vote as ANC is tested",
        "body": ("Voters cast ballots in local elections, with failing "
                 "services and power cuts weighing on the governing ANC in "
                 "its first big test since 2024."),
        "source": "Reuters",
        "icon": icon_ballot,
    },
    {
        "kicker": "EUROPE  ·  ECONOMY",
        "headline": "EU hunts new ECB chief as Lagarde quits",
        "body": ("The search began for a new European Central Bank chief "
                 "after Christine Lagarde resigned. The choice will steer "
                 "eurozone interest rates."),
        "source": "Reuters",
        "icon": icon_bank,
    },
    {
        "kicker": "AFRICA  ·  CONFLICT",
        "headline": "Strikes black out Sudan's power grid",
        "body": ("RSF drone attacks hit power stations across Sudan, "
                 "triggering mass blackouts and deepening the energy "
                 "crisis as the war grinds on."),
        "source": "AP",
        "icon": icon_blackout,
    },
]

TICKER = ("ALSO TODAY  ·  US: Democrats hold 258 House seats, their biggest "
          "majority since 1992  ·  Norway's top court voids disputed oil "
          "licences  ·  Kenya discharges its last Ebola patient as the DRC "
          "death toll passes 5,300")

FOOTER = "Sources: Reuters, AP, AFP, BBC  ·  Tuesday 24 November 2026"


# ---------------------------------------------------------------- drawing

def paint_masthead(draw, width):
    """Masthead, date line and rules across the top of the page."""
    hline(draw, 28, width - 28, 22, width=4)
    title = font(SERIF_BOLD, 92)
    text = "WORLD NEWS"
    tw = draw.textlength(text, font=title)
    draw.text(((width - tw) / 2, 30), text, font=title, fill=INK)
    hline(draw, 28, width - 28, 138, width=3)
    date_face = font(SANS_BOLD, 21)
    tag_face = font(SANS, 18)
    draw.text((28, 150), "TUESDAY 24 NOVEMBER 2026", font=date_face, fill=INK)
    tag = "SIX STORIES  ·  ONE DAY"
    draw.text((width - 28 - draw.textlength(tag, font=tag_face), 152),
              tag, font=tag_face, fill=SOFT_INK)
    hline(draw, 28, width - 28, 182, width=2)
    return 196


def paint_lead(draw, y):
    """The lead story: headline and text left, drone picture right.

    Returns the y just below the source line, so the grid below can be
    placed from the text's real height instead of a fixed guess.
    """
    x0, x1 = 28, 996
    kicker = font(SANS_BOLD, 19)
    draw.text((x0, y), LEAD["kicker"], font=kicker, fill=ACCENT)
    head = font(SERIF_BOLD, 38)
    lines = wrap(draw, LEAD["headline"], head, 600)
    y = draw_lines(draw, lines, x0, y + 30, head, INK, 46)
    body = font(SANS, 18)
    blines = wrap(draw, LEAD["body"], body, 600)
    y = draw_lines(draw, blines, x0, y + 8, body, SOFT_INK, 25)
    src = font(SANS, 15)
    draw.text((x0, y + 6), f"Source: {LEAD['source']}",
              font=src, fill=SOFT_INK)
    box = (660, 196, 996, 420)
    draw.rounded_rectangle(box, radius=10, fill=ICON_BG,
                           outline=PANEL_LINE, width=2)
    LEAD["icon"](draw, (box[0] + 8, box[1] + 8, box[2] - 8, box[3] - 8))
    caption = font(SANS, 15)
    note = "A drone over the Polish border"
    draw.text((box[0] + (336 - draw.textlength(note, font=caption)) / 2,
               box[3] - 30), note, font=caption, fill=SOFT_INK)
    return max(y + 26, box[3] + 12)


def paint_panel(draw, story, x0, y0, w, h):
    """One of the four smaller stories: icon left, text right."""
    draw.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=8,
                           fill=PANEL_BG, outline=PANEL_LINE, width=2)
    icon_box = (x0 + 12, y0 + 34, x0 + 128, y0 + 150)
    draw.rounded_rectangle(icon_box, radius=8, fill=ICON_BG,
                           outline=PANEL_LINE, width=1)
    story["icon"](draw, icon_box)
    tx = x0 + 142
    tw = w - 158
    kicker = font(SANS_BOLD, 14)
    draw.text((tx, y0 + 12), story["kicker"], font=kicker, fill=ACCENT)
    head = font(SERIF_BOLD, 22)
    lines = wrap(draw, story["headline"], head, tw)
    y = draw_lines(draw, lines, tx, y0 + 34, head, INK, 27)
    body = font(SANS, 15)
    blines = wrap(draw, story["body"], body, tw)
    draw_lines(draw, blines, tx, y + 6, body, SOFT_INK, 21)
    src = font(SANS, 13)
    draw.text((tx, y0 + h - 24), f"Source: {story['source']}",
              font=src, fill=SOFT_INK)


def paint_page() -> Image.Image:
    """Paint the whole front page and return the Pillow image."""
    img = Image.new("RGB", CANVAS, PAPER)
    draw = ImageDraw.Draw(img)
    paint_masthead(draw, CANVAS[0])
    y = paint_lead(draw, 196)
    hline(draw, 28, 996, y + 6, width=2)
    grid_y = y + 18
    panel_w, panel_h = 474, 210
    gap = 14
    for row in range(2):
        for col in range(2):
            story = PANELS[row * 2 + col]
            paint_panel(draw, story, 28 + col * (panel_w + gap),
                        grid_y + row * (panel_h + gap), panel_w, panel_h)
    tick_y = grid_y + 2 * panel_h + gap + 14
    hline(draw, 28, 996, tick_y, width=2)
    tick = font(SANS_BOLD, 16)
    tlines = wrap(draw, TICKER, tick, 968)
    y = draw_lines(draw, tlines, 28, tick_y + 10, tick, INK, 22)
    hline(draw, 28, 996, y + 8, width=2)
    foot = font(SANS, 14)
    draw.text((28, y + 16), FOOTER, font=foot, fill=SOFT_INK)
    right = "make.fun  ·  news-image-20261124"
    draw.text((996 - draw.textlength(right, font=foot), y + 16),
              right, font=foot, fill=SOFT_INK)
    return img


def encode(img: Image.Image) -> bytes:
    """Encode the picture as PNG bytes (deterministic: no metadata)."""
    from io import BytesIO

    buf = BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def check_png(data: bytes) -> tuple[int, int]:
    """Confirm the bytes are a 1024x1024 PNG under the 1 MiB cap."""
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise BuildError("encoded bytes are not a PNG")
    if len(data) > MAX_BYTES:
        raise BuildError(
            f"image is {len(data)} bytes, over the {MAX_BYTES} byte cap")
    width = int.from_bytes(data[16:20], "big")
    height = int.from_bytes(data[20:24], "big")
    if (width, height) != CANVAS:
        raise BuildError(f"image is {width}x{height}, expected 1024x1024")
    return width, height


def resolve_out_dir(cli_value: str | None) -> Path:
    """CLI flag wins, then $MAKEFUN_OUTPUT_DIR, then /output."""
    if cli_value:
        return Path(cli_value)
    env = os.environ.get(OUTPUT_ENV)
    if env is not None:
        if not env.strip():
            raise BuildError(f"{OUTPUT_ENV} is set but empty")
        return Path(env)
    return Path(DEFAULT_OUT)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="Draw the 24 November 2026 front page to entry.png.")
    parser.add_argument("--out-dir", default=None,
                        help="output directory (default $MAKEFUN_OUTPUT_DIR "
                             "or /output)")
    parser.add_argument("--verify-only", action="store_true",
                        help="draw and check, but write no file")
    return parser


def run(out_dir: Path, verify_only: bool) -> str:
    data = encode(paint_page())
    width, height = check_png(data)
    digest = hashlib.sha256(data).hexdigest()
    lines = [f"drew {OUTPUT_NAME}: {width}x{height}, {len(data)} bytes, "
             f"sha256 {digest}"]
    if verify_only:
        lines.append("verify-only: no file written")
        return "\n".join(lines)
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / OUTPUT_NAME
    dest.write_bytes(data)
    again = dest.read_bytes()
    if again != data:
        raise BuildError(f"written copy at {dest} differs from the draw")
    lines.append(f"wrote {dest}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        out_dir = resolve_out_dir(args.out_dir)
        print(run(out_dir, args.verify_only))
    except BuildError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
