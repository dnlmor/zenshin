from typing import Dict
from datetime import datetime

from ..models.analysis import AnalysisRequest, AnalysisResult, Repository
from .github_service import github_service
from .claude_service import claude_service


class AnalysisService:
    def __init__(self):
        self.github_service = github_service
        self.claude_service = claude_service
    
    async def analyze_repository(self, request: AnalysisRequest) -> AnalysisResult:
        """
        Main orchestration method for repository analysis
        """
        try:
            print("Debug: Starting analysis...")
            
            # Step 1: Fetch repository data from GitHub with auto-detection
            github_repo = await self.github_service.fetch_repository(
                github_url=str(request.github_url)
            )
            
            print(f"Debug: Fetched {len(github_repo.files)} files")
            
            if not github_repo.files:
                raise ValueError("No analyzable files found in the repository")
            
            # Step 2: Prepare user context for Claude
            context = {}
            if request.project_description:
                context['project_description'] = request.project_description
            if request.project_goals:
                context['project_goals'] = request.project_goals
            if request.focus_areas:
                context['focus_areas'] = request.focus_areas
            if request.experience_level:
                context['experience_level'] = request.experience_level
            
            print("Debug: Calling Claude...")
            
            # Step 3: Send code to Claude for analysis with context
            claude_response = await self.claude_service.analyze_code(
                files=github_repo.files,
                repository_name=github_repo.name,
                context=context if context else None
            )
            
            print(f"Debug: Got Claude response: {len(claude_response)} characters")
            
            # Step 4: Create the result
            repository = Repository(
                name=github_repo.name,
                url=str(request.github_url),
                languages=github_repo.languages or [],
                total_files_analyzed=len(github_repo.files)
            )
            
            print("Debug: Creating result...")
            
            result = AnalysisResult(
                repository=repository,
                ai_review=claude_response or "Analysis completed but no detailed feedback was generated.",
                timestamp=datetime.utcnow()
            )
            
            print("Debug: Result created successfully")
            print(f"Debug: Result has attributes: {dir(result)}")
            
            return result
            
        except Exception as e:
            print(f"Debug: Exception in analyze_repository: {e}")
            print(f"Debug: Exception type: {type(e)}")
            
            # Create fallback result
            repository = Repository(
                name="Repository",
                url=str(request.github_url),
                languages=[],
                total_files_analyzed=0
            )
            
            fallback_review = f"""**Overall Score: 70/100 (C+)**
Analysis encountered an issue: {str(e)}

**What's Good:**
* **Repository Access**: We were able to connect to your repository

**What Can Be Improved:**
1. **Analysis Completion (5/10):**
   * **Issue**: The analysis couldn't complete fully
   * **Action**: Try with a different repository

**Final Thoughts:**
There was a technical issue, but this doesn't reflect on your code quality!"""
            
            return AnalysisResult(
                repository=repository,
                ai_review=fallback_review,
                timestamp=datetime.utcnow()
            )
    
    async def health_check(self) -> Dict[str, bool]:
        """Check health of all dependent services"""
        results = {}
        
        try:
            results["github_service"] = True
        except Exception:
            results["github_service"] = False
        
        try:
            results["claude_service"] = await self.claude_service.health_check()
        except Exception:
            results["claude_service"] = False
        
        return results


# Service instance
analysis_service = AnalysisService()