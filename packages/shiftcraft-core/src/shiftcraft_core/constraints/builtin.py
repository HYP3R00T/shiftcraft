from __future__ import annotations

from collections.abc import Iterable

from shiftcraft_core.context import CompileContext
from shiftcraft_core.models import ConstraintSpec
from shiftcraft_core.registry import ConstraintHandler


def _index_of(value: str, options: tuple[str, ...], label: str) -> int:
    try:
        return options.index(value)
    except ValueError as exc:
        raise ValueError(f"Unknown {label}: {value!r}") from exc


class OneShiftPerDayHandler(ConstraintHandler):
    def compile(self, spec: ConstraintSpec, context: CompileContext) -> None:
        if spec.mode != "hard":
            raise ValueError("'one_shift_per_day' must be hard")

        problem = context.problem
        for employee_idx, _ in enumerate(problem.employees):
            for day_idx in range(problem.days):
                context.model.Add(
                    sum(context.x[(employee_idx, day_idx, shift_idx)] for shift_idx, _ in enumerate(problem.shifts))
                    <= 1
                )


class CoverageHandler(ConstraintHandler):
    def compile(self, spec: ConstraintSpec, context: CompileContext) -> None:
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


class MaxWorkDaysHandler(ConstraintHandler):
    def compile(self, spec: ConstraintSpec, context: CompileContext) -> None:
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


class NoNightToMorningHandler(ConstraintHandler):
    def compile(self, spec: ConstraintSpec, context: CompileContext) -> None:
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


class WeekendOffHandler(ConstraintHandler):
    def compile(self, spec: ConstraintSpec, context: CompileContext) -> None:
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


class ShiftSwitchingHandler(ConstraintHandler):
    def compile(self, spec: ConstraintSpec, context: CompileContext) -> None:
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
