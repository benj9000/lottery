from datetime import date

from lottery_numbers.application.repositories.draw_repository import DrawRepository
from lottery_numbers.application.repositories.ticket_repository import TicketRepository
from lottery_numbers.domain.draw import Draw
from lottery_numbers.domain.ticket import Ticket
from lottery_numbers.domain.ticket_evaluation import TicketEvaluation, TicketEvaluator


class EvaluateTicketAgainstDraw:
    """Evaluate the ticket for the specified date against the draw of the specified date."""

    def __init__(
        self,
        ticket_repo: TicketRepository,
        draw_repo: DrawRepository,
        ticket_evaluator: TicketEvaluator,
    ):
        self._ticket_repo: TicketRepository = ticket_repo
        self._draw_repo: DrawRepository = draw_repo
        self._ticket_evaluator: TicketEvaluator = ticket_evaluator

    def execute(self, draw_date: date) -> TicketEvaluation:
        ticket: Ticket = self._ticket_repo.get_for_date(draw_date)
        draw: Draw = self._draw_repo.get_for_date(draw_date)
        evaluation: TicketEvaluation = self._ticket_evaluator.evaluate(ticket, draw)
        return evaluation
