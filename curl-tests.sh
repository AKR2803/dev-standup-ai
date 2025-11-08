#!/bin/bash

# API Gateway URL - replace with your deployed URL
API_URL=${1:-"https://ymx4dqjcua.execute-api.us-east-1.amazonaws.com/dev"}

echo "🧪 Testing DevStandup AI API Endpoints"
echo "🌐 API URL: $API_URL"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

test_endpoint() {
    local name=$1
    local method=$2
    local path=$3
    local data=$4
    
    echo -e "\n${YELLOW}🧪 Testing: $name${NC}"
    echo "📡 $method $API_URL$path"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "%{http_code}" -X GET "$API_URL$path")
    else
        if [ -n "$data" ]; then
            response=$(curl -s -w "%{http_code}" -X POST \
                -H "Content-Type: application/json" \
                -d "$data" \
                "$API_URL$path")
        else
            response=$(curl -s -w "%{http_code}" -X POST "$API_URL$path")
        fi
    fi
    
    # Extract status code (last 3 characters)
    status_code="${response: -3}"
    body="${response%???}"
    
    if [ "$status_code" -ge 200 ] && [ "$status_code" -lt 300 ]; then
        echo -e "${GREEN}✅ Status: $status_code${NC}"
        echo "📥 Response: $(echo "$body" | jq '.' 2>/dev/null || echo "$body" | head -c 100)..."
    else
        echo -e "${RED}❌ Status: $status_code${NC}"
        echo "📥 Error: $(echo "$body" | jq '.' 2>/dev/null || echo "$body")"
    fi
}

# Test 1: Get Standup (should return 404 if no standup exists)
test_endpoint "Get Standup" "GET" "/api/standup"

# Test 2: GitHub Sync (should work with valid GitHub token)
test_endpoint "GitHub Sync" "POST" "/api/github/sync?hours=24"

# Test 3: Generate Standup (will consume Claude API tokens)
echo -e "\n${YELLOW}⚠️  The following tests will consume Claude API tokens. Continue? (y/N)${NC}"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    
    test_endpoint "Generate Standup" "POST" "/api/standup/generate?hours=24"
    
    test_endpoint "Generate Review" "POST" "/api/reviews/generate?hours=24"
    
    test_endpoint "Generate Docs" "POST" "/api/docs/generate" \
        '{"file_path": "src/utils.py", "function_name": "process_data", "code": "def process_data(data):\n    return data.upper()"}'
    
    test_endpoint "Generate Tests" "POST" "/api/tests/generate" \
        '{"file_path": "src/utils.py", "function_name": "process_data", "code": "def process_data(data):\n    return data.upper()"}'
    
else
    echo "⏭️  Skipped API token consuming tests"
fi

# Test 4: Slack Webhook (should handle invalid payload gracefully)
test_endpoint "Slack Webhook" "POST" "/api/slack/webhook" \
    '{"command": "/standup", "text": "", "user_id": "U123456"}'

echo -e "\n${GREEN}✅ API testing complete!${NC}"
echo ""
echo "📚 Usage Examples:"
echo "  Get Standup:     curl $API_URL/api/standup"
echo "  GitHub Sync:     curl -X POST $API_URL/api/github/sync?hours=24"
echo "  Generate Standup: curl -X POST $API_URL/api/standup/generate?hours=24"
echo ""
echo "🔧 Troubleshooting:"
echo "  - Check CloudWatch Logs for detailed error messages"
echo "  - Verify environment variables in Lambda configuration"
echo "  - Ensure DynamoDB tables exist and have correct permissions"