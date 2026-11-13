# Lab 2 – Prompts used

## Task 2.1 – Cleaning & Load

- Design a cleaning module that drops rows with missing year/value, unknown countries, and values outside plausible bounds.
- Make the load idempotent using PostgreSQL ON CONFLICT on the natural key (country_iso3, indicator_id, year, sex).

## Task 2.2 – Outlier detection

- Implement IQR-based outlier flagging (is_outlier column).
- Do not drop outliers, only mark them.
- Verify with a SQL query that groups by indicator and counts outliers.

## Task 2.3 – Re-import

- Confirm that re-running the import scripts does not increase the row count.
- Document the final observation count.

## Task 2.4 – Documentation

- Update README with Lab 2 results.
- Add docs/lab2_results.md and docs/prompts/lab2.md.
