from datetime import date
from typing import Annotated, ClassVar

from pydantic import BaseModel, ConfigDict, Field


class Ticket(BaseModel):
    """A lottery ticket with one or more number picks."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=False)

    ticket_number: TicketNumber
    draw_date: date = Field(description="The date of the draw this ticket is for.")
    lotto_6aus49_picks: list[Lotto6aus49Pick] = Field(
        min_length=1, description="One or more picks for LOTTO 6aus49."
    )
    play_spiel77: bool = Field(description="Whether to participate in Spiel 77.")
    play_super6: bool = Field(description="Whether to participate in SUPER 6.")


class TicketNumber(BaseModel):
    """
    The lottery ticket number used for the super number LOTTO 6aus49, Spiel 77, and SUPER 6.
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    number: str = Field(pattern=r"^\d{7}$", description="7-digit ticket number.")

    @property
    def super_number(self) -> str:
        """Get the last number for the super number."""
        return self.number[-1]

    @property
    def spiel77_number(self) -> str:
        """Get the full 7-digit number for Spiel 77."""
        return self.number

    @property
    def super6_number(self) -> str:
        """Get the last 6 digits for SUPER 6."""
        return self.number[-6:]


class Lotto6aus49Pick(BaseModel):
    """A pick of 6 numbers out of 49 for LOTTO 6aus49."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    numbers: Annotated[
        frozenset[
            Annotated[int, Field(ge=1, le=49, description="A number of a LOTTO 6aus49 pick.")]
        ],
        Field(
            min_length=6, max_length=6, description="The six numbers that make a LOTTO 6aus49 pick."
        ),
    ]
