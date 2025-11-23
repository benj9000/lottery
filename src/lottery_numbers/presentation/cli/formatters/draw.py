from dataclasses import dataclass
from typing import Self, override

from lottery_numbers.application.dtos import DrawDTO
from lottery_numbers.presentation.cli.format_utils import format_date


@dataclass(frozen=True)
class DrawFormatter:
    draw_date: str
    lotto_6aus49_winning_numbers: frozenset[int]
    super_number: int
    spiel77_number: str
    super6_number: str

    @classmethod
    def from_dto(cls, dto: DrawDTO) -> Self:
        return cls(
            draw_date=format_date(dto.draw_date),
            lotto_6aus49_winning_numbers=dto.lotto_6aus49_winning_numbers,
            super_number=dto.super_number,
            spiel77_number=dto.spiel77_number,
            super6_number=dto.super6_number,
        )

    @override
    def __str__(self) -> str:
        sorted_numbers: list[int] = sorted(self.lotto_6aus49_winning_numbers)
        numbers_formatted: str = "".join(f"[ {num:2d} ]" for num in sorted_numbers)

        width: int = 79
        lines: list[str] = [
            "═" * width,
            "                      🎱 LOTTERY DRAW",
            f"                         {self.draw_date}",
            "═" * width,
            "",
            "LOTTO 6aus49",
            f"  Winning Numbers:  {numbers_formatted}",
            f"  Super Number:     [ {self.super_number} ]",
            "",
            f"Spiel 77:   {'-'.join(self.spiel77_number)}",
            f"SUPER 6:    {'-'.join(self.super6_number)}",
        ]

        return "\n".join(lines)
