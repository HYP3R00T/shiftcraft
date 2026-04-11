"""Tests for engine/solver.py — solve() and build_model()."""

from __future__ import annotations

import pytest
from shiftcraft_core.engine.solver import build_model, solve
from shiftcraft_core.parser.loader import load


def _payload(rules: list | None = None) -> dict:
    return {
        "settings": {
            "shifts": ["morning", "afternoon", "night"],
            "leave_types": ["week_off"],
            "rules": rules or [],
        },
        "input": {
            "period": {"start": "2026-04-07", "end": "2026-04-09"},
            "team": [{"id": "E001", "name": "Alice"}, {"id": "E002", "name": "Bob"}],
        },
    }


@pytest.mark.unit
def test_solve_returns_optimal_or_feasible():
    result = solve(_payload())
    assert result["status"] in ("optimal", "feasible")


@pytest.mark.unit
def test_solve_schedule_has_correct_shape():
    result = solve(_payload())
    assert len(result["schedule"]) == 3  # 3 days
    for emp_map in result["schedule"].values():
        assert set(emp_map.keys()) == {"E001", "E002"}


@pytest.mark.unit
def test_solve_metadata_present():
    result = solve(_payload())
    assert "solve_time_seconds" in result["metadata"]
    assert result["metadata"]["solve_time_seconds"] >= 0


@pytest.mark.unit
def test_solve_infeasible_returns_infeasible_status():
    # Require 3 mornings per day with only 2 employees → infeasible.
    result = solve(
        _payload(
            rules=[
                {
                    "id": "r1",
                    "type": "daily_count",
                    "value": "morning",
                    "operator": ">=",
                    "count": 3,
                    "scope": {"who": {"type": "all"}, "when": {"type": "always"}},
                    "enforcement": "hard",
                }
            ]
        )
    )
    assert result["status"] == "infeasible"
    assert result["schedule"] == {}


@pytest.mark.unit
def test_build_model_returns_model_and_vars():
    settings, inp = load(_payload())
    from ortools.sat.python import cp_model

    model, vd = build_model(settings, inp)
    assert isinstance(model, cp_model.CpModel)
    assert "x" in vd
    assert "penalties" in vd
