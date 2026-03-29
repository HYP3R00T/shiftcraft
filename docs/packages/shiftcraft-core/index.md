---
icon: lucide/package
---

# shiftcraft-core

`shiftcraft-core` is the scheduling engine at the heart of shiftcraft. It takes a structured description of your team, their leave history, and your coverage requirements, then produces a day-by-day roster that satisfies all mandatory rules and optimizes for fairness where possible.

The engine is built on [Google OR-Tools CP-SAT](https://developers.google.com/optimization/reference/python/sat/python/cp_model), a constraint programming solver. You describe the problem; the solver finds the best valid answer.

## What it does

Given a scheduling period and a team, the engine decides:

- who works on each day
- which shift each person is assigned to
- who is off, and under what leave type
- which leave requests can be honored
- what gaps remain if the problem has no valid solution

## How it works

The engine runs in two passes.

First, it applies all hard constraints — rules that must hold in every valid roster. If no roster satisfies all hard constraints, the engine stops and returns a structured failure with the specific dates and rules that caused the conflict.

Second, if a feasible roster exists, the engine optimizes it. Each soft preference is expressed as a weighted penalty. The solver minimizes the total penalty across all preferences, producing the fairest roster it can find within the time limit.

The output always includes the total penalty score so the result is explainable and auditable.

## Sections

- [Input format](input.md) — what the engine expects
- [Output format](output.md) — what the engine returns
- [Constraints](constraints/index.md) — all rules, hard and soft
- [API Reference](api-reference.md) — auto-generated from source docstrings
