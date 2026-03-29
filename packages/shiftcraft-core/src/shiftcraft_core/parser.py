"""JSON parsing and validation — converts raw JSON dict into typed dataclasses."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from .constants import DAYS_OF_WEEK
from .types import (
    CompOffRecord,
    CoverageSlot,
    DateRangeOverride,
    DayCoverage,
    Employee,
    Holiday,
    LeaveRequest,
    ScheduleInput,
    ShiftHistory,
)


def _parse_date(s: str) -> date:
    """Parse ISO date string to date object."""
    return date.fromisoformat(s)


def _parse_slot(raw: dict[str, Any]) -> CoverageSlot:
    """Parse a coverage slot from raw JSON."""
    return CoverageSlot(min=raw["min"], target=raw["target"], max=raw["max"])


def _parse_day_coverage(raw: dict[str, Any]) -> DayCoverage:
    """Parse day coverage from raw JSON."""
    return DayCoverage(
        morning=_parse_slot(raw["morning"]),
        afternoon=_parse_slot(raw["afternoon"]),
        night=_parse_slot(raw["night"]),
        regular=_parse_slot(raw["regular"]),
    )


def load(payload: dict[str, Any]) -> ScheduleInput:
    """
    Parse and validate input JSON payload.

    Args:
        payload: Raw JSON dict containing period, team, coverage, and holidays.

    Returns:
        Validated ScheduleInput with all dates expanded and structures parsed.
    """
    period_start = _parse_date(payload["period"]["start"])
    period_end = _parse_date(payload["period"]["end"])

    # Expand date range into list of dates
    dates: list[date] = []
    cur = period_start
    while cur <= period_end:
        dates.append(cur)
        cur += timedelta(days=1)

    # Parse employees
    employees: list[Employee] = []
    for e in payload["team"]:
        leave_requests = [
            LeaveRequest(
                date=_parse_date(lr["date"]),
                leave_type=lr.get("leave_type"),
            )
            for lr in e.get("leave_requests", [])
        ]
        hist = e["history"]["last_month_shift_counts"]
        comp_off_raw = e["history"].get("comp_off", {})
        comp_off_records = [
            CompOffRecord(
                holiday_date=_parse_date(r["holiday_date"]),
                redeemed_on=_parse_date(r["redeemed_on"]) if r.get("redeemed_on") else None,
            )
            for r in comp_off_raw.get("records", [])
        ]

        # Parse previous_week_days (optional field for cross-month week tracking)
        previous_week_days: dict[date, str] | None = None
        if "previous_week_days" in e and e["previous_week_days"]:
            previous_week_days = {
                _parse_date(date_str): shift_type
                for date_str, shift_type in e["previous_week_days"].items()
                if shift_type  # Skip empty strings
            }

        employees.append(
            Employee(
                id=e["id"],
                name=e["name"],
                is_senior=e.get("is_senior", False),
                city=e.get("city", ""),
                comp_off_balance=e.get("comp_off_balance", 0),
                leave_requests=leave_requests,
                last_month_shift_counts=ShiftHistory(
                    morning=hist.get("morning", 0),
                    afternoon=hist.get("afternoon", 0),
                    night=hist.get("night", 0),
                    regular=hist.get("regular", 0),
                    week_off=hist.get("week_off", 0),
                    leave=hist.get("leave", 0),
                ),
                comp_off_records=comp_off_records,
                previous_week_days=previous_week_days,
            )
        )

    # Parse coverage by day of week
    cov_raw = payload["coverage"]
    coverage_by_dow: dict[str, DayCoverage] = {
        day: _parse_day_coverage(cov_raw["by_day_of_week"][day]) for day in DAYS_OF_WEEK
    }

    # Parse date range overrides
    date_range_overrides: list[DateRangeOverride] = [
        DateRangeOverride(
            start=_parse_date(dr["start"]),
            end=_parse_date(dr["end"]),
            morning=_parse_slot(dr["morning"]),
            afternoon=_parse_slot(dr["afternoon"]),
            night=_parse_slot(dr["night"]),
            regular=_parse_slot(dr["regular"]),
        )
        for dr in cov_raw.get("by_date_range", [])
    ]

    # Parse holidays
    holidays: list[Holiday] = [
        Holiday(
            date=_parse_date(h["date"]),
            locations=h.get("locations", []),
        )
        for h in payload.get("holidays", [])
    ]

    return ScheduleInput(
        period_start=period_start,
        period_end=period_end,
        dates=dates,
        employees=employees,
        coverage_by_dow=coverage_by_dow,
        date_range_overrides=date_range_overrides,
        holidays=holidays,
    )


# Made with Bob
