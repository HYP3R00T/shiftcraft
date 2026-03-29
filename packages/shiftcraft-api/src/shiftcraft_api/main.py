"""FastAPI application entry point."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from shiftcraft_core import solve

app = FastAPI(
    title="shiftcraft-api",
    description="Constraint-driven workforce scheduling API",
    version="0.1.0",
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


@app.post("/schedule")
def schedule(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Generate a schedule from the given input payload.

    Accepts the same JSON structure as shiftcraft-core's solve() function.
    """
    try:
        return solve(payload)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
