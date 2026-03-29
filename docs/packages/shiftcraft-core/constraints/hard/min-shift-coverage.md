---
icon: lucide/lock
---

# Minimum shift coverage

## What it means

For every day and every shift, the number of assigned employees must be at or above the configured minimum. Falling below the minimum on any shift on any day makes the roster invalid.

## Why it exists

Minimum coverage represents the lowest staffing level at which operations can function. Going below it means the team cannot handle the workload for that shift. This is a non-negotiable operational requirement.

## Example

Suppose Tuesday morning has a minimum of 1. There must be at least one person assigned to morning on every Tuesday. A Tuesday with zero morning staff is not a valid roster, even if afternoon and night are fully staffed.

If the minimum is 2 and only one person is available (because others are on leave or off), the engine will report an infeasible result for that day.

## Parameters

Coverage minimums are configured per shift per day of week, with optional date-range overrides.

| Field | Description |
|---|---|
| `coverage.by_day_of_week.<day>.<shift>.min` | Minimum headcount for that shift on that day of week |
| `coverage.by_date_range[].min` | Override minimum for a specific date range |

## Interaction with other constraints

This constraint is the primary driver of infeasibility. When combined with [leave capacity gate](leave-capacity-gate.md) and [two offs per week](two-offs-per-week.md), the engine must find a placement where enough people are working every day to meet all minimums while still giving everyone their required rest days.
