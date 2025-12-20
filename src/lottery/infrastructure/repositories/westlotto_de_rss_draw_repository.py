from datetime import date
from typing import Any, override
from xml.etree import ElementTree as ET

import requests

from lottery.application.repositories import DrawNotFoundError, DrawRepository
from lottery.domain.draw import Draw


class WestlottoDeRssDrawRepository(DrawRepository):
    """Repository that manages lottery draw data using WestLotto.de's RSS feed."""

    def __init__(
        self, client: WestlottoDeRssClient | None = None, mapper: DrawMapper | None = None
    ):
        self._client: WestlottoDeRssClient = client or WestlottoDeRssClient()
        self._mapper: DrawMapper = mapper or DrawMapper()

    @override
    def get_by_date(self, date: date) -> Draw:
        raw_data: dict[str, Any] = self._client.fetch_latest_draw()  # pyright: ignore[reportExplicitAny]
        draw: Draw = self._mapper.to_draw(raw_data)
        if draw.draw_date != date:
            raise DrawNotFoundError(date)
        return draw

    @override
    def get_since_date(self, date: date) -> list[Draw]:
        # The RSS feed does not provide historic data, so we return an empty list.
        return []


class WestlottoDeRssClient:
    """A HTTP client for the WestLotto.de RSS feed."""

    _BASE_URL: str = "http://www.ergebnisse.westlotto.de/gewinnzahlen/lottozahlen.rss"

    def fetch_latest_draw(self) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        """Fetch the latest draw data from the RSS feed."""
        response: requests.Response = requests.get(self._BASE_URL, timeout=5)
        response.raise_for_status()
        return self._parse_rss(response.text)

    def _parse_rss(self, rss_content: str) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        """Parse the RSS content to extract draw data."""
        root: ET.Element[str] = ET.fromstring(rss_content)
        items: list[ET.Element[str]] = root.findall(".//item")
        draw_data: dict[str, Any] = {}  # pyright: ignore[reportExplicitAny]
        for item in items:
            title_elem: ET.Element[str] | None = item.find("title")
            if title_elem is None:
                continue
            title: str | None = title_elem.text
            if title is None:
                continue
            if title.startswith("vom "):
                # The LOTTO 6 aus 49 item starts with "vom" followed by the date and the draw
                # numbers. For example: "vom 01.01.00: 1, 2, 12, 30, 40, 47 S: 0".

                # The year in the date in the title is ambigouos (00 -> 1900 vs. 2000).
                # The guid item has a value that encodes the date in an unambigouos way, for
                # example: "wlinfo-frss-lotto-2000-01-01".
                guid_elem: ET.Element[str] | None = item.find("guid")
                if guid_elem is not None and guid_elem.text is not None:
                    guid_parts: list[str] = guid_elem.text.split("-")
                    date_str: str = "-".join(guid_parts[-3:])
                    draw_data["date"] = date.fromisoformat(date_str)

                # Process the numbers section ("1, 2, 12, 30, 40, 47 S: 0").
                numbers_section: str = title.split(": ", maxsplit=1)[1]
                numbers_str: str
                super_str: str
                numbers_str, super_str = numbers_section.split("S:", maxsplit=1)
                lotto_nums: list[int] = [int(n.strip()) for n in numbers_str.split(",")]
                super_num: int = int(super_str.strip())

                draw_data["lotto_numbers"] = lotto_nums
                draw_data["super_number"] = super_num
            elif title.startswith("Spiel 77:"):
                # The Spiel 77 item starts with "Spiel 77:" followed by the winning numbers.
                # For example: "Spiel 77: 8295008".
                draw_data["spiel77"] = title.split(":")[1].strip()
            elif title.startswith("SUPER 6:"):
                # The SUPER 6 item starts with "SUPER 6:" followed by the winning numbers.
                # For example: "SUPER 6: 500395".
                draw_data["super6"] = title.split(":")[1].strip()
        return draw_data


class DrawMapper:
    """Mapper for converting RSS response data to `Draw` entities."""

    @staticmethod
    def to_draw(data: dict[str, Any]) -> Draw:  # pyright: ignore[reportExplicitAny]
        """Map RSS response data to a `Draw` entity."""
        return Draw(
            draw_date=data.get("date"),  # pyright: ignore[reportArgumentType]
            lotto_6aus49_winning_numbers=data.get("lotto_numbers"),  # pyright: ignore[reportArgumentType]
            super_number=data.get("super_number"),  # pyright: ignore[reportArgumentType]
            spiel77_number=data.get("spiel77"),  # pyright: ignore[reportArgumentType]
            super6_number=data.get("super6"),  # pyright: ignore[reportArgumentType]
        )
