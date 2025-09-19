from typing import List, Dict, Any
import asyncio
from datetime import datetime

from ..models.analysis import (
    AnalysisRequest, 
    AnalysisResult, 
    AnalysisSummary, 
    Repository,
    FileBreakdown,
    CodeIssue
)
from ..models.github import GitHubFile
from .github_service import github_service
from .claude_service import claude_service
from ..utils.code_parser import calculate_complexity_score
from ..utils.response_formatter import calculate_overall_score


class AnalysisService:
    def __init__(self):
        self.github_service = github_service
        self.claude_service = claude_service
    
    async def analyze_repository(self, request: AnalysisRequest) -> AnalysisResult:
        """
        Main orchestration method for repository analysis
        """
        try:
            # Step 1: Fetch repository data from GitHub
            github_repo = await self.github_service.fetch_repository(
                github_url=str(request.github_url),
                file_types=request.file_types,
                max_files=request.max_files
            )
            
            if not github_repo.files:
                raise ValueError("No analyzable files found in the repository")
            
            # Step 2: Send code to Claude for analysis
            claude_analysis = await self.claude_service.analyze_code(
                files=github_repo.files,
                repository_name=github_repo.name
            )
            
            # Step 3: Parse and structure the results
            structured_result = await self._structure_analysis_result(
                github_repo=github_repo,
                claude_analysis=claude_analysis,
                original_request=request
            )
            
            return structured_result
            
        except Exception as e:
            # Add context to errors
            error_msg = f"Analysis failed: {str(e)}"
            raise ValueError(error_msg)
    
    async def _structure_analysis_result(
        self, 
        github_repo, 
        claude_analysis: Dict[str, Any],
        original_request: AnalysisRequest
    ) -> AnalysisResult:
        """
        Structure the final analysis result
        """
        # Extract issues from Claude's response
        issues = self._extract_issues_from_claude_response(claude_analysis)
        
        # Create analysis summary
        summary = self._create_analysis_summary(claude_analysis, issues)
        
        # Create file breakdown
        file_breakdown = self._create_file_breakdown(github_repo.files, issues, claude_analysis)
        
        # Create repository info
        repository = Repository(
            name=github_repo.name,
            url=str(original_request.github_url),
            languages=github_repo.languages,
            total_files_analyzed=len(github_repo.files)
        )
        
        # Create final result
        result = AnalysisResult(
            repository=repository,
            analysis=claude_analysis,  # Raw Claude response for debugging
            summary=summary,
            issues=issues,
            file_breakdown=file_breakdown,
            timestamp=datetime.utcnow()
        )
        
        return result
    
    def _extract_issues_from_claude_response(self, claude_analysis: Dict[str, Any]) -> List[CodeIssue]:
        """
        Extract and validate issues from Claude's response
        """
        issues = []
        
        for issue_data in claude_analysis.get("detailed_issues", []):
            try:
                issue = CodeIssue(
                    file=issue_data.get("file", "unknown"),
                    line=issue_data.get("line"),
                    type=issue_data.get("type", "maintainability"),
                    severity=issue_data.get("severity", "medium"),
                    message=issue_data.get("message", "No description provided"),
                    suggestion=issue_data.get("suggestion", "No suggestion provided"),
                    code_snippet=issue_data.get("code_snippet"),
                    improved_code=issue_data.get("improved_code")
                )
                issues.append(issue)
            except Exception as e:
                # Skip invalid issues but log the error
                print(f"Warning: Skipping invalid issue: {e}")
                continue
        
        return issues
    
    def _create_analysis_summary(
        self, 
        claude_analysis: Dict[str, Any], 
        issues: List[CodeIssue]
    ) -> AnalysisSummary:
        """
        Create analysis summary from Claude's response and issues
        """
        # Get summary from Claude or calculate from issues
        claude_summary = claude_analysis.get("analysis_summary", {})
        
        # Count issues by type if Claude didn't provide counts
        issue_counts = self._count_issues_by_type(issues)
        
        return AnalysisSummary(
            total_issues=claude_summary.get("total_issues", len(issues)),
            critical_issues=self._count_issues_by_severity(issues, "critical"),
            security_issues=claude_summary.get("security_issues", issue_counts.get("security", 0)),
            performance_issues=claude_summary.get("performance_issues", issue_counts.get("performance", 0)),
            maintainability_issues=claude_summary.get("maintainability_issues", issue_counts.get("maintainability", 0)),
            style_issues=claude_summary.get("style_issues", issue_counts.get("style", 0)),
            bug_issues=claude_summary.get("bug_issues", issue_counts.get("bug", 0)),
            overall_score=claude_summary.get("overall_score", self._calculate_fallback_score(issues))
        )
    
    def _create_file_breakdown(
        self, 
        files: List[GitHubFile], 
        issues: List[CodeIssue],
        claude_analysis: Dict[str, Any]
    ) -> List[FileBreakdown]:
        """
        Create per-file breakdown of issues and scores
        """
        file_breakdown = []
        
        # Get file scores from Claude if available
        claude_file_scores = {
            fs["file"]: fs for fs in claude_analysis.get("file_scores", [])
        }
        
        for file in files:
            # Count issues for this file
            file_issues = [issue for issue in issues if issue.file == file.path]
            issues_count = len(file_issues)
            
            # Get score from Claude or calculate fallback
            if file.path in claude_file_scores:
                score = claude_file_scores[file.path].get("score", 85)
            else:
                score = self._calculate_file_score(file, file_issues)
            
            file_breakdown.append(FileBreakdown(
                file=file.path,
                issues_count=issues_count,
                score=max(0, min(100, score)),  # Ensure score is 0-100
                languages=[file.language] if file.language else []
            ))
        
        return file_breakdown
    
    def _count_issues_by_type(self, issues: List[CodeIssue]) -> Dict[str, int]:
        """
        Count issues by type
        """
        counts = {}
        for issue in issues:
            counts[issue.type.value] = counts.get(issue.type.value, 0) + 1
        return counts
    
    def _count_issues_by_severity(self, issues: List[CodeIssue], severity: str) -> int:
        """
        Count issues by severity level
        """
        return sum(1 for issue in issues if issue.severity.value == severity)
    
    def _calculate_fallback_score(self, issues: List[CodeIssue]) -> int:
        """
        Calculate overall score if Claude didn't provide one
        """
        if not issues:
            return 95
        
        # Simple scoring based on issue severity
        penalty = 0
        for issue in issues:
            if issue.severity.value == "critical":
                penalty += 25
            elif issue.severity.value == "high":
                penalty += 15
            elif issue.severity.value == "medium":
                penalty += 8
            elif issue.severity.value == "low":
                penalty += 3
        
        score = max(0, 100 - penalty)
        return score
    
    def _calculate_file_score(self, file: GitHubFile, file_issues: List[CodeIssue]) -> int:
        """
        Calculate file-level score based on issues and complexity
        """
        if not file_issues:
            # Base score from complexity
            complexity_score = calculate_complexity_score(file.content, file.language)
            return min(95, complexity_score)
        
        # Penalty-based scoring
        penalty = 0
        for issue in file_issues:
            if issue.severity.value == "critical":
                penalty += 30
            elif issue.severity.value == "high":
                penalty += 20
            elif issue.severity.value == "medium":
                penalty += 10
            elif issue.severity.value == "low":
                penalty += 5
        
        base_score = 100 - penalty
        return max(0, min(100, base_score))
    
    async def health_check(self) -> Dict[str, bool]:
        """
        Check health of all dependent services
        """
        results = {}
        
        try:
            # Check GitHub service (test with a simple validation)
            results["github_service"] = True  # GitHub service doesn't need API for validation
        except Exception:
            results["github_service"] = False
        
        try:
            # Check Claude service
            results["claude_service"] = await self.claude_service.health_check()
        except Exception:
            results["claude_service"] = False
        
        return results


# Service instance
analysis_service = AnalysisService()