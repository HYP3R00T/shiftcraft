---
icon: lucide/lock
---

# Leave capacity gate per day

## What it means

The number of employees who can be off on any given day is limited by how many workers are needed to meet minimum coverage. The engine computes the maximum allowable absences for each day as the difference between team size and the total minimum workers required across all shifts.

## Why it exists

Coverage minimums define the floor for how many people must be working. If too many employees are off simultaneously, that floor cannot be met. This constraint enforces the relationship between absence and coverage as a hard rule, preventing the engine from approving more leave than the team can absorb.

## Example

Suppose the team has five employees and a given day requires a minimum of three workers across all shifts (one morning, one afternoon, one night). The maximum number of employees who can be off that day is two (5 - 3 = 2).

If three employees have hard leave requests on that day, the engine cannot honor all three. It will report an infeasible result identifying that date and the conflicting requests.

## How it interacts with leave types

The capacity gate applies to all off days regardless of leave type — `week_off`, `annual`, and `comp_off` all count toward the daily absence total. The gate does not distinguish between leave types; it only cares about the total number of people absent.

## Interaction with other constraints

This is one of the most common sources of infeasibility. It interacts with [typed leave must be honored exactly](typed-leave-honored.md), [two offs per week](two-offs-per-week.md), and [minimum shift coverage](min-shift-coverage.md). When diagnosing an infeasible result, checking the leave capacity gate for each day is usually the first step.
