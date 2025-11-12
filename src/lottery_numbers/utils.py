import calendar
from datetime import date


def raise_for_date_without_lottery_draw(date: date) -> None:
    """Raise a `ValueError`, if there is no lottery draw on the date."""
    if date.weekday() not in [calendar.WEDNESDAY, calendar.SATURDAY]:
        raise ValueError(
            f"No lottery draw on {date} because it is a {calendar.day_name[date.weekday()]}."
        )
