"""Hard constraint: enforce minimum staffing coverage per shift/day.

Example payload fragment:
        {
            "type": "coverage",
            "mode": "hard",
            "params": {"min_per_shift": 1}
        }
"""

from __future__ import annotations

from shiftcraft_core.context import CompileContext
from shiftcraft_core.models import ConstraintSpec
from shiftcraft_core.registry import ConstraintHandler


class CoverageHandler(ConstraintHandler):
    """Compile coverage constraints into CP-SAT model."""

    def compile(self, spec: ConstraintSpec, context: CompileContext) -> None:
        """Apply minimum coverage constraints.

        Args:
            spec: Constraint specification containing min_per_shift.
            context: Shared compile context with problem and model state.

        Raises:
            ValueError: If mode is not hard or params are invalid.
        """

        if spec.mode != "hard":
            raise ValueError("'coverage' must be hard")

        min_per_shift = spec.params.get("min_per_shift", 1)
        if not isinstance(min_per_shift, int) or min_per_shift <= 0:
            raise ValueError("coverage.min_per_shift must be a positive integer")

        problem = context.problem
        for day_idx in range(problem.days):
            for shift_idx, _ in enumerate(problem.shifts):
                context.model.Add(
                    sum(
                        context.x[(employee_idx, day_idx, shift_idx)]
                        for employee_idx, _ in enumerate(problem.employees)
                    )
                    >= min_per_shift
                )
