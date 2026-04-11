"""Tests for schema/payload.py — PayloadSchema validation."""

from __future__ import annotations

import pytest
from pydantic import ValidationError
from shiftcraft_core.schema.payload import PayloadSchema


def _base_payload(extra_rules: list | None = None) -> dict:
    return {
        "settings": {
            "shifts": ["morning", "afternoon", "night"],
            "leave_types": ["week_off", "annual"],
            "rules": extra_rules or [],
        },
        "input": {
            "period": {"start": "2026-04-01", "end": "2026-04-03"},
            "team": [{"id": "E001", "name": "Alice"}],
        },
    }


@pytest.mark.unit
def test_valid_payload_passes_schema():
    PayloadSchema.model_validate(_base_payload())


@pytest.mark.unit
def test_missing_settings_key_raises():
    with pytest.raises(ValidationError):
        PayloadSchema.model_validate({"input": _base_payload()["input"]})


@pytest.mark.unit
def test_missing_input_key_raises():
    with pytest.raises(ValidationError):
        PayloadSchema.model_validate({"settings": _base_payload()["settings"]})


@pytest.mark.unit
def test_empty_shifts_raises():
    p = _base_payload()
    p["settings"]["shifts"] = []
    with pytest.raises(ValidationError):
        PayloadSchema.model_validate(p)


@pytest.mark.unit
def test_duplicate_shifts_raises():
    p = _base_payload()
    p["settings"]["shifts"] = ["morning", "morning"]
    with pytest.raises(ValidationError):
        PayloadSchema.model_validate(p)


@pytest.mark.unit
def test_overlapping_shifts_and_leave_types_raises():
    p = _base_payload()
    p["settings"]["leave_types"] = ["morning", "week_off"]
    with pytest.raises(ValidationError):
        PayloadSchema.model_validate(p)


@pytest.mark.unit
def test_soft_rule_without_weight_raises():
    p = _base_payload([
        {
            "id": "r1",
            "type": "daily_count",
            "value": "morning",
            "operator": ">=",
            "count": 1,
            "scope": {"who": {"type": "all"}, "when": {"type": "always"}},
            "enforcement": "soft",
        }
    ])
    with pytest.raises(ValidationError):
        PayloadSchema.model_validate(p)


@pytest.mark.unit
def test_period_start_after_end_raises():
    p = _base_payload()
    p["input"]["period"] = {"start": "2026-04-10", "end": "2026-04-01"}
    with pytest.raises(ValidationError):
        PayloadSchema.model_validate(p)


@pytest.mark.unit
def test_duplicate_employee_ids_raises():
    p = _base_payload()
    p["input"]["team"] = [
        {"id": "E001", "name": "Alice"},
        {"id": "E001", "name": "Bob"},
    ]
    with pytest.raises(ValidationError):
        PayloadSchema.model_validate(p)


@pytest.mark.unit
def test_empty_team_raises():
    p = _base_payload()
    p["input"]["team"] = []
    with pytest.raises(ValidationError):
        PayloadSchema.model_validate(p)


@pytest.mark.unit
def test_negative_balance_raises():
    p = _base_payload()
    p["input"]["team"] = [{"id": "E001", "name": "Alice", "balances": {"annual": -1}}]
    with pytest.raises(ValidationError):
        PayloadSchema.model_validate(p)
