from datetime import date
from pathlib import Path

from lottery.application.evaluate_ticket_use_case import (
    EvaluateTicketInteractor,
    EvaluateTicketPresenter,
    EvaluateTicketRequest,
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
from lottery.infrastructure.repositories.noop_evaluation_report_repository import (
    NoopEvaluationReportRepository,
)
from lottery.presentation.cli.cli_config import REPORTS_SUBDIR_NAME, TICKET_CONFIG_FILENAME
from lottery.presentation.cli.presenters.evaluate_ticket_presenter import CLIEvaluateTicketPresenter


def evaluate_ticket(
    data_dir: Path,
    draw_date: date,
    create_report: bool,
    report_format: ReportFormat,
) -> None:
    """Command to evaluate the ticket from the configuration against the draw on the given date."""
    config: TicketConfigProtocol = load_ticket_config(data_dir / TICKET_CONFIG_FILENAME)
    ticket_repo: TicketRepository = ConfigurationTicketRepository(config)

    draw_repo: DrawRepository = LottoDeApiDrawRepository()

    report_repo: EvaluationReportRepository
    if create_report:
        reports_dir: Path = data_dir / REPORTS_SUBDIR_NAME
        report_repo = FilesystemEvaluationReportRepository(reports_dir, report_format)
    else:
        report_repo = NoopEvaluationReportRepository()

    presenter: EvaluateTicketPresenter = CLIEvaluateTicketPresenter()

    use_case: EvaluateTicketInteractor = EvaluateTicketInteractor(
        ticket_repo, draw_repo, report_repo, presenter
    )
    request: EvaluateTicketRequest = EvaluateTicketRequest(draw_date)
    use_case.execute(request)
