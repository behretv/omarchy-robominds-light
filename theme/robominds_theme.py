"""robominds light theme — single source of truth + generator.

Loads ``theme/palette.toml`` and renders the omarchy ``colors.toml`` from it.
That is the only file the installed theme needs: omarchy generates the
per-app configs (VS Code, Neovim, terminals, ...) from ``colors.toml`` via
templates.

CLI::

    python -m theme.robominds_theme            # writes colors.toml to repo root
    python -m theme.robominds_theme --out-dir dist

Programmatic::

    from theme.robominds_theme import Palette, SyntaxRole
    pal = Palette.load()
    pal.syntax(SyntaxRole.KEYWORD)  # -> "#7A2968"
    pal.to_omarchy_colors_toml()
"""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Any

import tomllib

HERE = Path(__file__).resolve().parent
DEFAULT_PALETTE = HERE / "palette.toml"


# ---------------------------------------------------------------------------
# Enums — typed keys into the TOML sections.
# ---------------------------------------------------------------------------


class BrandBlue(StrEnum):
    BLUE_900 = "900"
    BLUE_800 = "800"
    BLUE_700 = "700"
    BLUE_600 = "600"
    BLUE_500 = "500"
    BLUE_400 = "400"
    BLUE_300 = "300"
    BLUE_200 = "200"
    BLUE_100 = "100"


class BrandGray(StrEnum):
    GRAY_800 = "800"
    GRAY_700 = "700"
    GRAY_400 = "400"
    GRAY_300 = "300"
    GRAY_200 = "200"
    GRAY_100 = "100"
    GRAY_50 = "50"
    MIDNIGHT = "midnight"
    WHITE = "white"
    NAVY_GRAY_1 = "navy_gray_1"
    NAVY_GRAY_2 = "navy_gray_2"


class Accent(StrEnum):
    """Shade keys shared by every accent family (violet/green/yellow/...)."""

    SHADE_700 = "700"
    SHADE_500 = "500"
    SHADE_300 = "300"
    SHADE_100 = "100"


class TealAccent(StrEnum):
    """Teal has no 100 shade."""

    SHADE_700 = "700"
    SHADE_500 = "500"
    SHADE_300 = "300"


class UIRole(StrEnum):
    BACKGROUND = "background"
    DARK_BACKGROUND = "dark_background"
    DARKER_BACKGROUND = "darker_background"
    LIGHTER_BACKGROUND = "lighter_background"
    FOREGROUND = "foreground"
    DARK_FOREGROUND = "dark_foreground"
    LIGHT_FOREGROUND = "light_foreground"
    BRIGHT_FOREGROUND = "bright_foreground"
    ACCENT = "accent"
    SELECTION = "selection"
    MUTED = "muted"
    BORDER = "border"
    BORDER_STRONG = "border_strong"


class TerminalColor(StrEnum):
    RED = "red"
    YELLOW = "yellow"
    ORANGE = "orange"
    GREEN = "green"
    CYAN = "cyan"
    BLUE = "blue"
    MAGENTA = "magenta"
    BROWN = "brown"
    BRIGHT_RED = "bright_red"
    BRIGHT_YELLOW = "bright_yellow"
    BRIGHT_GREEN = "bright_green"
    BRIGHT_CYAN = "bright_cyan"
    BRIGHT_BLUE = "bright_blue"
    BRIGHT_MAGENTA = "bright_magenta"


class SyntaxRole(StrEnum):
    KEYWORD = "keyword"
    STORAGE = "storage"
    FUNCTION = "function"
    FUNCTION_BUILTIN = "function_builtin"
    METHOD = "method"
    PARAMETER = "parameter"
    PROPERTY = "property"
    NUMBER = "number"
    BOOLEAN = "boolean"
    TYPE = "type"
    CLASS = "class"
    INTERFACE = "interface"
    ENUM = "enum"
    STRING = "string"
    OPERATOR = "operator"
    COMMENT = "comment"
    VARIABLE = "variable"
    VARIABLE_BUILTIN = "variable_builtin"
    CONSTANT_BUILTIN = "constant_builtin"
    DECORATOR = "decorator"
    NAMESPACE = "namespace"
    TAG = "tag"
    PUNCTUATION = "punctuation"
    BRACKET = "bracket"
    SEPARATOR = "separator"


class StatusRole(StrEnum):
    SUCCESS = "success"
    WARNING = "warning"
    DANGER = "danger"
    INFO = "info"


# ---------------------------------------------------------------------------
# Color helpers
# ---------------------------------------------------------------------------


def _hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    h = hex_str.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02x}{g:02x}{b:02x}"


def mix(start: str, end: str, amount: float) -> str:
    """Mix two hex colors. amount=0 → start, amount=1 → end."""
    sr, sg, sb = _hex_to_rgb(start)
    er, eg, eb = _hex_to_rgb(end)
    return _rgb_to_hex(
        round(sr * (1 - amount) + er * amount),
        round(sg * (1 - amount) + eg * amount),
        round(sb * (1 - amount) + eb * amount),
    )


def with_alpha(hex_str: str, alpha: float) -> str:
    """Return an 8-digit hex (#RRGGBBAA) for use in VS Code / Neovim."""
    aa = round(alpha * 255)
    return f"{hex_str}{aa:02x}"


# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------


class Palette:
    """Loaded and validated palette.toml with typed accessors."""

    def __init__(self, data: dict[str, Any]) -> None:
        self._d = data
        self._validate()

    # -- loading -----------------------------------------------------------
    @classmethod
    def load(cls, path: Path | str = DEFAULT_PALETTE) -> "Palette":
        path = Path(path)
        with path.open("rb") as fh:
            return cls(tomllib.load(fh))

    # -- meta --------------------------------------------------------------
    @property
    def name(self) -> str:
        return self._d["meta"]["name"]

    @property
    def mode(self) -> str:
        return self._d["meta"]["mode"]

    # -- raw brand access --------------------------------------------------
    def brand_blue(self, shade: BrandBlue) -> str:
        return self._d["brand"]["blue"][shade.value]

    def brand_gray(self, shade: BrandGray) -> str:
        return (
            self._d["brand"]["neutral"]["gray"][shade.value]
            if shade.value[0].isdigit()
            else self._d["brand"]["neutral"][shade.value]
        )

    def accent(self, family: str, shade: Accent | TealAccent | str) -> str:
        key = shade.value if isinstance(shade, StrEnum) else shade
        return self._d["brand"]["accent"][family][key]

    # -- semantic access ---------------------------------------------------
    def ui(self, role: UIRole | str) -> str:
        key = role.value if isinstance(role, StrEnum) else role
        return self._d["ui"][key]

    def terminal(self, color: TerminalColor | str) -> str:
        key = color.value if isinstance(color, StrEnum) else color
        return self._d["terminal"][key]

    def syntax(self, role: SyntaxRole | str) -> str:
        key = role.value if isinstance(role, StrEnum) else role
        return self._d["syntax"][key]

    def status(self, role: StatusRole | str) -> str:
        key = role.value if isinstance(role, StrEnum) else role
        return self._d["status"][key]

    # -- convenience dicts -------------------------------------------------
    @property
    def ui_colors(self) -> dict[str, str]:
        return dict(self._d["ui"])

    @property
    def terminal_colors(self) -> dict[str, str]:
        return dict(self._d["terminal"])

    @property
    def syntax_colors(self) -> dict[str, str]:
        return dict(self._d["syntax"])

    @property
    def status_colors(self) -> dict[str, str]:
        return dict(self._d["status"])

    # -- validation --------------------------------------------------------
    def _validate(self) -> None:
        required = ("meta", "brand", "ui", "terminal", "syntax", "status")
        missing = [k for k in required if k not in self._d]
        if missing:
            raise ValueError(f"palette.toml missing sections: {missing}")
        # every hex must parse
        for section in ("ui", "terminal", "syntax", "status"):
            for key, val in self._d[section].items():
                if not val.startswith("#") or len(val) not in (4, 7):
                    raise ValueError(
                        f"[{section}] {key} = {val!r} is not a valid hex color"
                    )


# ---------------------------------------------------------------------------
# Generator: omarchy quattro colors.toml
# ---------------------------------------------------------------------------

OMARCHY_KEY_ORDER: tuple[str, ...] = (
    "mode",
    "accent",
    "selection",
    "muted",
    "background",
    "dark_background",
    "darker_background",
    "lighter_background",
    "foreground",
    "dark_foreground",
    "light_foreground",
    "bright_foreground",
    "red",
    "yellow",
    "orange",
    "green",
    "cyan",
    "blue",
    "magenta",
    "brown",
    "bright_red",
    "bright_yellow",
    "bright_green",
    "bright_cyan",
    "bright_blue",
    "bright_magenta",
)


def generate_omarchy_colors_toml(pal: Palette) -> str:
    """Render the omarchy quattro ``colors.toml`` from the palette."""
    term = pal.terminal_colors
    ui = pal.ui_colors
    mapping: dict[str, str] = {
        "mode": pal.mode,
        "accent": ui["accent"],
        "selection": ui["selection"],
        "muted": ui["muted"],
        "background": ui["background"],
        "dark_background": ui["dark_background"],
        "darker_background": ui["darker_background"],
        "lighter_background": ui["lighter_background"],
        "foreground": ui["foreground"],
        "dark_foreground": ui["dark_foreground"],
        "light_foreground": ui["light_foreground"],
        "bright_foreground": ui["bright_foreground"],
        "red": term["red"],
        "yellow": term["yellow"],
        "orange": term["orange"],
        "green": term["green"],
        "cyan": term["cyan"],
        "blue": term["blue"],
        "magenta": term["magenta"],
        "brown": term["brown"],
        "bright_red": term["bright_red"],
        "bright_yellow": term["bright_yellow"],
        "bright_green": term["bright_green"],
        "bright_cyan": term["bright_cyan"],
        "bright_blue": term["bright_blue"],
        "bright_magenta": term["bright_magenta"],
    }
    lines = [f'{k} = "{mapping[k]}"' for k in OMARCHY_KEY_ORDER]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

TARGETS = ("omarchy",)


def _write(text: str, path: Path, label: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"  ✓ {label}: {path}")


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        prog="python -m theme.robominds_theme",
        description="Generate the omarchy colors.toml from palette.toml.",
    )
    parser.add_argument(
        "target",
        nargs="?",
        default="omarchy",
        choices=TARGETS,
        help="what to generate (default: omarchy — writes colors.toml to repo root)",
    )
    parser.add_argument(
        "--palette", type=Path, default=DEFAULT_PALETTE, help="path to palette.toml"
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="output directory (default: repo root)",
    )
    args = parser.parse_args(argv)

    pal = Palette.load(args.palette)
    print(f"Loaded palette: {pal.name} ({pal.mode}) from {args.palette}")

    # colors.toml is the only file the installed theme needs; omarchy
    # generates the per-app configs (VS Code, Neovim, terminals, ...) from it
    # via templates.
    out_omarchy = args.out_dir or HERE.parent
    _write(
        generate_omarchy_colors_toml(pal),
        out_omarchy / "colors.toml",
        "omarchy quattro",
    )
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
