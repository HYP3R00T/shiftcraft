from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from shiftcraft_core.models import ConstraintMode, ConstraintSpec, ObjectiveConfig, Problem


def _as_mode(raw: Any) -> ConstraintMode:
    if raw not in {"hard", "soft"}:
        msg = f"Constraint mode must be 'hard' or 'soft', got: {raw!r}"
        raise ValueError(msg)
    return raw


def parse_payload(payload: Mapping[str, Any] | str) -> Problem:
    """Parse JSON-like payload into validated intermediate representation."""

    data = json.loads(payload) if isinstance(payload, str) else dict(payload)

    employees_raw = data.get("employees")
    if not isinstance(employees_raw, list) or not employees_raw:
        raise ValueError("'employees' must be a non-empty list")
    employees = tuple(str(employee) for employee in employees_raw)

    days = data.get("days")
    if not isinstance(days, int) or days <= 0:
        raise ValueError("'days' must be a positive integer")

    shifts_raw = data.get("shifts")
    if not isinstance(shifts_raw, list) or not shifts_raw:
        raise ValueError("'shifts' must be a non-empty list")
    shifts = tuple(str(shift) for shift in shifts_raw)

    constraints_raw = data.get("constraints", [])
    if not isinstance(constraints_raw, list):
        raise ValueError("'constraints' must be a list")

    constraints: list[ConstraintSpec] = []
    for raw_spec in constraints_raw:
        if not isinstance(raw_spec, Mapping):
            raise ValueError("Each constraint must be an object")

        kind = raw_spec.get("type")
        if not isinstance(kind, str) or not kind.strip():
            raise ValueError("Constraint 'type' must be a non-empty string")

        mode = _as_mode(raw_spec.get("mode"))

        params = raw_spec.get("params", {})
        if not isinstance(params, Mapping):
            raise ValueError(f"Constraint '{kind}' params must be an object")

        weight_raw = raw_spec.get("weight", 1)
        if not isinstance(weight_raw, int) or weight_raw <= 0:
            raise ValueError(f"Constraint '{kind}' weight must be a positive integer")
        if mode == "soft" and "weight" not in raw_spec:
            raise ValueError(f"Soft constraint '{kind}' must provide a 'weight'")

        constraints.append(
            ConstraintSpec(
                type=kind,
                mode=mode,
                params=dict(params),
                weight=weight_raw,
            )
        )

    objective_raw = data.get("objective", {})
    if not isinstance(objective_raw, Mapping):
        raise ValueError("'objective' must be an object when provided")

    assignment_weight = objective_raw.get("assignment_weight", 1)
    fairness_weight = objective_raw.get("fairness_weight", 1)
    if not isinstance(assignment_weight, int) or assignment_weight < 0:
        raise ValueError("'objective.assignment_weight' must be an integer >= 0")
    if not isinstance(fairness_weight, int) or fairness_weight < 0:
        raise ValueError("'objective.fairness_weight' must be an integer >= 0")

    return Problem(
        employees=employees,
        days=days,
        shifts=shifts,
        constraints=tuple(constraints),
        objective=ObjectiveConfig(
            assignment_weight=assignment_weight,
            fairness_weight=fairness_weight,
        ),
    )
