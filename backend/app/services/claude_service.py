import os
import json
import httpx
from typing import List, Dict, Any, Optional
import asyncio

from ..models.github import GitHubFile
from ..models.analysis import CodeIssue, IssueType, IssueSeverity
from ..utils.response_formatter import parse_claude_response, calculate_overall_score


class ClaudeService:
    def __init__(self):
        self.api_key = os.getenv("CLAUDE_API_KEY")
        self.base_url = "https://api.anthropic.com/v1/messages"
        
        # Updated models based on your Tier 1 access
        self.models_to_try = [
            "claude-3-5-haiku-20241022",    # Claude Haiku 3.5 (fastest, cheapest)
            "claude-3-haiku-20240307",      # Claude Haiku 3 (backup)
            "claude-3-5-sonnet-20241022",   # Claude Sonnet 3.5/3.7
            "claude-sonnet-4-20250514",     # Claude Sonnet 4 (if available)
        ]
        
        self.model = self.models_to_try[0]  # Start with Haiku 3.5 (most efficient)
        self.max_tokens = 4000
        
        print(f"🔍 Debug: Initializing ClaudeService with model: {self.model}")
        print(f"🔍 Debug: Available models in your tier: Opus 4.x, Sonnet 4, Sonnet 3.7, Haiku 3.5, Haiku 3")
        print(f"🔍 Debug: CLAUDE_API_KEY from env: {'Found' if self.api_key else 'Not found'}")
        if self.api_key:
            print(f"🔍 Debug: API Key preview: {self.api_key[:15]}...")
        
        if not self.api_key:
            print("⚠️  Warning: CLAUDE_API_KEY environment variable is missing")
        else:
            print("✅ Debug: Claude API key loaded successfully")
    
    async def analyze_code(self, files: List[GitHubFile], repository_name: str) -> Dict[str, Any]:
        """
        Send code files to Claude for analysis and return structured results
        """
        if not files:
            raise ValueError("No files provided for analysis")
        
        # Prepare the analysis prompt
        prompt = self._create_analysis_prompt(files, repository_name)
        
        # Call Claude API
        claude_response = await self._call_claude_api(prompt)
        
        # Parse the response
        parsed_response = parse_claude_response(claude_response)
        
        return parsed_response
    
    def _create_analysis_prompt(self, files: List[GitHubFile], repository_name: str) -> str:
        """
        Create a comprehensive analysis prompt for Claude
        """
        # Build file content section
        files_content = []
        for file in files[:15]:  # Limit to prevent token overflow
            content_preview = file.content[:2000] if len(file.content) > 2000 else file.content
            files_content.append(f"""
File: {file.path}
Language: {file.language or 'Unknown'}
Size: {file.size} bytes
Content:
```{file.language or ''}
{content_preview}
```
{'... (content truncated)' if len(file.content) > 2000 else ''}
""")
        
        files_text = "\n".join(files_content)
        
        prompt = f"""You are an expert code reviewer analyzing the repository "{repository_name}". 

Please analyze the following code files and provide a comprehensive code review focusing on:

1. **Security Issues**: Vulnerabilities, unsafe practices, exposed secrets
2. **Performance Issues**: Inefficient algorithms, memory leaks, blocking operations
3. **Maintainability Issues**: Code complexity, lack of documentation, poor structure
4. **Style Issues**: Formatting, naming conventions, code standards
5. **Bugs**: Logic errors, potential runtime errors, edge cases

**Code Files to Analyze:**
{files_text}

**Required Output Format:**
Please respond with a JSON object in this exact structure:

```json
{{
  "analysis_summary": {{
    "total_issues": <number>,
    "security_issues": <number>,
    "performance_issues": <number>,
    "maintainability_issues": <number>,
    "style_issues": <number>,
    "bug_issues": <number>,
    "overall_score": <number 0-100>
  }},
  "detailed_issues": [
    {{
      "file": "<file_path>",
      "line": <line_number_or_null>,
      "type": "<security|performance|maintainability|style|bug>",
      "severity": "<critical|high|medium|low>",
      "message": "<brief_description>",
      "suggestion": "<how_to_fix>",
      "code_snippet": "<problematic_code_or_null>",
      "improved_code": "<suggested_improvement_or_null>"
    }}
  ],
  "file_scores": [
    {{
      "file": "<file_path>",
      "score": <score_0_to_100>,
      "issues_count": <number>
    }}
  ],
  "general_feedback": "<overall_assessment_and_recommendations>"
}}
```

**Guidelines:**
- Focus on actionable feedback with specific line numbers when possible
- Provide code suggestions for improvements
- Consider the overall architecture and patterns used
- Score files based on code quality (100 = perfect, 0 = critical issues)
- Overall score should reflect the repository's general code quality
- Prioritize security and performance issues over style issues
- Be constructive and specific in your suggestions

Analyze the code now and return only the JSON response:"""

        return prompt
    
    async def _call_claude_api(self, prompt: str) -> str:
        """
        Make API call to Claude
        """
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": [
                {
                    "role": "user", 
                    "content": prompt
                }
            ]
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                response_data = response.json()
                
                # Extract content from Claude's response format
                if "content" in response_data and response_data["content"]:
                    return response_data["content"][0]["text"]
                else:
                    raise ValueError("Unexpected response format from Claude API")
                    
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ValueError("Invalid Claude API key")
            elif e.response.status_code == 429:
                raise ValueError("Claude API rate limit exceeded")
            elif e.response.status_code == 400:
                raise ValueError("Invalid request to Claude API")
            else:
                raise ValueError(f"Claude API error: {e.response.status_code}")
        except httpx.RequestError as e:
            raise ValueError(f"Network error calling Claude API: {str(e)}")
    
    def _extract_issues_from_response(self, parsed_response: Dict[str, Any]) -> List[CodeIssue]:
        """
        Convert Claude's response to CodeIssue objects
        """
        issues = []
        
        for issue_data in parsed_response.get("detailed_issues", []):
            try:
                # Map issue type
                issue_type = IssueType(issue_data.get("type", "maintainability"))
                
                # Map severity
                severity = IssueSeverity(issue_data.get("severity", "medium"))
                
                issue = CodeIssue(
                    file=issue_data.get("file", "unknown"),
                    line=issue_data.get("line"),
                    type=issue_type,
                    severity=severity,
                    message=issue_data.get("message", ""),
                    suggestion=issue_data.get("suggestion", ""),
                    code_snippet=issue_data.get("code_snippet"),
                    improved_code=issue_data.get("improved_code")
                )
                issues.append(issue)
                
            except (ValueError, KeyError) as e:
                # Skip malformed issues
                continue
        
        return issues
    
    async def health_check(self) -> bool:
        """
        Check if Claude API is accessible - try multiple models
        """
        if not self.api_key:
            print("❌ Debug: No API key found")
            return False
        
        if not self.api_key.startswith('sk-ant-'):
            print(f"❌ Debug: Invalid API key format: {self.api_key[:12]}...")
            return False
        
        print("✅ Debug: API key format looks good")
        
        # Try each model until one works
        for model in self.models_to_try:
            try:
                print(f"🔍 Debug: Testing model: {model}")
                
                headers = {
                    "Content-Type": "application/json",
                    "X-API-Key": self.api_key,
                    "anthropic-version": "2023-06-01"
                }
                
                payload = {
                    "model": model,
                    "max_tokens": 10,
                    "messages": [{"role": "user", "content": "Hi"}]
                }
                
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(
                        self.base_url,
                        headers=headers,
                        json=payload
                    )
                    
                    print(f"🔍 Debug: Model {model} response status: {response.status_code}")
                    
                    if response.status_code == 200:
                        print(f"✅ Debug: Found working model: {model}")
                        self.model = model  # Update to working model
                        return True
                    else:
                        print(f"❌ Debug: Model {model} failed: {response.text}")
                        continue
                        
            except Exception as e:
                print(f"❌ Debug: Model {model} exception: {e}")
                continue
        
        print("❌ Debug: No working models found")
        return False


# Service instance
claude_service = ClaudeService()