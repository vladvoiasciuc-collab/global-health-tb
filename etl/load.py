"""Load cleaned observations into PostgreSQL with idempotent upsert.

Also handles country list and import logging.
"""
from datetime import datetime
from sqlalchemy import insert, func
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models import Observation, Country, Indicator, Source, ImportLog
from app.database import SessionLocal


def get_or_create_source(session: Session, name: str, url: str | None = None) -> int:
    source = session.query(Source).filter_by(name=name).one_or_none()
    if source is None:
        source = Source(name=name, url=url)
        session.add(source)
        session.flush()
    return source.source_id


def get_or_create_indicator(
    session: Session,
    code: str,
    name: str,
    unit: str | None,
    source_id: int,
) -> int:
    ind = session.query(Indicator).filter_by(code=code).one_or_none()
    if ind is None:
        ind = Indicator(code=code, name=name, unit=unit, source_id=source_id)
        session.add(ind)
        session.flush()
    return ind.indicator_id


def upsert_countries(session: Session, countries: list[dict]) -> int:
    if not countries:
        return 0
    stmt = pg_insert(Country).values(countries)
    stmt = stmt.on_conflict_do_update(
        index_elements=["iso3"],
        set_={
            "iso2": stmt.excluded.iso2,
            "name": stmt.excluded.name,
            "region": stmt.excluded.region,
            "income_group": stmt.excluded.income_group,
        },
    )
    result = session.execute(stmt)
    return result.rowcount or 0


def upsert_observations(
    session: Session,
    df,
    indicator_id: int,
    chunk_size: int = 1000,
) -> int:
    """Idempotent upsert on the natural key (country, indicator, year, sex)."""
    if df.empty:
        return 0

    rows = []
    for _, row in df.iterrows():
        rows.append(
            {
                "country_iso3": row["country_iso3"],
                "indicator_id": indicator_id,
                "year": int(row["year"]),
                "sex": row["sex"],
                "value": row["value"],
                "is_outlier": bool(row.get("is_outlier", False)),
            }
        )

    loaded = 0
    for start in range(0, len(rows), chunk_size):
        chunk = rows[start : start + chunk_size]
        stmt = pg_insert(Observation).values(chunk)
        stmt = stmt.on_conflict_do_update(
            constraint="uq_observation",
            set_={
                "value": stmt.excluded.value,
                "is_outlier": stmt.excluded.is_outlier,
                "imported_at": func.now(),
            },
        )
        result = session.execute(stmt)
        loaded += result.rowcount or 0
    return loaded


def log_import(
    session: Session,
    source_name: str,
    indicator_code: str,
    url: str,
    rows_loaded: int,
) -> None:
    session.add(
        ImportLog(
            source_name=source_name,
            indicator_code=indicator_code,
            url=url,
            rows_loaded=rows_loaded,
        )
    )
