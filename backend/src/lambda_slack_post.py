"""Lambda handler for Slack post operations."""
import json
import asyncio
from typing import Dict, Any
from .handlers.slack_integration import SlackIntegrationHandler
from .utils.logger import get_logger

logger = get_logger(__name__)
slack_handler = SlackIntegrationHandler()


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle Slack post standup operations."""
    try:
        logger.info("Slack post request")
        return asyncio.run(slack_handler.post_standup(event, context))
            
    except Exception as e:
        logger.error("Slack post error", error=str(e))
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }