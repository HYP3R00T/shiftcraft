"""Conflict detection and error reporting for infeasible schedules."""

from __future__ import annotations

from .constants import MAX_WORKING_EMPLOYEES_PER_DAY, SHIFTS
from .types import ScheduleInput


def diagnose_conflicts(inp: ScheduleInput) -> list[str]:
    """
    Analyze input to identify potential causes of infeasibility.

    Args:
        inp: The parsed schedule input.

    Returns:
        List of human-readable conflict explanations.
    """
    reasons: list[str] = []
    n_emp = len(inp.employees)

    for d in inp.dates:
        cov = inp.get_coverage(d)
        total_min = sum(getattr(cov, s).min for s in SHIFTS)

        # Check if minimum coverage exceeds team size
        if total_min > n_emp:
            reasons.append(f"{d.isoformat()}: total minimum coverage ({total_min}) exceeds team size ({n_emp})")

        # Check if minimum coverage exceeds max workers per day
        if total_min > MAX_WORKING_EMPLOYEES_PER_DAY:
            reasons.append(
                f"{d.isoformat()}: minimum coverage ({total_min}) exceeds "
                f"MAX_WORKING_EMPLOYEES_PER_DAY ({MAX_WORKING_EMPLOYEES_PER_DAY})"
            )

        # Check if hard leave requests conflict with coverage requirements
        hard_leaves_today = [
            emp.name for emp in inp.employees for lr in emp.leave_requests if lr.date == d and lr.leave_type is not None
        ]
        max_off = n_emp - total_min
        if len(hard_leaves_today) > max_off:
            reasons.append(
                f"{d.isoformat()}: {len(hard_leaves_today)} hard leave requests "
                f"({', '.join(hard_leaves_today)}) but only {max_off} can be off "
                f"(team={n_emp}, min_workers={total_min})"
            )

    if not reasons:
        reasons.append(
            "No obvious structural conflict detected. "
            "Likely caused by interaction of consecutive-day, weekly-off, or coverage constraints."
        )

    return reasons


# Made with Bob
