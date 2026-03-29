---
icon: lucide/lock
---

# Regular shift assigned after core shifts

## What it means

On weekdays, the regular shift is treated as a fallback. Core shifts (morning, afternoon, night) are staffed first. An employee is only assigned to regular after the core shift requirements for that day are satisfied.

On weekends, the regular shift is disabled by default (maximum of 0).

## Why it exists

The regular shift represents standard office hours and is not part of the rotating shift cycle. It exists to absorb employees who are not needed on a core shift on a given weekday. Treating it as a fallback ensures the rotating shifts are always prioritized, which is important for coverage continuity and fairness in shift rotation.

## Example

Suppose a Monday requires one morning, one afternoon, and one night worker, and the team has five people. After placing three people on core shifts, the remaining two are candidates for regular or off. The engine will assign regular to one of them (up to the regular maximum) and give the other an off day — it will not skip core shifts and place people on regular first.

## Parameters

| Parameter | Default | Description |
|---|---|---|
| `coverage.by_day_of_week.saturday.regular.max` | `0` | Regular is disabled on weekends by default |
| `coverage.by_day_of_week.sunday.regular.max` | `0` | Regular is disabled on weekends by default |

## Interaction with other constraints

This constraint works through the coverage maximum mechanism. Setting regular `max` to `0` on weekends is what enforces the weekend restriction — it is the same [maximum shift coverage](max-shift-coverage.md) constraint applied to a specific shift and day combination.
