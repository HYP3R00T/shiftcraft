"""Constraint package exports and default registry wiring.

This module provides a single import surface for all built-in constraints and
the default registry bootstrap function.

Example:
    from shiftcraft_core.constraints import create_default_registry

    registry = create_default_registry()
"""

from shiftcraft_core.constraints.coverage import CoverageHandler
from shiftcraft_core.constraints.max_work_days import MaxWorkDaysHandler
from shiftcraft_core.constraints.no_night_to_morning import NoNightToMorningHandler
from shiftcraft_core.constraints.one_shift_per_day import OneShiftPerDayHandler
from shiftcraft_core.constraints.shift_switching import ShiftSwitchingHandler
from shiftcraft_core.constraints.weekend_off import WeekendOffHandler
from shiftcraft_core.registry import ConstraintRegistry

__all__ = [
    "CoverageHandler",
    "MaxWorkDaysHandler",
    "NoNightToMorningHandler",
    "OneShiftPerDayHandler",
    "ShiftSwitchingHandler",
    "WeekendOffHandler",
    "create_default_registry",
]


def create_default_registry() -> ConstraintRegistry:
    """Create a registry preloaded with built-in constraint handlers.

    Returns:
        ConstraintRegistry: Registry containing all built-in handlers.
    """

    registry = ConstraintRegistry()
    registry.register("one_shift_per_day", OneShiftPerDayHandler())
    registry.register("coverage", CoverageHandler())
    registry.register("max_work_days", MaxWorkDaysHandler())
    registry.register("no_night_to_morning", NoNightToMorningHandler())
    registry.register("weekend_off", WeekendOffHandler())
    registry.register("shift_switching", ShiftSwitchingHandler())
    return registry
