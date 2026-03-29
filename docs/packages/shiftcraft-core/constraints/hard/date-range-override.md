---
icon: lucide/lock
---

# Date-range coverage overrides

## What it means

If a date falls within a configured date-range override, the override's coverage values apply instead of the day-of-week defaults. This allows specific dates to have different staffing requirements than their usual weekday or weekend pattern.

## Why it exists

Real-world schedules often have exceptions. A public holiday period, a product launch, a seasonal peak — these may require different staffing levels than the standard weekly pattern. Date-range overrides let you express those exceptions without changing the base configuration.

## Example

Suppose April 30th is a Thursday, and the standard Thursday configuration has regular shift minimum of 0. But for that specific date, operations require at least one regular shift worker. A date-range override for April 30th can set regular minimum to 1, and the engine will treat that day differently from all other Thursdays.

The override takes full precedence — all four shift slots (morning, afternoon, night, regular) come from the override for any date that falls within its range.

## Parameters

| Field | Description |
|---|---|
| `coverage.by_date_range[].start` | First date of the override range (inclusive) |
| `coverage.by_date_range[].end` | Last date of the override range (inclusive) |
| `coverage.by_date_range[].<shift>.min/target/max` | Coverage values for each shift within the range |

If a date matches multiple overlapping overrides, the first matching entry in the list is used.

## Interaction with other constraints

Overrides affect [minimum shift coverage](min-shift-coverage.md) and [maximum shift coverage](max-shift-coverage.md) for the dates they cover. Any constraint that reads coverage values will use the override values for those dates.
