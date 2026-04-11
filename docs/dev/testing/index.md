# Testing

This section documents how tests are structured, written, and run in this repository.

## Test Types

| Type | Marker | Purpose | Runs in CI |
|---|---|---|---|
| [Unit](unit-tests.md) | `@pytest.mark.unit` | Test a single function or class in isolation | Yes |
| [Integration](integration-tests.md) | `@pytest.mark.integration` | Test multiple components together | Yes |
| [Property-based](property-tests.md) | `@pytest.mark.slow` | Verify invariants across many generated inputs | Optional |

## Running Tests

Run tests from the repository root.

| Command | What it runs |
|---|---|
| `uv run pytest --cov=shiftcraft_core --cov-report=term-missing --cov-fail-under=80` | Full test run with coverage gate used by CI |
| `uv run pytest -m unit` | Unit tests only |
| `uv run pytest -m integration` | Integration tests only |
| `mise run test` | Same as the full test run above |

## File Layout

Tests mirror the source tree. Each source file has a corresponding test file in the same subdirectory under `tests/`.

```text
packages/shiftcraft-core/tests/
  conftest.py                  # shared fixtures
  test_integration.py          # full pipeline tests
  engine/
    test_dispatch.py
    test_objective.py
    test_solver.py
    test_variables.py
  formatter/
    test_output.py
  parser/
    test_loader.py
  primitives/
    test_cell.py
    test_column.py
    test_cross_row.py
    test_matrix.py
    test_row_balance.py
    test_row_count.py
    test_row_sequence.py
  schema/
    test_payload.py
    test_result.py
  scope/
    test_filters.py
```

## Related

- [Unit Tests](unit-tests.md)
- [Integration Tests](integration-tests.md)
- [Property-Based Tests](property-tests.md)
- [Optional Test Markers](optional-markers.md)
- [Developer Setup](../setup/index.md)
