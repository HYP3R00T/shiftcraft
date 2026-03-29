"""Pure data structures for shiftcraft-core scheduling system."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass
class LeaveRequest:
    """A leave request for a specific date with optional type."""

    date: date
    leave_type: str | None  # None | "annual" | "comp_off" | "week_off"


@dataclass
class CompOffRecord:
    """Record of a compensatory off earned and optionally redeemed."""

    holiday_date: date
    redeemed_on: date | None


@dataclass
class ShiftHistory:
    """Historical shift counts from the previous month."""

    morning: int
    afternoon: int
    night: int
    regular: int
    week_off: int
    leave: int


@dataclass
class Employee:
    """Team member with leave history and preferences."""

    id: str
    name: str
    is_senior: bool
    city: str
    comp_off_balance: int
    leave_requests: list[LeaveRequest]
    last_month_shift_counts: ShiftHistory
    comp_off_records: list[CompOffRecord]


@dataclass
class CoverageSlot:
    """Coverage requirements for a single shift slot."""

    min: int
    target: int
    max: int


@dataclass
class DayCoverage:
    """Coverage requirements for all shifts on a given day."""

    morning: CoverageSlot
    afternoon: CoverageSlot
    night: CoverageSlot
    regular: CoverageSlot


@dataclass
class DateRangeOverride:
    """Override default coverage for a specific date range."""

    start: date
    end: date
    morning: CoverageSlot
    afternoon: CoverageSlot
    night: CoverageSlot
    regular: CoverageSlot

    def covers(self, d: date) -> bool:
        """Check if this override applies to the given date."""
        return self.start <= d <= self.end

    def get_slot(self, shift: str) -> CoverageSlot:
        """Get the coverage slot for a specific shift."""
        return getattr(self, shift)


@dataclass
class Holiday:
    """Holiday definition with optional location restrictions."""

    date: date
    locations: list[str]  # empty = global holiday


@dataclass
class ScheduleInput:
    """Complete input specification for schedule generation."""

    period_start: date
    period_end: date
    dates: list[date]
    employees: list[Employee]
    coverage_by_dow: dict[str, DayCoverage]  # keyed by lowercase day name
    date_range_overrides: list[DateRangeOverride]
    holidays: list[Holiday]

    def get_coverage(self, d: date) -> DayCoverage:
        """
        Return effective coverage for a date.

        Applies date-range overrides first, falls back to day-of-week defaults.
        """
        for override in self.date_range_overrides:
            if override.covers(d):
                return DayCoverage(
                    morning=override.morning,
                    afternoon=override.afternoon,
                    night=override.night,
                    regular=override.regular,
                )
        dow = d.strftime("%A").lower()
        return self.coverage_by_dow[dow]

    def is_holiday_for(self, d: date, city: str) -> bool:
        """Check if a date is a holiday for a specific city."""
        return any(h.date == d and (not h.locations or city in h.locations) for h in self.holidays)

# Made with Bob
