"""Import World Bank countries + selected indicators."""
import logging
from pathlib import Path

from app.database import SessionLocal
from etl.extract_worldbank import download_worldbank_countries, download_worldbank_indicator
from etl.transform_worldbank import transform_worldbank_countries, transform_worldbank_file
from etl.clean import clean_observations
from etl.load import (
    get_or_create_source,
    get_or_create_indicator,
    upsert_countries,
    upsert_observations,
    log_import,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SOURCE_NAME = "World Bank"
RAW_DIR = Path("data/raw/worldbank")

# Adapt these to your TB topic
INDICATORS = [
    ("SH.XPD.CHEX.GD.ZS", "Current health expenditure (% of GDP)", "% of GDP", "SH.XPD.CHEX.GD.ZS_from2000.json"),
    ("NY.GDP.PCAP.CD", "GDP per capita (current US$)", "current US$", "NY.GDP.PCAP.CD_from2000.json"),
    ("SH.DYN.AIDS.ZS", "Prevalence of HIV (% of population ages 15-49)", "%", "SH.DYN.AIDS.ZS_from2000.json"),
    ("SH.TBS.CURE.ZS", "Tuberculosis treatment success rate", "% of new cases", "SH.TBS.CURE.ZS_from2000.json"),
]


def main() -> None:
    session = SessionLocal()
    try:
        # 1. Countries first
        countries_path, countries_url = download_worldbank_countries()
        countries_df = transform_worldbank_countries(countries_path)
        n_countries = upsert_countries(session, countries_df.to_dict("records"))
        logger.info("Upserted %d countries", n_countries)
        session.commit()

        valid_iso3 = set(countries_df["iso3"])
        source_id = get_or_create_source(session, SOURCE_NAME, "https://api.worldbank.org")

        # 2. Indicators
        for code, name, unit, filename in INDICATORS:
            path = RAW_DIR / filename
            if not path.exists():
                print(f"{code:<22} SKIP (missing {path.name})")
                continue
            try:
                raw = transform_worldbank_file(path, code)
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
