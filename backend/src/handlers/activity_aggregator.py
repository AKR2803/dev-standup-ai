"""Activity aggregator handler for fetching and storing GitHub activity."""
from datetime import datetime, timedelta
from typing import Dict, Any
from ..services.github_service import GitHubService
from ..services.dynamodb_service import DynamoDBService
from ..utils.logger import get_logger

logger = get_logger(__name__)


async def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for aggregating developer activity.
    
    This function fetches recent GitHub activity and stores it in DynamoDB.
    Can be triggered by EventBridge on a schedule or invoked manually.
    """
    try:
        # Parse event parameters
        since_hours = event.get('since_hours', 24)
        since = datetime.utcnow() - timedelta(hours=since_hours)
        
        logger.info("Starting activity aggregation", since=since.isoformat())
        
        # Initialize services
        github_service = GitHubService()
        dynamodb_service = DynamoDBService()
        
        # Fetch developer activities
        activities = await github_service.aggregate_developer_activity(since)
        
        if not activities:
            logger.warning("No activities found")
            return {
                'statusCode': 200,
                'body': {
                    'message': 'No activities found',
                    'activities_count': 0
                }
            }
        
        # Store activities in DynamoDB
        success = await dynamodb_service.store_developer_activities(activities)
        
        if success:
            logger.info("Activity aggregation completed", activities_count=len(activities))
            return {
                'statusCode': 200,
                'body': {
                    'message': 'Activity aggregation completed successfully',
                    'activities_count': len(activities),
                    'developers': [activity.developer for activity in activities]
                }
            }
        else:
            logger.error("Failed to store activities")
            return {
                'statusCode': 500,
                'body': {
                    'error': 'Failed to store activities in database'
                }
            }
    
    except Exception as e:
        logger.error("Activity aggregation failed", error=str(e))
        return {
            'statusCode': 500,
            'body': {
                'error': f'Activity aggregation failed: {str(e)}'
            }
        }


async def aggregate_activity_endpoint(since_hours: int = 24) -> Dict[str, Any]:
    """
    HTTP endpoint wrapper for activity aggregation.
    Used by API Gateway to trigger aggregation on demand.
    """
    event = {'since_hours': since_hours}
    return await lambda_handler(event, None)