"""Tests for cell-level primitives: value_assignment, value_exclusion."""

from __future__ import annotations

import pytest
from ortools.sat.python import cp_model
from shiftcraft_core.primitives.cell import handle_value_assignment, handle_value_exclusion
from shiftcraft_core.types.rules import Rule, RuleEnforcement, Scope, WhenFilter, WhoFilter

from ..conftest import get_assignment, make_employee, make_model, make_schedule_input, solve


def _rule(rule_type: str, enforcement: str, **params) -> Rule:
    return Rule(
        id="r1",
        type=rule_type,
        scope=Scope(who=WhoFilter(type="all"), when=WhenFilter(type="always")),
        enforcement=RuleEnforcement(enforcement),
        params=params,
    )


# ── value_assignment (hard) ───────────────────────────────────────────────────


@pytest.mark.unit
def test_hard_assignment_forces_state():
    emp = make_employee()
    inp = make_schedule_input([emp], days=1)
    model, vd = make_model(inp)
    rule = _rule("value_assignment", "hard", value="morning")
    handle_value_assignment(model, rule, [emp], inp.dates, inp, vd)
    solver, status = solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
    assert get_assignment(solver, vd, emp.id, inp.dates[0]) == "morning"


@pytest.mark.unit
def test_hard_assignment_infeasible_when_conflicting():
    """Two hard assignments to different states on the same cell → infeasible."""
    emp = make_employee()
    inp = make_schedule_input([emp], days=1)
    model, vd = make_model(inp)
    d = inp.dates[0]
    # Force morning AND afternoon on the same day — impossible.
    for state in ("morning", "afternoon"):
        rule = _rule("value_assignment", "hard", value=state)
        handle_value_assignment(model, rule, [emp], [d], inp, vd)
    _, status = solve(model)
    assert status == cp_model.INFEASIBLE


# ── value_assignment (soft) ───────────────────────────────────────────────────


@pytest.mark.unit
def test_soft_assignment_adds_penalty_when_violated():
    emp = make_employee()
    inp = make_schedule_input([emp], days=1)
    model, vd = make_model(inp)
    # Hard-force afternoon, then soft-prefer morning — penalty must be > 0.
    hard = _rule("value_assignment", "hard", value="afternoon")
    handle_value_assignment(model, hard, [emp], inp.dates, inp, vd)
    soft = Rule(
        id="r2",
        type="value_assignment",
        scope=Scope(who=WhoFilter(type="all"), when=WhenFilter(type="always")),
        enforcement=RuleEnforcement.PREFERENCE,
        params={"value": "morning"},
    )
    handle_value_assignment(model, soft, [emp], inp.dates, inp, vd)
    assert len(vd["penalties"]) > 0


# ── value_exclusion (hard) ────────────────────────────────────────────────────


@pytest.mark.unit
def test_hard_exclusion_blocks_state():
    emp = make_employee()
    inp = make_schedule_input([emp], days=3)
    model, vd = make_model(inp)
    # Exclude morning, afternoon, night — only week_off remains.
    rule = _rule("value_exclusion", "hard", values=["morning", "afternoon", "night"])
    handle_value_exclusion(model, rule, [emp], inp.dates, inp, vd)
    solver, status = solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
    for d in inp.dates:
        assert get_assignment(solver, vd, emp.id, d) == "week_off"


@pytest.mark.unit
def test_hard_exclusion_all_states_infeasible():
    emp = make_employee()
    inp = make_schedule_input([emp], days=1)
    model, vd = make_model(inp)
    rule = _rule("value_exclusion", "hard", values=["morning", "afternoon", "night", "week_off"])
    handle_value_exclusion(model, rule, [emp], inp.dates, inp, vd)
    _, status = solve(model)
    assert status == cp_model.INFEASIBLE


# ── value_exclusion (soft) ────────────────────────────────────────────────────


@pytest.mark.unit
def test_soft_exclusion_adds_penalty():
    emp = make_employee()
    inp = make_schedule_input([emp], days=1)
    model, vd = make_model(inp)
    # Hard-force morning, then soft-exclude morning — penalty must fire.
    hard = _rule("value_assignment", "hard", value="morning")
    handle_value_assignment(model, hard, [emp], inp.dates, inp, vd)
    soft = Rule(
        id="r2",
        type="value_exclusion",
        scope=Scope(who=WhoFilter(type="all"), when=WhenFilter(type="always")),
        enforcement=RuleEnforcement.PREFERENCE,
        params={"values": ["morning"]},
    )
    handle_value_exclusion(model, soft, [emp], inp.dates, inp, vd)
    assert len(vd["penalties"]) > 0
