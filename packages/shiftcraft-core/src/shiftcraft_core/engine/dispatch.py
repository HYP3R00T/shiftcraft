"""
Rule dispatch loop.

Iterates over all rules in settings, resolves WHO × WHEN scope,
and calls the appropriate primitive handler.
"""

from __future__ import annotations

from typing import Any

from ortools.sat.python import cp_model

from ..primitives import HANDLERS
from ..scope import filter_when, filter_who
from ..types.input import ScheduleInput
from ..types.rules import Settings


def apply_rules(
    model: cp_model.CpModel,
    settings: Settings,
    inp: ScheduleInput,
    vars_dict: dict[str, Any],
) -> None:
    """
    For each rule: resolve scope → call handler.

    Handlers are responsible for adding constraints or penalty terms to
    *model*.  Soft-constraint handlers append to ``vars_dict["penalties"]``.
    """
    for rule in settings.rules:
        handler = HANDLERS.get(rule.type)
        if handler is None:
            raise NotImplementedError(f"No handler registered for primitive type: {rule.type!r}")

        employees = filter_who(rule.scope.who, inp.employees)
        dates = filter_when(rule.scope.when, inp)

        handler(model, rule, employees, dates, inp, vars_dict)
