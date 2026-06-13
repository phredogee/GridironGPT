from datetime import date, datetime


def parse_signal_date(signal_date: str | None) -> date | None:
    if not signal_date:
        return None

    try:
        return datetime.fromisoformat(signal_date.replace("Z", "+00:00")).date()
    except Exception:
        return None


def days_old(signal_date: str | None) -> int:
    parsed = parse_signal_date(signal_date)

    if parsed is None:
        return 0

    return max(0, (date.today() - parsed).days)


def decay_weight(signal_date: str | None) -> float:
    age = days_old(signal_date)

    if age <= 1:
        return 1.0

    if age <= 7:
        return 0.75

    if age <= 14:
        return 0.50

    if age <= 30:
        return 0.25

    return 0.10


def apply_signal_decay(value: float, signal_date: str | None) -> float:
    return round(value * decay_weight(signal_date), 3)
