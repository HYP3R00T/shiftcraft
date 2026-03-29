---
icon: lucide/lock
---

# Annual and comp-off only on requested dates

## What it means

An employee cannot be assigned `annual` or `comp_off` on a date they did not explicitly request it. These leave types are not freely assignable by the engine — they only appear in the output when the employee asked for them on that specific date.

`week_off` is the only leave type the engine assigns freely to satisfy the two-off-days-per-week requirement.

## Why it exists

Annual leave and comp-off are entitlements that belong to the employee. The engine should not consume them without the employee's explicit request. Freely assigning annual leave to fill off-day slots would deplete an employee's leave balance without their knowledge or consent.

## Example

Suppose an employee has two unredeemed comp-off entitlements but has not requested any comp-off days in the current period. The engine will not assign `comp_off` to any of their off days. Their off days will all be `week_off`.

If the same employee requests `comp_off` on April 10th, the engine will assign `comp_off` on that date (subject to the [comp-off validity](comp-off-validity.md) constraint) and use `week_off` for all other off days.

## Interaction with other constraints

This constraint works together with [typed leave must be honored exactly](typed-leave-honored.md) and [comp-off validity](comp-off-validity.md). Together they define the full set of rules governing when and how each leave type can appear in the output.
