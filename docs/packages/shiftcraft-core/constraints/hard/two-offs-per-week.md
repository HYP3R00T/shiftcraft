---
icon: lucide/lock
---

# Two off days per calendar week

## What it means

Each employee must receive exactly two off days in every calendar week (Monday through Sunday), regardless of which days those off days fall on.

## Why it exists

This is a standard labor entitlement. Employees are entitled to a minimum number of rest days per week. The engine enforces this as a hard rule so no roster can accidentally under-assign rest days.

## Example

In a full week where an employee has no carry-over off days from the previous month, exactly two of the seven days must be assigned as off. The engine decides which two days, subject to coverage requirements and soft preferences.

If the team has five people and the daily cap is four workers, at least one person is off every day. The engine distributes those off days so each person accumulates exactly two per week.

## Cross-month weeks

When a scheduling period starts mid-week, some employees may already have off days from the previous month that fall in the same ISO calendar week. The engine accounts for those carry-over off days.

If an employee already has one off day from the previous month in that ISO week, only one more off day is required from the current period's dates in that week.

For partial weeks at the start or end of the scheduling period where fewer than seven days are present, the engine applies a flexible range (one or two off days) to maintain feasibility.

## Parameters

| Parameter | Default | Description |
|---|---|---|
| `weekly_off_days` | `2` | Required off days per calendar week per employee |
| `week_definition` | Monday–Sunday | ISO calendar week boundaries |

## Interaction with other constraints

This constraint interacts directly with [leave capacity gate](leave-capacity-gate.md) and [maximum working employees per day](max-workers-per-day.md). The engine must find off-day placements that satisfy all three simultaneously — enough people off to meet the weekly entitlement, but not so many off on the same day that coverage minimums are violated.
