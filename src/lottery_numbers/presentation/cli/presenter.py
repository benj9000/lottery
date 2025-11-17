from lottery_numbers.application.evaluate_ticket_use_case import EvaluateTicketResponse
from lottery_numbers.presentation.cli.presentation.draw import DrawPresentation
from lottery_numbers.presentation.cli.presentation.ticket import TicketPresentation
from lottery_numbers.presentation.cli.presentation.ticket_evaluation import (
    TicketEvaluationPresentation,
)


class EvaluateTicketCLIPresenter:
    def present(self, response: EvaluateTicketResponse) -> None:
        """Present a ticket evaluation on the command-line."""
        draw: DrawPresentation = DrawPresentation.from_dto(response.draw)
        ticket: TicketPresentation = TicketPresentation.from_dto(response.ticket)
        ticket_evaluation: TicketEvaluationPresentation = TicketEvaluationPresentation.from_dto(
            response.ticket_evaluation
        )

        print(ticket)
        print()
        print(draw)
        print()
        print(ticket_evaluation)
