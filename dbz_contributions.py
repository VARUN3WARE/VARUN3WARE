"""Render a GitHub contribution calendar as a Vegeta vs Goku beam clash (animated SVG).

    python3 dbz_contributions.py VARUN3WARE dist/dbz-clash.svg
"""

import random
import re
import sys
import urllib.request
from pathlib import Path

CELL, GAP = 11, 3
STEP = CELL + GAP
ROWS, COLS = 7, 53
SCALE = 4
SIDE = 120
TOP = 58
DUR = 12.0

W = SIDE * 2 + COLS * STEP - GAP
H = TOP + ROWS * STEP - GAP + 47
CX = W / 2
BEAM_Y = TOP + 3 * STEP + CELL / 2

T_SSJ, T_CHARGE, T_FIRE, T_MEET, T_BOOM, T_CALM = 0.8, 1.2, 1.8, 3.2, 8.0, 10.6
STRUGGLE = [(3.2, 0), (4.0, -45), (4.7, 35), (5.5, -85), (6.3, 70), (7.0, -25), (7.6, 95), (8.0, 0)]

BG, BORDER, GREY = "#0d1117", "#30363d", "#8b949e"
GREEN = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
PURPLE = ["#1d1530", "#3b1f6e", "#6e40c9", "#a371f7", "#e0c3ff"]
BLUE = ["#0f1d33", "#0c2d6b", "#1f6feb", "#58a6ff", "#b6e3ff"]
GOLD, HAIR = "#ffd84d", "#2b2b40"
GALICK, KAME = "#b45cff", "#38bdf8"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"

# Facing right. K hair, S skin, E eye, B suit, W white, Y gold trim, O gi, D dark blue.
VEGETA = [
    ".....K..K",
    "....KK.KK..K",
    "....KKKKK.KK",
    "...KKKKKKKKK",
    "...KKKKKKKKK",
    "...KKKKKKKKKK",
    "....KSSSKSSK",
    "....SSSSSESS",
    "....SSSSSSSS",
    ".....SSSSSS",
    "......SSSS",
    "...WWWWWWW",
    "..BWWWWWWWBBBBBWW",
    "..BWWWWWWWBBBBBWW",
    "..BYWWWWWY",
    "...BBBBBBB",
    "...BBBBBBB",
    "...BBB.BBB",
    "...BBB..BBB",
    "..BBB....BBB",
    "..WWW....WWW",
    ".WWWW....WWWW",
]
GOKU = [
    "...K..K..K",
    "..KK.KK.KK",
    ".KKKKKKKKKK",
    "KKKKKKKKKKKK",
    ".KKKKKKKKKKK",
    "KKKKKKKKKKKK",
    "..KKSSKSSKK",
    "...SSSSSESS",
    "...SSSSSSSS",
    "....SSSSSS",
    ".....SSSS",
    "...OOODDOOO",
    "..OOOODDOOOSSSSDSS",
    "..OOOOOOOOOSSSSDSS",
    "..SOOOOOOOS",
    "...DDDDDDD",
    "...OOOOOOO",
    "...OOO.OOO",
    "...OOO..OOO",
    "..OOO....OOO",
    "..DDD....DDD",
    ".DDDD....DDDD",
]
SPRITE_COLS = 18
SPRITE_COLOURS = {"S": "#f2c49b", "E": "#111111", "B": "#2f4fd8", "W": "#f0f0f0",
                  "Y": "#e8b923", "O": "#ff7a1a", "D": "#1e3a8a"}


def fetch(user):
    req = urllib.request.Request(
        f"https://github.com/users/{user}/contributions", headers={"User-Agent": "dbz-contributions"}
    )
    html = urllib.request.urlopen(req, timeout=30).read().decode()
    days = [
        (int(r), int(c), int(lvl))
        for r, c, lvl in re.findall(r'id="contribution-day-component-(\d+)-(\d+)" data-level="(\d)"', html)
    ]
    if not days:
        raise SystemExit("no contribution cells found; GitHub markup may have changed")
    m = re.search(r"([\d,]+)\s+contributions?\s+in the last year", html)
    return days, int(m.group(1).replace(",", "")) if m else 0


def anim(attr, frames, discrete=False):
    """SMIL animation over the shared DUR loop from (seconds, value) keyframes."""
    frames = sorted(frames)
    if frames[0][0] > 0:
        frames.insert(0, (0.0, frames[0][1]))
    if frames[-1][0] < DUR:
        frames.append((DUR, frames[-1][1]))
    values = ";".join(str(v) for _, v in frames)
    times = ";".join(f"{t / DUR:.4f}" for t, _ in frames)
    mode = ' calcMode="discrete"' if discrete else ""
    return (f'<animate attributeName="{attr}" values="{values}" keyTimes="{times}" '
            f'dur="{DUR}s" repeatCount="indefinite"{mode}/>')


def clash(t):
    for (t0, x0), (t1, x1) in zip(STRUGGLE, STRUGGLE[1:]):
        if t0 <= t <= t1:
            return CX + x0 + (x1 - x0) * (t - t0) / (t1 - t0)
    return CX


HAND_V = 22 + SPRITE_COLS * SCALE
HAND_G = W - HAND_V


def fronts(t):
    """Leading edge of each beam, or None when that beam isn't firing."""
    if not T_FIRE <= t < T_BOOM:
        return None, None
    if t < T_MEET:
        p = (t - T_FIRE) / (T_MEET - T_FIRE)
        return HAND_V + (CX - HAND_V) * p, HAND_G - (HAND_G - CX) * p
    c = clash(t)
    return c, c


def cell_svg(row, col, level):
    x = SIDE + col * STEP
    y = TOP + row * STEP
    centre = x + CELL / 2
    frames, last = [], None
    t = 0.0
    while t < DUR:
        v, g = fronts(t)
        if v is not None and centre <= v:
            colour = PURPLE[level]
        elif g is not None and centre >= g:
            colour = BLUE[level]
        else:
            colour = GREEN[level]
        if colour != last:
            frames.append((round(t, 2), colour))
            last = colour
        t += 0.02
    fill = f' fill="{GREEN[level]}"'
    body = anim("fill", frames, discrete=True) if len(frames) > 1 else ""
    return f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2"{fill}>{body}</rect>'


def sprite_svg(rows, left, top, mirror):
    groups = {}
    for r, line in enumerate(rows):
        for c, ch in enumerate(line.ljust(SPRITE_COLS, ".")):
            if ch == ".":
                continue
            cc = SPRITE_COLS - 1 - c if mirror else c
            groups.setdefault(ch, []).append(
                f'<rect x="{left + cc * SCALE}" y="{top + r * SCALE}" width="{SCALE}" height="{SCALE}"/>'
            )
    out = []
    for ch, rects in groups.items():
        if ch == "K":
            hair = anim("fill", [(0, HAIR), (T_SSJ, HAIR), (T_SSJ + 0.15, GOLD),
                                 (T_CALM, GOLD), (T_CALM + 0.4, HAIR)])
            out.append(f'<g fill="{HAIR}">{hair}{"".join(rects)}</g>')
        else:
            out.append(f'<g fill="{SPRITE_COLOURS[ch]}">{"".join(rects)}</g>')
    return "".join(out)


def fighter(rows, left, mirror, beam_colour, hand_x):
    top = BEAM_Y - 13 * SCALE
    mid_x = left + SPRITE_COLS * SCALE / 2
    aura = (
        f'<ellipse cx="{mid_x}" cy="{top + 46}" rx="44" ry="58" fill="{GOLD}" filter="url(#blur)" opacity="0">'
        + anim("opacity", [(0, 0), (T_SSJ, 0), (T_SSJ + 0.2, 0.55), (T_BOOM + 0.8, 0.45), (T_CALM, 0)])
        + anim("ry", [(0, 58), (2, 64), (4, 58), (6, 66), (8, 58), (10, 62)])
        + "</ellipse>"
    )
    charge = (
        f'<circle cx="{hand_x}" cy="{BEAM_Y}" r="0" fill="{beam_colour}" filter="url(#glow)">'
        + anim("r", [(0, 0), (T_CHARGE, 0), (T_FIRE, 12), (T_FIRE + 0.2, 9), (T_BOOM, 10), (T_BOOM + 0.05, 0)])
        + "</circle>"
    )
    bob = ('<animateTransform attributeName="transform" type="translate" values="0 0;0 -2;0 0" '
           'dur="1.2s" repeatCount="indefinite"/>')
    return f'<g>{aura}<g>{bob}{sprite_svg(rows, left, top, mirror)}</g>{charge}</g>'


def beams():
    times = [0, T_FIRE, T_MEET] + [t for t, _ in STRUGGLE[1:]] + [T_BOOM + 0.05]
    v_w, g_x, g_w = [], [], []
    for t in times:
        if t < T_FIRE or t >= T_BOOM + 0.05:
            v_w.append((t, 0))
            g_x.append((t, HAND_G))
            g_w.append((t, 0))
            continue
        v, g = fronts(min(t, T_BOOM - 0.001))
        v_w.append((t, round(v - HAND_V, 1)))
        g_x.append((t, round(g, 1)))
        g_w.append((t, round(HAND_G - g, 1)))
    flicker = '<animate attributeName="opacity" values="0.8;1;0.8" dur="0.15s" repeatCount="indefinite"/>'

    def beam(x_frames, w_frames, colour, core, x_static):
        layers = [(18, colour, "url(#glow)"), (6, core, "")]
        out = []
        for h, fill, flt in layers:
            x_anim = anim("x", x_frames) if x_frames else ""
            f_attr = f' filter="{flt}"' if flt else ""
            out.append(f'<rect x="{x_static}" y="{BEAM_Y - h / 2}" width="0" height="{h}" rx="{h / 2}" '
                       f'fill="{fill}"{f_attr}>{x_anim}{anim("width", w_frames)}{flicker if flt else ""}</rect>')
        return "".join(out)

    return beam(None, v_w, GALICK, "#f3e1ff", HAND_V) + beam(g_x, g_w, KAME, "#e0f7ff", HAND_G)


def clash_orb():
    xs = [(0, CX), (T_MEET, CX)] + [(t, round(CX + dx, 1)) for t, dx in STRUGGLE[1:]]
    spikes = "".join(
        f'<polygon points="0,-30 4,0 0,30 -4,0" fill="#ffffff" opacity="0.8" transform="rotate({a})"/>'
        for a in range(0, 180, 30)
    )
    move = (
        '<animateTransform attributeName="transform" type="translate" '
        f'values="{";".join(f"{x} {BEAM_Y}" for _, x in xs)};{CX} {BEAM_Y}" '
        f'keyTimes="{";".join(f"{t / DUR:.4f}" for t, _ in xs)};1" dur="{DUR}s" repeatCount="indefinite"/>'
    )
    show = anim("opacity", [(0, 0), (T_MEET - 0.05, 0), (T_MEET, 1), (T_BOOM, 1), (T_BOOM + 0.05, 0)])
    return (
        f'<g opacity="0">{show}<g>{move}'
        f'<g><animateTransform attributeName="transform" type="rotate" values="0;360" dur="0.8s" repeatCount="indefinite"/>{spikes}</g>'
        f'<circle r="15" fill="#ffffff" filter="url(#glow)">'
        f'<animate attributeName="r" values="13;19;13" dur="0.25s" repeatCount="indefinite"/></circle>'
        f"</g></g>"
    )


def shout(text_parts, x, anchor, colour):
    spans = []
    for word, t in text_parts:
        show = anim("opacity", [(0, 0), (t - 0.01, 0), (t, 1), (T_BOOM + 1.2, 1), (T_BOOM + 1.6, 0)])
        spans.append(f'<tspan opacity="0">{show}{word}</tspan>')
    return (f'<text x="{x}" y="34" text-anchor="{anchor}" font-family="{MONO}" font-size="16" '
            f'font-weight="800" fill="{colour}" filter="url(#glow)">{"".join(spans)}</text>')


def render(days, total):
    rnd = random.Random(9000)
    shake = [(0, "0 0"), (T_MEET, "0 0")]
    t = T_MEET
    while t < T_BOOM:
        t = round(t + 0.1, 2)
        shake.append((t, f"{rnd.uniform(-1.5, 1.5):.1f} {rnd.uniform(-1.2, 1.2):.1f}"))
    shake += [(T_BOOM, "0 0")]
    shake_anim = (
        '<animateTransform attributeName="transform" type="translate" '
        f'values="{";".join(v for _, v in shake)};0 0" '
        f'keyTimes="{";".join(f"{t / DUR:.4f}" for t, _ in shake)};1" dur="{DUR}s" repeatCount="indefinite"/>'
    )

    cells = "".join(cell_svg(r, c, lvl) for r, c, lvl in days)
    flash = anim("opacity", [(0, 0), (T_BOOM, 0), (T_BOOM + 0.08, 0.85), (T_BOOM + 0.7, 0)])
    boom = anim("r", [(0, 0), (T_BOOM, 0), (T_BOOM + 0.6, 520), (T_BOOM + 0.61, 0)])
    boom_o = anim("opacity", [(0, 0), (T_BOOM, 0), (T_BOOM + 0.05, 1), (T_BOOM + 0.6, 0)])

    galick = shout([("GALICK ", T_CHARGE), ("GUN!!", T_FIRE)], 18, "start", GALICK)
    kame = shout([("KA-", 1.0), ("ME-", 1.3), ("HA-", 1.5), ("ME-", 1.65), ("HA!!!", T_FIRE)], W - 18, "end", KAME)
    level = f"{total:,}"
    footer = (f"power level: {level} contributions in the last year"
              + (" · IT'S OVER 9000!!" if total > 9000 else ""))

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Contribution graph: Vegeta's Galick Gun clashes with Goku's Kamehameha. {level} contributions in the last year.">
  <defs>
    <filter id="glow" x="-50%" y="-200%" width="200%" height="500%">
      <feGaussianBlur stdDeviation="3" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="12"/></filter>
  </defs>
  <rect width="{W}" height="{H}" rx="14" fill="{BG}" stroke="{BORDER}"/>
  {galick}{kame}
  <g>{shake_anim}
    {cells}
    {beams()}
    {clash_orb()}
  </g>
  {fighter(VEGETA, 22, False, GALICK, HAND_V)}
  {fighter(GOKU, W - 22 - SPRITE_COLS * SCALE, True, KAME, HAND_G)}
  <circle cx="{CX}" cy="{BEAM_Y}" r="0" fill="#ffffff" opacity="0">{boom}{boom_o}</circle>
  <rect width="{W}" height="{H}" rx="14" fill="#ffffff" opacity="0" pointer-events="none">{flash}</rect>
  <text x="{CX}" y="{H - 16}" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{GREY}">{footer}</text>
</svg>
"""


if __name__ == "__main__":
    user = sys.argv[1] if len(sys.argv) > 1 else "VARUN3WARE"
    out = Path(sys.argv[2] if len(sys.argv) > 2 else "dist/dbz-clash.svg")
    days, total = fetch(user)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(days, total), encoding="utf-8")
    print(f"wrote {out} ({len(days)} days, {total} contributions)")
