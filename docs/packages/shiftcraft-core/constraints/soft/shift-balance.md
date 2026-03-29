---
icon: lucide/sliders
---

# Even shift distribution

## What it means

Over the scheduling period, morning, afternoon, and night assignments should be distributed as evenly as possible across all employees. The engine calculates a fair share for each shift type and penalizes deviations from that target.

## Why it exists

Even if the hard [core shift balance](../hard/core-shift-balance.md) constraint ensures no single employee is overloaded on one shift type, it does not guarantee fairness across the team. One employee could have 7 mornings while another has 5, both within the hard limit. This soft constraint pushes the optimizer toward equal distribution across the whole team.

## How the penalty is calculated

For each core shift type, the engine computes the total number of slots across the period and divides by the number of employees to get a target per person. For each employee, it measures the absolute deviation from that target and multiplies by the weight.

Example: if the morning target is 7 per person and one employee has 9, their deviation is 2. That contributes `2 × 10 = 20` to the total penalty.

## Example

Suppose a 30-day period has 22 morning slots to fill across 5 employees. The target is roughly 4 per person. A roster where counts are 4-4-4-5-5 scores better than one where counts are 3-3-4-6-6, even though both satisfy the hard balance constraint.

## Parameters

| Parameter | Default | Description |
|---|---|---|
| `W_SHIFT_BALANCE` | `10` | Penalty weight per unit of deviation from fair share |

## Interaction with other constraints

This constraint works alongside [prior-month history bias](history-bias.md). History bias nudges assignments away from shifts an employee already worked heavily last month, while shift balance nudges toward equal counts this month. Both contribute to the same penalty total.
