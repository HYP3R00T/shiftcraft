"""Tests for row-level sequence primitives: pair_sequence, run_sequence."""

from __future__ import annotations

import pytest
from ortools.sat.python import cp_model
from shiftcraft_core.primitives.cell import handle_value_assignment
from shiftcraft_core.primitives.row_sequence import handle_pair_sequence, handle_run_sequence
from shiftcraft_core.types.input import StateRun
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
    """Helper: hard-assign a state on a specific day."""
    rule = Rule(
        id=f"force_{d.isoformat()}_{state}",
        type="value_assignment",
        scope=Scope(who=WhoFilter(type="all"), when=WhenFilter(type="always")),
        enforcement=RuleEnforcement.HARD,
        params={"value": state},
    )
    handle_value_assignment(model, rule, [emp], [d], inp, vd)


# ── pair_sequence (hard, forbidden) ──────────────────────────────────────────


@pytest.mark.unit
def test_pair_sequence_forbidden_night_to_morning():
    """Night on day N → morning on day N+1 is forbidden."""
    emp = make_employee()
    inp = make_schedule_input([emp], days=3)
    model, vd = make_model(inp)
    # Force night on day 0.
    _force(model, vd, emp, inp, inp.dates[0], "night")
    rule = _rule("pair_sequence", from_value="night", to_value="morning", gap_days=1, forbidden=True)
    handle_pair_sequence(model, rule, [emp], inp.dates, inp, vd)
    solver, status = solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
    assert get_assignment(solver, vd, emp.id, inp.dates[1]) != "morning"


@pytest.mark.unit
def test_pair_sequence_forbidden_infeasible_when_no_alternative():
    """Night on day 0, only morning available on day 1 → infeasible."""
    emp = make_employee()
    inp = make_schedule_input([emp], days=2, states=["morning", "night"])
    model, vd = make_model(inp)
    _force(model, vd, emp, inp, inp.dates[0], "night")
    # Exclude everything except morning on day 1.
    from shiftcraft_core.primitives.cell import handle_value_exclusion

    excl = Rule(
        id="excl",
        type="value_exclusion",
        scope=Scope(who=WhoFilter(type="all"), when=WhenFilter(type="always")),
        enforcement=RuleEnforcement.HARD,
        params={"values": ["night"]},
    )
    handle_value_exclusion(model, excl, [emp], [inp.dates[1]], inp, vd)
    rule = _rule("pair_sequence", from_value="night", to_value="morning", gap_days=1, forbidden=True)
    handle_pair_sequence(model, rule, [emp], inp.dates, inp, vd)
    _, status = solve(model)
    assert status == cp_model.INFEASIBLE


# ── pair_sequence (hard, required) ───────────────────────────────────────────


@pytest.mark.unit
def test_pair_sequence_required_implies_next():
    """Morning on day N requires morning on day N+1."""
    emp = make_employee()
    inp = make_schedule_input([emp], days=3)
    model, vd = make_model(inp)
    _force(model, vd, emp, inp, inp.dates[0], "morning")
    rule = _rule("pair_sequence", from_value="morning", to_value="morning", gap_days=1, forbidden=False)
    handle_pair_sequence(model, rule, [emp], inp.dates, inp, vd)
    solver, status = solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
    assert get_assignment(solver, vd, emp.id, inp.dates[1]) == "morning"


# ── run_sequence (hard) ───────────────────────────────────────────────────────


@pytest.mark.unit
def test_run_sequence_triggers_after_n_consecutive():
    """After 2 consecutive nights, next day must be week_off."""
    emp = make_employee()
    inp = make_schedule_input([emp], days=5)
    model, vd = make_model(inp)
    # Force nights on days 0 and 1.
    _force(model, vd, emp, inp, inp.dates[0], "night")
    _force(model, vd, emp, inp, inp.dates[1], "night")
    rule = _rule(
        "run_sequence",
        trigger_value="night",
        trigger_count=2,
        then_value="week_off",
        then_operator=">=",
        then_count=1,
        then_days=1,
    )
    handle_run_sequence(model, rule, [emp], inp.dates, inp, vd)
    solver, status = solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
    assert get_assignment(solver, vd, emp.id, inp.dates[2]) == "week_off"


@pytest.mark.unit
def test_run_sequence_carry_over_from_previous_period():
    """
    Employee ended last period with 1 consecutive night (previous_state_run).
    trigger_count=2 → only 1 more night this period triggers the rule.
    """
    emp = make_employee(previous_state_run=StateRun(value="night", count=1))
    inp = make_schedule_input([emp], days=4)
    model, vd = make_model(inp)
    # Force night on day 0 only — combined with carry=1, that's 2 consecutive.
    _force(model, vd, emp, inp, inp.dates[0], "night")
    rule = _rule(
        "run_sequence",
        trigger_value="night",
        trigger_count=2,
        then_value="week_off",
        then_operator=">=",
        then_count=1,
        then_days=1,
    )
    handle_run_sequence(model, rule, [emp], inp.dates, inp, vd)
    solver, status = solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
    assert get_assignment(solver, vd, emp.id, inp.dates[1]) == "week_off"


@pytest.mark.unit
def test_run_sequence_does_not_trigger_without_full_run():
    """Only 1 consecutive night when trigger_count=2 → rule does not fire."""
    emp = make_employee()
    inp = make_schedule_input([emp], days=4)
    model, vd = make_model(inp)
    _force(model, vd, emp, inp, inp.dates[0], "night")
    # Force morning on day 1 to break the run.
    _force(model, vd, emp, inp, inp.dates[1], "morning")
    rule = _rule(
        "run_sequence",
        trigger_value="night",
        trigger_count=2,
        then_value="week_off",
        then_operator=">=",
        then_count=1,
        then_days=1,
    )
    handle_run_sequence(model, rule, [emp], inp.dates, inp, vd)
    solver, status = solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
    # Day 2 is free — rule didn't fire, so week_off is not forced.
    # Just verify it's still feasible (no infeasibility from the rule).
