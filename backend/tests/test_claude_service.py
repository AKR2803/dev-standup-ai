"""Tests for Claude service."""
import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from src.services.claude_service import ClaudeService
from src.models.activity import DeveloperActivity, GitHubCommit
from src.models.standup import TeamStandup, StandupItem
from src.models.review import CodeReview, ReviewSeverity


@pytest.fixture
def claude_service():
    """Create Claude service instance for testing."""
    return ClaudeService()


@pytest.fixture
def mock_developer_activity():
    """Mock developer activity data."""
    return DeveloperActivity(
        developer="John Doe",
        date=datetime.utcnow(),
        commits=[
            GitHubCommit(
                sha="abc123",
                message="Fix authentication bug",
                author="John Doe",
                timestamp=datetime.utcnow(),
                url="https://github.com/test",
                files_changed=["auth.py"]
            )
        ],
        pull_requests=[],
        issues=[]
    )


class TestClaudeService:
    """Test cases for ClaudeService."""
    
    @patch('src.services.claude_service.Anthropic')
    async def test_generate_standup_summary_success(self, mock_anthropic, claude_service, mock_developer_activity):
        """Test successful standup summary generation."""
        # Mock Claude API response
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = json.dumps({
            "team_items": [
                {
                    "developer": "John Doe",
                    "yesterday": ["Fixed authentication bug"],
                    "today": ["Working on new feature"],
                    "blockers": []
                }
            ],
            "summary": "Team made good progress",
            "key_highlights": ["Authentication fix deployed"],
            "team_blockers": []
        })
        
        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client
        
        # Override the client
        claude_service.client = mock_client
        
        activities = [mock_developer_activity]
        standup = await claude_service.generate_standup_summary(activities)
        
        assert isinstance(standup, TeamStandup)
        assert len(standup.team_items) == 1
        assert standup.team_items[0].developer == "John Doe"
        assert "Fixed authentication bug" in standup.team_items[0].yesterday
        assert standup.summary == "Team made good progress"
    
    @patch('src.services.claude_service.Anthropic')
    async def test_generate_standup_summary_api_error(self, mock_anthropic, claude_service, mock_developer_activity):
        """Test standup generation with API error."""
        mock_client = Mock()
        mock_client.messages.create.side_effect = Exception("API Error")
        mock_anthropic.return_value = mock_client
        
        claude_service.client = mock_client
        
        activities = [mock_developer_activity]
        standup = await claude_service.generate_standup_summary(activities)
        
        assert isinstance(standup, TeamStandup)
        assert len(standup.team_items) == 0
        assert standup.summary == "Failed to generate summary"
    
    @patch('src.services.claude_service.Anthropic')
    async def test_review_pull_request_success(self, mock_anthropic, claude_service):
        """Test successful PR review generation."""
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = json.dumps({
            "summary": "Good changes with minor issues",
            "overall_score": 8,
            "findings": [
                {
                    "file_path": "auth.py",
                    "line_number": 42,
                    "severity": "medium",
                    "category": "logic",
                    "message": "Consider null check",
                    "suggestion": "Add null validation",
                    "code_snippet": "user.name"
                }
            ],
            "suggestions": ["Add more tests"],
            "approved": False
        })
        
        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client
        
        claude_service.client = mock_client
        
        review = await claude_service.review_pull_request(42, "Test PR", "diff content")
        
        assert isinstance(review, CodeReview)
        assert review.pr_number == 42
        assert review.pr_title == "Test PR"
        assert review.overall_score == 8
        assert len(review.findings) == 1
        assert review.findings[0].severity == ReviewSeverity.MEDIUM
        assert review.findings[0].file_path == "auth.py"
    
    @patch('src.services.claude_service.Anthropic')
    async def test_generate_docstring_success(self, mock_anthropic, claude_service):
        """Test successful docstring generation."""
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = '''Calculate the sum of two numbers.
        
        Args:
            a (int): First number
            b (int): Second number
            
        Returns:
            int: Sum of a and b
        '''
        
        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client
        
        claude_service.client = mock_client
        
        result = await claude_service.generate_docstring(
            "math.py", 
            "add_numbers", 
            "def add_numbers(a, b):\n    return a + b"
        )
        
        assert result.file_path == "math.py"
        assert result.function_name == "add_numbers"
        assert "Calculate the sum" in result.generated_docstring
        assert result.style == "google"
    
    @patch('src.services.claude_service.Anthropic')
    async def test_generate_unit_test_success(self, mock_anthropic, claude_service):
        """Test successful unit test generation."""
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = '''import pytest
from math import add_numbers

def test_add_numbers():
    assert add_numbers(2, 3) == 5
    assert add_numbers(0, 0) == 0
    assert add_numbers(-1, 1) == 0
'''
        
        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client
        
        claude_service.client = mock_client
        
        result = await claude_service.generate_unit_test(
            "math.py",
            "add_numbers",
            "def add_numbers(a, b):\n    return a + b"
        )
        
        assert result.file_path == "math.py"
        assert result.function_name == "add_numbers"
        assert "test_add_numbers" in result.generated_test
        assert result.test_framework == "pytest"
        assert result.coverage_estimate == 85