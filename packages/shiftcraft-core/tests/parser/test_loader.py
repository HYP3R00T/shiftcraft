"""Tests for parser/loader.py — load() function."""

from __future__ import annotations

import pytest
from pydantic import ValidationError
from shiftcraft_core.parser.loader import load


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
def test_load_returns_settings_and_input():
    settings, inp = load(_base_payload())
    assert settings.shifts == ["morning", "afternoon", "night"]
    assert settings.leave_types == ["week_off", "annual"]
    assert len(inp.employees) == 1
    assert inp.employees[0].id == "E001"


@pytest.mark.unit
def test_load_expands_dates():
    _, inp = load(_base_payload())
    assert len(inp.dates) == 3


@pytest.mark.unit
def test_load_states_are_shifts_plus_leave():
    settings, inp = load(_base_payload())
    assert inp.states == settings.all_states
    assert inp.states == ["morning", "afternoon", "night", "week_off", "annual"]


@pytest.mark.unit
def test_load_employee_attributes_parsed():
    p = _base_payload()
    p["input"]["team"] = [{"id": "E001", "name": "Alice", "attributes": {"city": "Hyderabad"}}]
    _, inp = load(p)
    assert inp.employees[0].attributes == {"city": "Hyderabad"}


@pytest.mark.unit
def test_load_employee_balances_parsed():
    p = _base_payload()
    p["input"]["team"] = [{"id": "E001", "name": "Alice", "balances": {"annual": 5}}]
    _, inp = load(p)
    assert inp.employees[0].balances == {"annual": 5}


@pytest.mark.unit
def test_load_previous_state_run_parsed():
    p = _base_payload()
    p["input"]["team"] = [
        {
            "id": "E001",
            "name": "Alice",
            "history": {"previous_state_run": {"value": "night", "count": 2}},
        }
    ]
    _, inp = load(p)
    run = inp.employees[0].history.previous_state_run
    assert run is not None
    assert run.value == "night"
    assert run.count == 2


@pytest.mark.unit
def test_load_holiday_parsed():
    p = _base_payload()
    p["input"]["holidays"] = [{"date": "2026-04-01", "locations": ["Hyderabad"]}]
    _, inp = load(p)
    assert len(inp.holidays) == 1
    assert inp.holidays[0].locations == ["Hyderabad"]


@pytest.mark.unit
def test_load_rule_params_passed_through():
    p = _base_payload([
        {
            "id": "r1",
            "type": "daily_count",
            "value": "morning",
            "operator": ">=",
            "count": 1,
            "scope": {"who": {"type": "all"}, "when": {"type": "always"}},
            "enforcement": "hard",
        }
    ])
    settings, _ = load(p)
    assert settings.rules[0].params["value"] == "morning"
    assert settings.rules[0].params["count"] == 1


@pytest.mark.unit
def test_load_unknown_who_type_raises():
    p = _base_payload([
        {
            "id": "r1",
            "type": "daily_count",
            "value": "morning",
            "operator": ">=",
            "count": 1,
            "scope": {"who": {"type": "robot"}, "when": {"type": "always"}},
            "enforcement": "hard",
        }
    ])
    with pytest.raises((ValueError, ValidationError)):
        load(p)
