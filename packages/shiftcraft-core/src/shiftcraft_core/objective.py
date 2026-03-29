"""Soft constraints as weighted penalty terms added to the CP-SAT objective."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any

from ortools.sat.python import cp_model

from .constants import (
    CORE_SHIFTS,
    SHIFTS,
    W_HISTORY_BIAS,
    W_OFF_BALANCE,
    W_OFF_CONTIGUOUS,
    W_SHIFT_BALANCE,
    W_SHIFT_BLOCK,
    W_TARGET_COVERAGE,
    W_UNTYPED_LEAVE,
)
from .types import ScheduleInput


def _week_key(d: date) -> str:
    """ISO week identifier: year-Www."""
    iso = d.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def add_objective(
    model: cp_model.CpModel,
    inp: ScheduleInput,
    vars_dict: dict[str, Any],
) -> None:
    """Attach a minimise-penalty objective to *model*."""
    shift_vars: dict[tuple[str, str, str], cp_model.IntVar] = vars_dict["shift_vars"]
    off_vars: dict[tuple[str, str], cp_model.IntVar] = vars_dict["off_vars"]
    emp_ids: list[str] = vars_dict["emp_ids"]
    emp_by_id = vars_dict["emp_by_id"]
    date_isos: list[str] = vars_dict["date_isos"]

    # Group dates by ISO week for weekend off constraints
    weeks: dict[str, list[date]] = defaultdict(list)
    for d in inp.dates:
        weeks[_week_key(d)].append(d)

    penalties: list[cp_model.LinearExprT] = []
    n_emp = len(emp_ids)
    n_days = len(inp.dates)

    # ── 1. Shift balance + history bias ──────────────────────────────────────
    for shift in CORE_SHIFTS:
        total_slots = sum(getattr(inp.get_coverage(d), shift).target for d in inp.dates)
        target_per_emp = total_slots // n_emp

        for eid in emp_ids:
            emp_count = sum(shift_vars[(eid, diso, shift)] for diso in date_isos)
            hist_count = getattr(emp_by_id[eid].last_month_shift_counts, shift)

            # Penalise deviation from fair share
            dev = model.new_int_var(0, n_days, f"shift_dev_{eid}_{shift}")
            model.add_abs_equality(dev, emp_count - target_per_emp)
            penalties.append(W_SHIFT_BALANCE * dev)

            # History bias: penalise assigning more of a shift already heavy last month
            # Scale: each assignment costs hist_count extra penalty points
            hist_penalty = model.new_int_var(0, n_days * 30, f"hist_{eid}_{shift}")
            model.add(hist_penalty == hist_count * emp_count)
            penalties.append(W_HISTORY_BIAS * hist_penalty)

    # ── 2. Shift block fragmentation ─────────────────────────────────────────
    # Penalise: worked shift S on day i, but NOT shift S on day i+1 (and day i+1 is a work day)
    for eid in emp_ids:
        for i in range(len(inp.dates) - 1):
            d0iso = date_isos[i]
            d1iso = date_isos[i + 1]
            for shift in CORE_SHIFTS:
                # trans = 1 iff: on shift today AND (different shift OR off tomorrow)
                # Simplified: penalise shift_vars[d0,s] AND NOT shift_vars[d1,s]
                # (includes off days — that's fine, off days break blocks too)
                trans = model.new_bool_var(f"trans_{eid}_{d0iso}_{shift}")
                # trans >= shift_vars[d0,s] - shift_vars[d1,s]  (lower bound)
                model.add(trans >= shift_vars[(eid, d0iso, shift)] - shift_vars[(eid, d1iso, shift)])
                # trans <= 1 - shift_vars[d1,s]  (can't be 1 if d1 has same shift)
                model.add(trans <= 1 - shift_vars[(eid, d1iso, shift)])
                # trans <= shift_vars[d0,s]  (can't be 1 if d0 doesn't have this shift)
                model.add(trans <= shift_vars[(eid, d0iso, shift)])
                penalties.append(W_SHIFT_BLOCK * trans)

    # ── 3. Weekend off balance across employees ───────────────────────────────
    weekend_off_counts = []
    for eid in emp_ids:
        wkend_offs = [off_vars[(eid, d.isoformat())] for d in inp.dates if d.weekday() >= 5]
        if wkend_offs:
            wkend_count = model.new_int_var(0, len(wkend_offs), f"wkend_off_{eid}")
            model.add(wkend_count == sum(wkend_offs))
            weekend_off_counts.append(wkend_count)

    if len(weekend_off_counts) > 1:
        max_wk = model.new_int_var(0, n_days, "max_wkend_off")
        min_wk = model.new_int_var(0, n_days, "min_wkend_off")
        model.add_max_equality(max_wk, weekend_off_counts)
        model.add_min_equality(min_wk, weekend_off_counts)
        wk_imbalance = model.new_int_var(0, n_days, "wkend_off_imbalance")
        model.add(wk_imbalance == max_wk - min_wk)
        penalties.append(W_OFF_BALANCE * wk_imbalance)

    # ── 4. Prefer paired Sat+Sun offs ────────────────────────────────────────
    for eid in emp_ids:
        for wk_dates in weeks.values():
            sat = [d for d in wk_dates if d.weekday() == 5 and d in inp.dates]
            sun = [d for d in wk_dates if d.weekday() == 6 and d in inp.dates]
            if sat and sun:
                sat_off = off_vars[(eid, sat[0].isoformat())]
                sun_off = off_vars[(eid, sun[0].isoformat())]
                diff = model.new_int_var(0, 1, f"wkend_diff_{eid}_{sat[0].isoformat()}")
                model.add_abs_equality(diff, sat_off - sun_off)
                penalties.append(W_OFF_CONTIGUOUS * diff)

    # ── 5. Target coverage shortfall ─────────────────────────────────────────
    for d in inp.dates:
        diso = d.isoformat()
        cov = inp.get_coverage(d)
        for shift in SHIFTS:
            slot = getattr(cov, shift)
            if slot.target > slot.min:
                assigned = sum(shift_vars[(eid, diso, shift)] for eid in emp_ids)
                shortfall = model.new_int_var(0, slot.target, f"target_short_{diso}_{shift}")
                model.add(shortfall >= slot.target - assigned)
                penalties.append(W_TARGET_COVERAGE * shortfall)

    # ── 6. Untyped leave preference ───────────────────────────────────────────
    for emp in inp.employees:
        for lr in emp.leave_requests:
            if lr.leave_type is not None:
                continue
            diso = lr.date.isoformat()
            if diso not in set(date_isos):
                continue
            not_off = model.new_bool_var(f"untyped_miss_{emp.id}_{diso}")
            model.add(not_off == 1 - off_vars[(emp.id, diso)])
            penalties.append(W_UNTYPED_LEAVE * not_off)

    # ── Minimise total penalty ────────────────────────────────────────────────
    if penalties:
        model.minimize(sum(penalties))
