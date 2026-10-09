.PHONY: help db stations stations-force validate

help:
	@echo "Targets:"
	@echo "  make db              Build public_radio_facility_data.sqlite from tables/*.dat"
	@echo "  make stations        Generate stations/<CALLSIGN>.yaml (skips existing files)"
	@echo "  make stations-force  Regenerate all station files, overwriting existing ones"
	@echo "  make validate        Validate station YAML files (all, or FILES=\"stations/WBHM.yaml ...\")"

# create_db.py uses paths relative to the repo root, so run make from here.
# uv creates .venv and installs dependencies from pyproject.toml on first run.
db:
	uv run scripts/create_db.py

stations:
	uv run scripts/generate_stations.py

stations-force:
	uv run scripts/generate_stations.py --force

# Unfilled stub files fail validation, so pass FILES to check only specific ones.
validate:
	uv run scripts/validate_stations.py $(FILES)
