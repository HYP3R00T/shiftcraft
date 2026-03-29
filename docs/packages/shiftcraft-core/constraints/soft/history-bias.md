---
icon: lucide/sliders
---

# Prior-month history bias

## What it means

When distributing shifts, the engine considers how many of each shift type each employee worked in the previous month. Employees who worked a particular shift more last month are less preferred for that shift this month.

This creates continuity across months — someone who had a heavy night shift month last time is more likely to get morning or afternoon assignments this time.

## Why it exists

Shift fairness should be measured across time, not just within a single period. Without history bias, the engine might produce a perfectly balanced month in isolation but assign the same employee to nights every month simply because it is locally optimal. History bias introduces cross-period memory.

## How the penalty is calculated

For each employee and each core shift type, the engine multiplies the employee's previous month count for that shift by the number of times they are assigned that shift in the current period. A higher prior count combined with more current assignments produces a higher penalty.

This means the engine is not penalizing the employee for having worked nights last month — it is penalizing the roster for assigning them nights again this month when they already have a high night count.

## Example

Suppose two employees are equally valid candidates for a night shift on a given day. Employee A worked 9 nights last month; Employee B worked 4. The history bias penalty for assigning A to night is higher than for assigning B. The engine will prefer B for that night slot.

## Parameters

| Parameter | Default | Description |
|---|---|---|
| `W_HISTORY_BIAS` | `5` | Penalty weight per unit of history-weighted assignment |

## Interaction with other constraints

History bias works alongside [even shift distribution](shift-balance.md). Both push toward fairness, but from different angles — shift balance looks at the current period only, while history bias looks across the month boundary. Together they produce rosters that are fair both within the period and over time.
