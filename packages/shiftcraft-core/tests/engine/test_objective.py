"""Tests for engine/objective.py — add_history_bias()."""

from __future__ import annotations

import pytest
from ortools.sat.python import cp_model
from shiftcraft_core.engine.objective import add_history_bias

from ..conftest import make_employee, make_model, make_schedule_input


@pytest.mark.unit
def test_history_bias_adds_penalties_for_overrepresented_states():
    emp = make_employee(last_month_shift_counts={"night": 10, "morning": 2})
    inp = make_schedule_input([emp], days=5)
    model, vd = make_model(inp)
    add_history_bias(model, inp, vd)
    assert len(vd["penalties"]) > 0


@pytest.mark.unit
def test_history_bias_no_penalties_when_no_history():
    emp = make_employee()  # empty last_month_shift_counts
    inp = make_schedule_input([emp], days=5)
    model, vd = make_model(inp)
    add_history_bias(model, inp, vd)
    assert len(vd["penalties"]) == 0


@pytest.mark.unit
def test_history_bias_feasible():
    emp = make_employee(last_month_shift_counts={"morning": 8, "night": 3})
    inp = make_schedule_input([emp], days=5)
    model, vd = make_model(inp)
    add_history_bias(model, inp, vd)
    if vd["penalties"]:
        model.minimize(cp_model.LinearExpr.sum(vd["penalties"]))
    solver = cp_model.CpSolver()
    status = solver.solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
