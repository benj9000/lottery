from enum import IntEnum
from typing import ClassVar

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
    def winning_class(self) -> Super6WinningClass | None:
        """The winning class, if any."""
        return Super6WinningClass.from_consecutive_matches(self.matched_digits)

    @property
    def is_winner(self) -> bool:
        """Check if this is a winning combination."""
        return self.winning_class is not None


class Super6WinningClass(IntEnum):
    """Winning classes for SUPER 6."""

    CLASS_1 = 1  # 6 correct digits.
    CLASS_2 = 2  # 5 correct digits.
    CLASS_3 = 3  # 4 correct digits.
    CLASS_4 = 4  # 3 correct digits.
    CLASS_5 = 5  # 2 correct digits.
    CLASS_6 = 6  # 1 correct digit.

    @classmethod
    def from_consecutive_matches(cls, matches_count: int) -> Super6WinningClass | None:
        """Create a winning class from the number of consecutively matching digits."""
        if matches_count < 0 or matches_count > 6:
            raise ValueError("Invalid number of matching digits.")
        if matches_count == 0:
            return None
        return cls(7 - matches_count)
