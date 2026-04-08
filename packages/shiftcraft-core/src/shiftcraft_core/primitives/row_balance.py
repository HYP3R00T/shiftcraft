"""
Row-level balance primitive
  - spread_per_employee
"""

from __future__ import annotations

from datetime import date
from typing import Any

from ortools.sat.python import cp_model

from ._util import iso
from ..types.input import Employee, ScheduleInput
from ..types.rules import Rule


def handle_spread_per_employee(
    model: cp_model.CpModel,
    rule: Rule,
    employees: list[Employee],
    dates: list[date],
    inp: ScheduleInput,
    vars_dict: dict[str, Any],
) -> None:
    """
    For each employee, the difference between the max and min count of any
    state in ``values`` across *dates* must be at most ``max_diff``.
    """
    x = vars_dict["x"]
    values: list[str] = rule.params["values"]
    max_diff: int = rule.params["max_diff"]
    penalty = rule.penalty()

    for emp in employees:
        counts = []
        for s in values:
            cnt = model.new_int_var(0, len(dates), f"spread_emp_{emp.id}_{s}")
            model.add(
                cnt == cp_model.LinearExpr.sum([x[(emp.id, iso(d), s)] for d in dates if (emp.id, iso(d), s) in x])
            )
            counts.append(cnt)

        if len(counts) < 2:
            continue

        max_cnt = model.new_int_var(0, len(dates), f"spread_max_{emp.id}")
        min_cnt = model.new_int_var(0, len(dates), f"spread_min_{emp.id}")
        model.add_max_equality(max_cnt, counts)
        model.add_min_equality(min_cnt, counts)
        diff = model.new_int_var(0, len(dates), f"spread_diff_{emp.id}")
        model.add(diff == max_cnt - min_cnt)

        # Spec says spread_per_employee is soft only.
        slack = model.new_int_var(0, len(dates), f"spread_slack_{emp.id}")
        model.add(slack >= diff - max_diff)
        model.add(slack >= 0)
        vars_dict["penalties"].append(penalty * slack)
