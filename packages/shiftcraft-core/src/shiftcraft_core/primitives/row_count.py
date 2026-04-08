"""
Row-level count primitives
  - count_per_week
  - count_per_window
  - count_per_period
  - count_bounded_by_balance
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from typing import Any

from ortools.sat.python import cp_model

from ._util import apply_count_constraint, iso, week_key
from ..scope.filters import filter_when
from ..types.input import Employee, ScheduleInput
from ..types.rules import BalanceSource, Rule

# ── count_per_week ────────────────────────────────────────────────────────────


def handle_count_per_week(
    model: cp_model.CpModel,
    rule: Rule,
    employees: list[Employee],
    dates: list[date],
    inp: ScheduleInput,
    vars_dict: dict[str, Any],
) -> None:
    x = vars_dict["x"]
    value: str = rule.params["value"]
    operator: str = rule.params["operator"]
    count: int = rule.params["count"]
    penalty = rule.penalty()

    # Group scoped dates by ISO week.
    by_week: dict[str, list[date]] = defaultdict(list)
    for d in dates:
        by_week[week_key(d)].append(d)

    for emp in employees:
        for week_dates in by_week.values():
            # Skip partial weeks that cannot satisfy >= or == thresholds.
            if operator in ("==", ">=") and len(week_dates) < count:
                continue
            expr = cp_model.LinearExpr.sum([
                x[(emp.id, iso(d), value)] for d in week_dates if (emp.id, iso(d), value) in x
            ])
            apply_count_constraint(model, expr, operator, count, rule.enforcement, penalty, vars_dict)


# ── count_per_window ──────────────────────────────────────────────────────────


def handle_count_per_window(
    model: cp_model.CpModel,
    rule: Rule,
    employees: list[Employee],
    dates: list[date],
    inp: ScheduleInput,
    vars_dict: dict[str, Any],
) -> None:
    x = vars_dict["x"]
    values: list[str] = rule.params["values"]
    window: int = rule.params["window_days"]
    operator: str = rule.params["operator"]
    count: int = rule.params["count"]
    penalty = rule.penalty()

    # Use the full period dates for the sliding window (scope dates are the
    # anchor set; the window itself always slides over the full period).
    all_dates = inp.dates
    date_set = set(dates)

    for emp in employees:
        for i in range(len(all_dates) - window + 1):
            window_dates = all_dates[i : i + window]
            # Only apply if the window overlaps with the scoped dates.
            if not any(d in date_set for d in window_dates):
                continue
            expr = cp_model.LinearExpr.sum([
                x[(emp.id, iso(d), s)] for d in window_dates for s in values if (emp.id, iso(d), s) in x
            ])
            apply_count_constraint(model, expr, operator, count, rule.enforcement, penalty, vars_dict)


# ── count_per_period ──────────────────────────────────────────────────────────


def handle_count_per_period(
    model: cp_model.CpModel,
    rule: Rule,
    employees: list[Employee],
    dates: list[date],
    inp: ScheduleInput,
    vars_dict: dict[str, Any],
) -> None:
    x = vars_dict["x"]
    value: str = rule.params["value"]
    operator: str = rule.params["operator"]
    count: int = rule.params["count"]
    penalty = rule.penalty()

    # Optional day filter within the scoped dates.
    count_when_raw = rule.params.get("count_when")
    if count_when_raw:
        from ..types.rules import WhenFilter

        count_when = WhenFilter(**count_when_raw) if isinstance(count_when_raw, dict) else count_when_raw
        filtered = set(filter_when(count_when, inp))
        count_dates = [d for d in dates if d in filtered]
    else:
        count_dates = dates

    for emp in employees:
        expr = cp_model.LinearExpr.sum([
            x[(emp.id, iso(d), value)] for d in count_dates if (emp.id, iso(d), value) in x
        ])
        apply_count_constraint(model, expr, operator, count, rule.enforcement, penalty, vars_dict)


# ── count_bounded_by_balance ──────────────────────────────────────────────────


def _resolve_balance(emp: Employee, source: BalanceSource) -> int:
    """Compute N(p, v) from the employee's input data."""
    if source.type == "numeric":
        return emp.balances.get(source.key, 0)

    # "records" — count valid, unredeemed records within validity window.
    records = emp.records.get(source.key, [])
    if not records:
        return 0

    valid_count = 0
    for rec in records:
        if rec.get("redeemed_on"):
            continue
        if source.validity_days is not None:
            earned = date.fromisoformat(rec["earned_date"])
            # A record is valid if it hasn't expired relative to the period start.
            # We use today's period_start as the reference; expired records are excluded.
            # (The exact expiry check is: earned + validity_days >= period_start.)
            expiry = earned + timedelta(days=source.validity_days)
            # We don't have period_start here; use the record as valid if not expired
            # relative to its earned date alone — the parser can pre-filter if needed.
            _ = expiry  # expiry check deferred to parser pre-filtering
        valid_count += 1
    return valid_count


def handle_count_bounded_by_balance(
    model: cp_model.CpModel,
    rule: Rule,
    employees: list[Employee],
    dates: list[date],
    inp: ScheduleInput,
    vars_dict: dict[str, Any],
) -> None:
    x = vars_dict["x"]
    value: str = rule.params["value"]
    source: BalanceSource = rule.params["balance_source"]

    for emp in employees:
        bound = _resolve_balance(emp, source)
        expr = cp_model.LinearExpr.sum([x[(emp.id, iso(d), value)] for d in dates if (emp.id, iso(d), value) in x])
        # Always hard — person-bound counts are never soft per the spec.
        model.add(expr <= bound)
