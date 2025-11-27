from dataclasses import dataclass
from datetime import date
from typing import Self

from lottery.domain.draw import Draw
from lottery.domain.games.lotto_6aus49 import Lotto6aus49Evaluation
from lottery.domain.games.spiel77 import Spiel77Evaluation
from lottery.domain.games.super6 import Super6Evaluation
from lottery.domain.ticket import Ticket
from lottery.domain.ticket_evaluation import TicketEvaluation


@dataclass(frozen=True)
class DrawDTO:
    draw_date: date
    lotto_6aus49_winning_numbers: frozenset[int]
    super_number: int
    spiel77_number: str
    super6_number: str

    @classmethod
    def from_entity(cls, entity: Draw) -> Self:
        return cls(
            draw_date=entity.draw_date,
            lotto_6aus49_winning_numbers=entity.lotto_6aus49_winning_numbers,
            super_number=entity.super_number,
            spiel77_number=entity.spiel77_number,
            super6_number=entity.super6_number,
        )


@dataclass(frozen=True)
class TicketDTO:
    ticket_number: str
    draw_date: date
    lotto_6aus49_picks: list[frozenset[int]]
    play_spiel77: bool
    play_super6: bool

    @classmethod
    def from_entity(cls, entity: Ticket) -> Self:
        return cls(
            ticket_number=entity.ticket_number.number,
            draw_date=entity.draw_date,
            lotto_6aus49_picks=[pick.numbers for pick in entity.lotto_6aus49_picks],
            play_spiel77=entity.play_spiel77,
            play_super6=entity.play_super6,
        )


@dataclass(frozen=True)
class TicketEvaluationDTO:
    lotto_6aus49_evaluation: list[Lotto6aus49EvaluationDTO]
    spiel77_evaluation: Spiel77EvaluationDTO | None
    super6_evaluation: Super6EvaluationDTO | None

    @classmethod
    def from_entity(cls, entity: TicketEvaluation) -> Self:
        lotto_6aus49_evaluation_dto: list[Lotto6aus49EvaluationDTO] = [
            Lotto6aus49EvaluationDTO.from_entity(evaluation)
            for evaluation in entity.lotto_6aus49_evaluation
        ]
        spiel77_evaluation: Spiel77EvaluationDTO | None = (
            Spiel77EvaluationDTO.from_entity(entity.spiel77_evaluation)
            if entity.spiel77_evaluation
            else None
        )
        super6_evaluation: Super6EvaluationDTO | None = (
            Super6EvaluationDTO.from_entity(entity.super6_evaluation)
            if entity.super6_evaluation
            else None
        )

        return cls(
            lotto_6aus49_evaluation=lotto_6aus49_evaluation_dto,
            spiel77_evaluation=spiel77_evaluation,
            super6_evaluation=super6_evaluation,
        )


@dataclass(frozen=True)
class Lotto6aus49EvaluationDTO:
    matching_numbers: frozenset[int]
    super_number_matched: bool
    winning_class: int | None

    @classmethod
    def from_entity(cls, entity: Lotto6aus49Evaluation) -> Self:
        return cls(
            matching_numbers=entity.matching_numbers,
            super_number_matched=entity.super_number_matched,
            winning_class=entity.winning_class,
        )


@dataclass(frozen=True)
class Spiel77EvaluationDTO:
    matched_digits: int
    winning_class: int | None

    @classmethod
    def from_entity(cls, entity: Spiel77Evaluation) -> Self:
        return cls(
            matched_digits=entity.matched_digits,
            winning_class=entity.winning_class,
        )


@dataclass(frozen=True)
class Super6EvaluationDTO:
    matched_digits: int
    winning_class: int | None

    @classmethod
    def from_entity(cls, entity: Super6Evaluation) -> Super6EvaluationDTO:
        return cls(
            matched_digits=entity.matched_digits,
            winning_class=entity.winning_class,
        )
