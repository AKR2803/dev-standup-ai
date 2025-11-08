"""Data models for code reviews."""
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ReviewSeverity(str, Enum):
    """Severity levels for review findings."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ReviewFinding:
    """Individual code review finding."""
    file_path: str
    severity: ReviewSeverity
    category: str  # e.g., "logic", "performance", "security", "style"
    message: str
    line_number: Optional[int] = None
    suggestion: Optional[str] = None
    code_snippet: Optional[str] = None
    
    def dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'file_path': self.file_path,
            'line_number': self.line_number,
            'severity': self.severity.value,
            'category': self.category,
            'message': self.message,
            'suggestion': self.suggestion,
            'code_snippet': self.code_snippet
        }


@dataclass
class CodeReview:
    """Complete code review for a pull request."""
    pr_number: int
    pr_title: str
    timestamp: datetime
    summary: str
    overall_score: int  # 1-10 scale
    reviewer: str = "AI Assistant"
    findings: List[ReviewFinding] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    approved: bool = False
    
    @property
    def critical_issues(self) -> int:
        return len([f for f in self.findings if f.severity == ReviewSeverity.CRITICAL])
    
    @property
    def high_issues(self) -> int:
        return len([f for f in self.findings if f.severity == ReviewSeverity.HIGH])
    
    def dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'pr_number': self.pr_number,
            'pr_title': self.pr_title,
            'reviewer': self.reviewer,
            'timestamp': self.timestamp.isoformat(),
            'summary': self.summary,
            'overall_score': self.overall_score,
            'findings': [f.dict() for f in self.findings],
            'suggestions': self.suggestions,
            'approved': self.approved,
            'critical_issues': self.critical_issues,
            'high_issues': self.high_issues
        }


@dataclass
class DocstringGeneration:
    """Generated docstring for code."""
    file_path: str
    function_name: str
    original_code: str
    generated_docstring: str
    style: str = "google"  # google, numpy, sphinx
    
    def dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'file_path': self.file_path,
            'function_name': self.function_name,
            'original_code': self.original_code,
            'generated_docstring': self.generated_docstring,
            'style': self.style
        }


@dataclass
class TestGeneration:
    """Generated unit test for code."""
    file_path: str
    function_name: str
    original_code: str
    generated_test: str
    test_framework: str = "pytest"
    coverage_estimate: Optional[int] = None
    
    def dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'file_path': self.file_path,
            'function_name': self.function_name,
            'original_code': self.original_code,
            'generated_test': self.generated_test,
            'test_framework': self.test_framework,
            'coverage_estimate': self.coverage_estimate
        }