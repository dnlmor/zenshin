from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import os
from datetime import datetime

from .routers.analysis import router as analysis_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle application startup and shutdown events
    """
    # Startup
    logger.info("🚀 AI Code Review Assistant Backend Starting Up...")
    
    # Validate required environment variables
    required_env_vars = ["CLAUDE_API_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {missing_vars}")
        raise RuntimeError(f"Missing required environment variables: {missing_vars}")
    
    # Optional environment variables
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        logger.warning("⚠️  GITHUB_TOKEN not set. GitHub API rate limits will be lower.")
    
    logger.info("✅ Environment variables validated")
    logger.info("✅ Services initialized")
    logger.info("🎯 Backend ready to analyze repositories!")
    
    yield
    
    # Shutdown
    logger.info("🛑 AI Code Review Assistant Backend Shutting Down...")


# Create FastAPI app
app = FastAPI(
    title="AI Code Review Assistant",
    description="""
    🤖 **AI Code Review Assistant Backend**
    
    An intelligent code analysis tool that reviews GitHub repositories using Claude AI.
    
    ## Features
    * 🔍 **Repository Analysis**: Analyze any public GitHub repository
    * 🛡️ **Security Scanning**: Detect security vulnerabilities and unsafe practices
    * ⚡ **Performance Review**: Identify performance bottlenecks and optimizations
    * 🔧 **Maintainability**: Assess code structure and maintainability issues
    * 🎨 **Style Guide**: Check coding standards and formatting
    * 🐛 **Bug Detection**: Find potential bugs and edge cases
    
    ## Supported Languages
    Python, JavaScript, TypeScript, Java, C++, Go, Rust, and 20+ more languages.
    
    ## Usage
    1. Send a POST request to `/api/analyze` with a GitHub repository URL
    2. Receive comprehensive analysis with issues, scores, and recommendations
    3. Use results to improve code quality and security
    """,
    version="1.0.0",
    contact={
        "name": "Daniel",
        "email": "daniel@example.com"
    },
    license_info={
        "name": "MIT License"
    },
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React development server
        "http://localhost:5173",  # Vite development server
        "https://your-frontend-domain.com"  # Production frontend
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analysis_router)

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint with API information
    """
    return {
        "message": "🤖 AI Code Review Assistant Backend",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "docs": "/docs",
        "health": "/api/health",
        "analyze": "/api/analyze"
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    """
    Global exception handler for unhandled errors
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url)
        }
    )

# Custom HTTP exception handler
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc: HTTPException):
    """
    Custom HTTP exception handler
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url)
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    # Development server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )