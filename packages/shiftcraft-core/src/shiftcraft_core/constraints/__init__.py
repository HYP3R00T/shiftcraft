from shiftcraft_core.constraints.builtin import (
    CoverageHandler,
    MaxWorkDaysHandler,
    NoNightToMorningHandler,
    OneShiftPerDayHandler,
    ShiftSwitchingHandler,
    WeekendOffHandler,
)
from shiftcraft_core.registry import ConstraintRegistry


def create_default_registry() -> ConstraintRegistry:
    registry = ConstraintRegistry()
    registry.register("one_shift_per_day", OneShiftPerDayHandler())
    registry.register("coverage", CoverageHandler())
    registry.register("max_work_days", MaxWorkDaysHandler())
    registry.register("no_night_to_morning", NoNightToMorningHandler())
    registry.register("weekend_off", WeekendOffHandler())
    registry.register("shift_switching", ShiftSwitchingHandler())
    return registry
