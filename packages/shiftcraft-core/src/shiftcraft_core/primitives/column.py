"""
Column-level primitives
  - daily_count
  - daily_ratio
  - daily_conditional
"""

from __future__ import annotations

from datetime import date
from typing import Any

from ortools.sat.python import cp_model

from ._util import apply_count_constraint, iso
from ..scope.filters import filter_who
from ..types.input import Employee, ScheduleInput
from ..types.rules import Rule, RuleEnforcement, WhoFilter

# ── daily_count ───────────────────────────────────────────────────────────────


def handle_daily_count(
    model: cp_model.CpModel,
    rule: Rule,
    employees: list[Employee],
    dates: list[date],
    inp: ScheduleInput,
    vars_dict: dict[str, Any],
) -> None:
    """
    On each matching day, the count of employees (in scope) with a given
    state must satisfy operator/count.
    """
    x = vars_dict["x"]
    value = rule.params["value"]
    operator: str = rule.params["operator"]
    count: int = rule.params["count"]
    penalty = rule.penalty()

    # value may be a list (sum across states) or a single string.
    state_list: list[str] = value if isinstance(value, list) else [value]

    for d in dates:
        expr = cp_model.LinearExpr.sum([
            x[(emp.id, iso(d), s)] for emp in employees for s in state_list if (emp.id, iso(d), s) in x
        ])
        apply_count_constraint(model, expr, operator, count, rule.enforcement, penalty, vars_dict)


# ── daily_ratio ───────────────────────────────────────────────────────────────


def handle_daily_ratio(
    model: cp_model.CpModel,
    rule: Rule,
    employees: list[Employee],
    dates: list[date],
    inp: ScheduleInput,
    vars_dict: dict[str, Any],
) -> None:
    """
    On each matching day, numerator / denominator must satisfy operator/ratio.

    Ratio is linearised as: numerator * scale >= ratio * denominator * scale
    using integer arithmetic (scale = 100).
    """
    x = vars_dict["x"]
    value: str = rule.params["value"]
    numerator_who_raw = rule.params["numerator_who"]
    operator: str = rule.params["operator"]
    ratio: float = rule.params["ratio"]
    exclude_values: list[str] = rule.params.get("exclude_values", [])

    numerator_who = WhoFilter(**numerator_who_raw) if isinstance(numerator_who_raw, dict) else numerator_who_raw

    numerator_emps = filter_who(numerator_who, employees)
    scale = 100
    ratio_int = int(ratio * scale)

    for d in dates:
        # Numerator: employees in numerator_who with the target state.
        num_expr = cp_model.LinearExpr.sum([
            x[(emp.id, iso(d), value)] for emp in numerator_emps if (emp.id, iso(d), value) in x
        ])

        # Denominator: all scoped employees minus those in exclude_values.
        denom_vars = []
        for emp in employees:
            # Use a BoolVar: 1 if employee is NOT in an excluded state.
            present = model.new_bool_var(f"ratio_present_{emp.id}_{iso(d)}")
            excl_sum = cp_model.LinearExpr.sum([
                x[(emp.id, iso(d), ev)] for ev in exclude_values if (emp.id, iso(d), ev) in x
            ])
            model.add(excl_sum == 0).only_enforce_if(present)
            model.add(excl_sum >= 1).only_enforce_if(present.negated())
            denom_vars.append(present)

        denom_expr = cp_model.LinearExpr.sum(denom_vars)

        # Linearised ratio: num * scale >= ratio_int * denom  (for >=)
        if rule.enforcement == RuleEnforcement.HARD:
            match operator:
                case ">=":
                    model.add(num_expr * scale >= ratio_int * denom_expr)
                case "<=":
                    model.add(num_expr * scale <= ratio_int * denom_expr)
                case "==":
                    model.add(num_expr * scale == ratio_int * denom_expr)
        else:
            penalty = rule.penalty()
            slack = model.new_int_var(0, len(employees) * scale, f"ratio_slack_{iso(d)}")
            if operator == ">=":
                model.add(slack * scale >= ratio_int * denom_expr - num_expr * scale)
            else:
                model.add(slack * scale >= num_expr * scale - ratio_int * denom_expr)
            vars_dict["penalties"].append(penalty * slack)


# ── daily_conditional ─────────────────────────────────────────────────────────


def handle_daily_conditional(
    model: cp_model.CpModel,
    rule: Rule,
    employees: list[Employee],
    dates: list[date],
    inp: ScheduleInput,
    vars_dict: dict[str, Any],
) -> None:
    """
    If count(if_value, if_who) satisfies if_operator/if_count on day d,
    then count(then_value, then_who) must satisfy then_operator/then_count.
    """
    x = vars_dict["x"]
    if_value: str = rule.params["if_value"]
    if_who_raw = rule.params["if_who"]
    if_operator: str = rule.params["if_operator"]
    if_count: int = rule.params["if_count"]
    then_value: str = rule.params["then_value"]
    then_who_raw = rule.params["then_who"]
    then_operator: str = rule.params["then_operator"]
    then_count: int = rule.params["then_count"]

    if_who = WhoFilter(**if_who_raw) if isinstance(if_who_raw, dict) else if_who_raw
    then_who = WhoFilter(**then_who_raw) if isinstance(then_who_raw, dict) else then_who_raw

    if_emps = filter_who(if_who, inp.employees)
    then_emps = filter_who(then_who, inp.employees)

    for d in dates:
        if_expr = cp_model.LinearExpr.sum([
            x[(emp.id, iso(d), if_value)] for emp in if_emps if (emp.id, iso(d), if_value) in x
        ])
        then_expr = cp_model.LinearExpr.sum([
            x[(emp.id, iso(d), then_value)] for emp in then_emps if (emp.id, iso(d), then_value) in x
        ])

        # Condition active BoolVar.
        cond = model.new_bool_var(f"cond_{rule.id}_{iso(d)}")
        match if_operator:
            case ">=":
                model.add(if_expr >= if_count).only_enforce_if(cond)
                model.add(if_expr < if_count).only_enforce_if(cond.negated())
            case "<=":
                model.add(if_expr <= if_count).only_enforce_if(cond)
                model.add(if_expr > if_count).only_enforce_if(cond.negated())
            case "==":
                model.add(if_expr == if_count).only_enforce_if(cond)
                model.add(if_expr != if_count).only_enforce_if(cond.negated())

        if rule.enforcement == RuleEnforcement.HARD:
            match then_operator:
                case ">=":
                    model.add(then_expr >= then_count).only_enforce_if(cond)
                case "<=":
                    model.add(then_expr <= then_count).only_enforce_if(cond)
                case "==":
                    model.add(then_expr == then_count).only_enforce_if(cond)
        else:
            penalty = rule.penalty()
            slack = model.new_int_var(0, len(inp.employees), f"cond_slack_{rule.id}_{iso(d)}")
            if then_operator == ">=":
                model.add(slack >= then_count - then_expr).only_enforce_if(cond)
            else:
                model.add(slack >= then_expr - then_count).only_enforce_if(cond)
            model.add(slack == 0).only_enforce_if(cond.negated())
            vars_dict["penalties"].append(penalty * slack)
