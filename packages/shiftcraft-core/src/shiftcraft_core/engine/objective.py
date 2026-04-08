"""
History-bias objective — the one fixed soft objective that cannot be
expressed as a primitive because the baseline varies per person.

Penalises assigning a state to a person when they already had many of
that state in the previous period.
"""

from __future__ import annotations

from typing import Any

from ortools.sat.python import cp_model

from ..types.input import ScheduleInput


def add_history_bias(
    model: cp_model.CpModel,
    inp: ScheduleInput,
    vars_dict: dict[str, Any],
    weight: int = 5,
) -> None:
    """
    For each (employee, state) pair, penalise assignments proportional to
    how many times that state appeared in the employee's previous period.

    The penalty per assignment is: weight * hist_count.
    """
    x = vars_dict["x"]
    date_isos = vars_dict["date_isos"]
    penalties: list[cp_model.LinearExprT] = vars_dict["penalties"]

    for emp in inp.employees:
        hist = emp.history.last_month_shift_counts
        for state, hist_count in hist.items():
            if hist_count <= 0:
                continue
            for d_iso in date_isos:
                var = x.get((emp.id, d_iso, state))
                if var is not None:
                    penalties.append(weight * hist_count * var)
