#!/bin/bash

# Test Lambda deployment script

set -e

STAGE=${1:-dev}
REGION=${2:-us-east-1}

echo "🧪 Testing DevStandup AI Lambda deployment"

# Get API Gateway URL
API_URL=$(serverless info --stage $STAGE --region $REGION | grep "endpoint:" | awk '{print $2}')

if [ -z "$API_URL" ]; then
    echo "❌ Could not find API Gateway URL. Make sure deployment was successful."
    exit 1
fi

echo "🌐 Testing API at: $API_URL"

# Test health endpoint
echo "1. Testing health endpoint..."
curl -s "$API_URL/health" | jq '.'

# Test standup endpoint (should return empty or existing data)
echo "2. Testing standup endpoint..."
curl -s "$API_URL/api/standup" | jq '.'

# Test generate standup (this will make actual API calls)
echo "3. Testing standup generation (this will use Claude API)..."
echo "⚠️  This will consume Claude API tokens. Continue? (y/N)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    curl -s -X POST "$API_URL/api/standup/generate?hours=24" | jq '.'
else
    echo "Skipped standup generation test"
fi

echo "✅ Lambda testing complete!"
echo ""
echo "📊 Monitor your deployment:"
echo "- CloudWatch Logs: https://console.aws.amazon.com/cloudwatch/home?region=$REGION#logsV2:log-groups"
echo "- API Gateway: https://console.aws.amazon.com/apigateway/home?region=$REGION"
echo "- Lambda Functions: https://console.aws.amazon.com/lambda/home?region=$REGION"