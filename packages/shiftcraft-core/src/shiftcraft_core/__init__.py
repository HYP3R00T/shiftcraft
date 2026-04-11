"""shiftcraft-core: constraint-driven workforce scheduler using OR-Tools CP-SAT."""

from __future__ import annotations

from .engine import solve
from .schema import PayloadSchema, ResultSchema

__all__ = ["solve", "PayloadSchema", "ResultSchema"]
