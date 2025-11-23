from datetime import date
from pathlib import Path

from lottery_numbers.application.evaluate_ticket_use_case import (
    EvaluateTicketInteractor,
    EvaluateTicketPresenter,
    EvaluateTicketRequest,
)
from lottery_numbers.application.repositories import (
    DrawRepository,
    EvaluationReportRepository,
    TicketRepository,
)
from lottery_numbers.configuration import ConfigProtocol, load_config_from_default_location
from lottery_numbers.infrastructure.repositories.configuration_ticket_repository import (
    ConfigurationTicketRepository,
)
from lottery_numbers.infrastructure.repositories.draw_repository_mock import DrawRepositoryMock
from lottery_numbers.infrastructure.repositories.filesystem_evaluation_report_repository import (
    FilesystemEvaluationReportRepository,
    ReportFormat,
)
from lottery_numbers.presentation.cli.evaluate_ticket_presenter import (
    CLIEvaluateTicketPresenter,
)


def evaluate_ticket(draw_date: date) -> None:
    """Command to evaluate the ticket from the configuration against the draw on the given date."""
    config: ConfigProtocol = load_config_from_default_location()

    ticket_repo: TicketRepository = ConfigurationTicketRepository(config)

    draw_repo: DrawRepository = DrawRepositoryMock()  # TODO replace mock
    # draw_repo: DrawRepository = LottoDeApiDrawRepository()

    report_directory_path: Path = config.report_directory
    report_format: ReportFormat = ReportFormat(config.report_format)
    report_repo: EvaluationReportRepository = FilesystemEvaluationReportRepository(
        report_directory_path, report_format
    )

    presenter: EvaluateTicketPresenter = CLIEvaluateTicketPresenter()

    use_case: EvaluateTicketInteractor = EvaluateTicketInteractor(
        ticket_repo, draw_repo, report_repo, presenter
    )
    request: EvaluateTicketRequest = EvaluateTicketRequest(draw_date)

    use_case.execute(request)
