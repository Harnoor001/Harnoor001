# Profile panel generators

Every image on the profile is an animated SVG written by these scripts. GitHub
strips `<script>` and most CSS from READMEs but renders SVG `<img>`s, including
their CSS keyframes and SMIL animation, so that's where all the motion lives.

Run everything from the repo root.

| Panel | Script | Refresh |
|---|---|---|
| `assets/hero.svg` | `render_hero.py` | by hand, when the tagline changes |
| `assets/projects/*.svg` | `render_projects.py` (edit `PROJECTS`) | by hand, when featured projects change |
| `assets/neofetch.svg` | `render_neofetch.py` (edit `PROFILE` / `STACK`) | daily, via Actions |
| `assets/contributions.svg` | `render_heatmap.py` | daily, via Actions |

`fetch_github.py` writes `data/github.json` (contribution calendar scraped from
the public profile fragment, plus repo counts) that the two live panels read.
The workflow in `.github/workflows/refresh-profile.yml` runs it daily and on
demand (Actions tab → *Refresh profile panels* → *Run workflow*).

Shared colours and the terminal-window frame are in `theme.py`.
