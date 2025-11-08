"""Tests for GitHub service."""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from src.services.github_service import GitHubService
from src.models.activity import GitHubCommit, GitHubPullRequest, GitHubIssue


@pytest.fixture
def github_service():
    """Create GitHub service instance for testing."""
    return GitHubService()


@pytest.fixture
def mock_commit_data():
    """Mock GitHub commit API response."""
    return {
        "sha": "abc123",
        "commit": {
            "message": "Fix bug in authentication",
            "author": {
                "name": "John Doe",
                "date": "2023-11-07T10:00:00Z"
            }
        },
        "html_url": "https://github.com/owner/repo/commit/abc123"
    }


@pytest.fixture
def mock_pr_data():
    """Mock GitHub PR API response."""
    return {
        "number": 42,
        "title": "Add new feature",
        "body": "This PR adds a new feature",
        "user": {"login": "jane_doe"},
        "state": "open",
        "created_at": "2023-11-07T09:00:00Z",
        "updated_at": "2023-11-07T10:30:00Z",
        "html_url": "https://github.com/owner/repo/pull/42",
        "diff_url": "https://github.com/owner/repo/pull/42.diff",
        "additions": 50,
        "deletions": 10
    }


class TestGitHubService:
    """Test cases for GitHubService."""
    
    @patch('src.services.github_service.requests.get')
    async def test_get_recent_commits_success(self, mock_get, github_service, mock_commit_data):
        """Test successful commit fetching."""
        # Mock API response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = [mock_commit_data]
        mock_get.return_value = mock_response
        
        # Mock _get_commit_files method
        github_service._get_commit_files = AsyncMock(return_value=['file1.py', 'file2.py'])
        
        since = datetime.utcnow() - timedelta(hours=24)
        commits = await github_service.get_recent_commits(since)
        
        assert len(commits) == 1
        assert isinstance(commits[0], GitHubCommit)
        assert commits[0].sha == "abc123"
        assert commits[0].message == "Fix bug in authentication"
        assert commits[0].author == "John Doe"
        assert commits[0].files_changed == ['file1.py', 'file2.py']
    
    @patch('src.services.github_service.requests.get')
    async def test_get_recent_commits_api_error(self, mock_get, github_service):
        """Test commit fetching with API error."""
        mock_get.side_effect = Exception("API Error")
        
        since = datetime.utcnow() - timedelta(hours=24)
        commits = await github_service.get_recent_commits(since)
        
        assert commits == []
    
    @patch('src.services.github_service.requests.get')
    async def test_get_recent_pull_requests_success(self, mock_get, github_service, mock_pr_data):
        """Test successful PR fetching."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = [mock_pr_data]
        mock_get.return_value = mock_response
        
        since = datetime.utcnow() - timedelta(hours=24)
        prs = await github_service.get_recent_pull_requests(since)
        
        assert len(prs) == 1
        assert isinstance(prs[0], GitHubPullRequest)
        assert prs[0].number == 42
        assert prs[0].title == "Add new feature"
        assert prs[0].author == "jane_doe"
        assert prs[0].state == "open"
    
    @patch('src.services.github_service.requests.get')
    async def test_get_pr_diff_success(self, mock_get, github_service):
        """Test successful PR diff fetching."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = "diff --git a/file.py b/file.py\n+added line"
        mock_get.return_value = mock_response
        
        diff = await github_service.get_pr_diff(42)
        
        assert diff == "diff --git a/file.py b/file.py\n+added line"
    
    @patch('src.services.github_service.requests.get')
    async def test_get_pr_diff_error(self, mock_get, github_service):
        """Test PR diff fetching with error."""
        mock_get.side_effect = Exception("API Error")
        
        diff = await github_service.get_pr_diff(42)
        
        assert diff is None
    
    async def test_aggregate_developer_activity(self, github_service):
        """Test developer activity aggregation."""
        # Mock the individual methods
        github_service.get_recent_commits = AsyncMock(return_value=[
            GitHubCommit(
                sha="abc123",
                message="Test commit",
                author="John Doe",
                timestamp=datetime.utcnow(),
                url="https://github.com/test",
                files_changed=[]
            )
        ])
        
        github_service.get_recent_pull_requests = AsyncMock(return_value=[
            GitHubPullRequest(
                number=1,
                title="Test PR",
                author="John Doe",
                state="open",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                url="https://github.com/test",
                diff_url="https://github.com/test.diff"
            )
        ])
        
        github_service.get_recent_issues = AsyncMock(return_value=[])
        
        since = datetime.utcnow() - timedelta(hours=24)
        activities = await github_service.aggregate_developer_activity(since)
        
        assert len(activities) == 1
        assert activities[0].developer == "John Doe"
        assert activities[0].total_commits == 1
        assert activities[0].total_prs == 1
        assert activities[0].total_issues == 0