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

    game77_number: str = Field(
        pattern=r"^\d{7}$", description="The winning 7-digit number for Game 77."
    )
    super6_number: str = Field(
        pattern=r"^\d{6}$", description="The winning 6-digit number for Super 6."
    )

    @override
    def __str__(self) -> str:
        sorted_numbers: list[int] = sorted(self.lotto_6aus49_winning_numbers)
        numbers_formatted: str = "".join(f"[ {num:2d} ]" for num in sorted_numbers)

        date_str: str = self.draw_date.strftime("%A, %Y-%m-%d")

        width: int = 79
        lines: list[str] = [
            "═" * width,
            "                      🎱 LOTTERY DRAW",
            f"                         {date_str}",
            "═" * width,
            "",
            "LOTTO 6aus49",
            f"  Winning Numbers:  {numbers_formatted}",
            f"  Super Number:     [ {self.super_number} ]",
            "",
            f"Spiel 77:   {'-'.join(self.game77_number)}",
            f"SUPER 6:    {'-'.join(self.super6_number)}",
        ]

        return "\n".join(lines)
