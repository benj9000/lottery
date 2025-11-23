from typing import override

import click

from lottery_numbers.application.evaluate_ticket_use_case import (
    EvaluateTicketPresenter,
    EvaluateTicketResponse,
)
from lottery_numbers.presentation.cli.formatters.draw import DrawFormatter
from lottery_numbers.presentation.cli.formatters.evaluation import TicketEvaluationFormatter
from lottery_numbers.presentation.cli.formatters.ticket import TicketFormatter


class CLIEvaluateTicketPresenter(EvaluateTicketPresenter):
    @override
    def present(self, response: EvaluateTicketResponse) -> None:
        """Present a ticket, a draw and their evaluation on the command-line."""
        draw: DrawFormatter = DrawFormatter.from_dto(response.draw)
        ticket: TicketFormatter = TicketFormatter.from_dto(response.ticket)
        ticket_evaluation: TicketEvaluationFormatter = TicketEvaluationFormatter.from_dto(
            response.ticket_evaluation
        )

        print(ticket)
        print()
        print(draw)
        print()
        print(ticket_evaluation)
