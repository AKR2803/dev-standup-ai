---
noteId: "13d76bb0bcdb11f0bf24976974e5e5fc"
tags: []

---

# DevStandup AI

![DevStandup AI Thumbnail](/frontend/thumbnail.png)

AI-powered development team standup automation using GitHub activity analysis and Claude AI.

## Why Do This?

As teams scale, developers often spend valuable time on coordination rather than creation.  
Or as senior software engineer **Lloyd Atkinson** put it —  
> “Every day, we are expected to repeat the same mantra: *‘Yesterday, I did the work I needed to do. Today, I will do the work I need to do’.*”  
> — on daily stand-ups becoming a “parody of productivity.” [[LeadDev](https://leaddev.com/velocity/should-daily-stand-die?utm_source=chatgpt.com)]

Our goal is to make developer collaboration more effortless and insightful by addressing a few common friction points:

1. **Standup updates can take extra time to prepare** — turning a daily ritual into a chore.  
2. **Code reviews often vary in depth and consistency** — slowing down merges and learning.  
3. **Documentation and tests can lag behind new changes** — making knowledge harder to share.  
4. **It’s easy to lose track of overall project activity** — especially across fast-moving teams.  
5. **Teams juggle multiple tools for communication and tracking** — leading to fragmented workflows.

This project automates those repetitive tasks using AI, helping teams stay aligned without the overhead.

## Features

- **Automated Standup Generation**: Analyze GitHub activity to create structured standup summaries
- **AI Code Reviews**: Generate comprehensive PR reviews with security and quality insights
- **Documentation Generation**: Auto-generate docstrings and unit tests
- **Slack Integration**: Post standup summaries directly to Slack channels
- **Real-time Dashboard**: React frontend for managing and viewing AI-generated content

## Architecture

- **Backend**: FastAPI with Claude AI integration
- **Frontend**: React + TypeScript + Tailwind CSS
- **Database**: DynamoDB
- **AI Models**: Claude 3.5 Sonnet via Anthropic API or AWS Bedrock

## Quick Start (Local Development)

### Prerequisites

- Python 3.9+
- Node.js 18+
- Docker & Docker Compose
- GitHub Personal Access Token
- Claude API Key (Anthropic) OR AWS Bedrock access

### 1. Clone and Setup

```bash
git clone <repository-url>
cd devstandup-ai
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` with your credentials:

```bash
# GitHub Integration
GITHUB_TOKEN=ghp_your_github_token_here
GITHUB_REPO_OWNER=your-username
GITHUB_REPO_NAME=your-repo

# Claude API (Choose one)
# Option 1: Anthropic Claude API
CLAUDE_API_KEY=sk-ant-your-claude-api-key-here
CLAUDE_MODEL=claude-3-5-sonnet-20241022
USE_BEDROCK=false

# Option 2: AWS Bedrock Claude
USE_BEDROCK=true
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0

# Optional: Slack Integration
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_SIGNING_SECRET=your-slack-signing-secret
SLACK_CHANNEL=#standup
```

### 3. Start Services

```bash
# Start DynamoDB local and other services
docker-compose up -d

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install
```

### 4. Run Application

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Access the application:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Using AWS Bedrock Claude

To use AWS Bedrock instead of Anthropic's Claude API:

### 1. Setup AWS Credentials

```bash
# Option 1: AWS CLI
aws configure

# Option 2: Environment variables (already in .env)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
```

### 2. Enable Bedrock Model Access

1. Go to AWS Bedrock Console
2. Navigate to "Model access" 
3. Request access to "Claude 3.5 Sonnet"
4. Wait for approval (usually instant)

### 3. Update Configuration

```bash
# In .env file
USE_BEDROCK=true
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
```

## API Endpoints

### Core Endpoints

- `GET /api/standup` - Get latest standup summary
- `POST /api/standup/generate` - Generate new standup from GitHub activity
- `POST /api/reviews/generate` - Generate PR review
- `POST /api/docs/generate` - Generate function docstring
- `POST /api/tests/generate` - Generate unit tests
- `POST /api/github/sync` - Sync GitHub activity data

### Example Usage

```bash
# Generate standup for last 24 hours
curl -X POST "http://localhost:8000/api/standup/generate?hours=24"

# Review specific PR
curl -X POST "http://localhost:8000/api/reviews/generate?pr_number=123"

# Generate docstring
curl -X POST "http://localhost:8000/api/docs/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "src/utils.py",
    "function_name": "process_data",
    "code": "def process_data(data): return data.upper()"
  }'
```

## Development

### Backend Development

```bash
cd backend

# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run with auto-reload
python -m uvicorn src.main:app --reload

# Format code
black src/
isort src/

# Type checking
mypy src/
```

### Frontend Development

```bash
cd frontend

# Development server
npm run dev

# Build for production
npm run build

# Type checking
npm run type-check

# Linting
npm run lint
```

### Testing

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm test

# Integration tests
make test-integration
```

## Docker Deployment

### Build Images

```bash
# Build all services
docker-compose build

# Build specific service
docker build -f Dockerfile.backend -t devstandup-backend .
docker build -f Dockerfile.frontend -t devstandup-frontend .
```

### Production Deployment

```bash
# Start production stack
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

## Configuration Options

### Claude Model Selection

**Cost-Optimized (Recommended for development):**
```bash
# Anthropic Claude API models
CLAUDE_MODEL=claude-3-haiku-20240307         # ~$0.25/1M tokens (input), ~$1.25/1M tokens (output)
CLAUDE_MODEL=claude-3-5-sonnet-20241022      # ~$3/1M tokens (input), ~$15/1M tokens (output)
CLAUDE_MODEL=claude-3-opus-20240229          # ~$15/1M tokens (input), ~$75/1M tokens (output)

# AWS Bedrock model IDs (similar pricing)
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0      # Most cost-effective
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0   # Balanced performance/cost
BEDROCK_MODEL_ID=anthropic.claude-3-opus-20240229-v1:0       # Highest capability
```

**Model Comparison:**
- **Haiku**: 20x cheaper than Sonnet, 60x cheaper than Opus. Great for standups, basic reviews
- **Sonnet**: Best balance of capability and cost. Use for complex code reviews
- **Opus**: Most capable but expensive. Use only for critical analysis

### GitHub Configuration

```bash
# Required scopes for GitHub token:
# - repo (for private repos)
# - public_repo (for public repos)
# - read:user
# - user:email

GITHUB_TOKEN=ghp_your_token_here
GITHUB_REPO_OWNER=your-username
GITHUB_REPO_NAME=your-repo-name
```

## Troubleshooting

### Common Issues

**1. Claude API Rate Limits**
```bash
# Reduce request frequency
API_RATE_LIMIT=10  # requests per minute
```

**2. GitHub API Rate Limits**
```bash
# Use authenticated requests (higher limits)
# Ensure GITHUB_TOKEN is set correctly
```

**3. DynamoDB Connection Issues**
```bash
# Restart local DynamoDB
docker-compose restart dynamodb-local

# Check endpoint configuration
DYNAMODB_ENDPOINT=http://localhost:8001
```

**4. Bedrock Access Issues**
```bash
# Verify model access in AWS Console
# Check IAM permissions for bedrock:InvokeModel
# Ensure correct region configuration
```

### Logs and Debugging

```bash
# Backend logs
LOG_LEVEL=DEBUG

# View container logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Database inspection
aws dynamodb scan --table-name standups --endpoint-url http://localhost:8001
```

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## License

MIT License - see LICENSE file for details.