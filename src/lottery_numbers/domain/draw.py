from datetime import date
from typing import Annotated, ClassVar, override

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Draw(BaseModel):
    """A lottery draw."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    @field_validator("lotto_6aus49_winning_numbers", mode="before")
    @classmethod
    def convert_to_frozenset(cls, v: list[int]) -> frozenset[int]:
        return frozenset(v)

    draw_date: date = Field(description="The date of the lottery draw.")
    lotto_6aus49_winning_numbers: Annotated[
        frozenset[
            Annotated[int, Field(ge=1, le=49, description="A winning number for LOTTO 6aus49.")]
        ],
        Field(min_length=6, max_length=6, description="The six winning numbers for LOTTO 6aus49."),
    ]
    super_number: int = Field(ge=0, le=9, description="The winning super number for LOTTO 6aus49.")

    spiel77_number: str = Field(
        pattern=r"^\d{7}$", description="The winning 7-digit number for Spiel 77."
    )
    super6_number: str = Field(
        pattern=r"^\d{6}$", description="The winning 6-digit number for SUPER 6."
    )
