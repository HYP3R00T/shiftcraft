"""
Analyze the solver output.

Reads output.json and prints:
  - Per-employee shift counts for the month
  - Weekly off counts per employee per ISO week
  - Validation of hard constraints
"""

import json
from collections import defaultdict
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_PATH = BASE_DIR / "output.json"
INPUT_PATH = BASE_DIR / "input.json"

data = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
inp = json.loads(INPUT_PATH.read_text(encoding="utf-8"))

# Build id → name map
id_to_name = {e["id"]: e["name"] for e in inp["team"]}

# schedule is date-keyed: { date_iso: { emp_id: shift } }
# Transpose to emp-keyed for analysis: { emp_id: { date_iso: shift } }
_schedule_by_date: dict[str, dict[str, str]] = data["schedule"]
schedule: dict[str, dict[str, str]] = {}
for d_iso, emp_map in _schedule_by_date.items():
    for emp_id, shift in emp_map.items():
        schedule.setdefault(emp_id, {})[d_iso] = shift
status = data["status"]

print("=" * 72)
print(
    f"STATUS: {status.upper()}   |   Objective: {data['metadata'].get('objective')}   |   Solve time: {data['metadata']['solve_time_seconds']}s"
)
print("=" * 72)

if status not in ("optimal", "feasible"):
    print("No schedule to analyse.")
    raise SystemExit(1)

# ── Shift counts ──────────────────────────────────────────────────────────────
print("\nSHIFT COUNTS (full month)")
print("-" * 72)
header = f"{'Name':10s}  {'morning':>7}  {'afternoon':>9}  {'night':>5}  {'regular':>7}  {'week_off':>8}  {'annual':>6}  {'comp_off':>8}  {'total':>5}"
print(header)
print("-" * 72)

for emp_id, days in schedule.items():
    name = id_to_name.get(emp_id, emp_id)
    counts: dict[str, int] = defaultdict(int)
    for state in days.values():
        counts[state] += 1
    total = sum(counts.values())
    print(
        f"{name:10s}  "
        f"{counts['morning']:>7}  "
        f"{counts['afternoon']:>9}  "
        f"{counts['night']:>5}  "
        f"{counts['regular']:>7}  "
        f"{counts['week_off']:>8}  "
        f"{counts['annual']:>6}  "
        f"{counts['comp_off']:>8}  "
        f"{total:>5}"
    )

# ── Weekly off counts ─────────────────────────────────────────────────────────
print("\nWEEKLY OFF COUNTS (per ISO week)")
print("-" * 72)

emp_week_offs: dict[str, dict[int, int]] = defaultdict(lambda: defaultdict(int))
for emp_id, days in schedule.items():
    for date_iso, state in days.items():
        if state == "week_off":
            d = date.fromisoformat(date_iso)
            week = d.isocalendar().week
            emp_week_offs[emp_id][week] += 1

all_weeks = sorted({w for wmap in emp_week_offs.values() for w in wmap})
week_header = f"{'Name':10s}  " + "  ".join(f"W{w:02d}" for w in all_weeks) + "  Total"
print(week_header)
print("-" * 72)

for emp_id in schedule:
    name = id_to_name.get(emp_id, emp_id)
    row = f"{name:10s}  "
    total = 0
    for w in all_weeks:
        c = emp_week_offs[emp_id].get(w, 0)
        row += f"  {c:3d}"
        total += c
    row += f"  {total:5d}"
    print(row)

# ── Validation ────────────────────────────────────────────────────────────────
print("\nVALIDATION")
print("-" * 72)

issues: list[str] = []

# Check week_off == 2 for full weeks (skip partial boundary weeks)
period_start = date.fromisoformat(inp["period"]["start"])
period_end = date.fromisoformat(inp["period"]["end"])

for emp_id, wmap in emp_week_offs.items():
    name = id_to_name.get(emp_id, emp_id)
    for week, count in wmap.items():
        # Determine if this is a partial week at the period boundary.
        # A full ISO week has 7 days; if the period clips it, it's partial.
        week_days_in_period = sum(
            1 for d_iso in schedule[emp_id] if date.fromisoformat(d_iso).isocalendar().week == week
        )
        if week_days_in_period < 7:
            # Partial week — just check at least 0 (no hard requirement).
            continue
        if count != 2:
            issues.append(f"{name} W{week:02d}: {count} week_offs (expected 2)")

# Check night → morning forbidden transition
for emp_id, days in schedule.items():
    name = id_to_name.get(emp_id, emp_id)
    sorted_days = sorted(days.items())
    for i in range(len(sorted_days) - 1):
        d1, s1 = sorted_days[i]
        d2, s2 = sorted_days[i + 1]
        if s1 == "night" and s2 == "morning":
            issues.append(f"{name}: night→morning transition on {d1}→{d2}")

# Check leave preferences were honoured
preferences = [
    ("E001", "2026-04-05"),
    ("E001", "2026-04-18"),
    ("E001", "2026-04-19"),
    ("E001", "2026-04-23"),
    ("E005", "2026-04-03"),
    ("E005", "2026-04-04"),
    ("E003", "2026-04-28"),
]
for emp_id, date_iso in preferences:
    name = id_to_name.get(emp_id, emp_id)
    state = schedule.get(emp_id, {}).get(date_iso)
    if state not in ("annual", "week_off", "comp_off", "public_holiday"):
        issues.append(f"{name} {date_iso}: preference for off not honoured (got {state!r})")

if issues:
    print(f"\n[!] {len(issues)} issue(s) found:")
    for issue in issues:
        print(f"    - {issue}")
else:
    print("\n[OK] All checked constraints satisfied.")

print("\nNote: preference violations above are expected — the solver may override")
print("      employee day-off preferences when coverage requires it.")
