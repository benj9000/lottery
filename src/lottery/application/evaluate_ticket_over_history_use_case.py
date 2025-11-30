from dataclasses import dataclass
from datetime import date
from typing import Protocol

from lottery.application.repositories import (
    DrawRepository,
    EvaluationReportRepository,
    TicketRepository,
)
from lottery.domain.draw import Draw
from lottery.domain.ticket import Ticket
from lottery.domain.ticket_evaluation import TicketEvaluation, TicketEvaluator


class EvaluateTicketOverHistoryInteractor:
    """Evaluate the tickets against the draws since the specified date."""

    def __init__(
        self,
        ticket_repo: TicketRepository,
        draw_repo: DrawRepository,
        report_repo: EvaluationReportRepository,
        presenter: EvaluateTicketOverHistoryPresenter,
    ):
        self._ticket_repo: TicketRepository = ticket_repo
        self._draw_repo: DrawRepository = draw_repo
        self._report_repo: EvaluationReportRepository = report_repo
        self._presenter: EvaluateTicketOverHistoryPresenter = presenter

    def execute(self, since_date: date) -> None:
        draws: list[Draw] = self._draw_repo.get_since_date(since_date)
        ticket_evaluator: TicketEvaluator = TicketEvaluator()
        for draw in draws:
            ticket: Ticket = self._ticket_repo.get_for_date(draw.draw_date)
            evaluation: TicketEvaluation = ticket_evaluator.evaluate(ticket, draw)
            self._report_repo.add_report(ticket, draw, evaluation)

        response: EvaluateTicketOverHistoryResponse = EvaluateTicketOverHistoryResponse(
            len(draws), draws[0].draw_date, draws[-1].draw_date
        )
        self._presenter.present(response)


@dataclass(frozen=True)
class EvaluateTicketOverHistoryResponse:
    draw_count: int
    first_draw_date: date
    last_draw_date: date


class EvaluateTicketOverHistoryPresenter(Protocol):
    def present(self, response: EvaluateTicketOverHistoryResponse) -> None: ...
