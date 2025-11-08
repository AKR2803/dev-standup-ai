"""FastAPI application entry point."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
from typing import Optional, List
from datetime import datetime, timedelta

from .handlers.api_gateway import APIGatewayHandler
from .utils.config import settings
from .utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting DevStandup AI API", port=settings.api_port)
    yield
    logger.info("Shutting down DevStandup AI API")


# Create FastAPI app
app = FastAPI(
    title="DevStandup AI API",
    description="AI-powered development team standup automation",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize handler
api_handler = APIGatewayHandler()


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "DevStandup AI API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# Standup endpoints
@app.get("/api/standup")
async def get_standup():
    """Get latest standup summary."""
    try:
        result = await api_handler.get_standup({}, {})
        return JSONResponse(content=result["body"], status_code=result["statusCode"])
    except Exception as e:
        logger.error("Failed to get standup", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/standup/generate")
async def generate_standup(hours: int = 24):
    """Generate new standup summary."""
    try:
        event = {
            "queryStringParameters": {"hours": str(hours)},
            "body": None
        }
        result = await api_handler.generate_standup(event, {})
        return JSONResponse(content=result["body"], status_code=result["statusCode"])
    except Exception as e:
        logger.error("Failed to generate standup", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# Code review endpoints
@app.post("/api/reviews/generate")
async def generate_review(pr_number: Optional[int] = None, hours: int = 24):
    """Generate code review for PR."""
    try:
        query_params = {"hours": str(hours)}
        if pr_number:
            query_params["pr_number"] = str(pr_number)
            
        event = {
            "queryStringParameters": query_params,
            "body": None
        }
        result = await api_handler.generate_code_review(event, {})
        return JSONResponse(content=result["body"], status_code=result["statusCode"])
    except Exception as e:
        logger.error("Failed to generate review", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# Documentation endpoints
@app.post("/api/docs/generate")
async def generate_docstring(request: dict):
    """Generate docstring for function."""
    try:
        event = {
            "body": request,
            "queryStringParameters": {}
        }
        result = await api_handler.generate_docstring(event, {})
        return JSONResponse(content=result["body"], status_code=result["statusCode"])
    except Exception as e:
        logger.error("Failed to generate docstring", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tests/generate")
async def generate_test(request: dict):
    """Generate unit test for function."""
    try:
        event = {
            "body": request,
            "queryStringParameters": {}
        }
        result = await api_handler.generate_test(event, {})
        return JSONResponse(content=result["body"], status_code=result["statusCode"])
    except Exception as e:
        logger.error("Failed to generate test", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# GitHub sync endpoint
@app.post("/api/github/sync")
async def sync_github_activity(hours: int = 24):
    """Sync GitHub activity data."""
    try:
        event = {
            "queryStringParameters": {"hours": str(hours)},
            "body": None
        }
        result = await api_handler.aggregate_activity(event, {})
        return JSONResponse(content=result["body"], status_code=result["statusCode"])
    except Exception as e:
        logger.error("Failed to sync GitHub activity", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level=settings.log_level.lower()
    )