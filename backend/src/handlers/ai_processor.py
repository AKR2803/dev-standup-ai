"""AI processor handler for generating summaries and reviews."""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from ..services.github_service import GitHubService
from ..services.claude_service import ClaudeService
from ..services.dynamodb_service import DynamoDBService
from ..services.slack_service import SlackService
from ..utils.logger import get_logger

logger = get_logger(__name__)


async def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for AI processing tasks.
    
    Handles different AI operations based on the event type:
    - standup: Generate team standup summary
    - review: Review pull requests
    - docstring: Generate documentation
    - test: Generate unit tests
    """
    try:
        operation = event.get('operation', 'standup')
        logger.info("Starting AI processing", operation=operation)
        
        if operation == 'standup':
            return await generate_standup_summary(event)
        elif operation == 'review':
            return await review_pull_request(event)
        elif operation == 'docstring':
            return await generate_docstring(event)
        elif operation == 'test':
            return await generate_unit_test(event)
        else:
            return {
                'statusCode': 400,
                'body': {
                    'error': f'Unknown operation: {operation}'
                }
            }
    
    except Exception as e:
        logger.error("AI processing failed", error=str(e))
        return {
            'statusCode': 500,
            'body': {
                'error': f'AI processing failed: {str(e)}'
            }
        }


async def generate_standup_summary(event: Dict[str, Any]) -> Dict[str, Any]:
    """Generate team standup summary from recent activity."""
    try:
        # Get date range
        since_hours = event.get('since_hours', 24)
        since = datetime.utcnow() - timedelta(hours=since_hours)
        
        # Initialize services
        github_service = GitHubService()
        claude_service = ClaudeService()
        dynamodb_service = DynamoDBService()
        slack_service = SlackService()
        
        # Fetch recent activities
        activities = await github_service.aggregate_developer_activity(since)
        
        if not activities:
            return {
                'statusCode': 200,
                'body': {
                    'message': 'No activities found for standup generation'
                }
            }
        
        # Generate AI summary
        standup = await claude_service.generate_standup_summary(activities)
        
        # Store in database
        await dynamodb_service.store_team_standup(standup)
        
        # Post to Slack if requested
        post_to_slack = event.get('post_to_slack', True)
        if post_to_slack:
            await slack_service.post_standup_summary(standup)
        
        logger.info("Standup summary generated", developers=len(standup.team_items))
        
        return {
            'statusCode': 200,
            'body': {
                'message': 'Standup summary generated successfully',
                'standup': standup.dict(),
                'posted_to_slack': post_to_slack
            }
        }
    
    except Exception as e:
        logger.error("Failed to generate standup summary", error=str(e))
        return {
            'statusCode': 500,
            'body': {
                'error': f'Failed to generate standup summary: {str(e)}'
            }
        }


async def review_pull_request(event: Dict[str, Any]) -> Dict[str, Any]:
    """Review a specific pull request or recent PRs."""
    try:
        pr_number = event.get('pr_number')
        
        # Initialize services
        github_service = GitHubService()
        claude_service = ClaudeService()
        dynamodb_service = DynamoDBService()
        slack_service = SlackService()
        
        if pr_number:
            # Review specific PR
            reviews = await _review_single_pr(pr_number, github_service, claude_service)
        else:
            # Review recent PRs
            since_hours = event.get('since_hours', 24)
            since = datetime.utcnow() - timedelta(hours=since_hours)
            
            prs = await github_service.get_recent_pull_requests(since)
            reviews = []
            
            for pr in prs[:5]:  # Limit to 5 most recent PRs
                review = await _review_single_pr(pr.number, github_service, claude_service)
                if review:
                    reviews.append(review)
        
        # Store reviews and post to Slack
        for review in reviews:
            await dynamodb_service.store_code_review(review)
            
            post_to_slack = event.get('post_to_slack', True)
            if post_to_slack:
                await slack_service.post_pr_review(review)
        
        logger.info("PR reviews completed", count=len(reviews))
        
        return {
            'statusCode': 200,
            'body': {
                'message': f'Reviewed {len(reviews)} pull requests',
                'reviews': [review.dict() for review in reviews]
            }
        }
    
    except Exception as e:
        logger.error("Failed to review pull requests", error=str(e))
        return {
            'statusCode': 500,
            'body': {
                'error': f'Failed to review pull requests: {str(e)}'
            }
        }


async def _review_single_pr(pr_number: int, github_service: GitHubService, claude_service: ClaudeService) -> Optional[Any]:
    """Review a single pull request."""
    try:
        # Get PR details and diff
        prs = await github_service.get_recent_pull_requests(datetime.utcnow() - timedelta(days=7))
        pr = next((p for p in prs if p.number == pr_number), None)
        
        if not pr:
            logger.warning("PR not found", pr_number=pr_number)
            return None
        
        diff_content = await github_service.get_pr_diff(pr_number)
        if not diff_content:
            logger.warning("Could not fetch PR diff", pr_number=pr_number)
            return None
        
        # Generate AI review
        review = await claude_service.review_pull_request(pr_number, pr.title, diff_content)
        return review
    
    except Exception as e:
        logger.error("Failed to review single PR", pr_number=pr_number, error=str(e))
        return None


async def generate_docstring(event: Dict[str, Any]) -> Dict[str, Any]:
    """Generate docstring for specified code."""
    try:
        file_path = event.get('file_path')
        function_name = event.get('function_name')
        code = event.get('code')
        
        if not all([file_path, function_name, code]):
            return {
                'statusCode': 400,
                'body': {
                    'error': 'Missing required parameters: file_path, function_name, code'
                }
            }
        
        # Initialize services
        claude_service = ClaudeService()
        dynamodb_service = DynamoDBService()
        
        # Generate docstring
        docstring_gen = await claude_service.generate_docstring(file_path, function_name, code)
        
        # Store in database
        await dynamodb_service.store_ai_generation('docstring', docstring_gen.dict())
        
        logger.info("Docstring generated", function=function_name)
        
        return {
            'statusCode': 200,
            'body': {
                'message': 'Docstring generated successfully',
                'docstring': docstring_gen.dict()
            }
        }
    
    except Exception as e:
        logger.error("Failed to generate docstring", error=str(e))
        return {
            'statusCode': 500,
            'body': {
                'error': f'Failed to generate docstring: {str(e)}'
            }
        }


async def generate_unit_test(event: Dict[str, Any]) -> Dict[str, Any]:
    """Generate unit test for specified code."""
    try:
        file_path = event.get('file_path')
        function_name = event.get('function_name')
        code = event.get('code')
        
        if not all([file_path, function_name, code]):
            return {
                'statusCode': 400,
                'body': {
                    'error': 'Missing required parameters: file_path, function_name, code'
                }
            }
        
        # Initialize services
        claude_service = ClaudeService()
        dynamodb_service = DynamoDBService()
        
        # Generate unit test
        test_gen = await claude_service.generate_unit_test(file_path, function_name, code)
        
        # Store in database
        await dynamodb_service.store_ai_generation('test', test_gen.dict())
        
        logger.info("Unit test generated", function=function_name)
        
        return {
            'statusCode': 200,
            'body': {
                'message': 'Unit test generated successfully',
                'test': test_gen.dict()
            }
        }
    
    except Exception as e:
        logger.error("Failed to generate unit test", error=str(e))
        return {
            'statusCode': 500,
            'body': {
                'error': f'Failed to generate unit test: {str(e)}'
            }
        }