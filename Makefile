# omarchy-robominds-light
#
#   make install  clone this repo as an omarchy-managed theme and apply it
#   make update   pull latest changes in the installed theme and re-apply
#   make apply    regenerate theme files in the working copy and re-apply
#
# The theme is installed by `omarchy theme install`, which clones this repo
# into ~/.config/omarchy/themes/$(THEME_SLUG) (keeping its .git). Omarchy then
# manages updates via `omarchy theme update` and applies it with
# `omarchy theme set`.
#
# The theme ships only colors.toml (+ icons/keyboard/backgrounds); omarchy
# generates every per-app config (VS Code, Neovim, terminals, ...) from it via
# templates when the theme is applied.

REPO_URL  ?= git@github.com:behretv/omarchy-robominds-light.git
PYTHON    ?= python3
THEME_SLUG := robominds-light
THEME_DIR  := $(HOME)/.config/omarchy/themes/$(THEME_SLUG)

.PHONY: install update apply

install:
	omarchy theme install $(REPO_URL)

update:
	git -C $(CURDIR) pull --ff-only
	omarchy theme update
	omarchy theme set $(THEME_SLUG)

apply:
	$(PYTHON) theme/robominds_theme.py omarchy
ifeq ($(wildcard $(THEME_DIR)/.git),)
	$(error theme not installed at $(THEME_DIR); run 'make install' first)
endif
	cp -f colors.toml icons.theme keyboard.rgb LICENSE README.md $(THEME_DIR)/
	cp -rf backgrounds/* $(THEME_DIR)/backgrounds/
	cd $(THEME_DIR) && git add -A && git commit -m "Local: regenerated theme files" && git push
	omarchy theme set $(THEME_SLUG)
