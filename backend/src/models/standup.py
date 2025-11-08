"""Data models for standup summaries."""
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class StandupItem:
    """Individual standup item for a developer."""
    developer: str
    yesterday: List[str] = field(default_factory=list)
    today: List[str] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)
    mood: Optional[str] = None
    
    def dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'developer': self.developer,
            'yesterday': self.yesterday,
            'today': self.today,
            'blockers': self.blockers,
            'mood': self.mood
        }


@dataclass
class TeamStandup:
    """Complete team standup summary."""
    date: datetime
    team_items: List[StandupItem]
    summary: Optional[str] = None
    key_highlights: List[str] = field(default_factory=list)
    team_blockers: List[str] = field(default_factory=list)
    
    @property
    def total_developers(self) -> int:
        return len(self.team_items)
    
    @property
    def developers_with_blockers(self) -> int:
        return len([item for item in self.team_items if item.blockers])
    
    def dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'date': self.date.isoformat(),
            'team_items': [item.dict() for item in self.team_items],
            'summary': self.summary,
            'key_highlights': self.key_highlights,
            'team_blockers': self.team_blockers,
            'total_developers': self.total_developers,
            'developers_with_blockers': self.developers_with_blockers
        }