"""Tests for primitives/row_balance.py — spread_per_employee."""

from __future__ import annotations

import pytest
from ortools.sat.python import cp_model
from shiftcraft_core.primitives.row_balance import handle_spread_per_employee
from shiftcraft_core.types.rules import Rule, RuleEnforcement, RuleWeight, Scope, WhenFilter, WhoFilter

from ..conftest import make_employee, make_model, make_schedule_input, solve


def _rule(weight: str = "medium", **params) -> Rule:
    return Rule(
        id="r1",
        type="spread_per_employee",
        scope=Scope(who=WhoFilter(type="all"), when=WhenFilter(type="always")),
        enforcement=RuleEnforcement.SOFT,
        weight=RuleWeight(weight),
        params=params,
    )


@pytest.mark.unit
def test_adds_penalty_term():
    emp = make_employee()
    inp = make_schedule_input([emp], days=7)
    model, vd = make_model(inp)
    handle_spread_per_employee(
        model, _rule(values=["morning", "afternoon", "night"], max_diff=1), [emp], inp.dates, inp, vd
    )
    assert len(vd["penalties"]) > 0


@pytest.mark.unit
def test_feasible_with_penalty():
    emp = make_employee()
    inp = make_schedule_input([emp], days=9)
    model, vd = make_model(inp)
    handle_spread_per_employee(
        model, _rule(weight="low", values=["morning", "afternoon", "night"], max_diff=1), [emp], inp.dates, inp, vd
    )
    if vd["penalties"]:
        model.minimize(cp_model.LinearExpr.sum(vd["penalties"]))
    _, status = solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
