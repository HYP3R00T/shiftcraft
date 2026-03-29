---
icon: lucide/sliders
---

# Balanced weekend offs

## What it means

The total number of weekend off days (Saturday and Sunday) should be distributed fairly across all employees. The engine measures the difference between the employee with the most weekend offs and the one with the fewest, and penalizes large gaps.

## Why it exists

Weekend offs are more valuable than weekday offs for most employees. If the engine consistently gives some employees more weekend rest than others, that is an unfair distribution even if total off-day counts are equal. This constraint ensures the optimizer accounts for the quality of off days, not just the quantity.

## How the penalty is calculated

The engine counts the total weekend off days for each employee across the period. It then computes the difference between the maximum and minimum counts across the team. That difference, multiplied by the weight, is added to the penalty.

Example: if one employee has 6 weekend offs and another has 2, the imbalance is 4. That contributes `4 × 6 = 24` to the total penalty.

## Example

Suppose a 30-day period has 8 Saturdays and Sundays. With 5 employees, a perfectly balanced distribution would give each person roughly 3-4 weekend off days. A roster where counts are 3-3-4-4-4 scores better than one where counts are 1-2-4-5-6.

## Parameters

| Parameter | Default | Description |
|---|---|---|
| `W_OFF_BALANCE` | `6` | Penalty weight per unit of weekend off imbalance |

## Interaction with other constraints

This constraint works alongside [paired Saturday and Sunday offs](paired-weekend-offs.md). Balance ensures the total count is fair; pairing ensures the quality of those offs is maximized by grouping them together.
