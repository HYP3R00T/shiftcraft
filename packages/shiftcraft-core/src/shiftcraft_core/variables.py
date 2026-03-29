"""CP-SAT decision variable creation."""

from __future__ import annotations

from typing import Any

from ortools.sat.python import cp_model

from .constants import SHIFTS
from .types import ScheduleInput


def _iso(d) -> str:
    """Convert date to ISO string."""
    return d.isoformat()


def create_variables(model: cp_model.CpModel, inp: ScheduleInput) -> dict[str, Any]:
    """
    Create all decision variables for the scheduling problem.

    Args:
        model: The CP-SAT model to add variables to.
        inp: The parsed schedule input.

    Returns:
        Dictionary containing:
        - shift_vars: {(emp_id, date_iso, shift): BoolVar} — 1 if assigned
        - off_vars: {(emp_id, date_iso): BoolVar} — 1 if off (week_off or leave)
        - leave_vars: {(emp_id, date_iso, leave_type): BoolVar} — 1 if specific leave type
        - emp_ids: list of employee IDs
        - emp_by_id: dict mapping employee ID to Employee object
        - date_isos: list of date ISO strings
        - date_by_iso: dict mapping date ISO string to date object
    """
    emp_ids = [e.id for e in inp.employees]
    emp_by_id = {e.id: e for e in inp.employees}
    date_isos = [_iso(d) for d in inp.dates]
    date_by_iso = {_iso(d): d for d in inp.dates}

    # ── Shift assignment variables ────────────────────────────────────────────
    # shift_vars[(emp_id, date_iso, shift)] = 1 if employee works that shift on that date
    shift_vars: dict[tuple[str, str, str], cp_model.IntVar] = {}
    for eid in emp_ids:
        for diso in date_isos:
            for shift in SHIFTS:
                shift_vars[(eid, diso, shift)] = model.new_bool_var(f"shift_{eid}_{diso}_{shift}")

    # ── Off day variables ──────────────────────────────────────────────────────
    # off_vars[(emp_id, date_iso)] = 1 if employee is off (any leave type or week_off)
    off_vars: dict[tuple[str, str], cp_model.IntVar] = {}
    for eid in emp_ids:
        for diso in date_isos:
            off_vars[(eid, diso)] = model.new_bool_var(f"off_{eid}_{diso}")

    # ── Leave type variables ───────────────────────────────────────────────────
    # leave_vars[(emp_id, date_iso, leave_type)] = 1 if employee takes that leave type
    # leave_type ∈ {week_off, annual, comp_off}
    leave_vars: dict[tuple[str, str, str], cp_model.IntVar] = {}
    for eid in emp_ids:
        for diso in date_isos:
            for ltype in ("week_off", "annual", "comp_off"):
                leave_vars[(eid, diso, ltype)] = model.new_bool_var(f"leave_{eid}_{diso}_{ltype}")

    return {
        "shift_vars": shift_vars,
        "off_vars": off_vars,
        "leave_vars": leave_vars,
        "emp_ids": emp_ids,
        "emp_by_id": emp_by_id,
        "date_isos": date_isos,
        "date_by_iso": date_by_iso,
    }

# Made with Bob
