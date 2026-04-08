# Basic App Example

Generates an April 2026 roster for a real 5-person team using `shiftcraft-core`.

## Files

| File | Purpose |
|---|---|
| `settings.json` | Rules of the game — shifts, leave types, constraints |
| `input.json` | This run's data — team, period, history, balances |
| `run.py` | Loads both files, calls `solve()`, writes `output.json` |
| `analyze_output.py` | Reads `output.json` and prints shift counts + validation |

## Run

```sh
# From the repo root
uv run python examples/basic_app/run.py
uv run python examples/basic_app/analyze_output.py
```

Or via mise:

```sh
mise run example-basic
```

## Team

5 members across Hyderabad and Bengaluru. Shifts: morning, afternoon, night, regular.

## Key constraints

- Exactly 2 week-offs per full ISO calendar week per person
- At least 1 person on each of morning / afternoon / night every day
- No night → morning transition on consecutive days
- Comp-off usage bounded by each person's earned balance
- Employee day-off preferences honoured where coverage allows
