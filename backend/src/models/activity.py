"""Data models for developer activity."""
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class GitHubCommit:
    """Model for GitHub commit data."""
    sha: str
    message: str
    author: str
    timestamp: datetime
    url: str
    files_changed: List[str] = field(default_factory=list)
    
    def dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'sha': self.sha,
            'message': self.message,
            'author': self.author,
            'timestamp': self.timestamp.isoformat(),
            'url': self.url,
            'files_changed': self.files_changed
        }


@dataclass
class GitHubPullRequest:
    """Model for GitHub pull request data."""
    number: int
    title: str
    author: str
    state: str
    created_at: datetime
    updated_at: datetime
    url: str
    diff_url: str
    body: Optional[str] = None
    files_changed: List[str] = field(default_factory=list)
    additions: int = 0
    deletions: int = 0
    
    def dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'number': self.number,
            'title': self.title,
            'author': self.author,
            'state': self.state,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'url': self.url,
            'diff_url': self.diff_url,
            'body': self.body,
            'files_changed': self.files_changed,
            'additions': self.additions,
            'deletions': self.deletions
        }


@dataclass
class GitHubIssue:
    """Model for GitHub issue data."""
    number: int
    title: str
    author: str
    state: str
    created_at: datetime
    updated_at: datetime
    url: str
    body: Optional[str] = None
    labels: List[str] = field(default_factory=list)
    
    def dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'number': self.number,
            'title': self.title,
            'author': self.author,
            'state': self.state,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'url': self.url,
            'body': self.body,
            'labels': self.labels
        }


@dataclass
class DeveloperActivity:
    """Aggregated activity for a developer."""
    developer: str
    date: datetime
    commits: List[GitHubCommit] = field(default_factory=list)
    pull_requests: List[GitHubPullRequest] = field(default_factory=list)
    issues: List[GitHubIssue] = field(default_factory=list)
    comments: List[Dict[str, Any]] = field(default_factory=list)
    
    @property
    def total_commits(self) -> int:
        return len(self.commits)
    
    @property
    def total_prs(self) -> int:
        return len(self.pull_requests)
    
    @property
    def total_issues(self) -> int:
        return len(self.issues)
    
    def dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'developer': self.developer,
            'date': self.date.isoformat(),
            'commits': [{'sha': c.sha, 'message': c.message, 'author': c.author, 
                        'timestamp': c.timestamp.isoformat(), 'url': c.url, 
                        'files_changed': c.files_changed} for c in self.commits],
            'pull_requests': [{'number': pr.number, 'title': pr.title, 'author': pr.author,
                              'state': pr.state, 'created_at': pr.created_at.isoformat(),
                              'updated_at': pr.updated_at.isoformat(), 'url': pr.url,
                              'diff_url': pr.diff_url, 'body': pr.body,
                              'files_changed': pr.files_changed, 'additions': pr.additions,
                              'deletions': pr.deletions} for pr in self.pull_requests],
            'issues': [{'number': i.number, 'title': i.title, 'author': i.author,
                       'state': i.state, 'created_at': i.created_at.isoformat(),
                       'updated_at': i.updated_at.isoformat(), 'url': i.url,
                       'body': i.body, 'labels': i.labels} for i in self.issues],
            'comments': self.comments,
            'total_commits': self.total_commits,
            'total_prs': self.total_prs,
            'total_issues': self.total_issues
        }