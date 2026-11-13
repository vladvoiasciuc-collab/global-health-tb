"""Data cleaning for normalized observations before they reach the database.

Implements the techniques from Lab 1 section 1.5 and Lab 2 section 2.3.
"""
from dataclasses import dataclass
import logging
import pandas as pd

logger = logging.getLogger(__name__)

# Sex codes used in the Observation model (from Lab 1)
_VALID_SEX = {"BTSX", "MLE", "FMLE"}
_SEX_MAP = {
    "Male": "MLE",
    "Female": "FMLE",
    "Both sexes": "BTSX",
    "BTSX": "BTSX",
    "MLE": "MLE",
    "FMLE": "FMLE",
    None: "BTSX",
}

_KEY_COLUMNS = ["country_iso3", "indicator_code", "year", "sex"]


@dataclass(frozen=True)
class _Bounds:
    low: float
    high: float
    low_inclusive: bool = True


# Plausible bounds per indicator (extend for TB indicators as needed)
_INDICATOR_BOUNDS: dict[str, _Bounds] = {
    "SH.XPD.CHEX.GD.ZS": _Bounds(0, 30),          # health expenditure % GDP
    "NY.GDP.PCAP.CD": _Bounds(0, 500_000, low_inclusive=False),
    "SH.DYN.AIDS.ZS": _Bounds(0, 40),
    "SH.TBS.CURE.ZS": _Bounds(0, 100),
    # Add TB-specific WHO codes here when you use them
    # "MDG_0000000020": _Bounds(0, 1000),
}


def _drop(cleaned: pd.DataFrame, mask: pd.Series, reason: str) -> pd.DataFrame:
    """Drop rows where mask is True and log how many were dropped."""
    dropped = int(mask.sum())
    if dropped:
        logger.info("dropped %d observation rows: %s", dropped, reason)
    return cleaned[~mask]


def clean_observations(
    df: pd.DataFrame,
    valid_iso3: set[str],
    year_window: tuple[int, int] = (2000, 2024),
) -> pd.DataFrame:
    """Apply all cleaning rules and return a clean DataFrame ready for loading."""
    if df.empty:
        return df.copy()

    cleaned = df.copy()

    # 1. Standardize identifiers
    cleaned["country_iso3"] = cleaned["country_iso3"].astype(str).str.strip().str.upper()
    cleaned["indicator_code"] = cleaned["indicator_code"].astype(str).str.strip()

    # 2. Keep only real countries
    cleaned = _drop(
        cleaned,
        ~cleaned["country_iso3"].isin(valid_iso3),
        "country not in country table",
    )

    # 3. Type conversion
    cleaned["year"] = pd.to_numeric(cleaned["year"], errors="coerce")
    cleaned["value"] = pd.to_numeric(cleaned["value"], errors="coerce")

    # 4. Drop missing year or value
    cleaned = _drop(
        cleaned,
        cleaned["year"].isna() | cleaned["value"].isna(),
        "missing or non-numeric year/value",
    )

    # 5. Drop fractional years
    cleaned = _drop(
        cleaned,
        cleaned["year"] % 1 != 0,
        "year is not a whole number",
    )
    cleaned["year"] = cleaned["year"].astype(int)

    # 6. Year window
    y0, y1 = year_window
    cleaned = _drop(
        cleaned,
        ~cleaned["year"].between(y0, y1),
        f"year outside {y0}-{y1}",
    )

    # 7. Harmonize sex
    cleaned["sex"] = cleaned["sex"].fillna("BTSX").replace(_SEX_MAP)
    cleaned = _drop(
        cleaned,
        ~cleaned["sex"].isin(_VALID_SEX),
        "unknown sex code",
    )

    # 8. Range checks
    def out_of_bounds(row) -> bool:
        bounds = _INDICATOR_BOUNDS.get(row["indicator_code"])
        if bounds is None:
            return False
        v = row["value"]
        if bounds.low_inclusive:
            return v < bounds.low or v > bounds.high
        return v <= bounds.low or v > bounds.high

    cleaned = _drop(
        cleaned,
        cleaned.apply(out_of_bounds, axis=1),
        "value outside plausible bounds",
    )

    # 9. Deduplication
    cleaned = _drop(
        cleaned,
        cleaned.duplicated(subset=_KEY_COLUMNS, keep="last"),
        "duplicate (country, indicator, year, sex); kept the last",
    )

    return cleaned.reset_index(drop=True)
