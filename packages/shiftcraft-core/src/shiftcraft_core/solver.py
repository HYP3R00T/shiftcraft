"""Solver execution and orchestration."""

from __future__ import annotations

from typing import Any

from ortools.sat.python import cp_model

from .constants import SOLVER_TIME_LIMIT_SECONDS
from .constraints import add_constraints
from .diagnostics import diagnose_conflicts
from .formatter import format_solution
from .objective import add_objective
from .parser import load
from .types import ScheduleInput
from .variables import create_variables


def solve(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Main entry point: solve the scheduling problem.

    Args:
        payload: Raw JSON dict containing period, team, coverage, and holidays.

    Returns:
        Dictionary with solution status, schedule, summary, and penalty (or conflicts).
    """
    # Parse input
    inp = load(payload)

    # Build model
    model, vars_dict = build_model(inp)

    # Solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = SOLVER_TIME_LIMIT_SECONDS
    solver.parameters.log_search_progress = True

    status = solver.solve(model)

    # Handle infeasibility
    if status == cp_model.INFEASIBLE:
        conflicts = diagnose_conflicts(inp)
        return format_solution(status, solver, inp, vars_dict, conflicts)

    # Handle timeout
    if status == cp_model.UNKNOWN:
        return format_solution(
            status,
            solver,
            inp,
            vars_dict,
            ["Solver timed out without finding a feasible solution."],
        )

    # Return solution
    return format_solution(status, solver, inp, vars_dict)


def build_model(inp: ScheduleInput) -> tuple[cp_model.CpModel, dict[str, Any]]:
    """
    Build the complete CP-SAT model with variables, constraints, and objective.

    Args:
        inp: The parsed schedule input.

    Returns:
        Tuple of (model, vars_dict) where vars_dict contains all decision variables
        and metadata needed for solution formatting.
    """
    model = cp_model.CpModel()

    # Create decision variables
    vars_dict = create_variables(model, inp)

    # Add hard constraints
    add_constraints(model, inp, vars_dict)

    # Add soft constraints (objective function)
    add_objective(model, inp, vars_dict)

    return model, vars_dict


# Made with Bob
