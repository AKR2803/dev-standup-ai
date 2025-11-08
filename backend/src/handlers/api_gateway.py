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
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
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
            query_params = event.get('queryStringParameters') or {}
            pr_number = query_params.get('pr_number')
            hours = int(query_params.get('hours', 24))
            
            logger.info("Generating code review", pr_number=pr_number, hours=hours)
            
            if pr_number:
                # Review specific PR
                pr_data = await self.github_service.get_pull_request(int(pr_number))
                review = await self.ai_handler.review_pull_request(pr_data)
            else:
                # Review recent PRs
                prs = await self.github_service.get_recent_pull_requests(hours)
                reviews = []
                for pr in prs:
                    review = await self.ai_handler.review_pull_request(pr)
                    reviews.append(review)
                    await self.dynamodb_service.store_code_review(review)
                return self._create_response(200, {'reviews': [r.dict() for r in reviews]})
            
            await self.dynamodb_service.store_code_review(review)
            return self._create_response(200, review.dict())
        
        except Exception as e:
            logger.error("Failed to generate review", error=str(e))
            return self._create_response(500, {'error': str(e)})
    
    async def generate_docstring(self, event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Generate docstring for function."""
        try:
            body = json.loads(event.get('body', '{}'))
            file_path = body.get('file_path')
            function_name = body.get('function_name')
            code = body.get('code')
            
            if not all([file_path, function_name, code]):
                return self._create_response(400, {'error': 'Missing required fields'})
            
            logger.info("Generating docstring", function=function_name)
            
            docstring = await self.ai_handler.generate_docstring(file_path, function_name, code)
            return self._create_response(200, docstring.dict())
        
        except Exception as e:
            logger.error("Failed to generate docstring", error=str(e))
            return self._create_response(500, {'error': str(e)})
    
    async def generate_test(self, event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Generate unit test for function."""
        try:
            body = json.loads(event.get('body', '{}'))
            file_path = body.get('file_path')
            function_name = body.get('function_name')
            code = body.get('code')
            
            if not all([file_path, function_name, code]):
                return self._create_response(400, {'error': 'Missing required fields'})
            
            logger.info("Generating test", function=function_name)
            
            test = await self.ai_handler.generate_unit_test(file_path, function_name, code)
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