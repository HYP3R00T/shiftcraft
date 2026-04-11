"""Tests for schema/result.py — ResultSchema validation."""

from __future__ import annotations

import pytest
from pydantic import ValidationError
from shiftcraft_core.schema.result import ResultSchema


@pytest.mark.unit
def test_valid_optimal_result_passes():
    ResultSchema.model_validate({
        "status": "optimal",
        "schedule": {"2026-04-01": {"E001": "morning"}},
        "metadata": {"status": "optimal", "solve_time_seconds": 0.5, "objective": 100},
    })


@pytest.mark.unit
def test_valid_infeasible_result_passes():
    ResultSchema.model_validate({
        "status": "infeasible",
        "schedule": {},
        "metadata": {"status": "infeasible", "solve_time_seconds": 1.2, "objective": None},
    })


@pytest.mark.unit
def test_invalid_status_raises():
    with pytest.raises(ValidationError):
        ResultSchema.model_validate({
            "status": "broken",
            "schedule": {},
            "metadata": {"status": "broken", "solve_time_seconds": 0.1, "objective": None},
        })


@pytest.mark.unit
def test_negative_solve_time_raises():
    with pytest.raises(ValidationError):
        ResultSchema.model_validate({
            "status": "optimal",
            "schedule": {},
            "metadata": {"status": "optimal", "solve_time_seconds": -1.0, "objective": None},
        })


@pytest.mark.unit
def test_missing_metadata_raises():
    with pytest.raises(ValidationError):
        ResultSchema.model_validate({"status": "optimal", "schedule": {}})
