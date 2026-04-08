"""Input-side data structures: employees, holidays, schedule input."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class StateRun:
    """A consecutive run of a state carried over from the previous period."""

    value: str
    count: int


@dataclass(frozen=True)
class EmployeeHistory:
    """Per-employee history for period-boundary continuity."""

    # Shift counts from the immediately preceding period.
    last_month_shift_counts: dict[str, int] = field(default_factory=dict)
    # Consecutive run of a state at the end of the previous period.
    previous_state_run: StateRun | None = None


@dataclass(frozen=True)
class Employee:
    """
    A team member.

    ``attributes`` is a free-form map used only for rule targeting (WHO scope).
    The engine never inspects specific attribute keys — rules do.

    ``previous_week_days`` carries the literal assignments for days before the
    period start that fall in the same ISO week as the first period day.
    Used by ``count_per_week`` to correctly enforce weekly counts on the
    boundary week.  Keys are dates, values are state names.
    """

    id: str
    name: str
    attributes: dict[str, str] = field(default_factory=dict)
    # Per-person numeric balances keyed by state name, e.g. {"annual": 8}.
    balances: dict[str, int] = field(default_factory=dict)
    # Earned records keyed by state name, e.g. {"comp_off": [...]}.
    records: dict[str, list[dict[str, str]]] = field(default_factory=dict)
    history: EmployeeHistory = field(default_factory=EmployeeHistory)
    # Assignments from days before the period that share the same ISO week.
    # e.g. {"2026-03-30": "afternoon", "2026-03-31": "week_off"}
    previous_week_days: dict[date, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Holiday:
    """
    A public holiday.

    ``locations`` is the set of location attribute values for which this
    holiday applies.  An empty list means the holiday is global.
    """

    date: date
    locations: list[str] = field(default_factory=list)

    def applies_to(self, employee: Employee, location_key: str = "city") -> bool:
        """Return True if this holiday applies to *employee*."""
        if not self.locations:
            return True
        return employee.attributes.get(location_key, "") in self.locations


@dataclass
class ScheduleInput:
    """
    Complete, parsed input for one scheduling run.

    ``dates`` is the ordered list of every calendar day in the period.
    ``states`` is the full set of valid state names (work + off), derived
    from ``settings.shifts`` and ``settings.leave_types``.
    """

    period_start: date
    period_end: date
    dates: list[date]
    employees: list[Employee]
    holidays: list[Holiday]
    # All valid state names for this run (populated by the parser).
    states: list[str] = field(default_factory=list)

    # ── Convenience helpers ───────────────────────────────────────────────────

    def is_holiday_for(self, d: date, employee: Employee, location_key: str = "city") -> bool:
        """Return True if *d* is a public holiday for *employee*."""
        return any(h.date == d and h.applies_to(employee, location_key) for h in self.holidays)

    def is_weekend(self, d: date) -> bool:
        """Return True if *d* falls on a Saturday or Sunday."""
        return d.weekday() >= 5
