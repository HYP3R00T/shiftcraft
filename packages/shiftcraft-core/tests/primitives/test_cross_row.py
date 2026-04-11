"""Tests for primitives/cross_row.py — person_dependency."""

from __future__ import annotations

import pytest
from ortools.sat.python import cp_model
from shiftcraft_core.primitives.cell import handle_value_assignment
from shiftcraft_core.primitives.cross_row import handle_person_dependency
from shiftcraft_core.types.rules import Rule, RuleEnforcement, Scope, WhenFilter, WhoFilter

from ..conftest import get_assignment, make_employee, make_model, make_schedule_input, solve


def _rule(**params) -> Rule:
    return Rule(
        id="r1",
        type="person_dependency",
        scope=Scope(who=WhoFilter(type="all"), when=WhenFilter(type="always")),
        enforcement=RuleEnforcement.HARD,
        params=params,
    )


def _force(model, vd, emp, inp, d, state):
    rule = Rule(
        id=f"force_{d}_{state}",
        type="value_assignment",
        scope=Scope(who=WhoFilter(type="all"), when=WhenFilter(type="always")),
        enforcement=RuleEnforcement.HARD,
        params={"value": state},
    )
    handle_value_assignment(model, rule, [emp], [d], inp, vd)


@pytest.mark.unit
def test_if_a_off_b_must_work():
    alice, bob = make_employee("E001"), make_employee("E002")
    inp = make_schedule_input([alice, bob], days=1)
    model, vd = make_model(inp)
    _force(model, vd, alice, inp, inp.dates[0], "week_off")
    handle_person_dependency(
        model,
        _rule(
            employee_a="E001",
            employee_b="E002",
            if_values=["week_off"],
            then_values=["morning", "afternoon", "night"],
        ),
        [alice, bob],
        inp.dates,
        inp,
        vd,
    )
    solver, status = solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
    assert get_assignment(solver, vd, bob.id, inp.dates[0]) in ("morning", "afternoon", "night")


@pytest.mark.unit
def test_infeasible_when_both_forced_off():
    alice, bob = make_employee("E001"), make_employee("E002")
    inp = make_schedule_input([alice, bob], days=1)
    model, vd = make_model(inp)
    _force(model, vd, alice, inp, inp.dates[0], "week_off")
    _force(model, vd, bob, inp, inp.dates[0], "week_off")
    handle_person_dependency(
        model,
        _rule(
            employee_a="E001",
            employee_b="E002",
            if_values=["week_off"],
            then_values=["morning", "afternoon", "night"],
        ),
        [alice, bob],
        inp.dates,
        inp,
        vd,
    )
    _, status = solve(model)
    assert status == cp_model.INFEASIBLE


@pytest.mark.unit
def test_does_not_fire_when_condition_not_met():
    alice, bob = make_employee("E001"), make_employee("E002")
    inp = make_schedule_input([alice, bob], days=1)
    model, vd = make_model(inp)
    _force(model, vd, alice, inp, inp.dates[0], "morning")
    handle_person_dependency(
        model,
        _rule(
            employee_a="E001",
            employee_b="E002",
            if_values=["week_off"],
            then_values=["morning", "afternoon", "night"],
        ),
        [alice, bob],
        inp.dates,
        inp,
        vd,
    )
    _, status = solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
