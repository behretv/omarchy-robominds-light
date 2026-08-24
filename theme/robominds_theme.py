"""robominds light theme — single source of truth + generators.

Loads ``theme/palette.toml`` and renders three targets from it:

* **omarchy quattro** — ``colors.toml`` (terminal 16-color + surface vocab)
* **VS Code**         — ``robominds-light-color-theme.json`` (self-contained)
* **Neovim**          — ``colors/robominds-light.lua`` (standalone colorscheme)

CLI::

    python -m theme.robominds_theme all      --out-dir dist
    python -m theme.robominds_theme omarchy  --out-dir dist
    python -m theme.robominds_theme vscode   --out-dir dist
    python -m theme.robominds_theme neovim   --out-dir dist

Programmatic::

    from theme.robominds_theme import Palette, SyntaxRole
    pal = Palette.load()
    pal.syntax(SyntaxRole.KEYWORD)  # -> "#7A2968"
    pal.to_omarchy_colors_toml()
"""

from __future__ import annotations

import json
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
# Generator: VS Code color theme (self-contained)
# ---------------------------------------------------------------------------


def _vscode_token(
    name: str, scope: list[str], color: str, fontStyle: str | None = None
) -> dict[str, Any]:
    settings: dict[str, Any] = {"foreground": color}
    if fontStyle:
        settings["fontStyle"] = fontStyle
    return {"name": name, "scope": scope, "settings": settings}


def generate_vscode_theme(pal: Palette) -> str:
    """Render a self-contained VS Code color-theme JSON."""
    ui = pal.ui_colors
    s = pal.syntax_colors
    st = pal.status_colors
    fg = ui["foreground"]
    muted = ui["muted"]
    border = ui["border"]
    border_strong = ui["border_strong"]
    bg = ui["background"]
    dark_bg = ui["dark_background"]
    darker_bg = ui["darker_background"]
    lighter_bg = ui["lighter_background"]
    accent = ui["accent"]

    theme: dict[str, Any] = {
        "name": pal.name,
        "type": pal.mode,
        "semanticHighlighting": True,
        "semanticTokenColors": {
            "keyword": s["keyword"],
            "storage": s["storage"],
            "storage.type": s["storage"],
            "function": s["function"],
            "function.defaultLibrary": s["function_builtin"],
            "method": s["method"],
            "parameter": s["parameter"],
            "parameter.declaration": s["parameter"],
            "property": s["property"],
            "property.declaration": s["property"],
            "property.readonly": s["property"],
            "variable": s["variable"],
            "variable.defaultLibrary": s["constant_builtin"],
            "variable.readonly": s["property"],
            "number": s["number"],
            "boolean": s["boolean"],
            "type": s["type"],
            "type.defaultLibrary": s["type"],
            "class": s["class"],
            "interface": s["interface"],
            "enum": s["enum"],
            "enumMember": s["property"],
            "operator": s["operator"],
            "macro": s["function_builtin"],
            "namespace": s["namespace"],
            "decorator": s["decorator"],
            "string": s["string"],
            "comment": s["comment"],
        },
        "colors": {
            # editor
            "editor.background": bg,
            "editor.foreground": fg,
            "editorLineNumber.foreground": ui["dark_foreground"],
            "editorLineNumber.activeForeground": fg,
            "editorCursor.foreground": accent,
            "editor.selectionBackground": ui["selection"],
            "editor.selectionForeground": ui["foreground"],
            "editor.inactiveSelectionBackground": mix(ui["selection"], bg, 0.5),
            "editor.selectionHighlightBackground": with_alpha(ui["selection"], 0.5),
            "editor.lineHighlightBackground": darker_bg,
            "editor.lineHighlightBorder": darker_bg,
            "editorIndentGuide.background": lighter_bg,
            "editorIndentGuide.activeBackground": border_strong,
            "editorWhitespace.foreground": lighter_bg,
            "editor.findMatchBackground": with_alpha(ui["selection"], 0.6),
            "editor.findMatchHighlightBackground": with_alpha(ui["selection"], 0.35),
            "editorLink.activeForeground": accent,
            "editorBracketMatch.background": with_alpha(accent, 0.15),
            "editorBracketMatch.border": with_alpha(accent, 0.5),
            "editorGutter.addedBackground": st["success"],
            "editorGutter.modifiedBackground": st["info"],
            "editorGutter.deletedBackground": st["danger"],
            # general
            "foreground": fg,
            "background": bg,
            "selection.background": ui["selection"],
            "descriptionForeground": ui["light_foreground"],
            "errorForeground": st["danger"],
            "focusBorder": with_alpha(accent, 0.45),
            "widget.shadow": with_alpha("#0A1946", 0.12),
            # sidebar / activity bar
            "sideBar.background": dark_bg,
            "sideBar.foreground": ui["light_foreground"],
            "sideBar.border": border,
            "sideBarTitle.foreground": fg,
            "sideBarSectionHeader.background": darker_bg,
            "sideBarSectionHeader.foreground": fg,
            "activityBar.background": dark_bg,
            "activityBar.foreground": fg,
            "activityBar.inactiveForeground": ui["dark_foreground"],
            "activityBar.activeBorder": accent,
            "activityBarBadge.background": accent,
            "activityBarBadge.foreground": "#FFFFFF",
            # lists / trees
            "list.activeSelectionBackground": with_alpha(accent, 0.18),
            "list.activeSelectionForeground": fg,
            "list.inactiveSelectionBackground": darker_bg,
            "list.inactiveSelectionForeground": fg,
            "list.hoverBackground": lighter_bg,
            "list.focusBackground": with_alpha(accent, 0.12),
            "list.highlightForeground": accent,
            # tabs
            "editorGroupHeader.tabsBorder": border,
            "tab.activeBackground": bg,
            "tab.activeForeground": fg,
            "tab.inactiveBackground": dark_bg,
            "tab.inactiveForeground": ui["dark_foreground"],
            "tab.border": border,
            "tab.activeBorderTop": accent,
            # editor groups / panes
            "editorGroup.border": border,
            "editorPane.background": bg,
            # status bar
            "statusBar.background": dark_bg,
            "statusBar.foreground": ui["light_foreground"],
            "statusBar.border": border,
            "statusBar.debuggingBackground": st["warning"],
            "statusBar.debuggingForeground": "#FFFFFF",
            "statusBar.noFolderBackground": dark_bg,
            # title bar
            "titleBar.activeBackground": dark_bg,
            "titleBar.activeForeground": fg,
            "titleBar.inactiveBackground": dark_bg,
            "titleBar.inactiveForeground": ui["dark_foreground"],
            "titleBar.border": border,
            # menus / command center
            "menu.background": bg,
            "menu.foreground": fg,
            "menu.border": border,
            "menu.selectionBackground": with_alpha(accent, 0.18),
            "menu.selectionForeground": fg,
            "commandCenter.foreground": ui["light_foreground"],
            "commandCenter.activeForeground": fg,
            "commandCenter.background": darker_bg,
            # inputs
            "input.background": bg,
            "input.foreground": fg,
            "input.border": border_strong,
            "inputOption.activeBorder": accent,
            "input.placeholderForeground": ui["dark_foreground"],
            "dropdown.background": bg,
            "dropdown.foreground": fg,
            "dropdown.border": border_strong,
            # buttons
            "button.background": accent,
            "button.foreground": "#FFFFFF",
            "button.hoverBackground": mix(accent, "#000000", 0.12),
            "button.border": "transparent",
            # peek / widgets
            "peekView.border": accent,
            "peekViewEditor.background": dark_bg,
            "peekViewResult.background": dark_bg,
            "peekViewResult.matchHighlightBackground": with_alpha(ui["selection"], 0.6),
            # notifications
            "notification.background": dark_bg,
            "notification.foreground": fg,
            "notificationCenter.border": border,
            # scrollbars
            "scrollbar.shadow": "transparent",
            "scrollbarSlider.background": with_alpha(ui["dark_foreground"], 0.35),
            "scrollbarSlider.hoverBackground": with_alpha(ui["dark_foreground"], 0.55),
            "scrollbarSlider.activeBackground": with_alpha(ui["dark_foreground"], 0.7),
            # panels
            "panel.background": dark_bg,
            "panel.border": border,
            "panelTitle.activeBorder": accent,
            "panelTitle.activeForeground": fg,
            "panelTitle.inactiveForeground": ui["dark_foreground"],
            "terminal.background": bg,
            "terminal.foreground": fg,
            "terminal.border": border,
            # git
            "gitDecoration.addedResourceForeground": st["success"],
            "gitDecoration.modifiedResourceForeground": st["info"],
            "gitDecoration.deletedResourceForeground": st["danger"],
            "gitDecoration.untrackedResourceForeground": st["success"],
            "gitDecoration.ignoredResourceForeground": ui["dark_foreground"],
            "gitDecoration.conflictingResourceForeground": st["warning"],
            # diff
            "diffEditor.insertedTextBackground": with_alpha(st["success"], 0.15),
            "diffEditor.removedTextBackground": with_alpha(st["danger"], 0.15),
            "diffEditor.insertedLineBackground": with_alpha(st["success"], 0.08),
            "diffEditor.removedLineBackground": with_alpha(st["danger"], 0.08),
            # minimap
            "minimap.background": dark_bg,
            "minimap.selectionHighlight": with_alpha(ui["selection"], 0.6),
            "minimapGutter.addedBackground": st["success"],
            "minimapGutter.modifiedBackground": st["info"],
            "minimapGutter.deletedBackground": st["danger"],
            # terminal ANSI (16 colors)
            "terminal.ansiBlack": ui["foreground"],
            "terminal.ansiRed": pal.terminal(TerminalColor.RED),
            "terminal.ansiGreen": pal.terminal(TerminalColor.GREEN),
            "terminal.ansiYellow": pal.terminal(TerminalColor.YELLOW),
            "terminal.ansiBlue": pal.terminal(TerminalColor.BLUE),
            "terminal.ansiMagenta": pal.terminal(TerminalColor.MAGENTA),
            "terminal.ansiCyan": pal.terminal(TerminalColor.CYAN),
            "terminal.ansiWhite": ui["dark_foreground"],
            "terminal.ansiBrightBlack": ui["light_foreground"],
            "terminal.ansiBrightRed": pal.terminal(TerminalColor.BRIGHT_RED),
            "terminal.ansiBrightGreen": pal.terminal(TerminalColor.BRIGHT_GREEN),
            "terminal.ansiBrightYellow": pal.terminal(TerminalColor.BRIGHT_YELLOW),
            "terminal.ansiBrightBlue": pal.terminal(TerminalColor.BRIGHT_BLUE),
            "terminal.ansiBrightMagenta": pal.terminal(TerminalColor.BRIGHT_MAGENTA),
            "terminal.ansiBrightCyan": pal.terminal(TerminalColor.BRIGHT_CYAN),
            "terminal.ansiBrightWhite": ui["bright_foreground"],
        },
        "tokenColors": [
            _vscode_token(
                "Comments",
                ["comment", "punctuation.definition.comment"],
                s["comment"],
                "italic",
            ),
            _vscode_token(
                "Brackets",
                ["punctuation.section", "meta.brace", "meta.bracket"],
                with_alpha(s["bracket"], 0.6),
            ),
            _vscode_token(
                "Separators",
                ["punctuation.separator", "punctuation.terminator"],
                with_alpha(s["separator"], 0.7),
            ),
            _vscode_token("Accessor", ["punctuation.accessor"], s["operator"]),
            _vscode_token(
                "Strings",
                ["string", "string.quoted", "string.unquoted", "string.template"],
                s["string"],
            ),
            _vscode_token("Numbers", ["constant.numeric"], s["number"]),
            _vscode_token("Booleans", ["constant.language.boolean"], s["boolean"]),
            _vscode_token(
                "Constants builtin",
                ["constant.language", "support.constant"],
                s["constant_builtin"],
            ),
            _vscode_token("Keywords", ["keyword"], s["keyword"]),
            _vscode_token("Control keywords", ["keyword.control"], s["keyword"]),
            _vscode_token("Imports", ["keyword.control.import"], s["function_builtin"]),
            _vscode_token("Operators", ["keyword.operator", "operator"], s["operator"]),
            _vscode_token("Storage", ["storage", "storage.type"], s["storage"]),
            _vscode_token("Storage modifier", ["storage.modifier"], s["storage"]),
            _vscode_token(
                "Functions", ["entity.name.function", "support.function"], s["function"]
            ),
            _vscode_token(
                "Function builtin",
                ["support.function.builtin", "support.function.construct"],
                s["function_builtin"],
            ),
            _vscode_token("Methods", ["entity.name.function.method"], s["method"]),
            _vscode_token(
                "Parameters", ["variable.parameter", "meta.parameter"], s["parameter"]
            ),
            _vscode_token(
                "Properties",
                ["variable.other.property", "variable.other.object.property"],
                s["property"],
            ),
            _vscode_token("Types", ["support.type", "entity.name.type"], s["type"]),
            _vscode_token("Classes", ["entity.name.type.class"], s["class"]),
            _vscode_token("Interfaces", ["entity.name.type.interface"], s["interface"]),
            _vscode_token("Enums", ["entity.name.type.enum"], s["enum"]),
            _vscode_token("Enum members", ["variable.other.enummember"], s["property"]),
            _vscode_token("Type builtin", ["support.type.primitive"], s["type"]),
            _vscode_token("Variables", ["variable", "meta.variable"], s["variable"]),
            _vscode_token(
                "Variable builtin",
                ["variable.language", "variable.other.readwrite"],
                s["variable"],
            ),
            _vscode_token(
                "This/Self",
                ["variable.language.this", "variable.language.self"],
                s["variable_builtin"],
                "italic",
            ),
            _vscode_token(
                "Decorators",
                ["meta.decorator", "entity.name.function.decorator"],
                s["decorator"],
            ),
            _vscode_token(
                "Namespaces",
                ["entity.name.namespace", "entity.name.module"],
                s["namespace"],
            ),
            _vscode_token("Constants", ["variable.other.constant"], s["property"]),
            _vscode_token("Tags", ["entity.name.tag"], s["tag"]),
            _vscode_token(
                "Tag attributes", ["entity.other.attribute-name"], s["property"]
            ),
            _vscode_token(
                "Punctuation", ["punctuation"], with_alpha(s["punctuation"], 0.6)
            ),
            _vscode_token(
                "String Punctuation",
                [
                    "punctuation.definition.string",
                    "punctuation.definition.string.begin",
                    "punctuation.definition.string.end",
                    "string.quoted punctuation.definition.string",
                ],
                s["string"],
            ),
            _vscode_token("Markup heading", ["markup.heading"], s["keyword"]),
            _vscode_token("Markup bold", ["markup.bold"], fg, "bold"),
            _vscode_token("Markup italic", ["markup.italic"], fg, "italic"),
            _vscode_token("Markup link", ["markup.underline.link"], accent),
            _vscode_token(
                "Markup raw", ["markup.inline.raw", "markup.fenced_code"], s["function"]
            ),
            _vscode_token("Diff inserted", ["markup.inserted"], st["success"]),
            _vscode_token("Diff deleted", ["markup.deleted"], st["danger"]),
            _vscode_token("Diff changed", ["markup.changed"], st["info"]),
        ],
    }
    return json.dumps(theme, indent=4) + "\n"


# ---------------------------------------------------------------------------
# Generator: Neovim colorscheme (lua)
# ---------------------------------------------------------------------------


def _lua_quote(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def generate_neovim_colorscheme(pal: Palette) -> str:
    """Render a standalone Neovim lua colorscheme (``colors/*.lua``)."""
    ui = pal.ui_colors
    s = pal.syntax_colors
    st = pal.status_colors
    term = pal.terminal_colors
    bg = ui["background"]
    dark_bg = ui["dark_background"]
    darker_bg = ui["darker_background"]
    lighter_bg = ui["lighter_background"]
    fg = ui["foreground"]
    light_fg = ui["light_foreground"]
    dark_fg = ui["dark_foreground"]
    accent = ui["accent"]
    selection = ui["selection"]
    muted = ui["muted"]
    border = ui["border"]
    border_strong = ui["border_strong"]

    # nvim_set_hl rejects #RRGGBBAA; approximate translucency by mixing
    # toward the background so we get a solid, valid 6-digit hex.
    def blend(color: str, alpha: float) -> str:
        return mix(color, bg, 1 - alpha)

    # (hl_group, {fg=, bg=, style=}) — style is a lua string like "italic"
    highlights: list[tuple[str, dict[str, str | None]]] = [
        # --- editor chrome ---
        ("Normal", {"fg": fg, "bg": bg}),
        ("NormalNC", {"fg": fg, "bg": bg}),
        ("NormalFloat", {"fg": fg, "bg": dark_bg}),
        ("FloatBorder", {"fg": border_strong, "bg": dark_bg}),
        ("FloatTitle", {"fg": accent, "bg": dark_bg}),
        ("Cursor", {"fg": bg, "bg": accent}),
        ("CursorColumn", {"bg": darker_bg}),
        ("CursorLine", {"bg": darker_bg}),
        ("CursorLineNr", {"fg": accent, "bg": darker_bg}),
        ("LineNr", {"fg": dark_fg}),
        ("LineNrAbove", {"fg": dark_fg}),
        ("SignColumn", {"bg": bg}),
        ("FoldColumn", {"fg": dark_fg, "bg": dark_bg}),
        ("Folded", {"fg": light_fg, "bg": darker_bg}),
        ("NonText", {"fg": lighter_bg}),
        ("Whitespace", {"fg": lighter_bg}),
        ("Conceal", {"fg": dark_fg}),
        ("EndOfBuffer", {"fg": lighter_bg}),
        ("Visual", {"bg": selection}),
        ("VisualNOS", {"bg": mix(selection, bg, 0.5)}),
        ("Search", {"fg": ui["foreground"], "bg": selection}),
        ("IncSearch", {"fg": bg, "bg": accent}),
        ("CurSearch", {"fg": bg, "bg": accent}),
        ("MatchParen", {"bg": blend(accent, 0.25)}),
        ("ColorColumn", {"bg": darker_bg}),
        ("Conceal", {"fg": dark_fg}),
        ("VertSplit", {"fg": border}),
        ("WinSeparator", {"fg": border}),
        ("WinBar", {"fg": light_fg, "bg": bg}),
        ("WinBarNC", {"fg": dark_fg, "bg": bg}),
        ("StatusLine", {"fg": light_fg, "bg": dark_bg}),
        ("StatusLineNC", {"fg": dark_fg, "bg": darker_bg}),
        ("StatusLineTerm", {"fg": light_fg, "bg": dark_bg}),
        ("StatusLineTermNC", {"fg": dark_fg, "bg": darker_bg}),
        ("TabLine", {"fg": dark_fg, "bg": darker_bg}),
        ("TabLineSel", {"fg": fg, "bg": bg}),
        ("TabLineFill", {"bg": dark_bg}),
        ("WinBar", {"fg": light_fg, "bg": bg}),
        ("Title", {"fg": accent}),
        ("Directory", {"fg": accent}),
        ("Question", {"fg": st["info"]}),
        ("MoreMsg", {"fg": st["success"]}),
        ("ModeMsg", {"fg": light_fg}),
        ("WarningMsg", {"fg": st["warning"]}),
        ("ErrorMsg", {"fg": st["danger"]}),
        ("Error", {"fg": st["danger"]}),
        ("Todo", {"fg": st["warning"], "style": "bold"}),
        ("Underlined", {"fg": accent, "style": "underline"}),
        ("Bold", {"style": "bold"}),
        ("Italic", {"style": "italic"}),
        # --- popup menu / completion ---
        ("Pmenu", {"fg": light_fg, "bg": dark_bg}),
        ("PmenuSel", {"fg": bg, "bg": accent}),
        ("PmenuSbar", {"bg": darker_bg}),
        ("PmenuThumb", {"bg": border_strong}),
        ("WildMenu", {"fg": bg, "bg": accent}),
        # --- spell / diagnostics ---
        ("SpellBad", {"style": "undercurl"}),
        ("SpellCap", {"style": "undercurl"}),
        ("SpellRare", {"style": "undercurl"}),
        ("SpellLocal", {"style": "undercurl"}),
        ("DiagnosticError", {"fg": st["danger"]}),
        ("DiagnosticWarn", {"fg": st["warning"]}),
        ("DiagnosticInfo", {"fg": st["info"]}),
        ("DiagnosticHint", {"fg": accent}),
        ("DiagnosticOk", {"fg": st["success"]}),
        ("DiagnosticUnderlineError", {"style": "undercurl", "sp": st["danger"]}),
        ("DiagnosticUnderlineWarn", {"style": "undercurl", "sp": st["warning"]}),
        ("DiagnosticUnderlineInfo", {"style": "undercurl", "sp": st["info"]}),
        ("DiagnosticUnderlineHint", {"style": "undercurl", "sp": accent}),
        (
            "DiagnosticVirtualTextError",
            {"fg": st["danger"], "bg": blend(st["danger"], 0.1)},
        ),
        (
            "DiagnosticVirtualTextWarn",
            {"fg": st["warning"], "bg": blend(st["warning"], 0.1)},
        ),
        (
            "DiagnosticVirtualTextInfo",
            {"fg": st["info"], "bg": blend(st["info"], 0.1)},
        ),
        ("DiagnosticVirtualTextHint", {"fg": accent, "bg": blend(accent, 0.1)}),
        # --- diff ---
        ("DiffAdd", {"bg": blend(st["success"], 0.15)}),
        ("DiffChange", {"bg": blend(st["info"], 0.12)}),
        ("DiffDelete", {"bg": blend(st["danger"], 0.15)}),
        ("DiffText", {"bg": blend(st["info"], 0.25)}),
        ("Added", {"fg": st["success"]}),
        ("Removed", {"fg": st["danger"]}),
        ("Changed", {"fg": st["info"]}),
        # --- git gutter ---
        ("GitGutterAdd", {"fg": st["success"]}),
        ("GitGutterChange", {"fg": st["info"]}),
        ("GitGutterDelete", {"fg": st["danger"]}),
        ("GitSignsAdd", {"fg": st["success"]}),
        ("GitSignsChange", {"fg": st["info"]}),
        ("GitSignsDelete", {"fg": st["danger"]}),
        # --- syntax (legacy) ---
        ("Comment", {"fg": muted, "style": "italic"}),
        ("Constant", {"fg": s["number"]}),
        ("String", {"fg": s["string"]}),
        ("Character", {"fg": s["string"]}),
        ("Number", {"fg": s["number"]}),
        ("Boolean", {"fg": s["boolean"]}),
        ("Float", {"fg": s["number"]}),
        ("Identifier", {"fg": s["variable"]}),
        ("Function", {"fg": s["function"]}),
        ("Statement", {"fg": s["keyword"]}),
        ("Conditional", {"fg": s["keyword"]}),
        ("Repeat", {"fg": s["keyword"]}),
        ("Label", {"fg": s["keyword"]}),
        ("Operator", {"fg": s["operator"]}),
        ("Keyword", {"fg": s["keyword"]}),
        ("Exception", {"fg": s["keyword"]}),
        ("PreProc", {"fg": s["decorator"]}),
        ("Include", {"fg": s["function_builtin"]}),
        ("Define", {"fg": s["decorator"]}),
        ("Macro", {"fg": s["function_builtin"]}),
        ("PreCondit", {"fg": s["decorator"]}),
        ("Type", {"fg": s["type"]}),
        ("StorageClass", {"fg": s["storage"]}),
        ("Structure", {"fg": s["type"]}),
        ("Typedef", {"fg": s["type"]}),
        ("Special", {"fg": s["function"]}),
        ("SpecialChar", {"fg": s["string"]}),
        ("Tag", {"fg": s["tag"]}),
        ("Delimiter", {"fg": s["separator"]}),
        ("SpecialComment", {"fg": muted, "style": "italic"}),
        ("Debug", {"fg": s["function_builtin"]}),
    ]

    # Treesitter / LSP semantic groups — reuse the syntax roles.
    ts_map: list[tuple[str, str, str | None]] = [
        ("@variable", s["variable"], None),
        ("@variable.builtin", s["variable_builtin"], "italic"),
        ("@variable.parameter", s["parameter"], None),
        ("@variable.member", s["property"], None),
        ("@constant", s["property"], None),
        ("@constant.builtin", s["constant_builtin"], None),
        ("@module", s["namespace"], None),
        ("@string", s["string"], None),
        ("@string.special", s["string"], None),
        ("@character", s["string"], None),
        ("@number", s["number"], None),
        ("@boolean", s["boolean"], None),
        ("@float", s["number"], None),
        ("@function", s["function"], None),
        ("@function.builtin", s["function_builtin"], None),
        ("@function.call", s["function"], None),
        ("@method", s["method"], None),
        ("@method.call", s["method"], None),
        ("@constructor", s["type"], None),
        ("@keyword", s["keyword"], None),
        ("@keyword.function", s["keyword"], None),
        ("@keyword.operator", s["operator"], None),
        ("@keyword.return", s["keyword"], None),
        ("@keyword.import", s["function_builtin"], None),
        ("@keyword.storage", s["storage"], None),
        ("@keyword.conditional", s["keyword"], None),
        ("@keyword.repeat", s["keyword"], None),
        ("@keyword.exception", s["keyword"], None),
        ("@operator", s["operator"], None),
        ("@punctuation.delimiter", s["separator"], None),
        ("@punctuation.bracket", s["bracket"], None),
        ("@punctuation.special", s["operator"], None),
        ("@type", s["type"], None),
        ("@type.builtin", s["type"], None),
        ("@type.definition", s["type"], None),
        ("@type.qualifier", s["storage"], None),
        ("@comment", s["comment"], "italic"),
        ("@comment.error", st["danger"], "italic"),
        ("@comment.todo", st["warning"], "italic"),
        ("@comment.note", st["info"], "italic"),
        ("@tag", s["tag"], None),
        ("@tag.attribute", s["property"], None),
        ("@tag.delimiter", s["operator"], None),
        ("@markup.heading", s["keyword"], "bold"),
        ("@markup.italic", fg, "italic"),
        ("@markup.bold", fg, "bold"),
        ("@markup.strikethrough", fg, "strikethrough"),
        ("@markup.link", accent, "underline"),
        ("@markup.link.label", s["function"], None),
        ("@markup.raw", s["function"], None),
        ("@markup.list", s["operator"], None),
        ("@diff.plus", st["success"], None),
        ("@diff.minus", st["danger"], None),
        ("@diff.delta", st["info"], None),
        ("@label", s["keyword"], None),
        # LSP semantic tokens
        ("@lsp.type.keyword", s["keyword"], None),
        ("@lsp.type.variable", s["variable"], None),
        ("@lsp.type.function", s["function"], None),
        ("@lsp.type.method", s["method"], None),
        ("@lsp.type.parameter", s["parameter"], None),
        ("@lsp.type.property", s["property"], None),
        ("@lsp.type.type", s["type"], None),
        ("@lsp.type.class", s["class"], None),
        ("@lsp.type.interface", s["interface"], None),
        ("@lsp.type.enum", s["enum"], None),
        ("@lsp.type.enumMember", s["property"], None),
        ("@lsp.type.macro", s["function_builtin"], None),
        ("@lsp.type.decorator", s["decorator"], None),
        ("@lsp.type.namespace", s["namespace"], None),
        ("@lsp.type.number", s["number"], None),
        ("@lsp.type.string", s["string"], None),
        ("@lsp.type.comment", s["comment"], None),
        ("@lsp.type.operator", s["operator"], None),
        ("@lsp.mod.deprecated", None, "strikethrough"),
    ]

    # --- build lua -------------------------------------------------------
    L: list[str] = []
    L.append(f"-- {pal.name}: generated from theme/palette.toml.")
    L.append("-- Do not edit by hand; re-run `python -m theme.robominds_theme neovim`.")
    L.append("")
    L.append("if vim.g.colors_name == 'robominds-light' then")
    L.append("  return")
    L.append("end")
    L.append("")
    L.append("vim.opt.background = 'light'")
    L.append("vim.api.nvim_command('hi clear')")
    L.append("if vim.fn.exists('syntax_on') then")
    L.append("  vim.api.nvim_command('syntax reset')")
    L.append("end")
    L.append(f"vim.g.colors_name = {_lua_quote(pal.name)}")
    L.append("")
    # terminal colors
    L.append("-- terminal ANSI colors")
    ansi = [
        fg,
        term["red"],
        term["green"],
        term["yellow"],
        term["blue"],
        term["magenta"],
        term["cyan"],
        dark_fg,
        light_fg,
        term["bright_red"],
        term["bright_green"],
        term["bright_yellow"],
        term["bright_blue"],
        term["bright_magenta"],
        term["bright_cyan"],
        ui["bright_foreground"],
    ]
    for i, c in enumerate(ansi):
        L.append(f"vim.g.terminal_color_{i} = {_lua_quote(c)}")
    L.append("vim.g.terminal_ansi_colors = {")
    for c in ansi:
        L.append(f"  {_lua_quote(c)},")
    L.append("}")
    L.append("")

    def emit(group: str, spec: dict[str, str | None]) -> None:
        parts: list[str] = []
        if spec.get("fg"):
            parts.append(f"fg = {_lua_quote(spec['fg'])}")  # type: ignore[arg-type]
        if spec.get("bg"):
            parts.append(f"bg = {_lua_quote(spec['bg'])}")  # type: ignore[arg-type]
        if spec.get("sp"):
            parts.append(f"sp = {_lua_quote(spec['sp'])}")  # type: ignore[arg-type]
        style = spec.get("style")
        if style:
            # nvim_set_hl takes boolean flags (italic = true), not a style string.
            for attr in style.replace(" ", "").split(","):
                if attr and attr != "none":
                    parts.append(f"{attr} = true")
        if not parts:
            parts.append("fg = 'NONE'")
        joined = ", ".join(parts)
        L.append(f"vim.api.nvim_set_hl(0, {_lua_quote(group)}, {{{joined}}})")

    L.append("-- editor + legacy syntax")
    for group, spec in highlights:
        emit(group, spec)
    L.append("")
    L.append("-- treesitter / @lsp semantic tokens")
    for group, color, style in ts_map:
        spec: dict[str, str | None] = {}
        if color:
            spec["fg"] = color
        if style:
            spec["style"] = style
        emit(group, spec)
    L.append("")
    L.append("-- LSP reference highlights")
    emit("LspReferenceText", {"bg": blend(selection, 0.5)})
    emit("LspReferenceRead", {"bg": blend(selection, 0.6)})
    emit("LspReferenceWrite", {"bg": blend(selection, 0.7)})
    L.append("")
    L.append("-- nvim-cmp / blink")
    emit("CmpItemAbbr", {"fg": fg})
    emit("CmpItemAbbrMatch", {"fg": accent})
    emit("CmpItemAbbrDeprecated", {"fg": dark_fg, "style": "strikethrough"})
    emit("CmpItemKind", {"fg": s["type"]})
    emit("CmpItemMenu", {"fg": dark_fg})
    emit("BlinkCmpLabel", {"fg": fg})
    emit("BlinkCmpLabelMatch", {"fg": accent})
    emit("BlinkCmpKind", {"fg": s["type"]})
    L.append("")
    L.append("-- indent-blankline / gitsigns current line blame")
    emit("IndentBlanklineChar", {"fg": lighter_bg})
    emit("IndentBlanklineContextChar", {"fg": border_strong})
    emit("GitSignsCurrentLineBlame", {"fg": dark_fg})
    L.append("")
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

TARGETS = ("all", "omarchy", "vscode", "neovim")


def _write(text: str, path: Path, label: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"  ✓ {label}: {path}")


def generate_all(pal: Palette, out_dir: Path) -> None:
    """Generate all targets. omarchy colors.toml goes to out_dir root,
    vscode/neovim go to out_dir/dist/ for standalone use."""
    _write(
        generate_omarchy_colors_toml(pal), out_dir / "colors.toml", "omarchy quattro"
    )
    _write(
        generate_vscode_theme(pal),
        out_dir / "dist" / "vscode" / "robominds-light-color-theme.json",
        "VS Code (standalone)",
    )
    _write(
        generate_neovim_colorscheme(pal),
        out_dir / "dist" / "neovim" / "colors" / "robominds-light.lua",
        "Neovim (standalone)",
    )


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        prog="python -m theme.robominds_theme",
        description="Generate omarchy quattro / VS Code / Neovim themes from palette.toml.",
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
        help="output directory (default: repo root for omarchy, ./dist for vscode/neovim)",
    )
    args = parser.parse_args(argv)

    pal = Palette.load(args.palette)
    print(f"Loaded palette: {pal.name} ({pal.mode}) from {args.palette}")

    # omarchy colors.toml goes to repo root; standalone targets go to dist/
    if args.target in ("all", "omarchy"):
        out_omarchy = args.out_dir or HERE.parent
        _write(
            generate_omarchy_colors_toml(pal),
            out_omarchy / "colors.toml",
            "omarchy quattro",
        )
    if args.target in ("all", "vscode"):
        out_standalone = args.out_dir or Path("dist")
        _write(
            generate_vscode_theme(pal),
            out_standalone / "vscode" / "robominds-light-color-theme.json",
            "VS Code (standalone)",
        )
    if args.target in ("all", "neovim"):
        out_standalone = args.out_dir or Path("dist")
        _write(
            generate_neovim_colorscheme(pal),
            out_standalone / "neovim" / "colors" / "robominds-light.lua",
            "Neovim (standalone)",
        )
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
