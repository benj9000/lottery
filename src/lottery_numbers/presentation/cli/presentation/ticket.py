from dataclasses import dataclass
from typing import Self, override

from lottery_numbers.application.dtos import TicketDTO
from lottery_numbers.presentation.cli.format_utils import format_date


@dataclass(frozen=True)
class TicketPresentation:
    ticket_number: str
    draw_date: str
    lotto_6aus49_picks: list[list[int]]
    play_spiel77: bool
    play_super6: bool

    @classmethod
    def from_dto(cls, dto: TicketDTO) -> Self:
        return cls(
            ticket_number=dto.ticket_number,
            draw_date=format_date(dto.draw_date),
            lotto_6aus49_picks=[sorted(pick) for pick in dto.lotto_6aus49_picks],
            play_spiel77=dto.play_spiel77,
            play_super6=dto.play_super6,
        )

    @override
    def __str__(self) -> str:
        width: int = 79
        lines: list[str] = [
            "═" * width,
            f"                      🎫 LOTTERY TICKET #{self.ticket_number}",
            f"                         {self.draw_date}",
            "═" * width,
            "",
            "LOTTO 6aus49 Picks:",
        ]

        # Add all picks.
        for idx, pick in enumerate(self.lotto_6aus49_picks, start=1):
            lines.append(f"  Pick {idx}:  {pick}")

        # Add additional games, if any.
        additional_games: list[str] = []
        if self.play_spiel77:
            additional_games.append("Spiel 77")
        if self.play_super6:
            additional_games.append("SUPER 6")
        if additional_games:
            lines.append("")
            lines.append(f"Additional Games:  {', '.join(additional_games)}")

        return "\n".join(lines)
