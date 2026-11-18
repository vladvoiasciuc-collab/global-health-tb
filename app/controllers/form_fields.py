from app.domain import Sex


def blank_to_none(value: str | None) -> str | None:
    if value is None or value.strip() == "":
        return None
    return value.strip()


def to_int_or_none(value: str | None) -> int | None:
    if value is None or value.strip() == "":
        return None
    try:
        return int(value)
    except ValueError:
        return None


def to_sex_or_none(value: str | None) -> Sex | None:
    if value is None or value.strip() == "":
        return None
    try:
        return Sex(value.strip())
    except ValueError:
        return None
