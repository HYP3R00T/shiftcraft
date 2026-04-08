---
status: accepted
date: 2026-04-08
---

# Full rewrite of shiftcraft-core — no backward compatibility

## Context and Problem Statement

The new dynamic constraint engine (ADR-001) is a complete departure from
the existing `shiftcraft-core`. The data model, primitive names, dispatch
model, and input/output shapes are all different. The existing code cannot
be incrementally migrated — it must be replaced.

Backward compatibility with the old API is not a requirement. There are no
external consumers that need to be preserved.

How do we approach the rewrite?

## Considered Options

- Parallel build — build new engine alongside old code, switch over when ready
- Full in-place rewrite — delete old code, build new engine from scratch

## Decision Outcome

Chosen option: full in-place rewrite, because backward compatibility is not
required and the old code has no value to preserve.

The existing flat files (`constraints.py`, `objective.py`, `solver.py`,
`types.py`, `variables.py`, `parser.py`, `formatter.py`) will be deleted.
The new engine will be built in the sub-folders that already exist
(`engine/`, `primitives/`, `scope/`, `types/`, `parser/`, `formatter/`).

The rewrite is complete when the new engine can generate a valid schedule
from a JSON payload matching the new input format defined in
`design/architecture.md` and `design/services/core/constraint-primitives.md`.

### Consequences

- Good, because no dead code remains in the package during or after the rewrite
- Good, because the new structure is clean from the first commit
- Good, because there is no confusion about which implementation is active
- Bad, because the package produces no output until the rewrite is complete
- Bad, because there is no fallback if the rewrite hits an unexpected problem

## Pros and Cons of the Options

### Parallel build

- Good, because old system keeps working during development
- Bad, because backward compatibility is not needed — the old system has
  no value to preserve
- Bad, because the package contains two implementations simultaneously,
  creating confusion about which is active

### Full in-place rewrite (chosen)

- Good, because the codebase is clean throughout
- Good, because the new design is implemented without compromise
- Neutral, because the package is non-functional during the rewrite —
  acceptable since there are no active consumers
