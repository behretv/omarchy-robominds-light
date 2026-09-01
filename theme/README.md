# robominds-light theme generator

Build tool for the `omarchy-robominds-light` Omarchy theme. Defines all colors
in one place (`palette.toml`) and generates the theme files from it.

## Quick start

```bash
# default: writes colors.toml to repo root (the installable omarchy theme)
python -m theme.robominds_theme

# or to a custom output directory
python -m theme.robominds_theme --out-dir dist
```

Requires Python 3.11+ (uses stdlib `tomllib` — no pip installs).

## Output

The generator renders a single file: `colors.toml` (repo root by default). That
is the only file the installed theme needs — Omarchy auto-generates every
per-app config (terminal configs, VS Code theme, Neovim (aether), shell, etc.)
from it via templates on `omarchy theme set`.

## Source of truth: `palette.toml`

Six sections:

| Section | Purpose |
|---------|---------|
| `[meta]` | theme name, mode (`light`), version |
| `[brand]` | raw robominds brand palette (blue/gray/accent families) — the lookup table |
| `[ui]` | semantic UI roles: backgrounds, foregrounds, accent, selection, borders |
| `[terminal]` | 16-color terminal palette (omarchy quattro keys) |
| `[syntax]` | syntax highlighting roles (keyword, function, string, type, …) |
| `[status]` | success / warning / danger / info |

**To change a color:** edit the value in `[ui]`, `[terminal]`, `[syntax]`, or
`[status]` and re-run `python -m theme.robominds_theme`. The `[brand]` section
is the raw palette reference — map through the semantic sections, don't
reference brand directly in generators.

## Programmatic API

```python
from theme import Palette, SyntaxRole, UIRole, TerminalColor, BrandBlue

pal = Palette.load()  # loads theme/palette.toml

# typed enum access
pal.syntax(SyntaxRole.KEYWORD)  # "#7A2968"
pal.ui(UIRole.ACCENT)  # "#0052BB"
pal.terminal(TerminalColor.BRIGHT_GREEN)  # "#15803D"
pal.brand_blue(BrandBlue.BLUE_700)  # "#0052BB"

# string access (same thing, no import needed)
pal.syntax("keyword")  # "#7A2968"
pal.status("danger")  # "#D32F2F"

# raw dicts
pal.ui_colors  # {"background": "#FFFFFF", ...}
pal.terminal_colors  # {"red": "#9C1F1F", ...}
pal.syntax_colors  # {"keyword": "#7A2968", ...}

# generator (module-level function)
from theme import generate_omarchy_colors_toml

generate_omarchy_colors_toml(pal)  # -> string (colors.toml content)
```
