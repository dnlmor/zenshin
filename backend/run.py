#!/usr/bin/env python3
"""
Development server runner for AI Code Review Assistant

Usage:
    python run.py              # Start development server
    python run.py --prod       # Start production server
    python run.py --help       # Show help
"""

import argparse
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Debug: Print if API key is loaded (don't print full key for security)
claude_key = os.getenv("CLAUDE_API_KEY")
github_token = os.getenv("GITHUB_TOKEN")

print(f"🔑 Claude API Key loaded: {'Yes' if claude_key else 'No'}")
print(f"🔑 GitHub Token loaded: {'Yes' if github_token else 'No'}")

if claude_key:
    print(f"🔑 Claude API Key format: {claude_key[:12]}...")


def main():
    parser = argparse.ArgumentParser(description="AI Code Review Assistant Backend Server")
    parser.add_argument(
        "--prod", 
        action="store_true", 
        help="Run in production mode"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=int(os.getenv("PORT", 8000)),
        help="Port to run server on"
    )
    parser.add_argument(
        "--host", 
        default=os.getenv("HOST", "0.0.0.0"),
        help="Host to bind server to"
    )
    
    args = parser.parse_args()
    
    if args.prod:
        # Production configuration
        print("🚀 Starting AI Code Review Assistant in PRODUCTION mode...")
        uvicorn.run(
            "app.main:app",
            host=args.host,
            port=args.port,
            workers=4,
            log_level="warning"
        )
    else:
        # Development configuration
        print("🔧 Starting AI Code Review Assistant in DEVELOPMENT mode...")
        print(f"📡 Server will be available at http://{args.host}:{args.port}")
        print("📚 API documentation at http://localhost:8000/docs")
        print("🔍 Health check at http://localhost:8000/api/health")
        
        uvicorn.run(
            "app.main:app",
            host=args.host,
            port=args.port,
            reload=True,
            log_level="info"
        )

if __name__ == "__main__":
    main()