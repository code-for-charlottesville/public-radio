#!/usr/bin/env python3
"""Generate stations/<CALLSIGN>.yaml from _TEMPLATE.yaml for each callsign."""
import argparse
import re
import sys
from pathlib import Path

STATIONS = Path(__file__).resolve().parent.parent / "stations"
TEMPLATE = STATIONS / "_TEMPLATE.yaml"
CALLSIGNS = STATIONS / "callsigns.txt"
PLACEHOLDER = 'callsign: ""'
VALID = re.compile(r"^[A-Z]{3,4}$")


def read_callsigns(path):
    seen = {}
    for line in path.read_text().splitlines():
        call = line.strip().upper()
        if not call:
            continue
        if not VALID.match(call):
            sys.exit(f"Invalid callsign in {path.name}: {call!r}")
        seen.setdefault(call, None)
    return list(seen)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="overwrite existing files")
    args = parser.parse_args()

    template = TEMPLATE.read_text()
    if template.count(PLACEHOLDER) != 1:
        sys.exit(f"Expected exactly one {PLACEHOLDER!r} line in {TEMPLATE.name}")

    created = skipped = 0
    calls = read_callsigns(CALLSIGNS)
    for call in calls:
        out = STATIONS / f"{call}.yaml"
        if out.exists() and not args.force:
            skipped += 1
            continue
        out.write_text(template.replace(PLACEHOLDER, f'callsign: "{call}"'))
        created += 1

    print(f"{len(calls)} callsigns: {created} created, {skipped} skipped")


if __name__ == "__main__":
    main()
