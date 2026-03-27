"""Hard constraint: employee can work at most one shift per day.

Example payload fragment:
        {
            "type": "one_shift_per_day",
            "mode": "hard",
            "params": {}
        }
"""

from __future__ import annotations

from shiftcraft_core.context import CompileContext
from shiftcraft_core.models import ConstraintSpec
from shiftcraft_core.registry import ConstraintHandler


class OneShiftPerDayHandler(ConstraintHandler):
    """Compile one-shift-per-day hard constraints into CP-SAT model."""

    def compile(self, spec: ConstraintSpec, context: CompileContext) -> None:
        """Apply one-shift-per-day constraints.

        Args:
            spec: Constraint specification for this handler.
            context: Shared compile context with problem and model state.

        Raises:
            ValueError: If the constraint mode is not hard.
        """

        if spec.mode != "hard":
            raise ValueError("'one_shift_per_day' must be hard")

        problem = context.problem
        for employee_idx, _ in enumerate(problem.employees):
            for day_idx in range(problem.days):
                context.model.Add(
                    sum(context.x[(employee_idx, day_idx, shift_idx)] for shift_idx, _ in enumerate(problem.shifts))
                    <= 1
                )
