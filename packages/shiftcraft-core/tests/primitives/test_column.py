"""Tests for column-level primitives: daily_count, daily_ratio, daily_conditional."""

from __future__ import annotations

import pytest
from ortools.sat.python import cp_model
from shiftcraft_core.primitives.cell import handle_value_assignment
from shiftcraft_core.primitives.column import (
    handle_daily_conditional,
    handle_daily_count,
    handle_daily_ratio,
)
from shiftcraft_core.types.rules import Rule, RuleEnforcement, Scope, WhenFilter, WhoFilter

from ..conftest import get_assignment, make_employee, make_model, make_schedule_input, solve


def _rule(rule_type: str, enforcement: str = "hard", **params) -> Rule:
    return Rule(
        id="r1",
        type=rule_type,
        scope=Scope(who=WhoFilter(type="all"), when=WhenFilter(type="always")),
        enforcement=RuleEnforcement(enforcement),
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


# ── daily_count ───────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_daily_count_minimum_coverage():
    """At least 1 morning per day across 2 employees."""
    emps = [make_employee("E001"), make_employee("E002")]
    inp = make_schedule_input(emps, days=3)
    model, vd = make_model(inp)
    rule = _rule("daily_count", value="morning", operator=">=", count=1)
    handle_daily_count(model, rule, emps, inp.dates, inp, vd)
    solver, status = solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
    for d in inp.dates:
        morning_count = sum(1 for e in emps if get_assignment(solver, vd, e.id, d) == "morning")
        assert morning_count >= 1


@pytest.mark.unit
def test_daily_count_maximum_coverage():
    """At most 1 week_off per day across 3 employees."""
    emps = [make_employee(f"E00{i}") for i in range(1, 4)]
    inp = make_schedule_input(emps, days=3)
    model, vd = make_model(inp)
    rule = _rule("daily_count", value="week_off", operator="<=", count=1)
    handle_daily_count(model, rule, emps, inp.dates, inp, vd)
    solver, status = solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
    for d in inp.dates:
        off_count = sum(1 for e in emps if get_assignment(solver, vd, e.id, d) == "week_off")
        assert off_count <= 1


@pytest.mark.unit
def test_daily_count_infeasible_when_impossible():
    """Require 3 mornings per day with only 2 employees → infeasible."""
    emps = [make_employee("E001"), make_employee("E002")]
    inp = make_schedule_input(emps, days=1)
    model, vd = make_model(inp)
    rule = _rule("daily_count", value="morning", operator=">=", count=3)
    handle_daily_count(model, rule, emps, inp.dates, inp, vd)
    _, status = solve(model)
    assert status == cp_model.INFEASIBLE


@pytest.mark.unit
def test_daily_count_list_of_values():
    """At most 1 combined off (week_off + morning) per day."""
    emps = [make_employee("E001"), make_employee("E002")]
    inp = make_schedule_input(emps, days=2)
    model, vd = make_model(inp)
    rule = _rule("daily_count", value=["week_off", "morning"], operator="<=", count=1)
    handle_daily_count(model, rule, emps, inp.dates, inp, vd)
    solver, status = solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
    for d in inp.dates:
        combined = sum(1 for e in emps if get_assignment(solver, vd, e.id, d) in ("week_off", "morning"))
        assert combined <= 1


# ── daily_ratio ───────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_daily_ratio_senior_coverage():
    """At least 50% of working employees must be senior."""
    senior = make_employee("E001", attributes={"role": "senior"})
    junior = make_employee("E002", attributes={"role": "junior"})
    emps = [senior, junior]
    inp = make_schedule_input(emps, days=1)
    model, vd = make_model(inp)
    # Force both to morning (working).
    for e in emps:
        _force(model, vd, e, inp, inp.dates[0], "morning")
    rule = Rule(
        id="r1",
        type="daily_ratio",
        scope=Scope(who=WhoFilter(type="all"), when=WhenFilter(type="always")),
        enforcement=RuleEnforcement.HARD,
        params={
            "value": "morning",
            "numerator_who": {"type": "attribute", "key": "role", "value": "senior"},
            "operator": ">=",
            "ratio": 0.5,
            "exclude_values": [],
        },
    )
    handle_daily_ratio(model, rule, emps, inp.dates, inp, vd)
    solver, status = solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)


# ── daily_conditional ─────────────────────────────────────────────────────────


@pytest.mark.unit
def test_daily_conditional_fires_when_condition_met():
    """If >= 2 employees on morning, at least 1 must be senior."""
    senior = make_employee("E001", attributes={"role": "senior"})
    junior1 = make_employee("E002", attributes={"role": "junior"})
    junior2 = make_employee("E003", attributes={"role": "junior"})
    emps = [senior, junior1, junior2]
    inp = make_schedule_input(emps, days=1)
    model, vd = make_model(inp)
    # Force all 3 to morning.
    for e in emps:
        _force(model, vd, e, inp, inp.dates[0], "morning")
    rule = Rule(
        id="r1",
        type="daily_conditional",
        scope=Scope(who=WhoFilter(type="all"), when=WhenFilter(type="always")),
        enforcement=RuleEnforcement.HARD,
        params={
            "if_value": "morning",
            "if_who": {"type": "all"},
            "if_operator": ">=",
            "if_count": 2,
            "then_value": "morning",
            "then_who": {"type": "attribute", "key": "role", "value": "senior"},
            "then_operator": ">=",
            "then_count": 1,
        },
    )
    handle_daily_conditional(model, rule, emps, inp.dates, inp, vd)
    solver, status = solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
    assert get_assignment(solver, vd, senior.id, inp.dates[0]) == "morning"
