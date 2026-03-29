---
icon: lucide/file-output
---

# Output format

The engine always returns a JSON object. The shape of the response depends on whether a valid roster was found.

---

## When a roster is found

```json
{
  "status": "ok",
  "schedule": [...],
  "summary": {...},
  "penalty": 2856
}
```

### status

Either `"ok"` or `"feasible"`.

- `"ok"` means the solver found the mathematically optimal solution within the time limit.
- `"feasible"` means the solver found a valid solution but could not confirm it is the best possible one before the time limit was reached. The roster is still fully valid — all hard constraints are satisfied.

### schedule

A list of day objects, one per date in the scheduling period, in chronological order.

Each day object contains the date and one assignment per employee:

```json
{
  "date": "2026-04-01",
  "Amogha": "afternoon",
  "Suchi": "morning",
  "Basheer": "week_off",
  "Anuhya": "night",
  "Pavani": "regular"
}
```

Each employee's value is one of: `morning`, `afternoon`, `night`, `regular`, `week_off`, `annual`, `comp_off`.

### summary

A per-employee count of each assignment type across the full period.

```json
{
  "Amogha": {
    "morning": 5,
    "afternoon": 6,
    "night": 6,
    "regular": 6,
    "week_off": 7,
    "annual": 0,
    "comp_off": 0
  }
}
```

This is useful for auditing fairness and verifying that leave entitlements were applied correctly.

### penalty

An integer representing the total weighted penalty of the returned roster. Lower is better. A penalty of `0` would mean every soft preference was fully satisfied, which is rarely achievable in practice.

The penalty is computed as the sum of all soft constraint violations, each multiplied by its configured weight. See [soft constraints](constraints/soft.md) for the full list of what contributes to this score.

---

## When no roster is found

```json
{
  "status": "infeasible",
  "conflicts": [
    "2026-04-10: 3 hard leave requests (Alice, Bob, Carol) but only 2 can be off (team=5, min_workers=3)",
    "2026-04-15: total minimum coverage (6) exceeds team size (5)"
  ]
}
```

### status

`"infeasible"` when no valid roster exists, or `"infeasible"` when the solver timed out without finding any valid solution.

### conflicts

A list of human-readable explanations describing why the problem could not be solved. Each entry identifies the specific date and the rule that was violated.

Common causes include:

- Minimum coverage requirements that exceed the available team size on a given day
- Too many hard leave requests on the same date, leaving insufficient workers to meet minimum coverage
- Interactions between consecutive-day rules, weekly off requirements, and coverage minimums that create an impossible combination

If no specific structural conflict is detected, the message will indicate that the failure is likely caused by an interaction of multiple constraints rather than a single obvious violation.
