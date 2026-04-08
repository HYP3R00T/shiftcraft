"""
Row-level sequence primitives
  - pair_sequence
  - run_sequence
"""

from __future__ import annotations

from datetime import date
from typing import Any

from ortools.sat.python import cp_model

from ._util import iso
from ..types.input import Employee, ScheduleInput
from ..types.rules import Rule, RuleEnforcement

# ── pair_sequence ─────────────────────────────────────────────────────────────


def handle_pair_sequence(
    model: cp_model.CpModel,
    rule: Rule,
    employees: list[Employee],
    dates: list[date],
    inp: ScheduleInput,
    vars_dict: dict[str, Any],
) -> None:
    """
    If employee has ``from_value`` on day d, ``to_value`` is forbidden or
    required on day d + gap_days.
    """
    x = vars_dict["x"]
    from_value: str = rule.params["from_value"]
    to_value: str = rule.params["to_value"]
    gap: int = rule.params.get("gap_days", 1)
    forbidden: bool = rule.params.get("forbidden", True)
    penalty = rule.penalty()

    date_index = {d: i for i, d in enumerate(inp.dates)}

    for emp in employees:
        for d in dates:
            idx = date_index.get(d)
            if idx is None:
                continue
            next_idx = idx + gap
            if next_idx >= len(inp.dates):
                continue
            d_next = inp.dates[next_idx]

            from_var = x.get((emp.id, iso(d), from_value))
            to_var = x.get((emp.id, iso(d_next), to_value))
            if from_var is None or to_var is None:
                continue

            if rule.enforcement == RuleEnforcement.HARD:
                if forbidden:
                    # from_value on d AND to_value on d+gap is forbidden.
                    model.add_bool_or([from_var.negated(), to_var.negated()])
                else:
                    # from_value on d IMPLIES to_value on d+gap.
                    model.add_implication(from_var, to_var)
            else:
                # Soft: penalise the undesired pattern.
                if forbidden:
                    # Penalise if both are true.
                    both = model.new_bool_var(f"pair_both_{emp.id}_{iso(d)}")
                    model.add_bool_and([from_var, to_var]).only_enforce_if(both)
                    model.add_bool_or([from_var.negated(), to_var.negated()]).only_enforce_if(both.negated())
                    vars_dict["penalties"].append(penalty * both)
                else:
                    # Penalise if from is true but to is not.
                    missing = model.new_bool_var(f"pair_miss_{emp.id}_{iso(d)}")
                    model.add_implication(from_var, to_var).only_enforce_if(missing.negated())
                    model.add_bool_and([from_var, to_var.negated()]).only_enforce_if(missing)
                    vars_dict["penalties"].append(penalty * missing)


# ── run_sequence ──────────────────────────────────────────────────────────────


def handle_run_sequence(
    model: cp_model.CpModel,
    rule: Rule,
    employees: list[Employee],
    dates: list[date],
    inp: ScheduleInput,
    vars_dict: dict[str, Any],
) -> None:
    """
    After N consecutive days of ``trigger_value``, enforce a condition on
    the following ``then_days`` days.

    Carries over ``previous_state_run`` from employee history.
    """
    x = vars_dict["x"]
    trigger_value: str = rule.params["trigger_value"]
    trigger_count: int = rule.params["trigger_count"]
    then_value: str = rule.params["then_value"]
    then_operator: str = rule.params["then_operator"]
    then_count: int = rule.params["then_count"]
    then_days: int = rule.params["then_days"]
    penalty = rule.penalty()

    all_dates = inp.dates
    n = len(all_dates)

    for emp in inp.employees:
        # Carry-over from previous period.
        prev_run = emp.history.previous_state_run
        carry = prev_run.count if prev_run and prev_run.value == trigger_value else 0

        # Build a list of BoolVars for trigger_value across all dates.
        trigger_vars = [x.get((emp.id, iso(d), trigger_value)) for d in all_dates]

        for i in range(n):
            # How many trigger days do we need from the current period?
            needed = trigger_count - carry if i == 0 else trigger_count
            if needed <= 0:
                # Carry alone is enough — the rule fires from day 0.
                window_start = 0
            else:
                window_start = i
                window_end = i + needed - 1
                if window_end >= n:
                    continue

                # Check that days [window_start .. window_end] are all trigger_value.
                run_vars = [v for v in trigger_vars[window_start : window_end + 1] if v is not None]
                if len(run_vars) < needed:
                    continue

                # The rule fires only when the full run is present.
                run_active = model.new_bool_var(f"run_{emp.id}_{i}")
                model.add_bool_and(run_vars).only_enforce_if(run_active)
                model.add_bool_or([v.negated() for v in run_vars]).only_enforce_if(run_active.negated())

                # Consequence window: days immediately after the run.
                consequence_start = window_end + 1
                consequence_end = min(consequence_start + then_days - 1, n - 1)
                if consequence_start > n - 1:
                    continue

                then_vars = [
                    x.get((emp.id, iso(all_dates[j]), then_value))
                    for j in range(consequence_start, consequence_end + 1)
                ]
                then_vars = [v for v in then_vars if v is not None]
                if not then_vars:
                    continue

                then_expr = cp_model.LinearExpr.sum(then_vars)

                if rule.enforcement == RuleEnforcement.HARD:
                    match then_operator:
                        case ">=":
                            model.add(then_expr >= then_count).only_enforce_if(run_active)
                        case "<=":
                            model.add(then_expr <= then_count).only_enforce_if(run_active)
                        case "==":
                            model.add(then_expr == then_count).only_enforce_if(run_active)
                else:
                    slack = model.new_int_var(0, then_days, f"run_slack_{emp.id}_{i}")
                    if then_operator == ">=":
                        model.add(slack >= then_count - then_expr).only_enforce_if(run_active)
                        model.add(slack == 0).only_enforce_if(run_active.negated())
                    else:
                        model.add(slack >= then_expr - then_count).only_enforce_if(run_active)
                        model.add(slack == 0).only_enforce_if(run_active.negated())
                    vars_dict["penalties"].append(penalty * slack)

                # Only process the first window start per employee to avoid
                # redundant overlapping windows.
                break
