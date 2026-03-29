---
icon: lucide/file-input
---

# Input format

The engine accepts a single JSON object. This document describes every field, what it means, and how it affects scheduling decisions.

## Top-level structure

The input has four top-level keys:

- `period` — the date range to schedule
- `team` — the list of employees
- `coverage` — staffing requirements per day and shift
- `holidays` — declared public holidays with optional location scope

---

## period

Defines the scheduling window. Both dates are inclusive.

| Field | Type | Description |
|---|---|---|
| `start` | ISO date string | First day of the scheduling period |
| `end` | ISO date string | Last day of the scheduling period |

The engine expands this range into a list of individual dates internally. Every date in the range will have an assignment for every employee.

---

## team

A list of employee objects. Each employee carries their identity, leave requests, and historical context.

### Employee fields

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique identifier for the employee |
| `name` | string | Display name used in output |
| `is_senior` | boolean | Seniority flag (available for future constraint use) |
| `city` | string | Location, used for holiday scoping |
| `comp_off_balance` | integer | Current compensatory off balance |
| `leave_requests` | list | Leave requests for dates within the period |
| `history` | object | Prior month shift counts and comp-off records |
| `previous_week_days` | object | Shift assignments from the previous month that fall in the same ISO week as the period start |

### leave_requests

Each entry in `leave_requests` represents a request for a specific date.

| Field | Type | Description |
|---|---|---|
| `date` | ISO date string | The requested date |
| `leave_type` | string or null | `"annual"`, `"comp_off"`, `"week_off"`, or `null` |

When `leave_type` is `null`, the request is treated as a preference — the engine will try to honor it but may move it to a nearby feasible date. When `leave_type` is set, the request is treated as a hard requirement and must be honored exactly as specified.

### history

| Field | Type | Description |
|---|---|---|
| `last_month_shift_counts` | object | Count of each shift type worked in the previous month |
| `comp_off` | object | Comp-off balance and individual records |

The `last_month_shift_counts` object contains counts for `morning`, `afternoon`, `night`, `regular`, `week_off`, and `leave`. These are used to bias the current period's assignments toward fairness across months.

The `comp_off` object contains:

| Field | Type | Description |
|---|---|---|
| `remaining_count` | integer | Current unredeemed comp-off balance |
| `records` | list | Individual comp-off records with earn date and optional redemption date |

Each record in `records` has:

| Field | Type | Description |
|---|---|---|
| `holiday_date` | ISO date string | The holiday on which the comp-off was earned |
| `redeemed_on` | ISO date string or null | The date it was consumed, or `null` if still available |

### previous_week_days

An optional map of date strings to shift type strings. This covers days from the previous month that fall in the same ISO calendar week as the first days of the scheduling period. The engine uses this to correctly enforce the two-off-days-per-week rule across month boundaries.

---

## coverage

Defines how many people are needed for each shift on each day. Coverage can be specified by day of week, with optional overrides for specific date ranges.

### by_day_of_week

A map from day name (lowercase) to a coverage object. Every day of the week must be present.

Each day's coverage object contains four shift slots: `morning`, `afternoon`, `night`, and `regular`.

Each shift slot has three values:

| Field | Type | Description |
|---|---|---|
| `min` | integer | Minimum required headcount. Falling below this makes the roster invalid. |
| `target` | integer | Desired headcount. The engine tries to reach this but does not require it. |
| `max` | integer | Maximum allowed headcount. Assigning more than this makes the roster invalid. |

Setting `max` to `0` for a shift on a given day effectively disables that shift on that day. This is how the regular shift is disabled on weekends in the default configuration.

### by_date_range

An optional list of date range overrides. Each entry applies a specific coverage configuration to all dates within a range, taking precedence over the day-of-week defaults.

| Field | Type | Description |
|---|---|---|
| `start` | ISO date string | First date of the override range |
| `end` | ISO date string | Last date of the override range |
| `morning` | slot object | Coverage for morning shift |
| `afternoon` | slot object | Coverage for afternoon shift |
| `night` | slot object | Coverage for night shift |
| `regular` | slot object | Coverage for regular shift |

If a date matches multiple overrides, the first matching override in the list is used.

---

## holidays

A list of declared holidays. Holidays affect comp-off entitlement and staffing preference logic.

| Field | Type | Description |
|---|---|---|
| `date` | ISO date string | The holiday date |
| `locations` | list of strings | Cities where this holiday applies. An empty list means the holiday applies globally. |

An employee working on a holiday that applies to their city earns one comp-off entitlement. The engine uses location matching to determine which employees are affected.
