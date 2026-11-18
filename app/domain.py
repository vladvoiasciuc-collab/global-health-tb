from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class Sex(str, Enum):
    MLE = "MLE"
    FML = "FML"
    BTSX = "BTSX"  # both sexes


@dataclass(frozen=True)
class ObservationCriteria:
    """Filters for observations. None means 'do not filter on this'."""
    country_iso3: str | None = None
    indicator_code: str | None = None
    region: str | None = None
    year_from: int | None = None
    year_to: int | None = None
    sex: Sex | None = None


@dataclass(frozen=True)
class ObservationListItem:
    """One row ready to be shown in the table."""
    country_name: str
    country_iso3: str
    region: str | None
    indicator_code: str
    indicator_name: str
    unit: str | None
    year: int
    sex: str
    value: Decimal | None


@dataclass(frozen=True)
class Option:
    value: str
    label: str


@dataclass(frozen=True)
class FilterOptions:
    countries: list[Option]
    indicators: list[Option]
    regions: list[Option]
    sexes: list[Option]
