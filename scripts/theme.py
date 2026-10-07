"""Shared palette and terminal-window chrome for every profile SVG.

GitHub strips <script> and most inline CSS from READMEs, but it renders SVG
files referenced by <img>, including their CSS keyframes and SMIL animation.
Everything here is therefore plain SVG text, with no external fonts or assets.
"""

from xml.sax.saxutils import escape

USER = "Harnoor001"
HOST = "harnoor@tiet"

MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"

BG_TOP = "#111722"
BG = "#0d1117"
PANEL = "#161b22"
BORDER = "#30363d"
TEXT = "#e6edf3"
SOFT = "#c9d1d9"
MUTED = "#7d8590"
GREEN = "#3fb950"
BLUE = "#58a6ff"
PURPLE = "#d2a8ff"
ORANGE = "#ffa657"
RED = "#ff7b72"
MAROON = "#e5536f"  # turban accent, used sparingly

HEAT = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

# CSS animations use `both` fill and never a hidden base style, so switching
# them off leaves every element in its final, visible state.
REDUCED_MOTION = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"


def esc(s):
    return escape(str(s), {'"': "&quot;"})


def window(width, height, title, body, style="", font=MONO):
    """Wrap `body` in a macOS-style terminal window."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="{esc(font)}">'
        f"<style>{style}{REDUCED_MOTION}</style>"
        '<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{BG_TOP}"/><stop offset="1" stop-color="{BG}"/>'
        "</linearGradient></defs>"
        f'<rect width="{width}" height="{height}" rx="12" fill="url(#bg)"/>'
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="12" '
        f'fill="none" stroke="{BORDER}"/>'
        f'<line x1="0" y1="34" x2="{width}" y2="34" stroke="{BORDER}"/>'
        '<circle cx="22" cy="17" r="6" fill="#ff5f56"/>'
        '<circle cx="42" cy="17" r="6" fill="#ffbd2e"/>'
        '<circle cx="62" cy="17" r="6" fill="#27c93f"/>'
        f'<text x="{width / 2}" y="22" fill="{MUTED}" font-size="14" '
        f'text-anchor="middle">{esc(title)}</text>'
        f"{body}</svg>"
    )


def write(path, svg):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(svg)
    print(f"wrote {path} ({len(svg) / 1024:.1f} KB)")
