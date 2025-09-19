import os
import base64
import httpx
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse
import asyncio

from ..models.github import GitHubRepository, GitHubFile
from ..utils.validators import validate_github_url
from ..utils.code_parser import detect_language, is_supported_file


class GitHubService:
    def __init__(self):
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        if self.github_token:
            self.headers["Authorization"] = f"Bearer {self.github_token}"
    
    async def fetch_repository(self, github_url: str) -> GitHubRepository:
        """
        Fetch repository data from GitHub API with intelligent file detection
        """
        # Validate and parse GitHub URL
        if not validate_github_url(github_url):
            raise ValueError("Invalid GitHub repository URL")
        
        owner, repo = self._parse_github_url(github_url)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Get repository info
            repo_info = await self._get_repository_info(client, owner, repo)
            
            # Get repository languages to determine what to analyze
            languages = await self._get_repository_languages(client, owner, repo)
            
            # Auto-detect file types based on repository languages
            file_types = self._detect_relevant_file_types(languages)
            
            # Smart file limit - keep reasonable for API performance
            max_files = min(20, max(10, len(languages) * 3))
            
            # Get repository contents
            files = await self._get_repository_files(
                client, owner, repo, file_types, max_files, repo_info["default_branch"]
            )
            
            return GitHubRepository(
                name=repo,
                full_name=repo_info["full_name"],
                description=repo_info.get("description"),
                languages=list(languages.keys()),
                files=files,
                default_branch=repo_info["default_branch"]
            )
    
    def _detect_relevant_file_types(self, languages: Dict[str, int]) -> List[str]:
        """
        Auto-detect relevant file types based on repository languages
        """
        language_to_extensions = {
            'Python': ['py', 'pyw'],
            'JavaScript': ['js', 'mjs'],
            'TypeScript': ['ts', 'tsx'],
            'Java': ['java'],
            'C++': ['cpp', 'cc', 'cxx', 'h', 'hpp'],
            'C': ['c', 'h'],
            'C#': ['cs'],
            'PHP': ['php'],
            'Ruby': ['rb'],
            'Go': ['go'],
            'Rust': ['rs'],
            'Swift': ['swift'],
            'Kotlin': ['kt'],
            'Scala': ['scala'],
            'HTML': ['html', 'htm'],
            'CSS': ['css', 'scss', 'sass'],
            'Shell': ['sh', 'bash'],
            'PowerShell': ['ps1'],
        }
        
        file_types = set()
        
        for language in languages.keys():
            if language in language_to_extensions:
                file_types.update(language_to_extensions[language])
        
        # Always include common config/doc files
        file_types.update(['json', 'yaml', 'yml', 'md', 'txt'])
        
        # If no specific languages detected, use common web/general files
        if not file_types:
            file_types = ['py', 'js', 'ts', 'java', 'cpp', 'c', 'go', 'rs', 'md', 'json']
        
        return list(file_types)
    
    def _calculate_optimal_file_limit(self, languages: Dict[str, int]) -> int:
        """
        Calculate optimal number of files to analyze based on repository complexity
        """
        # Base limit
        base_limit = 15
        
        # Adjust based on number of languages (more languages = more files needed)
        language_bonus = min(10, len(languages) * 2)
        
        # Cap at reasonable limit for API performance
        return min(30, base_limit + language_bonus)
    
    def _parse_github_url(self, github_url: str) -> tuple[str, str]:
        """
        Parse GitHub URL to extract owner and repository name
        """
        parsed = urlparse(github_url)
        path_parts = parsed.path.strip('/').split('/')
        
        if len(path_parts) < 2:
            raise ValueError("Invalid GitHub URL format")
        
        owner = path_parts[0]
        repo = path_parts[1]
        
        return owner, repo
    
    async def _get_repository_info(self, client: httpx.AsyncClient, owner: str, repo: str) -> Dict[str, Any]:
        """
        Get basic repository information
        """
        url = f"{self.base_url}/repos/{owner}/{repo}"
        
        try:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ValueError(f"Repository {owner}/{repo} not found")
            elif e.response.status_code == 403:
                raise ValueError("GitHub API rate limit exceeded or access denied")
            else:
                raise ValueError(f"Failed to fetch repository info: {e.response.status_code}")
        except httpx.RequestError as e:
            raise ValueError(f"Network error while fetching repository: {str(e)}")
    
    async def _get_repository_languages(self, client: httpx.AsyncClient, owner: str, repo: str) -> Dict[str, int]:
        """
        Get repository programming languages
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/languages"
        
        try:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError:
            # If languages endpoint fails, return empty dict
            return {}
        except httpx.RequestError:
            return {}
    
    async def _get_repository_files(
        self, 
        client: httpx.AsyncClient, 
        owner: str, 
        repo: str, 
        file_types: List[str], 
        max_files: int,
        branch: str = "main"
    ) -> List[GitHubFile]:
        """
        Get repository files recursively
        """
        files = []
        
        try:
            # Get repository tree
            tree_url = f"{self.base_url}/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
            response = await client.get(tree_url, headers=self.headers)
            response.raise_for_status()
            tree_data = response.json()
            
            # Filter for supported files
            supported_files = []
            for item in tree_data.get("tree", []):
                if item["type"] == "blob":  # Only files, not directories
                    if is_supported_file(item["path"], file_types):
                        supported_files.append(item)
            
            # Limit number of files
            supported_files = supported_files[:max_files]
            
            # Fetch file contents concurrently (but limit concurrency)
            semaphore = asyncio.Semaphore(5)  # Max 5 concurrent requests
            tasks = [
                self._fetch_file_content(client, owner, repo, file_info, semaphore)
                for file_info in supported_files
            ]
            
            files = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out failed requests
            files = [f for f in files if isinstance(f, GitHubFile)]
            
            return files
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                # Try with 'master' branch if 'main' fails
                if branch == "main":
                    return await self._get_repository_files(
                        client, owner, repo, file_types, max_files, "master"
                    )
                else:
                    raise ValueError(f"Repository tree not found for branch {branch}")
            else:
                raise ValueError(f"Failed to fetch repository files: {e.response.status_code}")
        except httpx.RequestError as e:
            raise ValueError(f"Network error while fetching files: {str(e)}")
    
    async def _fetch_file_content(
        self, 
        client: httpx.AsyncClient, 
        owner: str, 
        repo: str, 
        file_info: Dict[str, Any],
        semaphore: asyncio.Semaphore
    ) -> Optional[GitHubFile]:
        """
        Fetch individual file content
        """
        async with semaphore:
            try:
                # Get file content via blob API
                blob_url = f"{self.base_url}/repos/{owner}/{repo}/git/blobs/{file_info['sha']}"
                response = await client.get(blob_url, headers=self.headers)
                response.raise_for_status()
                blob_data = response.json()
                
                # Decode base64 content
                if blob_data.get("encoding") == "base64":
                    try:
                        content = base64.b64decode(blob_data["content"]).decode('utf-8')
                    except (UnicodeDecodeError, ValueError):
                        # Skip binary files or files with encoding issues
                        return None
                else:
                    content = blob_data.get("content", "")
                
                # Skip very large files (>1MB)
                if len(content.encode('utf-8')) > 1024 * 1024:
                    return None
                
                return GitHubFile(
                    name=file_info["path"].split("/")[-1],
                    path=file_info["path"],
                    content=content,
                    language=detect_language(file_info["path"]),
                    size=file_info["size"]
                )
                
            except (httpx.HTTPStatusError, httpx.RequestError, ValueError, UnicodeDecodeError):
                # Skip files that can't be fetched
                return None


# Service instance
github_service = GitHubService()