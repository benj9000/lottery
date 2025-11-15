import calendar
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo


def raise_for_date_without_lottery_draw(date: date) -> None:
    """Raise a `ValueError`, if there is no lottery draw on the date."""
    if date.weekday() not in [calendar.WEDNESDAY, calendar.SATURDAY]:
        raise ValueError(
            f"No lottery draw on {date} because it is a {calendar.day_name[date.weekday()]}."
        )


def ensure_berlin_tz(dt: datetime) -> datetime:
    """Convert datetime to Berlin timezone."""
    if dt.tzinfo is None:
        # If naive, assume it is UTC.
        dt = dt.replace(tzinfo=timezone.utc)

    tzinfo_berlin: ZoneInfo = ZoneInfo("Europe/Berlin")
    return dt.astimezone(tzinfo_berlin)
