from datetime import date
from pathlib import Path

from lottery.application.evaluate_ticket_over_history_use_case import (
    EvaluateTicketOverHistoryInteractor,
    EvaluateTicketOverHistoryPresenter,
)
from lottery.application.repositories import (
    DrawRepository,
    EvaluationReportRepository,
    TicketRepository,
)
from lottery.configuration import TicketConfigProtocol, load_ticket_config
from lottery.infrastructure.repositories.configuration_ticket_repository import (
    ConfigurationTicketRepository,
)
from lottery.infrastructure.repositories.filesystem_evaluation_report_repository import (
    FilesystemEvaluationReportRepository,
    ReportFormat,
)
from lottery.infrastructure.repositories.lotto_de_api_draw_repository import (
    LottoDeApiDrawRepository,
)
from lottery.presentation.cli.cli_config import REPORTS_SUBDIR_NAME, TICKET_CONFIG_FILENAME
from lottery.presentation.cli.presenters.evaluate_ticket_over_history_presenter import (
    CLIEvaluateTicketOverHistoryPresenter,
)


def create_history(data_dir: Path, since_date: date, format: ReportFormat) -> None:
    """
    Command to create evaluation reports for the ticket from the configuration against the draws
    since the given date.
    """

    reports_dir: Path = data_dir / REPORTS_SUBDIR_NAME
    if any(reports_dir.iterdir()):
        raise ValueError("Reports directory has to be empty to create a history.")

    config: TicketConfigProtocol = load_ticket_config(data_dir / TICKET_CONFIG_FILENAME)
    ticket_repo: TicketRepository = ConfigurationTicketRepository(config)

    draw_repo: DrawRepository = LottoDeApiDrawRepository()

    report_repo: EvaluationReportRepository = FilesystemEvaluationReportRepository(
        reports_dir, format
    )

    presenter: EvaluateTicketOverHistoryPresenter = CLIEvaluateTicketOverHistoryPresenter()

    use_case: EvaluateTicketOverHistoryInteractor = EvaluateTicketOverHistoryInteractor(
        ticket_repo, draw_repo, report_repo, presenter
    )
    use_case.execute(since_date)
