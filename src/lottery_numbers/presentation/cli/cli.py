from datetime import date, datetime
from pathlib import Path

import click

from lottery_numbers.infrastructure.repositories.filesystem_evaluation_report_repository import (
    ReportFormat,
)
from lottery_numbers.presentation.cli.cli_config import DEFAULT_REPORT_FORMAT
from lottery_numbers.presentation.cli.commands.evaluate_ticket import evaluate_ticket
from lottery_numbers.presentation.cli.commands.init_data_directory import init_data_dir

click_data_dir_argument = click.argument(
    "data-dir",
    type=click.Path(dir_okay=True, file_okay=False, writable=True, path_type=Path),
)


@click.group()
@click.version_option()
def cli() -> None:
    """Lottery CLI application."""
    pass


@cli.command()
@click_data_dir_argument
def init(data_dir: Path) -> None:
    """Initialize the data directory at DATA_DIR."""
    init_data_dir(data_dir)


@cli.command()
@click_data_dir_argument
@click.option(
    "-d",
    "--draw-date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    required=False,
    default=lambda: datetime.today(),
    show_default="today",
    help="Date of the draw in format YYYY-MM-DD.",
)
@click.option(
    "-s", "--save-report", is_flag=True, default=False, help="Save a report of the evaluation."
)
@click.option(
    "-f",
    "--format",
    type=click.Choice(ReportFormat, case_sensitive=False),
    default=DEFAULT_REPORT_FORMAT,
    show_default=DEFAULT_REPORT_FORMAT.value,
    help="Format for the report (only has effect with --save-report).",
)
def evaluate(
    data_dir: Path,
    draw_date: datetime,
    save_report: bool,
    format: ReportFormat,
) -> None:
    """Evaluate the configured lottery ticket in DATA_DIR against a draw."""
    draw_date_date: date = draw_date.date()
    evaluate_ticket(data_dir, draw_date_date, save_report, format)


if __name__ == "__main__":
    cli()
