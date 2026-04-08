"""
Cross-row primitive
  - person_dependency
"""

from __future__ import annotations

from datetime import date
from typing import Any

from ortools.sat.python import cp_model

from ._util import iso
from ..types.input import Employee, ScheduleInput
from ..types.rules import Rule, RuleEnforcement


def handle_person_dependency(
    model: cp_model.CpModel,
    rule: Rule,
    employees: list[Employee],
    dates: list[date],
    inp: ScheduleInput,
    vars_dict: dict[str, Any],
) -> None:
    """
    If employee A's state is in ``if_values`` on day d,
    employee B's state must be in ``then_values``.
    """
    x = vars_dict["x"]
    emp_a_id: str = rule.params["employee_a"]
    emp_b_id: str = rule.params["employee_b"]
    if_values: list[str] = rule.params["if_values"]
    then_values: list[str] = rule.params["then_values"]
    penalty = rule.penalty()

    for d in dates:
        # a_triggered: True iff A is in one of if_values.
        a_vars = [x[(emp_a_id, iso(d), v)] for v in if_values if (emp_a_id, iso(d), v) in x]
        if not a_vars:
            continue

        a_triggered = model.new_bool_var(f"dep_a_{rule.id}_{iso(d)}")
        model.add(cp_model.LinearExpr.sum(a_vars) >= 1).only_enforce_if(a_triggered)
        model.add(cp_model.LinearExpr.sum(a_vars) == 0).only_enforce_if(a_triggered.negated())

        # b_satisfied: True iff B is in one of then_values.
        b_vars = [x[(emp_b_id, iso(d), v)] for v in then_values if (emp_b_id, iso(d), v) in x]
        if not b_vars:
            continue

        b_satisfied = model.new_bool_var(f"dep_b_{rule.id}_{iso(d)}")
        model.add(cp_model.LinearExpr.sum(b_vars) >= 1).only_enforce_if(b_satisfied)
        model.add(cp_model.LinearExpr.sum(b_vars) == 0).only_enforce_if(b_satisfied.negated())

        if rule.enforcement == RuleEnforcement.HARD:
            model.add_implication(a_triggered, b_satisfied)
        else:
            # Penalise: a_triggered AND NOT b_satisfied.
            violation = model.new_bool_var(f"dep_viol_{rule.id}_{iso(d)}")
            model.add_bool_and([a_triggered, b_satisfied.negated()]).only_enforce_if(violation)
            model.add_bool_or([a_triggered.negated(), b_satisfied]).only_enforce_if(violation.negated())
            vars_dict["penalties"].append(penalty * violation)
