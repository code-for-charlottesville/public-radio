import csv
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
