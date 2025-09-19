import os
import json
import httpx
from typing import List, Dict, Any, Optional
import asyncio

from ..models.github import GitHubFile


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
    
    async def analyze_code(self, files: List[GitHubFile], repository_name: str, context: Dict = None) -> str:
        """
        Send code files to Claude for analysis and return clean formatted review
        """
        if not files:
            raise ValueError("No files provided for analysis")
        
        # Prepare the analysis prompt
        prompt = self._create_analysis_prompt(files, repository_name, context)
        
        # Call Claude API and return the formatted response directly
        claude_response = await self._call_claude_api(prompt)
        
        return claude_response
    
    def _create_analysis_prompt(self, files: List[GitHubFile], repository_name: str, context: Dict = None) -> str:
        """
        Create a prompt for Claude to generate clean, actionable code review
        """
        # Build file content section
        files_content = []
        for file in files[:15]:  # Reasonable limit
            content_preview = file.content[:2500] if len(file.content) > 2500 else file.content
            files_content.append(f"""
**File: {file.path}** ({file.language or 'Unknown'})
```{file.language or ''}
{content_preview}
```
""")
        
        files_text = "\n".join(files_content)
        
        # Build context section
        context_section = ""
        if context:
            context_parts = []
            if context.get('project_description'):
                context_parts.append(f"**Project:** {context['project_description']}")
            if context.get('experience_level'):
                context_parts.append(f"**Developer Level:** {context['experience_level']}")
            if context.get('focus_areas'):
                focus = ", ".join(context['focus_areas'])
                context_parts.append(f"**Focus Areas:** {focus}")
            
            if context_parts:
                context_section = f"""
## CONTEXT:
{chr(10).join(context_parts)}
"""

        prompt = f"""You are a friendly code reviewer providing actionable feedback for the "{repository_name}" repository. 

{context_section}

## YOUR TASK:
Provide a clean, encouraging code review in the EXACT format below. Be specific but not overwhelming.

## CODE TO REVIEW:
{files_text}

## REQUIRED FORMAT:
Write your response exactly like this template:

**Overall Score: [XX]/100 (Grade)**
[One sentence summary of the code quality]

**What's Good:**
* **[Strength 1]**: [Why it's good and why it matters]
* **[Strength 2]**: [Explanation]
* **[Strength 3]**: [Explanation]

**What Can Be Improved:**

1. **[Issue Area] ([X]/10):**
   * **Issue**: [Specific problem you found]
   * **Action**: [Concrete step to fix it]

2. **[Issue Area] ([X]/10):**
   * **Issue**: [Specific problem you found]
   * **Action**: [Concrete step to fix it]

3. **[Issue Area] ([X]/10):**
   * **Issue**: [Specific problem you found]
   * **Action**: [Concrete step to fix it]

**Code Sample (if applicable):**

**Before:**
```[language]
[problematic code from their actual files]
```

**After:**
```[language]
[improved version]
```

**Final Thoughts:**
[Encouraging closing message about their progress and next steps]

## GUIDELINES:
- Be encouraging and constructive
- Focus on 2-4 key improvement areas maximum
- Use their actual code in examples when possible
- Give specific, actionable advice
- Adjust complexity based on their experience level
- End on a positive, motivating note
- Use the EXACT format structure shown above

Analyze the code and provide your review in this format:"""

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
    
    def _extract_issues_from_response(self, parsed_response: Dict[str, Any]) -> List[Dict]:
        """
        Convert Claude's response to simple issue dictionaries (not used in simplified version)
        """
        return parsed_response.get("detailed_issues", [])
    
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