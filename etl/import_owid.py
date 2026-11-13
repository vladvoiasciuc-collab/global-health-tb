"""Import selected OWID charts."""
import logging
from pathlib import Path

from app.database import SessionLocal
from etl.transform_owid import transform_owid_file
from etl.clean import clean_observations
from etl.load import (
    get_or_create_source,
    get_or_create_indicator,
    upsert_observations,
    log_import,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SOURCE_NAME = "Our World in Data"
RAW_DIR = Path("data/raw/owid")

# Add OWID chart slugs relevant to TB / health if available
INDICATORS = [
    # ("life-expectancy", "Life expectancy", "years", "life-expectancy.csv"),
]


def main() -> None:
    session = SessionLocal()
    try:
        from app.models import Country
        valid_iso3 = {c.iso3 for c in session.query(Country.iso3).all()}
        if not valid_iso3:
            raise SystemExit("Country table is empty. Run python -m etl.import_worldbank first.")

        source_id = get_or_create_source(session, SOURCE_NAME, "https://ourworldindata.org")

        for code, name, unit, filename in INDICATORS:
            path = RAW_DIR / filename
            if not path.exists():
                print(f"{code:<22} SKIP (missing {path.name})")
                continue
            try:
                raw = transform_owid_file(path, code)
                cleaned = clean_observations(raw, valid_iso3)
                indicator_id = get_or_create_indicator(session, code, name, unit, source_id)
                loaded = upsert_observations(session, cleaned, indicator_id)
                log_import(session, SOURCE_NAME, code, str(path), loaded)
                session.commit()
                print(f"{code:<22} raw={len(raw):>6}  clean={len(cleaned):>6}  loaded={loaded:>6}")
            except Exception as exc:
                session.rollback()
                logger.exception("%s: import failed", code)
    finally:
        session.close()


if __name__ == "__main__":
    main()
