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

    solver = cp_model.CpSolver()
    time_limit = settings.solver.get("time_limit_seconds", _DEFAULT_TIME_LIMIT)
    solver.parameters.max_time_in_seconds = float(time_limit)
    solver.parameters.log_search_progress = bool(settings.solver.get("log_progress", False))

    status = solver.solve(model)

    return format_solution(status, solver, inp, vars_dict)
