from __future__ import annotations

from typing import Protocol

from shiftcraft_core.context import CompileContext
from shiftcraft_core.models import ConstraintSpec


class ConstraintHandler(Protocol):
    """Compiles one declarative constraint into model constraints/objective terms."""

    def compile(self, spec: ConstraintSpec, context: CompileContext) -> None: ...


class ConstraintRegistry:
    """Registry that resolves constraint types to handlers."""

    def __init__(self) -> None:
        self._handlers: dict[str, ConstraintHandler] = {}

    def register(self, name: str, handler: ConstraintHandler) -> None:
        if name in self._handlers:
            raise ValueError(f"Constraint handler '{name}' is already registered")
        self._handlers[name] = handler

    def get(self, name: str) -> ConstraintHandler:
        try:
            return self._handlers[name]
        except KeyError as exc:
            raise ValueError(f"Unknown constraint type: {name}") from exc

    def compile(self, spec: ConstraintSpec, context: CompileContext) -> None:
        handler = self.get(spec.type)
        handler.compile(spec, context)

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._handlers))
