"""Slack integration handler for slash commands and webhooks."""
import json
from typing import Dict, Any
from urllib.parse import parse_qs
from ..services.slack_service import SlackService
from ..services.dynamodb_service import DynamoDBService
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SlackIntegrationHandler:
    """Handler for Slack integration."""
    
    def __init__(self):
        self.slack_service = SlackService()
        self.dynamodb_service = DynamoDBService()
    
    async def handle_webhook(self, event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Handle Slack webhook events."""
        try:
            body = event.get('body', '')
            
            # Handle URL-encoded form data from Slack
            if isinstance(body, str):
                parsed_body = parse_qs(body)
                slack_data = {key: value[0] if isinstance(value, list) else value 
                             for key, value in parsed_body.items()}
            else:
                slack_data = body
            
            # Handle slash commands
            if 'command' in slack_data:
                return await self._handle_slash_command(slack_data)
            
            # Handle interactive components
            elif 'payload' in slack_data:
                payload = json.loads(slack_data['payload'])
                return await self._handle_interactive_component(payload)
            
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Invalid request format'})
            }
        
        except Exception as e:
            logger.error("Slack webhook failed", error=str(e))
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': str(e)})
            }
    
    async def _handle_slash_command(self, slack_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Slack slash commands."""
        try:
            command = slack_data.get('command')
            text = slack_data.get('text', '')
            user_id = slack_data.get('user_id')
            
            logger.info("Handling slash command", command=command, user_id=user_id)
            
            response = await self.slack_service.handle_slash_command(command, text, user_id)
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(response)
            }
        
        except Exception as e:
            logger.error("Failed to handle slash command", error=str(e))
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'response_type': 'ephemeral',
                    'text': f'Error processing command: {str(e)}'
                })
            }
    
    async def _handle_interactive_component(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Slack interactive components."""
        try:
            action_type = payload.get('type')
            user = payload.get('user', {})
            
            logger.info("Handling interactive component", type=action_type, user_id=user.get('id'))
            
            # Process interactive actions
            if action_type == 'block_actions':
                actions = payload.get('actions', [])
                for action in actions:
                    action_id = action.get('action_id')
                    logger.info("Processing action", action_id=action_id)
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'text': 'Processing your request...'})
            }
        
        except Exception as e:
            logger.error("Failed to handle interactive component", error=str(e))
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'text': f'Error: {str(e)}'})
            }
    
    async def post_standup(self, event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Post standup summary to Slack."""
        try:
            body = json.loads(event.get('body', '{}'))
            standup_data = body.get('standup')
            
            if not standup_data:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'Missing standup data'})
                }
            
            await self.slack_service.post_standup_summary(standup_data)
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'message': 'Standup posted to Slack'})
            }
        
        except Exception as e:
            logger.error("Failed to post standup", error=str(e))
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': str(e)})
            }