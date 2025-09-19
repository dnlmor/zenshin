from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
import logging
import re
from datetime import datetime

from ..models.analysis import AnalysisRequest, AnalysisResult
from ..services.analysis_service import analysis_service
from ..utils.validators import validate_github_url

# Set up logging
logger = logging.getLogger(__name__)


def parse_ai_review(review_text: str) -> dict:
    """
    Parse the AI review text into structured components for frontend consumption
    """
    if not review_text:
        return {"overall_score": 75, "summary": "Analysis completed"}
    
    result = {}
    
    # Extract overall score (no letter grade)
    score_match = re.search(r'Overall Score[:\s]*(\d+)/100', review_text)
    if score_match:
        result["overall_score"] = int(score_match.group(1))
    else:
        result["overall_score"] = 75
    
    # Extract summary (first paragraph after score)
    lines = review_text.split('\n')
    summary_lines = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('**') and not line.startswith('#'):
            summary_lines.append(line)
        elif summary_lines:  # Stop at first heading after we found summary
            break
    result["summary"] = ' '.join(summary_lines) if summary_lines else "Analysis completed"
    
    # Extract strengths
    strengths = []
    strengths_section = re.search(r"\*\*What's Good:\*\*(.*?)(?=\*\*What Can Be Improved:\*\*|\*\*Areas for Improvement:\*\*|$)", review_text, re.DOTALL)
    if strengths_section:
        strength_items = re.findall(r'\*\s*\*\*([^*]+)\*\*[:\s]*([^*\n]+)', strengths_section.group(1))
        for title, description in strength_items:
            strengths.append({
                "title": title.strip(),
                "description": description.strip()
            })
    result["strengths"] = strengths
    
    # Extract improvements and normalize scores to match overall score
    improvements = []
    improvements_section = re.search(r"\*\*What Can Be Improved:\*\*(.*?)(?=\*\*Code Sample|\*\*Final Thoughts|\*\*Closing Remarks|$)", review_text, re.DOTALL)
    if improvements_section:
        # Look for numbered items
        improvement_items = re.findall(r'\d+\.\s*\*\*([^(]+)\(([^)]+)\):\*\*[^\*]*\*\s*\*\*Issue\*\*:\s*([^\*]+)\*\s*\*\*Action\*\*:\s*([^\n]+)', improvements_section.group(1))
        
        overall_score = result.get("overall_score", 75)
        
        for title, score_text, issue, action in improvement_items:
            # Normalize the score to be consistent with overall score
            # If overall score is high (90+), individual scores should be 8-9/10
            # If overall score is medium (70-89), individual scores should be 6-8/10
            # If overall score is low (<70), individual scores should be 4-6/10
            
            if overall_score >= 90:
                normalized_score = "8-9/10"
            elif overall_score >= 80:
                normalized_score = "7-8/10"
            elif overall_score >= 70:
                normalized_score = "6-7/10"
            else:
                normalized_score = "4-6/10"
            
            improvements.append({
                "title": title.strip(),
                "score": normalized_score,
                "issue": issue.strip(),
                "action": action.strip()
            })
    result["improvements"] = improvements
    
    # Extract code examples
    code_examples = {}
    before_match = re.search(r'\*\*Before:\*\*\s*```[a-zA-Z]*\s*(.*?)\s*```', review_text, re.DOTALL)
    after_match = re.search(r'\*\*After:\*\*\s*```[a-zA-Z]*\s*(.*?)\s*```', review_text, re.DOTALL)
    
    if before_match and after_match:
        code_examples = {
            "before": before_match.group(1).strip(),
            "after": after_match.group(1).strip()
        }
    result["code_examples"] = code_examples
    
    # Extract final thoughts
    final_thoughts_match = re.search(r'\*\*Final Thoughts[:\s]*\*\*\s*([^*]+(?:\*[^*]+)*)', review_text, re.DOTALL)
    if final_thoughts_match:
        result["final_thoughts"] = final_thoughts_match.group(1).strip()
    else:
        result["final_thoughts"] = "Keep up the good work!"
    
    return result

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
    status_code=status.HTTP_200_OK,
    summary="Analyze GitHub Repository",
    description="Analyze a GitHub repository for code quality with AI-powered insights"
)
async def analyze_repository(request: AnalysisRequest):
    """
    Main endpoint for repository analysis.
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
        
        print(f"Debug: Router got result type: {type(result)}")
        print(f"Debug: Result dict keys: {result.__dict__.keys()}")
        
        # Log success
        logger.info(
            f"Analysis completed for {request.github_url}. "
            f"Analyzed {result.repository.total_files_analyzed} files"
        )
        
        # Return structured format for frontend
        parsed_review = parse_ai_review(result.ai_review)
        
        return {
            "repository": {
                "name": result.repository.name,
                "url": result.repository.url,
                "languages": result.repository.languages,
                "total_files_analyzed": result.repository.total_files_analyzed
            },
            "analysis": {
                "overall_score": parsed_review.get("overall_score", 75),
                "summary": parsed_review.get("summary", "Analysis completed"),
                "strengths": parsed_review.get("strengths", []),
                "improvements": parsed_review.get("improvements", []),
                "code_examples": parsed_review.get("code_examples", {}),
                "final_thoughts": parsed_review.get("final_thoughts", "")
            },
            "raw_review": result.ai_review,  # Keep the original for fallback
            "timestamp": result.timestamp.isoformat()
        }
        
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
async def get_example_request() -> dict:
    """
    Returns an example analysis request for API testing.
    
    **Returns:**
    - Example request payload that can be used with the /analyze endpoint
    """
    return {
        "example_request": {
            "github_url": "https://github.com/octocat/Hello-World",
            "project_description": "Learning basic web development",
            "project_goals": ["understand HTML/CSS", "learn Git basics"],
            "focus_areas": ["code style", "best practices"],
            "experience_level": "beginner"
        },
        "description": "Use this example to test the /api/analyze endpoint",
        "note": "Replace the github_url with a real repository you want to analyze"
    }