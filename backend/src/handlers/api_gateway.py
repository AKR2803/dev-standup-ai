"""API Gateway handlers for REST endpoints."""
import json
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from ..handlers.activity_aggregator import aggregate_activity_endpoint
from ..handlers.ai_processor import generate_standup_summary, review_pull_request, generate_docstring, generate_unit_test
from ..handlers.slack_integration import get_recent_standups
from ..services.dynamodb_service import DynamoDBService
from ..services.github_service import GitHubService
from ..utils.config import settings
from ..utils.validators import DateRangeRequest, GenerateRequest
from ..utils.logger import get_logger, configure_logging

# Configure logging
configure_logging()
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="DevStandup.ai API",
    description="AI-powered engineering team assistant",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.get("/api/standup")
async def get_standup_summary(date_range: DateRangeRequest = Depends()):
    """Get team standup summary."""
    try:
        logger.info("Getting standup summary", start_date=date_range.start_date, end_date=date_range.end_date)
        
        result = await get_recent_standups()
        
        if result['statusCode'] == 200:
            return result['body']
        elif result['statusCode'] == 404:
            raise HTTPException(status_code=404, detail="No standup found")
        else:
            raise HTTPException(status_code=500, detail=result['body'].get('error', 'Internal server error'))
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get standup summary", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get standup: {str(e)}")


@app.post("/api/standup/generate")
async def generate_standup(since_hours: int = 24):
    """Generate new standup summary."""
    try:
        logger.info("Generating standup summary", since_hours=since_hours)
        
        event = {
            'operation': 'standup',
            'since_hours': since_hours,
            'post_to_slack': False  # Don't auto-post from API calls
        }
        
        result = await generate_standup_summary(event)
        
        if result['statusCode'] == 200:
            return result['body']
        else:
            raise HTTPException(status_code=500, detail=result['body'].get('error', 'Generation failed'))
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to generate standup", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to generate standup: {str(e)}")


@app.get("/api/reviews")
async def get_code_reviews(pr_number: Optional[int] = None):
    """Get code reviews."""
    try:
        logger.info("Getting code reviews", pr_number=pr_number)
        
        dynamodb_service = DynamoDBService()
        
        if pr_number:
            review = await dynamodb_service.get_code_review(pr_number)
            if review:
                return {"review": review.dict()}
            else:
                raise HTTPException(status_code=404, detail="Review not found")
        else:
            # Return recent reviews (simplified for MVP)
            return {"message": "List of recent reviews not implemented yet"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get code reviews", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get reviews: {str(e)}")


@app.post("/api/reviews/generate")
async def generate_code_review(pr_number: Optional[int] = None, since_hours: int = 24):
    """Generate code review for PR(s)."""
    try:
        logger.info("Generating code review", pr_number=pr_number, since_hours=since_hours)
        
        event = {
            'operation': 'review',
            'since_hours': since_hours,
            'post_to_slack': False
        }
        
        if pr_number:
            event['pr_number'] = pr_number
        
        result = await review_pull_request(event)
        
        if result['statusCode'] == 200:
            return result['body']
        else:
            raise HTTPException(status_code=500, detail=result['body'].get('error', 'Review generation failed'))
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to generate code review", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to generate review: {str(e)}")


@app.post("/api/docs/generate")
async def generate_documentation(request: GenerateRequest):
    """Generate documentation (docstrings)."""
    try:
        if request.type != 'docstring':
            raise HTTPException(status_code=400, detail="Invalid generation type for docs endpoint")
        
        logger.info("Generating documentation", data=request.data)
        
        event = {
            'operation': 'docstring',
            **request.data
        }
        
        result = await generate_docstring(event)
        
        if result['statusCode'] == 200:
            return result['body']
        else:
            raise HTTPException(status_code=500, detail=result['body'].get('error', 'Documentation generation failed'))
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to generate documentation", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to generate docs: {str(e)}")


@app.post("/api/tests/generate")
async def generate_tests(request: GenerateRequest):
    """Generate unit tests."""
    try:
        if request.type != 'test':
            raise HTTPException(status_code=400, detail="Invalid generation type for tests endpoint")
        
        logger.info("Generating unit tests", data=request.data)
        
        event = {
            'operation': 'test',
            **request.data
        }
        
        result = await generate_unit_test(event)
        
        if result['statusCode'] == 200:
            return result['body']
        else:
            raise HTTPException(status_code=500, detail=result['body'].get('error', 'Test generation failed'))
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to generate tests", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to generate tests: {str(e)}")


@app.post("/api/activity/aggregate")
async def aggregate_activity(since_hours: int = 24):
    """Trigger activity aggregation from GitHub."""
    try:
        logger.info("Aggregating activity", since_hours=since_hours)
        
        result = await aggregate_activity_endpoint(since_hours)
        
        if result['statusCode'] == 200:
            return result['body']
        else:
            raise HTTPException(status_code=500, detail=result['body'].get('error', 'Activity aggregation failed'))
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to aggregate activity", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to aggregate activity: {str(e)}")


@app.get("/api/activity")
async def get_activity(date_range: DateRangeRequest = Depends()):
    """Get developer activity for date range."""
    try:
        logger.info("Getting activity", start_date=date_range.start_date, end_date=date_range.end_date)
        
        github_service = GitHubService()
        activities = await github_service.aggregate_developer_activity(date_range.start_date)
        
        return {
            "activities": [activity.dict() for activity in activities],
            "count": len(activities)
        }
    
    except Exception as e:
        logger.error("Failed to get activity", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get activity: {str(e)}")


# Slack webhook endpoint
@app.post("/api/slack/webhook")
async def slack_webhook(request: dict):
    """Handle Slack webhook events."""
    try:
        from ..handlers.slack_integration import lambda_handler
        
        # Convert FastAPI request to Lambda event format
        event = {
            'httpMethod': 'POST',
            'body': json.dumps(request),
            'headers': {'content-type': 'application/json'}
        }
        
        result = await lambda_handler(event, None)
        
        if result['statusCode'] == 200:
            return json.loads(result['body'])
        else:
            raise HTTPException(status_code=result['statusCode'], detail=result.get('body'))
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Slack webhook failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error("Unhandled exception", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)