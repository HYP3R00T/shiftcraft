---
icon: lucide/shield
---

# Constraints

Constraints are the rules the engine uses to evaluate and select a roster. They fall into two categories.

## Hard constraints

Hard constraints are non-negotiable. Every valid roster must satisfy all of them. If no roster can satisfy all hard constraints simultaneously, the engine returns an infeasible result with an explanation of which rules were violated and on which dates.

[Browse hard constraints](hard/index.md)

## Soft constraints

Soft constraints are preferences. Violating them does not make a roster invalid. Instead, each violation adds a weighted penalty to the roster's score. The engine selects the roster with the lowest total penalty from among all valid rosters.

[Browse soft constraints](soft/index.md)

---

## How the two types interact

The engine always applies hard constraints first. Only rosters that pass all hard constraints are considered for optimization. Soft constraints then rank those valid rosters and select the best one.

This means soft constraints can never override hard constraints. If a preference conflicts with a hard rule, the hard rule always wins.

A practical consequence: if you configure very tight hard constraints — high minimum coverage, a small team, many leave requests — the feasible space shrinks. The engine may find a valid roster that scores poorly on soft preferences simply because there are few valid options to choose from.
