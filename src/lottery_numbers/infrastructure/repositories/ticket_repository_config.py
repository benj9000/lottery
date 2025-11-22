from datetime import date

from lottery_numbers.configuration import TicketConfigProtocol
from lottery_numbers.domain.ticket import Lotto6aus49Pick, Ticket, TicketNumber


class TicketRepositoryConfig:
    """Repository that manages lottery ticket data using a configuration file."""

    def __init__(self, config: TicketConfigProtocol):
        self._config: TicketConfigProtocol = config
        self._mapper: TicketMapper = TicketMapper()

    def get_for_date(self, draw_date: date) -> Ticket:
        return self._mapper.to_ticket(self._config, draw_date)


class TicketMapper:
    @staticmethod
    def to_ticket(config: TicketConfigProtocol, draw_date: date) -> Ticket:
        """
        Mapper for converting the numbers and game settings defined per configuration to `Ticket`
        entities.

        Numbers and game settings in a configuration are usually not volatile but long-lasting and
        played against every lottery draw. Therefore, the configuration does not provide a draw
        date, and the date passed is adopted.
        """
        ticket_number: TicketNumber = TicketNumber(number=config.ticket_number)
        picks: list[Lotto6aus49Pick] = [
            Lotto6aus49Pick(numbers=frozenset(pick)) for pick in config.picks
        ]
        return Ticket(
            ticket_number=ticket_number,
            lotto_6aus49_picks=picks,
            draw_date=draw_date,
            play_spiel77=config.play_spiel77,
            play_super6=config.play_super6,
        )
