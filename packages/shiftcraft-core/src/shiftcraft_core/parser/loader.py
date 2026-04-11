"""
load(payload) -> (Settings, ScheduleInput)

Validates the raw API payload against ``PayloadSchema``, then converts it
into fully typed internal objects.  A ``pydantic.ValidationError`` is raised
on any structural or type violation before the engine is invoked.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from ..schema.payload import PayloadSchema
from ..types.input import Employee, EmployeeHistory, Holiday, ScheduleInput, StateRun
from ..types.rules import (
    BalanceSource,
    Rule,
    RuleEnforcement,
    RuleWeight,
    Scope,
    Settings,
    WhenFilter,
    WhoFilter,
)

# ── Helpers ───────────────────────────────────────────────────────────────────


def _date(s: str) -> date:
    return date.fromisoformat(s)


def _expand_dates(start: date, end: date) -> list[date]:
    out: list[date] = []
    cur = start
    while cur <= end:
        out.append(cur)
        cur += timedelta(days=1)
    return out


# ── WHO / WHEN ────────────────────────────────────────────────────────────────


def _parse_who(raw: dict[str, Any]) -> WhoFilter:
    t = raw["type"]
    match t:
        case "all":
            return WhoFilter(type="all")
        case "attribute":
            return WhoFilter(type="attribute", key=raw["key"], value=raw["value"])
        case "employees":
            return WhoFilter(type="employees", ids=tuple(raw["ids"]))
        case _:
            raise ValueError(f"Unknown WHO type: {t!r}")


def _parse_when(raw: dict[str, Any]) -> WhenFilter:
    t = raw["type"]
    match t:
        case "always":
            return WhenFilter(type="always")
        case "dates":
            return WhenFilter(type="dates", values=tuple(raw["values"]))
        case "date_range":
            return WhenFilter(type="date_range", start=raw["start"], end=raw["end"])
        case "day_of_week":
            return WhenFilter(type="day_of_week", values=tuple(raw["values"]))
        case "day_type":
            return WhenFilter(type="day_type", value=raw["value"])
        case _:
            raise ValueError(f"Unknown WHEN type: {t!r}")


# ── Rules ─────────────────────────────────────────────────────────────────────


def _parse_balance_source(raw: dict[str, Any]) -> BalanceSource:
    return BalanceSource(
        type=raw["type"],
        key=raw["key"],
        validity_days=raw.get("validity_days"),
    )


def _parse_rule(raw: dict[str, Any]) -> Rule:
    enforcement = RuleEnforcement(raw["enforcement"])
    weight_raw = raw.get("weight")
    weight = RuleWeight(weight_raw) if weight_raw else None

    # Extract primitive-specific params (everything except the envelope fields).
    envelope_keys = {"id", "label", "type", "scope", "enforcement", "weight", "overrides"}
    params: dict[str, Any] = {k: v for k, v in raw.items() if k not in envelope_keys}

    # Normalise balance_source if present
    if "balance_source" in params:
        params["balance_source"] = _parse_balance_source(params["balance_source"])

    return Rule(
        id=raw["id"],
        type=raw["type"],
        scope=Scope(
            who=_parse_who(raw["scope"]["who"]),
            when=_parse_when(raw["scope"]["when"]),
        ),
        enforcement=enforcement,
        weight=weight,
        label=raw.get("label", ""),
        overrides=tuple(raw.get("overrides", [])),
        params=params,
    )


# ── Settings ──────────────────────────────────────────────────────────────────


def _parse_settings(raw: dict[str, Any]) -> Settings:
    return Settings(
        shifts=list(raw["shifts"]),
        leave_types=list(raw["leave_types"]),
        rules=[_parse_rule(r) for r in raw.get("rules", [])],
        solver=dict(raw.get("solver", {})),
    )


# ── Employees ─────────────────────────────────────────────────────────────────


def _parse_employee(raw: dict[str, Any]) -> Employee:
    hist_raw = raw.get("history", {})
    prev_run_raw = hist_raw.get("previous_state_run")
    history = EmployeeHistory(
        last_month_shift_counts=dict(hist_raw.get("last_month_shift_counts", {})),
        previous_state_run=(
            StateRun(value=prev_run_raw["value"], count=prev_run_raw["count"]) if prev_run_raw else None
        ),
    )
    previous_week_days: dict[date, str] = {
        _date(d): s
        for d, s in raw.get("previous_week_days", {}).items()
        if s  # skip empty strings
    }
    return Employee(
        id=raw["id"],
        name=raw["name"],
        attributes=dict(raw.get("attributes", {})),
        balances=dict(raw.get("balances", {})),
        records=dict(raw.get("records", {})),
        history=history,
        previous_week_days=previous_week_days,
    )


# ── Holidays ──────────────────────────────────────────────────────────────────


def _parse_holiday(raw: dict[str, Any]) -> Holiday:
    return Holiday(
        date=_date(raw["date"]),
        locations=list(raw.get("locations", [])),
    )


# ── Entry point ───────────────────────────────────────────────────────────────


def load(payload: dict[str, Any]) -> tuple[Settings, ScheduleInput]:
    """
    Validate and parse the raw API payload.

    Args:
        payload: Dict with top-level keys ``"settings"`` and ``"input"``.

    Returns:
        ``(settings, schedule_input)`` — fully typed objects ready for the engine.

    Raises:
        pydantic.ValidationError: If the payload does not conform to the input schema.
    """
    PayloadSchema.model_validate(payload)

    settings = _parse_settings(payload["settings"])

    inp_raw = payload["input"]
    period_start = _date(inp_raw["period"]["start"])
    period_end = _date(inp_raw["period"]["end"])

    schedule_input = ScheduleInput(
        period_start=period_start,
        period_end=period_end,
        dates=_expand_dates(period_start, period_end),
        employees=[_parse_employee(e) for e in inp_raw["team"]],
        holidays=[_parse_holiday(h) for h in inp_raw.get("holidays", [])],
        states=settings.all_states,
    )

    return settings, schedule_input
