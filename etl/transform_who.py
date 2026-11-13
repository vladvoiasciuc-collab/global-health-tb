"""Transform raw WHO GHO JSON into the normalized observation table."""
from pathlib import Path
import pandas as pd
from etl.json_types import read_json_records, require_keys

_SEX_DIMENSION = "SEX"


def transform_who_file(path: Path, code: str) -> pd.DataFrame:
    """Turn a saved WHO indicator JSON file into the five-column normalized table."""
    records = read_json_records(path)
    if not records:
        return pd.DataFrame(columns=["country_iso3", "indicator_code", "year", "sex", "value"])

    # Validate a sample record has the expected fields
    require_keys(records[0], ["SpatialDim", "TimeDim", "NumericValue"], context=str(path))

    raw = pd.DataFrame(records)

    # Sex is in Dim1 only when Dim1Type == SEX; otherwise drop the row
    if "Dim1" in raw.columns and "Dim1Type" in raw.columns:
        dim1_type = raw["Dim1Type"]
        raw = raw[dim1_type.isna() | (dim1_type == _SEX_DIMENSION)]
        sex = raw["Dim1"].where(raw["Dim1Type"] == _SEX_DIMENSION)
    else:
        sex = None

    return pd.DataFrame(
        {
            "country_iso3": raw["SpatialDim"],
            "indicator_code": code,
            "year": raw["TimeDim"],
            "sex": sex,
            "value": raw["NumericValue"],
        }
    )
