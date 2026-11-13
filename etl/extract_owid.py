"""Extractor for Our World in Data charts (CSV).

One CSV per chart. No paging.
"""
from pathlib import Path
import io
import requests
import pandas as pd

_DEFAULT_RAW_DIR = Path("data/raw/owid")
HTTP_TIMEOUT_S = 60
_HEADERS = {"User-Agent": "global-health-tb-lab/1.0"}


def _chart_url(slug: str) -> str:
    return f"https://ourworldindata.org/grapher/{slug}.csv"


def _download_csv(slug: str) -> tuple[pd.DataFrame, str]:
    url = _chart_url(slug)
    response = requests.get(url, headers=_HEADERS, timeout=HTTP_TIMEOUT_S)
    response.raise_for_status()
    chart = pd.read_csv(io.StringIO(response.text))
    return chart, url


def download_owid_chart(
    slug: str,
    *,
    output_dir: Path | None = None,
) -> tuple[Path, str]:
    """Download one OWID chart as CSV and save it raw."""
    df, url = _download_csv(slug)
    out = output_dir or _DEFAULT_RAW_DIR
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{slug}.csv"
    df.to_csv(path, index=False)
    return path, url
