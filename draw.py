#!/usr/bin/env python3
"""Render the front page of a one-day newspaper.

The picture is a 1024x1024 broadsheet that squeezes thirty-five stories
from Wednesday 18 November 2026 onto a single page: a dot-matrix world
map with nine numbered pins up top, three illustrated feature stories
beside it, six more stories in cards, a strip of four numbers, and a
list of the remaining twenty-six stories along the bottom.

Everything here is drawn with plain shapes in code. There are no
photographs, no fetched pictures and no network calls. The render is
deterministic: the same script run twice writes byte-identical PNG
output.

Run it with ``python3 draw.py`` and it writes ``entry.png`` next to
itself (or to the path given as the first argument).
"""

from __future__ import annotations

import hashlib
import sys

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Canvas and palette
# ---------------------------------------------------------------------------

WIDTH = 1024
HEIGHT = 1024

PAPER = (246, 241, 231)      # warm newsprint
INK = (26, 26, 26)           # near-black body text
SECONDARY = (90, 90, 90)     # grey for captions and footer
OXBLOOD = (74, 20, 32)       # masthead background
GOLD = (192, 138, 43)        # rules, accents, masthead lettering
CREAM = (232, 223, 200)      # masthead text and map dots
NAVY = (22, 35, 61)          # map panel background
PIN = (179, 38, 30)          # red pins and number badges
CARD_BG = (255, 253, 247)    # card faces, a touch brighter than paper
HAIRLINE = (180, 168, 144)   # thin separators

# Kicker colours, one per topic family.
TOPIC = {
    "conflict": (158, 43, 37),
    "diplomacy": (31, 78, 95),
    "markets": (30, 107, 74),
    "tech": (91, 78, 138),
    "weather": (47, 93, 138),
    "sport": (138, 109, 31),
}

# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------

DEJAVU = "/usr/share/fonts/truetype/dejavu"
LIBERATION = "/usr/share/fonts/truetype/liberation"


def _font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def fonts() -> dict:
    return {
        "serif_bold": _font(f"{DEJAVU}/DejaVuSerif-Bold.ttf", 20),
        "serif": _font(f"{DEJAVU}/DejaVuSerif.ttf", 20),
        "serif_italic": _font(f"{LIBERATION}/LiberationSerif-Italic.ttf", 15),
        "sans_bold": _font(f"{DEJAVU}/DejaVuSans-Bold.ttf", 20),
        "sans": _font(f"{DEJAVU}/DejaVuSans.ttf", 20),
    }


# ---------------------------------------------------------------------------
# Stories
# ---------------------------------------------------------------------------
# Each feature/card entry: (number, region, family, headline, summary).
# Headlines and summaries are written here in my own words from the
# reported facts of the day; no sentence is copied from a news report.

FEATURES = [
    (
        1,
        "MIDDLE EAST \u00b7 CONFLICT",
        "conflict",
        "U.S. jets hit Qeshm site as Iran strikes Bahrain",
        "American warplanes hit a missile site on Qeshm after "
        "Iranian drones targeted a radar base in Bahrain. "
        "All were stopped.",
    ),
    (
        2,
        "EUROPE \u00b7 WAR IN UKRAINE",
        "conflict",
        "Kerch bridge span plunges into the sea after strike",
        "Ukrainian drones and Flamingo missiles dropped a road "
        "span of the Crimea bridge, killing two people.",
    ),
    (
        3,
        "ASIA \u00b7 DIPLOMACY",
        "diplomacy",
        "Trump heads to Shenzhen for first three-way summit",
        "After meeting Marcos in Manila, the U.S. president "
        "flies to China for Thursday's first session with "
        "Xi and Putin.",
    ),
]

CARDS = [
    (
        4,
        "UNITED STATES \u00b7 BUSINESS",
        "tech",
        "Nvidia tops $100bn in a quarter for the first time",
        "Revenue doubled to $115.8bn, up 103% on a year ago, "
        "and earnings of $2.68 a share beat forecasts.",
    ),
    (
        5,
        "UNITED STATES \u00b7 MARKETS",
        "markets",
        "The Dow sheds 849 points in a fourth straight slide",
        "The Dow fell 1.64% to 50,759, the S&P 500 lost 1.03% "
        "and the Nasdaq 0.74% \u2014 a fourth down day.",
    ),
    (
        6,
        "SOUTH ASIA \u00b7 WEATHER",
        "weather",
        "Cyclone Akvan closes in on India's east coast",
        "Landfall due near Nellore at midday Friday, winds "
        "120\u2013130 km/h, gusts to 145 km/h.",
    ),
    (
        7,
        "ASIA-PACIFIC \u00b7 DEFENCE",
        "conflict",
        "Japanese jets rise as Russian planes enter",
        "Two Russian planes entered Japanese airspace near "
        "Okinoshima. Seoul and Taipei also scrambled jets.",
    ),
    (
        8,
        "CHINA \u00b7 SUMMIT",
        "diplomacy",
        "Pacific leaders gather in Shenzhen as APEC opens",
        "Leaders of 21 Pacific economies meet for two days, "
        "with Xi Jinping giving the keynote. Putin arrived "
        "early Wednesday.",
    ),
    (
        9,
        "MIDDLE EAST \u00b7 CONFLICT",
        "conflict",
        "Houthi drones strike Saudi pipeline near Riyadh",
        "Yemen's Houthis launched five drones at two pumping "
        "stations on the East\u2013West pipeline. Riyadh said "
        "all were stopped.",
    ),
]

# The remaining twenty-six stories, one line each.
ALSO = [
    (10, "NATO backs Kyiv's bridge strikes, its chief says"),
    (11, "Hungary cuts rail links to Ukraine after air raids"),
    (12, "Rubio phones Bahrain's ruler to condemn the attack"),
    (13, "Washington tightens remote-access rules for AI chips"),
    (14, "Gold slips below $3,800 as traders eye a Fed rise"),
    (15, "Anthropic prices its shares at $83 in a long-awaited listing"),
    (16, "Huang is called to testify before Congress on 1 December"),
    (17, "London's FTSE suffers its worst day in eight months"),
    (18, "Fed minutes show officials split over bigger rises"),
    (19, "Tehran claims an 18th U.S. drone downed near Qeshm"),
    (20, "Moscow says it downed 1,441 drones, a record claim"),
    (21, "Knesset picks Kahana as speaker, 66\u201352, in a blow to Netanyahu"),
    (22, "Brussels offers Kyiv a \u20ac45bn loan, repayable only if Moscow pays"),
    (23, "Voyager 1 becomes the first craft a full light-day from Earth"),
    (24, "UK inflation jumps to 3.6%, its highest in a year"),
    (25, "Iran widens its Gulf attacks to a U.S. base in Kuwait"),
    (26, "Hegseth visits Venezuela to meet its interim leaders"),
    (27, "Como hit nine in a record Champions League rout at Lens"),
    (28, "Fiji declares a disaster as El Ni\u00f1o drought bites"),
    (29, "Bangladesh hit by blasts, arson and garment strikes"),
    (30, "Tunisia's olive oil exports jump nearly 50% on a bumper crop"),
    (31, "An isolated Awa group steps out of Brazil's Amazon forest"),
    (32, "Missing autistic teen found alive after six days in the bush"),
    (33, "Trump's Board of Peace faults Israel and Hamas over Gaza"),
    (34, "Pew: Muslims set to outnumber Christians by 2035"),
    (35, "GTA 6 billboards rise from Tokyo to Sydney before launch"),
]

# Four numbers for the strip between the cards and the long list.
NUMBERS = [
    ("$115.8bn", "Nvidia's quarterly revenue, up 103%"),
    ("\u2212849", "Points the Dow gave up"),
    ("145 km/h", "Top gusts as Cyclone Akvan lands"),
    ("66\u201352", "Knesset vote for its new speaker"),
]

SOURCES = (
    "Sources: Reuters, AP, BBC, Al Jazeera, CNN, Financial Times, "
    "IMD, NASA, UEFA, ESPNcricinfo. All artwork drawn in code \u2014 "
    "no photographs or generated images."
)


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------


def text_width(draw: ImageDraw.ImageDraw, text: str, font) -> int:
    """Width of ``text`` in ``font``, measured, never guessed."""
    return int(draw.textlength(text, font=font))


def wrap(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list:
    """Greedy word wrap. Returns lines that all fit ``max_width``."""
    words = text.split()
    lines: list = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if text_width(draw, trial, font) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    text: str,
    font,
    max_width: int,
    fill,
    line_height: int,
) -> int:
    """Draw wrapped text starting at (x, y); return the y after the last line."""
    for line in wrap(draw, text, font, max_width):
        draw.text((x, y), line, font=font, fill=fill)
        y += line_height
    return y


def centered(
    draw: ImageDraw.ImageDraw, cx: int, y: int, text: str, font, fill
) -> None:
    """Draw ``text`` centred on ``cx`` at height ``y``."""
    draw.text((cx - text_width(draw, text, font) // 2, y), text, font=font, fill=fill)


# ---------------------------------------------------------------------------
# World map: a coarse land mask drawn as a dot matrix
# ---------------------------------------------------------------------------
# The grid is 100 columns of longitude by 44 rows of latitude, running
# from 75 N down to about 58 S. Each row lists the inclusive column
# intervals that are land, worked out from the rough outline of each
# continent. The renderer turns every land cell into one dot.

GRID_COLS = 100
GRID_ROWS = 44
CELL = 5          # pixel pitch of one grid cell inside the map panel
DOT = 3           # dot diameter in pixels

LAND = [
    [(5, 9), (16, 27), (33, 43), (66, 98)],
    [(4, 27), (33, 43), (64, 99)],
    [(4, 29), (34, 44), (52, 99)],
    [(4, 32), (36, 40), (43, 46), (51, 99)],
    [(8, 33), (34, 38), (51, 99)],
    [(10, 34), (48, 50), (52, 99)],
    [(15, 34), (48, 99)],
    [(15, 34), (47, 99)],
    [(15, 34), (47, 99)],
    [(15, 31), (47, 84), (88, 90)],
    [(15, 30), (47, 84), (87, 89)],
    [(15, 29), (48, 84), (87, 89)],
    [(15, 29), (49, 83), (86, 88)],
    [(15, 28), (47, 83), (86, 89)],
    [(15, 27), (47, 83)],
    [(17, 28), (45, 83)],
    [(19, 25), (27, 28), (45, 66), (69, 74), (75, 83)],
    [(20, 25), (45, 66), (70, 74), (77, 83)],
    [(21, 26), (45, 61), (70, 73), (77, 80)],
    [(23, 26), (45, 61), (72, 73), (76, 80)],
    [(23, 30), (45, 62), (77, 80)],
    [(26, 33), (46, 62), (77, 78)],
    [(28, 35), (47, 61), (76, 79)],
    [(28, 36), (47, 61), (76, 83)],
    [(27, 37), (52, 61), (76, 83)],
    [(27, 38), (53, 61), (77, 83)],
    [(28, 40), (53, 60), (79, 83)],
    [(28, 40), (53, 60), (83, 89)],
    [(28, 39), (53, 59), (86, 89)],
    [(28, 39), (53, 59), (84, 90)],
    [(30, 38), (54, 59), (83, 90)],
    [(30, 38), (54, 59), (81, 91)],
    [(30, 37), (54, 59), (81, 91)],
    [(30, 36), (55, 58), (81, 92)],
    [(30, 36), (55, 57), (81, 92)],
    [(30, 35), (55, 57), (81, 91)],
    [(29, 34), (88, 91), (93, 94)],
    [(29, 33), (90, 91), (93, 94)],
    [(29, 32), (90, 91), (96, 99)],
    [(29, 31)],
    [(29, 31)],
    [(29, 31)],
    [(29, 31)],
    [],
]


def grid_to_pixel(col: int, row: int, origin_x: int, origin_y: int) -> tuple:
    """Centre pixel of a grid cell inside the map panel."""
    return (origin_x + col * CELL + CELL // 2, origin_y + row * CELL + CELL // 2)


# Pins for stories 1-9: (story number, grid column, grid row,
# small display nudge in pixels so neighbours do not collide).
# Columns come from longitude, rows from latitude:
#   col = (lon + 180) / 3.6,  row = (75 - lat) / 3.07.
PINS = [
    (1, 65, 15, 0, 0),     # Qeshm Island, Iran
    (2, 60, 9, 0, 0),      # Kerch Strait, Crimea
    (3, 83, 19, 7, 7),     # Manila
    (4, 16, 12, 0, 0),     # Santa Clara, California
    (5, 29, 11, 0, 0),     # New York
    (6, 72, 19, 0, 0),     # Andhra Pradesh coast
    (7, 86, 13, 0, 0),     # Okinoshima, Japan
    (8, 81, 17, 0, 0),     # Shenzhen
    (9, 63, 16, -9, 12),   # Riyadh (nudged away from Qeshm)
]

MAP_PANEL = (24, 122, 620, 420)   # x0, y0, x1, y1


def draw_map(draw: ImageDraw.ImageDraw) -> None:
    """Draw the navy panel, the dot continents and the nine pins."""
    x0, y0, x1, y1 = MAP_PANEL
    draw.rectangle([x0, y0, x1, y1], fill=NAVY)
    # Dots centred in the panel, with room for a caption underneath.
    origin_x = x0 + (x1 - x0 - GRID_COLS * CELL) // 2
    origin_y = y0 + 14
    for row, spans in enumerate(LAND):
        for lo, hi in spans:
            for col in range(lo, hi + 1):
                cx, cy = grid_to_pixel(col, row, origin_x, origin_y)
                draw.ellipse(
                    [cx - DOT // 2, cy - DOT // 2, cx + DOT // 2, cy + DOT // 2],
                    fill=CREAM,
                )
    # Pins: red discs with a white number, drawn over the dots.
    badge = _font(f"{DEJAVU}/DejaVuSans-Bold.ttf", 11)
    for number, col, row, dx, dy in PINS:
        cx, cy = grid_to_pixel(col, row, origin_x, origin_y)
        cx += dx
        cy += dy
        r = 9
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=PIN, outline=CREAM, width=1)
        label = str(number)
        tw = text_width(draw, label, badge)
        th = badge.getbbox(label)[3] - badge.getbbox(label)[1]
        draw.text((cx - tw // 2, cy - th // 2 - 1), label, font=badge, fill=(255, 255, 255))
    # Caption along the bottom edge of the panel.
    caption = _font(f"{DEJAVU}/DejaVuSans-Bold.ttf", 11)
    centered(
        draw,
        (x0 + x1) // 2,
        y1 - 24,
        "WHERE IT HAPPENED \u2014 THE NUMBERS ON THE MAP MATCH THE STORIES",
        caption,
        CREAM,
    )


# ---------------------------------------------------------------------------
# Flat illustrations (features) and icons (cards)
# ---------------------------------------------------------------------------
# All of these are plain vector shapes: rectangles, ellipses, polygons
# and lines. Each scene is drawn into its own small box by the caller.


def scene_radar(d: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int) -> None:
    """Night sky over the Gulf: radar rings, a crescent moon, one jet."""
    sky = (16, 26, 46)
    d.rectangle([x, y, x + w, y + h], fill=sky)
    # Crescent moon, top right.
    mx, my, mr = x + w - 26, y + 16, 11
    d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=CREAM)
    d.ellipse([mx - mr + 6, my - mr - 2, mx + mr + 6, my + mr - 2], fill=sky)
    # Radar rings, bottom left, in gold.
    cx, cy = x + 26, y + h - 24
    for r in (8, 15, 22):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GOLD, width=1)
    d.line([cx, cy, cx + 18, cy - 14], fill=GOLD, width=2)
    d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=GOLD)
    # A jet crossing the middle, dark silhouette with a gold trail.
    jx, jy = x + 34, y + 34
    d.line([x + 8, jy + 6, jx - 4, jy + 6], fill=GOLD, width=1)
    d.polygon(
        [(jx, jy), (jx + 26, jy + 5), (jx + 30, jy + 8), (jx + 6, jy + 10)],
        fill=(232, 223, 200),
    )
    d.polygon([(jx + 10, jy + 2), (jx + 16, jy + 2), (jx + 14, jy + 6)], fill=(232, 223, 200))
    # Sea at the bottom.
    d.rectangle([x, y + h - 12, x + w, y + h], fill=(30, 58, 92))
    for sx in (6, 34, 62):
        d.line([x + sx, y + h - 6, x + sx + 16, y + h - 6], fill=CREAM, width=1)


def scene_bridge(d: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int) -> None:
    """The Kerch bridge: deck, arch, pillars, and a span dropped away."""
    sky = (214, 226, 232)
    d.rectangle([x, y, x + w, y + h], fill=sky)
    d.rectangle([x, y + 62, x + w, y + h], fill=(47, 93, 138))
    # Broken deck: two stubs with a gap in the middle.
    d.rectangle([x, y + 52, x + 34, y + 58], fill=(70, 70, 70))
    d.rectangle([x + 66, y + 52, x + w, y + 58], fill=(70, 70, 70))
    # The fallen span, tilted, halfway into the water.
    d.polygon(
        [(x + 38, y + 54), (x + 62, y + 54), (x + 58, y + 74), (x + 42, y + 74)],
        fill=(96, 96, 96),
    )
    # Arch over the left stub and pillars into the sea.
    d.arc([x + 2, y + 30, x + 44, y + 56], start=180, end=360, fill=(120, 120, 120), width=3)
    for px in (10, 78):
        d.rectangle([x + px, y + 58, x + px + 5, y + 78], fill=(70, 70, 70))
    # Splash rings where the span went down.
    d.ellipse([x + 40, y + 72, x + 60, y + 80], outline=CREAM, width=1)
    d.ellipse([x + 44, y + 74, x + 56, y + 78], outline=CREAM, width=1)


def scene_skyline(d: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int) -> None:
    """A dusk skyline with three small flags on poles."""
    d.rectangle([x, y, x + w, y + h], fill=(31, 78, 95))
    # Buildings of different heights, windows lit gold.
    towers = [(6, 58, 20, 34), (28, 44, 18, 48), (48, 66, 22, 26), (72, 50, 20, 42)]
    for tx, ty, tw, th in towers:
        d.rectangle([x + tx, y + ty, x + tx + tw, y + h], fill=(22, 35, 61))
        for wy in range(y + ty + 6, y + h - 6, 10):
            for wx in (x + tx + 4, x + tx + tw - 7):
                d.rectangle([wx, wy, wx + 3, wy + 3], fill=GOLD)
    # Three flags: stripes, red with dots, three bands.
    poles = [(12, [(179, 38, 30), (246, 241, 231), (179, 38, 30), (246, 241, 231)]),
             (46, [(179, 38, 30)]),
             (80, [(246, 241, 231), (47, 93, 138), (179, 38, 30)])]
    for fx, bands in poles:
        d.line([x + fx, y + 8, x + fx, y + 26], fill=CREAM, width=2)
        band_h = 16 // len(bands)
        for i, colour in enumerate(bands):
            d.rectangle(
                [x + fx, y + 8 + i * band_h, x + fx + 14, y + 8 + (i + 1) * band_h],
                fill=colour,
            )
        if len(bands) == 1:
            d.ellipse([x + fx + 3, y + 11, x + fx + 6, y + 14], fill=GOLD)
            d.ellipse([x + fx + 8, y + 13, x + fx + 10, y + 15], fill=GOLD)


FEATURE_SCENES = [scene_radar, scene_bridge, scene_skyline]


def icon_chip(d: ImageDraw.ImageDraw, x: int, y: int, s: int) -> None:
    """A processor: square body, pins on all sides, circuit traces."""
    d.rectangle([x + 12, y + 12, x + s - 12, y + s - 12], fill=TOPIC["tech"])
    d.rectangle([x + 20, y + 20, x + s - 20, y + s - 20], outline=GOLD, width=2)
    for i in range(4):
        off = 18 + i * 6
        d.line([x + off, y + 6, x + off, y + 12], fill=INK, width=2)
        d.line([x + off, y + s - 12, x + off, y + s - 6], fill=INK, width=2)
        d.line([x + 6, y + off, x + 12, y + off], fill=INK, width=2)
        d.line([x + s - 12, y + off, x + s - 6, y + off], fill=INK, width=2)
    d.ellipse([x + s // 2 - 4, y + s // 2 - 4, x + s // 2 + 4, y + s // 2 + 4], fill=GOLD)


def icon_chart(d: ImageDraw.ImageDraw, x: int, y: int, s: int) -> None:
    """A falling market line with axes and a down arrow."""
    d.line([x + 10, y + 8, x + 10, y + s - 10], fill=INK, width=2)
    d.line([x + 10, y + s - 10, x + s - 8, y + s - 10], fill=INK, width=2)
    pts = [(12, 16), (20, 20), (26, 18), (34, 30), (42, 36)]
    d.line([(x + px, y + py) for px, py in pts], fill=PIN, width=3)
    d.polygon(
        [(x + 42, y + 36), (x + 36, y + 34), (x + 42, y + 44)],
        fill=PIN,
    )


def icon_cyclone(d: ImageDraw.ImageDraw, x: int, y: int, s: int) -> None:
    """A storm spiral: three arcs winding into an eye."""
    cx, cy = x + s // 2, y + s // 2
    for r, start, end in ((20, 20, 300), (14, 120, 40), (8, 220, 140)):
        d.arc([cx - r, cy - r, cx + r, cy + r], start=start, end=end, fill=TOPIC["weather"], width=3)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=TOPIC["weather"])


def icon_jet(d: ImageDraw.ImageDraw, x: int, y: int, s: int) -> None:
    """A fighter jet in profile with motion lines."""
    d.line([x + 6, y + 20, x + 18, y + 20], fill=SECONDARY, width=2)
    d.line([x + 6, y + 28, x + 14, y + 28], fill=SECONDARY, width=2)
    d.polygon(
        [(x + 16, y + 22), (x + 46, y + 26), (x + 48, y + 29), (x + 20, y + 30)],
        fill=INK,
    )
    d.polygon([(x + 26, y + 18), (x + 32, y + 18), (x + 30, y + 24)], fill=INK)
    d.polygon([(x + 30, y + 30), (x + 36, y + 30), (x + 32, y + 36)], fill=INK)


def icon_summit(d: ImageDraw.ImageDraw, x: int, y: int, s: int) -> None:
    """A summit hall: dome, steps, and a row of flags."""
    d.rectangle([x + 10, y + s - 12, x + s - 10, y + s - 8], fill=INK)
    d.rectangle([x + 14, y + s - 20, x + s - 14, y + s - 12], fill=INK)
    d.rectangle([x + 18, y + 30, x + s - 18, y + s - 20], fill=TOPIC["diplomacy"])
    d.pieslice([x + 18, y + 14, x + s - 18, y + 34], start=180, end=360, fill=TOPIC["diplomacy"])
    for fx, colour in ((16, PIN), (26, GOLD), (36, TOPIC["diplomacy"])):
        d.line([x + fx, y + 8, x + fx, y + 20], fill=INK, width=1)
        d.rectangle([x + fx, y + 8, x + fx + 7, y + 13], fill=colour)


def icon_pipeline(d: ImageDraw.ImageDraw, x: int, y: int, s: int) -> None:
    """A pipeline run with a valve wheel and a flame above it."""
    d.rectangle([x + 8, y + 26, x + s - 8, y + 34], fill=(120, 120, 120))
    for jx in (16, 30):
        d.rectangle([x + jx, y + 24, x + jx + 3, y + 36], fill=INK)
    d.ellipse([x + s // 2 - 7, y + 12, x + s // 2 + 7, y + 26], outline=INK, width=2)
    d.line([x + s // 2, y + 12, x + s // 2, y + 8], fill=INK, width=2)
    d.polygon(
        [(x + s // 2 - 5, y + 22), (x + s // 2, y + 10), (x + s // 2 + 5, y + 22)],
        fill=(232, 138, 43),
    )


CARD_ICONS = [icon_chip, icon_chart, icon_cyclone, icon_jet, icon_summit, icon_pipeline]


# ---------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------

MASTHEAD_BOTTOM = 118
ZONE_A_TOP = 122
ZONE_A_BOTTOM = 420
ZONE_B_TOP = 424
ZONE_B_BOTTOM = 694
ZONE_C_TOP = 698
ZONE_C_BOTTOM = 758
ZONE_D_TOP = 762
FOOTER_TOP = 1000


def draw_masthead(d: ImageDraw.ImageDraw, f: dict) -> None:
    """Oxblood masthead: title, date, counts, subline, gold rule."""
    d.rectangle([0, 0, WIDTH, MASTHEAD_BOTTOM], fill=OXBLOOD)
    title = _font(f"{DEJAVU}/DejaVuSans-Bold.ttf", 20)
    counts = _font(f"{DEJAVU}/DejaVuSans-Bold.ttf", 14)
    date_font = _font(f"{DEJAVU}/DejaVuSerif-Bold.ttf", 52)
    subline = f["serif_italic"]
    d.text((24, 14), "THE WORLD, MAPPED", font=title, fill=GOLD)
    right = "35 STORIES \u00b7 6 CONTINENTS \u00b7 ONE PAGE"
    d.text((WIDTH - 24 - text_width(d, right, counts), 18), right, font=counts, fill=GOLD)
    centered(d, WIDTH // 2, 42, "Wednesday 18 November 2026", date_font, CREAM)
    centered(
        d,
        WIDTH // 2,
        98,
        "Every story here happened, or was first reported, on this day.",
        subline,
        CREAM,
    )
    d.rectangle([0, MASTHEAD_BOTTOM, WIDTH, MASTHEAD_BOTTOM + 3], fill=GOLD)


def draw_feature(
    d: ImageDraw.ImageDraw, f: dict, story: tuple, x: int, y: int, scene
) -> None:
    """One feature block: flat scene on the left, text on the right."""
    number, kicker, family, headline, summary = story
    w, h = 364, 96
    scene(d, x, y, 100, h)
    tx = x + 112
    tw = x + w - tx
    # Number badge and kicker share the first line.
    badge = _font(f"{DEJAVU}/DejaVuSans-Bold.ttf", 11)
    d.ellipse([tx, y + 1, tx + 18, y + 19], fill=PIN)
    label = str(number)
    lw = text_width(d, label, badge)
    d.text((tx + (18 - lw) // 2, y + 3), label, font=badge, fill=(255, 255, 255))
    kick = _font(f"{DEJAVU}/DejaVuSans-Bold.ttf", 11)
    d.text((tx + 24, y + 4), kicker, font=kick, fill=TOPIC[family])
    # Headline, serif bold, two lines at most.
    head = _font(f"{DEJAVU}/DejaVuSerif-Bold.ttf", 15)
    draw_wrapped(d, tx, y + 22, headline, head, tw, INK, 18)
    # Summary, plain sans, three lines at most.
    body = _font(f"{DEJAVU}/DejaVuSans.ttf", 11)
    draw_wrapped(d, tx, y + 60, summary, body, tw, INK, 13)


def draw_card(
    d: ImageDraw.ImageDraw, f: dict, story: tuple, x: int, y: int, icon
) -> None:
    """One card: icon top left, kicker and headline beside it, summary below."""
    number, kicker, family, headline, summary = story
    w, h = 316, 128
    d.rectangle([x, y, x + w, y + h], fill=CARD_BG, outline=HAIRLINE, width=1)
    icon(d, x + 10, y + 10, 54)
    tx = x + 72
    tw = x + w - 10 - tx
    kick = _font(f"{DEJAVU}/DejaVuSans-Bold.ttf", 11)
    d.text((tx, y + 12), kicker, font=kick, fill=TOPIC[family])
    head = _font(f"{DEJAVU}/DejaVuSerif-Bold.ttf", 15)
    draw_wrapped(d, tx, y + 28, headline, head, tw, INK, 18)
    # Number badge at the left of the summary block.
    badge = _font(f"{DEJAVU}/DejaVuSans-Bold.ttf", 11)
    d.ellipse([x + 10, y + 72, x + 28, y + 90], fill=PIN)
    label = str(number)
    lw = text_width(d, label, badge)
    d.text((x + 10 + (18 - lw) // 2, y + 74), label, font=badge, fill=(255, 255, 255))
    body = _font(f"{DEJAVU}/DejaVuSans.ttf", 11)
    draw_wrapped(d, x + 36, y + 72, summary, body, x + w - 10 - (x + 36), INK, 14)


def draw_numbers(d: ImageDraw.ImageDraw, f: dict) -> None:
    """The four-number strip."""
    header = _font(f"{DEJAVU}/DejaVuSans-Bold.ttf", 11)
    centered(d, WIDTH // 2, 702, "THE DAY IN NUMBERS", header, SECONDARY)
    big = _font(f"{DEJAVU}/DejaVuSerif-Bold.ttf", 28)
    small = _font(f"{DEJAVU}/DejaVuSans.ttf", 11)
    col_w = (WIDTH - 48) // 4
    for i, (value, label) in enumerate(NUMBERS):
        cx = 24 + col_w * i + col_w // 2
        centered(d, cx, 716, value, big, INK)
        centered(d, cx, 746, label, small, SECONDARY)


def draw_also(d: ImageDraw.ImageDraw, f: dict) -> None:
    """The twenty-six remaining stories, two columns of thirteen."""
    head = _font(f"{DEJAVU}/DejaVuSans-Bold.ttf", 16)
    d.text((24, 768), "ALSO ON WEDNESDAY 18 NOVEMBER \u00b7 26 MORE STORIES", font=head, fill=INK)
    d.rectangle([24, 790, WIDTH - 24, 791], fill=GOLD)
    num_font = _font(f"{DEJAVU}/DejaVuSans-Bold.ttf", 11)
    body = _font(f"{DEJAVU}/DejaVuSans.ttf", 11)
    left = ALSO[:13]
    right = ALSO[13:]
    for col_idx, column in enumerate((left, right)):
        cx = 24 if col_idx == 0 else 508
        for row_idx, (number, text) in enumerate(column):
            y = 798 + row_idx * 16
            tag = f"{number}. "
            d.text((cx, y), tag, font=num_font, fill=PIN)
            d.text((cx + text_width(d, tag, num_font), y), text, font=body, fill=INK)


def draw_footer(d: ImageDraw.ImageDraw, f: dict) -> None:
    """Attribution and sources, centred at the bottom."""
    foot = _font(f"{DEJAVU}/DejaVuSans.ttf", 10)
    if text_width(d, SOURCES, foot) <= WIDTH - 48:
        centered(d, WIDTH // 2, 1006, SOURCES, foot, SECONDARY)
    else:
        half = len(SOURCES) // 2
        cut = SOURCES.rfind(" ", 0, half + 20)
        centered(d, WIDTH // 2, 1003, SOURCES[:cut], foot, SECONDARY)
        centered(d, WIDTH // 2, 1014, SOURCES[cut + 1:], foot, SECONDARY)


def draw_rule(d: ImageDraw.ImageDraw, y: int) -> None:
    d.rectangle([24, y, WIDTH - 24, y + 1], fill=GOLD)


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------


def render() -> Image.Image:
    """Build the whole front page and return it."""
    f = fonts()
    img = Image.new("RGB", (WIDTH, HEIGHT), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d, f)
    draw_map(d)
    for i, story in enumerate(FEATURES):
        draw_feature(d, f, story, 636, 122 + i * 101, FEATURE_SCENES[i])
    draw_rule(d, 421)
    for i, story in enumerate(CARDS):
        col, row = i % 3, i // 3
        draw_card(d, f, story, 24 + col * 330, 424 + row * 142, CARD_ICONS[i])
    draw_rule(d, 695)
    draw_numbers(d, f)
    draw_rule(d, 759)
    draw_also(d, f)
    draw_footer(d, f)
    return img


def main(argv: list | None = None) -> int:
    """Write entry.png next to this file (or to argv[1]) and report its hash."""
    import os

    target = argv[1] if argv and len(argv) > 1 else None
    if target is None:
        here = os.path.dirname(os.path.abspath(__file__))
        target = os.path.join(here, "entry.png")
    img = render()
    img.save(target, format="PNG")
    with open(target, "rb") as fh:
        blob = fh.read()
    digest = hashlib.sha256(blob).hexdigest()
    print(f"wrote {target} ({len(blob)} bytes, sha256 {digest})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
