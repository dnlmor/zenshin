from pydantic import BaseModel, HttpUrl, Field, validator
from typing import List, Optional
from datetime import datetime
from enum import Enum

class IssueType(str, Enum):
    SECURITY = "security"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    STYLE = "style"
    BUG = "bug"

class IssueSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class AnalysisRequest(BaseModel):
    github_url: HttpUrl
    file_types: Optional[List[str]] = Field(
        default=["js", "py", "ts", "tsx", "jsx", "java"],
        description="File extensions to analyze"
    )
    max_files: Optional[int] = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of files to analyze"
    )
    
    @validator('file_types')
    def validate_file_types(cls, v):
        if v and len(v) == 0:
            return ["js", "py", "ts", "tsx", "jsx", "java"]
        return v

class CodeIssue(BaseModel):
    file: str
    line: Optional[int] = Field(None, ge=1)
    type: IssueType
    severity: IssueSeverity
    message: str = Field(..., min_length=1, max_length=500)
    suggestion: str = Field(..., min_length=1, max_length=1000)
    code_snippet: Optional[str] = Field(None, max_length=2000)
    improved_code: Optional[str] = Field(None, max_length=2000)

class FileBreakdown(BaseModel):
    file: str
    issues_count: int = Field(..., ge=0)
    score: int = Field(..., ge=0, le=100, description="Code quality score (0-100)")
    languages: List[str]

class Repository(BaseModel):
    name: str
    url: str
    languages: List[str]
    total_files_analyzed: int = Field(..., ge=0)

class AnalysisSummary(BaseModel):
    total_issues: int = Field(..., ge=0)
    critical_issues: int = Field(..., ge=0)
    security_issues: int = Field(..., ge=0)
    performance_issues: int = Field(..., ge=0)
    maintainability_issues: int = Field(default=0, ge=0)
    style_issues: int = Field(..., ge=0)
    bug_issues: int = Field(default=0, ge=0)
    overall_score: int = Field(..., ge=0, le=100, description="Overall repository score")

class AnalysisResult(BaseModel):
    repository: Repository
    analysis: dict  # Keep flexible for Claude's raw response
    summary: AnalysisSummary
    issues: List[CodeIssue]
    file_breakdown: List[FileBreakdown]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }