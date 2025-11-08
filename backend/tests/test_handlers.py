"""Tests for Lambda handlers."""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from src.handlers.activity_aggregator import lambda_handler as activity_handler
from src.handlers.ai_processor import lambda_handler as ai_handler
from src.handlers.slack_integration import lambda_handler as slack_handler


class TestActivityAggregatorHandler:
    """Test cases for activity aggregator handler."""
    
    @patch('src.handlers.activity_aggregator.GitHubService')
    @patch('src.handlers.activity_aggregator.DynamoDBService')
    async def test_lambda_handler_success(self, mock_dynamodb, mock_github):
        """Test successful activity aggregation."""
        # Mock services
        mock_github_instance = Mock()
        mock_github_instance.aggregate_developer_activity = AsyncMock(return_value=[
            Mock(developer="John Doe", total_commits=5)
        ])
        mock_github.return_value = mock_github_instance
        
        mock_dynamodb_instance = Mock()
        mock_dynamodb_instance.store_developer_activities = AsyncMock(return_value=True)
        mock_dynamodb.return_value = mock_dynamodb_instance
        
        event = {"since_hours": 24}
        result = await activity_handler(event, None)
        
        assert result['statusCode'] == 200
        assert result['body']['activities_count'] == 1
        assert 'John Doe' in result['body']['developers']
    
    @patch('src.handlers.activity_aggregator.GitHubService')
    @patch('src.handlers.activity_aggregator.DynamoDBService')
    async def test_lambda_handler_no_activities(self, mock_dynamodb, mock_github):
        """Test handler with no activities found."""
        mock_github_instance = Mock()
        mock_github_instance.aggregate_developer_activity = AsyncMock(return_value=[])
        mock_github.return_value = mock_github_instance
        
        event = {"since_hours": 24}
        result = await activity_handler(event, None)
        
        assert result['statusCode'] == 200
        assert result['body']['activities_count'] == 0
    
    @patch('src.handlers.activity_aggregator.GitHubService')
    async def test_lambda_handler_error(self, mock_github):
        """Test handler with service error."""
        mock_github.side_effect = Exception("Service error")
        
        event = {"since_hours": 24}
        result = await activity_handler(event, None)
        
        assert result['statusCode'] == 500
        assert 'error' in result['body']


class TestAIProcessorHandler:
    """Test cases for AI processor handler."""
    
    async def test_lambda_handler_unknown_operation(self):
        """Test handler with unknown operation."""
        event = {"operation": "unknown"}
        result = await ai_handler(event, None)
        
        assert result['statusCode'] == 400
        assert 'Unknown operation' in result['body']['error']
    
    @patch('src.handlers.ai_processor.GitHubService')
    @patch('src.handlers.ai_processor.ClaudeService')
    @patch('src.handlers.ai_processor.DynamoDBService')
    @patch('src.handlers.ai_processor.SlackService')
    async def test_generate_standup_success(self, mock_slack, mock_dynamodb, mock_claude, mock_github):
        """Test successful standup generation."""
        # Mock services
        mock_github_instance = Mock()
        mock_github_instance.aggregate_developer_activity = AsyncMock(return_value=[
            Mock(developer="John Doe")
        ])
        mock_github.return_value = mock_github_instance
        
        mock_claude_instance = Mock()
        mock_standup = Mock()
        mock_standup.dict.return_value = {"date": "2023-11-07", "team_items": []}
        mock_claude_instance.generate_standup_summary = AsyncMock(return_value=mock_standup)
        mock_claude.return_value = mock_claude_instance
        
        mock_dynamodb_instance = Mock()
        mock_dynamodb_instance.store_team_standup = AsyncMock(return_value=True)
        mock_dynamodb.return_value = mock_dynamodb_instance
        
        mock_slack_instance = Mock()
        mock_slack_instance.post_standup_summary = AsyncMock(return_value=True)
        mock_slack.return_value = mock_slack_instance
        
        event = {
            "operation": "standup",
            "since_hours": 24,
            "post_to_slack": True
        }
        
        result = await ai_handler(event, None)
        
        assert result['statusCode'] == 200
        assert 'standup' in result['body']
        assert result['body']['posted_to_slack'] is True


class TestSlackIntegrationHandler:
    """Test cases for Slack integration handler."""
    
    async def test_lambda_handler_invalid_request(self):
        """Test handler with invalid request format."""
        event = {"httpMethod": "GET"}
        result = await slack_handler(event, None)
        
        assert result['statusCode'] == 400
    
    @patch('src.handlers.slack_integration.SlackService')
    async def test_handle_slash_command(self, mock_slack):
        """Test slash command handling."""
        mock_slack_instance = Mock()
        mock_slack_instance.handle_slash_command = AsyncMock(return_value={
            "response_type": "ephemeral",
            "text": "Processing..."
        })
        mock_slack.return_value = mock_slack_instance
        
        event = {
            "httpMethod": "POST",
            "headers": {"content-type": "application/x-www-form-urlencoded"},
            "body": "command=/standup&text=&user_id=U123"
        }
        
        result = await slack_handler(event, None)
        
        assert result['statusCode'] == 200
        response_body = eval(result['body'])  # Convert string to dict
        assert response_body['text'] == "Processing..."