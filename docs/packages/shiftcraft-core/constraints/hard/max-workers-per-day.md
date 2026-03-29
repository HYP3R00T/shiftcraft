---
icon: lucide/lock
---

# Maximum working employees per day

## What it means

On any given day, the total number of employees assigned to any shift cannot exceed the configured daily cap. This cap applies across all shifts combined, not per shift.

## Why it exists

This constraint ensures that at least some employees are off every day. Without it, the engine could theoretically assign the entire team to work every single day and satisfy coverage minimums trivially — but that would leave no room for off days or leave.

In practice, this cap is set to `team_size - 1` or lower, guaranteeing that at least one person is always off.

## Example

With a team of five and a daily cap of four, at least one person must be off every day. The engine cannot produce a day where all five employees are working simultaneously.

If coverage minimums require three workers and the cap is four, the engine has flexibility to assign three or four workers on any given day, choosing based on soft preferences and leave requests.

## Parameters

| Parameter | Default | Description |
|---|---|---|
| `max_working_employees_per_day` | `4` | Maximum total employees working on any single day |

## Interaction with other constraints

This constraint works together with [two offs per week](two-offs-per-week.md) and [leave capacity gate](leave-capacity-gate.md). All three constrain how many people can be off on a given day from different angles — the daily cap sets an upper bound on workers, the weekly off rule sets a lower bound on rest days, and the leave capacity gate limits how many can be absent relative to coverage needs.
