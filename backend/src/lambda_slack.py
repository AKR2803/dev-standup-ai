"""Lambda handler for Slack webhook."""
import json
import asyncio
from typing import Dict, Any
from .handlers.slack_integration import SlackIntegrationHandler
from .utils.logger import get_logger

logger = get_logger(__name__)
slack_handler = SlackIntegrationHandler()


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle Slack webhook events."""
    cors_headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
        'Content-Type': 'application/json'
    }
    
    try:
        logger.info("Slack webhook request")
        result = asyncio.run(slack_handler.handle_webhook(event, context))
        result['headers'] = {**result.get('headers', {}), **cors_headers}
        return result
            
    except Exception as e:
        logger.error("Slack webhook error", error=str(e))
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({'error': str(e)})
        }