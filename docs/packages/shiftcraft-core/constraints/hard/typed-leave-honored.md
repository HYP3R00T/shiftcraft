---
icon: lucide/lock
---

# Typed leave must be honored exactly

## What it means

If a leave request specifies a `leave_type` of `annual`, `comp_off`, or `week_off`, that exact type must be assigned on that exact date. The engine cannot substitute a different leave type or move the date.

## Why it exists

Typed leave requests represent committed entitlements. An employee requesting `comp_off` on a specific date has a legal or contractual right to use that entitlement on that day. Similarly, approved annual leave is a firm commitment. The engine must respect these as facts, not preferences.

## Example

Suppose an employee requests `comp_off` on April 3rd. The output must show `comp_off` for that employee on April 3rd. The engine cannot convert it to `annual`, cannot move it to April 4th, and cannot assign a shift instead.

If honoring this request makes the roster infeasible — for example, because too many people have hard leave on the same day — the engine reports an infeasible result rather than silently ignoring the request.

## Parameters

| Field | Allowed values | Description |
|---|---|---|
| `leave_requests[].leave_type` | `annual`, `comp_off`, `week_off`, `null` | The type of leave being requested |

A `null` leave type is treated as a soft preference, not a hard requirement. See [untyped leave preference](../soft/untyped-leave-preference.md).

## Interaction with other constraints

This constraint interacts with [leave capacity gate](leave-capacity-gate.md). If multiple employees have hard leave on the same day and the capacity gate cannot accommodate all of them, the roster becomes infeasible. The engine will report which dates and requests caused the conflict.
