from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

ConstraintMode = Literal["hard", "soft"]
SolverStatus = Literal["optimal", "feasible", "infeasible", "model_invalid", "unknown"]


@dataclass(frozen=True, slots=True)
class ConstraintSpec:
    """Declarative constraint descriptor used by handlers."""

    type: str
    mode: ConstraintMode
    params: dict[str, Any] = field(default_factory=dict)
    weight: int = 1


@dataclass(frozen=True, slots=True)
class ObjectiveConfig:
    """Optional tie-breaker objective settings."""

    assignment_weight: int = 1
    fairness_weight: int = 1


@dataclass(frozen=True, slots=True)
class Problem:
    """Intermediate representation for a scheduling problem."""

    employees: tuple[str, ...]
    days: int
    shifts: tuple[str, ...]
    constraints: tuple[ConstraintSpec, ...]
    objective: ObjectiveConfig = ObjectiveConfig()


@dataclass(frozen=True, slots=True)
class PenaltySummary:
    """Aggregated penalty/violation metrics for one constraint type."""

    weight: int
    violations: int
    weighted_penalty: int


@dataclass(frozen=True, slots=True)
class SolutionMetadata:
    """Additional diagnostics returned with every solve."""

    status: SolverStatus
    penalties: dict[str, PenaltySummary]
    total_violations: int


@dataclass(frozen=True, slots=True)
class Solution:
    """Solver response model before JSON serialization."""

    schedule: list[dict[str, str | list[str] | None]]
    objective: int
    metadata: SolutionMetadata
