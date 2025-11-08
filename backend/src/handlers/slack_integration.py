"""Slack integration handler for slash commands and webhooks."""
import json
from typing import Dict, Any
from urllib.parse import parse_qs
from ..services.slack_service import SlackService
from ..services.dynamodb_service import DynamoDBService
from ..handlers.ai_processor import generate_standup_summary, review_pull_request
from ..utils.logger import get_logger

logger = get_logger(__name__)


async def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for Slack integration.
    
    Handles Slack slash commands and interactive components.
    """
    try:
        # Parse the request
        if event.get('httpMethod') == 'POST':
            body = event.get('body', '')
            
            # Handle URL-encoded form data from Slack
            if event.get('headers', {}).get('content-type') == 'application/x-www-form-urlencoded':
                parsed_body = parse_qs(body)
                slack_data = {key: value[0] if isinstance(value, list) else value 
                             for key, value in parsed_body.items()}
            else:
                slack_data = json.loads(body) if body else {}
            
            # Handle slash commands
            if 'command' in slack_data:
                return await handle_slash_command(slack_data)
            
            # Handle interactive components (buttons, etc.)
            elif 'payload' in slack_data:
                payload = json.loads(slack_data['payload'])
                return await handle_interactive_component(payload)
        
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid request format'})
        }
    
    except Exception as e:
        logger.error("Slack integration failed", error=str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }


async def handle_slash_command(slack_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Slack slash commands."""
    try:
        command = slack_data.get('command')
        text = slack_data.get('text', '')
        user_id = slack_data.get('user_id')
        
        logger.info("Handling slash command", command=command, user_id=user_id)
        
        slack_service = SlackService()
        
        # Get immediate response for user
        response = await slack_service.handle_slash_command(command, text, user_id)
        
        # Trigger background processing
        if command == '/standup':
            # Trigger standup generation asynchronously
            await _trigger_standup_generation()
        elif command == '/review':
            # Trigger PR review asynchronously
            await _trigger_pr_review(text)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(response)
        }
    
    except Exception as e:
        logger.error("Failed to handle slash command", error=str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({
                'response_type': 'ephemeral',
                'text': f'Error processing command: {str(e)}'
            })
        }


async def handle_interactive_component(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Slack interactive components (buttons, menus, etc.)."""
    try:
        action_type = payload.get('type')
        user = payload.get('user', {})
        
        logger.info("Handling interactive component", type=action_type, user_id=user.get('id'))
        
        if action_type == 'block_actions':
            actions = payload.get('actions', [])
            
            for action in actions:
                action_id = action.get('action_id')
                
                if action_id == 'generate_standup':
                    await _trigger_standup_generation()
                elif action_id == 'review_prs':
                    await _trigger_pr_review()
                elif action_id.startswith('review_pr_'):
                    pr_number = int(action_id.split('_')[-1])
                    await _trigger_pr_review(str(pr_number))
        
        return {
            'statusCode': 200,
            'body': json.dumps({'text': 'Processing your request...'})
        }
    
    except Exception as e:
        logger.error("Failed to handle interactive component", error=str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'text': f'Error: {str(e)}'})
        }


async def _trigger_standup_generation():
    """Trigger asynchronous standup generation."""
    try:
        event = {
            'operation': 'standup',
            'since_hours': 24,
            'post_to_slack': True
        }
        
        # In a real AWS environment, this would invoke another Lambda
        # For local development, we call directly
        result = await generate_standup_summary(event)
        logger.info("Standup generation triggered", result=result.get('statusCode'))
        
    except Exception as e:
        logger.error("Failed to trigger standup generation", error=str(e))


async def _trigger_pr_review(pr_text: str = None):
    """Trigger asynchronous PR review."""
    try:
        event = {
            'operation': 'review',
            'since_hours': 24,
            'post_to_slack': True
        }
        
        # If specific PR number provided
        if pr_text and pr_text.isdigit():
            event['pr_number'] = int(pr_text)
        
        # In a real AWS environment, this would invoke another Lambda
        # For local development, we call directly
        result = await review_pull_request(event)
        logger.info("PR review triggered", result=result.get('statusCode'))
        
    except Exception as e:
        logger.error("Failed to trigger PR review", error=str(e))


async def get_recent_standups() -> Dict[str, Any]:
    """API endpoint to get recent standup summaries."""
    try:
        dynamodb_service = DynamoDBService()
        standup = await dynamodb_service.get_latest_standup()
        
        if standup:
            return {
                'statusCode': 200,
                'body': {
                    'standup': standup.dict()
                }
            }
        else:
            return {
                'statusCode': 404,
                'body': {
                    'message': 'No recent standups found'
                }
            }
    
    except Exception as e:
        logger.error("Failed to get recent standups", error=str(e))
        return {
            'statusCode': 500,
            'body': {
                'error': f'Failed to retrieve standups: {str(e)}'
            }
        }