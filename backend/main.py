"""
backend/main.py
FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.walkthrough import router as walkthrough_router

app = FastAPI(title="Yatra API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten before production
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(walkthrough_router, prefix="/api")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
