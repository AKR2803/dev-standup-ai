"""Lambda handler for POST /api/tests/generate."""
import asyncio
from typing import Dict, Any
from .handlers.api_gateway import APIGatewayHandler
from .utils.logger import get_logger

logger = get_logger(__name__)
api_handler = APIGatewayHandler()


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Generate unit tests."""
    try:
        logger.info("Generate tests request")
        return asyncio.run(api_handler.generate_test(event, context))
    except Exception as e:
        logger.error("Generate tests error", error=str(e))
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': f'{{"error": "{str(e)}"}}'
        }