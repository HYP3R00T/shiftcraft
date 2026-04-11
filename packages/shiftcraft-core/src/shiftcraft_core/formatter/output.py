"""
format_solution(status, solver, inp, vars_dict) -> dict

Converts the CP-SAT solver result into the API response shape:
{
    "status": "optimal" | "feasible" | "infeasible" | "unknown",
    "schedule": { emp_id: { date_iso: state } },
    "metadata": { "solve_time_seconds": float, "objective": int | None }
}
"""

from __future__ import annotations

from typing import Any

from ortools.sat.python import cp_model

from ..types.input import ScheduleInput

_STATUS_MAP = {
    cp_model.OPTIMAL: "optimal",
    cp_model.FEASIBLE: "feasible",
    cp_model.INFEASIBLE: "infeasible",
    cp_model.UNKNOWN: "unknown",
    cp_model.MODEL_INVALID: "model_invalid",
}


def format_solution(
    status: cp_model.CpSolverStatus,
    solver: cp_model.CpSolver,
    inp: ScheduleInput,
    vars_dict: dict[str, Any],
) -> dict[str, Any]:
    status_str = _STATUS_MAP.get(status, "unknown")

    metadata: dict[str, Any] = {
        "status": status_str,
        "solve_time_seconds": round(solver.wall_time, 3),
        "objective": None,
    }

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {"status": status_str, "schedule": {}, "metadata": metadata}

    x = vars_dict["x"]
    date_isos = vars_dict["date_isos"]
    states = vars_dict["states"]

    by_date: dict[str, dict[str, str]] = {d_iso: {} for d_iso in date_isos}
    for emp in inp.employees:
        for d_iso in date_isos:
            for s in states:
                if solver.value(x[(emp.id, d_iso, s)]) == 1:
                    by_date[d_iso][emp.id] = s
                    break

    schedule: dict[str, dict[str, str]] = dict(sorted(by_date.items()))

    if vars_dict.get("penalties"):
        metadata["objective"] = int(solver.objective_value)

    return {"status": status_str, "schedule": schedule, "metadata": metadata}
