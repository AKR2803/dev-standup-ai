"""Configuration management for the application."""
import os
from typing import List
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    api_port: int = Field(default=8000, env="API_PORT")
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    cors_origins: List[str] = Field(default=["http://localhost:3000"], env="CORS_ORIGINS")
    
    # GitHub Integration
    github_token: str = Field(..., env="GITHUB_TOKEN")
    github_repo_owner: str = Field(..., env="GITHUB_REPO_OWNER")
    github_repo_name: str = Field(..., env="GITHUB_REPO_NAME")
    
    # Claude API (Anthropic or Bedrock)
    use_bedrock: bool = Field(default=False, env="USE_BEDROCK")
    claude_api_key: str = Field(default="", env="CLAUDE_API_KEY")
    claude_model: str = Field(default="claude-3-5-sonnet-20241022", env="CLAUDE_MODEL")
    
    # AWS Bedrock Configuration
    aws_region: str = Field(default="us-east-1", env="AWS_REGION")
    bedrock_model_id: str = Field(default="anthropic.claude-3-5-sonnet-20241022-v2:0", env="BEDROCK_MODEL_ID")
    
    # Slack Integration
    slack_bot_token: str = Field(..., env="SLACK_BOT_TOKEN")
    slack_signing_secret: str = Field(..., env="SLACK_SIGNING_SECRET")
    slack_channel: str = Field(default="#standup", env="SLACK_CHANNEL")
    
    # DynamoDB
    dynamodb_endpoint: str = Field(default="http://localhost:8001", env="DYNAMODB_ENDPOINT")
    dynamodb_region: str = Field(default="us-east-1", env="DYNAMODB_REGION")
    aws_access_key_id: str = Field(default="local", env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(default="local", env="AWS_SECRET_ACCESS_KEY")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if isinstance(self.cors_origins, str):
            self.cors_origins = [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()