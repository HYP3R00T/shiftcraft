"""
CP-SAT variable creation.

For each (employee, day) cell we create one Boolean variable per state.
Exactly one must be true — this enforces completeness and exclusivity.

vars_dict layout
----------------
{
    "x": dict[(emp_id, date_iso, state)] -> IntVar,
    "emp_ids": list[str],
    "date_isos": list[str],
    "states": list[str],
    "emp_by_id": dict[str, Employee],
}
"""

from __future__ import annotations

from typing import Any

from ortools.sat.python import cp_model

from ..types.input import ScheduleInput


def create_variables(
    model: cp_model.CpModel,
    inp: ScheduleInput,
) -> dict[str, Any]:
    """Create one BoolVar per (employee, day, state) and enforce exclusivity."""
    emp_ids = [e.id for e in inp.employees]
    emp_by_id = {e.id: e for e in inp.employees}
    date_isos = [d.isoformat() for d in inp.dates]
    states = inp.states

    x: dict[tuple[str, str, str], Any] = {}

    for emp in inp.employees:
        for _d, d_iso in zip(inp.dates, date_isos, strict=True):
            cell_vars: list[Any] = []
            for s in states:
                var = model.new_bool_var(f"x[{emp.id},{d_iso},{s}]")
                x[(emp.id, d_iso, s)] = var
                cell_vars.append(var)
            # Exactly one state per (employee, day)
            model.add_exactly_one(cell_vars)

    return {
        "x": x,
        "emp_ids": emp_ids,
        "date_isos": date_isos,
        "states": states,
        "emp_by_id": emp_by_id,
    }
