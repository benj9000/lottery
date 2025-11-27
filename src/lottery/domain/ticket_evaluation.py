from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field

from lottery.domain.draw import Draw
from lottery.domain.games.lotto_6aus49 import Lotto6aus49Evaluation, Lotto6aus49Evaluator
from lottery.domain.games.spiel77 import Spiel77Evaluation, Spiel77Evaluator
from lottery.domain.games.super6 import Super6Evaluation, Super6Evaluator
from lottery.domain.ticket import Ticket


class TicketEvaluator:
    """Main orchestrator for evaluating lottery tickets against draws."""

    def __init__(self) -> None:
        """Initialize the ticket evaluator with game-specific evaluators."""
        self._lotto_6aus49_evaluator: Lotto6aus49Evaluator = Lotto6aus49Evaluator()
        self._spiel77_evaluator: Spiel77Evaluator = Spiel77Evaluator()
        self._super6_evaluator: Super6Evaluator = Super6Evaluator()

    def evaluate(self, ticket: Ticket, draw: Draw) -> TicketEvaluation:
        """
        Evaluate a lottery ticket against a draw.

        Raises a `ValueError` if ticket and draw dates do not match.
        """
        if ticket.draw_date != draw.draw_date:
            raise ValueError(
                f"Ticket date {ticket.draw_date} does not match draw date {draw.draw_date}."
            )

        # Evaluate all LOTTO 6aus49 picks.
        lotto_6aus49_evaluations: list[Lotto6aus49Evaluation] = []
        for pick in ticket.lotto_6aus49_picks:
            evaluation: Lotto6aus49Evaluation = self._lotto_6aus49_evaluator.evaluate(
                ticket.ticket_number, pick, draw
            )
            lotto_6aus49_evaluations.append(evaluation)

        # Evaluate Spiel 77 if played.
        spiel77_evaluation: Spiel77Evaluation | None = None
        if ticket.play_spiel77:
            spiel77_evaluation = self._spiel77_evaluator.evaluate(ticket.ticket_number, draw)

        # Evaluate SUPER 6 if played.
        super6_evaluation: Super6Evaluation | None = None
        if ticket.play_super6:
            super6_evaluation = self._super6_evaluator.evaluate(ticket.ticket_number, draw)

        return TicketEvaluation(
            lotto_6aus49_evaluation=lotto_6aus49_evaluations,
            spiel77_evaluation=spiel77_evaluation,
            super6_evaluation=super6_evaluation,
        )


class TicketEvaluation(BaseModel):
    """Full evaluation of a lottery ticket."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    lotto_6aus49_evaluation: list[Lotto6aus49Evaluation] = Field(
        description="LOTTO 6aus49 evaluation for each pick on the ticket."
    )
    spiel77_evaluation: Spiel77Evaluation | None = Field(
        default=None, description="Spiel 77 evaluation if played."
    )
    super6_evaluation: Super6Evaluation | None = Field(
        default=None, description="SUPER 6 evaluation if played."
    )

    @property
    def has_any_win(self) -> bool:
        """Check if there are any wins across all games."""
        lotto_6aus49_win = any(eval.is_winner for eval in self.lotto_6aus49_evaluation)
        spiel77_win = self.spiel77_evaluation.is_winner if self.spiel77_evaluation else False
        super6_win = self.super6_evaluation.is_winner if self.super6_evaluation else False
        return lotto_6aus49_win or spiel77_win or super6_win
