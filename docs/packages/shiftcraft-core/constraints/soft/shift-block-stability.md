---
icon: lucide/sliders
---

# Shift block stability

## What it means

The engine prefers assigning the same shift type on consecutive days rather than switching frequently. A person who works night on Monday should ideally work night on Tuesday and Wednesday as well, rather than switching to morning on Tuesday.

Each time an employee is on a shift one day and not on that same shift the next day, a small penalty is added. This encourages stable blocks of the same shift type.

## Why it exists

Frequent shift changes are disruptive to sleep patterns and daily routines. Stable blocks of the same shift type are easier for employees to adapt to and are a common preference in shift scheduling. This constraint nudges the optimizer toward those stable patterns without making them mandatory.

## How the penalty is calculated

For each consecutive pair of days, and for each core shift type, the engine checks whether an employee was on that shift on day one but not on day two. Each such transition adds `1 × weight` to the penalty.

Note: a transition to an off day also counts as a block break. The engine does not distinguish between "switched to a different shift" and "went off" — both break the block.

## Example

An employee working night Monday through Friday contributes zero block-break penalties for those days. An employee alternating night-morning-night-morning contributes a block-break penalty for each switch.

A roster where someone works night for five consecutive days scores better than one where they alternate between night and morning every other day, all else being equal.

## Parameters

| Parameter | Default | Description |
|---|---|---|
| `W_SHIFT_BLOCK` | `8` | Penalty weight per shift block transition |

## Interaction with other constraints

This constraint can conflict with [even shift distribution](shift-balance.md). Perfectly stable blocks mean an employee works the same shift for long stretches, which may produce uneven distribution across shift types. The weights determine which preference wins when they conflict — shift balance (10) outweighs block stability (8).
