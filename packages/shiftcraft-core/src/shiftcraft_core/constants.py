"""Configuration constants and parameters for shiftcraft-core."""

from __future__ import annotations

# ── Shift and time definitions ────────────────────────────────────────────────

SHIFTS = ("morning", "afternoon", "night", "regular")
"""All possible shift types."""

CORE_SHIFTS = ("morning", "afternoon", "night")
"""Core shifts (excludes 'regular' which is assigned last)."""

DAYS_OF_WEEK = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
"""Days of the week in order."""

# ── Hard constraint parameters ────────────────────────────────────────────────

MAX_SHIFTS_PER_PERSON_PER_DAY = 1
"""Maximum number of shifts one person can work in a single day."""

MAX_CONSECUTIVE_WORK_DAYS = 6
"""Maximum number of consecutive working days allowed."""

WEEKLY_OFF_DAYS = 2
"""Required number of off days per calendar week."""

MAX_WORKING_EMPLOYEES_PER_DAY = 4
"""Maximum number of employees who can work on any given day."""

COMP_OFF_VALIDITY_DAYS = 90
"""Number of days a compensatory off remains valid before expiring."""

DISALLOWED_TRANSITIONS = {("night", "morning")}
"""Set of (shift_from, shift_to) tuples that are not allowed on consecutive days."""

# ── Solver configuration ──────────────────────────────────────────────────────

SOLVER_TIME_LIMIT_SECONDS = 30
"""Maximum time (in seconds) the solver will run before timing out."""

# ── Soft constraint weights ───────────────────────────────────────────────────
# Higher weight = more important to satisfy

W_SHIFT_BALANCE = 10
"""Weight for even distribution of morning/afternoon/night shifts."""

W_HISTORY_BIAS = 5
"""Weight for biasing toward employees who worked a shift less last month."""

W_SHIFT_BLOCK = 8
"""Weight for preferring contiguous shift blocks (penalize fragmentation)."""

W_OFF_BALANCE = 6
"""Weight for even distribution of weekend offs across employees."""

W_OFF_CONTIGUOUS = 4
"""Weight for preferring paired Saturday+Sunday offs."""

W_TARGET_COVERAGE = 3
"""Weight for preferring target headcount over just minimum."""

W_UNTYPED_LEAVE = 7
"""Weight for honoring untyped leave date preferences."""

# Made with Bob
