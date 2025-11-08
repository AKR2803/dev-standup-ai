"""Lambda handler for Slack operations."""
import json
import asyncio
from typing import Dict, Any
from .handlers.slack_integration import SlackIntegrationHandler
from .utils.logger import get_logger

logger = get_logger(__name__)
slack_handler = SlackIntegrationHandler()


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle Slack operations."""
    try:
        path = event.get('path', '/')
        logger.info("Slack Lambda request", path=path)
        
        if path == '/health':
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'status': 'healthy', 'service': 'slack'})
            }
        elif path == '/api/slack/webhook':
            return asyncio.run(slack_handler.handle_webhook(event, context))
        elif path == '/api/slack/post':
            return asyncio.run(slack_handler.post_standup(event, context))
        else:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Not found'})
            }
            
    except Exception as e:
        logger.error("Slack Lambda error", error=str(e))
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }