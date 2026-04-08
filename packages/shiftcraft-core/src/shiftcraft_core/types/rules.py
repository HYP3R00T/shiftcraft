"""Rule / settings data structures."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class RuleEnforcement(StrEnum):
    HARD = "hard"
    SOFT = "soft"
    PREFERENCE = "preference"


class RuleWeight(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    def penalty(self) -> int:
        return {"high": 100, "medium": 50, "low": 10}[self.value]


# ── Scope ─────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class WhoFilter:
    """
    WHO scope — which employees a rule targets.

    type: "all" | "attribute" | "employees"
    """

    type: str
    # "attribute" type
    key: str | None = None
    value: str | None = None
    # "employees" type
    ids: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class WhenFilter:
    """
    WHEN scope — which days a rule targets.

    type: "always" | "dates" | "date_range" | "day_of_week" | "day_type"
    """

    type: str
    # "dates" type
    values: tuple[str, ...] = field(default_factory=tuple)
    # "date_range" type
    start: str | None = None
    end: str | None = None
    # "day_of_week" type — values field reused (lowercase day names)
    # "day_type" type
    value: str | None = None


@dataclass(frozen=True)
class Scope:
    who: WhoFilter
    when: WhenFilter


# ── Balance source (for count_bounded_by_balance) ─────────────────────────────


@dataclass(frozen=True)
class BalanceSource:
    """
    Describes how to derive the per-person bound N(p, v).

    type: "numeric" | "records"
    """

    type: str
    key: str
    validity_days: int | None = None  # records type only


# ── Rule ──────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Rule:
    """
    A single scheduling rule in its parsed form.

    ``params`` holds all primitive-specific fields beyond the envelope
    (e.g. ``value``, ``count``, ``operator``, ``window_days``, …).
    """

    id: str
    type: str
    scope: Scope
    enforcement: RuleEnforcement
    params: dict[str, Any] = field(default_factory=dict)
    label: str = ""
    weight: RuleWeight | None = None
    overrides: tuple[str, ...] = field(default_factory=tuple)

    def penalty(self) -> int:
        """Return the penalty value for soft / preference rules."""
        if self.enforcement == RuleEnforcement.PREFERENCE:
            return 1
        if self.weight is not None:
            return self.weight.penalty()
        return 0


# ── Settings ──────────────────────────────────────────────────────────────────


@dataclass
class Settings:
    """
    The rules of the game — shared across runs for the same team.

    ``shifts``      — ordered list of working-state names.
    ``leave_types`` — ordered list of off-state names.
    ``rules``       — parsed rule objects.
    ``solver``      — raw solver config dict (time limit, etc.).
    """

    shifts: list[str]
    leave_types: list[str]
    rules: list[Rule]
    solver: dict[str, Any] = field(default_factory=dict)

    @property
    def all_states(self) -> list[str]:
        """All valid state names: working states followed by off states."""
        return self.shifts + self.leave_types
