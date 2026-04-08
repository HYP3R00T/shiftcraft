"""Primitive handler registry."""

from __future__ import annotations

from .cell import handle_value_assignment, handle_value_exclusion
from .column import handle_daily_conditional, handle_daily_count, handle_daily_ratio
from .cross_row import handle_person_dependency
from .matrix import handle_spread_across_team
from .row_balance import handle_spread_per_employee
from .row_count import (
    handle_count_bounded_by_balance,
    handle_count_per_period,
    handle_count_per_week,
    handle_count_per_window,
)
from .row_sequence import handle_pair_sequence, handle_run_sequence

HANDLERS = {
    # Cell
    "value_assignment": handle_value_assignment,
    "value_exclusion": handle_value_exclusion,
    # Row — count
    "count_per_week": handle_count_per_week,
    "count_per_window": handle_count_per_window,
    "count_per_period": handle_count_per_period,
    "count_bounded_by_balance": handle_count_bounded_by_balance,
    # Row — sequence
    "pair_sequence": handle_pair_sequence,
    "run_sequence": handle_run_sequence,
    # Row — balance
    "spread_per_employee": handle_spread_per_employee,
    # Column
    "daily_count": handle_daily_count,
    "daily_ratio": handle_daily_ratio,
    "daily_conditional": handle_daily_conditional,
    # Cross-row
    "person_dependency": handle_person_dependency,
    # Matrix
    "spread_across_team": handle_spread_across_team,
}

__all__ = ["HANDLERS"]
