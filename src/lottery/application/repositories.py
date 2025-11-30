from datetime import date
from typing import Protocol

from lottery.domain.draw import Draw
from lottery.domain.ticket import Ticket
from lottery.domain.ticket_evaluation import TicketEvaluation


class DrawRepository(Protocol):
    """Repositories that manage lottery draws."""

    def get_by_date(self, date: date) -> Draw:
        """
        Get the draw that occurred on the specified date.

        Raises a `DrawNotFoundError` when no draw was found for the requested date.
        """
        ...

    def get_since_date(self, date: date) -> list[Draw]:
        """Get the draws that occurred on or after the specified date."""
        ...


class DrawNotFoundError(Exception):
    """To be raised when no lottery draw can be found for the requested date."""

    def __init__(self, draw_date: date, message: str | None = None):
        self.draw_date: date = draw_date
        self.message: str = message or f"No draw found for date {draw_date}."
        super().__init__(self.message)


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


class EvaluationReportRepository(Protocol):
    """Repositories that manage evaluation reports."""

    def add_report(self, ticket: Ticket, draw: Draw, evaluation: TicketEvaluation) -> None:
        """
        Add an evaluation report based on the specified ticket, draw and evaluation.

        Raises a `EvaluationReportAlreadyExistsError` when an evaluation report already exists for
        the draw date.
        """
        ...


class EvaluationReportAlreadyExistsError(Exception):
    """To be raised when an evaluation report already exists for the requested date."""

    def __init__(self, draw_date: date, message: str | None = None):
        self.draw_date: date = draw_date
        self.message: str = message or f"Evaluation report already exists for date {draw_date}."
        super().__init__(self.message)
