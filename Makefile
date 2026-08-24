# omarchy-robominds-light
#
#   make apply    regenerate colors.toml from palette.toml and re-apply theme
#   make update   git pull, then apply

THEME_SLUG := omarchy-robominds-light
PYTHON     ?= python3

.PHONY: apply update

apply:
	$(PYTHON) theme/robominds_theme.py omarchy
	omarchy theme set $(THEME_SLUG)

update:
	git pull --ff-only
	@$(MAKE) apply
