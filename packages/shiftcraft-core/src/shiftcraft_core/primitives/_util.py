"""Shared helpers used across primitive handlers."""

from __future__ import annotations

from datetime import date
from typing import Any

from ortools.sat.python import cp_model

from ..types.rules import RuleEnforcement

# Module-level counter for unique slack variable names.
_slack_counter = 0


def _slack_name(prefix: str = "slack") -> str:
    global _slack_counter
    _slack_counter += 1
    return f"{prefix}_{_slack_counter}"


def iso(d: date) -> str:
    return d.isoformat()


def week_key(d: date) -> str:
    """ISO week identifier: 'YYYY-Www'."""
    c = d.isocalendar()
    return f"{c.year}-W{c.week:02d}"


def apply_count_constraint(
    model: cp_model.CpModel,
    expr: cp_model.LinearExprT,
    operator: str,
    count: int,
    enforcement: RuleEnforcement,
    penalty: int,
    vars_dict: dict[str, Any],
    ub: int = 10_000,
) -> None:
    """
    Add ``expr operator count`` as a hard constraint or soft penalty term.

    For soft constraints a slack variable is introduced and its value
    (scaled by *penalty*) is appended to ``vars_dict["penalties"]``.
    ``ub`` is the upper bound hint for slack variables.
    """
    if enforcement == RuleEnforcement.HARD:
        match operator:
            case ">=":
                model.add(expr >= count)
            case "<=":
                model.add(expr <= count)
            case "==":
                model.add(expr == count)
            case _:
                raise ValueError(f"Unknown operator: {operator!r}")
    else:
        # Soft: penalise violation via a non-negative slack variable.
        match operator:
            case ">=":
                # penalty * max(0, count - expr)
                slack = model.new_int_var(0, ub, _slack_name("slack_ge"))
                model.add(slack >= count - expr)
                vars_dict["penalties"].append(penalty * slack)
            case "<=":
                # penalty * max(0, expr - count)
                slack = model.new_int_var(0, ub, _slack_name("slack_le"))
                model.add(slack >= expr - count)
                vars_dict["penalties"].append(penalty * slack)
            case "==":
                # penalty * |expr - count|
                slack = model.new_int_var(0, ub, _slack_name("slack_eq"))
                diff = model.new_int_var(-ub, ub, _slack_name("diff_eq"))
                model.add(diff == expr - count)
                model.add_abs_equality(slack, diff)
                vars_dict["penalties"].append(penalty * slack)
            case _:
                raise ValueError(f"Unknown operator: {operator!r}")
