#!/bin/bash

# DevStandup AI Local Development Startup Script

set -e

echo "🚀 Starting DevStandup AI Local Development Environment"

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please copy .env.example to .env and configure it."
    exit 1
fi

# Start DynamoDB local
echo "📦 Starting DynamoDB Local..."
docker-compose up -d dynamodb-local

# Wait for DynamoDB to be ready
echo "⏳ Waiting for DynamoDB to be ready..."
sleep 3

# Check if Python virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    cd backend
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
else
    echo "🐍 Activating Python virtual environment..."
    cd backend
    source venv/bin/activate
    cd ..
fi

# Check if node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

echo "✅ Environment setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Configure your .env file with GitHub token and Claude API key"
echo "2. Start the backend: cd backend && source venv/bin/activate && python -m uvicorn src.main:app --reload"
echo "3. Start the frontend: cd frontend && npm run dev"
echo ""
echo "🌐 Access URLs:"
echo "- Frontend: http://localhost:5173"
echo "- Backend API: http://localhost:8000"
echo "- API Docs: http://localhost:8000/docs"
echo ""
echo "📚 For more details, see README.md"