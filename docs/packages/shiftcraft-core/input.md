---
icon: lucide/file-input
---

# Input format

The engine accepts a single JSON object with two top-level keys: `settings` and `input`.

`settings` describes the rules of the game — shifts, leave types, and constraints. It is typically shared across scheduling runs for the same team.

`input` describes the specific run — the period, the team, and any public holidays.

```json
{
  "settings": { ... },
  "input": { ... }
}
```

---

## settings

### shifts

An ordered list of working-state names. These are the shift types employees can be assigned to on any given day.

```json
"shifts": ["morning", "afternoon", "night", "regular"]
```

### leave_types

An ordered list of off-state names. These are the non-working states an employee can be assigned.

```json
"leave_types": ["week_off", "annual", "comp_off", "public_holiday"]
```

Together, `shifts` and `leave_types` define the complete set of valid states. Every employee will receive exactly one state per day in the scheduling period.

### solver

Optional solver configuration.

| Field | Type | Default | Description |
|---|---|---|---|
| `time_limit_seconds` | integer | `30` | Maximum wall-clock time the solver may run |
| `log_progress` | boolean | `false` | Whether to emit solver search logs |
| `num_workers` | integer | `0` | Number of parallel search workers. `0` = auto-detect. Has no effect on single-core environments (e.g. AWS Lambda). |
| `linearization_level` | integer | `1` | Controls how aggressively the solver linearises the model. `0` = minimal, `1` = standard (recommended), `2` = aggressive. Higher values improve optimality proofs but slow down finding the first solution. |
| `relative_gap_limit` | float | `0.02` | Stop as soon as a solution within this fraction of optimal is found. `0.0` = prove optimality (slowest). `0.02` = stop within 2% of optimal (recommended for production — roughly halves solve time with negligible quality difference). `0.05` = stop within 5% (fastest, noticeable quality trade-off). |

### rules

A list of rule objects. Each rule targets a subset of employees and days, and either enforces a hard constraint or expresses a soft preference.

Every rule has the following envelope fields:

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | Unique identifier for the rule |
| `label` | string | no | Human-readable description |
| `type` | string | yes | The primitive type — see [rule types](#rule-types) below |
| `scope` | object | yes | WHO and WHEN filters — see [scope](#scope) below |
| `enforcement` | string | yes | `"hard"`, `"soft"`, or `"preference"` |
| `weight` | string | soft/preference only | `"high"`, `"medium"`, or `"low"` |
| `overrides` | list of strings | no | IDs of rules this rule supersedes |

All remaining fields are primitive-specific and documented under [rule types](#rule-types).

---

## scope

Every rule has a `scope` with two sub-objects: `who` and `when`.

### who

Controls which employees the rule applies to.

| `type` | Additional fields | Description |
|---|---|---|
| `"all"` | — | Applies to every employee |
| `"attribute"` | `key`, `value` | Applies to employees whose `attributes[key] == value` |
| `"employees"` | `ids` (list of strings) | Applies to the listed employee IDs only |

### when

Controls which days the rule applies to.

| `type` | Additional fields | Description |
|---|---|---|
| `"always"` | — | Applies to every day in the period |
| `"dates"` | `values` (list of ISO date strings) | Applies only to the listed dates |
| `"date_range"` | `start`, `end` (ISO date strings) | Applies to all dates in the range, inclusive |
| `"day_of_week"` | `values` (list of lowercase day names) | Applies to matching weekdays, e.g. `["monday", "friday"]` |
| `"day_type"` | `value` | `"weekend"` or `"holiday"` |

---

## Rule types

### `value_exclusion`

Prevents one or more states from being assigned at all within the scope.

| Field | Type | Description |
|---|---|---|
| `values` | list of strings | States that must not be assigned |

### `value_assignment`

Forces or prefers a specific state on the scoped days.

| Field | Type | Description |
|---|---|---|
| `value` | string | The state to assign |

When `enforcement` is `"hard"`, the assignment is mandatory. When `"preference"`, the solver tries to honor it but may override it to satisfy hard constraints.

### `count_per_period`

Constrains how many times a state appears for each employee across the full period.

| Field | Type | Description |
|---|---|---|
| `value` | string | The state to count |
| `operator` | string | `"=="`, `">="`, or `"<="` |
| `count` | integer | The bound |

### `count_per_week`

Constrains how many times a state appears for each employee within each ISO calendar week. Partial boundary weeks are handled using `previous_week_days`.

| Field | Type | Description |
|---|---|---|
| `value` | string | The state to count |
| `operator` | string | `"=="`, `">="`, or `"<="` |
| `count` | integer | The bound |

### `count_per_window`

Constrains how many times a state appears within a rolling window of days.

| Field | Type | Description |
|---|---|---|
| `value` | string | The state to count |
| `operator` | string | `"=="`, `">="`, or `"<="` |
| `count` | integer | The bound |
| `window_days` | integer | Length of the rolling window in days |

### `daily_count`

Constrains how many employees are assigned a given state on each day within the scope. `value` may be a single string or a list of strings (the count applies to the combined total).

| Field | Type | Description |
|---|---|---|
| `value` | string or list of strings | The state(s) to count |
| `operator` | string | `"=="`, `">="`, or `"<="` |
| `count` | integer | The bound |

### `daily_ratio`

Constrains the ratio of employees in a state relative to a denominator group on each day.

| Field | Type | Description |
|---|---|---|
| `numerator_value` | string | The state being measured |
| `numerator_who` | WHO filter object | Which employees form the numerator |
| `denominator_who` | WHO filter object | Which employees form the denominator |
| `operator` | string | `">="` or `"<="` |
| `ratio` | float | The target ratio, e.g. `0.5` |

### `pair_sequence`

Constrains or forbids a specific state transition between consecutive days.

| Field | Type | Description |
|---|---|---|
| `from_value` | string | The state on day N |
| `to_value` | string | The state on day N+1 |
| `gap_days` | integer | Number of days between the two states (typically `1`) |
| `forbidden` | boolean | `true` to forbid the transition, `false` to require it |

### `run_sequence`

Enforces a consequence after a run of a state. For example: after N consecutive nights, the next M days must not be morning.

| Field | Type | Description |
|---|---|---|
| `trigger_value` | string | The state that triggers the rule |
| `trigger_count` | integer | How many consecutive days of `trigger_value` trigger the rule |
| `then_value` | string | The state that must or must not follow |
| `then_operator` | string | `"=="` or `"!="` |
| `then_count` | integer | How many days the consequence applies to |
| `then_days` | integer | How many days after the run the consequence window starts |

### `count_bounded_by_balance`

Caps how many times a state can be assigned per employee based on a per-person numeric balance or earned records.

| Field | Type | Description |
|---|---|---|
| `value` | string | The state being capped |
| `balance_source` | object | Describes where to read the per-person limit |

`balance_source` fields:

| Field | Type | Description |
|---|---|---|
| `type` | string | `"numeric"` to read from `employee.balances`, or `"records"` to count unredeemed records |
| `key` | string | The key to look up in `balances` or `records` |
| `validity_days` | integer | Records type only — records older than this many days are ignored |

### `spread_per_employee`

Soft constraint. Penalizes large differences in how many times each state in a set is assigned to the same employee.

| Field | Type | Description |
|---|---|---|
| `values` | list of strings | The states to balance |
| `max_diff` | integer | The maximum allowed difference between the highest and lowest count |

### `spread_across_team`

Soft constraint. Penalizes large differences in how many times a state is assigned across different employees.

| Field | Type | Description |
|---|---|---|
| `value` | string | The state to balance |
| `max_diff` | integer | The maximum allowed difference between the most and least assigned employees |
| `count_when` | WHEN filter object | Optional — restricts which days are counted (e.g. weekends only) |

---

## input

### period

Defines the scheduling window. Both dates are inclusive.

| Field | Type | Description |
|---|---|---|
| `start` | ISO date string | First day of the period |
| `end` | ISO date string | Last day of the period |

The engine assigns exactly one state to every employee for every date in this range.

### team

A list of employee objects.

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | Unique identifier, used as the key in the output schedule |
| `name` | string | yes | Display name |
| `attributes` | object | no | Free-form string map used for WHO scope targeting, e.g. `{"city": "Hyderabad", "seniority": "senior"}` |
| `balances` | object | no | Per-state numeric balances, e.g. `{"comp_off": 2}` |
| `records` | object | no | Per-state lists of earned records — see [records](#records) below |
| `history` | object | no | Prior period context — see [history](#history) below |
| `previous_week_days` | object | no | Assignments from days before the period that share the same ISO week as the period start |

#### records

A map from state name to a list of record objects. Each record represents one earned entitlement.

| Field | Type | Description |
|---|---|---|
| `earned_date` | ISO date string | When the entitlement was earned |
| `redeemed_on` | ISO date string or `null` | When it was used, or `null` if still available |

#### history

| Field | Type | Description |
|---|---|---|
| `last_month_shift_counts` | object | Count of each state in the previous period, e.g. `{"morning": 8, "night": 6}` |

#### previous_week_days

A map of ISO date strings to state names. Covers days from before the period start that fall in the same ISO calendar week as the first day of the period. Used by `count_per_week` rules to correctly enforce weekly counts at the boundary.

```json
"previous_week_days": {
  "2026-03-30": "afternoon",
  "2026-03-31": "week_off"
}
```

### holidays

A list of public holiday objects.

| Field | Type | Description |
|---|---|---|
| `date` | ISO date string | The holiday date |
| `locations` | list of strings | Attribute values (matched against `employee.attributes["city"]`) for which this holiday applies. An empty list means the holiday is global. |
