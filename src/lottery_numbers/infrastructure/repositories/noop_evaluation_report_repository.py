from typing import override

from lottery_numbers.application.repositories import (
    EvaluationReportRepository,
)
from lottery_numbers.domain.draw import Draw
from lottery_numbers.domain.ticket import Ticket
from lottery_numbers.domain.ticket_evaluation import TicketEvaluation


class NoopEvaluationReportRepository(EvaluationReportRepository):
    """A no operation evaluation report repository."""

    @override
    def add_report(self, ticket: Ticket, draw: Draw, evaluation: TicketEvaluation) -> None:
        pass
