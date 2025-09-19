from pydantic import BaseModel, Field, validator
from typing import List, Optional

class GitHubFile(BaseModel):
    name: str
    path: str
    content: str = Field(..., description="Base64 decoded file content")
    language: Optional[str] = None
    size: int = Field(..., ge=0, description="File size in bytes")
    
    @validator('size')
    def validate_file_size(cls, v):
        max_size = 1024 * 1024  # 1MB limit
        if v > max_size:
            raise ValueError(f'File size {v} exceeds maximum allowed size of {max_size} bytes')
        return v

class GitHubRepository(BaseModel):
    name: str
    full_name: str = Field(..., description="Owner/repository format")
    description: Optional[str] = None
    languages: List[str] = Field(default_factory=list)
    files: List[GitHubFile]
    default_branch: str = Field(default="main")
    
    @validator('files')
    def validate_files_not_empty(cls, v):
        if not v:
            raise ValueError('Repository must contain at least one file')
        return v