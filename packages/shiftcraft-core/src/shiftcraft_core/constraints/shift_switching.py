"""Soft constraint: penalize shift-type changes across consecutive days.

Example payload fragment:
        {
            "type": "shift_switching",
            "mode": "soft",
            "weight": 1,
            "params": {}
        }
"""

from __future__ import annotations

from shiftcraft_core.context import CompileContext
from shiftcraft_core.models import ConstraintSpec
from shiftcraft_core.registry import ConstraintHandler


class ShiftSwitchingHandler(ConstraintHandler):
    """Compile shift-switching penalties into objective terms."""

    def compile(self, spec: ConstraintSpec, context: CompileContext) -> None:
        """Apply penalties for consecutive-day shift changes.

        Args:
            spec: Constraint specification for shift-switching behavior.
            context: Shared compile context with problem and model state.

        Raises:
            ValueError: If mode is not soft.
        """

        if spec.mode != "soft":
            raise ValueError("'shift_switching' must be soft")

        problem = context.problem

        for employee_idx, _ in enumerate(problem.employees):
            for day_idx in range(problem.days - 1):
                for shift_a_idx, _ in enumerate(problem.shifts):
                    for shift_b_idx, _ in enumerate(problem.shifts):
                        if shift_a_idx == shift_b_idx:
                            continue

                        switched = context.model.NewBoolVar(
                            f"switch_e{employee_idx}_d{day_idx}_{shift_a_idx}_{shift_b_idx}"
                        )
                        context.model.Add(switched <= context.x[(employee_idx, day_idx, shift_a_idx)])
                        context.model.Add(switched <= context.x[(employee_idx, day_idx + 1, shift_b_idx)])
                        context.model.Add(
                            switched
                            >= context.x[(employee_idx, day_idx, shift_a_idx)]
                            + context.x[(employee_idx, day_idx + 1, shift_b_idx)]
                            - 1
                        )
                        context.add_penalty(spec.type, spec.weight, switched)
