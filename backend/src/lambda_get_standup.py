"""Lambda handler for GET /api/standup."""
import asyncio
from typing import Dict, Any
from .handlers.api_gateway import APIGatewayHandler
from .utils.logger import get_logger

logger = get_logger(__name__)
api_handler = APIGatewayHandler()


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Get standup summary."""
    try:
        logger.info("Get standup request")
        return asyncio.run(api_handler.get_standup(event, context))
    except Exception as e:
        logger.error("Get standup error", error=str(e))
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': f'{{"error": "{str(e)}"}}'
        }