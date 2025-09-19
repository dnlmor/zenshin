"""
Routers package for the AI Code Review Assistant.

This package contains all the API route handlers:
- AnalysisRouter: Main endpoint for repository analysis and health checks
"""

from .analysis import router as analysis_router

__all__ = ["analysis_router"]