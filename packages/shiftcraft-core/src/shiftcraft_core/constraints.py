"""Hard constraint definitions for the CP-SAT model."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any

from ortools.sat.python import cp_model

from .constants import (
    COMP_OFF_VALIDITY_DAYS,
    DISALLOWED_TRANSITIONS,
    MAX_CONSECUTIVE_WORK_DAYS,
    MAX_WORKING_EMPLOYEES_PER_DAY,
    SHIFTS,
    WEEKLY_OFF_DAYS,
)
from .types import ScheduleInput


def _iso(d: date) -> str:
    """Convert date to ISO string."""
    return d.isoformat()


def _week_key(d: date) -> str:
    """ISO week identifier: year-Www."""
    iso = d.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def add_constraints(model: cp_model.CpModel, inp: ScheduleInput, vars_dict: dict[str, Any]) -> None:
    """
    Add all hard constraints to the CP-SAT model.

    Args:
        model: The CP-SAT model to add constraints to.
        inp: The parsed schedule input.
        vars_dict: Dictionary containing decision variables and metadata.
    """
    shift_vars = vars_dict["shift_vars"]
    off_vars = vars_dict["off_vars"]
    leave_vars = vars_dict["leave_vars"]
    emp_ids = vars_dict["emp_ids"]
    date_isos = vars_dict["date_isos"]

    # ── Linking: a day is either working (exactly one shift) or off ───────────
    _add_work_or_off_constraints(model, emp_ids, date_isos, shift_vars, off_vars, leave_vars)

    # ── Hard: shift coverage (min/max) per day ─────────────────────────────────
    _add_coverage_constraints(model, inp, emp_ids, shift_vars)

    # ── Hard: max working employees per day ────────────────────────────────────
    _add_max_workers_per_day_constraint(model, inp, emp_ids, shift_vars)

    # ── Hard: no disallowed shift transitions ──────────────────────────────────
    _add_transition_constraints(model, inp, emp_ids, shift_vars)

    # ── REMOVED: max consecutive working days (moved to objective as SOFT) ────

    # ── Hard: exactly 2 off days per calendar week ─────────────────────────────
    _add_weekly_off_constraints(model, inp, emp_ids, off_vars, leave_vars)

    # ── Hard: leave capacity gate per day ──────────────────────────────────────
    _add_leave_capacity_constraints(model, inp, emp_ids, off_vars)

    # ── Hard: typed leave requests must be honored ─────────────────────────────
    _add_leave_request_constraints(model, inp, date_isos, leave_vars, emp_ids)

    # ── Hard: comp_off validity ────────────────────────────────────────────────
    _add_comp_off_validity_constraints(model, inp, leave_vars)

    # ── Hard: balanced shift distribution (max difference of 3 between shifts) ─
    _add_shift_balance_per_employee(model, inp, emp_ids, date_isos, shift_vars)


def _add_work_or_off_constraints(
    model: cp_model.CpModel,
    emp_ids: list[str],
    date_isos: list[str],
    shift_vars: dict,
    off_vars: dict,
    leave_vars: dict,
) -> None:
    """Ensure each employee either works exactly one shift or is off each day."""
    for eid in emp_ids:
        for diso in date_isos:
            working_shifts = [shift_vars[(eid, diso, s)] for s in SHIFTS]
            leave_types = [leave_vars[(eid, diso, lt)] for lt in ("week_off", "annual", "comp_off")]

            # off_var = OR of all leave types
            model.add_bool_or(leave_types + [off_vars[(eid, diso)].Not()])
            # off_var is 1 iff at least one leave type is 1
            model.add(off_vars[(eid, diso)] == sum(leave_types))

            # Exactly one of: working or off
            model.add(sum(working_shifts) + off_vars[(eid, diso)] == 1)

            # At most one leave type per day
            model.add(sum(leave_types) <= 1)


def _add_coverage_constraints(
    model: cp_model.CpModel,
    inp: ScheduleInput,
    emp_ids: list[str],
    shift_vars: dict,
) -> None:
    """Enforce min/max coverage requirements for each shift on each day."""
    for d in inp.dates:
        diso = _iso(d)
        cov = inp.get_coverage(d)
        for shift in SHIFTS:
            slot = getattr(cov, shift)
            assigned = [shift_vars[(eid, diso, shift)] for eid in emp_ids]
            model.add(sum(assigned) >= slot.min)
            model.add(sum(assigned) <= slot.max)


def _add_max_workers_per_day_constraint(
    model: cp_model.CpModel,
    inp: ScheduleInput,
    emp_ids: list[str],
    shift_vars: dict,
) -> None:
    """Limit total number of working employees per day."""
    for d in inp.dates:
        diso = _iso(d)
        working = [shift_vars[(eid, diso, s)] for eid in emp_ids for s in SHIFTS]
        model.add(sum(working) <= MAX_WORKING_EMPLOYEES_PER_DAY)


def _add_transition_constraints(
    model: cp_model.CpModel,
    inp: ScheduleInput,
    emp_ids: list[str],
    shift_vars: dict,
) -> None:
    """Prevent disallowed shift transitions (e.g., Night → Morning)."""
    emp_by_id = {e.id: e for e in inp.employees}
    first_diso = _iso(inp.dates[0])

    # Cross-month boundary: check last day of previous_week_days → first day of period
    for eid in emp_ids:
        emp = emp_by_id[eid]
        if emp.previous_week_days:
            # Find the date immediately before period_start
            from datetime import timedelta

            prev_day = inp.period_start - timedelta(days=1)
            prev_shift = emp.previous_week_days.get(prev_day)
            if prev_shift:
                for s_from, s_to in DISALLOWED_TRANSITIONS:
                    if prev_shift == s_from:
                        model.add(shift_vars[(eid, first_diso, s_to)] == 0)

    # Within-period transitions
    for i in range(len(inp.dates) - 1):
        d0, d1 = inp.dates[i], inp.dates[i + 1]
        d0iso, d1iso = _iso(d0), _iso(d1)
        for eid in emp_ids:
            for s_from, s_to in DISALLOWED_TRANSITIONS:
                model.add_implication(
                    shift_vars[(eid, d0iso, s_from)],
                    shift_vars[(eid, d1iso, s_to)].Not(),
                )


def _add_consecutive_work_limit(
    model: cp_model.CpModel,
    inp: ScheduleInput,
    emp_ids: list[str],
    shift_vars: dict,
) -> None:
    """Enforce maximum consecutive working days limit."""
    for eid in emp_ids:
        for i in range(len(inp.dates) - MAX_CONSECUTIVE_WORK_DAYS):
            window = inp.dates[i : i + MAX_CONSECUTIVE_WORK_DAYS + 1]
            working_in_window = [shift_vars[(eid, _iso(d), s)] for d in window for s in SHIFTS]
            model.add(sum(working_in_window) <= MAX_CONSECUTIVE_WORK_DAYS)


def _add_weekly_off_constraints(
    model: cp_model.CpModel,
    inp: ScheduleInput,
    emp_ids: list[str],
    off_vars: dict,
    leave_vars: dict,
) -> None:
    """
    Ensure exactly 2 week_off days per calendar week, accounting for previous month.

    Annual leave and comp_off do NOT count toward the weekly off quota — only
    explicit week_off assignments do. This ensures employees always get their
    2 rest days regardless of any leave taken that week.

    For full weeks (7 days in scheduling period): STRICT - exactly 2 week_offs required.
    For partial weeks at period start (prev offs known): enforce remaining exactly.
    For partial weeks at period end (rest of week in next month): flexible ±1.
    """
    weeks: dict[str, list[date]] = defaultdict(list)
    for d in inp.dates:
        weeks[_week_key(d)].append(d)

    # Identify which weeks are partial at the start vs end of the period
    first_week_key = _week_key(inp.period_start)
    last_week_key = _week_key(inp.period_end)

    emp_by_id = {e.id: e for e in inp.employees}

    for eid in emp_ids:
        emp = emp_by_id[eid]

        for week_key, wk_dates in weeks.items():
            # Count week_offs from previous month that fall in this ISO week
            prev_offs_in_week = 0
            if emp.previous_week_days:
                for prev_date, shift_type in emp.previous_week_days.items():
                    if _week_key(prev_date) == week_key and shift_type == "week_off":
                        prev_offs_in_week += 1

            # Only count week_off leave type — NOT annual or comp_off
            week_off_in_week = [leave_vars[(eid, _iso(d), "week_off")] for d in wk_dates]
            week_len = len(wk_dates)
            remaining_offs_needed = WEEKLY_OFF_DAYS - prev_offs_in_week

            if week_len >= 7:
                # Full week: exactly 2 week_offs (hard)
                model.add(sum(week_off_in_week) == remaining_offs_needed)
            elif week_key == first_week_key:
                # Partial week at period START: we know all previous offs,
                # so enforce exactly the remaining count needed
                capped = min(remaining_offs_needed, week_len)
                if capped > 0:
                    model.add(sum(week_off_in_week) == capped)
            elif week_key == last_week_key:
                # Partial week at period END: rest of week spills into next month,
                # be flexible to avoid impossible constraints when days are scarce
                model.add(sum(week_off_in_week) >= max(0, remaining_offs_needed - 1))
                model.add(sum(week_off_in_week) <= remaining_offs_needed)


def _add_leave_capacity_constraints(
    model: cp_model.CpModel,
    inp: ScheduleInput,
    emp_ids: list[str],
    off_vars: dict,
) -> None:
    """Ensure enough employees are working to meet minimum coverage."""
    for d in inp.dates:
        diso = _iso(d)
        cov = inp.get_coverage(d)
        required = sum(getattr(cov, s).min for s in SHIFTS)
        max_off = len(inp.employees) - required
        off_today = [off_vars[(eid, diso)] for eid in emp_ids]
        model.add(sum(off_today) <= max_off)


def _add_leave_request_constraints(
    model: cp_model.CpModel,
    inp: ScheduleInput,
    date_isos: list[str],
    leave_vars: dict,
    emp_ids: list[str],
) -> None:
    """Honor typed leave requests and restrict annual/comp_off to requested dates only."""
    # Build set of dates where each employee has annual/comp_off requests
    annual_requested: dict[str, set[str]] = {eid: set() for eid in emp_ids}
    comp_off_requested: dict[str, set[str]] = {eid: set() for eid in emp_ids}

    for emp in inp.employees:
        for lr in emp.leave_requests:
            diso = _iso(lr.date)
            if diso not in set(date_isos):
                continue
            if lr.leave_type == "annual":
                annual_requested[emp.id].add(diso)
            elif lr.leave_type == "comp_off":
                comp_off_requested[emp.id].add(diso)

            if lr.leave_type is not None:
                # Hard: force this exact leave type on this date
                model.add(leave_vars[(emp.id, diso, lr.leave_type)] == 1)

    # Hard: annual and comp_off can ONLY be used on dates where they were requested
    for eid in emp_ids:
        for diso in date_isos:
            # If annual not requested on this date, it cannot be assigned
            if diso not in annual_requested[eid]:
                model.add(leave_vars[(eid, diso, "annual")] == 0)

            # If comp_off not requested on this date, it cannot be assigned
            if diso not in comp_off_requested[eid]:
                model.add(leave_vars[(eid, diso, "comp_off")] == 0)


def _add_comp_off_validity_constraints(
    model: cp_model.CpModel,
    inp: ScheduleInput,
    leave_vars: dict,
) -> None:
    """Ensure comp_off usage doesn't exceed valid (non-expired) balance."""
    for emp in inp.employees:
        valid_comp_off_count = sum(
            1
            for r in emp.comp_off_records
            if r.redeemed_on is None and (inp.period_start - r.holiday_date).days <= COMP_OFF_VALIDITY_DAYS
        )
        # Total comp_off leaves taken cannot exceed valid balance
        comp_off_days = [leave_vars[(emp.id, _iso(d), "comp_off")] for d in inp.dates]
        model.add(sum(comp_off_days) <= valid_comp_off_count)


# Made with Bob


def _add_shift_balance_per_employee(
    model: cp_model.CpModel,
    inp: ScheduleInput,
    emp_ids: list[str],
    date_isos: list[str],
    shift_vars: dict,
) -> None:
    """Ensure each employee has balanced distribution across core shifts (morning/afternoon/night)."""
    from .constants import CORE_SHIFTS

    # For each employee, ensure their CORE shift counts are within a reasonable range
    # Note: 'regular' shift is excluded because it has limited availability (specific days only)
    for eid in emp_ids:
        shift_counts = []
        for shift in CORE_SHIFTS:
            count = model.new_int_var(0, len(date_isos), f"count_{eid}_{shift}")
            model.add(count == sum(shift_vars[(eid, diso, shift)] for diso in date_isos))
            shift_counts.append(count)

        # All core shift counts should be within 2 of each other
        # This ensures fair distribution: prevents cases like 9 morning, 6 afternoon, 6 night
        if len(shift_counts) > 1:
            max_count = model.new_int_var(0, len(date_isos), f"max_shift_{eid}")
            min_count = model.new_int_var(0, len(date_isos), f"min_shift_{eid}")
            model.add_max_equality(max_count, shift_counts)
            model.add_min_equality(min_count, shift_counts)

            # Maximum difference of 1 shift between any two core shift types
            # This ensures very tight balance: e.g., 6-6-6 or 6-6-7
            model.add(max_count - min_count <= 1)
