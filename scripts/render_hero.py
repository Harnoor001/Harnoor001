"""-> assets/hero.svg: a mock training run that "converges" into the name card.

Timeline: the command types itself, four epochs fill their progress bars while
the loss drops, then the name and tagline land. Plays once and holds.
"""

from theme import BLUE, BORDER, GREEN, HOST, MAROON, MUTED, ORANGE, PURPLE, SANS, SOFT, TEXT, esc, window, write

OUT = "assets/hero.svg"
W, H = 900, 396
X = 32
CH = 10.2  # forced glyph advance (textLength) so typing steps line up

COMMAND = "python train.py --model harnoor --epochs 4"
EPOCHS = [
    ("1.284", "0.41", "data wrangling"),
    ("0.637", "0.72", "classical ML"),
    ("0.219", "0.90", "deep learning"),
    ("0.058", "0.98", "production systems"),
]
NAME = "Harnoor Singh Khalsa"
TAGLINE = "Applied ML  ·  real-time systems  ·  AI-assisted engineering"
SUB = "Computer Engineering @ Thapar Institute of Engineering & Technology"


def typed(x, y, text, begin, colour=SOFT, size=17, per_char=0.035):
    """Monospace text revealed one glyph at a time via a stepped clip-path."""
    n = len(text)
    width = n * CH
    cid = f"t{int(x)}-{int(y)}"
    steps = ";".join(f"{i * CH:.1f}" for i in range(n + 1))
    return (
        f'<clipPath id="{cid}"><rect x="{x}" y="{y - size}" height="{size + 6}" width="0">'
        f'<animate attributeName="width" values="{steps}" calcMode="discrete" '
        f'begin="{begin:.2f}s" dur="{n * per_char:.2f}s" fill="freeze"/></rect></clipPath>'
        f'<text clip-path="url(#{cid})" x="{x}" y="{y}" font-size="{size}" fill="{colour}" '
        f'textLength="{width:.1f}" lengthAdjust="spacingAndGlyphs" xml:space="preserve">{esc(text)}</text>'
    ), begin + n * per_char


def build():
    style = (
        ".f{animation:fade .5s ease-out both}"
        "@keyframes fade{from{opacity:0}to{opacity:1}}"
        ".up{animation:up .8s cubic-bezier(.2,.8,.2,1) both}"
        "@keyframes up{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}"
        ".k{animation:blink 1s steps(1) infinite}@keyframes blink{50%{opacity:0}}"
    )
    defs = (
        '<defs><linearGradient id="name" x1="0" x2="1">'
        f'<stop offset="0" stop-color="{MAROON}"/><stop offset=".55" stop-color="{PURPLE}"/>'
        f'<stop offset="1" stop-color="{BLUE}"/></linearGradient></defs>'
    )
    parts = [defs, f'<text x="{X}" y="72" font-size="17" fill="{GREEN}">$</text>']
    cmd, t = typed(X + 2 * CH, 72, COMMAND, 0.3)
    parts.append(cmd)

    bar_x, bar_w = X + 13 * CH, 300
    y = 108
    t += 0.25
    for i, (loss, acc, stage) in enumerate(EPOCHS):
        dur = 0.55
        parts.append(
            f'<g class="f" style="animation-delay:{t:.2f}s">'
            f'<text x="{X}" y="{y}" font-size="16" fill="{MUTED}">epoch {i + 1}/4</text>'
            f'<rect x="{bar_x}" y="{y - 12}" width="{bar_w}" height="12" rx="3" fill="#21262d" stroke="{BORDER}"/>'
            f"</g>"
            f'<rect x="{bar_x}" y="{y - 12}" width="0" height="12" rx="3" fill="{GREEN}">'
            f'<animate attributeName="width" from="0" to="{bar_w}" begin="{t:.2f}s" dur="{dur}s" '
            f'calcMode="spline" keySplines=".4 0 .2 1" keyTimes="0;1" fill="freeze"/></rect>'
            f'<g class="f" style="animation-delay:{t + dur:.2f}s">'
            f'<text x="{bar_x + bar_w + 18}" y="{y}" font-size="16" fill="{SOFT}">'
            f'loss <tspan fill="{ORANGE}">{loss}</tspan>  acc <tspan fill="{GREEN}">{acc}</tspan>'
            f'<tspan fill="{MUTED}">  # {esc(stage)}</tspan></text></g>'
        )
        t += dur + 0.12
        y += 30

    y += 14
    parts.append(
        f'<g class="f" style="animation-delay:{t:.2f}s"><text x="{X}" y="{y}" font-size="16" fill="{GREEN}">'
        f'✓ converged <tspan fill="{MUTED}">· checkpoint saved →</tspan></text></g>'
    )
    t += 0.35
    parts.append(
        f'<g class="up" style="animation-delay:{t:.2f}s">'
        f'<text x="{X}" y="{y + 62}" font-family="{esc(SANS)}" font-size="46" font-weight="800" '
        f'fill="url(#name)" letter-spacing="-0.5">{esc(NAME)}</text></g>'
    )
    t += 0.45
    tag, t = typed(X, y + 98, TAGLINE, t, TEXT, 17, 0.022)
    parts.append(tag)
    parts.append(
        f'<g class="f" style="animation-delay:{t:.2f}s"><text x="{X}" y="{y + 126}" font-size="14" '
        f'fill="{MUTED}" textLength="{len(SUB) * 8.4:.1f}" lengthAdjust="spacingAndGlyphs">{esc(SUB)}</text>'
        f'<rect class="k" x="{X + len(SUB) * 8.4 + 8}" y="{y + 114}" width="9" height="16" fill="{SOFT}"/></g>'
    )
    assert y + 126 < H - 16
    return window(W, H, f"{HOST}: ~/profile", "".join(parts), style)


if __name__ == "__main__":
    write(OUT, build())
