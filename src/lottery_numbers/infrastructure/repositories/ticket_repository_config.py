from datetime import date
from importlib.machinery import ModuleSpec
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType
from typing import Protocol, cast, get_type_hints

from lottery_numbers.domain.ticket import Lotto6aus49Pick, Ticket, TicketNumber


class TicketRepositoryConfig:
    """Repository that manages lottery ticket data using a configuration file."""

    def __init__(self, config_file_path: Path):
        self._config: ConfigProtocol = self._load_config(config_file_path)
        self._mapper: TicketMapper = TicketMapper()

    def get_for_date(self, draw_date: date) -> Ticket:
        return self._mapper.to_ticket(self._config, draw_date)

    @staticmethod
    def _load_config(config_file_path: Path) -> ConfigProtocol:
        """Load the configuration from the file at the given path."""

        if not config_file_path.exists() or not config_file_path.is_file():
            raise FileNotFoundError(f"Configuration file not found at {config_file_path}.")

        spec: ModuleSpec | None = spec_from_file_location("config", config_file_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Failed to load module spec from {config_file_path}")

        config_module: ModuleType = module_from_spec(spec)
        spec.loader.exec_module(config_module)

        # Validate all required attributes from the protocol.
        required_attrs = get_type_hints(ConfigProtocol).keys()
        missing_attrs = [attr for attr in required_attrs if not hasattr(config_module, attr)]
        if missing_attrs:
            raise AttributeError(
                f"Config module is missing required attributes: {', '.join(missing_attrs)}"
            )

        return cast(ConfigProtocol, cast(object, config_module))


class TicketMapper:
    @staticmethod
    def to_ticket(config: ConfigProtocol, draw_date: date) -> Ticket:
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


class ConfigProtocol(Protocol):
    """A configuration that defines the numbers and games that are played."""

    ticket_number: str
    picks: list[tuple[int, int, int, int, int, int]]
    play_spiel77: bool
    play_super6: bool
