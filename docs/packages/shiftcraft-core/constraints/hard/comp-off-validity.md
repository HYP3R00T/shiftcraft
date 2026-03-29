---
icon: lucide/lock
---

# Comp-off cannot exceed valid balance

## What it means

An employee can only redeem comp-off entitlements that are currently valid. A comp-off record is valid if it has not already been redeemed and was earned within the validity window relative to the period start date.

## Why it exists

Comp-off entitlements expire. An employee who worked a holiday six months ago cannot carry that entitlement indefinitely. The validity window ensures that comp-off is used within a reasonable timeframe and prevents stale records from inflating an employee's available balance.

## Example

Suppose an employee has three comp-off records:

- Earned January 1st, redeemed February 10th — already consumed, not available
- Earned January 26th, not redeemed — earned 64 days before the period start of April 1st, still within the 90-day window, available
- Earned December 15th, not redeemed — earned 107 days before April 1st, outside the 90-day window, expired

In this case, the employee has exactly one valid comp-off entitlement available for the current period. The engine will allow at most one `comp_off` day to be assigned, even if the employee requests more.

## Parameters

| Parameter | Default | Description |
|---|---|---|
| `comp_off_validity_days` | `90` | Number of days after earning that a comp-off remains redeemable |

## Interaction with other constraints

This constraint gates [typed leave must be honored exactly](typed-leave-honored.md) for comp-off requests. If an employee requests `comp_off` but has no valid balance, the request cannot be honored and the roster becomes infeasible.
