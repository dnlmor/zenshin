# Zenshin - AI Code Review Assistant

A modern, full-stack web application that provides intelligent code reviews for GitHub repositories using Claude AI. Built as a portfolio project to demonstrate full-stack development skills.

## Features

- **AI-Powered Code Analysis**: Uses Claude AI to analyze code quality, security, performance, and maintainability
- **GitHub Integration**: Automatically fetches and analyzes files from any public GitHub repository
- **Structured Feedback**: Provides detailed insights with strengths, improvements, and actionable recommendations
- **Modern UI**: Clean, responsive design with glassmorphism effects and smooth animations
- **Real-time Progress**: Live progress tracking during analysis with loading animations
- **Code Examples**: Before/after code comparisons with syntax highlighting
- **Context-Aware**: Tailors feedback based on developer experience level and project goals

## Tech Stack

### Backend
- **Python FastAPI** - Modern, fast web framework
- **Claude AI API** - Advanced AI code analysis
- **GitHub API** - Repository data fetching
- **Pydantic** - Data validation and serialization
- **Async/Await** - High-performance concurrent operations

### Frontend
- **React 18** - Modern UI library with hooks
- **TypeScript** - Type-safe development
- **Tailwind CSS v3** - Utility-first styling
- **Vite** - Fast build tooling
- **Lucide React** - Beautiful icons

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 18+
- Claude API key from [Anthropic](https://console.anthropic.com/)
- GitHub Personal Access Token (optional, for higher rate limits)

### Backend Setup

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd zenshin
```

2. **Set up Python environment**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
```

Edit `.env` with your API keys:
```env
CLAUDE_API_KEY=your_claude_api_key_here
GITHUB_TOKEN=your_github_token_here  # Optional but recommended
```

4. **Start the backend server**
```bash
python run.py
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Install dependencies**
```bash
cd frontend
npm install
```

2. **Start the development server**
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## API Documentation

### Endpoints

#### `POST /api/analyze`
Analyze a GitHub repository

**Request:**
```json
{
  "github_url": "https://github.com/username/repository",
  "project_description": "Description of the project",
  "project_goals": ["goal1", "goal2"],
  "focus_areas": ["security", "performance"],
  "experience_level": "intermediate"
}
```

**Response:**
```json
{
  "repository": {
    "name": "repository-name",
    "url": "https://github.com/username/repository",
    "languages": ["Python", "JavaScript"],
    "total_files_analyzed": 15
  },
  "analysis": {
    "overall_score": 87,
    "summary": "High-quality codebase with good practices...",
    "strengths": [
      {
        "title": "Code Structure",
        "description": "Well-organized and maintainable..."
      }
    ],
    "improvements": [
      {
        "title": "Error Handling",
        "score": "7/10",
        "issue": "Some functions lack proper error handling",
        "action": "Add try-catch blocks for external API calls"
      }
    ],
    "code_examples": {
      "before": "// Current code",
      "after": "// Improved code"
    },
    "final_thoughts": "Overall excellent work..."
  },
  "timestamp": "2025-09-20T..."
}
```

#### `GET /api/health`
Check service health status

#### `GET /api/analyze/example`
Get example request format

## Project Structure

```
zenshin/
├── backend/
│   ├── app/
│   │   ├── models/          # Pydantic data models
│   │   ├── services/        # Business logic services
│   │   ├── routers/         # API route handlers
│   │   ├── utils/           # Utility functions
│   │   └── main.py          # FastAPI application
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── hooks/           # Custom React hooks
│   │   ├── services/        # API integration
│   │   ├── types/           # TypeScript interfaces
│   │   └── utils/           # Utility functions
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## Architecture

### Backend Architecture
- **Stateless Design**: No database required, processes requests independently
- **Service Layer**: Clean separation between GitHub API, Claude AI, and business logic
- **Auto-Detection**: Automatically detects relevant file types and languages
- **Error Handling**: Comprehensive error handling with detailed user feedback
- **Rate Limiting**: Built-in protection against API abuse

### Frontend Architecture
- **Component-Based**: Modular React components for reusability
- **Custom Hooks**: Business logic separated from UI components
- **Type Safety**: Full TypeScript coverage for reliable development
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Progressive Loading**: Real-time feedback during analysis process

## Deployment

### Backend Deployment (Railway/Render)

1. **Create deployment service**
2. **Set environment variables**
3. **Deploy from repository**

### Frontend Deployment (Vercel/Netlify)

1. **Build the project**
```bash
npm run build
```

2. **Deploy build folder**
3. **Configure API proxy for production**

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development Workflow

### Adding New Features

1. **Backend**: Add new endpoints in `routers/`, business logic in `services/`
2. **Frontend**: Create components in `components/`, add types in `types/`
3. **Integration**: Update API service and add proper error handling

### Code Quality

- **Backend**: Follow PEP 8, use type hints, write docstrings
- **Frontend**: Use TypeScript strict mode, follow React best practices
- **Testing**: Add unit tests for critical functionality

## Troubleshooting

### Common Issues

**Backend not starting:**
- Check Python version (3.8+ required)
- Verify API keys are set correctly
- Check port 8000 is not in use

**Frontend build errors:**
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check Node.js version (18+ required)
- Verify TypeScript configuration

**API connection issues:**
- Ensure backend is running on port 8000
- Check CORS configuration
- Verify proxy settings in vite.config.ts

## Performance Considerations

- **File Limits**: Analysis limited to 30 files maximum for performance
- **Caching**: Consider implementing Redis for repeated repository analysis
- **Rate Limiting**: Respect GitHub and Claude API rate limits
- **Concurrency**: Backend uses async operations for optimal performance

## Security

- **API Keys**: Never commit API keys to version control
- **Input Validation**: All inputs validated on both frontend and backend
- **CORS**: Configured for specific origins in production
- **Error Handling**: Sensitive information never exposed in error messages

## Acknowledgments

- **Claude AI** by Anthropic for intelligent code analysis
- **GitHub API** for repository data access
- **React** and **FastAPI** communities for excellent documentation
- **Tailwind CSS** for the utility-first styling approach

---

**Built by dnlmor** 