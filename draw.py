#!/usr/bin/env python3
"""Draw the news-image-20261118 entry: "THE WORLD, MAPPED".

A 1024x1024 editorial infographic summing up Wednesday 18 November 2026
in 35 stories. Pure PIL, fully deterministic: no randomness, no clock, no
network. Run:  python3 draw.py [out.png]
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

# --- palette (brief section 4) -------------------------------------------
PAPER = (246, 241, 231)      # #F6F1E7 warm cream
OXBLOOD = (74, 20, 32)       # #4A1420 masthead
GOLD = (192, 138, 43)        # #C08A2B rules / accents
INK = (26, 26, 26)           # #1A1A1A main text
GREY = (90, 90, 90)          # #5A5A5A secondary text
RED = (179, 38, 30)          # #B3261E pins / numbers
NAVY = (22, 35, 61)          # #16233D map panel
DOT = (232, 223, 200)        # #E8DFC8 map dots
CARD_BG = (252, 250, 244)    # near-paper card panel
CARD_LINE = (216, 205, 184)  # card border
CREAM = (246, 241, 231)

KICKER_COLORS = {
    "conflict": (158, 43, 37),
    "diplomacy": (31, 78, 95),
    "markets": (30, 107, 74),
    "tech": (91, 78, 138),
    "weather": (47, 93, 138),
    "culture": (138, 109, 31),
}

# --- fonts (present on this VM) -------------------------------------------
FD = "/usr/share/fonts/truetype/dejavu"
FL = "/usr/share/fonts/truetype/liberation"


def font(path, size):
    return ImageFont.truetype(path, size)


F_SERIF_B = lambda s: font(f"{FD}/DejaVuSerif-Bold.ttf", s)      # display/headline
F_SANS_B = lambda s: font(f"{FD}/DejaVuSans-Bold.ttf", s)        # kicker/numbers
F_SANS = lambda s: font(f"{FD}/DejaVuSans.ttf", s)               # body/list
F_SERIF_I = lambda s: font(f"{FL}/LiberationSerif-Italic.ttf", s)  # subline

# --- world landmask: 96 x 48 equirectangular grid, rows of (start, end) ---
# Composed from coarse lat/lon knowledge; row r covers lat 90-3.125*r.
LAND = {
    0: [(36, 39)],
    1: [(36, 39)],
    2: [(34, 40), (25, 28), (51, 53)],
    3: [(33, 41), (24, 28), (51, 54)],
    4: [(33, 42), (22, 30), (51, 53), (60, 62), (72, 76)],
    5: [(4, 10), (14, 22), (34, 42), (51, 53), (66, 95)],
    6: [(3, 11), (13, 26), (35, 42), (42, 44), (52, 56), (62, 95)],
    7: [(3, 12), (12, 30), (34, 41), (50, 95)],
    8: [(4, 13), (13, 33), (35, 40), (50, 95)],
    9: [(5, 13), (14, 35), (37, 39), (46, 48), (50, 95)],
    10: [(8, 12), (15, 35), (46, 48), (50, 53), (54, 95)],
    11: [(15, 33), (46, 48), (49, 95)],
    12: [(15, 33), (46, 95)],
    13: [(15, 33), (45, 91)],
    14: [(15, 33), (45, 86)],
    15: [(15, 30), (45, 49), (50, 53), (55, 60), (60, 63), (63, 68), (68, 84), (83, 86)],
    16: [(15, 29), (45, 49), (49, 53), (55, 60), (60, 65), (65, 68), (68, 72), (72, 84), (81, 83), (83, 86)],
    17: [(15, 29), (46, 51), (54, 86)],
    18: [(17, 28), (46, 51), (54, 65), (64, 68), (66, 72), (72, 77), (77, 80)],
    19: [(16, 28), (46, 56), (57, 63), (66, 72), (72, 77), (77, 80)],
    20: [(18, 25), (45, 56), (57, 64), (66, 71), (72, 77)],
    21: [(19, 26), (44, 57), (57, 63), (66, 70), (72, 79)],
    22: [(20, 26), (43, 50), (58, 63), (68, 69), (72, 78)],
    23: [(23, 27), (43, 50), (58, 62), (68, 69), (72, 77), (80, 81)],
    24: [(24, 28), (43, 50), (58, 60), (72, 77), (80, 81)],
    25: [(25, 28), (28, 32), (43, 49), (58, 60), (73, 80)],
    26: [(26, 30), (27, 34), (44, 49), (58, 59), (73, 80), (83, 85)],
    27: [(27, 35), (46, 59), (73, 80), (83, 86)],
    28: [(28, 36), (50, 59), (73, 81), (83, 86)],
    29: [(28, 38), (50, 59), (74, 82), (83, 87)],
    30: [(29, 39), (51, 59), (74, 82), (83, 87)],
    31: [(29, 38), (51, 59), (75, 82), (83, 87)],
    32: [(30, 38), (51, 59), (59, 61), (75, 81), (79, 88)],
    33: [(30, 38), (51, 59), (59, 61), (79, 89)],
    34: [(31, 37), (51, 58), (59, 60), (78, 89)],
    35: [(31, 37), (51, 57), (78, 89)],
    36: [(31, 35), (51, 57), (78, 89)],
    37: [(31, 35), (52, 57), (79, 88)],
    38: [(31, 34), (52, 56), (79, 87)],
    39: [(31, 33), (53, 55), (79, 86), (93, 95)],
    40: [(31, 32), (80, 85), (93, 95)],
    41: [(31, 31), (81, 84), (93, 94)],
    42: [(30, 31), (93, 94)],
    43: [(30, 30)],
    44: [(30, 30)],
    45: [(30, 30)],
    46: [(30, 30)],
    47: [],
}

# Pin positions in grid coords (col, row) for feature stories 1-9.
PINS = {
    1: (63, 20),   # Qeshm Island / Bahrain
    2: (58, 14),   # Crimea bridge
    3: (80, 24),   # Manila
    4: (15, 17),   # Santa Clara (Nvidia)
    5: (28, 16),   # New York (Wall Street)
    6: (69, 23),   # Andhra Pradesh coast
    7: (83, 17),   # Japan (Okinoshima)
    8: (78, 21),   # Shenzhen
    9: (60, 21),   # Riyadh (Saudi pipeline)
}

# --- story data (all verified 18 Nov 2026; see study brief) ---------------
# features: (number, kicker, kicker_family, headline, summary)
FEATURES = [
    (1, "MIDDLE EAST · CONFLICT", "conflict",
     "US–Iran trade fire over Bahrain and Qeshm",
     "US jets hit an IRGC site on Qeshm; Iran fired drones at Bahrain. All intercepted."),
    (2, "EUROPE · WAR IN UKRAINE", "conflict",
     "A span of the Crimea bridge falls into the sea",
     "Ukrainian drones and missiles destroyed a Kerch road span; two were killed."),
    (3, "ASIA · DIPLOMACY", "diplomacy",
     "Trump meets Marcos, then flies to Shenzhen",
     "Trump met Marcos in Manila; a first Xi–Putin trilateral is set for Thursday."),
]

# cards: (number, kicker, kicker_family, headline, summary, icon)
CARDS = [
    (4, "UNITED STATES · BUSINESS", "markets",
     "Nvidia's revenue doubles to $115.8bn",
     "Q3 sales rose 103% to a first $100bn-plus quarter; EPS $2.68 beat "
     "$2.47. Shares rose ~5% after hours.", "chip"),
    (5, "UNITED STATES · MARKETS", "markets",
     "Wall Street slides as the Dow drops 849",
     "The Dow fell 1.64% to 50,759; the S&P 500 lost 1.03%. A fourth "
     "straight day of losses.", "chart"),
    (6, "SOUTH ASIA · WEATHER", "weather",
     "Cyclone Akvan bears down on Andhra Pradesh",
     "The Bay of Bengal storm lands between Nellore and Visakhapatnam on "
     "Friday, with gusts to 145 km/h.", "cyclone"),
    (7, "ASIA-PACIFIC · DEFENCE", "diplomacy",
     "Japan scrambles jets as Russian planes enter",
     "Two Russian aircraft were suspected near Okinoshima on Tuesday; Seoul "
     "and Taipei also responded.", "jet"),
    (8, "CHINA · SUMMIT", "diplomacy",
     "APEC opens in Shenzhen with Xi keynote",
     "Leaders of 21 Pacific economies meet 18–19 November; Putin arrived "
     "in the early hours of the day.", "summit"),
    (9, "MIDDLE EAST · CONFLICT", "conflict",
     "Houthis launch drones at Saudi pipeline",
     "Yemen's Houthis sent five drones at two pump stations on the "
     "East–West pipeline near Riyadh.", "drone"),
]

# numbers strip: (big, label)
NUMBERS = [
    ("$115.8bn", "Nvidia quarterly revenue, up 103%"),
    ("−849", "Points lost by the Dow on Tuesday"),
    ("145 km/h", "Top gusts at Cyclone Akvan landfall"),
    ("3rd", "Iran attack on US targets in Bahrain"),
]

# "also" list, items 10-35: (number, one-line story)
ALSO = [
    (10, "NATO backs bridge strikes — Ukraine has the right to self-defence"),
    (11, "Hungary ends rail links to Ukraine after Russian air strikes"),
    (12, "Rubio calls Bahrain's leader to condemn the Iran attacks"),
    (13, "US tightens AI-chip remote-access rules for exports to China"),
    (14, "Gold breaks below $3,800 as markets brace for a Fed hike"),
    (15, "Anthropic IPO looms as investors await the first offering"),
    (16, "Huang to testify before Congress on 1 December"),
    (17, "London's FTSE suffers its worst day in eight months, −1.76%"),
    (18, "Fed October minutes due; UK October inflation at 07:00"),
    (19, "Iran claims an 18th US drone downed — an MQ-1 south of Qeshm"),
    (20, "Moscow says it downed 1,441 drones — a record claim"),
    (21, "Knesset picks Kahana as speaker, 66–52, in a blow to Netanyahu"),
    (22, "South Korea holds emergency meeting over a possible Java flaw"),
    (23, "Asia stocks snap their losing streak on the Nvidia beat"),
    (24, "Tashima bids for the FIFA presidency, a first for Japan"),
    (25, "Chip curbs threaten the US–China trade truce"),
    (26, "Illinois man held over a threat to blow up a biofuels plant"),
    (27, "UK hands a US Army officer to US military in an espionage probe"),
    (28, "France: 'not co-belligerent' in Ukraine, minister says"),
    (29, "Top UN court to rule on the Myanmar genocide case on Thursday"),
    (30, "Canada and China extend trade deals as Xi meets Carney"),
    (31, "Britain sanctions Israeli settlement firms over the two-state push"),
    (32, "Guatemala electoral-offences prosecutor wounded in an attack"),
    (33, "Fiji declares a disaster over the El Niño drought"),
    (34, "COP31 talks hit deadlock on climate finance in Antalya"),
    (35, "Sudan: UN confirms more than 2,230 civilian deaths"),
]

# --- text helpers ----------------------------------------------------------
def text_w(fnt, s):
    b = fnt.getbbox(s)
    return b[2] - b[0]


def wrap(fnt, text, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if text_w(fnt, trial) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(d, x, y, lines, fnt, fill, leading=None):
    """Draw lines top-left at (x, y); returns the y just below the block."""
    if leading is None:
        leading = int(fnt.size * 1.18)
    for ln in lines:
        d.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def draw_tracked(d, x, y, text, fnt, fill, tracking=2):
    """Draw text with extra letter spacing; returns the width used."""
    cx = x
    for ch in text:
        d.text((cx, y), ch, font=fnt, fill=fill)
        cx += text_w(fnt, ch) + tracking
    return cx - x - tracking


def fit_lines(fnt, text, max_w, max_lines):
    """Wrap text to at most max_lines; ellipsize the last line if needed."""
    lines = wrap(fnt, text, max_w)
    if len(lines) <= max_lines:
        return lines
    lines = lines[:max_lines]
    while lines and text_w(fnt, lines[-1] + "…") > max_w:
        lines[-1] = lines[-1][:-1].rstrip()
    lines[-1] = lines[-1].rstrip() + "…"
    return lines


# --- map -------------------------------------------------------------------
def draw_map(d, x0, y0, w, h):
    """Navy panel with a cream dot-matrix world map and numbered red pins."""
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=10, fill=NAVY)
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=10, outline=GOLD, width=1)
    label = "WHERE THE NEWS HAPPENED — NUMBERS MATCH THE STORIES"
    lf = F_SANS_B(11)
    d.text((x0 + (w - text_w(lf, label)) // 2, y0 + 10), label, font=lf,
           fill=(200, 190, 160))
    mx0, my0 = x0 + 12, y0 + 34
    mw, mh = w - 24, h - 46
    cw, ch = mw / 96.0, mh / 48.0
    for r, spans in LAND.items():
        cy = my0 + (r + 0.5) * ch
        for a, b in spans:
            for c in range(a, b + 1):
                cx = mx0 + (c + 0.5) * cw
                d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=DOT)
    pf = F_SANS_B(11)
    for num, (gc, gr) in sorted(PINS.items()):
        px = mx0 + (gc + 0.5) * cw
        py = my0 + (gr + 0.5) * ch
        d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=RED,
                  outline=CREAM, width=2)
        s = str(num)
        d.text((px - text_w(pf, s) / 2, py - 7), s, font=pf, fill=CREAM)


# --- flat vector illustrations (feature strips, 96 x 94) --------------------
def illo_bridge(d, x, y, w, h):
    """Kerch bridge: pale sky, sea, deck with a broken span falling."""
    d.rectangle([x, y, x + w, y + h], fill=(214, 226, 238))
    d.rectangle([x, y + int(h * 0.62), x + w, y + h], fill=(47, 93, 138))
    # towers
    d.rectangle([x + 18, y + 22, x + 23, y + int(h * 0.62)], fill=OXBLOOD)
    d.rectangle([x + w - 23, y + 22, x + w - 18, y + int(h * 0.62)], fill=OXBLOOD)
    # deck, left segment level, right segment broken and tilted
    d.rectangle([x + 6, y + 34, x + w // 2 - 6, y + 40], fill=OXBLOOD)
    d.polygon([(x + w // 2 + 4, y + 38), (x + w - 8, y + 52),
               (x + w - 8, y + 58), (x + w // 2 + 4, y + 44)], fill=OXBLOOD)
    # falling span piece + splash
    d.polygon([(x + w // 2 - 2, y + 52), (x + w // 2 + 14, y + 58),
               (x + w // 2 + 10, y + 66), (x + w // 2 - 6, y + 60)], fill=GOLD)
    for dx in (-6, 0, 6):
        d.arc([x + w // 2 + dx - 7, y + int(h * 0.66), x + w // 2 + dx + 7,
               y + int(h * 0.80)], 180, 360, fill=CREAM, width=2)
    # cables
    d.line([x + 20, y + 24, x + 46, y + 36], fill=INK, width=1)
    d.line([x + w - 20, y + 24, x + w - 46, y + 36], fill=INK, width=1)


def illo_radar(d, x, y, w, h):
    """Night strike: dark sky, moon, radar sweep, jet silhouette."""
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    for sx, sy in ((10, 12), (30, 26), (72, 10), (58, 20), (86, 30), (44, 8)):
        d.ellipse([x + sx - 1, y + sy - 1, x + sx + 1, y + sy + 1], fill=DOT)
    d.ellipse([x + w - 30, y + 8, x + w - 10, y + 28], fill=(232, 223, 200))
    # radar arcs from bottom-left
    for r in (22, 36, 50):
        d.arc([x - r, y + h - r, x + r, y + h + r], 270, 360, fill=(120, 180, 120),
              width=2)
    d.line([x + 4, y + h - 6, x + 40, y + h - 46], fill=(120, 200, 120), width=2)
    # jet silhouette
    jx, jy = x + 52, y + 46
    d.polygon([(jx, jy - 12), (jx + 26, jy), (jx, jy + 4), (jx + 6, jy + 2),
               (jx - 2, jy + 12), (jx - 6, jy + 2)], fill=CREAM)
    d.line([jx - 14, jy + 2, jx - 2, jy + 2], fill=GOLD, width=2)


def illo_skyline(d, x, y, w, h):
    """Shenzhen skyline at dusk with three small flags (US, China, Russia)."""
    d.rectangle([x, y, x + w, y + h], fill=(240, 217, 168))
    d.ellipse([x + 66, y + 6, x + 88, y + 28], fill=(232, 170, 60))
    # buildings
    heights = [46, 62, 40, 70, 52, 34, 58]
    bx = x + 4
    for hh in heights:
        bw = (w - 8) // len(heights)
        d.rectangle([bx, y + h - hh, bx + bw - 3, y + h], fill=OXBLOOD)
        for wy in range(y + h - hh + 6, y + h - 4, 9):
            d.rectangle([bx + 3, wy, bx + 5, wy + 3], fill=GOLD)
        bx += bw
    # three flag poles with stripe flags
    for i, cols in enumerate((((179, 38, 30), (246, 241, 231), (31, 78, 95)),
                              ((222, 32, 32), (255, 220, 60)),
                              ((246, 241, 231), (31, 78, 95), (179, 38, 30)))):
        px = x + 14 + i * 32
        d.line([px, y + 8, px, y + 30], fill=INK, width=2)
        for j, c in enumerate(cols):
            d.rectangle([px + 2, y + 8 + j * 6, px + 16, y + 8 + j * 6 + 6],
                        fill=c)
        d.ellipse([px + 6, y + 12, px + 8, y + 14], fill=GOLD)


ILLOS = {1: illo_bridge, 2: illo_radar, 3: illo_skyline}


# --- small card icons (54 x 54 on a navy tile) ------------------------------
def icon_tile(d, x, y, kind):
    d.rounded_rectangle([x, y, x + 54, y + 54], radius=7, fill=NAVY)
    fg, ac = CREAM, GOLD
    if kind == "chip":
        d.rectangle([x + 16, y + 16, x + 38, y + 38], outline=fg, width=2)
        d.rectangle([x + 23, y + 23, x + 31, y + 31], fill=ac)
        for i in range(3):
            for xx, yy in ((x + 20 + i * 7, y + 10), (x + 20 + i * 7, y + 40),
                           (x + 10, y + 20 + i * 7), (x + 40, y + 20 + i * 7)):
                d.line([xx, yy, xx, yy + 4] if xx in (x + 10, x + 40) else
                       [xx, yy, xx + 4, yy], fill=fg, width=2)
    elif kind == "chart":
        d.line([x + 10, y + 44, x + 44, y + 44], fill=fg, width=2)
        d.line([x + 10, y + 44, x + 10, y + 12], fill=fg, width=2)
        pts = [(12, 16), (20, 24), (28, 22), (36, 34), (44, 42)]
        d.line([(x + a, y + b) for a, b in pts], fill=RED, width=3)
        d.polygon([(x + 44, y + 42), (x + 38, y + 40), (x + 44, y + 36)],
                  fill=RED)
    elif kind == "cyclone":
        for r in (8, 14, 20):
            d.arc([x + 27 - r, y + 24 - r, x + 27 + r, y + 24 + r], 200, 20,
                  fill=fg, width=2)
        for dx, dy in ((-14, 14), (10, 18), (16, 10)):
            d.line([x + 27 + dx, y + 24 + dy, x + 27 + dx, y + 24 + dy + 5],
                   fill=(140, 180, 220), width=2)
    elif kind == "jet":
        d.ellipse([x + 8, y + 8, x + 24, y + 24], fill=RED)
        d.polygon([(x + 14, y + 34), (x + 46, y + 24), (x + 14, y + 30),
                   (x + 22, y + 28), (x + 18, y + 42), (x + 12, y + 30)],
                  fill=fg)
    elif kind == "summit":
        for i, hh in enumerate((26, 38, 30)):
            bx = x + 8 + i * 14
            d.rectangle([bx, y + 46 - hh, bx + 11, y + 46], fill=fg)
            d.line([bx + 5, y + 46 - hh - 8, bx + 5, y + 46 - hh], fill=ac,
                   width=2)
            d.rectangle([bx + 5, y + 46 - hh - 8, bx + 12,
                         y + 46 - hh - 3], fill=ac)
    elif kind == "drone":
        d.line([x + 14, y + 14, x + 40, y + 40], fill=fg, width=2)
        d.line([x + 40, y + 14, x + 14, y + 40], fill=fg, width=2)
        for cx, cy in ((14, 14), (40, 14), (14, 40), (40, 40)):
            d.ellipse([x + cx - 5, y + cy - 5, x + cx + 5, y + cy + 5],
                      outline=ac, width=2)
        d.rectangle([x + 22, y + 22, x + 32, y + 32], fill=RED)
        d.line([x + 8, y + 48, x + 46, y + 48], fill=(140, 180, 220), width=3)

# --- layout ------------------------------------------------------------------
def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # --- masthead 0-118 (oxblood) ---
    d.rectangle([0, 0, W, 118], fill=OXBLOOD)
    brand = "THE WORLD, MAPPED"
    bf = F_SANS_B(19)
    draw_tracked(d, 24, 16, brand, bf, GOLD, tracking=3)
    count = "35 STORIES · 6 CONTINENTS · ONE PAGE"
    cf = F_SANS_B(13)
    d.text((W - 24 - text_w(cf, count), 18), count, font=cf, fill=GOLD)
    date = "Wednesday 18 November 2026"
    df = F_SERIF_B(46)
    d.text(((W - text_w(df, date)) // 2, 40), date, font=df, fill=CREAM)
    sub = "Every story on this page happened, or was first reported, on this day."
    sf = F_SERIF_I(14)
    d.text(((W - text_w(sf, sub)) // 2, 94), sub, font=sf, fill=(214, 200, 170))
    d.rectangle([0, 118, W, 121], fill=GOLD)

    # --- zone A 122-420: map hero + 3 features ---
    draw_map(d, 24, 130, 596, 282)
    fx, fw = 636, 364
    fy = 122
    for i, (num, kicker, fam, head, summ) in enumerate(FEATURES):
        y = fy + i * 100
        # illustration strip
        ILLOS[num](d, fx, y + 2, 96, 92)
        d.rectangle([fx, y + 2, fx + 96, y + 94], outline=CARD_LINE, width=1)
        tx, tw = fx + 108, fw - 108
        kc = KICKER_COLORS[fam]
        kf = F_SANS_B(10)
        d.text((tx, y + 4), kicker, font=kf, fill=kc)
        hf = F_SERIF_B(16)
        hl = fit_lines(hf, head, tw, 2)
        yy = draw_lines(d, tx, y + 20, hl, hf, INK, leading=19)
        sf2 = F_SANS(12)
        sl = fit_lines(sf2, summ, tw, 3)
        draw_lines(d, tx, yy + 2, sl, sf2, GREY, leading=15)
        # red number badge on the illustration corner
        bf2 = F_SANS_B(12)
        d.ellipse([fx + 2, y + 4, fx + 22, y + 24], fill=RED, outline=CREAM,
                  width=1)
        s = str(num)
        d.text((fx + 12 - text_w(bf2, s) / 2, y + 8), s, font=bf2, fill=CREAM)
    d.line([24, 421, 1000, 421], fill=OXBLOOD, width=2)

    # --- zone B 424-694: 6 cards, 3 x 2 ---
    cw2, ch2 = 320, 131
    for i, (num, kicker, fam, head, summ, icon) in enumerate(CARDS):
        cx = 24 + (i % 3) * (cw2 + 8)
        cy = 424 + (i // 3) * (ch2 + 8)
        d.rounded_rectangle([cx, cy, cx + cw2, cy + ch2], radius=6,
                            fill=CARD_BG, outline=CARD_LINE, width=1)
        icon_tile(d, cx + 12, cy + 12, icon)
        bf2 = F_SANS_B(11)
        d.ellipse([cx + 54, cy + 8, cx + 72, cy + 26], fill=RED, outline=CREAM,
                  width=1)
        s = str(num)
        d.text((cx + 63 - text_w(bf2, s) / 2, cy + 11), s, font=bf2, fill=CREAM)
        tx, tw = cx + 76, cw2 - 88
        kf = F_SANS_B(10)
        d.text((tx, cy + 10), kicker, font=kf, fill=KICKER_COLORS[fam])
        hf = F_SERIF_B(15)
        hl = fit_lines(hf, head, tw, 2)
        yy = draw_lines(d, tx, cy + 26, hl, hf, INK, leading=18)
        sf2 = F_SANS(12)
        sl = fit_lines(sf2, summ, tw, 3)
        draw_lines(d, tx, yy + 3, sl, sf2, GREY, leading=15)
    d.line([24, 695, 1000, 695], fill=OXBLOOD, width=2)

    # --- zone C 698-758: BY THE NUMBERS ---
    nf = F_SANS_B(11)
    d.text((24, 703), "BY THE NUMBERS", font=nf, fill=GREY)
    col_w = 244
    for i, (big, label) in enumerate(NUMBERS):
        x = 24 + i * col_w
        bf3 = F_SERIF_B(30)
        d.text((x, 716), big, font=bf3, fill=OXBLOOD)
        lf = F_SANS(11)
        d.text((x, 748), label, font=lf, fill=GREY)
    d.line([24, 761, 1000, 761], fill=OXBLOOD, width=2)

    # --- zone D 762-1000: ALSO list, 2 columns x 13 rows ---
    hf = F_SANS_B(15)
    d.text((24, 769),
           "ALSO ON WEDNESDAY 18 NOVEMBER — 26 MORE STORIES",
           font=hf, fill=OXBLOOD)
    af = F_SANS(11)
    anf = F_SANS_B(11)
    col_x = [24, 524]
    row_h = 16
    y0 = 791
    for i, (num, text) in enumerate(ALSO):
        col = i // 13
        row = i % 13
        x = col_x[col]
        y = y0 + row * row_h
        ns = f"{num}. "
        d.text((x, y), ns, font=anf, fill=RED)
        d.text((x + text_w(anf, ns), y), text, font=af, fill=INK)

    # --- footer 1000-1022 ---
    ff = F_SANS(10)
    foot = ("Sources: Reuters, Associated Press, BBC, Barron's, IMD, RFE/RL  ·  "
            "All events of Wednesday 18 November 2026  ·  Drawn entirely by code; "
            "no photographs.")
    d.text(((W - text_w(ff, foot)) // 2, 1006), foot, font=ff, fill=GREY)
    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    img = render()
    img.save(out, "PNG", optimize=True)
    print(f"wrote {out} {os.path.getsize(out)} bytes {img.size[0]}x{img.size[1]}")


if __name__ == "__main__":
    main()
