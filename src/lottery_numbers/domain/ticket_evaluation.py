from typing import ClassVar, override

from pydantic import BaseModel, ConfigDict, Field

from lottery_numbers.domain.draw import Draw
from lottery_numbers.domain.games.lotto_6aus49 import Lotto6aus49Evaluation, Lotto6aus49Evaluator
from lottery_numbers.domain.games.spiel77 import Spiel77Evaluation, Spiel77Evaluator
from lottery_numbers.domain.games.super6 import Super6Evaluation, Super6Evaluator
from lottery_numbers.domain.ticket import Ticket
from lottery_numbers.utils import center_text


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

    @override
    def __str__(self) -> str:
        width: int = 79
        lines: list[str] = [
            "═" * width,
            "                      📊 TICKET EVALUATION",
            "═" * width,
            "",
            "LOTTO 6aus49 Evaluation",
            "─" * width,
        ]

        # Add LOTTO 6aus49 evaluation.
        for idx, eval in enumerate(self.lotto_6aus49_evaluation, start=1):
            eval_str: str = str(eval)
            eval_lines: list[str] = eval_str.split("\n")
            lines.append(f"  Pick {idx}:  {eval_lines[0]}")
            for line in eval_lines[1:]:
                lines.append(f"  {line}")

            if idx < len(self.lotto_6aus49_evaluation):
                lines.append("")

        # Add Spiel 77 evaluation if played.
        if self.spiel77_evaluation:
            lines.append("")
            lines.append("Spiel 77 Evaluation")
            lines.append("─" * width)
            lines.append(f"  {self.spiel77_evaluation}")

        # Add SUPER 6 evaluation if played.
        if self.super6_evaluation:
            lines.append("")
            lines.append("SUPER 6 Evaluation")
            lines.append("─" * width)
            lines.append(f"  {self.super6_evaluation}")

        # Add summary.
        lines.append("")
        lines.append("═" * width)
        if self.has_any_win:
            # Collect names of games with wins.
            winning_games: list[str] = []

            if any(r.is_winner for r in self.lotto_6aus49_evaluation):
                winning_games.append("LOTTO 6aus49")

            if self.spiel77_evaluation and self.spiel77_evaluation.is_winner:
                winning_games.append("Spiel 77")

            if self.super6_evaluation and self.super6_evaluation.is_winner:
                winning_games.append("SUPER 6")

            # Format the list of games.
            games_str: str
            if len(winning_games) == 1:
                games_str = winning_games[0]
            else:
                games_str = f"{', '.join(winning_games[:-1])} and {winning_games[-1]}"

            message: str = f"🎉 CONGRATULATIONS! You won at {games_str}."
            lines.append(center_text(message, width=width))
        else:
            no_win_message: str = "No winning combinations."
            lines.append(center_text(no_win_message, width=width))

        lines.append("═" * width)

        return "\n".join(lines)
