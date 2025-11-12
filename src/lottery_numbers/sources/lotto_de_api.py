from datetime import date, datetime
from typing import ClassVar

import requests
from pydantic import BaseModel, ConfigDict, Field, RootModel

from lottery_numbers.utils import raise_for_date_without_lottery_draw


class GameType(BaseModel):
    """Partial API response model for `gameType` objects."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    name: str


class DrawNumber(BaseModel):
    """Partial API response model for items in `drawNumbersCollection` arrays."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    index: int = Field(ge=1, le=6)
    drawNumber: int = Field(ge=1, le=49)


class Game77(BaseModel):
    """Partial API response model for `game77` objects."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    drawDate: datetime
    gameType: GameType
    numbers: str = Field(pattern=r"^\d{7}$")


class Super6(BaseModel):
    """Partial API response model for `super6` objects."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    drawDate: datetime
    gameType: GameType
    numbers: str = Field(pattern=r"^\d{6}$")


class Draw(BaseModel):
    """Partial API response model for items in the root array."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    drawDate: datetime
    gameType: GameType
    drawNumbersCollection: list[DrawNumber]
    superNumber: int = Field(ge=0, le=9)
    game77: Game77
    super6: Super6


Response = RootModel[list[Draw]]
"""
Partial API response model.

It provides and validates only the fields of interest.
"""


def build_url(date: date) -> str:
    """
    Build the URL for an API call to get the lottery draw data of the given day.

    Example URL: https://www.lotto.de/api/stats/entities.lotto/draws/946681200000.
    """
    raise_for_date_without_lottery_draw(date)

    base_url: str = "https://www.lotto.de/api/stats/entities.lotto/draws/"

    # The API accepts a UNIX timestamp with milliseconds as a path parameter and returns the lottery
    # draw data for the day of the UNIX timestamp. The exact millisecond does not matter, it is only
    # about the day to which it belongs.
    midnight: datetime = datetime.combine(date, datetime.min.time())
    timestamp_seconds: int = int(midnight.timestamp())
    timestamp_milliseconds: int = timestamp_seconds * 1_000

    return f"{base_url}{timestamp_milliseconds}"


def fetch_data(url: str) -> Response:
    """Fetch data via the lotto.de API using the provided URL."""
    response: requests.Response = requests.get(url, timeout=5)
    response.raise_for_status()
    return Response.model_validate_json(response.text)
