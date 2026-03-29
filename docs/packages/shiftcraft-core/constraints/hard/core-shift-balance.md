---
icon: lucide/lock
---

# Core shift balance per employee

## What it means

Across the scheduling period, each employee's count of morning, afternoon, and night shifts must stay within one of each other. The engine will not produce a roster where one person has significantly more of one core shift type than another.

The regular shift is excluded from this balance check because its availability is limited to weekdays and specific coverage configurations, making equal distribution impractical.

## Why it exists

Shift rotation fairness is a fundamental expectation in workforce scheduling. If one employee consistently gets morning shifts while another always works nights, that is an unfair distribution regardless of whether coverage is met. This constraint enforces a hard floor on fairness so the optimizer cannot sacrifice it entirely in pursuit of other preferences.

## Example

Suppose the scheduling period produces roughly 7 assignments per core shift type per person. Counts like 6-7-7 or 7-7-8 across morning, afternoon, and night are acceptable — the difference between the highest and lowest is at most 1.

A distribution like 9-6-6 would violate this constraint. The engine would reject any roster where one shift type count is more than 1 above another for the same employee.

## Parameters

| Parameter | Default | Description |
|---|---|---|
| `max_core_shift_imbalance_per_employee` | `1` | Maximum allowed difference between any two core shift counts for a single employee |

## Interaction with other constraints

This is a hard fairness floor. The soft constraint [even shift distribution](../soft/shift-balance.md) builds on top of it by also trying to balance counts across employees (not just within one employee's own shift types). Together they enforce both intra-employee and inter-employee fairness.
