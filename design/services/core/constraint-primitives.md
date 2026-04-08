# Constraint Primitives

## Context

The scheduling engine translates user-defined rules into CP-SAT constraints.
Each rule is a JSON object with a `type` field that identifies the primitive,
a `scope` that defines WHO and WHEN it applies, and an `enforcement` level.

See [problem.md](../../problem.md) for the mathematical foundation.
See [architecture.md](../../architecture.md) for the dispatch model.

Every primitive follows this envelope:

```json
{
  "id": "rule-001",
  "label": "human-readable description",
  "type": "<primitive-type>",
  "scope": {
    "who": { ... },
    "when": { ... }
  },
  "enforcement": "hard" | "soft",
  "weight": "high" | "medium" | "low",
  "overrides": ["rule-id", ...]
}
```

- `id` — unique identifier for this rule within the settings
- `label` — optional, for display in the frontend
- `scope.who` — which employees this rule applies to
- `scope.when` — which days this rule applies to
- `enforcement` — `"hard"` (must satisfy) or `"soft"` (penalise violation)
- `weight` — required when `enforcement` is `"soft"`: `"high"` (100), `"medium"` (50), `"low"` (10). For employee-stated preferences use `"preference"` as enforcement (penalty = 1).
- `overrides` — optional list of rule IDs this rule explicitly supersedes

---

## Scope reference

### WHO

```json
{ "type": "all" }
{ "type": "attribute", "key": "role", "value": "senior" }
{ "type": "employees", "ids": ["E001", "E002"] }
```

### WHEN

```json
{ "type": "always" }
{ "type": "dates", "values": ["2026-04-10"] }
{ "type": "date_range", "start": "2026-04-01", "end": "2026-04-15" }
{ "type": "day_of_week", "values": ["friday", "saturday"] }
{ "type": "day_type", "value": "weekend" }
{ "type": "day_type", "value": "holiday" }
```

---

## Primitives

### `value_assignment`

Force or prefer a specific state for matching employees on matching days.

```json
{
  "type": "value_assignment",
  "value": "annual"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `value` | string | yes | The state to assign |

- Hard: the cell is fixed. The solver has no choice.
- Soft: a penalty is incurred if the cell is not this value.

In practice: an employee's annual leave is approved for April 10th — that cell is fixed to `annual` and the solver cannot change it. Or softer: an employee says "I'd prefer Friday off" — the solver tries to give them an off state but can override it if coverage is short.

Covers: approved leave requests, public holiday assignments, mandatory shift
assignments, employee day-off preferences.

---

### `value_exclusion`

Block one or more states for matching employees on matching days.

```json
{
  "type": "value_exclusion",
  "values": ["annual", "comp_off"]
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `values` | string[] | yes | States that must not be assigned |

- Hard: any listed state is forbidden. Violation makes the schedule infeasible.
- Soft: a penalty is incurred if any listed state is assigned.

In practice: nobody can take annual leave or comp_off during the last week of the month — those states are blocked for all employees on those days. Separately, `public_holiday` is always blocked on non-holiday days, which is how the calendar-gated governance works.

Covers: blackout periods, role-based shift restrictions, calendar-gated state
blocking (e.g. `public_holiday` blocked on non-holiday days).

---

### `count_per_week`

Per employee, the count of a state within each ISO calendar week must
satisfy a condition.

```json
{
  "type": "count_per_week",
  "value": "week_off",
  "operator": "==",
  "count": 2
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `value` | string | yes | State to count |
| `operator` | `">="` \| `"<="` \| `"=="` | yes | Comparison operator |
| `count` | integer | yes | Threshold |

Covers: mandatory rest days per week, maximum shifts of a type per week.

Note: counts only the named state. A week with a `public_holiday` still
requires the full `week_off` count — they are independent.

In practice: every employee must have exactly 2 week_offs per calendar week. The solver checks each week independently — week 1, week 2, week 3. If Monday is a public holiday, the employee still needs 2 week_offs that week on top of it, giving them 3 off days total that week.

---

### `count_per_window`

Per employee, the count of a state (or set of states) within any sliding
window of N consecutive days must satisfy a condition.

```json
{
  "type": "count_per_window",
  "values": ["morning", "afternoon", "night"],
  "window_days": 7,
  "operator": "<=",
  "count": 6
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `values` | string[] | yes | States to count (sum across all listed) |
| `window_days` | integer | yes | Window size in days |
| `operator` | `">="` \| `"<="` \| `"=="` | yes | Comparison operator |
| `count` | integer | yes | Threshold |

Covers: maximum working days in any 7-day span, fatigue rules, max nights
in any rolling window.

In practice: in any 7-day stretch, an employee may work at most 6 days. The solver checks every possible 7-day window — days 1–7, days 2–8, days 3–9, and so on. This catches cases where someone works 6 days at the end of one week and 6 days at the start of the next, which a per-week count would miss.

---

### `count_per_period`

Per employee, the count of a state across the full scheduling period must
satisfy a condition. An optional day filter restricts which days are counted.

```json
{
  "type": "count_per_period",
  "value": "annual",
  "operator": "<=",
  "count": 5,
  "count_when": { "type": "day_type", "value": "weekend" }
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `value` | string | yes | State to count |
| `operator` | `">="` \| `"<="` \| `"=="` | yes | Comparison operator |
| `count` | integer | yes | Threshold |
| `count_when` | WHEN object | no | Filter — only count days matching this |

Covers: total leave days in a period, max weekend working days per month,
monthly shift type quotas.

In practice: an employee may take at most 5 days of annual leave this month — the solver counts `annual` across all days in the period. With `count_when` set to weekends only: at most 3 weekend days may be working shifts — weekday shifts are ignored in the count.

---

### `count_bounded_by_balance`

Per employee, the count of a state across the full period must not exceed
a balance that belongs to that employee. The balance is derived from input
data — either a fixed numeric quota or a count of valid earned records.

```json
{
  "type": "count_bounded_by_balance",
  "value": "comp_off",
  "balance_source": { "type": "records", "key": "comp_off_records", "validity_days": 90 }
}
```

```json
{
  "type": "count_bounded_by_balance",
  "value": "annual",
  "balance_source": { "type": "numeric", "key": "annual_leave_days" }
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `value` | string | yes | State whose usage is bounded |
| `balance_source.type` | `"records"` \| `"numeric"` | yes | How the bound is derived |
| `balance_source.key` | string | yes | Field name on the employee object |
| `balance_source.validity_days` | integer | no | Records older than this are excluded (records type only) |

Both source types reduce to the same constraint at solve time:
`count(p, v) <= N(p, v)`. The difference is only in how N is computed
from the input.

Covers: comp-off entitlement, annual leave quotas, any finite per-person
leave balance.

In practice: Alice worked on 2 public holidays and earned 2 comp_off records. She can use `comp_off` at most 2 times this period — the balance comes from her records. Bob has 8 annual leave days remaining on his profile — he can use `annual` at most 8 times. Same constraint form, different input source.

---

### `pair_sequence`

If an employee has state A on day d, state B is required or forbidden on
day d+1 (or d-1 for backward direction).

```json
{
  "type": "pair_sequence",
  "from_value": "night",
  "to_value": "morning",
  "gap_days": 1,
  "direction": "forward",
  "forbidden": true
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `from_value` | string | yes | Trigger state |
| `to_value` | string | yes | Consequent state |
| `gap_days` | integer | yes | Days between trigger and consequent |
| `direction` | `"forward"` \| `"backward"` | no | Default: `"forward"` |
| `forbidden` | boolean | no | `true` = forbidden, `false` = required. Default: `true` |

- Hard: the transition is forbidden or required with no exception.
- Soft: the transition is penalised (shift block stability — prefer same
  state on consecutive working days).

Covers: forbidden shift transitions (night → morning), cool-down periods,
shift block stability preference, paired day preferences (Saturday off
implies Sunday off, expressed as backward direction).

In practice: if someone works night shift on Monday, they cannot work morning shift on Tuesday — the rest gap is too short. With soft enforcement and `forbidden: false`: if someone works morning today, the solver prefers they work morning tomorrow too — every time it switches shift types on consecutive working days, it incurs a penalty. With backward direction: if Sunday is a week_off, Saturday should also have been a week_off.

---

### `run_sequence`

After N consecutive days of state A, a condition applies to the immediately
following M days.

```json
{
  "type": "run_sequence",
  "trigger_value": "night",
  "trigger_count": 3,
  "then_value": "week_off",
  "then_operator": ">=",
  "then_count": 2,
  "then_days": 2
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `trigger_value` | string | yes | State that must appear consecutively |
| `trigger_count` | integer | yes | Length of consecutive run that activates the rule |
| `then_value` | string | yes | State required or restricted in the following window |
| `then_operator` | `">="` \| `"<="` \| `"=="` | yes | Comparison operator |
| `then_count` | integer | yes | Required count of `then_value` in the window |
| `then_days` | integer | yes | Size of the window after the trigger run |

Period boundary: if `previous_state_run` in employee history shows a
partial run of `trigger_value` from the previous period, that count carries
over. A `trigger_count: 3` rule with `previous_state_run: {value: "night", count: 2}`
needs only 1 more night this period to trigger.

Covers: fatigue rules (after N nights, must have M days off), maximum
consecutive working days with mandatory rest.

In practice: after 3 consecutive night shifts, the employee must have at least 2 week_offs in the next 2 days. If an employee ended last month with 2 consecutive nights, the solver knows this from `previous_state_run` — so just 1 more night this month triggers the rule, not 3.

---

### `spread_per_employee`

Across the full period, for a single employee, the difference between the
highest and lowest count of any state in a set must be at most B.

```json
{
  "type": "spread_per_employee",
  "values": ["morning", "afternoon", "night"],
  "max_diff": 1
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `values` | string[] | yes | States whose counts must be balanced |
| `max_diff` | integer | yes | Maximum allowed difference between any two counts |

Covers: fair shift rotation per employee — no one gets significantly more
of one shift type than another.

In practice: across the month, Alice's morning, afternoon, and night counts should differ by at most 1. If she ends up with 9 mornings, 6 afternoons, and 6 nights, the difference is 3 — that violates a `max_diff: 1` rule. The solver tries to keep her shift counts as even as possible.

---

### `spread_across_team`

Across the full period, for a given state, the difference between the
highest and lowest count across all employees in scope must be minimised.

```json
{
  "type": "spread_across_team",
  "value": "night",
  "max_diff": 2
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `value` | string | yes | State whose team-wide counts must be balanced |
| `max_diff` | integer | yes | Maximum allowed difference across employees |

An optional day filter (`count_when`) restricts which days are counted,
enabling weekend off balance as a special case.

```json
{
  "type": "spread_across_team",
  "value": "week_off",
  "max_diff": 1,
  "count_when": { "type": "day_type", "value": "weekend" }
}
```

Covers: equal night shift distribution across the team, equal weekend off
distribution across the team.

In practice: across the month, no employee should have significantly more night shifts than anyone else. If Alice has 8 nights and Bob has 3, the difference is 5 — the solver tries to close that gap. With `count_when` set to weekends: the solver counts only week_offs that fall on weekend days and tries to distribute those equally — this is how weekend off balance works.

---

### `daily_count`

On any matching day, the count of employees with a given state must satisfy
a condition. Supports hard minimum, hard maximum, and soft target.

```json
{
  "type": "daily_count",
  "value": "morning",
  "operator": ">=",
  "count": 2
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `value` | string or string[] | yes | State(s) to count (sum if list) |
| `operator` | `">="` \| `"<="` \| `"=="` | yes | Comparison operator |
| `count` | integer | yes | Threshold |

When WHO is scoped (not `"all"`), the count applies only within the filtered
group.

- Hard `>=`: minimum coverage — infeasible if not met
- Hard `<=`: maximum coverage or leave capacity gate
- Soft `>=`: target coverage — penalised if below target

Covers: minimum/maximum shift coverage, max workers per day, leave capacity
gate, role-specific coverage requirements, soft coverage targets.

In practice: at least 2 employees must be on morning shift every day (hard minimum — infeasible if not met), ideally 3 (soft target — penalised if fewer), at most 5 (hard maximum). For leave capacity: at most 3 people can be off on any day, ensuring enough people are always working. With WHO scoped to seniors: at least 1 senior must be on morning — the count only looks at seniors, not the whole team.

---

### `daily_ratio`

On any matching day, the ratio of employees with a state within a group
must satisfy a condition.

```json
{
  "type": "daily_ratio",
  "value": "morning",
  "numerator_who": { "type": "attribute", "key": "role", "value": "senior" },
  "operator": ">=",
  "ratio": 0.4,
  "exclude_values": ["annual", "comp_off", "week_off", "public_holiday"]
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `value` | string | yes | State counted in the numerator |
| `numerator_who` | WHO object | yes | Which employees count toward the numerator |
| `operator` | `">="` \| `"<="` \| `"=="` | yes | Comparison operator |
| `ratio` | float (0–1) | yes | Threshold ratio |
| `exclude_values` | string[] | no | States excluded from the denominator |

The denominator is the count of employees in the rule's WHO scope on that
day, minus those in `exclude_values`. `exclude_values` must be explicit —
there is no implicit "on leave" definition.

Covers: minimum senior ratio per shift, percentage-based staffing rules.

In practice: at least 40% of employees working on any day must be senior. If 10 people are working and 3 are on leave, the denominator is 10 (or fewer if leave states are in `exclude_values`). A fixed count of "4 seniors" would be impossible on a short-staffed day — a ratio adjusts automatically with team size.

---

### `daily_conditional`

On any matching day, if the count of employees with state A satisfies a
condition, then the count with state B must satisfy another condition.

```json
{
  "type": "daily_conditional",
  "if_value": "morning",
  "if_who": { "type": "all" },
  "if_operator": ">=",
  "if_count": 5,
  "then_value": "morning",
  "then_who": { "type": "attribute", "key": "role", "value": "manager" },
  "then_operator": ">=",
  "then_count": 1
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `if_value` | string | yes | State counted in the condition |
| `if_who` | WHO object | yes | Scope for the condition count |
| `if_operator` | `">="` \| `"<="` \| `"=="` | yes | Condition operator |
| `if_count` | integer | yes | Condition threshold |
| `then_value` | string | yes | State counted in the consequence |
| `then_who` | WHO object | yes | Scope for the consequence count |
| `then_operator` | `">="` \| `"<="` \| `"=="` | yes | Consequence operator |
| `then_count` | integer | yes | Consequence threshold |

Covers: conditional coverage rules (if more than N staff working, at least
1 manager must be present).

In practice: if more than 5 employees are working on a day, at least 1 of them must be a manager. On a quiet day with only 3 people working, the rule doesn't fire at all — the condition isn't met so the consequence doesn't apply.

---

### `person_dependency`

On any matching day, if employee A's state belongs to a set V1, then
employee B's state must belong to a set V2.

```json
{
  "type": "person_dependency",
  "employee_a": "E001",
  "employee_b": "E002",
  "if_values": ["week_off", "annual", "comp_off", "public_holiday"],
  "then_values": ["morning", "afternoon", "night"]
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `employee_a` | string | yes | The employee whose state is the condition |
| `employee_b` | string | yes | The employee whose state is constrained |
| `if_values` | string[] | yes | States of A that trigger the rule |
| `then_values` | string[] | yes | States B must be in when rule is triggered |

Special cases expressed through this primitive:

- Mutual exclusion: `if_values = V`, `then_values = S \ V`
  (if A is in the excluded set, B must not be)
- Co-assignment: `if_values = {v}`, `then_values = {v}` for each v
  (if A is on morning, B must also be on morning)

Covers: team lead / deputy dependency, paired worker co-assignment, key
person mutual exclusion.

In practice: if the team lead is on any off state, the deputy must be on a working shift — the team can't have both absent on the same day. For mutual exclusion: Alice and Bob cannot both be off on the same day — if Alice is off, Bob must be working. For co-assignment: Alice and Bob are paired workers who must always be on the same shift — if Alice is on morning, Bob must also be on morning.
