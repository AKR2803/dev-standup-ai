"""Data models for standup summaries."""
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


class StandupItem(BaseModel):
    """Individual standup item for a developer."""
    developer: str
    yesterday: List[str] = []
    today: List[str] = []
    blockers: List[str] = []
    mood: Optional[str] = None


class TeamStandup(BaseModel):
    """Complete team standup summary."""
    date: datetime
    team_items: List[StandupItem]
    summary: Optional[str] = None
    key_highlights: List[str] = []
    team_blockers: List[str] = []
    
    @property
    def total_developers(self) -> int:
        return len(self.team_items)
    
    @property
    def developers_with_blockers(self) -> int:
        return len([item for item in self.team_items if item.blockers])