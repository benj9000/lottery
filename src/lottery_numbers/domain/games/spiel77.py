from enum import IntEnum
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field

from lottery_numbers.domain.draw import Draw
from lottery_numbers.domain.ticket import TicketNumber


class Spiel77Evaluator:
    """Evaluator for Spiel 77 lottery tickets."""

    def evaluate(self, ticket_number: TicketNumber, draw: Draw) -> Spiel77Evaluation:
        """Evaluate a Spiel 77 ticket against a draw."""
        matched_digits: int = self._count_matching_digits_from_right(
            ticket_number.spiel77_number, draw.spiel77_number
        )
        return Spiel77Evaluation(matched_digits=matched_digits)

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


class Spiel77Evaluation(BaseModel):
    """An evaluation of a Spiel 77 ticket."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    matched_digits: int = Field(
        ge=0, le=7, description="Number of matching digits from right to left."
    )

    @property
    def winning_class(self) -> Spiel77WinningClass | None:
        """The winning class, if any."""
        return Spiel77WinningClass.from_consecutive_matches(self.matched_digits)

    @property
    def is_winner(self) -> bool:
        """Check if this is a winning combination."""
        return self.winning_class is not None


class Spiel77WinningClass(IntEnum):
    """Winning classes for Spiel 77."""

    CLASS_1 = 1  # 7 correct digits.
    CLASS_2 = 2  # 6 correct digits.
    CLASS_3 = 3  # 5 correct digits.
    CLASS_4 = 4  # 4 correct digits.
    CLASS_5 = 5  # 3 correct digits.
    CLASS_6 = 6  # 2 correct digits.
    CLASS_7 = 7  # 1 correct digit.

    @classmethod
    def from_consecutive_matches(cls, matches_count: int) -> Spiel77WinningClass | None:
        """Create a winning class from the number of consecutively matching digits."""
        if matches_count < 0 or matches_count > 7:
            raise ValueError("Invalid number of matching digits.")
        if matches_count == 0:
            return None
        return cls(8 - matches_count)
