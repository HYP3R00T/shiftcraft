from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from shiftcraft_core.models import Problem

SOFT_PRIORITY_SCALE = 10_000


@dataclass(slots=True)
class PenaltyEntry:
    """One soft-constraint violation variable in the objective."""

    constraint_type: str
    weight: int
    var: Any


@dataclass(slots=True)
class CompileContext:
    """Mutable state shared while compiling constraints."""

    problem: Problem
    model: Any
    x: dict[tuple[int, int, int], Any] = field(default_factory=dict)
    penalties: list[PenaltyEntry] = field(default_factory=list)
    tie_breakers: list[Any] = field(default_factory=list)

    def add_penalty(self, constraint_type: str, weight: int, var: Any) -> None:
        self.penalties.append(PenaltyEntry(constraint_type=constraint_type, weight=weight, var=var))

    def add_tie_breaker(self, expr: Any) -> None:
        self.tie_breakers.append(expr)
