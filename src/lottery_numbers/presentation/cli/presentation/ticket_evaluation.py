from dataclasses import dataclass
from typing import Self, override

from lottery_numbers.application.dtos import (
    Lotto6aus49EvaluationDTO,
    Spiel77EvaluationDTO,
    Super6EvaluationDTO,
    TicketEvaluationDTO,
)
from lottery_numbers.presentation.cli.format_utils import center_text


@dataclass(frozen=True)
class TicketEvaluationPresentation:
    lotto_6aus49_evaluation: list[Lotto6aus49EvaluationPresentation]
    spiel77_evaluation: Spiel77EvaluationPresentation | None
    super6_evaluation: Super6EvaluationPresentation | None

    @classmethod
    def from_dto(cls, dto: TicketEvaluationDTO) -> Self:
        lotto_6aus49_evaluation: list[Lotto6aus49EvaluationPresentation] = [
            Lotto6aus49EvaluationPresentation.from_dto(evaluation)
            for evaluation in dto.lotto_6aus49_evaluation
        ]
        spiel77_evaluation: Spiel77EvaluationPresentation | None = (
            Spiel77EvaluationPresentation.from_dto(dto.spiel77_evaluation)
            if dto.spiel77_evaluation
            else None
        )
        super6_evaluation: Super6EvaluationPresentation | None = (
            Super6EvaluationPresentation.from_dto(dto.super6_evaluation)
            if dto.super6_evaluation
            else None
        )

        return cls(
            lotto_6aus49_evaluation=lotto_6aus49_evaluation,
            spiel77_evaluation=spiel77_evaluation,
            super6_evaluation=super6_evaluation,
        )

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
        # Collect names of games with wins.
        winning_games: list[str] = []
        if any(r.has_win for r in self.lotto_6aus49_evaluation):
            winning_games.append("LOTTO 6aus49")
        if self.spiel77_evaluation and self.spiel77_evaluation.has_win:
            winning_games.append("Spiel 77")
        if self.super6_evaluation and self.super6_evaluation.has_win:
            winning_games.append("SUPER 6")

        if winning_games:
            # Format the list of games.
            games_str: str
            if len(winning_games) == 1:
                games_str = winning_games[0]
            else:
                games_str = f"{', '.join(winning_games[:-1])} and {winning_games[-1]}"

            message: str = f"🎉 CONGRATULATIONS! You won at {games_str}."
            lines.append(center_text(message, width=width))
        else:
            lines.append(center_text("No winning combinations.", width=width))

        lines.append("═" * width)

        return "\n".join(lines)


@dataclass(frozen=True)
class Lotto6aus49EvaluationPresentation:
    matching_numbers: list[int]
    super_number_matched: bool
    winning_class: int | None

    @property
    def winning_class_description(self) -> str:
        if self.winning_class is None:
            return ""

        descriptions: dict[int, str] = {
            1: "6 numbers + super number",
            2: "6 numbers",
            3: "5 numbers + super number",
            4: "5 numbers",
            5: "4 numbers + super number",
            6: "4 numbers",
            7: "3 numbers + super number",
            8: "3 numbers",
            9: "2 numbers + super number",
        }

        if self.winning_class not in descriptions:
            return "invalid winning class!"

        return descriptions[self.winning_class]

    @property
    def matches_count(self) -> int:
        return len(self.matching_numbers)

    @property
    def has_win(self) -> int:
        return self.winning_class is not None

    @classmethod
    def from_dto(cls, dto: Lotto6aus49EvaluationDTO) -> Self:
        if dto.winning_class is not None and dto.winning_class not in range(1, 10):
            raise ValueError(f"Invalid winning class: {dto.winning_class}.")

        return cls(
            matching_numbers=sorted(dto.matching_numbers),
            super_number_matched=dto.super_number_matched,
            winning_class=dto.winning_class,
        )

    @override
    def __str__(self) -> str:
        lines: list[str] = []

        # Winning class line.
        if self.winning_class is None:
            super_text: str = " + super number" if self.super_number_matched else ""
            plural_s: str = "s" if self.matches_count != 1 else ""
            lines.append(f"No win ({self.matches_count} number{plural_s}{super_text})")
        else:
            lines.append(f"✨ WIN  Class {self.winning_class} ({self.winning_class_description})")

        # Matched numbers line.
        if self.matches_count > 0:
            matches_text: str = (
                "".join(f"[ {num:2d} ]" for num in sorted(self.matching_numbers)) or "–"
            )
            lines.append(f"         Matched: {matches_text}")

        return "\n".join(lines)


@dataclass(frozen=True)
class Spiel77EvaluationPresentation:
    matched_digits: int
    winning_class: int | None

    @property
    def winning_class_description(self) -> str:
        if self.winning_class is None:
            return ""

        descriptions: dict[int, str] = {
            1: "7 correct digits",
            2: "6 correct digits",
            3: "5 correct digits",
            4: "4 correct digits",
            5: "3 correct digits",
            6: "2 correct digits",
            7: "1 correct digit",
        }

        if self.winning_class not in descriptions:
            return "invalid winning class!"

        return descriptions[self.winning_class]

    @property
    def has_win(self) -> int:
        return self.winning_class is not None

    @classmethod
    def from_dto(cls, dto: Spiel77EvaluationDTO) -> Self:
        if dto.winning_class is not None and dto.winning_class not in range(1, 8):
            raise ValueError(f"Invalid winning class: {dto.winning_class}.")

        return cls(
            matched_digits=dto.matched_digits,
            winning_class=dto.winning_class,
        )

    @override
    def __str__(self) -> str:
        if self.winning_class is None:
            return "No win (0 matching digits)"

        return f"✨ WIN  Class {self.winning_class} ({self.winning_class_description})"


@dataclass(frozen=True)
class Super6EvaluationPresentation:
    matched_digits: int
    winning_class: int | None

    @property
    def winning_class_description(self) -> str:
        if self.winning_class is None:
            return ""

        descriptions: dict[int, str] = {
            1: "6 correct digits",
            2: "5 correct digits",
            3: "4 correct digits",
            4: "3 correct digits",
            5: "2 correct digits",
            6: "1 correct digit",
        }

        if self.winning_class not in descriptions:
            return "invalid winning class!"

        return descriptions[self.winning_class]

    @property
    def has_win(self) -> int:
        return self.winning_class is not None

    @classmethod
    def from_dto(cls, dto: Super6EvaluationDTO) -> Self:
        if dto.winning_class is not None and dto.winning_class not in range(1, 7):
            raise ValueError(f"Invalid winning class: {dto.winning_class}.")

        return cls(
            matched_digits=dto.matched_digits,
            winning_class=dto.winning_class,
        )

    @override
    def __str__(self) -> str:
        if self.winning_class is None:
            return "No win (0 matching digits)"

        return f"✨ WIN  Class {self.winning_class} ({self.winning_class_description})"
