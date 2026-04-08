# Architecture

Shiftcraft is a data-driven scheduling engine. Business rules are expressed
as JSON rule descriptors. The solver reads them and emits CP-SAT constraints.
No code changes are needed when rules change.

See [problem.md](problem.md) for the problem definition and constraint
taxonomy. See [services/core/constraint-primitives.md](services/core/constraint-primitives.md)
for the full primitive specification.

---

## System shape

```text
API request
  └── settings  (rules of the game — shifts, leave types, rules)
  └── input     (data for this run — team, period, holidays)
        │
        ▼
    Parser
        │  validates and hydrates into typed objects
        ▼
    Rule compiler
        │  for each rule: filter_who() + filter_when() → handler()
        ▼
    CP-SAT model
        │  solve()
        ▼
    Formatter
        │
        ▼
API response
  └── schedule  (assignments per person per day)
  └── metadata  (solve time, status, soft constraint violations)
```

The core dispatch loop:

```python
for rule in settings["rules"]:
    handler = HANDLERS[rule["type"]]
    employees = filter_who(rule["scope"]["who"], team)
    dates     = filter_when(rule["scope"]["when"], all_dates)
    handler(model, rule, employees, dates, vars)
```

One handler per primitive type. Adding a new primitive = adding one function.

---

## Payload structure

Every API call sends two top-level objects:

```json
{
  "settings": { "shifts": [], "leave_types": [], "solver": {}, "rules": [] },
  "input":    { "period": {}, "team": [], "holidays": [] }
}
```

- `settings` — the rules of the game. Shared across runs for the same team.
- `input` — the data for this specific run. Changes every scheduling period.

Coverage requirements are not a separate field. They are expressed as
`daily_count` rules in `settings.rules`.

---

## Employees

Each employee carries a free-form `attributes` map. The system never
hardcodes what attributes exist — it uses them only for rule targeting.

```json
{
  "id": "E001",
  "name": "Alice",
  "attributes": { "city": "Hyderabad", "role": "senior", "contract": "full-time" }
}
```

Each employee may also carry a `history` object for period-boundary
continuity:

```json
{
  "history": {
    "last_month_shift_counts": { "morning": 8, "night": 6, "afternoon": 7 },
    "previous_state_run": { "value": "night", "count": 2 }
  }
}
```

- `last_month_shift_counts` — feeds the history bias soft objective
- `previous_state_run` — carries over a consecutive run from the previous
  period for `sequence_constraint` evaluation

---

## Scope — WHO × WHEN

Every rule targets a subset of employees (WHO) and a subset of dates (WHEN).
These are always independent — any WHO can combine with any WHEN.

WHO options:

```json
{ "type": "all" }
{ "type": "attribute", "key": "role", "value": "senior" }
{ "type": "employees", "ids": ["E001", "E002"] }
```

WHEN options:

```json
{ "type": "always" }
{ "type": "dates", "values": ["2026-04-10"] }
{ "type": "date_range", "start": "2026-04-01", "end": "2026-04-15" }
{ "type": "day_of_week", "values": ["friday", "saturday"] }
{ "type": "day_type", "value": "weekend" }
{ "type": "day_type", "value": "holiday" }
```

---

## Enforcement spectrum

```text
"hard"                       must be satisfied — infeasible if violated
"soft" + "weight": "high"    strongly preferred  (penalty = 100)
"soft" + "weight": "medium"  preferred           (penalty = 50)
"soft" + "weight": "low"     nice to have        (penalty = 10)
"preference"                 employee-stated wish (penalty = 1)
```

Hard constraints have no ordering or priority between them. The solver must
satisfy all of them simultaneously or declare the problem infeasible.

Soft constraints are weighted penalties added to the objective function.
The solver minimises total penalty. Conflicts between soft constraints are
resolved by weight, not by order.

---

## Conflict resolution

When two rules target the same (employee, date) cell with contradictory
values, the later rule may declare an explicit override:

```json
{
  "id": "rule-012",
  "type": "assignment_force",
  "forced_value": "comp_off",
  "overrides": ["rule-006"],
  "scope": {
    "who": { "type": "employees", "ids": ["E001"] },
    "when": { "type": "dates", "values": ["2026-04-10"] }
  },
  "enforcement": "hard"
}
```

The `overrides` field is explicit — the user declared the conflict
intentionally. No implicit priority order. If two hard rules conflict
without an `overrides` declaration, the solver returns infeasible.

---

## Fixed solver behaviour

Two categories of logic are not user-configurable rules. They are built
into the solver:

- Derivation rules — generate data rather than restrict assignments.
  Example: working on a public holiday earns a comp_off record. This
  creates a record; it does not constrain the schedule.

- History bias — a soft objective that penalises assigning a state to a
  person when they already had many of that state last period. References
  `history.last_month_shift_counts` per employee. Cannot be expressed as
  a primitive because the baseline varies per person.

---

## Out of scope

- Hour-level timing — "11 hours rest between shifts" requires time-of-day
  awareness. This system is day-granularity only.

- Fixed rotation patterns — cyclic rotations (M→A→N→WO→WO, repeat) are a
  different scheduling paradigm. Teams using fixed rotations need a rotation
  calendar, not a constraint solver.

- Multi-resource assignment — "worker must be on Line A or Line B, not both"
  involves multiple simultaneous resource dimensions.
