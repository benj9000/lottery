from datetime import date
from enum import Enum
from pathlib import Path
from typing import Any, TextIO, override

from lottery_numbers.application.repositories import (
    EvaluationReportAlreadyExistsError,
    EvaluationReportRepository,
)
from lottery_numbers.domain.draw import Draw
from lottery_numbers.domain.games.lotto_6aus49 import Lotto6aus49Evaluation
from lottery_numbers.domain.games.spiel77 import Spiel77Evaluation
from lottery_numbers.domain.games.super6 import Super6Evaluation
from lottery_numbers.domain.ticket import Ticket
from lottery_numbers.domain.ticket_evaluation import TicketEvaluation


class ReportFormat(Enum):
    """Supported report output formats."""

    JSON = "json"
    YAML = "yaml"


class FilesystemEvaluationReportRepository(EvaluationReportRepository):
    """Repository that manages evaluation reports stored in different text-based formats."""

    def __init__(self, directory_path: Path, format: ReportFormat):
        """Initialize the repository with a path to the storage directory and a format."""
        if not directory_path.exists():
            raise FileNotFoundError(f"Report directory not found: {directory_path}.")
        self._directory_path: Path = directory_path
        self._report_format: ReportFormat = format
        self._directory_path.mkdir(exist_ok=True)

    @override
    def add_report(self, ticket: Ticket, draw: Draw, evaluation: TicketEvaluation) -> None:
        if ticket.draw_date != draw.draw_date:
            raise ValueError(
                f"Draw dates of ticket ({ticket.draw_date}) and draw ({draw.draw_date}) do not match."
            )

        draw_date: date = ticket.draw_date
        file_path: Path = self._init_file_path(draw_date)
        report_dict: dict[str, Any] = ReportDictFactory().create(  # pyright: ignore[reportExplicitAny]
            draw_date, draw, ticket, evaluation
        )
        self._write_report_dict_to_file(report_dict, file_path)

    def _init_file_path(self, draw_date: date) -> Path:
        """
        Initialize and return the file path for the evaluation report for the specific draw date.

        Raises a `EvaluationReportAlreadyExistsError` when an evaluation report already exists for
        the specified date.
        """
        subdirectory_path: Path = self._get_subdirectory_path(draw_date)
        file_path: Path = self._get_file_path(subdirectory_path, draw_date)
        if file_path.exists():
            message: str = f"Evaluation report already exists for date {draw_date} at {file_path}."
            raise EvaluationReportAlreadyExistsError(draw_date, message)

        if not subdirectory_path.exists():
            subdirectory_path.mkdir()

        return file_path

    def _get_file_path(self, directory_path: Path, draw_date: date) -> Path:
        """Get the file path for a specific draw date."""
        extension = self._report_format.value
        # return self._get_subdirectory_path(draw_date) / f"{draw_date.isoformat()}.{extension}"
        return directory_path / f"{draw_date.isoformat()}.{extension}"

    def _get_subdirectory_path(self, draw_date: date) -> Path:
        """Get the subdirectory path for a specific draw date."""
        return self._directory_path / str(draw_date.year)

    def _write_report_dict_to_file(self, report_dict: dict[str, Any], file_path: Path) -> None:  # pyright: ignore[reportExplicitAny]
        """Write the report dict into the file at the specified path."""
        with open(file_path, "w", encoding="utf-8") as f:
            match self._report_format:
                case ReportFormat.JSON:
                    self._dump_json(report_dict, f)
                case ReportFormat.YAML:
                    self._dump_yaml(report_dict, f)

    def _dump_json(self, report_dict: dict[str, Any], stream: TextIO) -> None:  # pyright: ignore[reportExplicitAny]
        """Dump the report dict as JSON into the file."""
        import json

        json.dump(report_dict, stream, indent=4)

    def _dump_yaml(self, report_dict: dict[str, Any], file: TextIO) -> None:  # pyright: ignore[reportExplicitAny]
        """Dump the report dict as YAML into the file."""
        import yaml

        yaml.safe_dump(report_dict, file, sort_keys=False)


class ReportDictFactory:
    """Produce dictionaries that can serve for serialization purposes."""

    @staticmethod
    def create(
        draw_date: date, draw: Draw, ticket: Ticket, evaluation: TicketEvaluation
    ) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        """Create a report dictionary for serialization purposes based on the provided entities."""
        return {
            "draw_date": draw_date.isoformat(),
            "draw": {
                "winning_numbers": sorted(draw.lotto_6aus49_winning_numbers),
                "super_number": draw.super_number,
                "spiel77_number": draw.spiel77_number,
                "super6_number": draw.super6_number,
            },
            "ticket": {
                "ticket_number": ticket.ticket_number.number,
                "games": {
                    "spiel77": ticket.play_spiel77,
                    "super6": ticket.play_super6,
                },
                "lotto_6aus49_picks": [
                    {
                        "numbers": sorted(pick.numbers),
                        "evaluation": ReportDictFactory._format_lotto_evaluation(
                            evaluation.lotto_6aus49_evaluation[i]
                        ),
                    }
                    for i, pick in enumerate(ticket.lotto_6aus49_picks)
                ],
                "spiel77_evaluation": (
                    ReportDictFactory._format_spiel77_evaluation(evaluation.spiel77_evaluation)
                    if evaluation.spiel77_evaluation
                    else None
                ),
                "super6_evaluation": (
                    ReportDictFactory._format_super6_evaluation(evaluation.super6_evaluation)
                    if evaluation.super6_evaluation
                    else None
                ),
            },
            "summary": ReportDictFactory._format_summary(evaluation),
        }

    @staticmethod
    def _format_summary(evaluation: TicketEvaluation) -> str:
        """Format a summary for a ticket evaluation."""
        summary_parts: list[str] = []

        if evaluation.lotto_6aus49_evaluation and (
            lotto_6aus49_summary := ReportDictFactory._format_lotto_6aus49_summary(
                evaluation.lotto_6aus49_evaluation
            )
        ):
            summary_parts.append(lotto_6aus49_summary)

        if evaluation.spiel77_evaluation and (
            spiel77_summary := ReportDictFactory._format_spiel77_summary(
                evaluation.spiel77_evaluation
            )
        ):
            summary_parts.append(spiel77_summary)

        if evaluation.super6_evaluation and (
            super6_summary := ReportDictFactory._format_super6_summary(evaluation.super6_evaluation)
        ):
            summary_parts.append(super6_summary)

        if summary_parts:
            return "; ".join(summary_parts) + "."

        return "No win."

    @staticmethod
    def _format_lotto_6aus49_summary(evaluations: list[Lotto6aus49Evaluation]) -> str | None:
        """
        Format a summary for a list of LOTTO 6aus49 evaluations if any qualified for a winning
        class.
        """
        winning_data: list[tuple[int, int]] = [
            (evaluation.winning_class, len(evaluation.matching_numbers))
            for evaluation in evaluations
            if evaluation.winning_class
        ]

        if not winning_data:
            return None

        super_matched: bool = evaluations[0].super_number_matched if evaluations else False
        super_suffix: str = " + super" if super_matched else ""
        plural: str = "es" if len(winning_data) > 1 else ""
        winning_picks_str: list[str] = [
            f"{winning_class} ({count} numbers{super_suffix})"
            for winning_class, count in winning_data
        ]

        return f"LOTTO 6aus49: winning class{plural} {', '.join(winning_picks_str)}"

    @staticmethod
    def _format_spiel77_summary(evaluation: Spiel77Evaluation) -> str | None:
        """Format a summary for a Spiel77 evaluation if it qualified for a winning class."""
        if not evaluation.winning_class:
            return None

        return (
            f"Spiel 77: winning class {evaluation.winning_class} "
            f"({evaluation.matched_digits} digits)"
        )

    @staticmethod
    def _format_super6_summary(evaluation: Super6Evaluation) -> str | None:
        """Format a summary for a SUPER 6 evaluation if it qualified for a winning class."""
        if not evaluation.winning_class:
            return None

        return (
            f"SUPER 6: winning class {evaluation.winning_class} "
            "({evaluation.matched_digits} digits)"
        )

    @staticmethod
    def _format_lotto_evaluation(evaluation: Lotto6aus49Evaluation) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        """Format a Lotto 6aus49 evaluation."""
        return {
            "matching_numbers": sorted(evaluation.matching_numbers),
            "super_number_matched": evaluation.super_number_matched,
            "winning_class": evaluation.winning_class,
        }

    @staticmethod
    def _format_spiel77_evaluation(evaluation: Spiel77Evaluation) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        """Format a Spiel77 evaluation."""
        return {
            "matched_digits": evaluation.matched_digits,
            "winning_class": evaluation.winning_class,
        }

    @staticmethod
    def _format_super6_evaluation(evaluation: Super6Evaluation) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        """Format a Super6 evaluation."""
        return {
            "matched_digits": evaluation.matched_digits,
            "winning_class": evaluation.winning_class,
        }
