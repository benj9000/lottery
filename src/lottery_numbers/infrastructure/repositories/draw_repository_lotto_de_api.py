from datetime import date, datetime
from typing import Annotated, ClassVar
from zoneinfo import ZoneInfo

import requests
from pydantic import AfterValidator, BaseModel, ConfigDict, Field, PastDatetime, RootModel

from lottery_numbers.application.repositories import DrawNotFoundError
from lottery_numbers.domain.draw import Draw
from lottery_numbers.utils import ensure_berlin_tz


class DrawRepositoryLottoDeApi:
    """Repository that manages lottery draw data using LOTTO.de's API."""

    def __init__(self):
        self._mapper: DrawMapper = DrawMapper()

    def get_for_date(self, draw_date: date) -> Draw:
        url: str = self._build_url(draw_date)
        response: ApiResponse = self._fetch(url)
        draws: list[Draw] = self._mapper.to_draws(response)
        if len(draws) == 0:
            raise DrawNotFoundError(draw_date)
        if len(draws) > 1:
            raise ValueError(
                f"API returned data for multiples draws for date {draw_date}; expected exactly one."
            )
        return draws[0]

    @staticmethod
    def _build_url(draw_date: date) -> str:
        """
        Build the URL for an API call to get the lottery draw data of the given day.

        Example URL: https://www.lotto.de/api/stats/entities.lotto/draws/946681200000.
        """

        base_url: str = "https://www.lotto.de/api/stats/entities.lotto/draws/"

        # The API accepts a UNIX timestamp with milliseconds as a path parameter and returns the lottery
        # draw data for the day of the UNIX timestamp. The exact millisecond does not matter, it is only
        # about the day to which it belongs.
        midnight: datetime = datetime.combine(
            draw_date, datetime.min.time(), ZoneInfo("Europe/Berlin")
        )
        timestamp_seconds: int = int(midnight.timestamp())
        timestamp_milliseconds: int = timestamp_seconds * 1_000

        return f"{base_url}{timestamp_milliseconds}"

    @staticmethod
    def _fetch(url: str) -> ApiResponse:
        """Fetch data via the lotto.de API using the provided URL."""
        response: requests.Response = requests.get(url, timeout=5)
        response.raise_for_status()
        return ApiResponse.model_validate_json(response.text)


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
