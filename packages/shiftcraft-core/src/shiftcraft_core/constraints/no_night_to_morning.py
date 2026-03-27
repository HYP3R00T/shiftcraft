"""Hard constraint: forbid Night-to-Morning transitions across days.

Example payload fragment:
        {
            "type": "no_night_to_morning",
            "mode": "hard",
            "params": {"night_shift": "N", "morning_shift": "M"}
        }
"""

from __future__ import annotations

from shiftcraft_core.context import CompileContext
from shiftcraft_core.models import ConstraintSpec
from shiftcraft_core.registry import ConstraintHandler


def _index_of(value: str, options: tuple[str, ...], label: str) -> int:
    """Return index of a shift label or raise a descriptive error.

    Args:
        value: Shift label to find.
        options: Available shift labels.
        label: Name used in error message.

    Returns:
        int: Index of the shift label in options.

    Raises:
        ValueError: If value is not present in options.
    """

    try:
        return options.index(value)
    except ValueError as exc:
        raise ValueError(f"Unknown {label}: {value!r}") from exc


class NoNightToMorningHandler(ConstraintHandler):
    """Compile no-night-to-morning transition constraints."""

    def compile(self, spec: ConstraintSpec, context: CompileContext) -> None:
        """Apply Night-to-Morning transition bans.

        Args:
            spec: Constraint specification with optional shift labels.
            context: Shared compile context with problem and model state.

        Raises:
            ValueError: If mode is not hard, labels are invalid, or shifts are missing.
        """

        if spec.mode != "hard":
            raise ValueError("'no_night_to_morning' must be hard")

        night_shift = spec.params.get("night_shift", "N")
        morning_shift = spec.params.get("morning_shift", "M")
        if not isinstance(night_shift, str) or not isinstance(morning_shift, str):
            raise ValueError("no_night_to_morning shift labels must be strings")

        problem = context.problem
        night_idx = _index_of(night_shift, problem.shifts, "night shift")
        morning_idx = _index_of(morning_shift, problem.shifts, "morning shift")

        for employee_idx, _ in enumerate(problem.employees):
            for day_idx in range(problem.days - 1):
                context.model.Add(
                    context.x[(employee_idx, day_idx, night_idx)] + context.x[(employee_idx, day_idx + 1, morning_idx)]
                    <= 1
                )
