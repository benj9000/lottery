from dataclasses import dataclass
from datetime import date
from typing import Protocol

from lottery.application.dtos import DrawDTO, TicketDTO, TicketEvaluationDTO
from lottery.application.repositories import (
    DrawRepository,
    EvaluationReportRepository,
    TicketRepository,
)
from lottery.domain.draw import Draw
from lottery.domain.ticket import Ticket
from lottery.domain.ticket_evaluation import TicketEvaluation, TicketEvaluator


class EvaluateTicketInteractor:
    """Evaluate the ticket for the specified date against the draw of the specified date."""

    def __init__(
        self,
        ticket_repo: TicketRepository,
        draw_repo: DrawRepository,
        report_repo: EvaluationReportRepository,
        presenter: EvaluateTicketPresenter,
    ):
        self._ticket_repo: TicketRepository = ticket_repo
        self._draw_repo: DrawRepository = draw_repo
        self._report_repo: EvaluationReportRepository = report_repo
        self._presenter: EvaluateTicketPresenter = presenter

    def execute(self, request: EvaluateTicketRequest) -> None:
        # Fetch ticket and draw for the specified date.
        ticket: Ticket = self._ticket_repo.get_for_date(request.draw_date)
        draw: Draw = self._draw_repo.get_for_date(request.draw_date)

        # Evaluate ticket against draw.
        ticket_evaluator: TicketEvaluator = TicketEvaluator()
        evaluation: TicketEvaluation = ticket_evaluator.evaluate(ticket, draw)

        # Save a report.
        self._report_repo.add_report(ticket, draw, evaluation)

        response: EvaluateTicketResponse = EvaluateTicketResponseMapper.to_response(
            ticket, draw, evaluation
        )

        self._presenter.present(response)


@dataclass(frozen=True)
class EvaluateTicketRequest:
    draw_date: date


@dataclass(frozen=True)
class EvaluateTicketResponse:
    ticket: TicketDTO
    draw: DrawDTO
    ticket_evaluation: TicketEvaluationDTO


class EvaluateTicketResponseMapper:
    @staticmethod
    def to_response(
        ticket: Ticket, draw: Draw, ticket_evaluation: TicketEvaluation
    ) -> EvaluateTicketResponse:
        return EvaluateTicketResponse(
            ticket=TicketDTO.from_entity(ticket),
            draw=DrawDTO.from_entity(draw),
            ticket_evaluation=TicketEvaluationDTO.from_entity(ticket_evaluation),
        )


class EvaluateTicketPresenter(Protocol):
    def present(self, response: EvaluateTicketResponse) -> None: ...
