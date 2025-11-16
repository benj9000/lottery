from enum import IntEnum
from typing import ClassVar, override

from pydantic import BaseModel, ConfigDict, Field

from lottery_numbers.domain.draw import Draw
from lottery_numbers.domain.ticket import TicketNumber


class Super6Evaluator:
    """Evaluator for SUPER 6 lottery tickets."""

    def evaluate(self, ticket_number: TicketNumber, draw: Draw) -> Super6Evaluation:
        """Evaluate a SUPER 6 ticket against a draw."""
        matched_digits: int = self._count_matching_digits_from_right(
            ticket_number.super6_number, draw.super6_number
        )
        return Super6Evaluation(matched_digits=matched_digits)

    @staticmethod
    def _count_matching_digits_from_right(ticket_number: str, winning_number: str) -> int:
        """Count how many digits match from right to left consecutively."""
        count: int = 0
        for t_digit, w_digit in zip(reversed(ticket_number), reversed(winning_number)):
            if t_digit == w_digit:
                count += 1
            else:
                break
        return count


class Super6Evaluation(BaseModel):
    """An evaluation of a SUPER 6 ticket."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    matched_digits: int = Field(
        ge=0, le=6, description="Number of matching digits from right to left."
    )

    @property
    def winning_class(self) -> Super6WinningClass:
        """The winning class."""
        return Super6WinningClass.from_consecutive_matches(self.matched_digits)

    @property
    def is_winner(self) -> bool:
        """Check if this is a winning combination."""
        return self.winning_class is not Super6WinningClass.NO_WIN

    @override
    def __str__(self) -> str:
        if not self.is_winner:
            return "No win (0 matching digits)"

        class_num: str = self.winning_class.name.replace("CLASS_", "")
        return f"✨ WIN  Class {class_num} ({self.winning_class.description})"


class Super6WinningClass(IntEnum):
    """Winning classes for SUPER 6."""

    CLASS_1 = 1
    CLASS_2 = 2
    CLASS_3 = 3
    CLASS_4 = 4
    CLASS_5 = 5
    CLASS_6 = 6
    NO_WIN = 999  # Not an official winning class.

    @property
    def description(self) -> str:
        descriptions = {
            1: "6 correct digits",
            2: "5 correct digits",
            3: "4 correct digits",
            4: "3 correct digits",
            5: "2 correct digits",
            6: "1 correct digit",
            999: "0 correct digits",
        }
        return descriptions[self.value]

    @classmethod
    def from_consecutive_matches(cls, matches_count: int) -> Super6WinningClass:
        """Create a winning class from the number of consecutively matching digits."""
        if matches_count < 0 or matches_count > 6:
            raise ValueError("Invalid number of matching digits.")
        if matches_count == 0:
            return cls.NO_WIN
        return cls(7 - matches_count)
