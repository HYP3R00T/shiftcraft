#!/usr/bin/env python3
"""Analyze the schedule output to verify weekly off distribution."""

import json
from collections import defaultdict
from datetime import datetime

# Load the output
with open("output.json") as f:
    data = json.load(f)

# Analyze weekly offs per employee per week
print("=" * 80)
print("WEEKLY OFF ANALYSIS")
print("=" * 80)

employees = ["Amogha", "Suchi", "Basheer", "Anuhya", "Pavani"]
emp_week_offs = defaultdict(lambda: defaultdict(int))

for day in data["schedule"]:
    date = datetime.fromisoformat(day["date"])
    week_num = date.isocalendar()[1]

    for emp in employees:
        if day[emp] == "week_off":
            emp_week_offs[emp][week_num] += 1

print("\nWeek Off Counts per Employee per ISO Week:")
print("-" * 80)
for emp in employees:
    weeks = sorted(emp_week_offs[emp].items())
    week_str = ", ".join(f"W{w}: {c}" for w, c in weeks)
    total = sum(c for _, c in weeks)
    print(f"{emp:10s}: {week_str} | Total: {total}")

# Check if any week has issues
print("\n" + "=" * 80)
print("VALIDATION")
print("=" * 80)

issues = []
for emp in employees:
    for week, count in emp_week_offs[emp].items():
        if week in [14, 18]:  # Partial weeks
            if count < 1:
                issues.append(f"{emp} Week {week}: {count} offs (expected ≥1 for partial week)")
        else:  # Full weeks
            if count != 2:
                issues.append(f"{emp} Week {week}: {count} offs (expected exactly 2 for full week)")

if issues:
    print("\n[!] Issues found:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("\n[OK] All weekly off constraints satisfied!")

# Summary statistics
print("\n" + "=" * 80)
print("SUMMARY STATISTICS")
print("=" * 80)
for emp, stats in data["summary"].items():
    print(f"\n{emp}:")
    for shift_type, count in stats.items():
        print(f"  {shift_type:12s}: {count:2d}")

# Made with Bob
