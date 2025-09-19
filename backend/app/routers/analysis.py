from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Dict, Any
import logging
from datetime import datetime

from ..models.analysis import AnalysisRequest, AnalysisResult
from ..services.analysis_service import analysis_service
from ..utils.validators import validate_github_url

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api",
    tags=["analysis"],
    responses={
        400: {"description": "Bad Request"},
        422: {"description": "Validation Error"},
        500: {"description": "Internal Server Error"}
    }
)


@router.post(
    "/analyze",
    response_model=AnalysisResult,
    status_code=status.HTTP_200_OK,
    summary="Analyze GitHub Repository",
    description="Analyze a GitHub repository for code quality, security issues, and improvements"
)
async def analyze_repository(request: AnalysisRequest) -> AnalysisResult:
    """
    Main endpoint for repository analysis.
    
    This endpoint:
    1. Validates the GitHub URL
    2. Fetches repository data from GitHub API
    3. Sends code to Claude AI for analysis
    4. Returns structured analysis results
    
    **Parameters:**
    - **github_url**: Valid GitHub repository URL
    - **file_types**: List of file extensions to analyze (optional)
    - **max_files**: Maximum number of files to analyze (1-100, default: 20)
    
    **Returns:**
    - Comprehensive analysis with issues, scores, and recommendations
    """
    try:
        # Additional URL validation
        if not validate_github_url(str(request.github_url)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid GitHub repository URL format"
            )
        
        # Log the analysis request
        logger.info(f"Starting analysis for repository: {request.github_url}")
        
        # Perform the analysis
        result = await analysis_service.analyze_repository(request)
        
        # Log success
        logger.info(
            f"Analysis completed for {request.github_url}. "
            f"Found {result.summary.total_issues} issues across "
            f"{result.repository.total_files_analyzed} files"
        )
        
        return result
        
    except ValueError as e:
        # Handle business logic errors
        error_detail = str(e)
        logger.error(f"Analysis failed for {request.github_url}: {error_detail}")
        
        # Map specific error types to appropriate HTTP status codes
        if "not found" in error_detail.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_detail
            )
        elif "rate limit" in error_detail.lower():
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=error_detail
            )
        elif "api key" in error_detail.lower() or "access denied" in error_detail.lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API authentication failed"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_detail
            )
            
    except Exception as e:
        # Handle unexpected errors
        error_msg = f"Unexpected error during analysis: {str(e)}"
        logger.error(f"Unexpected error for {request.github_url}: {error_msg}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred during analysis"
        )


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check the health of the analysis service and its dependencies"
)
async def health_check() -> JSONResponse:
    """
    Health check endpoint to verify service status.
    
    Checks:
    - Analysis service availability
    - GitHub service connectivity
    - Claude API accessibility
    
    **Returns:**
    - Service health status and timestamp
    """
    try:
        # Check service health
        health_status = await analysis_service.health_check()
        
        # Determine overall health
        all_healthy = all(health_status.values())
        
        response_data = {
            "status": "healthy" if all_healthy else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "services": health_status,
            "version": "1.0.0"
        }
        
        # Return appropriate status code
        status_code = status.HTTP_200_OK if all_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
        
        return JSONResponse(
            status_code=status_code,
            content=response_data
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": "Health check failed",
                "version": "1.0.0"
            }
        )


@router.get(
    "/analyze/example",
    status_code=status.HTTP_200_OK,
    summary="Get Example Request",
    description="Get an example analysis request for testing purposes"
)
async def get_example_request() -> Dict[str, Any]:
    """
    Returns an example analysis request for API testing.
    
    **Returns:**
    - Example request payload that can be used with the /analyze endpoint
    """
    return {
        "example_request": {
            "github_url": "https://github.com/octocat/Hello-World",
            "file_types": ["py", "js", "ts", "java"],
            "max_files": 15
        },
        "description": "Use this example to test the /api/analyze endpoint",
        "note": "Replace the github_url with a real repository you want to analyze"
    }
