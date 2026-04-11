"""Tests for row-level count primitives."""

from __future__ import annotations

import pytest
from ortools.sat.python import cp_model
from shiftcraft_core.primitives.row_count import (
    handle_count_bounded_by_balance,
    handle_count_per_period,
    handle_count_per_week,
    handle_count_per_window,
)
from shiftcraft_core.types.rules import BalanceSource, Rule, RuleEnforcement, Scope, WhenFilter, WhoFilter

from ..conftest import get_assignment, make_employee, make_model, make_schedule_input, solve


def _rule(rule_type: str, enforcement: str = "hard", **params) -> Rule:
    return Rule(
        id="r1",
        type=rule_type,
        scope=Scope(who=WhoFilter(type="all"), when=WhenFilter(type="always")),
        enforcement=RuleEnforcement(enforcement),
        params=params,
    )


# ── count_per_period ──────────────────────────────────────────────────────────


@pytest.mark.unit
def test_count_per_period_hard_upper_bound():
    """At most 1 week_off in 5 days."""
    emp = make_employee()
    inp = make_schedule_input([emp], start="2026-04-07", days=5)
    model, vd = make_model(inp)
    rule = _rule("count_per_period", value="week_off", operator="<=", count=1)
    handle_count_per_period(model, rule, [emp], inp.dates, inp, vd)
    solver, status = solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
    offs = sum(1 for d in inp.dates if get_assignment(solver, vd, emp.id, d) == "week_off")
    assert offs <= 1


@pytest.mark.unit
def test_count_per_period_hard_exact():
    """Exactly 2 week_offs in 7 days."""
    emp = make_employee()
    inp = make_schedule_input([emp], start="2026-04-07", days=7)
    model, vd = make_model(inp)
    rule = _rule("count_per_period", value="week_off", operator="==", count=2)
    handle_count_per_period(model, rule, [emp], inp.dates, inp, vd)
    solver, status = solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
    offs = sum(1 for d in inp.dates if get_assignment(solver, vd, emp.id, d) == "week_off")
    assert offs == 2


@pytest.mark.unit
def test_count_per_period_infeasible_when_impossible():
    """Exactly 10 week_offs in 3 days → infeasible."""
    emp = make_employee()
    inp = make_schedule_input([emp], days=3)
    model, vd = make_model(inp)
    rule = _rule("count_per_period", value="week_off", operator="==", count=10)
    handle_count_per_period(model, rule, [emp], inp.dates, inp, vd)
    _, status = solve(model)
    assert status == cp_model.INFEASIBLE


# ── count_per_week ────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_count_per_week_exactly_two():
    """Exactly 2 week_offs per ISO week across a full 2-week period."""
    emp = make_employee()
    # 2026-04-06 is Monday — two full ISO weeks
    inp = make_schedule_input([emp], start="2026-04-06", days=14)
    model, vd = make_model(inp)
    rule = _rule("count_per_week", value="week_off", operator="==", count=2)
    handle_count_per_week(model, rule, [emp], inp.dates, inp, vd)
    solver, status = solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
    from shiftcraft_core.primitives._util import week_key

    by_week: dict[str, int] = {}
    for d in inp.dates:
        wk = week_key(d)
        if get_assignment(solver, vd, emp.id, d) == "week_off":
            by_week[wk] = by_week.get(wk, 0) + 1
        else:
            by_week.setdefault(wk, 0)
    for wk, cnt in by_week.items():
        assert cnt == 2, f"Week {wk}: expected 2 week_offs, got {cnt}"


# ── count_per_window ──────────────────────────────────────────────────────────


@pytest.mark.unit
def test_count_per_window_max_working_days():
    """At most 5 working days in any 7-day window."""
    emp = make_employee()
    inp = make_schedule_input([emp], start="2026-04-06", days=14, states=["morning", "afternoon", "night", "week_off"])
    model, vd = make_model(inp)
    rule = _rule("count_per_window", values=["morning", "afternoon", "night"], window_days=7, operator="<=", count=5)
    handle_count_per_window(model, rule, [emp], inp.dates, inp, vd)
    solver, status = solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
    assignments = [get_assignment(solver, vd, emp.id, d) for d in inp.dates]
    working = {"morning", "afternoon", "night"}
    for i in range(len(assignments) - 6):
        window = assignments[i : i + 7]
        assert sum(1 for s in window if s in working) <= 5


# ── count_bounded_by_balance ──────────────────────────────────────────────────


@pytest.mark.unit
def test_bounded_by_numeric_balance_zero():
    """Employee with comp_off balance=0 cannot be assigned comp_off."""
    emp = make_employee(balances={"comp_off": 0})
    inp = make_schedule_input([emp], days=5, states=["morning", "week_off", "comp_off"])
    model, vd = make_model(inp)
    rule = Rule(
        id="r1",
        type="count_bounded_by_balance",
        scope=Scope(who=WhoFilter(type="all"), when=WhenFilter(type="always")),
        enforcement=RuleEnforcement.HARD,
        params={"value": "comp_off", "balance_source": BalanceSource(type="numeric", key="comp_off")},
    )
    handle_count_bounded_by_balance(model, rule, [emp], inp.dates, inp, vd)
    solver, status = solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
    assert all(get_assignment(solver, vd, emp.id, d) != "comp_off" for d in inp.dates)


@pytest.mark.unit
def test_bounded_by_numeric_balance_two():
    """Employee with comp_off balance=2 can use it at most twice."""
    emp = make_employee(balances={"comp_off": 2})
    inp = make_schedule_input([emp], days=5, states=["morning", "week_off", "comp_off"])
    model, vd = make_model(inp)
    rule = Rule(
        id="r1",
        type="count_bounded_by_balance",
        scope=Scope(who=WhoFilter(type="all"), when=WhenFilter(type="always")),
        enforcement=RuleEnforcement.HARD,
        params={"value": "comp_off", "balance_source": BalanceSource(type="numeric", key="comp_off")},
    )
    handle_count_bounded_by_balance(model, rule, [emp], inp.dates, inp, vd)
    solver, status = solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
    used = sum(1 for d in inp.dates if get_assignment(solver, vd, emp.id, d) == "comp_off")
    assert used <= 2


@pytest.mark.unit
def test_bounded_by_records_counts_unredeemed():
    """Employee with 2 unredeemed records can use comp_off at most twice."""
    emp = make_employee(
        records={
            "comp_off": [
                {"earned_date": "2026-01-01", "redeemed_on": None},
                {"earned_date": "2026-02-01", "redeemed_on": None},
                {"earned_date": "2026-03-01", "redeemed_on": "2026-03-15"},  # already redeemed
            ]
        }
    )
    inp = make_schedule_input([emp], days=5, states=["morning", "week_off", "comp_off"])
    model, vd = make_model(inp)
    rule = Rule(
        id="r1",
        type="count_bounded_by_balance",
        scope=Scope(who=WhoFilter(type="all"), when=WhenFilter(type="always")),
        enforcement=RuleEnforcement.HARD,
        params={"value": "comp_off", "balance_source": BalanceSource(type="records", key="comp_off")},
    )
    handle_count_bounded_by_balance(model, rule, [emp], inp.dates, inp, vd)
    solver, status = solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
    used = sum(1 for d in inp.dates if get_assignment(solver, vd, emp.id, d) == "comp_off")
    assert used <= 2
