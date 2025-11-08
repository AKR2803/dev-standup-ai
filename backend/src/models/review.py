"""Data models for code reviews."""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class ReviewSeverity(str, Enum):
    """Severity levels for review findings."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ReviewFinding(BaseModel):
    """Individual code review finding."""
    file_path: str
    line_number: Optional[int] = None
    severity: ReviewSeverity
    category: str  # e.g., "logic", "performance", "security", "style"
    message: str
    suggestion: Optional[str] = None
    code_snippet: Optional[str] = None


class CodeReview(BaseModel):
    """Complete code review for a pull request."""
    pr_number: int
    pr_title: str
    reviewer: str = "AI Assistant"
    timestamp: datetime
    summary: str
    overall_score: int  # 1-10 scale
    findings: List[ReviewFinding] = []
    suggestions: List[str] = []
    approved: bool = False
    
    @property
    def critical_issues(self) -> int:
        return len([f for f in self.findings if f.severity == ReviewSeverity.CRITICAL])
    
    @property
    def high_issues(self) -> int:
        return len([f for f in self.findings if f.severity == ReviewSeverity.HIGH])


class DocstringGeneration(BaseModel):
    """Generated docstring for code."""
    file_path: str
    function_name: str
    original_code: str
    generated_docstring: str
    style: str = "google"  # google, numpy, sphinx


class TestGeneration(BaseModel):
    """Generated unit test for code."""
    file_path: str
    function_name: str
    original_code: str
    generated_test: str
    test_framework: str = "pytest"
    coverage_estimate: Optional[int] = None