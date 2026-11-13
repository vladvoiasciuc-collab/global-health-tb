"""Transform raw World Bank JSON into normalized observations and a country list."""
from pathlib import Path
import pandas as pd
from etl.json_types import read_json_records, require_keys


def transform_worldbank_countries(path: Path) -> pd.DataFrame:
    """Turn the World Bank countries JSON into a clean country table (no aggregates)."""
    records = read_json_records(path)
    if not records:
        return pd.DataFrame(columns=["iso3", "iso2", "name", "region", "income_group"])

    require_keys(records[0], ["id", "iso2Code", "name", "region", "incomeLevel"], context=str(path))

    df = pd.DataFrame(records)
    # Drop aggregates (region value is "Aggregates")
    df = df[df["region"].apply(lambda r: isinstance(r, dict) and r.get("value") != "Aggregates")]

    return pd.DataFrame(
        {
            "iso3": df["id"],
            "iso2": df["iso2Code"],
            "name": df["name"],
            "region": df["region"].apply(lambda r: r.get("value") if isinstance(r, dict) else None),
            "income_group": df["incomeLevel"].apply(lambda r: r.get("value") if isinstance(r, dict) else None),
        }
    )


def transform_worldbank_file(path: Path, code: str) -> pd.DataFrame:
    """Turn a saved World Bank indicator JSON into the five-column normalized table."""
    records = read_json_records(path)
    if not records:
        return pd.DataFrame(columns=["country_iso3", "indicator_code", "year", "sex", "value"])

    require_keys(records[0], ["countryiso3code", "date", "value"], context=str(path))

    raw = pd.DataFrame(records)
    return pd.DataFrame(
        {
            "country_iso3": raw["countryiso3code"],
            "indicator_code": code,
            "year": raw["date"],
            "sex": None,  # World Bank indicators are usually both sexes
            "value": raw["value"],
        }
    )
