from pathlib import Path
from typing import Literal

ticket_number: str = "1234567"
picks: list[tuple[int, int, int, int, int, int]] = [
    (1, 2, 3, 4, 5, 6),
    (11, 12, 13, 14, 15, 16),
    (21, 22, 23, 24, 25, 26),
]
play_spiel77: bool = True
play_super6: bool = True

report_directory: Path = Path(__file__).parent / "data" / "reports"
report_format: Literal["json", "yaml"] = "json"
