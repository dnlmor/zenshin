# File Structure

    backend/
    ├── venv/                           # Virtual environment (created by python -m venv)
    ├── app/
    │   ├── __init__.py                 # Package initialization
    │   ├── main.py                     # FastAPI application entry point
    │   │
    │   ├── models/
    │   │   ├── __init__.py             # Models package initialization
    │   │   ├── analysis.py             # Analysis request/response models
    │   │   └── github.py               # GitHub API response models
    │   │
    │   ├── services/
    │   │   ├── __init__.py             # Services package initialization
    │   │   ├── github_service.py       # GitHub API integration service
    │   │   ├── claude_service.py       # Claude API integration service
    │   │   └── analysis_service.py     # Main analysis orchestration service
    │   │
    │   ├── routers/
    │   │   ├── __init__.py             # Routers package initialization
    │   │   └── analysis.py             # Analysis endpoints router
    │   │
    │   └── utils/
    │       ├── __init__.py             # Utils package initialization
    │       ├── code_parser.py          # Code parsing and language detection utilities
    │       ├── response_formatter.py   # Format API responses
    │       └── validators.py           # Input validation utilities
    │
    ├── tests/                          # Test directory (optional for MVP)
    │   ├── __init__.py
    │   ├── test_github_service.py
    │   ├── test_claude_service.py
    │   └── test_analysis.py
    │
    ├── .env                            # Environment variables (not committed to git)
    ├── .env.example                    # Environment variables template
    ├── .gitignore                      # Git ignore file
    ├── requirements.txt                # Python dependencies
    ├── test_setup.py                   # Setup verification script
    ├── README.md                       # Backend documentation