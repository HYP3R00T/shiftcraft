"""Hard constraint: cap total assigned days per employee.

Example payload fragment:
        {
            "type": "max_work_days",
            "mode": "hard",
            "params": {"max": 5}
        }
"""

from __future__ import annotations

from shiftcraft_core.context import CompileContext
from shiftcraft_core.models import ConstraintSpec
from shiftcraft_core.registry import ConstraintHandler


class MaxWorkDaysHandler(ConstraintHandler):
    """Compile max-work-days constraints into CP-SAT model."""

    def compile(self, spec: ConstraintSpec, context: CompileContext) -> None:
        """Apply per-employee max work day limits.

        Args:
            spec: Constraint specification containing max day limit.
            context: Shared compile context with problem and model state.

        Raises:
            ValueError: If mode is not hard or max is invalid.
        """

        if spec.mode != "hard":
            raise ValueError("'max_work_days' must be hard")

        limit = spec.params.get("max")
        if not isinstance(limit, int) or limit < 0:
            raise ValueError("max_work_days.max must be an integer >= 0")

        problem = context.problem
        for employee_idx, _ in enumerate(problem.employees):
            context.model.Add(
                sum(
                    context.x[(employee_idx, day_idx, shift_idx)]
                    for day_idx in range(problem.days)
                    for shift_idx, _ in enumerate(problem.shifts)
                )
                <= limit
            )
