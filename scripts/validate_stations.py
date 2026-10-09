#!/usr/bin/env python3
"""Validate station YAML files.

Usage: validate_stations.py [FILE ...]
With no arguments, validates every stations/*.yaml except _TEMPLATE.yaml.
Exits 1 if any file has errors.
"""
import os
import re
import sys
from pathlib import Path

import yaml

# Resolve stations/ relative to this script so it works from any directory
STATIONS = Path(__file__).resolve().parent.parent / "stations"

# The exact set of keys every station file must have (matches _TEMPLATE.yaml)
KEYS = [
    "callsign",
    "service_code",
    "frn",
    "control_of_respondent",
    "licensee_name",
    "top_level_owner",
]

# Callsigns are 3-4 uppercase letters (e.g. KUT, WBHM); same pattern as
# generate_stations.py
CALLSIGN = re.compile(r"^[A-Z]{3,4}$")
SERVICE_CODE = re.compile(r"^[A-Za-z]+$")
# FRNs are 10 digits and may have leading zeros, so they must stay strings
FRN = re.compile(r"^[0-9]{10}$")


def check(path):
    """Return a list of error messages for one file (empty if it is valid)."""
    try:
        data = yaml.safe_load(path.read_text())
    except yaml.YAMLError as exc:
        return [f"invalid YAML: {exc}"]
    if not isinstance(data, dict):
        return ["file must contain key: value pairs"]

    # Structural checks first: the right keys, each holding a clean string.
    # Later rules assume these hold, so bail out early if any fail.
    errors = []
    missing = [k for k in KEYS if k not in data]
    extra = [k for k in data if k not in KEYS]
    if missing:
        errors.append(f"missing keys: {', '.join(missing)}")
    if extra:
        errors.append(f"unexpected keys: {', '.join(map(str, extra))}")

    # Unquoted values like no, 0012345670 or an empty key parse as bool, int
    # or None instead of str, so reject anything that isn't a string
    values = {}
    for key in KEYS:
        if key not in data:
            continue
        value = data[key]
        if not isinstance(value, str):
            errors.append(f'{key}: must be a string, wrap the value in double quotes (got {value!r})')
        elif value != value.strip():
            errors.append(f"{key}: has leading or trailing whitespace")
        else:
            values[key] = value
    if errors:
        return errors

    # Field-level rules. Values are known to be clean strings from here on.
    callsign = values["callsign"]
    if not CALLSIGN.match(callsign):
        errors.append(f"callsign: must be 3-4 uppercase letters (got {callsign!r})")
    elif callsign != path.stem:
        # Only checked once the callsign itself is valid, to avoid noisy
        # duplicate messages
        errors.append(f"callsign: {callsign!r} does not match filename {path.name!r}")
    if not SERVICE_CODE.match(values["service_code"]):
        errors.append("service_code: must be letters only and not blank")
    if not FRN.match(values["frn"]):
        errors.append("frn: must be exactly 10 digits")
    control = values["control_of_respondent"]
    if control not in ("Y", "N"):
        errors.append('control_of_respondent: must be "Y" or "N"')
    if not values["licensee_name"]:
        errors.append("licensee_name: must not be blank")
    # An owner is only optional when the licensee is not controlled by anyone
    # else. An invalid control value also lands here, which is intended: we
    # can't say the blank is allowed.
    if control != "N" and not values["top_level_owner"]:
        errors.append('top_level_owner: may only be blank when control_of_respondent is "N"')
    return errors


def main():
    # Explicit file arguments (used by CI for the files changed in a PR),
    # otherwise every real station file. Files starting with "_" (the
    # template) are skipped.
    if len(sys.argv) > 1:
        paths = [Path(a) for a in sys.argv[1:]]
    else:
        paths = sorted(p for p in STATIONS.glob("*.yaml") if not p.name.startswith("_"))

    # In GitHub Actions, "::error file=...::msg" lines become inline
    # annotations on the PR; locally we print plain "path: msg" lines
    on_github = os.environ.get("GITHUB_ACTIONS") == "true"
    failed = 0
    for path in paths:
        if not path.is_file():
            errors = ["file not found"]
        else:
            errors = check(path)
        for msg in errors:
            print(f"::error file={path}::{msg}" if on_github else f"{path}: {msg}")
        failed += bool(errors)

    print(f"{len(paths)} files checked, {failed} with errors")
    # Non-zero exit is what makes the CI check fail
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
