"""Tests for engine/dispatch.py — apply_rules()."""

from __future__ import annotations

import pytest
from ortools.sat.python import cp_model
from shiftcraft_core.engine.dispatch import apply_rules
from shiftcraft_core.engine.variables import create_variables
from shiftcraft_core.types.rules import Rule, RuleEnforcement, Scope, Settings, WhenFilter, WhoFilter

from ..conftest import make_employee, make_schedule_input, solve


def _settings(rules: list[Rule]) -> Settings:
    return Settings(
        shifts=["morning", "afternoon", "night"],
        leave_types=["week_off"],
        rules=rules,
    )


def _rule(**params) -> Rule:
    return Rule(
        id="r1",
        type="daily_count",
        scope=Scope(who=WhoFilter(type="all"), when=WhenFilter(type="always")),
        enforcement=RuleEnforcement.HARD,
        params=params,
    )


@pytest.mark.unit
def test_dispatch_applies_rule_to_model():
    emp = make_employee()
    inp = make_schedule_input([emp], days=1)
    model = cp_model.CpModel()
    vd = create_variables(model, inp)
    vd["penalties"] = []
    settings = _settings([_rule(value="morning", operator=">=", count=1)])
    apply_rules(model, settings, inp, vd)
    _, status = solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)


@pytest.mark.unit
def test_dispatch_unknown_rule_type_raises():
    emp = make_employee()
    inp = make_schedule_input([emp], days=1)
    model = cp_model.CpModel()
    vd = create_variables(model, inp)
    vd["penalties"] = []
    settings = _settings([
        Rule(
            id="r1",
            type="nonexistent_primitive",
            scope=Scope(who=WhoFilter(type="all"), when=WhenFilter(type="always")),
            enforcement=RuleEnforcement.HARD,
            params={},
        )
    ])
    with pytest.raises(NotImplementedError):
        apply_rules(model, settings, inp, vd)


@pytest.mark.unit
def test_dispatch_empty_rules_is_noop():
    emp = make_employee()
    inp = make_schedule_input([emp], days=1)
    model = cp_model.CpModel()
    vd = create_variables(model, inp)
    vd["penalties"] = []
    apply_rules(model, _settings([]), inp, vd)
    _, status = solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
