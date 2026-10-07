"""data/github.json -> assets/neofetch.svg (the `whoami` card beside the portrait).

Same 840x880 frame as the portrait so the two sit level in a README table.
Static facts live in PROFILE / STACK below; the GitHub block is live.
"""

import datetime as dt
import json

from theme import BLUE, BORDER, GREEN, HEAT, HOST, MAROON, MUTED, ORANGE, PURPLE, RED, SOFT, TEXT, esc, window, write

DATA = "data/github.json"
OUT = "assets/neofetch.svg"

W, H = 840, 880
X, Y0, LH = 40, 76, 31
KEY_W = 150

PROFILE = [
    ("Name", "Harnoor Singh Khalsa"),
    ("Role", "Applied ML · AI-assisted engineering"),
    ("Uni", "Thapar Institute of Engg. & Technology"),
    ("Degree", "B.E. Computer Engineering · 4th year"),
    ("Location", "Patiala, Punjab, India"),
    ("Focus", "real-time ML systems, model efficiency,"),
    ("", "spec-driven LLM pair-programming"),
    ("Now", "real-time delivery ETA service"),
    ("", "Kafka → Redis → LightGBM → FastAPI"),
]

STACK = [
    ("ML", "PyTorch · scikit-learn · LightGBM"),
    ("Data", "Pandas · NumPy · SQL · Plotly · SimPy"),
    ("Serving", "FastAPI · Flask · Streamlit"),
    ("Streaming", "Kafka · Redis"),
]


def build(data):
    style = (
        ".l{animation:in .45s ease-out both}"
        "@keyframes in{0%{opacity:0;transform:translateX(-10px)}100%{opacity:1;transform:none}}"
        ".k{animation:blink 1s steps(1) infinite}@keyframes blink{50%{opacity:0}}"
    )
    lines = []  # (svg fragment, extra gap before)

    def kv(key, val, colour=BLUE):
        return (
            f'<text x="{X}" font-size="21"><tspan fill="{colour}" font-weight="700">{esc(key)}</tspan>'
            f'<tspan x="{X + KEY_W}" fill="{SOFT}">{esc(val)}</tspan></text>'
        )

    def rule(label):
        return (
            f'<text x="{X}" font-size="18" fill="{MUTED}">── {esc(label)} '
            f'{"─" * (60 - len(label))}</text>'
        )

    lines.append((f'<text x="{X}" font-size="18" fill="{GREEN}">$ <tspan fill="{SOFT}">neofetch</tspan></text>', 0))
    lines.append(
        (
            f'<text x="{X}" font-size="27" font-weight="700"><tspan fill="{MAROON}">harnoor</tspan>'
            f'<tspan fill="{SOFT}">@</tspan><tspan fill="{BLUE}">tiet</tspan></text>',
            8,
        )
    )
    lines.append((f'<line x1="{X}" x2="{X + 236}" stroke="{BORDER}" stroke-width="2"/>', -14))
    for k, v in PROFILE:
        lines.append((kv(k, v), 0))
    lines.append((rule("stack"), 10))
    for k, v in STACK:
        lines.append((kv(k, v, PURPLE), 0))
    lines.append((rule("github · live"), 10))

    best = dt.date.fromisoformat(data["best_day"]["date"])
    live = [
        ("Commits", f'{data["total"]} contributions · last 12 months'),
        ("Active", f'{data["active_days"]} days · peak {data["best_day"]["count"]} on {best:%b} {best.day}'),
        ("Repos", f'{data["public_repos"]} public'),
    ]
    if data["current_streak"] >= 2:
        live.append(("Streak", f'{data["current_streak"]} days and counting'))
    for k, v in live:
        lines.append((kv(k, v, ORANGE), 0))

    # neofetch colour strip
    strip = "".join(
        f'<rect x="{X + i * 44}" y="-16" width="40" height="20" rx="3" fill="{c}"/>'
        for i, c in enumerate([RED, ORANGE, "#e3b341", GREEN, BLUE, PURPLE, MAROON, SOFT])
    ) + "".join(
        f'<rect x="{X + 8 * 44 + 16 + i * 26}" y="-16" width="20" height="20" rx="3" fill="{c}"/>'
        for i, c in enumerate(HEAT[1:])
    )
    lines.append((f"<g>{strip}</g>", 22))

    parts, y, t = [], Y0, 0.25
    for frag, gap in lines:
        y += gap
        parts.append(f'<g transform="translate(0 {y})"><g class="l" style="animation-delay:{t:.2f}s">{frag}</g></g>')
        y += LH
        t += 0.09
    y += 14
    parts.append(
        f'<g transform="translate(0 {y})"><g class="l" style="animation-delay:{t:.2f}s">'
        f'<text x="{X}" font-size="18" fill="{GREEN}">$ </text>'
        f'<rect class="k" x="{X + 24}" y="-15" width="10" height="19" fill="{SOFT}"/></g></g>'
    )
    assert y < H - 20, f"card overflows: y={y}"
    return window(W, H, f"{HOST}: ~$ whoami", "".join(parts), style)


if __name__ == "__main__":
    with open(DATA, encoding="utf-8") as f:
        write(OUT, build(json.load(f)))
