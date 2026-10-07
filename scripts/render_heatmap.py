"""data/github.json -> assets/contributions.svg (animated contribution graph).

Cells pop in along a diagonal sweep; active days flash bright as they land.
"""

import datetime as dt
import json

from theme import BLUE, GREEN, HEAT, HOST, MUTED, SANS, SOFT, TEXT, esc, window, write

DATA = "data/github.json"
OUT = "assets/contributions.svg"

CELL, GAP = 13, 3
STEP = CELL + GAP
LEFT, TOP = 46, 100


def build(data):
    days = data["days"]
    first = dt.date.fromisoformat(days[0]["date"])
    offset = (first.weekday() + 1) % 7  # GitHub columns start on Sunday
    weeks = (len(days) + offset + 6) // 7
    W = LEFT + weeks * STEP + 22
    H = TOP + 7 * STEP + 70

    style = (
        ".c{transform-box:fill-box;transform-origin:center;"
        "animation:pop .5s cubic-bezier(.2,.9,.3,1.3) both}"
        ".on{animation:pop .5s cubic-bezier(.2,.9,.3,1.3) both,glow .9s ease-out both}"
        "@keyframes pop{0%{opacity:0;transform:scale(.2)}100%{opacity:1;transform:scale(1)}}"
        "@keyframes glow{0%,40%{filter:brightness(2.2)}100%{filter:brightness(1)}}"
        ".f{animation:fade .6s ease-out both}"
        "@keyframes fade{from{opacity:0}to{opacity:1}}"
    )

    parts = [
        f'<text x="24" y="64" font-size="15" fill="{GREEN}">$ <tspan fill="{SOFT}">'
        f"git log --author={esc(HOST.split('@')[0])} --since=&quot;1 year ago&quot; | heatmap</tspan></text>"
    ]

    # month labels where a new month starts in the first row of a column
    seen = None
    for i, d in enumerate(days):
        col, row = divmod(i + offset, 7)
        date = dt.date.fromisoformat(d["date"])
        if row == 0 or i == 0:
            if date.month != seen and col < weeks - 1:
                parts.append(
                    f'<text x="{LEFT + col * STEP}" y="{TOP - 6}" font-size="12" '
                    f'font-family="{esc(SANS)}" fill="{MUTED}">{date:%b}</text>'
                )
                seen = date.month
    for row, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        parts.append(
            f'<text x="12" y="{TOP + row * STEP + 10}" font-size="11" '
            f'font-family="{esc(SANS)}" fill="{MUTED}">{label}</text>'
        )

    for i, d in enumerate(days):
        col, row = divmod(i + offset, 7)
        delay = (col + row * 1.5) * 0.028
        cls = "c on" if d["count"] else "c"
        parts.append(
            f'<rect class="{cls}" x="{LEFT + col * STEP}" y="{TOP + row * STEP}" width="{CELL}" '
            f'height="{CELL}" rx="2.5" fill="{HEAT[min(d["level"], 4)]}" '
            f'style="animation-delay:{delay:.2f}s"/>'
        )

    end = (weeks + 9) * 0.028 + 0.3
    best = dt.date.fromisoformat(data["best_day"]["date"])
    y = TOP + 7 * STEP + 34
    summary = (
        f'<tspan fill="{TEXT}" font-weight="700">{data["total"]}</tspan> contributions in the last year'
        f'  ·  <tspan fill="{TEXT}" font-weight="700">{data["active_days"]}</tspan> active days'
        f'  ·  best day <tspan fill="{TEXT}" font-weight="700">{data["best_day"]["count"]}</tspan>'
        f" ({best:%b} {best.day})"
    )
    parts.append(
        f'<g class="f" style="animation-delay:{end:.2f}s">'
        f'<text x="24" y="{y}" font-size="14" fill="{MUTED}">{summary}</text>'
        f'<text x="{W - 24 - 5 * 16 - 78}" y="{y}" font-size="12" font-family="{esc(SANS)}" fill="{MUTED}">Less</text>'
        + "".join(
            f'<rect x="{W - 24 - 5 * 16 - 40 + k * 16}" y="{y - 11}" width="12" height="12" rx="2.5" fill="{c}"/>'
            for k, c in enumerate(HEAT)
        )
        + f'<text x="{W - 24 - 30}" y="{y}" font-size="12" font-family="{esc(SANS)}" fill="{MUTED}">More</text>'
        f'<text x="{W - 24}" y="{H - 12}" font-size="11" fill="{BLUE}" text-anchor="end" opacity="0.7">'
        f'refreshed {esc(data["updated"])}</text>'
        "</g>"
    )
    return window(W, H, f"{HOST}: ~/contributions", "".join(parts), style)


if __name__ == "__main__":
    with open(DATA, encoding="utf-8") as f:
        write(OUT, build(json.load(f)))
