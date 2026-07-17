"""
backend/main.py
FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from backend.database.mongo_client import init_db, close_db
from backend.api.walkthrough import router as walkthrough_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize MongoDB (Firebase already inits on import in jwt.py)
    print("Starting up... Connecting to MongoDB.")
    await init_db()
    yield
    # Shutdown: Close MongoDB connection
    print("Shutting down... Closing MongoDB connection.")
    await close_db()


app = FastAPI(
    title="Yatra API",
    version="0.1.0",
    description="Backend for the Yatra AI Walkthrough App",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten before production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(walkthrough_router, prefix="/api")


@app.get("/health")
async def health() -> dict:
    """Simple health check endpoint."""
    return {"status": "ok", "message": "Yatra backend is running!"}
