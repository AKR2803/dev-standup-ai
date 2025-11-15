"""Lambda handler for POST /api/docs/generate."""
import asyncio
from typing import Dict, Any
from .handlers.api_gateway import APIGatewayHandler
from .utils.logger import get_logger

logger = get_logger(__name__)
api_handler = APIGatewayHandler()


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Generate docstring."""
    cors_headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
        'Content-Type': 'application/json'
    }
    
    try:
        logger.info("Generate docs request")
        result = asyncio.run(api_handler.generate_docstring(event, context))
        result['headers'] = {**result.get('headers', {}), **cors_headers}
        return result
    except Exception as e:
        logger.error("Generate docs error", error=str(e))
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': f'{{"error": "{str(e)}"}}'
        }