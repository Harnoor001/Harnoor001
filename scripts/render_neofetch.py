"""data/github.json -> assets/neofetch.svg (the full-width `whoami` card).

Two columns: who I am on the left, stack + live GitHub numbers on the right.
Static facts live in PROFILE / STACK below; the GitHub block is live.
"""

import datetime as dt
import json

from theme import BLUE, BORDER, GREEN, HEAT, HOST, MAROON, MUTED, ORANGE, PURPLE, RED, SOFT, esc, window, write

DATA = "data/github.json"
OUT = "assets/neofetch.svg"

W = 960
X1, X2 = 36, 490  # column origins
KEY_W = 112
LH = 30
FONT = 17
COL_CHARS = 40  # rule length in the right column

PROFILE = [
    ("Role", "Applied ML · AI-assisted eng."),
    ("Uni", "Thapar Institute (TIET)"),
    ("Degree", "B.E. Computer Eng. · 4th year"),
    ("Location", "Patiala, Punjab, India"),
    ("Focus", "real-time ML systems,"),
    ("", "model efficiency,"),
    ("", "spec-driven LLM pairing"),
    ("Now", "real-time delivery ETA"),
    ("", "Kafka → Redis → LightGBM"),
]

STACK = [
    ("ML", "PyTorch · scikit-learn · LightGBM"),
    ("Data", "Pandas · NumPy · SQL · Plotly"),
    ("Serving", "FastAPI · Flask · Streamlit"),
    ("Streaming", "Kafka · Redis"),
]


def build(data):
    style = (
        ".l{animation:in .45s ease-out both}"
        "@keyframes in{0%{opacity:0;transform:translateX(-10px)}100%{opacity:1;transform:none}}"
        ".k{animation:blink 1s steps(1) infinite}@keyframes blink{50%{opacity:0}}"
    )

    def kv(x, key, val, colour):
        return (
            f'<text x="{x}" font-size="{FONT}"><tspan fill="{colour}" font-weight="700">{esc(key)}</tspan>'
            f'<tspan x="{x + KEY_W}" fill="{SOFT}">{esc(val)}</tspan></text>'
        )

    def rule(x, label):
        return f'<text x="{x}" font-size="{FONT - 2}" fill="{MUTED}">── {esc(label)} {"─" * (COL_CHARS - len(label))}</text>'

    best = dt.date.fromisoformat(data["best_day"]["date"])
    live = [
        ("Commits", f'{data["total"]} in the last 12 months'),
        ("Active", f'{data["active_days"]} days · peak {data["best_day"]["count"]} on {best:%b} {best.day}'),
        ("Repos", f'{data["public_repos"]} public'),
    ]
    if data["current_streak"] >= 2:
        live.append(("Streak", f'{data["current_streak"]} days and counting'))

    left = [kv(X1, k, v, BLUE) for k, v in PROFILE]
    right = [rule(X2, "stack")] + [kv(X2, k, v, PURPLE) for k, v in STACK]
    right += [rule(X2, "github · live")] + [kv(X2, k, v, ORANGE) for k, v in live]

    def row(y, t, frag):
        return f'<g transform="translate(0 {y})"><g class="l" style="animation-delay:{t:.2f}s">{frag}</g></g>'

    parts = [
        row(70, 0.2, f'<text x="{X1}" font-size="{FONT}" fill="{GREEN}">$ <tspan fill="{SOFT}">neofetch</tspan></text>'),
        row(
            108,
            0.3,
            f'<text x="{X1}" font-size="25" font-weight="700"><tspan fill="{MAROON}">harnoor</tspan>'
            f'<tspan fill="{SOFT}">@</tspan><tspan fill="{BLUE}">tiet</tspan>'
            f'<tspan fill="{MUTED}" font-size="{FONT}" font-weight="400">  ·  Harnoor Singh Khalsa</tspan></text>'
            f'<line x1="{X1}" x2="{W - X1}" y1="16" y2="16" stroke="{BORDER}" stroke-width="1.5"/>',
        ),
    ]
    y0, t0 = 162, 0.4
    for i in range(max(len(left), len(right))):
        y, t = y0 + i * LH, t0 + i * 0.08
        if i < len(left):
            parts.append(row(y, t, left[i]))
        if i < len(right):
            parts.append(row(y, t + 0.04, right[i]))

    y = y0 + max(len(left), len(right)) * LH + 14
    t = t0 + max(len(left), len(right)) * 0.08
    strip = "".join(
        f'<rect x="{X1 + 64 + i * 40}" y="-15" width="36" height="18" rx="3" fill="{c}"/>'
        for i, c in enumerate([RED, ORANGE, "#e3b341", GREEN, BLUE, PURPLE, MAROON, SOFT])
    ) + "".join(
        f'<rect x="{X1 + 64 + 8 * 40 + 14 + i * 24}" y="-15" width="18" height="18" rx="3" fill="{c}"/>'
        for i, c in enumerate(HEAT[1:])
    )
    parts.append(
        row(
            y,
            t,
            f'<text x="{X1}" font-size="{FONT}" fill="{GREEN}">$ </text>'
            f'<rect class="k" x="{X1 + 22}" y="-14" width="9" height="17" fill="{SOFT}"/>{strip}',
        )
    )
    return window(W, y + 30, f"{HOST}: ~$ whoami", "".join(parts), style)


if __name__ == "__main__":
    with open(DATA, encoding="utf-8") as f:
        write(OUT, build(json.load(f)))
