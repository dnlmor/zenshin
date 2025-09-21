import { FocusArea, ExperienceLevel, RepositoryForm } from '@/types';

// App Configuration
export const APP_CONFIG = {
  name: 'AI Code Review Assistant',
  description: 'Get intelligent code reviews powered by AI',
  version: '1.0.0',
  author: 'Daniel',
} as const;

// API Configuration
export const API_CONFIG = {
  timeout: 60000, // 60 seconds for analysis
  retryAttempts: 3,
  retryDelay: 1000,
} as const;

// Form Options
export const EXPERIENCE_LEVELS: { value: ExperienceLevel; label: string }[] = [
  { value: '', label: 'Select your level' },
  { value: 'beginner', label: 'Beginner' },
  { value: 'intermediate', label: 'Intermediate' },
  { value: 'advanced', label: 'Advanced' },
];

export const FOCUS_AREAS: { value: FocusArea; label: string; description: string }[] = [
  {
    value: 'security',
    label: 'Security',
    description: 'Focus on security vulnerabilities and best practices',
  },
  {
    value: 'performance',
    label: 'Performance',
    description: 'Identify performance bottlenecks and optimizations',
  },
  {
    value: 'maintainability',
    label: 'Maintainability',
    description: 'Code structure, readability, and maintainability',
  },
  {
    value: 'style',
    label: 'Code Style',
    description: 'Formatting, naming conventions, and style guidelines',
  },
  {
    value: 'testing',
    label: 'Testing',
    description: 'Test coverage and testing best practices',
  },
];

// Score Thresholds
export const SCORE_THRESHOLDS = {
  excellent: 90,
  good: 80,
  fair: 70,
  poor: 60,
} as const;

// Score Colors for UI
export const SCORE_COLORS = {
  excellent: 'text-green-600 bg-green-50 border-green-200',
  good: 'text-blue-600 bg-blue-50 border-blue-200',
  fair: 'text-yellow-600 bg-yellow-50 border-yellow-200',
  poor: 'text-red-600 bg-red-50 border-red-200',
} as const;

// URL Validation
export const GITHUB_URL_PATTERN = /^https:\/\/github\.com\/[a-zA-Z0-9._-]+\/[a-zA-Z0-9._-]+\/?$/;

// Default Form Values
export const DEFAULT_FORM_VALUES: RepositoryForm = {
  url: '',
  description: '',
  goals: [],
  focusAreas: [],
  experienceLevel: '',
};

// Loading Messages
export const LOADING_MESSAGES = [
  'Analyzing your repository...',
  'Fetching code files...',
  'Running AI analysis...',
  'Generating insights...',
  'Almost done...',
] as const;

// Error Messages
export const ERROR_MESSAGES = {
  invalidUrl: 'Please enter a valid GitHub repository URL',
  networkError: 'Unable to connect to the server. Please check your connection.',
  serverError: 'Server error occurred. Please try again later.',
  timeoutError: 'Analysis took too long. Please try again.',
  unknownError: 'An unexpected error occurred. Please try again.',
} as const;

// Success Messages
export const SUCCESS_MESSAGES = {
  analysisComplete: 'Analysis completed successfully!',
  dataLoaded: 'Repository data loaded',
} as const;

// Animation Durations (in milliseconds)
export const ANIMATION_DURATIONS = {
  fast: 200,
  normal: 300,
  slow: 500,
} as const;

// Component Sizes
export const COMPONENT_SIZES = {
  spinner: {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  },
  button: {
    sm: 'px-3 py-2 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  },
} as const;

// Utility Functions
export const getScoreColor = (score: number): string => {
  if (score >= SCORE_THRESHOLDS.excellent) return SCORE_COLORS.excellent;
  if (score >= SCORE_THRESHOLDS.good) return SCORE_COLORS.good;
  if (score >= SCORE_THRESHOLDS.fair) return SCORE_COLORS.fair;
  return SCORE_COLORS.poor;
};

export const getScoreLabel = (score: number): string => {
  if (score >= SCORE_THRESHOLDS.excellent) return 'Excellent';
  if (score >= SCORE_THRESHOLDS.good) return 'Good';
  if (score >= SCORE_THRESHOLDS.fair) return 'Fair';
  return 'Needs Improvement';
};

export const validateGitHubUrl = (url: string): boolean => {
  return GITHUB_URL_PATTERN.test(url.trim());
};

export const formatTimestamp = (timestamp: string): string => {
  return new Date(timestamp).toLocaleString();
};

export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
};

export const capitalizeFirst = (str: string): string => {
  return str.charAt(0).toUpperCase() + str.slice(1);
};