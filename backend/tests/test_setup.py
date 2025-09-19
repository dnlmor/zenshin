import os
from dotenv import load_dotenv
import asyncio
from app.services.github_service import GitHubService

async def test_setup():
    load_dotenv()
    
    # Test environment variables
    print("Testing environment variables...")
    claude_key = os.getenv("CLAUDE_API_KEY")
    github_token = os.getenv("GITHUB_TOKEN") 
    
    if claude_key and github_token:
        print("✅ Environment variables loaded")
    else:
        print("❌ Missing environment variables")
        return
    
    # Test GitHub service
    print("\nTesting GitHub service...")
    github_service = GitHubService()
    
    try:
        # Test with a simple public repository
        repo = await github_service.get_repository(
            "https://github.com/octocat/Hello-World", 
            ["md", "txt"], 
            5
        )
        print(f"✅ GitHub service working: {repo.name}")
    except Exception as e:
        print(f"❌ GitHub service error: {e}")

if __name__ == "__main__":
    asyncio.run(test_setup())