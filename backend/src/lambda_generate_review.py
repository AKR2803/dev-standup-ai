"""Lambda handler for POST /api/reviews/generate."""
import asyncio
from typing import Dict, Any
from .handlers.api_gateway import APIGatewayHandler
from .utils.logger import get_logger

logger = get_logger(__name__)
api_handler = APIGatewayHandler()


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Generate code review."""
    try:
        logger.info("Generate review request")
        return asyncio.run(api_handler.generate_code_review(event, context))
    except Exception as e:
        logger.error("Generate review error", error=str(e))
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': f'{{"error": "{str(e)}"}}'
        }