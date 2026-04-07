# Scheduling Problem — Foundations & Constraint Taxonomy

## Problem statement

Given a set of people P, a set of days D, and a set of states S, find an
assignment function:

```text
f : P x D -> S
```

such that all hard constraints are satisfied and the total penalty from soft
constraint violations is minimised.

## Fundamental variables

- P — a finite set of people (employees), each carrying attributes and
  balance records
- D — a finite ordered set of days (the scheduling period), each carrying
  a day type and coverage requirements
- S — a finite set of states (working states and off states)
- f(p, d) — the state assigned to person p on day d

## Day types

Every day d in D has a day type. The day type is metadata on the day — it
is not a state and is not part of the assignment. It affects which states
are valid on that day and what coverage is required.

In general, T (the set of day types) is open — any number of types could
exist. In this problem, T has exactly two elements:

- `regular` — a normal working day. No special designation. Coverage
  requirements apply as configured for that day of the week. All states
  are valid subject to other constraints.

- `holiday` — a public holiday. This is a binary flag on the day, scoped
  per employee by location: for a given day d and employee p,
  is_holiday(p, d) is either true or false. Different locations may observe
  different holidays, overlapping subsets, or none at all.

  A holiday day has two configurable properties:
    - Coverage requirements: how many employees are needed on each working
    state on this day. This may be zero (no one needs to work) or non-zero
    (some must work). Configured independently from regular day coverage.
    - Scope: the set of employees for whom is_holiday(p, d) = true, defined
    by a location attribute on p.

  A holiday does not automatically determine any assignment. What it does:
    - Makes the calendar-gated off state (e.g. `public_holiday`) valid for
    employees where is_holiday(p, d) = true. That state is blocked for all
    other employees on that day, and blocked for everyone on regular days.
    - May trigger a derivation rule for employees who work on it (see
    Derivation rules section).
    - Has no effect on the week_off frequency requirement. `week_off` and
    `public_holiday` are independent off states. An employee in a week with
    one holiday still needs their full week_off allocation that week.

## State categories

S is partitioned into two disjoint subsets:

- S_work — working states. The person is present and assigned to a shift.
  The set of working states is open and defined by configuration.
  Example: morning, afternoon, night, regular, on_call

- S_off — off states. The person is absent.
  The set of off states is open and defined by configuration.
  Example: week_off, annual, comp_off, public_holiday

All absent states are off states. They share the same nature — the person
is not working. What differs between them is the governance rule that
controls how many times each one may be used. There are exactly three
orthogonal governance forms:

- Window-frequency governed
    - For every recurring sub-window W of D of a defined type, the count of
    days where f(p, d) = v within W must satisfy a condition. The condition
    resets with every window. No balance is consumed. No request is needed.
    - This form cannot be expressed as total-bound because it applies
    independently to every window, not to the period total.
    - Example: week_off must occur exactly 2 times in every ISO calendar week.
    This is a structural rest requirement. It resets every week. A week
    where is_holiday(p, d) = true for one day still requires exactly 2
    week_offs — the public_holiday off is additional, not a substitute.

- Total-bound governed
    - Across the full period D, the count of days where f(p, d) = v must not
    exceed a bound N(p, v) that belongs to the person. The constraint form
    is: count(p, v) <= N(p, v). How N is derived is an input concern, not
    a constraint category. Two derivation methods exist:
        - Fixed quota: N is given upfront as a number (e.g. 12 annual leave
      days remaining). It decrements on use and may have a validity window
      (e.g. must be used within the calendar year).
        - Earned records: N is the count of valid, unexpired, unredeemed records
      for person p (e.g. comp_off records earned when is_holiday(p, d) = true
      and f(p, d) belongs to S_work). Each record has an earned date and a
      validity duration. N increments when a record is earned and decrements
      when one is consumed.
    - Both derivation methods reduce to the same constraint at solve time.
    - This form cannot be expressed as window-frequency because it has no
    recurring window structure.
    - Example: annual leave is bounded by a remaining quota. comp_off is
    bounded by the count of valid earned records.

- Calendar-gated governed
    - The state may only be assigned when is_holiday(p, d) = true for that
    employee. It is blocked on all other days. No balance is consumed. No
    frequency condition applies. Placement is determined entirely by the
    day type flag and coverage requirements.
    - This form cannot be expressed as window-frequency (it does not recur
    on a schedule) and cannot be expressed as total-bound (there is no
    balance). It operates on cell validity, not on counts.
    - Example: public_holiday may only be assigned when is_holiday(p, d) = true
    for that employee. It does not consume annual leave or week_off. An
    employee in a week where is_holiday(p, d) = true for one day will have
    3 off days that week: 1 public_holiday and 2 week_off.

Which states belong to which governance form is configuration. The problem
formulation does not hardcode any state names.

## Derivation rules

Some events during scheduling produce side effects that generate new balance
records for a person. These are derivation rules. They operate outside the
constraint system — they do not restrict assignments, they produce data that
feeds the total-bound governance of off states.

Derivation rules are optional and configurable per team. Whether a rule
applies, and what it produces, is part of the problem configuration.

One derivation rule is defined in this problem:

- Comp_off accrual: if f(p, d) belongs to S_work and is_holiday(p, d) = true,
  then a new comp_off record is created for p with earned date d and a
  validity duration defined by configuration. The record is valid immediately
  from the earned date — it may be used within the same scheduling period if
  the earned date falls before the period end. It affects the total-bound
  governance of the comp_off state: N(p, comp_off) increases by 1.

## Time granularity

D is a set of calendar days. Each element of D is one day. The problem
assigns exactly one state per person per day. What a state means in terms
of clock hours is outside the problem — that is configuration.

## The assignment matrix

f can be visualised as a matrix where rows are people and columns are days:

```text
         Day1     Day2     Day3     ...     DayN
Person1  f(p1,d1) f(p1,d2) f(p1,d3)        f(p1,dN)
Person2  f(p2,d1) f(p2,d2) f(p2,d3)        f(p2,dN)
...
PersonM  f(pM,d1) f(pM,d2) f(pM,d3)        f(pM,dN)
```

Every cell holds exactly one element of S. A constraint is a rule about the
values in this matrix.

## Base constraints

These are not configurable rules. They define what a valid assignment is.

- Completeness — f(p, d) must be defined for every p in P and every d in D.
  No cell may be left empty.

- Exclusivity — f(p, d) is a single value from S. A person cannot hold two
  states on the same day.

## Constraint taxonomy

### Category 1 — Cell-level constraints

Rules about the value of a single cell f(p, d). There are exactly two
orthogonal primitives. Enforcement level (hard or soft) is a property
applied to either — it does not create a third primitive.

- Value assignment
    - Definition: for a given person p and day d, f(p, d) should or must
    equal a specific value v.
    - Hard: the solver has no choice. The cell is fixed.
    - Soft: if f(p, d) does not equal v, a penalty is incurred. The solver
    tries to satisfy it but is not required to.
    - Example (hard): an employee's annual leave request is approved. That
    cell must be `annual`.
    - Example (hard): an employee is not working on a holiday day —
    that cell must be `public_holiday`, not `week_off` or `annual`.
    - Example (soft): an employee requests a day off without specifying
    which off state. The solver tries to assign any off state but may
    assign a working state if coverage demands it.

- Value exclusion
    - Definition: for a given person p and day d, f(p, d) should or must
    not be any value in a set V_excluded.
    - Hard: the solver may assign any state outside V_excluded. Violation
    makes the schedule infeasible.
    - Soft: if f(p, d) belongs to V_excluded, a penalty is incurred.
    - Example (hard): during a blackout period, `annual` and `comp_off` are
    blocked for all employees on those days.
    - Example (hard): `public_holiday` is blocked on all days where
    is_holiday(p, d) = false. This is the cell-level expression of
    calendar-gated governance.

### Category 2 — Row-level constraints

Rules about the values across all days for a single person p. These operate
on the row vector [ f(p, d1), f(p, d2), ..., f(p, dN) ].

There are exactly three orthogonal sub-categories. Count, sequence, and
balance operate on completely different dimensions of the row vector and
none can be expressed as another.

#### 2a. Count-based

How many times does a value v (or a set V) appear in this person's row,
measured over a defined time window? The constraint form is always:
count operator threshold, where the window and threshold vary.

- Per-week count
    - Definition: for each ISO calendar week W within D, the count of days
    in W where f(p, d) = v must satisfy: count operator threshold. Operator
    is one of: equal to, at least, at most.
    - Example: every employee must have exactly 2 days where f(p, d) =
    `week_off` in every calendar week. This counts only `week_off` — not
    `public_holiday`, `annual`, or any other off state. A week where
    is_holiday(p, d) = true for one day will have 3 off days total:
    1 `public_holiday` and 2 `week_off`. The frequency rule applies to
    `week_off` alone.

- Sliding window count
    - Definition: for every consecutive subsequence of D of length N, the
    count of days where f(p, d) belongs to a set V must satisfy: count
    operator threshold.
    - Example: in any 7-day window, an employee may work at most 6 days
    (count of days where f(p, d) belongs to S_work is at most 6). If this
    comes from a labour regulation it is hard — violating it makes the
    schedule infeasible. If it expresses a preference it is soft — violating
    it incurs a penalty. The enforcement level is configuration.

- Period count
    - Definition: across all days in D, the count of days where f(p, d) = v
    must satisfy: count operator threshold. An optional filter restricts
    counting to a subset of D (e.g. only weekends).
    - Example: across the full month, an employee may take at most 5 days
    where f(p, d) = `annual`. Or: at most 3 weekend days may be working
    states.

- Person-bound count
    - Definition: across all days in D, the count of days where f(p, d) = v
    must not exceed a bound N(p, v) that belongs to person p. The constraint
    form is: count(p, v) <= N(p, v). N is derived from input data — either
    a fixed quota or the count of valid earned records for p. Both reduce
    to the same constraint form at solve time.
    - Example (quota): an employee has 8 remaining days of annual leave.
    count(p, annual) must not exceed 8.
    - Example (records): an employee has 2 valid comp-off records.
    count(p, comp_off) must not exceed 2.
    - Note: this is a period count where the threshold is person-specific and
    derived from a balance rather than a fixed configuration value. The
    constraint form is identical — only the source of the threshold differs,
    which is an input concern.

#### 2b. Sequence-based

What is the relationship between f(p, d) and f(p, d') for adjacent or
near-adjacent days? The constraint form is always: given the value(s) on
day d, what is required or forbidden on day d+k?

- Pair sequence
    - Definition: if f(p, d) = A, then f(p, d+1) must not equal B (or must
    equal B). Applies to every consecutive pair of days in D. Enforcement
    is hard or soft depending on configuration.
    - Example (hard): if f(p, d) = `night`, then f(p, d+1) must not equal
    `morning`. The transition night -> morning is forbidden.
    - Example (soft): if f(p, d) = `morning` and f(p, d+1) belongs to S_work
    but f(p, d+1) ≠ `morning`, a penalty is incurred. The solver prefers
    runs of the same working state. This is shift block stability expressed
    as a soft pair sequence rule.

- Length-N sequence
    - Definition: if f(p, d-N+1) through f(p, d) are all equal to A (N
    consecutive days of A), then within the next M days, the count of days
    where f(p, d') = B must satisfy: count operator threshold. Enforcement
    is hard or soft depending on configuration.
    - Example (hard): after 3 consecutive days where f(p, d) = `night`, at
    least 2 of the following 2 days must have f(p, d') = `week_off`.
    - Example (soft): if Saturday and Sunday are adjacent and f(p, Saturday)
    belongs to S_off, then f(p, Sunday) should also belong to S_off. A
    split weekend is penalised. This is day pairing expressed as a soft
    length-1 sequence rule.

#### 2c. Balance-based

How evenly distributed are working states across a person's row over the
full period? The constraint form is always: the difference between the
maximum and minimum count of any working state must be bounded.

- Per-person spread
    - Definition: let count(p, v) be the number of days where f(p, d) = v.
    For a set of working states V_work, the difference between the maximum
    and minimum count across all v in V_work must be at most some bound B:
    max(count(p, v)) - min(count(p, v)) is at most B, for all v in V_work.
    - Example: across the month, the counts of `morning`, `afternoon`, and
    `night` for one employee should differ by at most 1. An employee with
    9 mornings, 6 afternoons, and 6 nights violates this if B = 1.
    - Note: balance is orthogonal to count-based rules because it requires
    comparing multiple values simultaneously. A single count constraint
    cannot express "the difference between the counts of v1 and v2 is
    bounded" — that requires two counts and a comparison between them.

### Category 3 — Column-level constraints

Rules about the distribution of values across all people on a single day d.
These operate on the column vector [ f(p1, d), f(p2, d), ..., f(pM, d) ].

There are exactly three orthogonal primitives. Minimum, maximum, and target
all share the same form — count operator threshold — and collapse into one
primitive with enforcement level as a property. Ratio and conditional are
genuinely different forms and cannot be expressed as each other or as a
plain count.

- Count constraint
    - Definition: for a given day d and state v (or set V), the count of
    people where f(p, d) = v must satisfy: count operator threshold.
    Operator is one of: at least, at most, equal to. Enforcement is hard
    or soft.
    - Hard (minimum): count >= T_min. The schedule is infeasible if not met.
    - Hard (maximum): count <= T_max. The schedule is infeasible if exceeded.
    - Soft (target): count should be T_target. A penalty proportional to the
    shortfall is incurred if the actual count falls below T_target. The
    schedule remains valid as long as the hard minimum is met.
    - Example: at least 2 employees must have f(p, d) = `morning` every day
    (hard minimum). Ideally 3 should (soft target). At most 5 may (hard
    maximum).

- Ratio constraint
    - Definition: for a given day d, let N_group be the count of people in a
    defined sub-group (e.g. all people where f(p, d) belongs to S_work).
    The count of people in a further sub-group with state v, divided by
    N_group, must satisfy: ratio operator threshold. Enforcement is hard
    or soft.
    - This is orthogonal to count constraint because the denominator N_group
    varies per day — it cannot be reduced to a fixed threshold.
    - Example: at least 40% of employees working on any day must have the
    attribute role = senior.

- Conditional constraint
    - Definition: if the count of people with state A on day d satisfies
    condition C1, then the count of people with state B on day d must
    satisfy condition C2. This is an implication: C1 implies C2.
    Enforcement is hard or soft.
    - This is orthogonal to count and ratio because it links two counts via
    an implication. Neither a plain count nor a ratio can express "if X
    then Y."
    - Example: if more than 5 employees have a working state on a day, at
    least 1 of them must have the attribute role = manager.

### Category 4 — Cross-row constraints

Rules that link the assignments of two specific people on the same day.
These operate on pairs of cells f(p1, d) and f(p2, d) for the same d.

There is exactly one orthogonal primitive. Mutual exclusion and co-assignment
are both special cases of dependency with specific parameterisations.

- Dependency
    - Definition: for two people p1 and p2, if f(p1, d) belongs to a set V1,
    then f(p2, d) must belong to a set V2. Enforcement is hard or soft.
    - Mutual exclusion is a special case: V1 = V, V2 = S \ V. If p1 is in
    the excluded set, p2 must not be. "Two key employees cannot both be
    absent" is: if f(p1, d) in S_off then f(p2, d) must be in S_work.
    - Co-assignment is a special case: for every v in S, V1 = {v} and
    V2 = {v}. If p1 is on morning, p2 must also be on morning. Expressed
    directly as f(p1, d) = f(p2, d).
    - Example (dependency): if f(team_lead, d) belongs to S_off, then
    f(deputy, d) must belong to S_work.
    - Example (mutual exclusion): two key employees must not both have off
    states on the same day.
    - Example (co-assignment): two paired workers must always be on the same
    shift.

### Category 5 — Matrix-level constraints

Rules about fairness or balance across the entire matrix — all people over
all days. There are exactly two orthogonal primitives. Team-level spread
and weekend off balance share the same form and collapse into one primitive
with an optional day filter. History continuity references external data
from a prior period and cannot be expressed as a spread constraint.

- Cross-person spread (soft)
    - Definition: let count(p, v, F) be the number of days in a filtered
    subset F of D where f(p, d) = v for person p. Across all people in P,
    the difference between the maximum and minimum count must be minimised:
    max over P of count(p, v, F) minus min over P of count(p, v, F) is
    minimised. F is optional — if omitted, counts across all days in D.
    - Team-level spread is this primitive with F = D (no filter).
    Example: the number of `night` shifts should be roughly equal for all
    employees across the month.
    - Weekend off balance is this primitive with F = weekend days and
    v = any state in S_off.
    Example: the number of weekend off days should be roughly equal for all
    employees across the month.

- History continuity (soft)
    - Definition: let hist(p, v) be the count of days with state v for person
    p in the immediately preceding period. The solver penalises assigning
    more of state v to person p when hist(p, v) is already high, biasing
    toward states that were underrepresented last period.
    - This is orthogonal to cross-person spread because it references counts
    from a prior period, not the current matrix. No spread constraint can
    express a bias based on external historical data.
    - Example: an employee who had many `night` shifts last month should
    receive fewer `night` shifts this month, all else being equal.

## Primitive reference

| Category | Primitive | Enforcement |
|---|---|---|
| Base | Completeness | Implicit |
| Base | Exclusivity | Implicit |
| Cell | Value assignment | Hard or Soft |
| Cell | Value exclusion | Hard or Soft |
| Row — count | Per ISO week | Hard or Soft |
| Row — count | Sliding window | Hard or Soft |
| Row — count | Full period | Hard or Soft |
| Row — count | Person-bound (quota or records) | Hard |
| Row — sequence | Pair (A -> B), incl. shift block stability | Hard or Soft |
| Row — sequence | Length-N run -> consequence, incl. day pairing | Hard or Soft |
| Row — balance | Per-person spread | Soft |
| Column | Count constraint (min / max / target) | Hard or Soft |
| Column | Ratio constraint | Hard or Soft |
| Column | Conditional constraint | Hard or Soft |
| Cross-row | Dependency (incl. mutual exclusion, co-assignment) | Hard or Soft |
| Matrix | Cross-person spread (incl. weekend off balance) | Soft |
| Matrix | History continuity | Soft |
