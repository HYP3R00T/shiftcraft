"""Engine: variable creation, rule dispatch, solve orchestration."""

from __future__ import annotations

from .solver import build_model, solve

__all__ = ["build_model", "solve"]
