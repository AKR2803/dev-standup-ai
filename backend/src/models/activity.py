"""Data models for developer activity."""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class GitHubCommit(BaseModel):
    """Model for GitHub commit data."""
    sha: str
    message: str
    author: str
    timestamp: datetime
    url: str
    files_changed: List[str] = []


class GitHubPullRequest(BaseModel):
    """Model for GitHub pull request data."""
    number: int
    title: str
    body: Optional[str] = None
    author: str
    state: str
    created_at: datetime
    updated_at: datetime
    url: str
    diff_url: str
    files_changed: List[str] = []
    additions: int = 0
    deletions: int = 0


class GitHubIssue(BaseModel):
    """Model for GitHub issue data."""
    number: int
    title: str
    body: Optional[str] = None
    author: str
    state: str
    created_at: datetime
    updated_at: datetime
    url: str
    labels: List[str] = []


class DeveloperActivity(BaseModel):
    """Aggregated activity for a developer."""
    developer: str
    date: datetime
    commits: List[GitHubCommit] = []
    pull_requests: List[GitHubPullRequest] = []
    issues: List[GitHubIssue] = []
    comments: List[Dict[str, Any]] = []
    
    @property
    def total_commits(self) -> int:
        return len(self.commits)
    
    @property
    def total_prs(self) -> int:
        return len(self.pull_requests)
    
    @property
    def total_issues(self) -> int:
        return len(self.issues)