"""Extractors for WHO GHO OData API.

Only downloads raw data and saves it. Transformation is separate.
"""
from pathlib import Path
from typing import Any
import requests
import json

_DEFAULT_RAW_DIR = Path("data/raw/who")
HTTP_TIMEOUT_S = 120


class WhoApiError(Exception):
    """Raised when the WHO GHO response shape is unexpected."""


def _download_rows(code: str, filter_expr: str) -> tuple[list[dict[str, Any]], str]:
    base = f"https://ghoapi.azureedge.net/api/{code}"
    params = {"$filter": filter_expr}
    rows: list[dict[str, Any]] = []
    next_url: str | None = base

    while next_url:
        response = requests.get(next_url, params=params, timeout=HTTP_TIMEOUT_S)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise WhoApiError(f"{next_url}: expected a JSON object, got {payload!r}")
        value = payload.get("value", [])
        if not isinstance(value, list):
            raise WhoApiError(f"{next_url}: 'value' is not a list: {value!r}")
        rows.extend(value)
        next_link = payload.get("@odata.nextLink")
        next_url = next_link if isinstance(next_link, str) else None
        params = None  # nextLink already contains the filter

    return rows, base


def _save_raw(output_dir: Path, filename: str, rows: list[dict[str, Any]]) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / filename
    path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    return path


def download_who_indicator(
    code: str,
    year_from: int = 2000,
    *,
    output_dir: Path | None = None,
) -> tuple[Path, str]:
    """Download one WHO indicator (all countries, from year_from) and save the raw JSON."""
    rows, url = _download_rows(
        code, f"SpatialDimType eq 'COUNTRY' and TimeDim ge {year_from}"
    )
    path = _save_raw(
        output_dir or _DEFAULT_RAW_DIR, f"{code}_from{year_from}.json", rows
    )
    return path, url
