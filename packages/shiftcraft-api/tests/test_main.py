"""Tests for shiftcraft_api/main.py."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from shiftcraft_api.main import app

client = TestClient(app)

EXAMPLE = Path(__file__).resolve().parents[3] / "examples" / "basic_app"


@pytest.fixture(scope="module")
def valid_payload() -> dict:
    return {
        "settings": json.loads((EXAMPLE / "settings.json").read_text()),
        "input": json.loads((EXAMPLE / "input.json").read_text()),
    }


# ── /health ───────────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ── /schedule ─────────────────────────────────────────────────────────────────


@pytest.mark.integration
def test_schedule_returns_200(valid_payload):
    response = client.post("/schedule", json=valid_payload)
    assert response.status_code == 200


@pytest.mark.integration
def test_schedule_result_status(valid_payload):
    response = client.post("/schedule", json=valid_payload)
    data = response.json()
    assert data["status"] in ("optimal", "feasible")


@pytest.mark.integration
def test_schedule_result_has_schedule_and_metadata(valid_payload):
    response = client.post("/schedule", json=valid_payload)
    data = response.json()
    assert "schedule" in data
    assert "metadata" in data


@pytest.mark.unit
def test_schedule_invalid_payload_returns_422():
    response = client.post("/schedule", json={"bad": "payload"})
    assert response.status_code == 422


@pytest.mark.unit
def test_schedule_empty_team_returns_422():
    response = client.post(
        "/schedule",
        json={
            "settings": {
                "shifts": ["morning"],
                "leave_types": ["week_off"],
                "rules": [],
            },
            "input": {
                "period": {"start": "2026-04-01", "end": "2026-04-03"},
                "team": [],
            },
        },
    )
    assert response.status_code == 422


@pytest.mark.unit
def test_schedule_overlapping_states_returns_422():
    response = client.post(
        "/schedule",
        json={
            "settings": {
                "shifts": ["morning"],
                "leave_types": ["morning"],  # overlap
                "rules": [],
            },
            "input": {
                "period": {"start": "2026-04-01", "end": "2026-04-01"},
                "team": [{"id": "E001", "name": "Alice"}],
            },
        },
    )
    assert response.status_code == 422
