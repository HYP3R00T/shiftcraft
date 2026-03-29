---
icon: lucide/sliders
---

# Paired Saturday and Sunday offs

## What it means

When an employee gets a weekend off, the engine prefers giving them both Saturday and Sunday off in the same week rather than splitting them across different weekends or pairing a weekend day with a weekday off.

## Why it exists

A single day off on Saturday or Sunday is less restful than a full weekend. Employees benefit more from two consecutive days off than from two isolated days. This constraint nudges the optimizer toward grouping weekend offs together when coverage allows.

## How the penalty is calculated

For each ISO week that contains both a Saturday and a Sunday within the scheduling period, the engine checks whether an employee has exactly one of the two as an off day. If Saturday is off but Sunday is not (or vice versa), a penalty is added. If both are off or neither is off, no penalty is added for that week.

## Example

Suppose an employee has two weekend off days in a given week. Giving them Saturday and Sunday off together contributes zero penalty for that week. Giving them Saturday off this week and Sunday off next week contributes a penalty for each split week.

## Parameters

| Parameter | Default | Description |
|---|---|---|
| `W_OFF_CONTIGUOUS` | `4` | Penalty weight per split weekend (one day off, one day working) |

## Interaction with other constraints

This constraint works alongside [balanced weekend offs](weekend-off-balance.md). Balance ensures the total count is fair across the team; pairing ensures the individual experience of those offs is as good as possible. Both contribute to the same penalty total.
