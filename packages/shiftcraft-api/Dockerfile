FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Copy workspace config and both packages needed
COPY pyproject.toml uv.lock ./
COPY packages/shiftcraft-core ./packages/shiftcraft-core
COPY packages/shiftcraft-api ./packages/shiftcraft-api

# Install only shiftcraft-api and its dependencies (no dev deps)
RUN uv sync --package shiftcraft-api --no-dev --frozen

EXPOSE 8000

CMD ["uv", "run", "--no-dev", "uvicorn", "shiftcraft_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
