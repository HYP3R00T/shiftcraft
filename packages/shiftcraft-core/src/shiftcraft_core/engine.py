from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from typing import Any

from ortools.sat.python import cp_model

from shiftcraft_core.constraints import create_default_registry
from shiftcraft_core.context import SOFT_PRIORITY_SCALE, CompileContext
from shiftcraft_core.models import PenaltySummary, Problem, Solution, SolutionMetadata, SolverStatus
from shiftcraft_core.parser import parse_payload


def _build_decision_variables(context: CompileContext) -> None:
    problem = context.problem
    for employee_idx, _ in enumerate(problem.employees):
        for day_idx in range(problem.days):
            for shift_idx, _ in enumerate(problem.shifts):
                context.x[(employee_idx, day_idx, shift_idx)] = context.model.NewBoolVar(
                    f"x_e{employee_idx}_d{day_idx}_s{shift_idx}"
                )


def _apply_tie_breakers(context: CompileContext) -> None:
    problem = context.problem

    if problem.objective.assignment_weight > 0:
        total_assignments = sum(context.x.values())
        context.add_tie_breaker(problem.objective.assignment_weight * total_assignments)

    if problem.objective.fairness_weight > 0:
        workloads = []
        for employee_idx, _ in enumerate(problem.employees):
            workloads.append(
                sum(
                    context.x[(employee_idx, day_idx, shift_idx)]
                    for day_idx in range(problem.days)
                    for shift_idx, _ in enumerate(problem.shifts)
                )
            )

        max_load = context.model.NewIntVar(0, problem.days, "max_load")
        min_load = context.model.NewIntVar(0, problem.days, "min_load")
        for load in workloads:
            context.model.Add(load <= max_load)
            context.model.Add(load >= min_load)

        context.add_tie_breaker(problem.objective.fairness_weight * (max_load - min_load))


def _build_objective(context: CompileContext) -> None:
    soft_objective = sum(entry.weight * entry.var for entry in context.penalties)
    tie_breaker_objective = sum(context.tie_breakers)
    context.model.Minimize(SOFT_PRIORITY_SCALE * soft_objective + tie_breaker_objective)


def _status_name(status_code: int) -> SolverStatus:
    status_map: dict[int, SolverStatus] = {
        int(cp_model.OPTIMAL): "optimal",
        int(cp_model.FEASIBLE): "feasible",
        int(cp_model.INFEASIBLE): "infeasible",
        int(cp_model.MODEL_INVALID): "model_invalid",
        int(cp_model.UNKNOWN): "unknown",
    }
    return status_map[int(status_code)]


def _extract_schedule(
    problem: Problem, solver: cp_model.CpSolver, x: dict[tuple[int, int, int], Any]
) -> list[dict[str, str | list[str] | None]]:
    schedule: list[dict[str, str | list[str] | None]] = []
    for day_idx in range(problem.days):
        day_plan: dict[str, str | list[str] | None] = {}
        for shift_idx, shift_name in enumerate(problem.shifts):
            assigned = [
                employee
                for employee_idx, employee in enumerate(problem.employees)
                if solver.Value(x[(employee_idx, day_idx, shift_idx)]) == 1
            ]
            if not assigned:
                day_plan[shift_name] = None
            elif len(assigned) == 1:
                day_plan[shift_name] = assigned[0]
            else:
                day_plan[shift_name] = assigned
        schedule.append(day_plan)
    return schedule


def solve_problem(problem: Problem) -> Solution:
    registry = create_default_registry()
    model = cp_model.CpModel()
    context = CompileContext(problem=problem, model=model)

    _build_decision_variables(context)

    for spec in problem.constraints:
        registry.compile(spec, context)

    _apply_tie_breakers(context)
    _build_objective(context)

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = 0

    status = solver.Solve(model)
    status_name = _status_name(status)

    penalty_totals: dict[str, dict[str, int]] = defaultdict(lambda: {"weight": 0, "violations": 0, "weighted": 0})
    for entry in context.penalties:
        value = solver.Value(entry.var) if status in {cp_model.OPTIMAL, cp_model.FEASIBLE} else 0
        bucket = penalty_totals[entry.constraint_type]
        bucket["weight"] = entry.weight
        bucket["violations"] += value
        bucket["weighted"] += entry.weight * value

    penalties = {
        kind: PenaltySummary(
            weight=bucket["weight"],
            violations=bucket["violations"],
            weighted_penalty=bucket["weighted"],
        )
        for kind, bucket in sorted(penalty_totals.items())
    }

    total_violations = sum(summary.violations for summary in penalties.values())

    if status not in {cp_model.OPTIMAL, cp_model.FEASIBLE}:
        return Solution(
            schedule=[],
            objective=0,
            metadata=SolutionMetadata(
                status=status_name,
                penalties=penalties,
                total_violations=total_violations,
            ),
        )

    objective = int(round(solver.ObjectiveValue()))
    schedule = _extract_schedule(problem, solver, context.x)

    return Solution(
        schedule=schedule,
        objective=objective,
        metadata=SolutionMetadata(
            status=status_name,
            penalties=penalties,
            total_violations=total_violations,
        ),
    )


def solve(payload: Mapping[str, Any] | str) -> dict[str, Any]:
    """Public API entry point: JSON payload in, schedule JSON out."""

    problem = parse_payload(payload)
    solution = solve_problem(problem)

    return {
        "schedule": solution.schedule,
        "objective": solution.objective,
        "metadata": {
            "status": solution.metadata.status,
            "total_violations": solution.metadata.total_violations,
            "penalties": {
                kind: {
                    "weight": summary.weight,
                    "violations": summary.violations,
                    "weighted_penalty": summary.weighted_penalty,
                }
                for kind, summary in solution.metadata.penalties.items()
            },
        },
    }
