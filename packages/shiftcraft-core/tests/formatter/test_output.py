"""Tests for formatter/output.py — format_solution()."""

from __future__ import annotations

import pytest
from ortools.sat.python import cp_model
from shiftcraft_core.engine.solver import build_model
from shiftcraft_core.formatter.output import format_solution
from shiftcraft_core.parser.loader import load


def _payload() -> dict:
    return {
        "settings": {
            "shifts": ["morning", "afternoon", "night"],
            "leave_types": ["week_off"],
            "rules": [],
        },
        "input": {
            "period": {"start": "2026-04-07", "end": "2026-04-08"},
            "team": [{"id": "E001", "name": "Alice"}],
        },
    }


@pytest.mark.unit
def test_format_solution_optimal_shape():
    settings, inp = load(_payload())
    model, vd = build_model(settings, inp)
    solver = cp_model.CpSolver()
    status = solver.solve(model)
    result = format_solution(status, solver, inp, vd)
    assert result["status"] in ("optimal", "feasible")
    assert "2026-04-07" in result["schedule"]
    assert "E001" in result["schedule"]["2026-04-07"]


@pytest.mark.unit
def test_format_solution_schedule_is_date_keyed():
    settings, inp = load(_payload())
    model, vd = build_model(settings, inp)
    solver = cp_model.CpSolver()
    status = solver.solve(model)
    result = format_solution(status, solver, inp, vd)
    dates = list(result["schedule"].keys())
    assert dates == sorted(dates)


@pytest.mark.unit
def test_format_solution_infeasible_returns_empty_schedule():
    settings, inp = load(_payload())
    model, vd = build_model(settings, inp)
    # Force infeasibility: require 5 mornings with 1 employee.
    model.add(cp_model.LinearExpr.sum([vd["x"][("E001", d, "morning")] for d in vd["date_isos"]]) >= 5)
    solver = cp_model.CpSolver()
    status = solver.solve(model)
    result = format_solution(status, solver, inp, vd)
    assert result["status"] == "infeasible"
    assert result["schedule"] == {}


@pytest.mark.unit
def test_format_solution_metadata_solve_time():
    settings, inp = load(_payload())
    model, vd = build_model(settings, inp)
    solver = cp_model.CpSolver()
    status = solver.solve(model)
    result = format_solution(status, solver, inp, vd)
    assert result["metadata"]["solve_time_seconds"] >= 0
