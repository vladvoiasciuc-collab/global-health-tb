"""Transform raw OWID CSV into the normalized observation table."""
from pathlib import Path
import pandas as pd


def transform_owid_file(path: Path, code: str) -> pd.DataFrame:
    """Turn a saved OWID chart CSV into the five-column normalized table.

    Expects columns: entity, code, year, and exactly one value column.
    """
    df = pd.read_csv(path)
    value_cols = [c for c in df.columns if c not in ("entity", "code", "year")]
    if len(value_cols) != 1:
        raise ValueError(f"{path}: expected exactly one value column, found {value_cols}")

    value_col = value_cols[0]
    return pd.DataFrame(
        {
            "country_iso3": df["code"],
            "indicator_code": code,
            "year": df["year"],
            "sex": None,
            "value": df[value_col],
        }
    )
