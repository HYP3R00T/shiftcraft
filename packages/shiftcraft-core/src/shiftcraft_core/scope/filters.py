"""
filter_who(who, employees) -> list[Employee]
filter_when(when, dates, inp) -> list[date]

Both functions are pure — no side effects, no model access.
"""

from __future__ import annotations

from datetime import date

from ..types.input import Employee, ScheduleInput
from ..types.rules import WhenFilter, WhoFilter

# ── WHO ───────────────────────────────────────────────────────────────────────


def filter_who(who: WhoFilter, employees: list[Employee]) -> list[Employee]:
    """Return the subset of *employees* matched by *who*."""
    match who.type:
        case "all":
            return list(employees)
        case "attribute":
            return [e for e in employees if e.attributes.get(who.key) == who.value]
        case "employees":
            ids = set(who.ids)
            return [e for e in employees if e.id in ids]
        case _:
            raise ValueError(f"Unknown WHO type: {who.type!r}")


# ── WHEN ──────────────────────────────────────────────────────────────────────


def filter_when(when: WhenFilter, inp: ScheduleInput) -> list[date]:
    """Return the subset of *inp.dates* matched by *when*."""
    match when.type:
        case "always":
            return list(inp.dates)

        case "dates":
            target = {date.fromisoformat(v) for v in when.values}
            return [d for d in inp.dates if d in target]

        case "date_range":
            start = date.fromisoformat(when.start)  # type: ignore[arg-type]
            end = date.fromisoformat(when.end)  # type: ignore[arg-type]
            return [d for d in inp.dates if start <= d <= end]

        case "day_of_week":
            # when.values holds lowercase day names: "monday", "friday", …
            _dow = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
            target_indices = {_dow.index(v) for v in when.values}
            return [d for d in inp.dates if d.weekday() in target_indices]

        case "day_type":
            match when.value:
                case "weekend":
                    return [d for d in inp.dates if inp.is_weekend(d)]
                case "holiday":
                    # A day is a "holiday day" if at least one employee has a
                    # holiday on it.  Primitive handlers narrow further per employee.
                    holiday_dates = {h.date for h in inp.holidays}
                    return [d for d in inp.dates if d in holiday_dates]
                case _:
                    raise ValueError(f"Unknown day_type value: {when.value!r}")

        case _:
            raise ValueError(f"Unknown WHEN type: {when.type!r}")
