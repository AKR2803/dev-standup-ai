"""Activity aggregator handler for fetching and storing GitHub activity."""
from datetime import datetime, timedelta
from typing import Dict, Any, List
from ..services.github_service import GitHubService
from ..services.dynamodb_service import DynamoDBService
from ..models.activity import DeveloperActivity
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ActivityAggregatorHandler:
    """Handler for aggregating GitHub activity."""
    
    def __init__(self):
        self.github_service = GitHubService()
        self.dynamodb_service = DynamoDBService()
    
    async def aggregate_activity(self, since_hours: int = 24) -> List[DeveloperActivity]:
        """Aggregate developer activity from GitHub."""
        try:
            logger.info("Aggregating activity", since_hours=since_hours)
            
            activities = await self.github_service.aggregate_developer_activity(since_hours)
            
            # Store activities in DynamoDB
            for activity in activities:
                await self.dynamodb_service.store_developer_activity(activity)
            
            logger.info("Activity aggregation completed", count=len(activities))
            return activities
        
        except Exception as e:
            logger.error("Failed to aggregate activity", error=str(e))
            raise