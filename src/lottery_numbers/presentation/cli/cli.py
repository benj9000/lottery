from __future__ import annotations

from datetime import date, datetime

import click

from lottery_numbers.presentation.cli.commands import evaluate_ticket


@click.group()
def cli() -> None:
    """Lottery CLI application."""
    pass


@cli.command()
@click.option(
    "-d",
    "--draw-date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    required=False,
    default=lambda: datetime.today(),
    show_default="today",
    help="Date of the draw in format YYYY-MM-DD.",
)
def evaluate(draw_date: datetime) -> None:
    """Evaluate the configured lottery ticket against a draw."""
    draw_date_date: date = draw_date.date()
    evaluate_ticket(draw_date_date)


if __name__ == "__main__":
    cli()
