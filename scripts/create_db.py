import csv
import json
import re
import sqlite3
from pathlib import Path

import pandas as pd

# Create a database connection, create db if does not exist
con = sqlite3.connect("public_radio_facility_data.sqlite")

# Loop over the .dat files in the tables directory
for path in Path("tables").glob("*.dat"):
    # Get the table name from the file name
    table_name = path.stem
    read_kwargs = dict(
        delimiter="|",
        dtype=str,
        quoting=csv.QUOTE_NONE,
        encoding="utf-8",
        keep_default_na=False,
    )
    try:
        df = pd.read_csv(path, **read_kwargs)
    except pd.errors.ParserError:
        # the C parser hits a buffer overflow on some files (e.g. the
        # ownership_reports table); the slower python engine handles them
        df = pd.read_csv(path, engine="python", **read_kwargs)
    # drop the trailing "^" and empty columns caused by the "^|" row terminator
    df = df.loc[:, ~df.columns.str.startswith(("^", "Unnamed"))]

    # empty strings -> NULL, and the 1753 placeholder date -> NULL
    df = df.replace({"": None})
    df = df.replace(r"^1753-01-01.*", None, regex=True)

    # Sanitize the table name to ensure it is a valid SQLite table name
    table_name = re.sub(r"\W", "_", path.stem)
    df.to_sql(table_name, con, if_exists="replace", index=False)
    print(f"{path.name}: {len(df):,} rows -> table {table_name}")



def contour_to_geojson(contour):
    """Turn "lat ,lon|lat ,lon|..." into a GeoJSON Polygon string.

    GeoJSON wants [lon, lat] order, and the ring must be closed, so the first
    point (azimuth 0) is repeated at the end (azimuth 360). Returns None if any
    point is missing or unparseable.
    """
    try:
        ring = []
        for point in contour.split("|"):
            lat, lon = (float(v) for v in point.split(","))
            ring.append([lon, lat])
    except ValueError:
        return None
    if len(ring) < 3:
        return None
    ring.append(ring[0])
    return json.dumps({"type": "Polygon", "coordinates": [ring]}, separators=(",", ":"))


# The FCC FM contour file is pipe-delimited text with one row per application:
# ids, the transmitter site, then 360 "lat ,lon" points (one per degree,
# clockwise from true north). Keep the 360 points as one string in `contour`
# instead of 360 columns; split on "|" to recover them.
contour_path = Path("tables/FM_service_contour_current.txt")
if contour_path.exists():
    rows = []
    with contour_path.open(encoding="utf-8") as f:
        next(f)  # header
        for line in f:
            parts = [p.strip() for p in line.rstrip("\n").split("|")]
            if len(parts) < 6:
                continue
            # first 5 fields are ids/site; the rest are contour points, minus
            # the trailing "^" row terminator
            points = [p for p in parts[5:] if p and p != "^"]
            rows.append((*parts[:5], "|".join(points)))
    contours = pd.DataFrame(
        rows,
        columns=[
            "application_id",
            "service",
            "lms_application_id",
            "dts_site_number",
            "transmitter_site",
            "contour",
        ],
    )
    # The FCC file repeats a few rows verbatim; drop them so that
    # (lms_application_id, dts_site_number) is a unique key.
    contours = contours.drop_duplicates()
    # `geometry` is the column datasette-geojson-map renders on a map
    contours["geometry"] = contours["contour"].map(contour_to_geojson)
    contours.to_sql("fm_service_contour", con, if_exists="replace", index=False)
    print(f"{contour_path.name}: {len(contours):,} rows -> table fm_service_contour")

# Indexes on the filter/join columns keep callsign lookups fast. The view is a
# ready-made query that SQLite browsers open like a table: filter its callsign
# column to look up a single station.
con.executescript(
    """
    CREATE INDEX IF NOT EXISTS idx_facility_callsign
        ON facility (callsign);
    CREATE INDEX IF NOT EXISTS idx_facility_applicant_facility_uuid
        ON facility_applicant (facility_uuid);
    CREATE INDEX IF NOT EXISTS idx_facility_applicant_frn
        ON facility_applicant (frn);
    CREATE INDEX IF NOT EXISTS idx_facility_facility_id
        ON facility (facility_id);
    CREATE INDEX IF NOT EXISTS idx_application_facility_facility_id
        ON application_facility (afac_facility_id);
    CREATE INDEX IF NOT EXISTS idx_application_facility_application_id
        ON application_facility (afac_application_id);
    CREATE INDEX IF NOT EXISTS idx_application_application_id
        ON application (aapp_application_id);
    CREATE UNIQUE INDEX IF NOT EXISTS idx_fm_service_contour_key
        ON fm_service_contour (lms_application_id, dts_site_number);
    CREATE INDEX IF NOT EXISTS idx_respondent_frn
        ON ownership_reports_respondent_representative_info (respondent_frn);

    DROP VIEW IF EXISTS station_ownership;
    CREATE VIEW station_ownership AS
    SELECT DISTINCT
        f.facility_id,
        f.callsign,
        f.service_code,
        fa.legal_name AS licensee_name,
        fa.frn,
        r.control_of_respondent,
        r.organization AS respondent_organization,
        r.nature_of_respondent
    FROM facility f
    JOIN facility_applicant fa
        ON f.facility_uuid = fa.facility_uuid
    LEFT JOIN ownership_reports_respondent_representative_info r
        ON fa.frn = r.respondent_frn
    WHERE fa.contact_ind = 'N';

    DROP VIEW IF EXISTS facility_by_frn;
    CREATE VIEW facility_by_frn AS
    SELECT
		f.*,
		fa.legal_name as licensee_name,
		fa.frn
	FROM facility f
	JOIN facility_applicant fa
		ON f.facility_uuid = fa.facility_uuid
	WHERE fa.contact_ind = 'N'
	ORDER BY f.service_code, f.callsign;
    """
)
con.commit()
con.close()
