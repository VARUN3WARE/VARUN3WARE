"""Regenerate the animated SVGs in assets/. Edit CONTRIBUTIONS when PRs merge, then run:

    python3 generate_assets.py
"""

import math
import random
from pathlib import Path

NAME = "Varun Rao"
TAGLINE = "AI/ML engineer · agent reliability · robotics data infra"
SUBLINE = "IIT Bhilai · Kaggle Expert · building Human Slop"

# (repo, merged, open)
CONTRIBUTIONS = [
    ("Hebbian-Robotics/hflow", 12, 0),
    ("ArgusLabs-ai/ARGUS", 4, 0),
    ("kornia/kornia", 2, 0),
    ("NVIDIA/nvcf", 1, 0),
    ("shap/shap", 0, 2),
]

ASSETS = Path(__file__).parent / "assets"

BG = "#0d1117"
PANEL = "#161b22"
BORDER = "#30363d"
BLUE = "#58a6ff"
PURPLE = "#bc8cff"
GREEN = "#7ee787"
GREY = "#8b949e"
WHITE = "#e6edf3"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"


def fade_in(begin, dur=0.8):
    return f'<animate attributeName="opacity" from="0" to="1" begin="{begin}s" dur="{dur}s" fill="freeze"/>'


def rise_in(begin, dur=0.9):
    return fade_in(begin, dur) + (
        f'<animateTransform attributeName="transform" type="translate" from="0 14" to="0 0" '
        f'begin="{begin}s" dur="{dur}s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".2 .8 .2 1"/>'
    )


def typewriter_values(n_chars, char_w, x0=0.0):
    """Discrete width/x keyframes so text appears one character at a time."""
    widths = [f"{x0 + i * char_w:.1f}" for i in range(n_chars + 1)]
    times = [f"{i / n_chars:.4f}" for i in range(n_chars + 1)]
    return ";".join(widths), ";".join(times)


def header_svg():
    w, h = 1200, 340
    rnd = random.Random(7)

    layers_x = [850, 945, 1040, 1125]
    layers_n = [3, 5, 5, 2]
    nodes = []
    for x, n in zip(layers_x, layers_n):
        span = 50 * (n - 1)
        nodes.append([(x, 170 - span / 2 + 50 * i) for i in range(n)])

    edges, signals = [], []
    for li in range(len(nodes) - 1):
        for a in nodes[li]:
            for b in nodes[li + 1]:
                edges.append(
                    f'<line x1="{a[0]}" y1="{a[1]:.0f}" x2="{b[0]}" y2="{b[1]:.0f}" class="edge"/>'
                )
                begin = li * 0.55 + rnd.uniform(0, 0.5)
                colour = "url(#sig)" if rnd.random() > 0.3 else GREEN
                signals.append(
                    f'<line x1="{a[0]}" y1="{a[1]:.0f}" x2="{b[0]}" y2="{b[1]:.0f}" '
                    f'pathLength="100" stroke="{colour}" stroke-width="2" stroke-linecap="round" '
                    f'stroke-dasharray="10 200" stroke-dashoffset="10" filter="url(#glow)">'
                    f'<animate attributeName="stroke-dashoffset" values="10;-100;-100" keyTimes="0;0.42;1" '
                    f'dur="2.6s" begin="{begin:.2f}s" repeatCount="indefinite"/>'
                    f"</line>"
                )

    circles = []
    for li, layer in enumerate(nodes):
        for x, y in layer:
            delay = li * 0.55 + 0.9
            circles.append(
                f'<circle cx="{x}" cy="{y:.0f}" r="8" fill="{BG}" stroke="{BLUE}" stroke-width="2"/>'
                f'<circle cx="{x}" cy="{y:.0f}" r="4" fill="{PURPLE}" filter="url(#glow)" opacity="0.25">'
                f'<animate attributeName="opacity" values="0.25;1;0.25" dur="2.6s" '
                f'begin="{delay:.2f}s" repeatCount="indefinite"/>'
                f"</circle>"
            )

    # Noisy, decaying loss curve along the bottom-left.
    pts = []
    for i in range(71):
        x = 60 + i * 10
        decay = math.exp(-i / 16)
        noise = rnd.uniform(-4, 4) * (0.3 + decay)
        y = 312 - 34 * decay + noise
        pts.append((x, y))
    loss_path = "M" + " L".join(f"{x},{y:.1f}" for x, y in pts)

    tag_vals, tag_times = typewriter_values(len(TAGLINE), 12.0)
    cur_vals, _ = typewriter_values(len(TAGLINE), 12.0, x0=62.0)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{NAME}: {TAGLINE}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{BG}"/>
      <stop offset="1" stop-color="#111827"/>
    </linearGradient>
    <linearGradient id="sig" x1="0" x2="1">
      <stop offset="0" stop-color="{BLUE}"/>
      <stop offset="1" stop-color="{PURPLE}"/>
    </linearGradient>
    <linearGradient id="shine" x1="-1" y1="0" x2="0" y2="0">
      <stop offset="0" stop-color="{WHITE}"/>
      <stop offset="0.45" stop-color="{WHITE}"/>
      <stop offset="0.5" stop-color="{BLUE}"/>
      <stop offset="0.55" stop-color="{WHITE}"/>
      <stop offset="1" stop-color="{WHITE}"/>
      <animate attributeName="x1" values="-1;1" dur="4s" begin="1s" repeatCount="indefinite"/>
      <animate attributeName="x2" values="0;2" dur="4s" begin="1s" repeatCount="indefinite"/>
    </linearGradient>
    <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">
      <path d="M32 0H0V32" fill="none" stroke="{BORDER}" stroke-width="0.5" opacity="0.35"/>
    </pattern>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="2.2" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <clipPath id="type"><rect x="60" y="178" height="34" width="0">
      <animate attributeName="width" values="{tag_vals}" keyTimes="{tag_times}" calcMode="discrete" dur="2.8s" begin="1.2s" fill="freeze"/>
    </rect></clipPath>
    <style>.edge {{ stroke: {BORDER}; stroke-width: 1; opacity: .7; }}</style>
  </defs>

  <rect width="{w}" height="{h}" rx="18" fill="url(#bg)"/>
  <rect width="{w}" height="{h}" rx="18" fill="url(#grid)"/>
  <rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="18" fill="none" stroke="{BORDER}"/>

  <text x="60" y="84" font-family="{MONO}" font-size="16" fill="{GREEN}" opacity="0">&gt; model.load("varun") <tspan fill="{GREY}"># weights: 2 years of 3 AM training runs</tspan>{fade_in(0)}</text>

  <text x="56" y="152" font-family="{SANS}" font-size="68" font-weight="800" fill="url(#shine)" opacity="0">{NAME}{rise_in(0.3)}</text>

  <g clip-path="url(#type)">
    <text x="62" y="203" font-family="{MONO}" font-size="20" fill="{BLUE}">{TAGLINE}</text>
  </g>
  <rect y="185" width="11" height="22" fill="{BLUE}" x="62">
    <animate attributeName="x" values="{cur_vals}" keyTimes="{tag_times}" calcMode="discrete" dur="2.8s" begin="1.2s" fill="freeze"/>
    <animate attributeName="opacity" values="1;0" keyTimes="0;0.5" calcMode="discrete" dur="1s" repeatCount="indefinite"/>
  </rect>

  <text x="62" y="243" font-family="{MONO}" font-size="15" fill="{GREY}" opacity="0">{SUBLINE}{fade_in(4.1)}</text>

  <g opacity="0">{fade_in(0.6)}
    <text x="60" y="268" font-family="{MONO}" font-size="11" fill="{GREY}">loss</text>
    <text x="700" y="330" font-family="{MONO}" font-size="11" fill="{GREY}">epoch → ∞</text>
    <path d="{loss_path}" fill="none" stroke="url(#sig)" stroke-width="2" pathLength="100"
          stroke-dasharray="100" stroke-dashoffset="100" filter="url(#glow)">
      <animate attributeName="stroke-dashoffset" values="100;0;0" keyTimes="0;0.7;1" dur="6s" repeatCount="indefinite"/>
    </path>
    <circle r="4.5" fill="{GREEN}" filter="url(#glow)">
      <animateMotion dur="6s" repeatCount="indefinite" keyPoints="0;1;1" keyTimes="0;0.7;1" calcMode="linear" path="{loss_path}"/>
    </circle>
  </g>

  <g opacity="0">{fade_in(0.4)}
    {"".join(edges)}
    {"".join(signals)}
    {"".join(circles)}
    <text x="850" y="300" font-family="{MONO}" font-size="11" fill="{GREY}">input</text>
    <text x="1100" y="300" font-family="{MONO}" font-size="11" fill="{GREY}">output</text>
  </g>
</svg>
"""


def terminal_svg():
    char_w = 8.4
    line_h = 26
    top = 70
    rows = len(CONTRIBUTIONS)
    w = 860
    h = top + line_h * (rows + 4) + 20
    total_merged = sum(m for _, m, _ in CONTRIBUTIONS)
    total_open = sum(o for _, _, o in CONTRIBUTIONS)
    max_merged = max(m for _, m, _ in CONTRIBUTIONS) or 1

    cmd = "gh search prs --author VARUN3WARE --merged --not-owner"
    cmd_vals, cmd_times = typewriter_values(len(cmd), char_w)
    cmd_dur = len(cmd) * 0.045
    t = 0.4 + cmd_dur + 0.35

    lines = []
    for i, (repo, merged, opened) in enumerate(CONTRIBUTIONS):
        y = top + line_h * (i + 1)
        begin = t + i * 0.35
        bar_w = 280 * merged / max_merged
        status = f"{merged} merged" if merged else f"{opened} open"
        colour = GREEN if merged else "#d29922"
        bar = (
            f'<rect x="470" y="{y - 13}" width="0" height="14" rx="3" fill="url(#bar)">'
            f'<animate attributeName="width" values="0;{bar_w:.1f}" dur="0.9s" begin="{begin + 0.15:.2f}s" '
            f'fill="freeze" calcMode="spline" keySplines=".2 .8 .2 1"/></rect>'
            if merged
            else f'<rect x="470" y="{y - 13}" width="{12 * opened}" height="14" rx="3" fill="none" '
            f'stroke="#d29922" stroke-dasharray="3 3" opacity="0"><set attributeName="opacity" to="1" '
            f'begin="{begin + 0.15:.2f}s" fill="freeze"/></rect>'
        )
        lines.append(
            f'<g opacity="0"><set attributeName="opacity" to="1" begin="{begin:.2f}s" fill="freeze"/>'
            f'<text x="28" y="{y}" fill="{WHITE}">{repo}</text>'
            f'<text x="330" y="{y}" fill="{colour}">{status}</text>'
            f"</g>{bar}"
        )

    end = t + rows * 0.35 + 0.6
    sum_y = top + line_h * (rows + 2)
    prompt_y = top + line_h * (rows + 3)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{total_merged} merged upstream pull requests">
  <defs>
    <linearGradient id="bar" x1="0" x2="1">
      <stop offset="0" stop-color="{BLUE}"/>
      <stop offset="1" stop-color="{PURPLE}"/>
    </linearGradient>
    <clipPath id="cmd"><rect x="62" y="{top - 18}" height="26" width="0">
      <animate attributeName="width" values="{cmd_vals}" keyTimes="{cmd_times}" calcMode="discrete" dur="{cmd_dur:.2f}s" begin="0.4s" fill="freeze"/>
    </rect></clipPath>
  </defs>

  <rect width="{w}" height="{h}" rx="12" fill="{BG}" stroke="{BORDER}"/>
  <path d="M0 12a12 12 0 0 1 12-12h{w - 24}a12 12 0 0 1 12 12v24H0z" fill="{PANEL}"/>
  <circle cx="24" cy="18" r="6" fill="#ff5f56"/><circle cx="44" cy="18" r="6" fill="#ffbd2e"/><circle cx="64" cy="18" r="6" fill="#27c93f"/>
  <text x="{w / 2}" y="23" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{GREY}">varun@iit-bhilai: ~/open-source</text>

  <g font-family="{MONO}" font-size="14">
    <text x="28" y="{top}" fill="{GREEN}">~ $</text>
    <g clip-path="url(#cmd)"><text x="62" y="{top}" fill="{WHITE}">{cmd}</text></g>

    {"".join(lines)}

    <g opacity="0"><set attributeName="opacity" to="1" begin="{end:.2f}s" fill="freeze"/>
      <line x1="28" y1="{sum_y - 22}" x2="{w - 28}" y2="{sum_y - 22}" stroke="{BORDER}"/>
      <text x="28" y="{sum_y}" fill="{GREY}">total</text>
      <text x="330" y="{sum_y}" fill="{GREEN}" font-weight="700">{total_merged} merged upstream</text>
      <text x="520" y="{sum_y}" fill="#d29922">{total_open} awaiting review</text>
    </g>

    <g opacity="0"><set attributeName="opacity" to="1" begin="{end + 0.4:.2f}s" fill="freeze"/>
      <text x="28" y="{prompt_y}" fill="{GREEN}">~ $</text>
      <rect x="62" y="{prompt_y - 14}" width="9" height="18" fill="{WHITE}">
        <animate attributeName="opacity" values="1;0" keyTimes="0;0.5" calcMode="discrete" dur="1s" repeatCount="indefinite"/>
      </rect>
    </g>
  </g>
</svg>
"""


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    (ASSETS / "header.svg").write_text(header_svg(), encoding="utf-8")
    (ASSETS / "terminal.svg").write_text(terminal_svg(), encoding="utf-8")
    print("wrote", ASSETS / "header.svg", "and", ASSETS / "terminal.svg")
