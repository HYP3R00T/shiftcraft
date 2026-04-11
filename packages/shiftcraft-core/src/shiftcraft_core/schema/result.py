"""
Output result schema.

Validates the dict returned by ``format_solution()`` before it leaves the engine.
A ``ValidationError`` here indicates a bug in the formatter or solver output.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field

SolverStatus = Literal["optimal", "feasible", "infeasible", "unknown", "model_invalid"]


class MetadataSchema(BaseModel):
    status: SolverStatus
    solve_time_seconds: Annotated[float, Field(ge=0.0)]
    objective: int | None = None


class ResultSchema(BaseModel):
    """
    The complete output contract returned by ``solve()``.

    When status is ``"optimal"`` or ``"feasible"``, ``schedule`` is a
    date-keyed mapping of employee ID to assigned state.

    When status is ``"infeasible"`` or ``"unknown"``, ``schedule`` is empty.
    """

    status: SolverStatus
    schedule: dict[str, dict[str, str]]
    metadata: MetadataSchema
