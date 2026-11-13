"""Helpers for reading raw JSON files saved by the extractors."""
from pathlib import Path
from typing import Any
import json


def read_json_records(path: Path) -> list[dict[str, Any]]:
    """Load a raw JSON file (list of records) written by an extractor."""
    text = path.read_text(encoding="utf-8")
    data = json.loads(text)
    if not isinstance(data, list):
        raise ValueError(f"{path}: expected a list of records, got {type(data).__name__}")
    return data


def require_keys(record: dict[str, Any], keys: list[str], context: str = "") -> None:
    """Raise a clear error if any required key is missing from a record."""
    missing = [k for k in keys if k not in record]
    if missing:
        raise ValueError(f"{context}: missing keys {missing} in record {record!r}")
