---
icon: lucide/lock
---

# No night-to-morning transition

## What it means

Certain shift transitions are disallowed on consecutive days for the same person. The default disallowed transition is night followed by morning.

## Why it exists

A night shift typically ends in the early hours of the morning. Assigning a morning shift the very next day leaves insufficient rest time. This constraint protects employee wellbeing and is a common requirement in workforce scheduling regulations.

## Example

Suppose someone works the night shift on Monday. The following day, Tuesday, they cannot be assigned to morning. They can be assigned afternoon, night, regular, or an off day — any of those are valid.

If the team is small and coverage is tight, the engine may place them on afternoon Tuesday rather than morning, even if morning would otherwise be the fairest assignment.

## Parameters

| Parameter | Default | Description |
|---|---|---|
| `disallowed_shift_transitions` | `{(night, morning)}` | Set of (from, to) shift pairs that cannot appear on consecutive days |

## Interaction with other constraints

This constraint interacts with [minimum shift coverage](min-shift-coverage.md). If many employees worked night on the same day, the pool of people eligible for morning the next day shrinks. In extreme cases this can make the problem infeasible if the morning minimum cannot be met from the remaining eligible employees.
