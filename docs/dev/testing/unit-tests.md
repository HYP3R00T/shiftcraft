# Unit Tests

Unit tests verify a single function or class in isolation. They use local,
synthetic inputs and avoid external dependencies.

## What to Unit Test

Unit tests are appropriate for:

- Pure functions with deterministic outputs
- Input validation and error handling
- Edge cases and boundary values

Unit tests are not appropriate for:

- Cross-module workflows spanning many layers
- Network calls or long-running jobs

## File Layout

Unit tests mirror the source tree. Each source module has a corresponding test file
in the same subdirectory under `tests/`.

| Source module | Test file |
|---|---|
| `engine/dispatch.py` | `tests/engine/test_dispatch.py` |
| `parser/loader.py` | `tests/parser/test_loader.py` |
| `primitives/cell.py` | `tests/primitives/test_cell.py` |
| `schema/payload.py` | `tests/schema/test_payload.py` |

## Marking Unit Tests

Apply the `unit` marker to all unit tests.

```python
import pytest

@pytest.mark.unit
def test_rejects_empty_input():
    with pytest.raises(ValueError):
        parse("")
```

## Shared Fixtures

Common builders and helpers live in `tests/conftest.py`. Import them using relative
imports from subdirectory test files.

```python
from ..conftest import make_employee, make_schedule_input, make_model, solve
```

## Synthetic Inputs

Build minimal inputs directly in the test rather than loading large fixtures.

```python
emp = make_employee("E001", balances={"comp_off": 2})
inp = make_schedule_input([emp], days=5)
```

## Error Handling Tests

Use `pytest.raises` with a `match` pattern to assert on the exception message.

```python
def test_unknown_who_type_raises():
    with pytest.raises(ValueError, match="Unknown WHO type"):
        filter_who(WhoFilter(type="unknown"), [])
```

## Related

- [Testing Overview](index.md)
- [Integration Tests](integration-tests.md)
- [Optional Test Markers](optional-markers.md)
