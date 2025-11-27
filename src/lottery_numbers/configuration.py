from importlib.machinery import ModuleSpec
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType
from typing import Protocol, cast, get_type_hints


class TicketConfigProtocol(Protocol):
    """A configuration that defines a ticket, i.e., the numbers and games that are played."""

    ticket_number: str
    picks: list[tuple[int, int, int, int, int, int]]
    play_spiel77: bool
    play_super6: bool


def load_ticket_config(config_file: Path) -> TicketConfigProtocol:
    """Load the ticket configuration from the file at the specified path."""

    if not config_file.exists() or not config_file.is_file():
        raise FileNotFoundError(f"Configuration file not found at {config_file}.")

    spec: ModuleSpec | None = spec_from_file_location("config", config_file)
    if spec is None or spec.loader is None:
        raise ImportError(f"Failed to load module spec from {config_file}")

    config_module: ModuleType = module_from_spec(spec)
    spec.loader.exec_module(config_module)

    # Validate all required attributes from the protocol.
    required_attrs = get_type_hints(TicketConfigProtocol).keys()
    missing_attrs = [attr for attr in required_attrs if not hasattr(config_module, attr)]
    if missing_attrs:
        missing_attrs_str = ", ".join(missing_attrs)
        raise AttributeError(
            f"Ticket config module is missing required attributes: {missing_attrs_str}"
        )

    return cast(TicketConfigProtocol, cast(object, config_module))


def load_config_from_default_location() -> TicketConfigProtocol:
    """Load the configuration from the file at the default location."""
    filename: str = "config.py"
    project_root: Path = Path(__file__).parent.parent.parent
    config_file_path: Path = project_root / filename
    return load_ticket_config(config_file_path)
