# Design

Internal engineering documentation for Shiftcraft. Not published to the
user-facing docs site.

## What lives here

| Path | Purpose |
|---|---|
| `problem.md` | Problem statement and constraint taxonomy |
| `architecture.md` | System shape, components, data flow, cross-cutting concerns |
| `adr/` | Architecture decision records — one file per decision |
| `services/core/` | Design docs for shiftcraft-core (solver engine) |
| `services/api/` | Design docs for shiftcraft-api |
| `services/web/` | Design docs for shiftcraft-web |

## Reading order

1. `problem.md` — understand the problem space
2. `architecture.md` — understand the system shape
3. `adr/` — understand why key decisions were made
4. `services/<name>/` — understand a specific service

---

## How to add a document

### Adding a service design doc

Create a file under `services/<service-name>/`. The service name should
match the package name: `core`, `api`, `web`.

```sh
design/services/core/constraint-primitives.md
design/services/api/endpoints.md
design/services/web/data-model.md
```

Use this structure inside the file:

```markdown
# <Title>

## Context
What problem does this document address? Why does this exist?

## Design
The actual design — data structures, flows, decisions.

## Constraints
What must this design not violate? What are the hard boundaries?

## Open questions
Anything not yet decided. Remove entries as they are resolved.
```

### Adding an ADR

Create a file under `adr/` named `NNN-short-title.md` where NNN is the
next available number.

```sh
design/adr/001-dynamic-constraint-engine.md
design/adr/002-cp-sat-solver.md
```

Use the MADR format ([madr.adr.github.io](https://adr.github.io/madr/)):

```markdown
# {short title — problem and solution}

## Context and Problem Statement

{What is the situation? What problem needs to be solved?
Two to three sentences is enough.}

## Considered Options

- {option 1}
- {option 2}
- {option 3}

## Decision Outcome

Chosen option: "{option}", because {justification}.

### Consequences

- Good, because {positive consequence}
- Bad, because {negative consequence or trade-off}

## Pros and Cons of the Options

### {option 1}

- Good, because {argument}
- Bad, because {argument}

### {option 2}

- Good, because {argument}
- Bad, because {argument}
```

Optional fields you can add at the top as frontmatter:

```yaml
---
status: accepted          # proposed | accepted | deprecated | superseded by ADR-NNN
date: YYYY-MM-DD
---
```

ADRs are not edited once accepted. If a decision changes, write a new ADR
and mark the old one as `superseded by ADR-NNN`.

### Updating existing documents

Edit the file directly. The git history records what changed and when.
For significant changes, the commit message should explain why, not just
what changed.

---

## What not to do

- Do not create placeholder files or empty READMEs in sub-folders.
  Create a file only when you have real content to put in it.
- Do not duplicate content across documents. If something is defined in
  `problem.md`, reference it — do not restate it.
- Do not let documents grow beyond what is useful. If a section has not
  been read or updated in a long time, consider removing it.
