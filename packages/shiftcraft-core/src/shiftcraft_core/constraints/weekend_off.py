"""Soft constraint: penalize weekend assignments for selected employees.

Example payload fragment:
        {
            "type": "weekend_off",
            "mode": "soft",
            "weight": 10,
            "params": {"employees": ["A", "B"], "weekend_days": [5, 6]}
        }
"""

from __future__ import annotations

from collections.abc import Iterable

from shiftcraft_core.context import CompileContext
from shiftcraft_core.models import ConstraintSpec
from shiftcraft_core.registry import ConstraintHandler


class WeekendOffHandler(ConstraintHandler):
    """Compile weekend-off preference penalties into objective terms."""

    def compile(self, spec: ConstraintSpec, context: CompileContext) -> None:
        """Apply weekend-off soft penalties.

        Args:
            spec: Constraint specification with employee/weekend configuration.
            context: Shared compile context with problem and model state.

        Raises:
            ValueError: If mode is not soft or parameters are invalid.
        """

        if spec.mode != "soft":
            raise ValueError("'weekend_off' must be soft")

        problem = context.problem

        employee_names = spec.params.get("employees", list(problem.employees))
        if not isinstance(employee_names, Iterable):
            raise ValueError("weekend_off.employees must be a list of employee IDs")
        employee_set = {str(name) for name in employee_names}
        employee_indices = [idx for idx, employee in enumerate(problem.employees) if employee in employee_set]

        weekend_days = spec.params.get("weekend_days")
        if weekend_days is None:
            weekend_idxs = [0] if problem.days == 1 else [problem.days - 2, problem.days - 1]
        else:
            if not isinstance(weekend_days, list) or not all(isinstance(day, int) for day in weekend_days):
                raise ValueError("weekend_off.weekend_days must be a list of day indices")
            weekend_idxs = [day for day in weekend_days if 0 <= day < problem.days]

        for employee_idx in employee_indices:
            works_weekend = context.model.NewBoolVar(f"weekend_off_e{employee_idx}_viol")
            weekend_assignments = [
                context.x[(employee_idx, day_idx, shift_idx)]
                for day_idx in weekend_idxs
                for shift_idx, _ in enumerate(problem.shifts)
            ]

            if not weekend_assignments:
                context.model.Add(works_weekend == 0)
            else:
                total = sum(weekend_assignments)
                context.model.Add(total >= 1).OnlyEnforceIf(works_weekend)
                context.model.Add(total == 0).OnlyEnforceIf(works_weekend.Not())

            context.add_penalty(spec.type, spec.weight, works_weekend)
