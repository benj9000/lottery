from pathlib import Path

from lottery.infrastructure.repositories.filesystem_evaluation_report_repository import ReportFormat

TICKET_CONFIG_TEMPLATE: Path = Path(__file__).parent / "ticket_config_template.py"
"""Path to the ticket configuration template."""

TICKET_CONFIG_FILENAME: str = "ticket.py"
"""Name of the ticket configuration file used when initializing a data directory."""

REPORTS_SUBDIR_NAME: str = "reports"
"""Name of the report subdirectory used when initializing a data directory."""

DEFAULT_REPORT_FORMAT: ReportFormat = ReportFormat.JSON
"""Default report format when none is explicitly requested."""
