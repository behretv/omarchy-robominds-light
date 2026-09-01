# omarchy-robominds-light

A light Omarchy theme using the official robominds brand colors, extracted from
the [robominds living style guide](https://brand.robominds.de).

## Install

```bash
omarchy theme install https://github.com/<org>/omarchy-robominds-light.git
```

Or clone manually:

```bash
git clone https://github.com/<org>/omarchy-robominds-light.git \
  ~/.config/omarchy/themes/robominds-light
omarchy theme set robominds-light
```

## How it works

This repo doubles as:

1. **An installable Omarchy theme** — the repo root is the theme directory.
   `colors.toml` is the only required file; Omarchy auto-generates terminal
   configs, VS Code theme, Neovim (aether) config, shell colors, and more from
   it via templates on `omarchy theme set`.

2. **A build tool** — the [`theme/`](theme/) directory contains
   `palette.toml` (the single source of truth) and a Python generator that
   renders `colors.toml` from it. Edit colors in one place, regenerate.

```
omarchy-robominds-light/
├── colors.toml           ← generated: the omarchy quattro color file
├── backgrounds/          ← wallpaper images (add your own)
├── icons.theme            ← icon theme name
├── keyboard.rgb           ← keyboard RGB accent (hex without #)
├── LICENSE
├── README.md              ← you are here
├── .gitignore
└── theme/                 ← build tooling (not part of the installed theme)
    ├── palette.toml       ← single source of truth: all colors + semantic roles
    ├── robominds_theme.py ← enums, loader, generator (colors.toml)
    └── README.md          ← build tool docs
```

## Regenerating `colors.toml`

```bash
# writes colors.toml to repo root
python -m theme.robominds_theme

# or to a custom output directory
python -m theme.robominds_theme --out-dir dist
```

Requires Python 3.11+ (uses stdlib `tomllib`).

## Adding backgrounds

Drop wallpaper images into `backgrounds/` (jpg, png, webp). Omarchy cycles
through them with `omarchy theme bg next`.

## License

MIT
