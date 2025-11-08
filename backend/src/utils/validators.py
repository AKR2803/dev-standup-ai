"""Input validation utilities."""
from typing import Optional
from pydantic import BaseModel, validator
from datetime import datetime, timedelta


class DateRangeRequest(BaseModel):
    """Request model for date range queries."""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    @validator('start_date', pre=True, always=True)
    def set_default_start_date(cls, v):
        if v is None:
            return datetime.utcnow() - timedelta(days=1)
        return v
    
    @validator('end_date', pre=True, always=True)
    def set_default_end_date(cls, v):
        if v is None:
            return datetime.utcnow()
        return v
    
    @validator('end_date')
    def end_date_after_start_date(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v


class GenerateRequest(BaseModel):
    """Request model for AI generation endpoints."""
    type: str
    data: dict
    
    @validator('type')
    def validate_type(cls, v):
        allowed_types = ['standup', 'review', 'docstring', 'test']
        if v not in allowed_types:
            raise ValueError(f'type must be one of {allowed_types}')
        return v