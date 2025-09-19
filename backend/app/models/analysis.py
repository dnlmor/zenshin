from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional
from datetime import datetime

class AnalysisRequest(BaseModel):
    github_url: HttpUrl
    project_description: Optional[str] = Field(None, max_length=1000)
    project_goals: Optional[List[str]] = None
    focus_areas: Optional[List[str]] = None
    experience_level: Optional[str] = None

class Repository(BaseModel):
    name: str
    url: str
    languages: List[str]
    total_files_analyzed: int = Field(..., ge=0)

class AnalysisResult(BaseModel):
    repository: Repository
    ai_review: str = Field(..., description="Clean, formatted review")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }