"""Tests for scope/filters.py — filter_who() and filter_when()."""

from __future__ import annotations

from datetime import date

import pytest
from shiftcraft_core.scope.filters import filter_when, filter_who
from shiftcraft_core.types.input import Holiday
from shiftcraft_core.types.rules import WhenFilter, WhoFilter

from ..conftest import make_employee, make_schedule_input

# ── WHO ───────────────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_who_all_returns_everyone():
    emps = [make_employee("E001"), make_employee("E002")]
    assert len(filter_who(WhoFilter(type="all"), emps)) == 2


@pytest.mark.unit
def test_who_employees_filters_by_id():
    emps = [make_employee("E001"), make_employee("E002"), make_employee("E003")]
    result = filter_who(WhoFilter(type="employees", ids=("E001", "E003")), emps)
    assert [e.id for e in result] == ["E001", "E003"]


@pytest.mark.unit
def test_who_attribute_matches_key_value():
    emps = [
        make_employee("E001", attributes={"role": "senior"}),
        make_employee("E002", attributes={"role": "junior"}),
        make_employee("E003", attributes={"role": "senior"}),
    ]
    result = filter_who(WhoFilter(type="attribute", key="role", value="senior"), emps)
    assert [e.id for e in result] == ["E001", "E003"]


@pytest.mark.unit
def test_who_attribute_no_match_returns_empty():
    emps = [make_employee("E001", attributes={"role": "junior"})]
    assert filter_who(WhoFilter(type="attribute", key="role", value="senior"), emps) == []


@pytest.mark.unit
def test_who_unknown_type_raises():
    with pytest.raises(ValueError, match="Unknown WHO type"):
        filter_who(WhoFilter(type="unknown"), [make_employee()])


# ── WHEN ──────────────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_when_always_returns_all_dates():
    inp = make_schedule_input([make_employee()], start="2026-04-07", days=7)
    assert filter_when(WhenFilter(type="always"), inp) == inp.dates


@pytest.mark.unit
def test_when_dates_returns_matching():
    inp = make_schedule_input([make_employee()], start="2026-04-07", days=7)
    result = filter_when(WhenFilter(type="dates", values=("2026-04-07", "2026-04-09")), inp)
    assert len(result) == 2
    assert result[0].isoformat() == "2026-04-07"
    assert result[1].isoformat() == "2026-04-09"


@pytest.mark.unit
def test_when_dates_out_of_period_ignored():
    inp = make_schedule_input([make_employee()], start="2026-04-07", days=3)
    assert filter_when(WhenFilter(type="dates", values=("2026-04-01",)), inp) == []


@pytest.mark.unit
def test_when_date_range_inclusive():
    inp = make_schedule_input([make_employee()], start="2026-04-07", days=7)
    result = filter_when(WhenFilter(type="date_range", start="2026-04-08", end="2026-04-10"), inp)
    assert len(result) == 3
    assert result[0].isoformat() == "2026-04-08"
    assert result[-1].isoformat() == "2026-04-10"


@pytest.mark.unit
def test_when_day_of_week_filters_correctly():
    inp = make_schedule_input([make_employee()], start="2026-04-07", days=7)
    result = filter_when(WhenFilter(type="day_of_week", values=("saturday", "sunday")), inp)
    assert len(result) == 2
    assert all(d.weekday() >= 5 for d in result)


@pytest.mark.unit
def test_when_day_type_weekend():
    inp = make_schedule_input([make_employee()], start="2026-04-07", days=7)
    result = filter_when(WhenFilter(type="day_type", value="weekend"), inp)
    assert all(inp.is_weekend(d) for d in result)
    assert len(result) == 2


@pytest.mark.unit
def test_when_day_type_holiday():
    holiday = Holiday(date=date(2026, 4, 9))
    inp = make_schedule_input([make_employee()], start="2026-04-07", days=7, holidays=[holiday])
    result = filter_when(WhenFilter(type="day_type", value="holiday"), inp)
    assert len(result) == 1
    assert result[0].isoformat() == "2026-04-09"


@pytest.mark.unit
def test_when_unknown_type_raises():
    inp = make_schedule_input([make_employee()], start="2026-04-07", days=3)
    with pytest.raises(ValueError, match="Unknown WHEN type"):
        filter_when(WhenFilter(type="unknown"), inp)


@pytest.mark.unit
def test_when_unknown_day_type_raises():
    inp = make_schedule_input([make_employee()], start="2026-04-07", days=3)
    with pytest.raises(ValueError, match="Unknown day_type"):
        filter_when(WhenFilter(type="day_type", value="lunar"), inp)
