---
icon: lucide/lock
---

# Hard constraints

Hard constraints are rules that every valid roster must satisfy. A roster that violates any hard constraint is rejected entirely — the engine will not return it, even if it scores well on soft preferences.

If no roster can satisfy all hard constraints simultaneously, the engine returns an infeasible result with a list of the specific dates and rules that caused the conflict.

## Assignment

- [One shift per person per day](one-shift-per-day.md)
- [No night-to-morning transition](no-night-to-morning.md)
- [Two off days per calendar week](two-offs-per-week.md)

## Coverage

- [Minimum shift coverage](min-shift-coverage.md)
- [Maximum shift coverage](max-shift-coverage.md)
- [Maximum working employees per day](max-workers-per-day.md)
- [Date-range coverage overrides](date-range-override.md)
- [Regular shift assigned after core shifts](regular-shift-order.md)

## Leave

- [Typed leave must be honored exactly](typed-leave-honored.md)
- [Annual and comp-off only on requested dates](leave-on-requested-dates.md)
- [Comp-off cannot exceed valid balance](comp-off-validity.md)
- [Leave capacity gate per day](leave-capacity-gate.md)

## Fairness

- [Core shift balance per employee](core-shift-balance.md)
