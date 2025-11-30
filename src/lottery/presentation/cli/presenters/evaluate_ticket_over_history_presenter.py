from typing import override

from lottery.application.evaluate_ticket_over_history_use_case import (
    EvaluateTicketOverHistoryPresenter,
    EvaluateTicketOverHistoryResponse,
)
from lottery.presentation.cli.format_utils import center_text


class CLIEvaluateTicketOverHistoryPresenter(EvaluateTicketOverHistoryPresenter):
    @override
    def present(self, response: EvaluateTicketOverHistoryResponse) -> None:
        """Present a the evaluation of tickets over history on the command-line."""
        width: int = 79
        lines: list[str] = [
            "═" * width,
            center_text(f"Added {response.draw_count} evaluation reports.", width=width),
            center_text(f"({response.first_draw_date} - {response.last_draw_date})", width=width),
            "═" * width,
        ]
        print("\n".join(lines))
