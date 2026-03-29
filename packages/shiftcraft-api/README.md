# shiftcraft-api

FastAPI wrapper around [shiftcraft-core](../shiftcraft-core).

## Run locally

```sh
uv run uvicorn shiftcraft_api.main:app --reload
```

API docs available at `http://localhost:8000/docs`.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/schedule` | Generate a schedule |

The `/schedule` endpoint accepts the same JSON payload as `shiftcraft-core`'s `solve()` function.
See [shiftcraft-core input docs](../../docs/packages/shiftcraft-core/input.md) for the schema.
