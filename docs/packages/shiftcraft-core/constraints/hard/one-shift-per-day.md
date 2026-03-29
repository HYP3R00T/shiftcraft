---
icon: lucide/lock
---

# One shift per person per day

## What it means

A person can be assigned to at most one shift on any given calendar day. They are either working one shift or they are off. There is no concept of a split day or a partial shift.

## Why it exists

Overlapping shift assignments would produce an incoherent schedule — a person cannot physically be in two places at once, and payroll systems expect a single assignment per person per day.

## Example

Suppose the team has a morning, afternoon, and night shift running on the same day.

If someone is assigned to night, they cannot also appear as morning or afternoon on that same day. The engine will never produce a row where one person has two shift values on the same date.

## Parameters

| Parameter | Default | Description |
|---|---|---|
| `max_shifts_per_person_per_day` | `1` | Maximum shifts one person can work in a single day |

## Interaction with other constraints

This constraint works together with the [leave capacity gate](leave-capacity-gate.md). On any given day, each employee is in exactly one state: working one shift, or off under one leave type.
