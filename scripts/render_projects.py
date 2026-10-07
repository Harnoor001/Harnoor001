"""-> assets/projects/<repo>.svg: one animated card per featured project.

The README wraps each card in a link to its repo, which is the only way to
make part of an SVG image clickable on GitHub. Edit PROJECTS to change them.
"""

import os
import textwrap

from theme import BG, BLUE, BORDER, GREEN, MAROON, MONO, MUTED, ORANGE, PANEL, PURPLE, SOFT, TEXT, esc, write

OUT_DIR = "assets/projects"
W, H = 440, 250
PAD = 24
CH = 8.4  # forced glyph advance at 14px

PROJECTS = [
    {
        "repo": "Realtime-Delivery-ETA",
        "status": ("building in public", ORANGE),
        "desc": "Streaming ETA prediction for quick-commerce. "
        "Kafka events → Redis features → quantile LightGBM, served by FastAPI.",
        "metric": "p99 < 100 ms target · nightly retraining",
        "tags": ["Kafka", "Redis", "LightGBM", "FastAPI"],
    },
    {
        "repo": "Self-Pruning-Network",
        "status": ("research", PURPLE),
        "desc": "A CIFAR-10 network that learns which neurons matter, "
        "prunes the rest and fine-tunes into a smaller, faster model.",
        "metric": "−67% params · 8× faster · ~dense accuracy",
        "tags": ["PyTorch", "Pruning", "CIFAR-10"],
    },
    {
        "repo": "stock-market-trend-analysis",
        "status": ("dashboard", BLUE),
        "desc": "Returns, risk, volatility, SMA crossovers and correlations "
        "for five tech stocks, with an interactive dashboard.",
        "metric": "AAPL · MSFT · GOOGL · AMZN · NVDA vs SPY",
        "tags": ["Pandas", "Plotly", "yFinance", "Streamlit"],
    },
    {
        "repo": "TOPSIS-Text-Summarization-Model-Selection-A5",
        "title": "TOPSIS-Summarizer-Selection",
        "status": ("NLP", GREEN),
        "desc": "Picks the best summarization model (BART, T5, PEGASUS…) "
        "by trading ROUGE/BLEU quality against inference cost.",
        "metric": "5 transformers · 5 criteria · 1 winner",
        "tags": ["Transformers", "TOPSIS", "MCDM"],
    },
]


def mono(x, y, text, size=14, fill=SOFT, weight=None, advance=CH, anchor=None):
    extra = f' font-weight="{weight}"' if weight else ""
    extra += f' text-anchor="{anchor}"' if anchor else ""
    return (
        f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}"{extra} '
        f'textLength="{len(text) * advance:.1f}" lengthAdjust="spacingAndGlyphs">{esc(text)}</text>'
    )


def card(p):
    title = p.get("title", p["repo"])
    status, status_colour = p["status"]
    style = (
        ".up{animation:up .7s cubic-bezier(.2,.8,.2,1) both}"
        "@keyframes up{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}"
        ".p{animation:pop .4s ease-out both}@keyframes pop{from{opacity:0}to{opacity:1}}"
        "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"
    )
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'font-family="{esc(MONO)}"><style>{style}</style>'
        '<defs><linearGradient id="edge" x1="0" x2="1">'
        f'<stop offset="0" stop-color="{MAROON}"/><stop offset=".5" stop-color="{PURPLE}"/>'
        f'<stop offset="1" stop-color="{BLUE}"/></linearGradient>'
        '<linearGradient id="sheen" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        '<stop offset=".5" stop-color="#fff" stop-opacity=".9"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>'
        f'</linearGradient><clipPath id="card"><rect width="{W}" height="{H}" rx="12"/></clipPath></defs>'
        f'<g class="up"><rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="12" fill="{PANEL}" stroke="{BORDER}"/>'
        f'<g clip-path="url(#card)"><rect width="{W}" height="3" fill="url(#edge)"/>'
        # a highlight that sweeps along the top edge every few seconds
        f'<rect y="0" width="90" height="3" fill="url(#sheen)" x="-90">'
        f'<animate attributeName="x" values="-90;{W};{W}" keyTimes="0;.35;1" dur="5s" begin="1s" '
        f'repeatCount="indefinite"/></rect></g>'
    ]
    # repo glyph + title
    parts.append(
        f'<g transform="translate({PAD} 30)" fill="none" stroke="{MUTED}" stroke-width="1.5">'
        '<path d="M2 1.5h9.5v12H3.5a1.5 1.5 0 0 0-1.5 1.5zM2 15v-13.5"/><path d="M5 15v3l1.5-1 1.5 1v-3"/></g>'
        + mono(PAD + 22, 46, title, 16, BLUE, 700, 9.4)
    )
    # status pill, right-aligned on its own row so long repo names never collide
    sw = len(status) * 7.2 + 26
    parts.append(
        f'<g class="p" style="animation-delay:.5s"><rect x="{PAD}" y="62" width="{sw:.1f}" height="22" rx="11" '
        f'fill="none" stroke="{status_colour}" stroke-opacity=".6"/>'
        f'<circle cx="{PAD + 12}" cy="73" r="3.5" fill="{status_colour}">'
        f'<animate attributeName="opacity" values="1;.3;1" dur="2s" repeatCount="indefinite"/></circle>'
        + mono(PAD + 21, 77.5, status, 12, status_colour, None, 7.2)
        + "</g>"
    )
    y = 112
    lines = textwrap.wrap(p["desc"], 46)
    assert len(lines) <= 3, f"{p['repo']}: description needs {len(lines)} lines, max 3"
    for line in lines:
        parts.append(mono(PAD, y, line, 14, SOFT))
        y += 21
    y += 8
    parts.append(
        f'<g class="p" style="animation-delay:.8s">'
        + mono(PAD, y, "▸ " + p["metric"], 13, GREEN, None, 7.8)
        + "</g>"
    )
    x, y = PAD, H - 24
    for i, tag in enumerate(p["tags"]):
        tw = len(tag) * 7.2 + 18
        parts.append(
            f'<g class="p" style="animation-delay:{1 + i * .12:.2f}s">'
            f'<rect x="{x}" y="{y - 16}" width="{tw:.1f}" height="23" rx="6" fill="{BG}" stroke="{BORDER}"/>'
            + mono(x + 9, y, tag, 12, TEXT, None, 7.2)
            + "</g>"
        )
        x += tw + 8
    parts.append("</g></svg>")
    return "".join(parts)


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    for p in PROJECTS:
        write(f"{OUT_DIR}/{p['repo']}.svg", card(p))
