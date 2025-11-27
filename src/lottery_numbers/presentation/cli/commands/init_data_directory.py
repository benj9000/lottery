import os
import shutil
from pathlib import Path

from lottery_numbers.presentation.cli.cli_config import (
    REPORTS_SUBDIR_NAME,
    TICKET_CONFIG_FILENAME,
    TICKET_CONFIG_TEMPLATE,
)


def init_data_dir(target_dir: Path) -> None:
    """
    Initialize the data directory at the specified path.

    Creates
     - a ticket configuration to be filled out, `target_dir/ticket.py`, and
     - a directory for reports, `target_dir/reports/`.
    """
    # Ensure target directory does not exist.
    if target_dir.exists():
        raise FileExistsError(f"Target directory already exists at {target_dir}.")
    # Ensure the directory where to place the target directory does exist.
    if not target_dir.parent.exists():
        raise FileNotFoundError(
            f"Parent directory of the data directory does not exist at {target_dir.parent}."
        )

    # Create the data directory at the specified location.
    target_dir.mkdir()
    # Create a "reports" subdirectory.
    reports_dir = target_dir / REPORTS_SUBDIR_NAME
    reports_dir.mkdir()
    # Copy the ticket template file into the data directory.
    if not TICKET_CONFIG_TEMPLATE.is_file():
        raise FileNotFoundError(f"Ticket template not found at {TICKET_CONFIG_TEMPLATE}")

    ticket_config_target_path: Path = target_dir / TICKET_CONFIG_FILENAME
    ticket_config: Path = Path(shutil.copyfile(TICKET_CONFIG_TEMPLATE, ticket_config_target_path))
    os.chmod(ticket_config, 0o644)

    print("Data directory initialized.")
    print(f"Created data directory: {target_dir}.")
    print(f"Created reports directory: {reports_dir}.")
    print(f"Created ticket configuration template: {ticket_config_target_path}.")
