---
status: accepted
date: 2026-04-08
---

# Dynamic constraint engine — rules as data, not code

## Context and Problem Statement

The original `shiftcraft-core` had all scheduling rules hardcoded in Python.
Adding or changing a rule meant editing the package, publishing a new version,
and redeploying. This worked for a single team with fixed requirements.

The problem: every team has different rules. Different shift structures,
different rest day policies, different location-specific holidays, different
leave entitlements. With hardcoded constraints, supporting a second team
means forking the codebase or adding conditional logic — both of which
compound with every new team.

How do we build a scheduling engine that works for any team without changing
code when rules change?

## Considered Options

- Hardcoded constraints per team (current approach)
- Configuration flags to toggle predefined constraint variants
- Rules as data — a primitive system where constraints are JSON descriptors

## Decision Outcome

Chosen option: rules as data, because it is the only option that scales to
arbitrary teams without code changes.

Configuration flags only work for a known, finite set of variants. The
moment a team needs a rule that wasn't anticipated, a code change is still
required. It defers the problem rather than solving it.

Rules as data means the engine is a compiler: it reads rule descriptors and
emits CP-SAT constraints. Adding a rule for a team = adding a JSON object.
Adding a new primitive type = adding one Python function. The engine itself
never changes when business rules change.

### Consequences

- Good, because any team can configure their own rules without a developer
- Good, because rules are auditable — the JSON is the source of truth
- Good, because the engine is stable — new teams don't require new deployments
- Bad, because the initial design is more complex than hardcoded constraints
- Bad, because rule conflicts must be detected and reported explicitly

## Pros and Cons of the Options

### Hardcoded constraints per team

- Good, because simple to implement initially
- Bad, because every new team or rule change requires a code change
- Bad, because teams with overlapping but different rules create branching logic

### Configuration flags

- Good, because simpler than a full primitive system
- Neutral, because works for anticipated variants
- Bad, because fails the moment a team needs an unanticipated rule
- Bad, because the flag space grows unbounded over time

### Rules as data (chosen)

- Good, because the engine is team-agnostic
- Good, because rules are composable — any WHO can combine with any WHEN
- Good, because CP-SAT handles the mathematical form regardless of meaning
- Bad, because requires a well-defined primitive taxonomy upfront
- Bad, because infeasibility reporting is harder than with hardcoded constraints
