# Integration Tests

Integration tests verify that multiple components work correctly together with
realistic inputs and minimal mocking.

## What Integration Tests Cover

- End-to-end behavior of the full solve pipeline
- Correct output shape and valid state assignments
- Hard constraint satisfaction across a real scheduling period

## Marking Integration Tests

Apply the `integration` marker.

```python
import pytest

@pytest.mark.integration
def test_status_is_optimal_or_feasible(result):
    assert result["status"] in ("optimal", "feasible")
```

## Structure

Integration tests for `shiftcraft-core` live in `tests/test_integration.py` and use
a module-scoped fixture that runs the solver once and shares the result across all
tests in the file.

```python
@pytest.fixture(scope="module")
def result(payload) -> dict:
    return solve(payload)
```

This keeps the full solve from running once per test, which matters given solver
wall time.

## Running Integration Tests

```shell
uv run pytest -m integration
```

Or as part of the full suite:

```shell
uv run pytest --cov=shiftcraft_core --cov-report=term-missing --cov-fail-under=80
```

## Related

- [Testing Overview](index.md)
- [Optional Test Markers](optional-markers.md)
- [Unit Tests](unit-tests.md)
