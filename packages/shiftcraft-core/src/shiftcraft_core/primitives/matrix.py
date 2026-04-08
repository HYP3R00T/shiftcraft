"""
Matrix-level primitive
  - spread_across_team
"""

from __future__ import annotations

from datetime import date
from typing import Any

from ortools.sat.python import cp_model

from ._util import iso
from ..scope.filters import filter_when
from ..types.input import Employee, ScheduleInput
from ..types.rules import Rule, WhenFilter


def handle_spread_across_team(
    model: cp_model.CpModel,
    rule: Rule,
    employees: list[Employee],
    dates: list[date],
    inp: ScheduleInput,
    vars_dict: dict[str, Any],
) -> None:
    """
    Across all employees in scope, the difference between the max and min
    count of ``value`` (optionally filtered by ``count_when``) must be at
    most ``max_diff``.
    """
    x = vars_dict["x"]
    value: str = rule.params["value"]
    max_diff: int = rule.params["max_diff"]
    penalty = rule.penalty()

    # Optional day filter.
    count_when_raw = rule.params.get("count_when")
    if count_when_raw:
        count_when = WhenFilter(**count_when_raw) if isinstance(count_when_raw, dict) else count_when_raw
        filtered = set(filter_when(count_when, inp))
        count_dates = [d for d in dates if d in filtered]
    else:
        count_dates = dates

    if not count_dates or not employees:
        return

    counts = []
    for emp in employees:
        cnt = model.new_int_var(0, len(count_dates), f"team_spread_{emp.id}")
        model.add(
            cnt
            == cp_model.LinearExpr.sum([
                x[(emp.id, iso(d), value)] for d in count_dates if (emp.id, iso(d), value) in x
            ])
        )
        counts.append(cnt)

    if len(counts) < 2:
        return

    max_cnt = model.new_int_var(0, len(count_dates), "team_spread_max")
    min_cnt = model.new_int_var(0, len(count_dates), "team_spread_min")
    model.add_max_equality(max_cnt, counts)
    model.add_min_equality(min_cnt, counts)
    diff = model.new_int_var(0, len(count_dates), "team_spread_diff")
    model.add(diff == max_cnt - min_cnt)

    slack = model.new_int_var(0, len(count_dates), "team_spread_slack")
    model.add(slack >= diff - max_diff)
    model.add(slack >= 0)
    vars_dict["penalties"].append(penalty * slack)
