# Global Health – Tuberculosis Burden

ETL pipeline that loads World Bank and WHO indicators into PostgreSQL for analysis of tuberculosis and related health/economic data.

## Architecture

![Architecture diagram](architecture_diagram.jpg)

## Database

- PostgreSQL 18
- Tables: `country`, `source`, `indicator`, `observation`, `import_log`
- Natural key on `observation`: `(country_iso3, indicator_id, year, sex)`
- Outlier flag: `is_outlier` (IQR method)

## Indicators

| Code | Name | Source |
|------|------|--------|
| SH.XPD.CHEX.GD.ZS | Current health expenditure (% of GDP) | World Bank |
| NY.GDP.PCAP.CD | GDP per capita (current US$) | World Bank |
| SH.DYN.AIDS.ZS | Prevalence of HIV (% of population ages 15-49) | World Bank |
| SH.TBS.CURE.ZS | Tuberculosis treatment success rate | World Bank |
| MDG_0000000020 | Tuberculosis incidence (per 100,000 population) | WHO |

## Lab 2 – Data Cleaning & Idempotent Load

### Outlier detection (IQR)

Outliers are flagged with the interquartile range method (Q1 - 1.5×IQR to Q3 + 1.5×IQR) and stored in `is_outlier`. They are not dropped.

Results after import:

| Indicator | Total rows | Outliers |
|-----------|------------|----------|
| MDG_0000000020 | 4713 | 375 |
| NY.GDP.PCAP.CD | 5242 | 423 |
| SH.DYN.AIDS.ZS | 3768 | 451 |
| SH.TBS.CURE.ZS | 4462 | 217 |
| SH.XPD.CHEX.GD.ZS | 4562 | 69 |

### Idempotent re-import

Re-running the import scripts does not create duplicate rows. The load uses `ON CONFLICT DO UPDATE` on the natural key.

Total observations after re-import: **22747**

## Screenshots

### pgAdmin – database tree
![pgAdmin tree](screenshots/pgadmin_tree.png)

### PostgreSQL version
![SELECT version](screenshots/select_version.png)

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m app.create_tables
python -m etl.import_worldbank
python -m etl.import_who
```

## Project structure

```
app/
  models.py
  database.py
  create_tables.py
etl/
  clean.py
  load.py
  import_worldbank.py
  import_who.py
```
