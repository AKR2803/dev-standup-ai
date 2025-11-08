"""DynamoDB service for data persistence."""
import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from ..models.activity import DeveloperActivity
from ..models.standup import TeamStandup
from ..models.review import CodeReview, DocstringGeneration, TestGeneration
from ..utils.config import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DynamoDBService:
    """Service for DynamoDB operations."""
    
    def __init__(self):
        # Configure DynamoDB resource based on environment
        if settings.dynamodb_endpoint:
            # Local development with custom endpoint
            self.dynamodb = boto3.resource(
                'dynamodb',
                endpoint_url=settings.dynamodb_endpoint,
                region_name=settings.dynamodb_region,
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key
            )
        else:
            # AWS Lambda environment - use default credentials and region
            self.dynamodb = boto3.resource(
                'dynamodb',
                region_name=settings.dynamodb_region
            )
        
        # Don't create tables in Lambda - they should already exist
        if settings.dynamodb_endpoint:
            self._ensure_tables()
    
    def _ensure_tables(self):
        """Ensure required DynamoDB tables exist."""
        # Use serverless.yml table names with stage suffix
        stage = os.getenv('STAGE', 'dev')
        tables = {
            f'devstandup-activities-{stage}': {
                'KeySchema': [
                    {'AttributeName': 'developer', 'KeyType': 'HASH'},
                    {'AttributeName': 'date', 'KeyType': 'RANGE'}
                ],
                'AttributeDefinitions': [
                    {'AttributeName': 'developer', 'AttributeType': 'S'},
                    {'AttributeName': 'date', 'AttributeType': 'S'}
                ]
            },
            f'devstandup-standups-{stage}': {
                'KeySchema': [
                    {'AttributeName': 'id', 'KeyType': 'HASH'}
                ],
                'AttributeDefinitions': [
                    {'AttributeName': 'id', 'AttributeType': 'S'}
                ]
            },
            f'devstandup-reviews-{stage}': {
                'KeySchema': [
                    {'AttributeName': 'pr_number', 'KeyType': 'HASH'}
                ],
                'AttributeDefinitions': [
                    {'AttributeName': 'pr_number', 'AttributeType': 'N'}
                ]
            }
        }
        
        existing_tables = [table.name for table in self.dynamodb.tables.all()]
        
        for table_name, schema in tables.items():
            if table_name not in existing_tables:
                try:
                    table = self.dynamodb.create_table(
                        TableName=table_name,
                        KeySchema=schema['KeySchema'],
                        AttributeDefinitions=schema['AttributeDefinitions'],
                        BillingMode='PAY_PER_REQUEST'
                    )
                    table.wait_until_exists()
                    logger.info("Created DynamoDB table", table_name=table_name)
                except ClientError as e:
                    logger.error("Failed to create table", table_name=table_name, error=str(e))
    
    async def store_developer_activities(self, activities: List[DeveloperActivity]) -> bool:
        """Store developer activities in DynamoDB."""
        stage = os.getenv('STAGE', 'dev')
        table = self.dynamodb.Table(f'devstandup-activities-{stage}')
        
        try:
            with table.batch_writer() as batch:
                for activity in activities:
                    item = {
                        'developer': activity.developer,
                        'date': activity.date.isoformat(),
                        'commits': [commit.dict() for commit in activity.commits],
                        'pull_requests': [pr.dict() for pr in activity.pull_requests],
                        'issues': [issue.dict() for issue in activity.issues],
                        'comments': activity.comments,
                        'total_commits': activity.total_commits,
                        'total_prs': activity.total_prs,
                        'total_issues': activity.total_issues,
                        'created_at': datetime.utcnow().isoformat()
                    }
                    batch.put_item(Item=item)
            
            logger.info("Stored developer activities", count=len(activities))
            return True
            
        except ClientError as e:
            logger.error("Failed to store developer activities", error=str(e))
            return False
    
    async def get_developer_activities(self, date: datetime) -> List[DeveloperActivity]:
        """Retrieve developer activities for a specific date."""
        stage = os.getenv('STAGE', 'dev')
        table = self.dynamodb.Table(f'devstandup-activities-{stage}')
        date_str = date.date().isoformat()
        
        try:
            response = table.scan(
                FilterExpression='begins_with(#date, :date)',
                ExpressionAttributeNames={'#date': 'date'},
                ExpressionAttributeValues={':date': date_str}
            )
            
            activities = []
            for item in response['Items']:
                # Convert back to models
                activity = DeveloperActivity(
                    developer=item['developer'],
                    date=datetime.fromisoformat(item['date']),
                    commits=[],  # Would need to reconstruct from stored data
                    pull_requests=[],
                    issues=[],
                    comments=item.get('comments', [])
                )
                activities.append(activity)
            
            logger.info("Retrieved developer activities", count=len(activities))
            return activities
            
        except ClientError as e:
            logger.error("Failed to retrieve developer activities", error=str(e))
            return []
    
    async def store_team_standup(self, standup: TeamStandup) -> bool:
        """Store team standup summary."""
        stage = os.getenv('STAGE', 'dev')
        table = self.dynamodb.Table(f'devstandup-standups-{stage}')
        
        try:
            item = {
                'id': standup.date.date().isoformat(),
                'date': standup.date.date().isoformat(),
                'team_items': [item.dict() for item in standup.team_items],
                'summary': standup.summary,
                'key_highlights': standup.key_highlights,
                'team_blockers': standup.team_blockers,
                'total_developers': standup.total_developers,
                'developers_with_blockers': standup.developers_with_blockers,
                'created_at': datetime.utcnow().isoformat()
            }
            
            table.put_item(Item=item)
            logger.info("Stored team standup", date=standup.date.date())
            return True
            
        except ClientError as e:
            logger.error("Failed to store team standup", error=str(e))
            return False
    
    async def get_latest_standup(self) -> Optional[TeamStandup]:
        """Get the most recent team standup."""
        stage = os.getenv('STAGE', 'dev')
        table = self.dynamodb.Table(f'devstandup-standups-{stage}')
        
        try:
            response = table.scan()
            items = response['Items']
            
            if not items:
                return None
            
            # Sort by date and get latest
            latest_item = max(items, key=lambda x: x['date'])
            
            # Convert back to model (simplified)
            standup = TeamStandup(
                date=datetime.fromisoformat(latest_item['date'] + 'T00:00:00'),
                team_items=[],  # Would need to reconstruct
                summary=latest_item.get('summary'),
                key_highlights=latest_item.get('key_highlights', []),
                team_blockers=latest_item.get('team_blockers', [])
            )
            
            return standup
            
        except ClientError as e:
            logger.error("Failed to retrieve latest standup", error=str(e))
            return None
    
    async def store_code_review(self, review: CodeReview) -> bool:
        """Store code review results."""
        stage = os.getenv('STAGE', 'dev')
        table = self.dynamodb.Table(f'devstandup-reviews-{stage}')
        
        try:
            item = {
                'pr_number': review.pr_number,
                'pr_title': review.pr_title,
                'reviewer': review.reviewer,
                'timestamp': review.timestamp.isoformat(),
                'summary': review.summary,
                'overall_score': review.overall_score,
                'findings': [finding.dict() for finding in review.findings],
                'suggestions': review.suggestions,
                'approved': review.approved,
                'critical_issues': review.critical_issues,
                'high_issues': review.high_issues
            }
            
            table.put_item(Item=item)
            logger.info("Stored code review", pr_number=review.pr_number)
            return True
            
        except ClientError as e:
            logger.error("Failed to store code review", error=str(e))
            return False
    
    async def get_code_review(self, pr_number: int) -> Optional[CodeReview]:
        """Retrieve code review for a specific PR."""
        stage = os.getenv('STAGE', 'dev')
        table = self.dynamodb.Table(f'devstandup-reviews-{stage}')
        
        try:
            response = table.get_item(Key={'pr_number': pr_number})
            
            if 'Item' not in response:
                return None
            
            item = response['Item']
            
            # Convert back to model (simplified)
            review = CodeReview(
                pr_number=item['pr_number'],
                pr_title=item['pr_title'],
                reviewer=item['reviewer'],
                timestamp=datetime.fromisoformat(item['timestamp']),
                summary=item['summary'],
                overall_score=item['overall_score'],
                findings=[],  # Would need to reconstruct
                suggestions=item.get('suggestions', []),
                approved=item.get('approved', False)
            )
            
            return review
            
        except ClientError as e:
            logger.error("Failed to retrieve code review", pr_number=pr_number, error=str(e))
            return None
    
    async def store_ai_generation(self, generation_type: str, content: Dict[str, Any]) -> bool:
        """Store AI-generated content (docstrings, tests, etc.)."""
        table = self.dynamodb.Table('ai_generations')
        
        try:
            item = {
                'id': f"{generation_type}_{datetime.utcnow().isoformat()}",
                'type': generation_type,
                'content': content,
                'created_at': datetime.utcnow().isoformat()
            }
            
            table.put_item(Item=item)
            logger.info("Stored AI generation", type=generation_type)
            return True
            
        except ClientError as e:
            logger.error("Failed to store AI generation", error=str(e))
            return False