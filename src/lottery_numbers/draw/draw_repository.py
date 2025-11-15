from datetime import date
from typing import Protocol

from lottery_numbers.draw.draw import Draw


class DrawRepository(Protocol):
    """Repositories that manage lottery draws."""

    def get_for_date(self, draw_date: date) -> Draw:
        """
        Get the draw that occurred on the specified date.

        Raises a `DrawNotFoundError` when no draw was found for the requested date.
        """
        ...


class DrawNotFoundError(Exception):
    """To be raised when no lottery draw can be found for the requested date."""

    def __init__(self, draw_date: date, message: str | None = None):
        self.draw_date: date = draw_date
        self.message: str = message or f"No draw found for date {draw_date}."
        super().__init__(self.message)
