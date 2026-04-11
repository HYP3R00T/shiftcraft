"""
Integration test: full solve pipeline against the example payload.

Verifies that the engine produces a valid, optimal schedule that satisfies
all hard constraints declared in the example settings.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest
from shiftcraft_core import solve

EXAMPLE = Path(__file__).resolve().parents[3] / "examples" / "basic_app"


@pytest.fixture(scope="module")
def payload() -> dict:
    settings = json.loads((EXAMPLE / "settings.json").read_text())
    inp = json.loads((EXAMPLE / "input.json").read_text())
    return {"settings": settings, "input": inp}


@pytest.fixture(scope="module")
def result(payload) -> dict:
    return solve(payload)


# ── Status ────────────────────────────────────────────────────────────────────


@pytest.mark.integration
def test_status_is_optimal_or_feasible(result):
    assert result["status"] in ("optimal", "feasible")


@pytest.mark.integration
def test_metadata_present(result):
    meta = result["metadata"]
    assert "solve_time_seconds" in meta
    assert meta["solve_time_seconds"] >= 0


# ── Schedule shape ────────────────────────────────────────────────────────────


@pytest.mark.integration
def test_schedule_covers_all_dates(payload, result):
    start = date.fromisoformat(payload["input"]["period"]["start"])
    end = date.fromisoformat(payload["input"]["period"]["end"])
    expected_dates = {
        (start + __import__("datetime").timedelta(days=i)).isoformat() for i in range((end - start).days + 1)
    }
    assert set(result["schedule"].keys()) == expected_dates


@pytest.mark.integration
def test_every_employee_assigned_every_day(payload, result):
    emp_ids = {e["id"] for e in payload["input"]["team"]}
    for d_iso, emp_map in result["schedule"].items():
        assert set(emp_map.keys()) == emp_ids, f"Missing employees on {d_iso}"


@pytest.mark.integration
def test_all_states_are_valid(payload, result):
    valid = set(payload["settings"]["shifts"]) | set(payload["settings"]["leave_types"])
    for d_iso, emp_map in result["schedule"].items():
        for emp_id, state in emp_map.items():
            assert state in valid, f"{emp_id} on {d_iso} has invalid state {state!r}"


# ── Hard constraint verification ──────────────────────────────────────────────


@pytest.mark.integration
def test_no_night_to_morning_transition(payload, result):
    """Hard rule: night → morning on consecutive days is forbidden."""
    schedule = result["schedule"]
    dates = sorted(schedule.keys())
    emp_ids = [e["id"] for e in payload["input"]["team"]]
    for i in range(len(dates) - 1):
        d1, d2 = dates[i], dates[i + 1]
        for emp_id in emp_ids:
            s1 = schedule[d1][emp_id]
            s2 = schedule[d2][emp_id]
            assert not (s1 == "night" and s2 == "morning"), f"{emp_id}: night→morning on {d1}→{d2}"


@pytest.mark.integration
def test_exactly_two_week_offs_per_full_iso_week(payload, result):
    """Hard rule: exactly 2 week_offs per ISO calendar week (full weeks only)."""
    from collections import defaultdict

    schedule = result["schedule"]
    emp_ids = [e["id"] for e in payload["input"]["team"]]

    # Build per-employee, per-week counts.
    week_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    week_day_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for d_iso, emp_map in schedule.items():
        d = date.fromisoformat(d_iso)
        wk = f"{d.isocalendar().year}-W{d.isocalendar().week:02d}"
        for emp_id in emp_ids:
            week_day_counts[emp_id][wk] += 1
            if emp_map[emp_id] == "week_off":
                week_counts[emp_id][wk] += 1

    for emp_id in emp_ids:
        for wk, day_count in week_day_counts[emp_id].items():
            if day_count < 7:
                continue  # partial boundary week — skip
            offs = week_counts[emp_id].get(wk, 0)
            assert offs == 2, f"{emp_id} W{wk}: {offs} week_offs (expected 2)"


@pytest.mark.integration
def test_at_most_two_employees_off_per_day(payload, result):
    """Hard rule: at most 2 employees on any off state on any day."""
    off_states = set(payload["settings"]["leave_types"])
    for d_iso, emp_map in result["schedule"].items():
        off_count = sum(1 for s in emp_map.values() if s in off_states)
        assert off_count <= 2, f"{d_iso}: {off_count} employees off (max 2)"


@pytest.mark.integration
def test_comp_off_within_balance(payload, result):
    """Hard rule: comp_off usage must not exceed each employee's balance."""
    balances = {e["id"]: e.get("balances", {}).get("comp_off", 0) for e in payload["input"]["team"]}
    usage: dict[str, int] = dict.fromkeys(balances, 0)
    for emp_map in result["schedule"].values():
        for emp_id, state in emp_map.items():
            if state == "comp_off":
                usage[emp_id] += 1
    for emp_id, used in usage.items():
        assert used <= balances[emp_id], f"{emp_id}: used {used} comp_off but balance is {balances[emp_id]}"
