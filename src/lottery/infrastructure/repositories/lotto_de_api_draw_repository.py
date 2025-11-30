from datetime import date, datetime
from typing import Annotated, Any, ClassVar, override
from zoneinfo import ZoneInfo

import requests
from pydantic import AfterValidator, BaseModel, ConfigDict, Field, PastDatetime, RootModel

from lottery.application.repositories import DrawNotFoundError, DrawRepository
from lottery.domain.draw import Draw
from lottery.utils import ensure_berlin_tz


class LottoDeApiDrawRepository(DrawRepository):
    """Repository that manages lottery draw data using LOTTO.de's API."""

    def __init__(self, client: LottoDeApiClient | None = None, mapper: DrawMapper | None = None):
        self._client: LottoDeApiClient = client or LottoDeApiClient()
        self._mapper: DrawMapper = mapper or DrawMapper()

    @override
    def get_by_date(self, date: date) -> Draw:
        raw_data: list[dict[str, Any]] = self._client.fetch_draw_by_date(date)  # pyright: ignore[reportExplicitAny]
        response: ApiResponse = ApiResponse.model_validate(raw_data)
        draws: list[Draw] = self._mapper.to_draws(response)
        if len(draws) == 0:
            raise DrawNotFoundError(date)
        if len(draws) > 1:
            raise ValueError(
                f"API returned data for multiples draws for date {date}; expected exactly one."
            )
        return draws[0]

    @override
    def get_since_date(self, date: date) -> list[Draw]:
        raw_data: list[dict[str, Any]] = self._client.fetch_all_draws()  # pyright: ignore[reportExplicitAny]
        response: ApiResponse = ApiResponse.model_validate(raw_data)
        return self._mapper.to_draws(response)


class LottoDeApiClient:
    """A HTTP client for the LOTTO.de API."""

    _BASE_URL: str = "https://www.lotto.de/api/stats/entities.lotto"

    def fetch_draw_by_date(self, draw_date: date) -> list[dict[str, Any]]:  # pyright: ignore[reportExplicitAny]
        """Fetch the data for the draw that occured on the specified date."""
        url: str = self._build_url_for_date(draw_date)
        return self._fetch(url)

    def fetch_all_draws(self) -> list[dict[str, Any]]:  # pyright: ignore[reportExplicitAny]
        """Fetch the data for all avaiable draws."""
        return self._fetch(self._BASE_URL, 30)

    def _fetch(self, url: str, timeout: int = 5) -> list[dict[str, Any]]:  # pyright: ignore[reportExplicitAny]
        """Fetch data via the LOTTO.de API using the provided URL."""
        response: requests.Response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return self._filter(response.json())  # pyright: ignore[reportAny]

    def _filter(self, raw_data: list[dict[str, Any]]) -> list[dict[str, Any]]:  # pyright: ignore[reportExplicitAny]
        """
        Filter the raw API resonse data.

        The lottery rules and draw frequency changed over time. We filter out the draw data that is
        not compatible with the today's rules.

        See https://www.lotto.de/lotto-6aus49/ueber/historie.
        """
        # In 2013, the winning classes were adjusted, such that we will get valid evaluations only
        # for draws after that date.
        cutoff_timestamp_ms: int = self._date_to_timestamp_with_ms(date(2014, 1, 1))
        filtered_data = [item for item in raw_data if item["drawDate"] >= cutoff_timestamp_ms]
        return filtered_data

    def _build_url_for_date(self, date: date) -> str:
        """Build the URL for an API call to get the lottery draw data of the specified day."""

        timestamp_ms: int = self._date_to_timestamp_with_ms(date)
        return f"{self._BASE_URL}/draws/{timestamp_ms}"

    def _date_to_timestamp_with_ms(self, date: date) -> int:
        """
        Convert the specified date to a UNIX timestamp with milliseconds.

        The API accepts a UNIX timestamp with milliseconds as a path parameter and returns the
        lottery draw data for the day of the UNIX timestamp. The exact millisecond does not matter,
        it is only about the day to which it belongs.
        """
        midnight: datetime = datetime.combine(date, datetime.min.time(), ZoneInfo("Europe/Berlin"))
        return int(midnight.timestamp()) * 1_000


class DrawMapper:
    """Mapper for converting lotto.de API responses to `Draw` entities."""

    @staticmethod
    def to_draws(response: ApiResponse) -> list[Draw]:
        """Map lotto.de API response to a list of `Draw` entities."""
        return [DrawMapper.to_draw(draw) for draw in response.root]

    @staticmethod
    def to_draw(draw_response: DrawResponse) -> Draw:
        """Map a single draw from a lotto.de API response to a `Draw` entity."""
        return Draw(
            draw_date=draw_response.drawDate.date(),
            lotto_6aus49_winning_numbers=[
                item.drawNumber for item in draw_response.drawNumbersCollection
            ],  # pyright: ignore[reportArgumentType]
            super_number=draw_response.superNumber,
            spiel77_number=draw_response.game77.numbers,
            super6_number=draw_response.super6.numbers,
        )


# Models for data returned by the API.


class GameTypeResponse(BaseModel):
    """Partial API response model for `gameType` objects."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    name: str


class DrawNumberResponse(BaseModel):
    """Partial API response model for items in `drawNumbersCollection` arrays."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    index: int = Field(ge=1, le=6)
    drawNumber: int = Field(ge=1, le=49)


class Game77Response(BaseModel):
    """Partial API response model for `game77` objects."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    drawDate: Annotated[PastDatetime, AfterValidator(ensure_berlin_tz)]
    gameType: GameTypeResponse
    numbers: str = Field(pattern=r"^\d{7}$")


class Super6Response(BaseModel):
    """Partial API response model for `super6` objects."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    drawDate: Annotated[PastDatetime, AfterValidator(ensure_berlin_tz)]
    gameType: GameTypeResponse
    numbers: str = Field(pattern=r"^\d{6}$")


class DrawResponse(BaseModel):
    """Partial API response model for items in the root array."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    drawDate: Annotated[PastDatetime, AfterValidator(ensure_berlin_tz)]
    gameType: GameTypeResponse
    drawNumbersCollection: list[DrawNumberResponse]
    superNumber: int = Field(ge=0, le=9)
    game77: Game77Response
    super6: Super6Response


ApiResponse = RootModel[list[DrawResponse]]
"""
Partial API response model.

It provides and validates only the fields of interest.
"""
