"""Shared fixtures for shiftcraft-core tests."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import pytest
from ortools.sat.python import cp_model
from shiftcraft_core.engine.variables import create_variables
from shiftcraft_core.types.input import Employee, EmployeeHistory, Holiday, ScheduleInput, StateRun

# ── Date helpers ──────────────────────────────────────────────────────────────


def make_dates(start: str, days: int) -> list[date]:
    s = date.fromisoformat(start)
    return [s + timedelta(days=i) for i in range(days)]


# ── Employee builders ─────────────────────────────────────────────────────────


def make_employee(
    emp_id: str = "E001",
    name: str = "Alice",
    attributes: dict[str, str] | None = None,
    balances: dict[str, int] | None = None,
    records: dict[str, list[dict[str, Any]]] | None = None,
    previous_week_days: dict[date, str] | None = None,
    last_month_shift_counts: dict[str, int] | None = None,
    previous_state_run: StateRun | None = None,
) -> Employee:
    return Employee(
        id=emp_id,
        name=name,
        attributes=attributes or {},
        balances=balances or {},
        records=records or {},
        history=EmployeeHistory(
            last_month_shift_counts=last_month_shift_counts or {},
            previous_state_run=previous_state_run,
        ),
        previous_week_days=previous_week_days or {},
    )


# ── Schedule input builder ────────────────────────────────────────────────────


def make_schedule_input(
    employees: list[Employee],
    start: str = "2026-04-07",  # Monday
    days: int = 7,
    states: list[str] | None = None,
    holidays: list[Holiday] | None = None,
) -> ScheduleInput:
    dates = make_dates(start, days)
    return ScheduleInput(
        period_start=dates[0],
        period_end=dates[-1],
        dates=dates,
        employees=employees,
        holidays=holidays or [],
        states=states or ["morning", "afternoon", "night", "week_off"],
    )


# ── CP-SAT model + vars builder ───────────────────────────────────────────────


def make_model(inp: ScheduleInput) -> tuple[cp_model.CpModel, dict]:
    model = cp_model.CpModel()
    vars_dict = create_variables(model, inp)
    vars_dict["penalties"] = []
    return model, vars_dict


def solve(model: cp_model.CpModel) -> tuple[cp_model.CpSolver, cp_model.CpSolverStatus]:
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10
    status = solver.solve(model)
    return solver, status


def get_assignment(solver: cp_model.CpSolver, vars_dict: dict, emp_id: str, d: date) -> str:
    """Return the assigned state for (emp_id, d) from a solved model."""
    x = vars_dict["x"]
    for s in vars_dict["states"]:
        if solver.value(x[(emp_id, d.isoformat(), s)]) == 1:
            return s
    return "?"


# ── Pytest fixtures ───────────────────────────────────────────────────────────


@pytest.fixture
def alice() -> Employee:
    return make_employee("E001", "Alice")


@pytest.fixture
def bob() -> Employee:
    return make_employee("E002", "Bob")


@pytest.fixture
def one_week_inp(alice: Employee) -> ScheduleInput:
    """Single employee, Mon–Sun, 4 states."""
    return make_schedule_input([alice])


@pytest.fixture
def two_emp_inp(alice: Employee, bob: Employee) -> ScheduleInput:
    return make_schedule_input([alice, bob])
