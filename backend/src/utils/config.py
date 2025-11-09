"""Configuration management for the application."""
import os
from typing import List


class Settings:
    """Application settings loaded from environment variables."""
    
    def __init__(self):
        # API Configuration
        self.api_port = int(os.getenv("API_PORT", "8000"))
        self.api_host = os.getenv("API_HOST", "0.0.0.0")
        cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000")
        self.cors_origins = [origin.strip() for origin in cors_origins_str.split(",")]
        
        # GitHub Integration
        self.github_token = os.getenv("GITHUB_TOKEN", "")
        self.github_repo_owner = os.getenv("GITHUB_REPO_OWNER", "")
        self.github_repo_name = os.getenv("GITHUB_REPO_NAME", "")
        
        # Claude API (Anthropic or Bedrock)
        self.use_bedrock = os.getenv("USE_BEDROCK", "false").lower() == "true"
        self.claude_api_key = os.getenv("CLAUDE_API_KEY", "")
        self.claude_model = os.getenv("CLAUDE_MODEL", "claude-3-haiku-20240307")
        
        # AWS Bedrock Configuration
        self.aws_region = os.getenv("AWS_REGION", "us-east-1")
        self.bedrock_model_id = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
        
        # Slack Integration
        self.slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL", "")
        self.slack_signing_secret = os.getenv("SLACK_SIGNING_SECRET", "")
        
        # DynamoDB
        self.dynamodb_endpoint = os.getenv("DYNAMODB_ENDPOINT", "")
        self.dynamodb_region = os.getenv("DYNAMODB_REGION", "us-east-1")
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID", "")
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY", "")
        
        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()