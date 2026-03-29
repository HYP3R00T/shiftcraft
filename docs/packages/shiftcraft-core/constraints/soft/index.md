---
icon: lucide/sliders
---

# Soft constraints

Soft constraints are preferences. Violating them does not make a roster invalid, but each violation adds a weighted penalty to the roster's score. The engine selects the roster with the lowest total penalty from among all valid rosters.

Each soft constraint has a weight. A higher weight means the engine treats that preference as more important relative to others. When two preferences conflict, the one with the higher weight tends to win.

## How penalty scoring works

The total penalty is the sum of all individual penalty contributions:

```text
total_penalty = sum of (weight × deviation) for each soft constraint
```

The `penalty` value in the output represents this total. Lower is better. A penalty of zero would mean every soft preference was fully met, which is rarely achievable in practice.

## Shift preferences

- [Even shift distribution](shift-balance.md) — weight 10
- [Shift block stability](shift-block-stability.md) — weight 8
- [Prior-month history bias](history-bias.md) — weight 5

## Off-day preferences

- [Balanced weekend offs](weekend-off-balance.md) — weight 6
- [Paired Saturday and Sunday offs](paired-weekend-offs.md) — weight 4

## Coverage preferences

- [Target coverage shortfall](target-coverage.md) — weight 3

## Leave preferences

- [Untyped leave date preference](untyped-leave-preference.md) — weight 7

## Weight summary

| Preference | Weight |
|---|---|
| Even shift distribution | 10 |
| Untyped leave preference | 7 |
| Shift block stability | 8 |
| Weekend off balance | 6 |
| Prior-month history bias | 5 |
| Paired weekend offs | 4 |
| Target coverage shortfall | 3 |
