"""Data cleaning for normalized observations before they reach the database.

Implements the techniques from Lab 1 section 1.5 and Lab 2 section 2.3.
Includes IQR outlier flagging (Task 2.2).
"""
from dataclasses import dataclass
import logging
import pandas as pd

logger = logging.getLogger(__name__)

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


_INDICATOR_BOUNDS: dict[str, _Bounds] = {
    "SH.XPD.CHEX.GD.ZS": _Bounds(0, 30),
    "NY.GDP.PCAP.CD": _Bounds(0, 500_000, low_inclusive=False),
    "SH.DYN.AIDS.ZS": _Bounds(0, 40),
    "SH.TBS.CURE.ZS": _Bounds(0, 100),
    "MDG_0000000020": _Bounds(0, 1000),
}


def _drop(cleaned: pd.DataFrame, mask: pd.Series, reason: str) -> pd.DataFrame:
    dropped = int(mask.sum())
    if dropped:
        logger.info("dropped %d observation rows: %s", dropped, reason)
    return cleaned[~mask]


def clean_observations(
    df: pd.DataFrame,
    valid_iso3: set[str],
    year_window: tuple[int, int] = (2000, 2024),
) -> pd.DataFrame:
    if df.empty:
        return df.copy()

    cleaned = df.copy()

    cleaned["country_iso3"] = cleaned["country_iso3"].astype(str).str.strip().str.upper()
    cleaned["indicator_code"] = cleaned["indicator_code"].astype(str).str.strip()

    cleaned = _drop(
        cleaned,
        ~cleaned["country_iso3"].isin(valid_iso3),
        "country not in country table",
    )

    cleaned["year"] = pd.to_numeric(cleaned["year"], errors="coerce")
    cleaned["value"] = pd.to_numeric(cleaned["value"], errors="coerce")

    cleaned = _drop(
        cleaned,
        cleaned["year"].isna() | cleaned["value"].isna(),
        "missing or non-numeric year/value",
    )

    cleaned = _drop(
        cleaned,
        cleaned["year"] % 1 != 0,
        "year is not a whole number",
    )
    cleaned["year"] = cleaned["year"].astype(int)

    y0, y1 = year_window
    cleaned = _drop(
        cleaned,
        ~cleaned["year"].between(y0, y1),
        f"year outside {y0}-{y1}",
    )

    cleaned["sex"] = cleaned["sex"].fillna("BTSX").replace(_SEX_MAP)
    cleaned = _drop(
        cleaned,
        ~cleaned["sex"].isin(_VALID_SEX),
        "unknown sex code",
    )

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

    cleaned = _drop(
        cleaned,
        cleaned.duplicated(subset=_KEY_COLUMNS, keep="last"),
        "duplicate (country, indicator, year, sex); kept the last",
    )

    # Task 2.2: IQR outlier flag (does not drop rows)
    cleaned["is_outlier"] = False
    for code in cleaned["indicator_code"].unique():
        mask = cleaned["indicator_code"] == code
        vals = cleaned.loc[mask, "value"]
        if len(vals) < 4:
            continue
        q1 = vals.quantile(0.25)
        q3 = vals.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        outlier_mask = mask & ((cleaned["value"] < lower) | (cleaned["value"] > upper))
        cleaned.loc[outlier_mask, "is_outlier"] = True

    return cleaned.reset_index(drop=True)
