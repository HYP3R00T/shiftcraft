"""Tests for engine/variables.py — create_variables()."""

from __future__ import annotations

import pytest
from ortools.sat.python import cp_model
from shiftcraft_core.engine.variables import create_variables

from ..conftest import make_employee, make_schedule_input


@pytest.mark.unit
def test_creates_one_var_per_employee_day_state():
    emp = make_employee()
    inp = make_schedule_input([emp], days=3)
    model = cp_model.CpModel()
    vd = create_variables(model, inp)
    expected = len(inp.employees) * len(inp.dates) * len(inp.states)
    assert len(vd["x"]) == expected


@pytest.mark.unit
def test_exactly_one_state_per_cell_is_enforced():
    """Solver must assign exactly one state per (employee, day)."""
    emp = make_employee()
    inp = make_schedule_input([emp], days=2)
    model = cp_model.CpModel()
    vd = create_variables(model, inp)
    solver = cp_model.CpSolver()
    status = solver.solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
    for d_iso in vd["date_isos"]:
        assigned = sum(solver.value(vd["x"][(emp.id, d_iso, s)]) for s in vd["states"])
        assert assigned == 1


@pytest.mark.unit
def test_vars_dict_contains_expected_keys():
    emp = make_employee()
    inp = make_schedule_input([emp], days=1)
    model = cp_model.CpModel()
    vd = create_variables(model, inp)
    assert "x" in vd
    assert "emp_ids" in vd
    assert "date_isos" in vd
    assert "states" in vd
    assert "emp_by_id" in vd


@pytest.mark.unit
def test_emp_by_id_maps_correctly():
    emp = make_employee("E001")
    inp = make_schedule_input([emp], days=1)
    model = cp_model.CpModel()
    vd = create_variables(model, inp)
    assert vd["emp_by_id"]["E001"] is emp
