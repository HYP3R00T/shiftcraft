"""
Run the shiftcraft-core solver against the example input.

Reads settings.json (rules of the game) and input.json (this run's data),
merges them into the API payload, solves, and writes output.json.
"""

import json
from pathlib import Path

from shiftcraft_core import solve

BASE_DIR = Path(__file__).resolve().parent
SETTINGS_PATH = BASE_DIR / "settings.json"
INPUT_PATH = BASE_DIR / "input.json"
OUTPUT_PATH = BASE_DIR / "output.json"


def main() -> None:
    settings = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    inp = json.loads(INPUT_PATH.read_text(encoding="utf-8"))

    payload = {"settings": settings, "input": inp}

    print("Solving April 2026 schedule for 5-person team…")
    result = solve(payload)

    OUTPUT_PATH.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Status  : {result['status']}")
    print(f"Objective: {result['metadata'].get('objective')}")
    print(f"Solve time: {result['metadata']['solve_time_seconds']}s")
    print(f"Output written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
