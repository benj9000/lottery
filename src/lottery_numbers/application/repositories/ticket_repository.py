from datetime import date
from typing import Protocol

from lottery_numbers.domain.ticket import Ticket


class TicketRepository(Protocol):
    """Repositories that manage lottery tickets."""

    def get_for_date(self, draw_date: date) -> Ticket:
        """
        Get the lottery ticket for the draw on the specified date.

        Raises a `TicketNotFoundError` when no ticket was found for the requested date.
        """
        ...


class TicketNotFoundError(Exception):
    """To be raised when no lottery ticket can be found for the requested date."""

    def __init__(self, draw_date: date, message: str | None = None):
        self.draw_date: date = draw_date
        self.message: str = message or f"No ticket found for date {draw_date}."
        super().__init__(self.message)
