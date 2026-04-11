---
icon: lucide/file-output
---

# Output format

The engine always returns a JSON object with three top-level keys: `status`, `schedule`, and `metadata`.

---

## status

A string indicating the solver outcome.

| Value | Meaning |
|---|---|
| `"optimal"` | The solver found the best possible roster within the time limit |
| `"feasible"` | The solver found a valid roster but could not confirm it is optimal before the time limit expired. All hard constraints are satisfied. |
| `"infeasible"` | No roster exists that satisfies all hard constraints |
| `"unknown"` | The solver timed out before finding any valid roster |
| `"model_invalid"` | The model could not be constructed — indicates a configuration error |

---

## schedule

When `status` is `"optimal"` or `"feasible"`, `schedule` is a date-keyed object. Each key is an ISO date string. Each value is a map of employee ID to assigned state for that day.

```json
"schedule": {
  "2026-04-01": {
    "E001": "afternoon",
    "E002": "week_off",
    "E003": "night",
    "E004": "week_off",
    "E005": "morning"
  },
  "2026-04-02": {
    "E001": "afternoon",
    "E002": "morning",
    ...
  }
}
```

Dates are sorted chronologically. Every date in the requested period is present. Every employee in the input team has exactly one state per date.

Valid state values are whatever was declared in `settings.shifts` and `settings.leave_types` for the run.

When `status` is `"infeasible"` or `"unknown"`, `schedule` is an empty object `{}`.

---

## metadata

Present in all responses.

| Field | Type | Description |
|---|---|---|
| `status` | string | Same value as the top-level `status` field |
| `solve_time_seconds` | float | Wall-clock time the solver ran, in seconds |
| `objective` | integer or `null` | Total weighted penalty of the returned roster — see below |

### objective

The objective is the sum of all soft constraint penalties in the returned roster. It is only present (non-null) when the model includes soft constraints.

Lower is better. A value of `0` would mean every soft preference was fully satisfied. In practice, some penalty is expected when preferences conflict with coverage requirements or with each other.

The number is only meaningful relative to other runs with the same input and the same constraint weights. It cannot be compared across runs with different team sizes, periods, or rule configurations.

---

## Full example

```json
{
  "status": "optimal",
  "schedule": {
    "2026-04-01": {
      "E001": "afternoon",
      "E002": "week_off",
      "E003": "night",
      "E004": "week_off",
      "E005": "morning"
    }
  },
  "metadata": {
    "status": "optimal",
    "solve_time_seconds": 0.886,
    "objective": 4543
  }
}
```
