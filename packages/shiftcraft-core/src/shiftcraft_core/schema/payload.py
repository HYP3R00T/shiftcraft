"""
Input payload schema.

Validates the raw dict passed to ``solve()`` before the engine touches it.
A ``ValidationError`` is raised immediately on any structural or type violation.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

# ── Scope ─────────────────────────────────────────────────────────────────────


class WhoAll(BaseModel):
    type: Literal["all"]


class WhoAttribute(BaseModel):
    type: Literal["attribute"]
    key: str
    value: str


class WhoEmployees(BaseModel):
    type: Literal["employees"]
    ids: Annotated[list[str], Field(min_length=1)]


WhoSchema = WhoAll | WhoAttribute | WhoEmployees


class WhenAlways(BaseModel):
    type: Literal["always"]


class WhenDates(BaseModel):
    type: Literal["dates"]
    values: Annotated[list[str], Field(min_length=1)]


class WhenDateRange(BaseModel):
    type: Literal["date_range"]
    start: str
    end: str


class WhenDayOfWeek(BaseModel):
    type: Literal["day_of_week"]
    values: Annotated[list[str], Field(min_length=1)]


class WhenDayType(BaseModel):
    type: Literal["day_type"]
    value: Literal["weekend", "holiday"]


WhenSchema = WhenAlways | WhenDates | WhenDateRange | WhenDayOfWeek | WhenDayType


class ScopeSchema(BaseModel):
    who: Annotated[WhoSchema, Field(discriminator="type")]
    when: Annotated[WhenSchema, Field(discriminator="type")]


# ── Rules ─────────────────────────────────────────────────────────────────────


class RuleSchema(BaseModel):
    model_config = {"extra": "allow"}  # primitive-specific params pass through

    id: str
    type: str
    scope: ScopeSchema
    enforcement: Literal["hard", "soft", "preference"]
    label: str = ""
    weight: Literal["high", "medium", "low"] | None = None
    overrides: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def weight_required_for_soft(self) -> RuleSchema:
        if self.enforcement == "soft" and self.weight is None:
            raise ValueError(f"Rule {self.id!r}: soft rules must specify a weight")
        return self


# ── Settings ──────────────────────────────────────────────────────────────────


class SolverConfigSchema(BaseModel):
    time_limit_seconds: Annotated[int, Field(gt=0)] = 30
    log_progress: bool = False
    num_workers: Annotated[int, Field(ge=0)] = 0
    linearization_level: Annotated[int, Field(ge=0, le=2)] = 1
    relative_gap_limit: Annotated[float, Field(ge=0.0, le=1.0)] = 0.02


class SettingsSchema(BaseModel):
    shifts: Annotated[list[str], Field(min_length=1)]
    leave_types: Annotated[list[str], Field(min_length=1)]
    rules: list[RuleSchema] = Field(default_factory=list)
    solver: SolverConfigSchema = Field(default_factory=SolverConfigSchema)

    @field_validator("shifts", "leave_types")
    @classmethod
    def no_duplicates(cls, v: list[str]) -> list[str]:
        if len(v) != len(set(v)):
            raise ValueError("State names must be unique")
        return v

    @model_validator(mode="after")
    def shifts_and_leave_types_disjoint(self) -> SettingsSchema:
        overlap = set(self.shifts) & set(self.leave_types)
        if overlap:
            raise ValueError(f"States appear in both shifts and leave_types: {overlap}")
        return self


# ── Input ─────────────────────────────────────────────────────────────────────


class PeriodSchema(BaseModel):
    start: str
    end: str

    @model_validator(mode="after")
    def start_before_end(self) -> PeriodSchema:
        from datetime import date

        s = date.fromisoformat(self.start)
        e = date.fromisoformat(self.end)
        if s > e:
            raise ValueError(f"period.start ({self.start}) must not be after period.end ({self.end})")
        return self


class StateRunSchema(BaseModel):
    value: str
    count: Annotated[int, Field(ge=1)]


class EmployeeHistorySchema(BaseModel):
    last_month_shift_counts: dict[str, Annotated[int, Field(ge=0)]] = Field(default_factory=dict)
    previous_state_run: StateRunSchema | None = None


class CompOffRecordSchema(BaseModel):
    earned_date: str
    redeemed_on: str | None = None


class EmployeeSchema(BaseModel):
    id: str
    name: str
    attributes: dict[str, str] = Field(default_factory=dict)
    balances: dict[str, Annotated[int, Field(ge=0)]] = Field(default_factory=dict)
    records: dict[str, list[dict[str, Any]]] = Field(default_factory=dict)
    history: EmployeeHistorySchema = Field(default_factory=EmployeeHistorySchema)
    previous_week_days: dict[str, str] = Field(default_factory=dict)


class HolidaySchema(BaseModel):
    date: str
    locations: list[str] = Field(default_factory=list)


class InputSchema(BaseModel):
    period: PeriodSchema
    team: Annotated[list[EmployeeSchema], Field(min_length=1)]
    holidays: list[HolidaySchema] = Field(default_factory=list)

    @field_validator("team")
    @classmethod
    def unique_employee_ids(cls, v: list[EmployeeSchema]) -> list[EmployeeSchema]:
        ids = [e.id for e in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Employee IDs must be unique")
        return v


# ── Top-level payload ─────────────────────────────────────────────────────────


class PayloadSchema(BaseModel):
    """
    The complete input contract for ``solve()``.

    Validate with ``PayloadSchema.model_validate(raw_dict)`` before passing
    the payload to the engine. A ``ValidationError`` is raised on any violation.
    """

    settings: SettingsSchema
    input: InputSchema
    hint: dict[str, dict[str, str]] | None = None
    """
    Optional warm-start hint. A date-keyed schedule from a previous run
    (``{date_iso: {emp_id: state}}``) that seeds the solver's initial search.
    Providing a good hint can significantly reduce solve time while still
    guaranteeing a fully optimal result.
    """
