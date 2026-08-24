"""robominds light theme — single source of truth + generators."""

from .robominds_theme import (
    Accent,
    BrandBlue,
    BrandGray,
    DEFAULT_PALETTE,
    Palette,
    StatusRole,
    SyntaxRole,
    TerminalColor,
    TealAccent,
    UIRole,
    generate_all,
    generate_neovim_colorscheme,
    generate_omarchy_colors_toml,
    generate_vscode_theme,
)

__all__ = [
    "Accent",
    "BrandBlue",
    "BrandGray",
    "DEFAULT_PALETTE",
    "Palette",
    "StatusRole",
    "SyntaxRole",
    "TerminalColor",
    "TealAccent",
    "UIRole",
    "generate_all",
    "generate_neovim_colorscheme",
    "generate_omarchy_colors_toml",
    "generate_vscode_theme",
]
