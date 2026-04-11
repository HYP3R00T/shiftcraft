"""Solver orchestration: build model → solve → return result dict."""

from __future__ import annotations

from typing import Any

from ortools.sat.python import cp_model

from .dispatch import apply_rules
from .objective import add_history_bias
from .variables import create_variables
from ..formatter import format_solution
from ..parser import load
from ..types.input import ScheduleInput
from ..types.rules import Settings

_DEFAULT_TIME_LIMIT = 30


def _apply_hint(
    model: cp_model.CpModel,
    vars_dict: dict[str, Any],
    hint: dict[str, dict[str, str]],
) -> None:
    """
    Seed the solver with a warm-start hint from a previous schedule.

    ``hint`` is a date-keyed schedule: ``{date_iso: {emp_id: state}}``.
    For each hinted cell, the matching variable is set to 1 and all other
    state variables for that cell are set to 0.  The solver is free to
    deviate — this only guides the initial search direction.
    """
    x = vars_dict["x"]
    states = vars_dict["states"]
    for d_iso, emp_map in hint.items():
        for emp_id, hinted_state in emp_map.items():
            for s in states:
                var = x.get((emp_id, d_iso, s))
                if var is not None:
                    model.add_hint(var, 1 if s == hinted_state else 0)


def build_model(
    settings: Settings,
    inp: ScheduleInput,
) -> tuple[cp_model.CpModel, dict[str, Any]]:
    """
    Construct the full CP-SAT model.

    Returns ``(model, vars_dict)`` where ``vars_dict`` also contains the
    accumulated ``penalties`` list used by soft-constraint handlers.
    """
    model = cp_model.CpModel()
    vars_dict = create_variables(model, inp)
    vars_dict["penalties"] = []

    apply_rules(model, settings, inp, vars_dict)
    add_history_bias(model, inp, vars_dict)

    if vars_dict["penalties"]:
        model.minimize(cp_model.LinearExpr.sum(vars_dict["penalties"]))

    return model, vars_dict


def solve(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Main entry point.

    Args:
        payload: Raw JSON dict with top-level keys ``"settings"`` and ``"input"``.

    Returns:
        Result dict with keys ``"status"``, ``"schedule"``, ``"metadata"``.
    """
    settings, inp = load(payload)

    model, vars_dict = build_model(settings, inp)

    # Optional warm-start hint — a previous schedule in date-keyed format.
    hint = payload.get("hint")
    if hint:
        _apply_hint(model, vars_dict, hint)

    solver = cp_model.CpSolver()
    time_limit = settings.solver.get("time_limit_seconds", _DEFAULT_TIME_LIMIT)
    solver.parameters.max_time_in_seconds = float(time_limit)
    solver.parameters.log_search_progress = bool(settings.solver.get("log_progress", False))
    # Use all available cores — CP-SAT parallelises search across workers.
    num_workers = settings.solver.get("num_workers", 0)  # 0 = auto-detect
    if num_workers:
        solver.parameters.num_workers = int(num_workers)
    # Linearisation level 1 is faster for scheduling problems with many
    # Boolean variables; level 2 (default) adds cuts that help optimality
    # proofs but slow down finding the first feasible solution.
    solver.parameters.linearization_level = settings.solver.get("linearization_level", 1)
    # Stop as soon as a solution within this relative gap of optimal is found.
    # 0.0 = prove optimality; small values (e.g. 0.05) trade proof for speed.
    relative_gap = settings.solver.get("relative_gap_limit", 0.0)
    if relative_gap > 0.0:
        solver.parameters.relative_gap_limit = float(relative_gap)

    status = solver.solve(model)

    return format_solution(status, solver, inp, vars_dict)
