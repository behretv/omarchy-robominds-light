# Makefile for the omarchy-robominds-light theme.
#
# The repo is cloned directly under ~/.config/omarchy/themes/, so the
# directory name IS the theme slug. Updating = git pull + regenerate
# colors.toml; refreshing = re-apply the theme via `omarchy theme set`.
#
# Common usage:
#   make update     # pull latest + regenerate colors.toml
#   make apply      # re-apply the theme to Omarchy
#   make refresh    # update + apply (the usual "I want it current" combo)
#   make build      # regenerate colors.toml from palette.toml only
#   make dist       # also render standalone VS Code + Neovim themes
#   make clean      # remove generated artifacts (colors.toml, dist/)

THEME_SLUG := omarchy-robominds-light
PYTHON     ?= python3

.PHONY: all update build dist apply refresh clean status help

# Default: bring everything up to date and re-apply.
all: refresh

# Pull latest from git, then regenerate colors.toml.
update:
	@git pull --ff-only
	@$(MAKE) --no-print-directory build

# Regenerate colors.toml from theme/palette.toml.
build:
	@$(PYTHON) -m theme.robominds_theme omarchy
	@echo ">> colors.toml regenerated"

# Render all standalone targets (colors.toml + vscode + neovim into dist/).
dist:
	@$(PYTHON) -m theme.robominds_theme all
	@echo ">> all targets regenerated"

# Re-apply the theme to Omarchy (picks up new colors.toml + backgrounds).
apply:
	@omarchy theme set $(THEME_SLUG)
	@echo ">> theme applied: $(THEME_SLUG)"

# The convenient one-shot: update sources, rebuild, re-apply.
refresh: update apply

# Show current theme status.
status:
	@echo "Repo:   $$(git remote get-url origin 2>/dev/null || echo '(no remote)')"
	@echo "Branch: $$(git branch --show-current)"
	@echo "Head:   $$(git log -1 --format='%h %s')"
	@echo "Theme:  $$(omarchy theme current)"

# Remove generated files. Does NOT touch backgrounds/ or theme/palette.toml.
clean:
	@rm -f colors.toml
	@rm -rf dist/
	@echo ">> cleaned colors.toml and dist/"

help:
	@echo "omarchy-robominds-light Makefile"
	@echo ""
	@echo "  make update    git pull + regenerate colors.toml"
	@echo "  make build     regenerate colors.toml from palette.toml"
	@echo "  make dist      regenerate colors.toml + vscode + neovim themes"
	@echo "  make apply     re-apply the theme to Omarchy"
	@echo "  make refresh   update + apply (default)"
	@echo "  make status    show repo + current theme info"
	@echo "  make clean     remove colors.toml and dist/"
	@echo "  make help      this message"
