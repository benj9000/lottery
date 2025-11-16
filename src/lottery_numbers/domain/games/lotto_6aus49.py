from enum import IntEnum
from typing import ClassVar, override

from pydantic import BaseModel, ConfigDict, Field

from lottery_numbers.domain.draw import Draw
from lottery_numbers.domain.ticket import Lotto6aus49Pick, TicketNumber


class Lotto6aus49Evaluator:
    """Evaluator for LOTTO 6aus49 picks."""

    def evaluate(
        self, ticket_number: TicketNumber, pick: Lotto6aus49Pick, draw: Draw
    ) -> Lotto6aus49Evaluation:
        picked_numbers: frozenset[int] = pick.numbers
        drawn_numbers: frozenset[int] = draw.lotto_6aus49_winning_numbers
        matching_numbers: frozenset[int] = picked_numbers & drawn_numbers

        super_number_matched: bool = ticket_number.super_number == str(draw.super_number)

        return Lotto6aus49Evaluation(
            matching_numbers=matching_numbers, super_number_matched=super_number_matched
        )


class Lotto6aus49Evaluation(BaseModel):
    """An evaluation of a LOTTO 6aus40 pick."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    matching_numbers: frozenset[int] = Field(
        max_length=6, description="The numbers that matched between the pick and the draw."
    )
    super_number_matched: bool = Field(description="Whether the super number matched.")

    @property
    def winning_class(self) -> Lotto6aus49WinningClass | None:
        """The winning class, if any."""
        return Lotto6aus49WinningClass.from_match_data(
            len(self.matching_numbers), self.super_number_matched
        )

    @property
    def is_winner(self) -> bool:
        """Check if this is a winning combination."""
        return self.winning_class is not None

    @override
    def __str__(self) -> str:
        lines: list[str] = []
        matches_count: int = len(self.matching_numbers)

        # Winning class line.
        if self.winning_class is None:
            super_text: str = " + super number" if self.super_number_matched else ""
            plural_s: str = "s" if matches_count != 1 else ""
            lines.append(f"No win ({matches_count} number{plural_s}{super_text})")
        else:
            lines.append(f"✨ WIN  Class {self.winning_class} ({self.winning_class.description})")

        # Matched numbers line.
        if matches_count > 0:
            matches_text: str = (
                "".join(f"[ {num:2d} ]" for num in sorted(self.matching_numbers)) or "–"
            )
            lines.append(f"         Matched: {matches_text}")

        return "\n".join(lines)


class Lotto6aus49WinningClass(IntEnum):
    """Winning classes for LOTTO 6aus49."""

    CLASS_1 = 1
    CLASS_2 = 2
    CLASS_3 = 3
    CLASS_4 = 4
    CLASS_5 = 5
    CLASS_6 = 6
    CLASS_7 = 7
    CLASS_8 = 8
    CLASS_9 = 9

    @property
    def description(self) -> str:
        descriptions = {
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
        return descriptions[self.value]

    @classmethod
    def from_match_data(
        cls, matches_count: int, super_number_matched: bool
    ) -> Lotto6aus49WinningClass | None:
        """
        Create a winning class from the number of matching numbers and whether the super number is a
        match.
        """
        if matches_count < 0 or matches_count > 6:
            raise ValueError("Invalid number of matching numbers.")

        mapping = {
            (6, True): cls.CLASS_1,
            (6, False): cls.CLASS_2,
            (5, True): cls.CLASS_3,
            (5, False): cls.CLASS_4,
            (4, True): cls.CLASS_5,
            (4, False): cls.CLASS_6,
            (3, True): cls.CLASS_7,
            (3, False): cls.CLASS_8,
            (2, True): cls.CLASS_9,
        }
        return mapping.get((matches_count, super_number_matched)) or None
