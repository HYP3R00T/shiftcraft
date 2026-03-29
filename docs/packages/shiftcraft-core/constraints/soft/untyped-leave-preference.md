---
icon: lucide/sliders
---

# Untyped leave date preference

## What it means

When an employee submits a leave request without specifying a leave type, the engine treats it as a preference for that date. It tries to assign an off day on the requested date, but may place the off day on a different date if coverage constraints prevent honoring the original request.

## Why it exists

Not all leave requests are firm commitments. An employee might indicate a preferred day off without it being a formal annual leave or comp-off request. The engine should try to accommodate these preferences but cannot guarantee them — coverage must come first. Treating them as soft constraints gives the optimizer the flexibility to honor them when possible and move them when necessary.

## How the penalty is calculated

For each untyped leave request, the engine checks whether the employee is off on the requested date. If they are working on that date instead, a penalty is added.

Note: the engine may still give the employee an off day elsewhere in the week to satisfy the [two offs per week](../hard/two-offs-per-week.md) requirement — the penalty only fires when the specific requested date is not honored.

## Example

Suppose an employee requests April 10th off without a leave type. If coverage on April 10th requires all available workers and no one else can cover, the engine will assign the employee to work that day and add a penalty. Their weekly off days will still be assigned on other dates in that week.

If April 10th can be accommodated, the engine will prefer placing the off day there to avoid the penalty.

## Parameters

| Parameter | Default | Description |
|---|---|---|
| `W_UNTYPED_LEAVE` | `7` | Penalty weight per untyped leave request not honored on its requested date |

## Interaction with other constraints

This is the second-highest-weight soft constraint, just below [even shift distribution](shift-balance.md). The engine treats untyped leave preferences as nearly as important as shift fairness. Compare this with [typed leave must be honored exactly](../hard/typed-leave-honored.md) — typed leave is a hard constraint and cannot be moved at all.
