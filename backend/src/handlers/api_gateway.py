"""Lambda handlers for API Gateway endpoints."""
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from ..handlers.activity_aggregator import ActivityAggregatorHandler
from ..handlers.ai_processor import AIProcessorHandler
from ..handlers.slack_integration import SlackIntegrationHandler
from ..services.dynamodb_service import DynamoDBService
from ..services.github_service import GitHubService
from ..utils.config import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)


class APIGatewayHandler:
    """Handler class for API Gateway Lambda functions."""
    
    def __init__(self):
        self.dynamodb_service = DynamoDBService()
        self.github_service = GitHubService()
        self.activity_handler = ActivityAggregatorHandler()
        self.ai_handler = AIProcessorHandler()
        self.slack_handler = SlackIntegrationHandler()
    
    def _create_response(self, status_code: int, body: Any, headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Create standardized Lambda response."""
        default_headers = {
            'Content-Type': 'application/json'
        }
        if headers:
            default_headers.update(headers)
        
        return {
            'statusCode': status_code,
            'headers': default_headers,
            'body': json.dumps(body) if isinstance(body, (dict, list)) else body
        }
    

    
    async def get_standup(self, event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Get latest standup summary."""
        try:
            logger.info("Getting standup summary")
            standup = await self.dynamodb_service.get_latest_standup()
            
            if standup:
                return self._create_response(200, standup.dict())
            else:
                return self._create_response(404, {'error': 'No standup found'})
        
        except Exception as e:
            logger.error("Failed to get standup", error=str(e))
            return self._create_response(500, {'error': str(e)})
    
    async def generate_standup(self, event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Generate new standup summary."""
        try:
            from datetime import timedelta, timezone
            
            query_params = event.get('queryStringParameters') or {}
            hours = int(query_params.get('hours', 24))
            
            logger.info("Generating standup", hours=hours)
            
            # Aggregate activity first
            activities = await self.github_service.aggregate_developer_activity(hours)
            
            # Generate AI summary
            standup = await self.ai_handler.generate_standup_summary(activities)
            
            # Store in DynamoDB
            await self.dynamodb_service.store_team_standup(standup)
            
            return self._create_response(200, standup.dict())
        
        except Exception as e:
            logger.error("Failed to generate standup", error=str(e))
            return self._create_response(500, {'error': str(e)})
    
    async def generate_code_review(self, event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Generate code review for PR."""
        try:
            from datetime import timedelta, timezone
            
            query_params = event.get('queryStringParameters') or {}
            pr_number = query_params.get('pr_number')
            hours = int(query_params.get('hours', 24))
            since = datetime.now(timezone.utc) - timedelta(hours=hours)
            
            logger.info("Generating code review", pr_number=pr_number, hours=hours)
            
            if pr_number:
                # Review specific PR
                pr_data = await self.github_service.get_pull_request(int(pr_number))
                if not pr_data:
                    return self._create_response(404, {'error': f'PR #{pr_number} not found in repository'})
                
                review = await self.ai_handler.review_pull_request(pr_data)
                return self._create_response(200, review.dict())
            else:
                # Review recent PRs
                prs = await self.github_service.get_recent_pull_requests(since)
                if not prs:
                    return self._create_response(200, {
                        'reviews': [],
                        'message': f'No pull requests found in the last {hours} hours'
                    })
                
                reviews = []
                for pr in prs:
                    try:
                        review = await self.ai_handler.review_pull_request(pr)
                        reviews.append(review)
                    except Exception as pr_error:
                        logger.error("Failed to review individual PR", pr_number=pr.number, error=str(pr_error))
                        continue
                
                return self._create_response(200, {
                    'reviews': [r.dict() for r in reviews],
                    'message': f'Generated {len(reviews)} reviews from {len(prs)} PRs'
                })
        
        except Exception as e:
            logger.error("Failed to generate review", error=str(e))
            return self._create_response(500, {'error': str(e)})
    
    async def generate_docstring(self, event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Generate docstrings for entire file."""
        try:
            body = json.loads(event.get('body', '{}'))
            file_path = body.get('file_path')
            branch = body.get('branch', 'main')
            
            if not file_path:
                return self._create_response(400, {'error': 'Missing file_path'})
            
            logger.info("Generating docstrings for file", file=file_path)
            
            # Fetch file content from GitHub
            file_content = await self.github_service.get_file_content(file_path, branch)
            if not file_content:
                return self._create_response(404, {'error': 'File not found in repository'})
            
            docstring = await self.ai_handler.generate_docstring(file_path, "entire_file", file_content)
            return self._create_response(200, docstring.dict())
        
        except Exception as e:
            logger.error("Failed to generate docstring", error=str(e))
            return self._create_response(500, {'error': str(e)})
    
    async def generate_test(self, event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Generate unit tests for entire file."""
        try:
            body = json.loads(event.get('body', '{}'))
            file_path = body.get('file_path')
            branch = body.get('branch', 'main')
            
            if not file_path:
                return self._create_response(400, {'error': 'Missing file_path'})
            
            logger.info("Generating tests for file", file=file_path)
            
            # Fetch file content from GitHub
            file_content = await self.github_service.get_file_content(file_path, branch)
            if not file_content:
                return self._create_response(404, {'error': 'File not found in repository'})
            
            test = await self.ai_handler.generate_unit_test(file_path, "entire_file", file_content)
            return self._create_response(200, test.dict())
        
        except Exception as e:
            logger.error("Failed to generate test", error=str(e))
            return self._create_response(500, {'error': str(e)})

    
    async def aggregate_activity(self, event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Aggregate GitHub activity."""
        try:
            query_params = event.get('queryStringParameters') or {}
            hours = int(query_params.get('hours', 24))
            
            logger.info("Aggregating activity", hours=hours)
            
            activities = await self.github_service.aggregate_developer_activity(hours)
            
            # Store activities in DynamoDB
            await self.dynamodb_service.store_developer_activities(activities)
            
            return self._create_response(200, {
                'message': f'Aggregated {len(activities)} developer activities',
                'count': len(activities)
            })
        
        except Exception as e:
            logger.error("Failed to aggregate activity", error=str(e))
            return self._create_response(500, {'error': str(e)})