"""Format CP-SAT solution into the output JSON structure."""

from __future__ import annotations

from typing import Any

from ortools.sat.python import cp_model

from .constants import SHIFTS
from .types import ScheduleInput


def format_solution(
    status: cp_model.CpSolverStatus,
    solver: cp_model.CpSolver,
    inp: ScheduleInput,
    vars_dict: dict[str, Any],
    conflict_reasons: list[str] | None = None,
) -> dict[str, Any]:
    """
    Build the output dict from solver results.

    Args:
        status: CP-SAT solver status code.
        solver: The CP-SAT solver instance.
        inp: The parsed schedule input.
        vars_dict: Dictionary containing decision variables and metadata.
        conflict_reasons: Optional list of conflict explanations for infeasible solutions.

    Returns:
        On failure:
          {"status": "infeasible", "conflicts": [...]}

        On success:
          {
            "status": "ok" | "feasible",
            "schedule": [{"date": ..., "<name>": "<shift|week_off|annual|comp_off>"}, ...],
            "summary": {"<name>": {"morning": n, "afternoon": n, ...}, ...},
            "penalty": <int>
          }
    """
    if status in (cp_model.INFEASIBLE, cp_model.UNKNOWN):
        return {
            "status": "infeasible",
            "conflicts": conflict_reasons or ["No feasible roster found. Check constraints."],
        }

    shift_vars = vars_dict["shift_vars"]
    leave_vars = vars_dict["leave_vars"]
    emp_ids: list[str] = vars_dict["emp_ids"]
    emp_by_id = vars_dict["emp_by_id"]

    leave_types = ("week_off", "annual", "comp_off")

    # ── Per-employee summary counters ─────────────────────────────────────────
    summary: dict[str, dict[str, int]] = {
        emp_by_id[eid].name: dict.fromkeys((*SHIFTS, "week_off", "annual", "comp_off"), 0) for eid in emp_ids
    }

    # ── Day-by-day schedule rows ──────────────────────────────────────────────
    schedule: list[dict[str, str]] = []

    for d in inp.dates:
        diso = d.isoformat()
        row: dict[str, str] = {"date": diso}

        for eid in emp_ids:
            name = emp_by_id[eid].name
            assignment = "?"

            # Check shifts
            for shift in SHIFTS:
                if solver.value(shift_vars[(eid, diso, shift)]) == 1:
                    assignment = shift
                    summary[name][shift] += 1
                    break

            # Check leave types if not on a shift
            if assignment == "?":
                for lt in leave_types:
                    if solver.value(leave_vars[(eid, diso, lt)]) == 1:
                        assignment = lt
                        summary[name][lt] += 1
                        break

            row[name] = assignment

        schedule.append(row)

    penalty = int(solver.objective_value) if status == cp_model.OPTIMAL else int(solver.best_objective_bound)

    return {
        "status": "ok" if status == cp_model.OPTIMAL else "feasible",
        "schedule": schedule,
        "summary": summary,
        "penalty": penalty,
    }


# Made with Bob
