from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Stop(BaseModel):
    stop_id: str
    stop_name: str
    image_prompt: str
    narration_script: str
    daily_life_facts: list[str] = Field(min_length=3)
    image_url: Optional[str] = None
    generated: bool = False


class WorldState(BaseModel):
    walkthrough_id: str
    user_uid: Optional[str] = None
    place: str
    era: str
    era_summary: str
    created_at: datetime
    stops: list[Stop] = Field(min_length=3, max_length=5)


class WalkthroughSummary(BaseModel):
    place: str
    era: str
    share_slug: str
    created_at: datetime


class AgentError(Exception):
    pass


class ValidationError(Exception):
    pass