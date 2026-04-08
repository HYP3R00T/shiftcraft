"""
Cell-level primitives
  - value_assignment
  - value_exclusion
"""

from __future__ import annotations

from datetime import date
from typing import Any

from ortools.sat.python import cp_model

from ._util import iso
from ..types.input import Employee, ScheduleInput
from ..types.rules import Rule, RuleEnforcement


def handle_value_assignment(
    model: cp_model.CpModel,
    rule: Rule,
    employees: list[Employee],
    dates: list[date],
    inp: ScheduleInput,
    vars_dict: dict[str, Any],
) -> None:
    """Force or prefer a specific state for each (employee, day) in scope."""
    x = vars_dict["x"]
    value: str = rule.params["value"]
    penalty = rule.penalty()

    for emp in employees:
        for d in dates:
            var = x.get((emp.id, iso(d), value))
            if var is None:
                continue
            if rule.enforcement == RuleEnforcement.HARD:
                model.add(var == 1)
            else:
                # Soft: penalise if the cell is NOT this value.
                not_var = model.new_bool_var(f"not_{var.name}")
                model.add_bool_xor([var, not_var])
                vars_dict["penalties"].append(penalty * not_var)


def handle_value_exclusion(
    model: cp_model.CpModel,
    rule: Rule,
    employees: list[Employee],
    dates: list[date],
    inp: ScheduleInput,
    vars_dict: dict[str, Any],
) -> None:
    """Block one or more states for each (employee, day) in scope."""
    x = vars_dict["x"]
    values: list[str] = rule.params["values"]
    penalty = rule.penalty()

    for emp in employees:
        for d in dates:
            for value in values:
                var = x.get((emp.id, iso(d), value))
                if var is None:
                    continue
                if rule.enforcement == RuleEnforcement.HARD:
                    model.add(var == 0)
                else:
                    vars_dict["penalties"].append(penalty * var)
