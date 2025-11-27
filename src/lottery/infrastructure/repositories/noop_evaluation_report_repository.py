from typing import override

from lottery.application.repositories import EvaluationReportRepository
from lottery.domain.draw import Draw
from lottery.domain.ticket import Ticket
from lottery.domain.ticket_evaluation import TicketEvaluation


class NoopEvaluationReportRepository(EvaluationReportRepository):
    """A no operation evaluation report repository."""

    @override
    def add_report(self, ticket: Ticket, draw: Draw, evaluation: TicketEvaluation) -> None:
        pass
