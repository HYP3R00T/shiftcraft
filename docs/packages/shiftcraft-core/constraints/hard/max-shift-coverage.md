---
icon: lucide/lock
---

# Maximum shift coverage

## What it means

For every day and every shift, the number of assigned employees must not exceed the configured maximum. Assigning more people than the maximum to a shift on a given day makes the roster invalid.

## Why it exists

Maximum coverage serves two purposes. First, it prevents over-staffing a shift when there is no operational need. Second, and more commonly, it is used to disable a shift entirely on certain days by setting the maximum to zero.

## Example

The regular shift has a maximum of 0 on weekends in the default configuration. This means no one can be assigned to regular on Saturday or Sunday. If the engine tried to place someone on regular on a Sunday, the roster would be invalid.

On weekdays, the regular shift has a maximum of 1, meaning at most one person can be on regular per day.

## Parameters

| Field | Description |
|---|---|
| `coverage.by_day_of_week.<day>.<shift>.max` | Maximum headcount for that shift on that day of week |
| `coverage.by_date_range[].max` | Override maximum for a specific date range |

Setting `max` to `0` is the standard way to disable a shift on a given day.

## Interaction with other constraints

Maximum coverage works alongside [minimum shift coverage](min-shift-coverage.md) to define the valid range for each shift slot. The engine must find an assignment where every shift on every day falls within `[min, max]`.
