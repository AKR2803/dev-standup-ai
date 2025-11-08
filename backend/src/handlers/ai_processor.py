"""AI processor handler for generating summaries and reviews."""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from ..services.github_service import GitHubService
from ..services.claude_service import ClaudeService
from ..services.dynamodb_service import DynamoDBService
from ..services.slack_service import SlackService
from ..models.activity import DeveloperActivity
from ..models.standup import TeamStandup
from ..models.review import CodeReview
from ..utils.logger import get_logger

logger = get_logger(__name__)


class AIProcessorHandler:
    """Handler for AI processing tasks."""
    
    def __init__(self):
        self.github_service = GitHubService()
        self.claude_service = ClaudeService()
        self.dynamodb_service = DynamoDBService()
        self.slack_service = SlackService()
    
    async def generate_standup_summary(self, activities: List[DeveloperActivity]) -> TeamStandup:
        """Generate team standup summary from activities."""
        try:
            logger.info("Generating standup summary", activities_count=len(activities))
            
            standup = await self.claude_service.generate_standup_summary(activities)
            
            # Store in database
            await self.dynamodb_service.store_team_standup(standup)
            
            logger.info("Standup summary generated", developers=len(standup.team_items))
            return standup
        
        except Exception as e:
            logger.error("Failed to generate standup summary", error=str(e))
            raise
    
    async def review_pull_request(self, pr_data: Any) -> CodeReview:
        """Review a single pull request."""
        try:
            logger.info("Reviewing pull request", pr_number=pr_data.number)
            
            # Get PR diff
            diff_content = await self.github_service.get_pr_diff(pr_data.number)
            
            # Generate AI review
            review = await self.claude_service.review_pull_request(
                pr_data.number, pr_data.title, diff_content
            )
            
            # Store in database
            await self.dynamodb_service.store_code_review(review)
            
            logger.info("PR review completed", pr_number=pr_data.number)
            return review
        
        except Exception as e:
            logger.error("Failed to review PR", pr_number=pr_data.number, error=str(e))
            raise
    
    async def generate_docstring(self, file_path: str, function_name: str, code: str):
        """Generate docstring for function."""
        try:
            logger.info("Generating docstring", function=function_name)
            
            docstring = await self.claude_service.generate_docstring(file_path, function_name, code)
            
            logger.info("Docstring generated", function=function_name)
            return docstring
        
        except Exception as e:
            logger.error("Failed to generate docstring", function=function_name, error=str(e))
            raise
    
    async def generate_unit_test(self, file_path: str, function_name: str, code: str):
        """Generate unit test for function."""
        try:
            logger.info("Generating unit test", function=function_name)
            
            test = await self.claude_service.generate_unit_test(file_path, function_name, code)
            
            logger.info("Unit test generated", function=function_name)
            return test
        
        except Exception as e:
            logger.error("Failed to generate unit test", function=function_name, error=str(e))
            raise