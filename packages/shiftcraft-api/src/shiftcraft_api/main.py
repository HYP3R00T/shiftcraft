"""FastAPI application entry point."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from shiftcraft_core import PayloadSchema, ResultSchema, solve


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("shiftcraft-api running at http://localhost:8000", flush=True)
    print("API docs at        http://localhost:8000/docs", flush=True)
    yield


app = FastAPI(
    title="shiftcraft-api",
    description="Constraint-driven workforce scheduling API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,  # type: ignore[arg-type]
    allow_origins=["*"],  # tighten this when deploying
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    """Health check."""
    return {"status": "ok"}


@app.post("/schedule", response_model=ResultSchema)
def schedule(payload: PayloadSchema) -> dict[str, Any]:
    """
    Generate a schedule from the given input payload.

    Validates the request against the shiftcraft-core input contract and
    returns a result conforming to the output contract.
    """
    try:
        return solve(payload.model_dump())
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
