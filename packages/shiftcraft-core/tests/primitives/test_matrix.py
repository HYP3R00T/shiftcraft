"""Tests for primitives/matrix.py — spread_across_team."""

from __future__ import annotations

import pytest
from ortools.sat.python import cp_model
from shiftcraft_core.primitives.matrix import handle_spread_across_team
from shiftcraft_core.types.rules import Rule, RuleEnforcement, RuleWeight, Scope, WhenFilter, WhoFilter

from ..conftest import make_employee, make_model, make_schedule_input, solve


def _rule(weight: str = "medium", **params) -> Rule:
    return Rule(
        id="r1",
        type="spread_across_team",
        scope=Scope(who=WhoFilter(type="all"), when=WhenFilter(type="always")),
        enforcement=RuleEnforcement.SOFT,
        weight=RuleWeight(weight),
        params=params,
    )


@pytest.mark.unit
def test_adds_penalty_term():
    emps = [make_employee(f"E00{i}") for i in range(1, 4)]
    inp = make_schedule_input(emps, start="2026-04-06", days=7)
    model, vd = make_model(inp)
    handle_spread_across_team(model, _rule(value="night", max_diff=1), emps, inp.dates, inp, vd)
    assert len(vd["penalties"]) > 0


@pytest.mark.unit
def test_feasible_with_penalty():
    emps = [make_employee(f"E00{i}") for i in range(1, 3)]
    inp = make_schedule_input(emps, days=7)
    model, vd = make_model(inp)
    handle_spread_across_team(model, _rule(weight="low", value="night", max_diff=2), emps, inp.dates, inp, vd)
    if vd["penalties"]:
        model.minimize(cp_model.LinearExpr.sum(vd["penalties"]))
    _, status = solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
