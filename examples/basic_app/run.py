import json
from pathlib import Path

from shiftcraft_core import solve

BASE_DIR = Path(__file__).resolve().parent
INPUT_PATH = BASE_DIR / "input.json"
OUTPUT_PATH = BASE_DIR / "output.json"


def main() -> None:
    payload = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    result = solve(payload)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
