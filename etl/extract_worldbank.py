"""Extractors for World Bank Indicators API.

Downloads countries list and indicator series. Saves raw JSON.
"""
from pathlib import Path
from typing import Any
import time
import requests
import json

_DEFAULT_RAW_DIR = Path("data/raw/worldbank")
HTTP_TIMEOUT_S = 300  # increased


class WorldBankApiError(Exception):
    """Raised when the World Bank response shape is unexpected."""


def _get_all_pages(url: str, max_retries: int = 3) -> tuple[list[dict[str, Any]], str]:
    records: list[dict[str, Any]] = []
    page = 1
    while True:
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    url,
                    params={"page": page, "per_page": 500},  # smaller page size
                    timeout=HTTP_TIMEOUT_S,
                )
                response.raise_for_status()
                break
            except requests.exceptions.ReadTimeout:
                if attempt == max_retries - 1:
                    raise
                time.sleep(5 * (attempt + 1))
        else:
            raise WorldBankApiError(f"{url}: failed after retries")

        body = response.json()
        if not (isinstance(body, list) and len(body) == 2):
            raise WorldBankApiError(f"{url}: unexpected response {body!r}")
        meta, data = body
        if not isinstance(meta, dict) or "pages" not in meta:
            raise WorldBankApiError(f"{url}: missing page metadata in {meta!r}")
        records.extend(data or [])
        if page >= int(meta["pages"]):
            return records, url
        page += 1


def _save_raw(output_dir: Path, filename: str, rows: list[dict[str, Any]]) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / filename
    path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    return path


def download_worldbank_countries(output_dir: Path | None = None) -> tuple[Path, str]:
    """Download the list of World Bank countries (excludes aggregates later in transform)."""
    url = "https://api.worldbank.org/v2/country?format=json"
    records, _ = _get_all_pages(url)
    path = _save_raw(output_dir or _DEFAULT_RAW_DIR, "countries.json", records)
    return path, url


def download_worldbank_indicator(
    code: str,
    year_from: int = 2000,
    *,
    output_dir: Path | None = None,
) -> tuple[Path, str]:
    """Download one World Bank indicator for all countries from year_from."""
    url = f"https://api.worldbank.org/v2/country/all/indicator/{code}?format=json&date={year_from}:2024"
    records, used_url = _get_all_pages(url)
    path = _save_raw(
        output_dir or _DEFAULT_RAW_DIR, f"{code}_from{year_from}.json", records
    )
    return path, used_url
