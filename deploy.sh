#!/bin/bash

# DevStandup AI Lambda Deployment Script

set -e

echo "🚀 Deploying DevStandup AI to AWS Lambda"

# Check if serverless is installed
if ! command -v serverless &> /dev/null; then
    echo "❌ Serverless Framework not found. Installing..."
    npm install -g serverless
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please copy .env.example to .env and configure it."
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Validate required environment variables
if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ GITHUB_TOKEN is required"
    exit 1
fi

if [ -z "$GITHUB_REPO_OWNER" ]; then
    echo "❌ GITHUB_REPO_OWNER is required"
    exit 1
fi

if [ -z "$GITHUB_REPO_NAME" ]; then
    echo "❌ GITHUB_REPO_NAME is required"
    exit 1
fi

if [ "$USE_BEDROCK" = "false" ] && [ -z "$CLAUDE_API_KEY" ]; then
    echo "❌ CLAUDE_API_KEY is required when USE_BEDROCK=false"
    exit 1
fi

# Install serverless plugins
echo "📦 Installing Serverless plugins..."
npm install --save-dev serverless-python-requirements

# Deploy to AWS
STAGE=${1:-dev}
REGION=${2:-us-east-1}

echo "🌍 Deploying to stage: $STAGE, region: $REGION"

serverless deploy --stage $STAGE --region $REGION

echo "✅ Deployment complete!"
echo ""
echo "🌐 Lambda Functions Deployed:"
echo "📖 Read Function (GET operations)"
echo "🤖 AI Function (Claude API calls)"
echo "🐙 GitHub Function (GitHub sync)"
echo "💬 Slack Function (Slack integration)"
echo ""
echo "🌐 API Gateway URLs:"
serverless info --stage $STAGE --region $REGION | grep "endpoint:"

echo ""
echo "🧪 Test the deployment:"
API_URL=$(serverless info --stage $STAGE --region $REGION | grep 'endpoint:' | head -1 | awk '{print $2}')
echo "Health Check: curl $API_URL/health"
echo "Get Standup: curl $API_URL/api/standup"
echo "Generate Standup: curl -X POST $API_URL/api/standup/generate?hours=24"
echo "GitHub Sync: curl -X POST $API_URL/api/github/sync?hours=24"