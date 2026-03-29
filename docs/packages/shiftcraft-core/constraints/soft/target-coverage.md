---
icon: lucide/sliders
---

# Target coverage shortfall

## What it means

Each shift slot has a target headcount in addition to a minimum. The minimum is a hard requirement; the target is a preference. The engine tries to reach the target but does not require it.

When the assigned count falls below the target (but still meets the minimum), a penalty is added proportional to the shortfall.

## Why it exists

The target represents the ideal staffing level — enough people to handle the expected workload comfortably, with some buffer. Meeting only the minimum means the team is operating at the bare floor. This constraint encourages the optimizer to staff above the minimum when it can do so without violating other preferences.

## How the penalty is calculated

For each day and each shift where the target exceeds the minimum, the engine measures how far below the target the actual assignment falls. Each unit of shortfall multiplied by the weight is added to the penalty.

Example: if morning target is 2 and only 1 person is assigned, the shortfall is 1. That contributes `1 × 3 = 3` to the total penalty.

## Example

Suppose morning has a minimum of 1 and a target of 2. A roster that assigns 2 people to morning every day scores better than one that consistently assigns only 1, even though both are valid.

In practice, this constraint has the lowest weight of all soft constraints. It will be sacrificed first when it conflicts with fairness or leave preferences.

## Parameters

| Parameter | Default | Description |
|---|---|---|
| `W_TARGET_COVERAGE` | `3` | Penalty weight per unit of shortfall below target |

## Interaction with other constraints

This is the lowest-weight soft constraint. It will lose to all other preferences when trade-offs are necessary. Its main effect is to break ties — when two rosters are otherwise equivalent, the one that better meets target coverage wins.
