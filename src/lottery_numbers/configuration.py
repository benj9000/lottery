from importlib.machinery import ModuleSpec
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType
from typing import Literal, Protocol, cast, get_type_hints


class TicketConfigProtocol(Protocol):
    """A subconfiguration that defines the numbers and games that are played."""

    ticket_number: str
    picks: list[tuple[int, int, int, int, int, int]]
    play_spiel77: bool
    play_super6: bool


class ReportConfigProtocol(Protocol):
    """A subconfiguration that defines how and where to store reports."""

    report_directory: Path
    report_format: Literal["json", "yaml"]


class ConfigProtocol(TicketConfigProtocol, ReportConfigProtocol, Protocol):
    """A full application configuration."""

    ...


def load_config(config_file_path: Path) -> ConfigProtocol:
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
